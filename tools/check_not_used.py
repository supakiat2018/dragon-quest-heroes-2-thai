import csv

with open('text_csv/dqh2_all_english_text.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r.get('OriginalEnglish') == 'NOT USED' and r.get('ThaiTranslation'):
            print(f"E{r['EntryID']} S{r['StringIndex']}: {repr(r['OriginalEnglish'])} -> {repr(r['ThaiTranslation'])}")
            break
