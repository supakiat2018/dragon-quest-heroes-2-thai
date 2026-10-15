# -*- coding: utf-8 -*-
"""
translate_side_quests.py
Translates entry_00141_Side_Quests.csv
"""

import csv

QUEST_TITLES = {
    "Long Time No See": "ไม่ได้เจอกันนานเลยนะ",
    "Cousinly Combat": "ศึกประลองลูกพี่ลูกน้อง",
    "The Lady in Red": "สตรีในชุดแดง",
    "An Old Acquaintance": "คนรู้จักเก่า",
    "The Journey Begins": "การเดินทางเริ่มต้นขึ้น",
    "The Road to Accordia": "เส้นทางสู่ออร์คาเนีย",
    "A Wanderer Between Worlds": "ผู้พเนจรข้ามมิติ",
    "His Radiance": "พระบารมีอันเจิดจ้า",
    "Two Troubled Travellers": "สองนักเดินทางผู้พบปัญหา",
    "On the Brink of Battle": "ณ ริมขอบแห่งสงคราม",
    "March of the Dunisians": "การเดินทัพของชาวดูนิเซีย",
    "The Too-Proud Prince": "เจ้าชายผู้ทะนงตนเกินไป",
    "An Accusation and an Alibi": "ข้อกล่าวหาและพยานหลักฐาน",
    "Sticking Up for the Big Guy": "ปกป้องพี่ใหญ่ผู้ใจดี",
    "Brawn and Bravado": "พละกำลังและความกล้าหาญ",
    "A Predestined Prison Break": "แหกคุกตามลิขิตชะตา",
    "The Cold-Hearted Queen": "ราชินีผู้เย็นชา",
    "Not So Ingenious Now": "หมดสิ้นความฉลาดปราดเปรื่อง",
    "A Mysterious Man in Black": "ชายลึกลับในชุดดำ",
    "A World Once More at War": "โลกที่หวนสู่วังวนสงครามอีกครา",
    "Kings Fetid and Feathered": "ราชาผู้เน่าเปื่อยและราชาติดปีก",
    "The Mother of All Monsters": "มารดาแห่งเหล่ามอนสเตอร์",
    "Sovereign Sacrifice": "การเสียสละขององค์ราชา",
    "Sorcery and Sleaze": "เวทมนตร์และความเสื่อมทราม",
    "An Abominable Intrusion": "การบุกรุกของอสูรหิมะ",
    "Unleashing the Legend": "ปลดปล่อยตำนานอันยิ่งใหญ่",
    "The Bigger They Come": "ยิ่งใหญ่ยักษ์ยิ่งล้มดัง",
    "All Hail Alena<FG>": "ขอคารวะองค์หญิงอารีน่า<FG>",
    "This War Ends Here and Now": "สงครามนี้ต้องยุติลงตรงนี้และเดี๋ยวนี้",
    "Your...Majesties<FH>": "ฝ่าบาท...ทั้ง 2 พระองค์<FH>",
    "Kitty in Pink": "เจ้าเหมียวสีชมพู",
    "All Doubts Dispelled": "คลายสิ้นทุกข้อกังขา",
    "Twin-King Tête-à-Tête": "เผชิญหน้าสองราชันย์",
    "Evil Unmasked": "เผยโฉมหน้าความชั่วร้าย",
    "What's Got into You<FG><FH>": "นี่มันเกิดอะไรขึ้นกับเจ้ากันแน่<FG><FH>",
    "Awakenings": "การตื่นรู้",
    "Facing Their Demons": "เผชิญหน้ากับปีศาจในจิตใจ",
    "Last Blast": "การระเบิดศึกครั้งสุดท้าย",
    "The End of the Beginning": "จุดสิ้นสุดของการเริ่มต้น",
    "A Prelude to Adventure": "โหมโรงสู่การผจญภัย",
    "Credits": "รายนามผู้สร้าง",
    "The Prophecy": "คำทำนายแห่งโชคชะตา",
}

def apply_translation():
    file_path = "text_csv/categories/entry_00141_Side_Quests.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for row in rows:
        eng = row["OriginalEnglish"].strip()
        if eng in QUEST_TITLES:
            row["ThaiTranslation"] = QUEST_TITLES[eng]
            updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} quest titles in entry_00141_Side_Quests.csv")

if __name__ == "__main__":
    apply_translation()
