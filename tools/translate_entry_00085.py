# -*- coding: utf-8 -*-
"""
translate_entry_00085.py
Translates entry_00085_Accessory_Types.csv
"""

import csv

MAP_85 = {
    "Standard": "มาตรฐาน",
    "Dragon Quest I": "ดราก้อนเควสต์ 1",
    "Luceus": "แอคท์",
    "Aurora": "เมียร์",
}

def translate_85():
    target_csv = "text_csv/categories/entry_00085_Accessory_Types.csv"
    with open(target_csv, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    updated = 0
    for r in reader:
        eng = r["OriginalEnglish"].strip()
        if eng in MAP_85:
            r["ThaiTranslation"] = MAP_85[eng]
            updated += 1

    with open(target_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

    print(f"[SUCCESS] Updated {updated} lines in {target_csv}!")

if __name__ == "__main__":
    translate_85()
