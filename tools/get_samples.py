import csv

with open('text_csv/categories/entry_00246_Main_Story_Cutscenes_Dialogues.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

indices = [0, 26, 107, 187, 250, 319, 420, 500, 615, 750, 856, 920, 999]
for idx in indices:
    r = rows[idx]
    print(f"Row {idx} (StringIndex {r.get('StringIndex')}):")
    print(f"EN: {r.get('OriginalEnglish', '')}")
    print(f"TH: {r.get('ThaiTranslation', '')}")
    print("-" * 60)
