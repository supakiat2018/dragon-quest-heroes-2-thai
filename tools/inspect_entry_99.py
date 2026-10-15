import csv

with open('text_csv/categories/entry_00099_Stats_Attributes.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Total rows in Entry 99: {len(rows)}")
for r in rows:
    orig = r['OriginalEnglish'].strip()
    if orig:
        print(f"[{r['StringIndex']:3s}] {orig}")
