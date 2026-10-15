# -*- coding: utf-8 -*-
"""
translate_key_items.py
Translates entry_00113_Key_Items.csv
"""

import csv

KEY_ITEMS = {
    0: ("กุญแจจอมโจร", "เครื่องมือชั้นยอดที่ช่วยให้คุณเปิดหีบสมบัติและประตูที่ลงกลอนไว้ได้"),
    1: ("อัญมณีรูร่า", "อัญมณีล้ำค่าสุดวิเศษที่ช่วยให้คุณเดินทางข้ามมิติอย่างรวดเร็วด้วยคาถารูร่า"),
    2: ("กล่องใส่เหรียญมอนสเตอร์", "กล่องสำหรับเก็บเหรียญเพื่อใช้เรียกเหล่าสหายสัตว์ประหลาดออกมาช่วยต่อสู้"),
    3: ("บัญชีรายชื่อลูกค้า", "เอกสารรายชื่อลูกค้ารายสำคัญของพ่อค้าคนหนึ่ง"),
    4: ("หนังสือผ่านทาง", "เอกสารอนุญาตให้ผู้ถือสามารถเดินทางเข้าสู่อาณาจักรดูนิเซียได้"),
    5: ("ศิลาฮอยมี่", "หินช่วยชีวิตที่ช่วยรักษาบาดแผลที่ได้รับในการต่อสู้"),
    6: ("ศิลาเบฮอยมี่", ""),
    7: ("ศิลาเบโฮม่า", ""),
    8: ("ศิลาเบโฮมาซุน", ""),
    9: ("อัญมณีเทนชันอินเกเนีย", "อัญมณีอันแยบยลแห่งอินเกเนียที่ช่วยปลุกเร้าเทนชันให้พลุ่งพล่าน"),
    10: ("แร่หินพลังอัลคาซาม", "แร่หินจากอัลคาซามที่ช่วยเพิ่มพูนเทนชัน"),
    11: ("ศิลาตรีเอกานุภาพ", "โบราณวัตถุในตำนานที่จำเป็นสำหรับการเข้ารับบททดสอบอันแสนเข็ญ"),
    12: ("ภาชนะปริศนา", "ภาชนะที่มีพลังพิเศษอันลึกลับซ่อนเร้นอยู่ภายใน"),
    13: ("ดวงใจแห่งแสงสว่าง", "อัญมณีศักดิ์สิทธิ์ที่สามารถขับไล่ความมืดมิดอันลึกดำดิ่งที่สุดได้"),
    14: ("ปลามงคลสมรส", "ปลาหายากจากฮาร์บาที่เปี่ยมล้นไปด้วยมนตร์วิเศษแห่งการครองเรือน"),
    15: ("ศิลาลาพิสเลเวลิ", "มีเพียงสัตว์ประหลาดเท่านั้นที่สามารถดึงพลังของหินเวทมนตร์นี้มาใช้ได้"),
    16: ("แหวนแห่งนักรบ", "สัญลักษณ์แห่งนักรบผู้เกรียงไกร...หรืออาจเป็นของหญิงสาวผู้รักสวยรักงาม"),
    17: ("ไม้เนื้อดี", "ไม้ท่อนแข็งแกร่งดั่งหินผาและหายากจากพงไพรไวลด์วูด"),
    18: ("เหรียญเล็ก", ""),
    19: ("เหรียญทอง", ""),
    20: ("ใบไม้อิกดราซิล", ""),
    21: ("ลูกแก้วโบนัส", ""),
    22: ("กุญแจปรอทเงิน", ""),
}

def apply_translation():
    file_path = "text_csv/categories/entry_00113_Key_Items.csv"
    with open(file_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys()

    updated = 0
    for slot_idx, (thai_name, thai_desc) in KEY_ITEMS.items():
        base_row = slot_idx * 8
        if base_row + 7 >= len(rows):
            continue

        chunk = rows[base_row:base_row+8]
        chunk[0]["ThaiTranslation"] = thai_name
        chunk[1]["ThaiTranslation"] = thai_name
        chunk[2]["ThaiTranslation"] = thai_desc
        chunk[3]["ThaiTranslation"] = thai_name
        # Articles in Thai are empty
        chunk[4]["ThaiTranslation"] = ""
        chunk[5]["ThaiTranslation"] = ""
        chunk[6]["ThaiTranslation"] = ""
        chunk[7]["ThaiTranslation"] = ""
        updated += 1

    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Updated {updated} key items in entry_00113_Key_Items.csv")

if __name__ == "__main__":
    apply_translation()
