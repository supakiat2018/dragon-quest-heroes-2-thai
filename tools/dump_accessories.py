import csv
import json

with open('text_csv/categories/entry_00092_Accessories.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

accs = []
for i in range(0, len(rows), 8):
    chunk = rows[i:i+8]
    disp = chunk[1]['OriginalEnglish'].strip() if len(chunk) > 1 else ''
    desc = chunk[2]['OriginalEnglish'].strip() if len(chunk) > 2 else ''
    if disp:
        accs.append({
            'slot': i // 8,
            'start_row': i,
            'name': disp,
            'desc': desc
        })

print(f"Total valid accessories: {len(accs)}")
with open('tools/accessories_list.json', 'w', encoding='utf-8') as out:
    json.dump(accs, out, ensure_ascii=False, indent=2)

for a in accs:
    print(f"[{a['slot']:2d}] {a['name']:30s} | {a['desc']}")
