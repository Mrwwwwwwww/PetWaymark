#!/usr/bin/env python3
"""Rebuild the intentionally small attributed GeoNames slice from local dumps.

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


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--dump-dir', type=Path, required=True)
    args = p.parse_args()
    data, selected = generate(args.dump_dir)
    target = ROOT / 'apps/pages'
    (target / 'locations.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (target / 'geonames-subset.tsv').write_text(''.join('\t'.join(selected[i])+'\n' for i in sorted(selected)))
    (target / 'geonames-country-subset.tsv').write_text('\n'.join(l for l in (args.dump_dir/'countryInfo.txt').read_text().splitlines() if l[:3] in ['CN\t','US\t','FR\t'])+'\n')
    print('Imported sourced place slice; no government verification or transport coverage claimed')
