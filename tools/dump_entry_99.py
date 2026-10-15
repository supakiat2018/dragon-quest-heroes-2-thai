import csv

with open('text_csv/categories/entry_00099_Stats_Attributes.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

unique = []
seen = set()
for r in rows:
    eng = r['OriginalEnglish'].strip()
    if eng and eng not in seen:
        seen.add(eng)
        unique.append(eng)

print(f"Total unique stats in Entry 99: {len(unique)}")
with open('tools/unique_stats.txt', 'w', encoding='utf-8') as out:
    for u in unique:
        out.write(f"{u}\n")

print("Saved to tools/unique_stats.txt")
