# -*- coding: utf-8 -*-
"""
translate_story_quests_part4.py
Translates rows 4000 to 4799 of entry_00036_Story_Quests.csv (29 lines)
"""

import csv

STORY_QUESTS_PART4 = {
    # 4056-4058: A Hard Day's Night Clubber
    4056: "คลับเบอร์ยามราตรีสุดหฤโหด",
    4057: "คลับเบอร์ยามราตรีสุดหฤโหด",
    4058: "มอนสเตอร์ขนาดยักษ์พร้อมกระบองมหึมาปรากฏตัวขึ้นมาอย่างกะทันหัน หากไม่มีใครหยุดมันไว้โดยเร็ว ฮาร์บาจะต้องเผชิญหน้ากับหายนะครั้งใหญ่หลวงอย่างแน่นอน<FG>",

    # 4144-4145: Special Live Battle
    4144: "ศึกสมรภูมิสดพิเศษ",
    4145: "ศึกสมรภูมิสดพิเศษ",

    # 4184-4186: To Blacka Pastures
    4184: "สู่ทุ่งหญ้าทมิฬแบล็กก้า<FG>",
    4185: "สู่ทุ่งหญ้าทมิฬแบล็กก้า<FG>",
    4186: "มุ่งหน้าไปยังทุ่งหญ้าทมิฬแบล็กก้าผ่านประตูมิติ",

    # 4192-4194: To the Damned Dunes
    4192: "สู่เนินทรายต้องคำสาป<FG>",
    4193: "สู่เนินทรายต้องคำสาป<FG>",
    4194: "มุ่งหน้าไปยังเนินทรายต้องคำสาปผ่านประตูมิติ",

    # 4200-4202: To the Darkwood
    4200: "สู่ป่าทมิฬดาร์กวูด<FG>",
    4201: "สู่ป่าทมิฬดาร์กวูด<FG>",
    4202: "มุ่งหน้าไปยังป่าทมิฬดาร์กวูดผ่านประตูมิติ",

    # 4208-4210: To Blackrock Ravine
    4208: "สู่หุบผาหินทมิฬแบล็กร็อก<FG>",
    4209: "สู่หุบผาหินทมิฬแบล็กร็อก<FG>",
    4210: "มุ่งหน้าไปยังหุบผาหินทมิฬแบล็กร็อกผ่านประตูมิติ",

    # 4216-4218: To the Fetid Foothills
    4216: "สู่เชิงเขาเน่าเปื่อยเฟติด<FG>",
    4217: "สู่เชิงเขาเน่าเปื่อยเฟติด<FG>",
    4218: "มุ่งหน้าไปยังเชิงเขาเน่าเปื่อยเฟติดผ่านประตูมิติ",

    # 4224-4226: To Dead Man's Land
    4224: "สู่แดนคนตายเดดแมนแลนด์<FG>",
    4225: "สู่แดนคนตายเดดแมนแลนด์<FG>",
    4226: "มุ่งหน้าไปยังแดนคนตายเดดแมนแลนด์ผ่านประตูมิติ",

    # 4232-4234: To the Tomb of the Sun
    4232: "สู่สุสานแห่งสุริยัน<FG>",
    4233: "สู่สุสานแห่งสุริยัน<FG>",
    4234: "มุ่งหน้าไปยังสุสานแห่งสุริยันผ่านประตูมิติ",

    # 4288-4290: Buds in the Woods
    4288: "เพื่อนเกลอในดงดิบ",
    4289: "เพื่อนเกลอในดงดิบ",
    4290: "ไม้เนื้อแข็งทนทานที่จำเป็นสำหรับการซ่อมสะพานสามารถหาได้จากสถานที่เดียวเท่านั้น<MV>นั่นคือป่าดงดิบไวลด์วูด <F4><I0>01 และพรรคพวกไม่มีทางเลือกอื่นนอกจากต้องค้นหาทรัพยากรหายากนี้ในผืนป่าน่าสะพรึงกลัว<FG>",
}

def apply_translation():
    file_path = "text_csv/categories/entry_00036_Story_Quests.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for row_idx, thai_text in STORY_QUESTS_PART4.items():
        if row_idx < len(rows):
            rows[row_idx]["ThaiTranslation"] = thai_text
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} lines in rows 4000-4799 of entry_00036_Story_Quests.csv (Dict entries: {len(STORY_QUESTS_PART4)})")

if __name__ == "__main__":
    apply_translation()
