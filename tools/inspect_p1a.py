import json

data = json.load(open('tools/dlc_p1a.json', encoding='utf-8'))
print(f"Total items: {len(data)}")
for i, item in enumerate(data):
    sidx = item['StringIndex']
    en = item['OriginalEnglish']
    print(f"{i} (idx {sidx}): {en}")
