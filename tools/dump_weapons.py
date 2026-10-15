import csv
import json

with open('text_csv/categories/entry_00071_Weapons_Equipment.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

weapons = []
for i in range(0, len(rows), 8):
    chunk = rows[i:i+8]
    disp = chunk[1]['OriginalEnglish'].strip() if len(chunk) > 1 else ''
    desc = chunk[2]['OriginalEnglish'].strip() if len(chunk) > 2 else ''
    if disp:
        weapons.append({
            'slot': i // 8,
            'start_row': i,
            'name': disp,
            'desc': desc
        })

print(f"Total weapons: {len(weapons)}")
with open('tools/weapons_list.json', 'w', encoding='utf-8') as out:
    json.dump(weapons, out, ensure_ascii=False, indent=2)

print("Saved to tools/weapons_list.json")
