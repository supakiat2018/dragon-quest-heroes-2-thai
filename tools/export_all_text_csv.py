"""
export_all_text_csv.py
สคริปต์สแกนและดึงข้อความภาษาอังกฤษทั้งหมด (51 รายการ, 21,653 บรรทัด, 146,717 คำ)
จาก DRAGON QUEST HEROES™ II (LINKDATA.BIN)
ส่งออกเป็นไฟล์ CSV (UTF-8 with BOM) สำหรับนำไปแปลภาษาไทยได้ง่ายผ่าน Excel หรือ Google Sheets
"""

import os
import sys
import csv
import struct
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
from find_text import decompress_entry

IDX_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.IDX"
BIN_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\LINKDATA.BIN"

OUT_DIR = os.path.join(BASE_DIR, "workspace", "extracted_csv")
OUT_MASTER_CSV = os.path.join(BASE_DIR, "workspace", "dqh2_all_english_text.csv")
OUT_SUMMARY_CSV = os.path.join(BASE_DIR, "workspace", "dqh2_entries_summary.csv")

# รายการ 51 Entry ภาษาอังกฤษทั้งหมดในเกมพร้อมหมวดหมู่ (Category)
ENGLISH_ENTRIES_INFO = {
    1:     "Characters_Main",
    8:     "NPC_Titles",
    15:    "Monsters",
    22:    "Heroes_Party",
    29:    "Vocations_Classes",
    36:    "Story_Quests",
    43:    "Kingdoms_Regions",
    50:    "Areas_Wilderness",
    57:    "Spells",
    64:    "Weapon_Categories",
    71:    "Weapons_Equipment",
    78:    "Orbs",
    85:    "Accessory_Types",
    92:    "Accessories",
    99:    "Stats_Attributes",
    106:   "Materials_Items",
    113:   "Key_Items",
    120:   "Abilities_Skills",
    127:   "Skill_Types",
    134:   "Party_Vocations",
    141:   "Side_Quests",
    148:   "Dungeons_Mazes",
    155:   "Menu_Categories",
    162:   "System_Help",
    169:   "Accolades_Trophies",
    176:   "Battle_Perks",
    183:   "Combat_Tutorials",
    190:   "Character_Index",
    197:   "Location_Lore",
    204:   "Menus_UI_Settings",
    211:   "Battle_Guides_Tutorials",
    218:   "Dungeon_Prompts",
    225:   "Battle_Announcements",
    232:   "Boundary_Alerts",
    239:   "Mission_Objectives",
    246:   "Main_Story_Cutscenes_Dialogues",
    253:   "Monster_Medals",
    260:   "Side_Quest_Rumours",
    267:   "Monster_Lore_Bestiary",
    274:   "Feature_Unlocks",
    281:   "Party_Battle_Banter",
    288:   "Tavern_Online_Lobby",
    295:   "Monster_Nicknames",
    302:   "Monster_Transformations",
    309:   "Transformation_Attacks",
    316:   "PC_Config_Tool",
    323:   "Keyboard_Gamepad_Controls",
    518:   "DLC_Epilogue_Stories",
    11652: "Adventurer_Arena",
    11666: "Dungeon_Master_Prompts",
    11673: "Hocus_Pocus_Medals"
}

def parse_message_entry(chunk):
    """
    ถอดรหัสไฟล์ข้อความ Koei Tecmo (Magic 0x01)
    คืนค่ารายการ: (string_index, ptr_file_offset, str_file_offset, raw_str_bytes)
    """
    if len(chunk) < 32 or not chunk.startswith(b"\x01\x00\x00\x00\x0c\x00\x00\x00"):
        return None

    ptr_field = struct.unpack_from("<I", chunk, 0x18)[0]
    ptr_start = 0x0C + ptr_field
    if ptr_start >= len(chunk):
        return None

    first_rel = struct.unpack_from("<I", chunk, ptr_start)[0]
    if first_rel == 0 or first_rel > len(chunk):
        return None

    num_ptrs = first_rel // 4
    if num_ptrs == 0 or num_ptrs > 50000:
        return None

    results = []
    for idx in range(num_ptrs):
        ptr_file_off = ptr_start + idx * 4
        rel_off = struct.unpack_from("<I", chunk, ptr_file_off)[0]
        if rel_off == 0:
            continue
        str_file_off = ptr_start + rel_off
        if str_file_off >= len(chunk):
            continue
        end = chunk.find(b"\x00", str_file_off)
        if end == -1:
            end = len(chunk)
        raw_bytes = chunk[str_file_off:end]
        results.append((idx, ptr_file_off, str_file_off, raw_bytes))

    return results

import re

def escape_text_for_csv(raw_bytes):
    """
    แปลงข้อความเป็นสตริงพร้อมถอดรหัส Escape Code ให้อ่านและแปลง่าย
    """
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1", "replace")

    # แปลงแท็กควบคุม \x1bXX เป็น <XX> (เช่น \x1bFH -> <FH>, \x1bFG -> <FG>)
    text = re.sub(r'\x1b(..)', r'<\1>', text)
    # แปลงขึ้นบรรทัดใหม่ให้เป็น \n เพื่อให้อยู่ในบรรทัดเดียวกันใน CSV
    text = text.replace('\r\n', '\\n').replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
    return text


def main():
    print("=================================================================")
    print("[*] Dragon Quest Heroes II - Complete English Text Extractor")
    print("=================================================================")

    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"[*] Reading LINKDATA.IDX from: {IDX_PATH}")
    with open(IDX_PATH, "rb") as f_idx:
        idx_data = f_idx.read()
    total_idx_entries = len(idx_data) // 32
    entries_meta = [struct.unpack("<QQQQ", idx_data[i*32:(i+1)*32]) for i in range(total_idx_entries)]
    print(f"[+] Total entries in IDX: {total_idx_entries:,}")

    master_rows = []
    summary_rows = []

    total_lines = 0
    total_words = 0
    start_time = time.time()

    with open(BIN_PATH, "rb") as f_bin:
        for num, (eid, cat) in enumerate(ENGLISH_ENTRIES_INFO.items(), 1):
            if eid >= len(entries_meta):
                print(f"[-] Entry {eid} out of bounds")
                continue

            off, size, zsize, zip_flag = entries_meta[eid]
            chunk = decompress_entry(f_bin, off, size, zsize, zip_flag)
            parsed = parse_message_entry(chunk)

            if not parsed:
                print(f"[-] Entry {eid} ({cat}): Failed to parse message format")
                continue

            entry_rows = []
            non_empty_count = 0
            word_count = 0
            sample_text = ""

            for str_idx, ptr_off, str_off, raw_bytes in parsed:
                txt = escape_text_for_csv(raw_bytes)
                if txt.strip():
                    non_empty_count += 1
                    words = len(txt.split())
                    word_count += words
                    if not sample_text:
                        sample_text = txt[:50]

                row = [
                    eid,
                    cat,
                    str_idx,
                    ptr_off,
                    str_off,
                    txt,
                    "" # ThaiTranslation (เว้นว่างไว้ให้ผู้ใช้แปล)
                ]
                entry_rows.append(row)
                master_rows.append(row)

            total_lines += non_empty_count
            total_words += word_count

            # บันทึกไฟล์ CSV แยกเฉพาะ Entry นี้
            out_single_csv = os.path.join(OUT_DIR, f"entry_{eid:05d}_{cat}.csv")
            with open(out_single_csv, "w", newline="", encoding="utf-8-sig") as f_single:
                writer = csv.writer(f_single)
                writer.writerow(["EntryID", "Category", "StringIndex", "PointerOffset", "StringOffset", "OriginalEnglish", "ThaiTranslation"])
                writer.writerows(entry_rows)

            summary_rows.append([
                eid,
                cat,
                len(entry_rows),
                non_empty_count,
                word_count,
                sample_text
            ])

            print(f"[{num:2d}/51] Entry {eid:5d} ({cat:<30s}): {non_empty_count:4d} lines, {word_count:5d} words")

    # บันทึก Master CSV รวมทุก Entry
    print(f"\n[*] Writing Master CSV to: {OUT_MASTER_CSV}")
    with open(OUT_MASTER_CSV, "w", newline="", encoding="utf-8-sig") as f_master:
        writer = csv.writer(f_master)
        writer.writerow(["EntryID", "Category", "StringIndex", "PointerOffset", "StringOffset", "OriginalEnglish", "ThaiTranslation"])
        writer.writerows(master_rows)

    # บันทึก Summary CSV สรุปสารบัญทั้ง 51 หมวดหมู่
    print(f"[*] Writing Summary CSV to: {OUT_SUMMARY_CSV}")
    with open(OUT_SUMMARY_CSV, "w", newline="", encoding="utf-8-sig") as f_sum:
        writer = csv.writer(f_sum)
        writer.writerow(["EntryID", "Category", "TotalSlots", "NonEmptyLines", "WordCount", "SampleText"])
        writer.writerows(summary_rows)

    elapsed = time.time() - start_time
    print("=================================================================")
    print(f"[SUCCESS] Extracted all English text in {elapsed:.2f} seconds!")
    print(f"[+] Total English Entries: {len(ENGLISH_ENTRIES_INFO)}")
    print(f"[+] Total Text Rows Extracted: {len(master_rows):,}")
    print(f"[+] Total Meaningful Text Lines: {total_lines:,}")
    print(f"[+] Total English Words: {total_words:,}")
    print(f"[+] Master CSV: {OUT_MASTER_CSV}")
    print(f"[+] Summary Catalog: {OUT_SUMMARY_CSV}")
    print(f"[+] Folder with individual CSVs: {OUT_DIR}")
    print("=================================================================")

if __name__ == "__main__":
    main()
