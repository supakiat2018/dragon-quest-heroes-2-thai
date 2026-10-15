import csv

targets = [
    'Full Screen Display', 'Resolution', 'Frame Rate', 'Quality Settings',
    'No. of On-Screen Characters', 'Draw Distance', 'Textures', 'Custom',
    'Choose whether to play in full screen or windowed mode.'
]

with open('text_csv/categories/entry_00204_Menus_UI_Settings.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        en = row['OriginalEnglish'].strip()
        for t in targets:
            if en == t or en == '  ' + t or t in en:
                print(f"{row['StringIndex']:4s} | ptr={row['PointerOffset']:5s} | {en:35s} -> {row['ThaiTranslation']}")
