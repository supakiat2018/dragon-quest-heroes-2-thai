"""
build_dqh2_addon.py
สคริปต์สร้างไฟล์แพ็กเกจฟอนต์และข้อความภาษาไทยภายนอก (dqh2_font_addons.bin)
โดยไม่ต้องแก้ไขไฟล์ LINKDATA.BIN บนดิสก์เลยแม้แต่ไบต์เดียว!

ประกอบด้วย:
1. Entry 204: ข้อความเมนูหลัก 7 เมนู + ประโยคคำถาม Save Slot แบบรวมพยางค์ชิดสนิท
2. Entry 341: ฟอนต์หลักในเกมขนาด 4096x8192 บรรจุอักขระไทยและ Ligature พยางค์ชิด
3. Entry 342: ฟอนต์เมนูไตเติลขนาด 1024x1024 บรรจุอักขระไทย
"""

import os
import sys
import struct
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from mod_en_thai_menus import SLOTS, TARGET_MENUS, render_unstretched_glyph, FONT_TTF, patch_font_sheet
from test_cell_encoder import encode_cell_dxt5
from inject_inplace import pack_entry_chunks

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
OUT_ADDON = os.path.join(GAME_DIR, "dqh2_font_addons.bin")

# อักขระ Cyrillic ใน entry_341
CYR_UPPER_341 = [chr(0x0410 + i) for i in range(32)]
CYR_UPPER_341.insert(6, chr(0x0401)) # Ё

CYR_LOWER_341 = [chr(0x0430 + i) for i in range(32)]
CYR_LOWER_341.insert(6, chr(0x0451)) # ё

def get_341_cell(char):
    if char in CYR_UPPER_341:
        idx = CYR_UPPER_341.index(char)
        return (8, 19 + idx)
    elif char in CYR_LOWER_341:
        idx = CYR_LOWER_341.index(char)
        return (8, 52 + idx)
    else:
        raise ValueError(f"Char {char} not found in Cyrillic alphabet")

def build_entry_341():
    print("[*] Building Entry 341 (Main Dialogue Font - 100% Single Natural Characters)...")
    with open(os.path.join(BASE_DIR, "backup", "entry_341_original.g1t"), "rb") as f:
        g1t_data = bytearray(f.read())
        
    font_std = ImageFont.truetype(FONT_TTF, 30)
    G1T_HEADER_SIZE = 56
    SCANBAND_BYTES = 1024 * 16 # 16384 bytes
    
    # วาด 29 อักขระมาตรฐานธรรมชาติ 100% ด้วย Baseline ที่เท่ากันทุกตัว
    for token, slot in SLOTS.items():
        ch = slot['char']
        r, c = get_341_cell(ch)
        cell_img = render_unstretched_glyph(font_std, token, slot)
        dxt_rows = encode_cell_dxt5(cell_img)
        bx = c * 9
        by = r * 9
        for dy in range(9):
            offset = G1T_HEADER_SIZE + (by + dy) * SCANBAND_BYTES + bx * 16
            g1t_data[offset : offset + 144] = dxt_rows[dy]
            
    print("[*] Compressing Entry 341 chunks...")
    packed = pack_entry_chunks(g1t_data)
    print(f"[+] Entry 341 packed size: {len(packed)} bytes")
    return packed

def build_entry_342():
    print("[*] Building Entry 342 (Menu Font - 100% Single Natural Characters)...")
    patch_font_sheet()
    path_342 = os.path.join(BASE_DIR, "workspace", "tex_342", "out", "entry_342.g1t")
    with open(path_342, "rb") as f:
        g1t_data = bytearray(f.read())

    packed = pack_entry_chunks(bytes(g1t_data))
    print(f"[+] Entry 342 packed size: {len(packed)} bytes")
    return packed

def build_entry_204():
    print("[*] Building Entry 204 (English Text with Thai Menus & Tight Dialogue)...")
    with open(os.path.join(BASE_DIR, "backup", "entry_204_original.bin"), "rb") as f:
        data = bytearray(f.read())
        
    ORIG_SIZE = len(data) # 86768
    
    # 1. เมนูหลัก 7 รายการบนไตเติล
    menus_6 = [
        {'off': 4032, 'tokens': ['เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'เ', 'ดิ', 'น', 'ท', 'า', 'ง']},
        {'off': 4036, 'tokens': ['ส', 'ร้', 'า', 'ง', 'บั', 'น', 'ทึ', 'ก']},
        {'off': 4040, 'tokens': ['ล', 'บ', 'บั', 'น', 'ทึ', 'ก']},
        {'off': 6800, 'tokens': ['ตั้', 'ง', 'ค่', 'า', 'ก', 'ร', 'า', 'ฟิ', 'ก']},
        {'off': 6804, 'tokens': ['ตั้', 'ง', 'ค่', 'า', 'คี', 'ย์', 'บ', 'อ', 'ร์', 'ด']},
        {'off': 7092, 'tokens': ['ตั้', 'ง', 'ค่', 'า', 'เ', 'ม', 'า', 'ส์']},
        {'off': 6808, 'tokens': ['อ', 'อ', 'ก', 'จ', 'า', 'ก', 'เ', 'ก', 'ม']},
    ]
    
    # 2. ประโยคคำถาม Save/Load แบบอักขระเดี่ยวมาตรฐาน (No PUA Ligatures)
    # ต้ อ ง ก า ร ส ร้ า ง บั น ทึ ก ก า ร เ ดิ น ท า ง ใ น ช่ อ ง ใ ด ?
    dialogue_tokens_std = [
        'ต้', 'อ', 'ง', 'ก', 'า', 'ร',
        'ส', 'ร้', 'า', 'ง',
        'บั', 'น', 'ทึ', 'ก',
        'ก', 'า', 'ร',
        'เ', 'ดิ', 'น', 'ท', 'า', 'ง',
        'ใ', 'น',
        'ช่', 'อ', 'ง',
        'ใ', 'ด'
    ]
    dialogue_cyr_str = "".join(SLOTS[t]['char'] if t in SLOTS else t for t in dialogue_tokens_std)
    dialogue_utf8 = dialogue_cyr_str.encode('utf-8') + b"\x1bFH\x00"

    # 1. เขียนเมนู 1, 2, 3 ในบล็อกว่าง 79264..79332 (71 ไบต์)
    cur_off = 79264
    for m in menus_6[:3]:
        cyr_str = "".join(SLOTS[t]['char'] for t in m['tokens'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1

    # 2. เขียนเมนู 4, 5, 6, 7 ในบล็อกว่าง 86672..86768 (97 ไบต์)
    cur_off = 86672
    for m in menus_6[3:]:
        cyr_str = "".join(SLOTS[t]['char'] for t in m['tokens'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1

    # 3. เขียน Dialogue Prompt ในบล็อก Unused ว่างขนาด 2,115 ไบต์ที่ตำแหน่ง 66624
    pos_dialogue = 66624
    data[pos_dialogue : pos_dialogue + len(dialogue_utf8)] = dialogue_utf8
    struct.pack_into("<I", data, 32, pos_dialogue - 0x20)
    
    assert len(data) == ORIG_SIZE, f"Size changed: {len(data)} != {ORIG_SIZE}"
    print(f"[+] Entry 204 successfully created ({len(data)} bytes, 100% fits in original slot)")
    return bytes(data)

def main():
    print("==========================================================")
    print("[*] Building DQH2 Thai Addon Package (dqh2_font_addons.bin)")
    print("==========================================================")
    
    data_204 = build_entry_204()
    data_341 = build_entry_341()
    data_342 = build_entry_342()
    
    # Structure of dqh2_font_addons.bin:
    # Header:
    #   magic: 8 bytes "DQH2THAI"
    #   num_entries: uint32 (3)
    # For each entry:
    #   entry_id: uint32
    #   linkdata_offset: uint64
    #   linkdata_size: uint64
    #   data_len: uint64
    #   data_bytes: [data_len]
    
    entries = [
        (204, 2250752, 86768, data_204),
        (341, 45149440, 1539328, data_341),
        (342, 46688768, 47616, data_342)
    ]
    
    buf = bytearray()
    buf.extend(b"DQH2THAI")
    buf.extend(struct.pack("<I", len(entries)))
    
    for eid, off, sz, d in entries:
        buf.extend(struct.pack("<IQQQ", eid, off, sz, len(d)))
        buf.extend(d)
        
    with open(OUT_ADDON, "wb") as f:
        f.write(buf)
        
    print(f"\n[SUCCESS] Generated: {OUT_ADDON} ({len(buf)} bytes, ~{len(buf)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    main()
