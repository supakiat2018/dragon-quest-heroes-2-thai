import csv

with open('text_csv/categories/entry_00253_Monster_Medals.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

unique_names = set()
for r in rows:
    eng = r['OriginalEnglish'].strip()
    if eng and eng not in ['the', 'a', 'an', 'some', 'the ']:
        unique_names.add(eng)

with open('tools/unique_medals.txt', 'w', encoding='utf-8') as out:
    for u in sorted(list(unique_names)):
        out.write(f"{u}\n")

print(f"Dumped {len(unique_names)} unique medals to tools/unique_medals.txt")
