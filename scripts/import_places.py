#!/usr/bin/env python3
"""Rebuild attributed place data from local dumps (small seed or global v2).

Download CN.zip, US.zip, FR.zip, countryInfo.txt and readme.txt from
https://download.geonames.org/export/dump/ into --dump-dir first.
No population filter; no coordinate-based inference of administrative parents.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
# Selected IDs, Chinese display labels, source-based administrative parents.
SPEC = {
 'CN': ('中国', [
  ('1796236', '上海市', ['1796231','12324204'], [('1787956','徐汇区')]),
  ('1816670', '北京市', ['2038349','11876380'], [('1815402','朝阳区'),('1809103','海淀区')]),
  ('1806775', '黄山市（安徽省）', ['1818058'], [('1792358','屯溪区'),('1786429','黟县（县）')]),
 ]),
 'US': ('美国', [('5128581','纽约市（纽约州）',['5128638'],[])]),
 'FR': ('法国', [('2988507','巴黎（法兰西岛）',['3012874','2968815','2988506','6455259'],[])]),
}


def generate(dump_dir):
    selected = {}
    archives = {}
    countries = {}
    for cc, (label, specs) in SPEC.items():
        archive = dump_dir / (cc + '.zip')
        archives[cc] = {'url': f'https://download.geonames.org/export/dump/{cc}.zip',
                        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
        needed = {i for ident, _, parents, areas in specs for i in [ident, *parents, *(a[0] for a in areas)]}
        with zipfile.ZipFile(archive) as z:
            for line in z.read(cc + '.txt').decode().splitlines():
                row = line.split('\t')
                if row[0] in needed:
                    selected[row[0]] = row
        if needed - selected.keys():
            raise ValueError(f'Missing IDs: {needed - selected.keys()}')
        def record(ident, name=None):
            r = selected[ident]
            assert r[8] == cc
            return {'id': ident, 'name': name or r[1], 'originalName': r[1],
                    'type': r[7], 'adminCodes': r[10:14], 'modifiedAt': r[18],
                    'sourceURL': f'https://www.geonames.org/{ident}/',
                    'license': 'CC-BY-4.0', 'review': 'source_codes_only_not_government_verified'}
        cities = []
        for ident, name, parents, area_specs in specs:
            city = record(ident, name)
            city['parents'] = [record(i) for i in parents]
            city['areas'] = []
            # Admin parent matches by code prefix, not geographic proximity.
            prefix = city['adminCodes'][:2]
            for area_id, area_name in area_specs:
                area = record(area_id, area_name)
                if area['type'] != 'ADM3' or area['adminCodes'][:2] != prefix:
                    raise ValueError(f'Unproved city/area relationship: {ident}/{area_id}')
                area['parents'] = [*city['parents'], {'id': ident, 'name': name}]
                city['areas'].append(area)
            cities.append(city)
        info = next(l.split('\t') for l in (dump_dir / 'countryInfo.txt').read_text().splitlines() if l.startswith(cc+'\t'))
        countries[cc] = {'name': label, 'id': info[16], 'originalName': info[4], 'cities': cities}
    return {'version':'2026-10-10-geonames-slice.1', 'retrievedAt':'2026-10-10',
            'attribution':'GeoNames; Chinese labels and slice mapping by PetWaymark contributors',
            'license':'CC-BY-4.0', 'licenseURL':'https://creativecommons.org/licenses/by/4.0/',
            'documentationURL':'https://download.geonames.org/export/dump/readme.txt',
            'archives':archives, 'auxiliaryInputs':{name:{'url':'https://download.geonames.org/export/dump/'+name,'sha256':hashlib.sha256((dump_dir/name).read_bytes()).hexdigest()} for name in ['countryInfo.txt','readme.txt']}, 'countries':countries}, selected


def generate_global(dump_dir):
    """All countryInfo entries, all ADM1, top three major cities per ADM1.

    China: every current ADM2 in CN dump plus existing selected city records.
    HK/MO/TW remain separate source jurisdictions; CN picker also exposes these
    three provincial entries without applying mainland transport rules to them.
    """
    import re
    from collections import defaultdict
    old = json.loads((ROOT/'scripts/places-seed.json').read_text())
    old_cities = {c['id']: c for v in old['countries'].values() for c in v['cities']}
    rows = {}
    def chinese(r):
        names = [n for n in r[3].split(',') if re.fullmatch(r'[\u4e00-\u9fff·]+', n)]
        return next((n for n in names if n.endswith(('市','自治州','地区','盟','省','自治区'))), names[0] if names else r[1])
    def record(r, name=None):
        rows[r[0]] = r
        return {'id':r[0], 'name':name or r[1], 'originalName':r[1], 'type':r[7],
                'adminCodes':r[10:14], 'modifiedAt':r[18], 'sourceURL':f'https://www.geonames.org/{r[0]}/',
                'license':'CC-BY-4.0', 'review':'source_codes_only_not_government_verified'}
    infos = [l.split('\t') for l in (dump_dir/'countryInfo.txt').read_text().splitlines() if l and not l.startswith('#') and l[:2] not in ['CS','AN']]
    labels = {'CN':'中国','HK':'中国香港','MO':'中国澳门','TW':'中国台湾','US':'美国','FR':'法国','GB':'英国','JP':'日本','KR':'韩国','CA':'加拿大','AU':'澳大利亚','NZ':'新西兰','DE':'德国','IT':'意大利','ES':'西班牙','SG':'新加坡','TH':'泰国','MY':'马来西亚','RU':'俄罗斯'}
    # Membership checked against https://european-union.europa.eu/principles-countries-history/eu-countries_en (2026-10-10).
    countries = {r[0]:{'id':r[16], 'name':labels.get(r[0],r[4]), 'originalName':r[4], 'cities':[], 'subdivisions':[], 'euMember':r[0] in 'AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE'.split()} for r in infos}
    admins = {}
    for line in (dump_dir/'admin1CodesASCII.txt').read_text().splitlines():
        code,name,ascii_name,ident = line.split('\t')
        cc, ac = code.split('.',1)
        if cc not in countries: continue
        a = {'id':ident,'code':ac,'name':name,'originalName':name,'sourceURL':f'https://www.geonames.org/{ident}/','license':'CC-BY-4.0'}
        admins[code]=a; countries[cc]['subdivisions'].append(a)
    city_groups = defaultdict(list)
    with zipfile.ZipFile(dump_dir/'cities15000.zip') as z:
        for line in z.read('cities15000.txt').decode().splitlines():
            r=line.split('\t')
            if r[8] in countries: city_groups[(r[8],r[10])].append(r)
    for (cc,ac), group in sorted(city_groups.items()):
        if cc=='CN': continue
        for r in sorted(group,key=lambda r:(-int(r[14] or 0),r[0]))[:3]:
            c=record(r); c.update(areas=[],parents=[],subdivision=ac)
            if cc in ['HK','MO','TW']: c['name']=chinese(r)
            if r[0] in old_cities: c['name']=old_cities[r[0]]['name']
            countries[cc]['cities'].append(c)
    with zipfile.ZipFile(dump_dir/'CN.zip') as z:
        cn={r[0]:r for r in (l.split('\t') for l in z.read('CN.txt').decode().splitlines())}
    for r in cn.values():
        if r[7]=='ADM1':
            a=admins['CN.'+r[10]]; a['name']=chinese(r); a['record']=record(r,a['name'])
    selected = [r for r in cn.values() if r[7]=='ADM2' and r[0] not in ['12324204','11876380']] # municipalities use existing city points
    selected += [cn[i] for i in ['1796236','1816670'] if i in cn]
    for r in selected:
        c=record(r,chinese(r)); c.update(subdivision=r[10], areas=[], parents=[admins['CN.'+r[10]]['record']])
        if r[0] in old_cities:
            previous=old_cities[r[0]]; c['name']=previous['name']; c['areas']=previous['areas']; c['parents']=previous['parents']
            for parent in c['parents']:
                if parent['id'] in cn: rows[parent['id']]=cn[parent['id']]
            for area in c['areas']: rows[area['id']]=cn[area['id']]
        countries['CN']['cities'].append(c)
    # Public factual names/codes from the attributed, licensed 2023 snapshot.
    china_cities=json.loads((ROOT/'apps/pages/china-cities.json').read_text())
    name_by_code={r['code']:r['name'] for r in china_cities if r['name'] not in ['市辖区','县','省直辖县级行政区划','自治区直辖县级行政区划']}
    for c in countries['CN']['cities']:
        if c['adminCodes'][1] in name_by_code and c['id'] not in old_cities:
            c['name']=name_by_code[c['adminCodes'][1]]
            c['displayNameSource']='china-admin-2023'
    missing=set(name_by_code)-{c['adminCodes'][1] for c in countries['CN']['cities']}
    if missing: raise ValueError(f'Missing mainland prefectures: {missing}')
    # Preserve the source-city identifiers used by existing bookmarked routes.
    for ident,c in old_cities.items():
        cc=next(cc for cc,v in old['countries'].items() if any(x['id']==ident for x in v['cities']))
        if not any(x['id']==ident for x in countries[cc]['cities']):
            raise ValueError(f'Existing city missing: {ident}')
    for cc,country in countries.items():
        for city in country['cities']:
            if city['subdivision'] and cc+'.'+city['subdivision'] not in admins:
                city['subdivision']='' # no guessed parent
        names=[c['name'] for c in country['cities']]
        for city in country['cities']:
            if names.count(city['name'])>1 and city['id'] not in old_cities:
                region=admins.get(cc+'.'+city['subdivision'],{}).get('name','未收录省州')
                city['name']+=f'（{region}）'
                peers=[c for c in country['cities'] if c['name']==city['name']]
                if len(peers)>1: city['name']+=f'（同名地点 {peers.index(city)+1}）'
    for cc in ['HK','MO','TW']:
        countries['CN']['subdivisions'].append({'id':countries[cc]['id'], 'code':cc,'name':labels[cc], 'jurisdiction':cc,'sourceURL':f"https://www.geonames.org/{countries[cc]['id']}/",'license':'CC-BY-4.0'})
    files=['countryInfo.txt','admin1CodesASCII.txt','cities15000.zip','CN.zip','readme.txt']
    return {'version':'2026-10-10-geonames-global.2','retrievedAt':'2026-10-10',
            'attribution':'GeoNames; Chinese labels and slice mapping by PetWaymark contributors',
            'license':'CC-BY-4.0','licenseURL':'https://creativecommons.org/licenses/by/4.0/',
            'documentationURL':'https://download.geonames.org/export/dump/readme.txt',
            'archives':{n:{'url':'https://download.geonames.org/export/dump/'+n,'sha256':hashlib.sha256((dump_dir/n).read_bytes()).hexdigest()} for n in files},
            'supplementaryInputs':{n:{'url':'https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/c49d495b40ac73eb1a66f6eeae5f8fd10696f035/dist/'+n,'sha256':hashlib.sha256((ROOT/'apps/pages'/('china-'+n)).read_bytes()).hexdigest(),'license':'WTFPL-2.0','asOf':'2023-06-30'} for n in ['cities.json','provinces.json']},
            'countries':countries}, rows

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--dump-dir', type=Path, required=True)
    p.add_argument('--global-places', action='store_true')
    args = p.parse_args()
    data, selected = (generate_global if args.global_places else generate)(args.dump_dir)
    target = ROOT / 'apps/pages'
    (target / 'locations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (target / 'geonames-subset.tsv').write_text(''.join('\t'.join(selected[i])+'\n' for i in sorted(selected)))
    (target / 'geonames-country-subset.tsv').write_text('\n'.join(l for l in (args.dump_dir/'countryInfo.txt').read_text().splitlines() if l and not l.startswith('#'))+'\n')
    (target / 'geonames-admin1-subset.tsv').write_text((args.dump_dir/'admin1CodesASCII.txt').read_text())
    print('Imported attributed places; source hierarchy is not government verification')
