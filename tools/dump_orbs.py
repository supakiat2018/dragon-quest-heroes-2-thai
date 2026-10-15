import csv
import json

with open('text_csv/categories/entry_00078_Orbs.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

orbs = []
for i in range(0, len(rows), 8):
    chunk = rows[i:i+8]
    disp = chunk[1]['OriginalEnglish'].strip() if len(chunk) > 1 else ''
    desc = chunk[2]['OriginalEnglish'].strip() if len(chunk) > 2 else ''
    if disp and disp != 'Unused':
        orbs.append({
            'slot': i // 8,
            'start_row': i,
            'name': disp,
            'desc': desc
        })

print(f"Total valid orbs: {len(orbs)}")
with open('tools/orbs_list.json', 'w', encoding='utf-8') as out:
    json.dump(orbs, out, ensure_ascii=False, indent=2)

for o in orbs:
    print(f"[{o['slot']:2d}] {o['name']:25s} | {o['desc']}")
