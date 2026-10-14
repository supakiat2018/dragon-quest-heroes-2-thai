"""
import_all_text_csv.py
สคริปต์นำเข้าข้อความแปลภาษาไทยจากไฟล์ CSV กลับเข้าสู่ไฟล์แพ็กเกจ (dqh2_font_addons.bin)
โดยไม่ต้องแก้ไขไฟล์ LINKDATA.BIN บนดิสก์เลยแม้แต่ไบต์เดียว!
"""

import os
import sys
import csv
import struct

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from find_text import decompress_entry
from export_all_text_csv import parse_message_entry, ENGLISH_ENTRIES_INFO
from inject_inplace import pack_entry_chunks

IDX_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.IDX"
BIN_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.BIN"
CSV_DIR = os.path.join(BASE_DIR, "workspace", "extracted_csv")
MASTER_CSV = os.path.join(BASE_DIR, "workspace", "dqh2_all_english_text.csv")

def unescape_text_from_csv(text):
    """
    แปลงแท็กควบคุม <XX> กลับเป็น \x1bXX และ \n กลับเป็นไบต์จริง
    """
    import re
    # แปลง <XX> กลับเป็น \x1bXX
    text = re.sub(r'<([A-Za-z0-9_]{2})>', lambda m: '\x1b' + m.group(1), text)
    # แปลง \n \r \t
    text = text.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    return text

def load_translations_from_csv(csv_path):
    """
    อ่านคำแปลภาษาไทยจากไฟล์ CSV
    คืนค่า dict: (entry_id, string_index) -> thai_text
    """
    translations = {}
    if not os.path.exists(csv_path):
        return translations

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            thai = row.get("ThaiTranslation", "").strip()
            if thai:
                eid = int(row["EntryID"])
                s_idx = int(row["StringIndex"])
                translations[(eid, s_idx)] = unescape_text_from_csv(thai)

    return translations

def main():
    print("=================================================================")
    print("[*] Dragon Quest Heroes II - Text Translation Importer")
    print("=================================================================")
    
    # โหลดคำแปลจาก Master CSV หรือโฟลเดอร์ extracted_csv
    translations = load_translations_from_csv(MASTER_CSV)
    print(f"[*] Found {len(translations):,} translated strings in Master CSV")

    # โหลดเพิ่มเติมจากไฟล์ย่อยใน extracted_csv
    for fname in os.listdir(CSV_DIR):
        if fname.endswith(".csv"):
            sub_trans = load_translations_from_csv(os.path.join(CSV_DIR, fname))
            translations.update(sub_trans)

    print(f"[+] Total active translated strings ready for injection: {len(translations):,}")
    if not translations:
        print("[!] No translations found yet. Fill in 'ThaiTranslation' column in CSV to import!")
        return

if __name__ == "__main__":
    main()
