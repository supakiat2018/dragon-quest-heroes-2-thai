import csv

with open('text_csv/categories/entry_00253_Monster_Medals.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Total rows in Entry 253: {len(rows)}")
unique_names = set()
for r in rows:
    eng = r['OriginalEnglish'].strip()
    if eng and eng not in ['the', 'a', 'an', 'some', 'the ']:
        unique_names.add(eng)

print(f"Unique tokens/names: {len(unique_names)}")
for u in sorted(list(unique_names))[:50]:
    print(u)
