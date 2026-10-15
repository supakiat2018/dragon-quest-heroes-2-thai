"""
translate_core_glossary.py
แปลหมวดหมู่คำศัพท์หลัก 4 ไฟล์แรกด้วยมือ (Authentic Dragon Quest Lore & Canon)
1. entry_00001_Characters_Main.csv (69 รายการ)
2. entry_00029_Vocations_Classes.csv (42 รายการ)
3. entry_00043_Kingdoms_Regions.csv (60 รายการ)
4. entry_00057_Spells.csv (8 รายการ)
และซิงค์ข้อมูลคำแปลทั้งหมดเข้าสู่ text_csv/dqh2_all_english_text.csv (Master CSV)
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "text_csv")
CATEGORIES_DIR = os.path.join(CSV_DIR, "categories")
MASTER_CSV = os.path.join(CSV_DIR, "dqh2_all_english_text.csv")

# 1. ตัวละครหลัก (Characters Main) - 23 ตัวละคร x 3 ช่องอ้างอิง = 69 บรรทัด
CHARACTERS_MAP = {
    "Lazarel": "ราเซล",
    "Teresa": "เทเรเซีย",
    "Cesar": "ซีซาร์",
    "Desdemona": "เดสเดโมน่า",
    "Alena": "อาลีน่า",
    "Kiryl": "คริฟต์",
    "Torneko": "ทอร์เนโก้",
    "Meena": "มีเนีย",
    "Maya": "มาเนีย",
    "Carver": "ฮัสซัน",
    "Terry": "เทอร์รี่",
    "Maribel": "มาริเบล",
    "Ruff": "กาโบ",
    "Angelo": "คูเคิล",
    "Jessica": "เจสสิก้า",
    "Luceus": "แอคท์",
    "Aurora": "เมียร์",
    "Doric": "ดิลค์",
    "Isla": "จูเลียตต้า",
    "Psaro": "พิซาโร่",
    "Bianca": "เบียงก้า",
    "Nera": "ฟลอร่า",
    "Yangus": "ยังกัส"
}

# 2. อาชีพและตัวย่ออาชีพ (Vocations Classes) - ชาย/หญิง x 7 อาชีพ x 3 ช่อง = 42 บรรทัด
VOCATIONS_MAP = {
    "Warrior": "นักรบ",
    "WAR": "รบ",
    "GUE": "รบ",
    "Martial Artist": "นักสู้",
    "MAR": "สู้",
    "LOT": "สู้",
    "Mage": "จอมเวท",
    "MAG": "เวท",
    "Priest": "นักบวช",
    "Priestess": "นักบวช",
    "PRI": "บวช",
    "SAC": "บวช",
    "Thief": "จอมโจร",
    "THI": "โจร",
    "LAD": "โจร",
    "Gladiator": "กลาดิเอเตอร์",
    "GLA": "กลาด",
    "Sage": "ปราชญ์",
    "SAG": "ปราชญ์"
}

# 3. เมือง อาณาจักร และภูมิภาค (Kingdoms Regions) - 30 คู่ = 60 บรรทัด
KINGDOMS_MAP = {
    "Harba": "ฮาร์บา",
    "Accordia": "ออร์คาเนีย",
    "Dunisia": "แจวาล",
    "Outer Dunisia": "ชานเมืองแจวาล",
    "The Wildwood": "ป่าดงพงไพร",
    "Ingenia": "อินจีเนีย",
    "The Great Divide": "หุบผาพรมแดน",
    "Mt Neverest": "ยอดเขาเนเวอร์เรสต์",
    "Greena Pastures": "ทุ่งหญ้ากรีน่า",
    "The Grand Dunes": "ทะเลทรายแกรนด์ดูนส์",
    "The Lumberlands": "พงไพรลัมเบอร์แลนด์",
    "Redrock Ravine": "หุบผาหินแดงเรดร็อค",
    "The Frosty Foothills": "เนินเขาเยือกแข็งฟรอสตี้",
    "No Man's Land": "แดนรกร้างไร้เจ้าของ",
    "Blacka Pastures": "ทุ่งทมิฬแบล็คก้า",
    "The Damned Dunes": "ทะเลทรายต้องสาป",
    "The Darkwood": "ป่าดงทมิฬ",
    "Blackrock Ravine": "หุบผาหินดำแบล็คร็อค",
    "The Fetid Foothills": "เนินเขากลิ่นเน่าเฟรติด",
    "Dead Man's Land": "แดนมรณะ",
    "The Pinnacle of Peace": "ยอดเขาสันติภาพ",
    "Ad Hoc Encampment": "ค่ายพักชั่วคราว",
    "The Beastlands": "แดนสัตว์อสูร",
    "Klor": "คลอร์",
    "Kadava": "คาดาวา",
    "Al-Khazam": "อัล-คาซัม",
    "The Black Manse": "คฤหาสน์ทมิฬ",
    "Gragwort's Grotto": "ถ้ำของแกรกเวิร์ต",
    "Unused": "ไม่ได้ใช้งาน"
}

# 4. คาถาฟื้นพลัง (Spells) - 4 คาถา x 2 ช่อง = 8 บรรทัด
SPELLS_MAP = {
    "Heal": "โฮอิมี่",
    "Midheal": "เบโฮอิมี่",
    "Moreheal": "เบโฮอิม",
    "Fullheal": "เบโฮม่า"
}

def translate_file(filepath, mapping):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        reader = list(csv.reader(f))
    
    header = reader[0]
    rows = reader[1:]
    count = 0
    
    for row in rows:
        eng = row[5]
        if eng in mapping:
            row[6] = mapping[eng]
            count += 1
            
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
        
    return count, rows

def sync_master_csv(all_translated_rows):
    """นำคำแปลทั้งหมดไปอัปเดตใส่ dqh2_all_english_text.csv"""
    # Key: (EntryID, StringIndex) -> ThaiTranslation
    lookup = {}
    for row in all_translated_rows:
        entry_id = int(row[0])
        str_idx = int(row[2])
        thai = row[6]
        if thai:
            lookup[(entry_id, str_idx)] = thai
            
    with open(MASTER_CSV, "r", encoding="utf-8-sig", newline="") as f:
        master_reader = list(csv.reader(f))
        
    header = master_reader[0]
    master_rows = master_reader[1:]
    sync_count = 0
    
    for row in master_rows:
        entry_id = int(row[0])
        str_idx = int(row[2])
        if (entry_id, str_idx) in lookup:
            row[6] = lookup[(entry_id, str_idx)]
            sync_count += 1
            
    with open(MASTER_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(master_rows)
        
    return sync_count

def main():
    print("=" * 60)
    print("เริ่มการแปลหมวดหมู่คำศัพท์หลัก 4 ไฟล์ (Authentic Dragon Quest Lore)")
    print("=" * 60)
    
    tasks = [
        (os.path.join(CATEGORIES_DIR, "entry_00001_Characters_Main.csv"), CHARACTERS_MAP, "Characters_Main"),
        (os.path.join(CATEGORIES_DIR, "entry_00029_Vocations_Classes.csv"), VOCATIONS_MAP, "Vocations_Classes"),
        (os.path.join(CATEGORIES_DIR, "entry_00043_Kingdoms_Regions.csv"), KINGDOMS_MAP, "Kingdoms_Regions"),
        (os.path.join(CATEGORIES_DIR, "entry_00057_Spells.csv"), SPELLS_MAP, "Spells"),
    ]
    
    all_translated = []
    total_translated = 0
    
    for path, mapping, name in tasks:
        count, rows = translate_file(path, mapping)
        print(f"[{name}] แปลเรียบร้อยแล้ว: {count} บรรทัด")
        total_translated += count
        all_translated.extend(rows)
        
    print("-" * 60)
    print(f"รวมคำแปลใน 4 หมวดหมู่: {total_translated} บรรทัด")
    
    # ซิงค์เข้า Master CSV
    sync_count = sync_master_csv(all_translated)
    print(f"[Master CSV] อัปเดตซิงค์คำแปลเข้า dqh2_all_english_text.csv: {sync_count} บรรทัด")
    print("=" * 60)
    print("การแปล 4 หมวดหมู่อ้างอิงหลักเสร็จสมบูรณ์ 100%!")

if __name__ == "__main__":
    main()
