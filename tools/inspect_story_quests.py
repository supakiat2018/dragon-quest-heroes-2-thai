import csv
import sys

r = list(csv.DictReader(open('text_csv/categories/entry_00036_Story_Quests.csv', encoding='utf-8-sig')))

start_row = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end_row = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

non_empty = [(i, r[i]['StringIndex'], r[i]['OriginalEnglish']) for i in range(start_row, min(end_row, len(r))) if r[i]['OriginalEnglish'].strip() != '']
print(f"Total non-empty in rows {start_row}-{end_row}: {len(non_empty)}")

# Group by 8 rows if applicable
i = 0
while i < len(non_empty):
    row_idx, sidx, text = non_empty[i]
    print(f"[{row_idx:4d}] {text}")
    i += 1
