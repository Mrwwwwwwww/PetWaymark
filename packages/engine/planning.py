"""Neutral public leads and itemized manual cost notes, with no service calls."""
from copy import deepcopy
import math
from urllib.parse import urlsplit
from packages.engine.evaluate import day
from packages.engine.io import ROOT
from scripts.validate_data import read_json

COST_ITEMS = [
    ('origin_transfer','Origin ground transfer','起运道路接驳'),
    ('veterinary','Examination, vaccination and identification','检查、接种及标识'),
    ('laboratory','Antibody laboratory and sample shipping','抗体实验室及样本寄送'),
    ('certification','Official certificate and endorsement','官方证书及背书'),
    ('document_delivery','Original document delivery','原件交付'),
    ('container','Transport container','运输容器'),
    ('main_transport','Main transport and handling','主运输及操作'),
    ('arrival_inspection','Arrival inspection and quarantine if applicable','抵达检查及适用隔离'),
    ('destination_transfer','Destination ground transfer','目的地接驳'),
    ('overnight_care','Delay and overnight care contingency','延误及过夜照护备选'),
    ('taxes','Taxes and additional charges','税费及附加项')]


def load_directory(root=ROOT):
    return read_json(root / 'data/providers/directory.json')


def costs(quotes=None, *, assessment_at):
    """Manual anonymous notes only; unknown items prevent a total or comparison."""
    at=day(assessment_at)
    if quotes is None:quotes={}
    if not isinstance(quotes,dict) or set(quotes)-{x[0] for x in COST_ITEMS}:
        raise ValueError('unknown cost item')
    rows=[]
    allowed={'currency','min','max','quoted_at','expires_at','includes','excludes','source'}
    for ident,en,zh in COST_ITEMS:
        row=dict(item_id=ident,label={'en':en,'zh-CN':zh},currency=None,min=None,max=None,
                 quoted_at=None,expires_at=None,includes=None,excludes=None,source=None,status='unquoted',
                 confirmation='unknown')
        q=quotes.get(ident)
        if q is not None:
            if not isinstance(q,dict) or set(q)-allowed:raise ValueError('invalid cost note fields')
            row.update(deepcopy(q))
            for name in ('min','max'):
                v=row[name]
                if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or v<0):
                    raise ValueError('invalid amount')
            if row['min'] is not None and row['max'] is not None and row['min']>row['max']:
                raise ValueError('reversed cost range')
            currency=row['currency']
            if currency is not None and (not isinstance(currency,str) or len(currency)!=3 or not currency.isascii() or not currency.isupper() or not currency.isalpha()):
                raise ValueError('invalid currency')
            for name in ('includes','excludes'):
                if row[name] is not None and (not isinstance(row[name],list) or any(not isinstance(v,str) for v in row[name])):
                    raise ValueError('invalid inclusion list')
            if row['source'] is not None and (not isinstance(row['source'],str) or urlsplit(row['source']).scheme!='https' or not urlsplit(row['source']).netloc):
                raise ValueError('cost source must be a public https reference')
            issued=day(row['quoted_at']) if row['quoted_at'] is not None else None
            expires=day(row['expires_at']) if row['expires_at'] is not None else None
            if issued and expires and issued>expires:raise ValueError('reversed quote dates')
            complete=all(row[k] is not None for k in allowed)
            row['status']=('future_dated' if issued and issued>at else 'expired' if expires and at>=expires else
                           'manual_note_complete_unconfirmed' if complete else 'incomplete')
        rows.append(row)
    return dict(items=rows,total=None,total_currency=None,comparable=False,
                unquoted_items=[r['item_id'] for r in rows if r['status']=='unquoted'],
                policy='No totals, exchange conversions or live quotations; expiry date is conservatively excluded.')
