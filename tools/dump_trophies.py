import csv
import json

r = list(csv.DictReader(open('text_csv/categories/entry_00169_Accolades_Trophies.csv', encoding='utf-8-sig')))
trophies = []
for i in range(0, len(r), 8):
    chunk = r[i:i+8]
    name = chunk[0]['OriginalEnglish'].strip()
    desc = chunk[2]['OriginalEnglish'].strip()
    if name or desc:
        trophies.append({'slot': i//8, 'name': name, 'desc': desc})

print(f'Total trophies: {len(trophies)}')
json.dump(trophies, open('tools/trophies_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
for x in trophies:
    print(f"[{x['slot']:2d}] {x['name']:25s} | {x['desc']}")
