# -*- coding: utf-8 -*-
"""
translate_transformation_attacks.py
Translates entry_00309_Transformation_Attacks.csv (138 lines)
"""

import csv

ATTACK_TRANSLATIONS = {
    'Abyssal Breath': 'ลมหายใจอเวจี',
    'Bang': 'อิโอ',
    'Barging Charge': 'พุ่งกระแทกชน',
    'Barrel Roll': 'หมุนตัวกลิ้งสว่าน',
    'Bash Dash': 'พุ่งชนกระแทก',
    'Bashback': 'ฟาดสะท้อนกลับ',
    'Bitter Beam': 'ลำแสงขมขื่น',
    'Blazing Breath': 'ลมหายใจเพลิงพิโรธ',
    'Blistering Breath': 'ลมหายใจเพลิงแผดเผา',
    'Blistering Twister': 'พายุหมุนเพลิงแผดเผา',
    'Body Slam': 'ทิ้งตัวกระแทก',
    'Bolide Blast': 'ระเบิดอุกกาบาต',
    'Boom': 'อิโอร่า',
    'Boreal Bore': 'สว่านเหมันต์',
    'Bow Barrage': 'ห่าฝนเกาทัณฑ์',
    'Circle of Hell': 'วงแหวนโลกันตร์',
    'Club': 'ฟาดกระบอง',
    'Crackle': 'เฮียดาโก้',
    'Crass Cross': 'ฟันกากบาททมิฬ',
    'Cratermaker': 'ทุบพสุธาแยก',
    'Crystal Crash': 'ผลึกคริสตัลถล่ม',
    'Cyclone Spin': 'หมุนวนไซโคลน',
    'Dark Dart': 'ศรทมิฬ',
    'Death Breath': 'ลมหายใจมรณะ',
    'Diamond Dash': 'พุ่งทะยานเพชร',
    'Diamond Dervish': 'ระบำสว่านเพชร',
    'Falcon Slash': 'ฟอลคอนสแลช',
    'Fire Flight': 'บินถลาเพลิง',
    'Fireball': 'ลูกไฟเพลิง',
    'Fireball Throw': 'ขว้างลูกไฟเพลิง',
    'Flame Breath': 'ลมหายใจเพลิง',
    'Flame Slash': 'ดาบเพลิงพิฆาต',
    'Flash Freeze': 'แช่แข็งฉับพลัน',
    'Flying Kick': 'กระโดดถีบกลางเวหา',
    'Freezing Blizzard': 'พายุหิมะเยือกแข็ง',
    'Frizz': 'เมร่า',
    'Frost Flare': 'เปลวเพลิงเหมันต์',
    'Frostfoot': 'ย่างก้าวเยือกแข็ง',
    'Frosty Flop': 'ทับบดขยี้เยือกแข็ง',
    'Gale Raiser': 'เรียกลมพายุ',
    'Geyser': 'น้ำพุร้อนพวยพุ่ง',
    'Gigantaxe': 'ขวานยักษ์ผ่าพิภพ',
    'Golden Glare': 'สายตาทองคำสยบ',
    'Ground Pound': 'กระแทกพื้นพสุธา',
    'Gyroblade': 'ใบมีดไจโรสว่าน',
    'Hack Attack': 'กระหน่ำจามขวาน',
    'Hatchet Man': 'ขวานผ่าปีศาจ',
    'Helm Splitter': 'ผ่าหมวกเกราะ',
    'Helter Belter': 'หมัดเหวี่ยงอลหม่าน',
    'Hot Runnings': 'วิ่งตะลุยไฟ',
    'Ice Scream': 'เสียงกรีดร้องเยือกแข็ง',
    'Inferno': 'ไฟนรกโลกันตร์',
    'Kaboom': 'อิโอนาซึน',
    'Kacrackle Slash': 'ดาบน้ำแข็งมหาประลัย',
    'Kamikazee': 'เมกันเต้',
    'Kazam': 'ดอลคูม่า',
    'Kazapple': 'มินาดีน',
    'Kerfrizz': 'เมราโซม่า',
    'Kerwoosh': 'บากิมูโช',
    'Kerzam': 'ดอลมอนเต้',
    'Kick': 'เตะ',
    'Lance-a-Lot': 'รัวแทงหอกอัศวิน',
    'Let Rip': 'ฟาดเต็มแรง',
    'Miracle Slash': 'มิราเคิลสแลช',
    'Multifeet': 'รัวลูกเตะพายุหมุน',
    'Multithrust': 'รัวแทงหอก',
    'Parallax': 'ฟันประกบสองทิศ',
    'Plasma Dome': 'โดมพลาสมา',
    'Platycopter': 'ปากเป็ดใบพัดบิน',
    'Pressure Pointer': 'จุดชีพจรพิฆาต',
    'Quantum Leap': 'ก้าวกระโดดข้ามมิติ',
    'Raw Roar': 'เสียงคำรามป่าเถื่อน',
    'Robobeam': 'ลำแสงหุ่นยนต์',
    'Sabre Reel': 'หมุนกงล้อเสือเขี้ยวดาบ',
    'Sabre Wheel': 'กงล้อเสือเขี้ยวดาบ',
    'Savage Slash': 'ฟันเฉือนอย่างบ้าคลั่ง',
    'Scorch': 'เพลิงโลกันตร์แผดเผา',
    "Scram 'n' Zam": 'ดอลม่าสับหลีก',
    'Searing Slice': 'ดาบเฉือนเพลิงลุกโชน',
    'Shadow Shot': 'ยิงศรเงาพราย',
    'Sizz': 'กิร่า',
    'Sizzling Smash': 'ทุบระเบิดเพลิง',
    'Sleet Shot': 'ยิงลูกเห็บเยือกแข็ง',
    'Slime Spank': 'สไลม์ตบสั่งสอน',
    'Snow Boulder': 'หินหิมะยักษ์',
    'Snowball': 'ลูกบอลหิมะ',
    'Spark Spank': 'ตบประกายไฟ',
    'Spinning Slice': 'หมุนตัวฟัน',
    'Squall Balls': 'ลูกบอลพายุหมุน',
    "Stone's Throat": 'พ่นหินกลืนกิน',
    'Sucker Punch': 'หมัดลอบชก',
    'Sunburst': 'ระเบิดสุริยัน',
    'Sweet Breath': 'ลมหายใจหลับใหล',
    'Sword Swing': 'เหวี่ยงดาบ',
    'Tailspin': 'หมุนควงหาง',
    'Thin Air': 'คลื่นสุญญากาศ',
    'Thunder Rush': 'พุ่งทะยานสายฟ้า',
    'Thunderbolt': 'อัสนีบาตฟาด',
    'Thwack': 'ซาคิ',
    'Tumblebleed': 'กลิ้งทิ่มแทง',
    'Tumboggan': 'ไถลตัวพุ่งชน',
    'War Cry': 'เสียงคำรามศึก',
    'Wind Shear': 'คมมีดสายลม',
    'Wind Sickles': 'เคียวสายลม',
    'Zap': 'เดอิน',
    'Über Falcon Slash': 'ซูเปอร์ฟอลคอนสแลช',
    'Über Spinning Slice': 'ซูเปอร์หมุนตัวฟัน',
}

def apply_translation():
    file_path = "text_csv/categories/entry_00309_Transformation_Attacks.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for r in rows:
        eng = r["OriginalEnglish"]
        if eng and eng in ATTACK_TRANSLATIONS:
            r["ThaiTranslation"] = ATTACK_TRANSLATIONS[eng]
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} transformation attacks in {file_path}")

if __name__ == "__main__":
    apply_translation()
