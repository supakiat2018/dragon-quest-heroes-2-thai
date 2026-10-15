import csv

with open('text_csv/categories/entry_00246_Main_Story_Cutscenes_Dialogues.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

indices = [1000, 1014, 1046, 1091, 1188, 1282, 1332, 1400, 1451, 1533, 1652, 1791, 1808, 1832, 1942, 1991]
for idx in indices:
    r = rows[idx]
    print(f"Row {idx} (StringIndex {r.get('StringIndex')}):")
    print(f"EN: {r.get('OriginalEnglish', '')}")
    print(f"TH: {r.get('ThaiTranslation', '')}")
    print("-" * 60)
