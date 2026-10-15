import csv

with open('text_csv/categories/entry_00127_Skill_Types.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

with open('tools/entry_127_rows.txt', 'w', encoding='utf-8') as out:
    for r in rows:
        if r['OriginalEnglish'].strip():
            out.write(f"[{r['StringIndex']:3s}] {r['OriginalEnglish']}\n")

print("Dumped to tools/entry_127_rows.txt")
