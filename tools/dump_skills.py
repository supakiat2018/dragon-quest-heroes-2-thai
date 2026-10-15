import csv
import json

with open('text_csv/categories/entry_00120_Abilities_Skills.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

skills = []
for i in range(0, len(rows), 8):
    chunk = rows[i:i+8]
    disp = chunk[0]['OriginalEnglish'].strip() if len(chunk) > 0 else ''
    desc = chunk[2]['OriginalEnglish'].strip() if len(chunk) > 2 else ''
    if disp:
        skills.append({
            'slot': i // 8,
            'start_row': i,
            'name': disp,
            'desc': desc
        })

print(f"Total skills/abilities: {len(skills)}")
with open('tools/skills_list.json', 'w', encoding='utf-8') as out:
    json.dump(skills, out, ensure_ascii=False, indent=2)

print("Saved to tools/skills_list.json")
