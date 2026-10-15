# -*- coding: utf-8 -*-
"""
translate_areas.py
Translates entry_00050_Areas_Wilderness.csv
"""

import csv

AREA_TRANSLATIONS = {
    "Greena Pastures": "ทุ่งหญ้ากรีน่า",
    "The Grand Dunes": "เนินทรายยักษ์แกรนด์ดูนส์",
    "The Lumberlands": "ผืนป่าลัมเบอร์แลนด์",
    "Redrock Ravine": "หุบผาหินแดงเรดร็อก",
    "The Frosty Foothills": "เชิงเขาเยือกแข็งฟรอสตี้",
    "No Man's Land": "แดนร้างไร้ผู้ครอบครอง",
    "Barracks Backyard": "ลานหลังค่ายทหาร",
    "Gates of Harba": "ประตูเมืองฮาร์บา",
    "Streets of Harba": "ถนนในเมืองฮาร์บา",
    "Dunisian Desert": "ทะเลทรายดูนิเซีย",
    "Dunisian Oilfields": "แหล่งบ่อน้ำมันดูนิเซีย",
    "The Pyramid": "พีระมิด",
    "<FH><FH><FH>": "<FH><FH><FH>",
    "Ancient Ruins": "ซากปรักหักพังโบราณ",
    "Tomb of Kings": "สุสานแห่งกษัตริย์",
    "Tomb of the Sun": "สุสานแห่งสุริยัน",
    "Outer Dunisia": "ชานเมืองดูนิเซีย",
    "The Wildwood": "ป่าดงดิบไวลด์วูด",
    "Unclearing<FI> Entrance": "ทางเข้าป่าดงทึบอันเคลียริ่ง<FI>",
    "The Unclearing": "ป่าดงทึบอันเคลียริ่ง",
    "Unclearing<FI> Exit": "ทางออกป่าดงทึบอันเคลียริ่ง<FI>",
    "Boss's Bower": "รังหัวหน้าใหญ่",
    "Clearing": "ลานโล่งกลางป่า",
    "Dank Dungeon": "คุกใต้ดินอับชื้น",
    "Ingenia Castle": "ปราสาทอินเกเนีย",
    "Throne Room": "ท้องพระโรง",
    "Great Divide<FI> South": "กำแพงแบ่งดินแดนใต้<FI>",
    "The Great Divide": "กำแพงแบ่งดินแดน",
    "Al-Khazami Outpost": "ด่านหน้าอัลคาซาม",
    "Great Divide<FI> Centre": "กำแพงแบ่งดินแดนกลาง<FI>",
    "Great Divide<FI> East": "กำแพงแบ่งดินแดนตะวันออก<FI>",
    "Great Divide<FI> West": "กำแพงแบ่งดินแดนตะวันตก<FI>",
    "Glacial Grotto": "ถ้ำธารน้ำแข็ง",
    "Mt Neverest": "ภูเขาเนเวอเรสต์",
    "Mt Neverest<FI> Summit": "ยอดเขาเนเวอเรสต์<FI>",
    "Gragwort's Grotto": "ถ้ำของแกรกเวิร์ต",
    "City Square": "ลานจัตุรัสกลางเมือง",
    "Streets of Accordia": "ถนนในเมืองออร์คาเนีย",
    "Level 1": "ชั้น 1",
    "Level 2": "ชั้น 2",
    "Level 3": "ชั้น 3",
    "Level 4": "ชั้น 4",
    "Level 5": "ชั้น 5",
    "Level 6": "ชั้น 6",
    "The Pinnacle of Peace": "วิหารยอดพสุธาสันติภาพ",
    "Pinnacle Passageway": "ทางเดินยอดพสุธา",
    "Royal Chambers": "ห้องประทับขององค์กษัตริย์",
    "Black Manse<FI> Base": "ฐานคฤหาสน์ทมิฬ<FI>",
    "Lair of the Gatekeepers": "รังของผู้เฝ้าประตู",
    "The Black Manse": "คฤหาสน์ทมิฬ",
    "Suspicious Bushes": "พุ่มไม้ต้องสงสัย",
    "The Great Spiral Stair": "บันไดวนยักษ์",
    "The Pinnacle's Pinnacle": "ยอดสูงสุดแห่งยอดพสุธา",
    "Black Manse<FI> Top": "ยอดคฤหาสน์ทมิฬ<FI>",
    "Corridor of Power": "ระเบียงแห่งอำนาจ",
    "The Seat of Evil": "บัลลังก์แห่งความชั่วร้าย",
    "Ad Hoc Encampment": "ค่ายพักแรมชั่วคราว",
    "Accordia": "ออร์คาเนีย",
    "The Clashroom": "สมรภูมิปะทะคลัชรูม",
    "Blacka Pastures": "ทุ่งหญ้าทมิฬแบล็กก้า",
    "The Damned Dunes": "เนินทรายต้องคำสาป",
    "The Darkwood": "ป่าทมิฬดาร์กวูด",
    "Blackrock Ravine": "หุบผาหินทมิฬแบล็กร็อก",
    "The Fetid Foothills": "เชิงเขาเน่าเปื่อยเฟติด",
    "Dead Man's Land": "แดนคนตายเดดแมนแลนด์",
}

def apply_translation():
    file_path = "text_csv/categories/entry_00050_Areas_Wilderness.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for row in rows:
        eng = row["OriginalEnglish"].strip()
        if eng in AREA_TRANSLATIONS:
            row["ThaiTranslation"] = AREA_TRANSLATIONS[eng]
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} area names in entry_00050_Areas_Wilderness.csv")

if __name__ == "__main__":
    apply_translation()
