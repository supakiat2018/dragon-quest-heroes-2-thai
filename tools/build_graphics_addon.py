"""
build_graphics_addon.py
สคริปต์สร้างไฟล์แพ็กเกจฟอนต์และข้อความภาษาไทยภายนอก (dqh2_font_addons.bin)
แก้ปัญหาสระ ำ (ต่ำ, ลำ, จำ, กำ) 100% ไม่ให้แยกวงกลมลอยและไม่มีช่องว่าง
พร้อมฉีดคำแปลภาษาไทยครบทุกเมนู ทุกตัวเลือกหน้าตั้งค่ากราฟิก และหน้าต่างเลือกผู้กล้า!
"""

import os
import sys
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from exact_cyrillic_table import CYR_MAP
from test_cell_encoder import encode_cell_dxt5
from inject_inplace import pack_entry_chunks
from draw_thai_glyphs import encode_dxt5_white, make_dds_file

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
OUT_ADDON = os.path.join(GAME_DIR, "dqh2_font_addons.bin")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")
OUT_G1T = os.path.join(TEX_DIR, "out", "entry_342.g1t")
ORIG_PNG = os.path.join(BASE_DIR, "backup", "entry_342_original.png")
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")

CELL_SIZE = 36
TARGET_BASELINE = 31
FONT_SIZE = 30

CYR_CHARS = list(CYR_MAP.keys())
assert len(CYR_CHARS) == 66, f"Expected 66 Cyrillic characters, got {len(CYR_CHARS)}"

# 1. นิยามโทเค็น 66 ตัว (18 Ligatures + 48 Base)
# Sara Am (ต่ำ, ลำ, จำ, กำ) ถูกรวมเป็น Ligature ชิ้นเดียว เพื่อไม่ให้สระ ำ แยกเป็นวงกลมลอย!
LIGATURES = [
    ('ต่ำ', 26.0), ('ลำ', 26.0), ('จำ', 25.0), ('กำ', 26.0),
    ('ตั้', 20.0), ('ริ่', 16.0), ('ดิ', 19.0), ('ค่', 19.0), ('คี', 19.0),
    ('ฟิ', 19.0), ('ทึ', 19.0), ('บั', 20.0), ('ย์', 20.0), ('ส์', 20.0),
    ('ต้', 19.0), ('ช่', 18.0), ('ร้', 17.0), ('ร์', 17.0),
]

BASE_CHARS = [
    ('ก', 19.0), ('ข', 18.0), ('ค', 18.0), ('ง', 17.0), ('จ', 17.0),
    ('ฉ', 18.0), ('ช', 18.0), ('ญ', 24.0), ('ณ', 24.0), ('ด', 19.0),
    ('ต', 17.0), ('ถ', 18.0), ('ท', 19.0), ('ธ', 18.0), ('น', 19.0),
    ('บ', 19.0), ('ป', 18.0), ('ผ', 18.0), ('พ', 18.0), ('ฟ', 18.0),
    ('ภ', 18.0), ('ม', 19.0), ('ย', 18.0), ('ร', 16.0), ('ล', 18.0),
    ('ว', 14.0), ('ศ', 18.0), ('ส', 19.0), ('ห', 18.0), ('อ', 18.0),
    ('ะ', 14.0), ('ั', 14.0), ('า', 15.0), ('ิ', 14.0), ('ี', 14.0),
    ('ึ', 14.0), ('ื', 14.0), ('ุ', 14.0), ('ู', 14.0), ('เ', 11.0),
    ('แ', 17.0), ('โ', 14.0), ('ใ', 14.0), ('ไ', 15.0), ('็', 14.0),
    ('่', 14.0), ('้', 14.0), ('์', 14.0)
]

ALL_TOKENS_LIST = LIGATURES + BASE_CHARS
assert len(ALL_TOKENS_LIST) == 66, f"Total tokens must be exactly 66, got {len(ALL_TOKENS_LIST)}"

SLOTS = {}
for i, (tok, w) in enumerate(ALL_TOKENS_LIST):
    ch = CYR_CHARS[i]
    cell = CYR_MAP[ch]
    SLOTS[tok] = {
        'char': ch,
        'cell': cell,
        'w': w
    }

SORTED_TOKENS = sorted(SLOTS.keys(), key=len, reverse=True)

def encode_thai_string(s):
    res = []
    i = 0
    while i < len(s):
        matched = False
        for t in SORTED_TOKENS:
            if s.startswith(t, i):
                res.append(SLOTS[t]['char'])
                i += len(t)
                matched = True
                break
        if not matched:
            res.append(s[i])
            i += 1
    return "".join(res)

def render_unstretched_glyph(font, token):
    """
    วาด Glyph ลงบน Cell 36x36 ด้วย baseline 31
    กรณี 'ตั้' และ 'ริ่' ยกระดับวรรณยุกต์ขึ้นไม่ให้ชนสระ
    กรณี 'ต่ำ' วาดเป็น Ligature ชิ้นเดียวสมบูรณ์แบบ
    """
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    
    if token == 'ตั้':
        d.text((2, TARGET_BASELINE), 'ตั', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_t = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_t = ImageDraw.Draw(temp_t)
        d_t.text((25, 25), '้', font=f_tone, fill=(255, 255, 255, 255))
        arr_t = np.array(temp_t)[:, :, 3]
        coords = np.argwhere(arr_t > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_tho = temp_t.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_tho, (14, 0), crop_tho)
        return cell
    elif token == 'ริ่':
        d.text((2, TARGET_BASELINE), 'ริ', font=font, fill=(255, 255, 255, 255), anchor='ls')
        f_tone = ImageFont.truetype(FONT_TTF, 18)
        temp_ek = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        d_ek = ImageDraw.Draw(temp_ek)
        d_ek.text((25, 25), '่', font=f_tone, fill=(255, 255, 255, 255))
        arr_ek = np.array(temp_ek)[:, :, 3]
        coords = np.argwhere(arr_ek > 20)
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        crop_ek = temp_ek.crop((min_x, min_y, max_x + 1, max_y + 1))
        cell.paste(crop_ek, (11, 2), crop_ek)
        return cell
    else:
        bbox = font.getbbox(token)
        draw_x = 2 - min(0, bbox[0])
        d.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
        return cell

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
    print("[*] Building Entry 341 (Main Dialogue Font - 66 Thai Glyphs)...")
    with open(os.path.join(BASE_DIR, "backup", "entry_341_original.g1t"), "rb") as f:
        g1t_data = bytearray(f.read())
        
    font_std = ImageFont.truetype(FONT_TTF, 30)
    G1T_HEADER_SIZE = 56
    SCANBAND_BYTES = 1024 * 16 # 16384 bytes
    
    for token, slot in SLOTS.items():
        ch = slot['char']
        r, c = get_341_cell(ch)
        cell_img = render_unstretched_glyph(font_std, token)
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
    print("[*] Building Entry 342 (Menu Font - 66 Thai Glyphs with Perfect Sara Am)...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)
    
    for token, slot in SLOTS.items():
        row, col = slot['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        glyph_cell = render_unstretched_glyph(font, token)
        
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        
    preview_path = os.path.join(TEX_DIR, "entry_342_thai_natural.png")
    img.save(preview_path)
    
    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)
        
    out_dir = os.path.join(TEX_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, out_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    
    with open(OUT_G1T, "rb") as f:
        g1t_data = f.read()
        
    packed = pack_entry_chunks(g1t_data)
    print(f"[+] Entry 342 packed size: {len(packed)} bytes")
    return packed

def build_entry_204():
    print("[*] Building Entry 204 with Full Menus, Hero Select, and Graphics Settings...")
    with open(os.path.join(BASE_DIR, "backup", "entry_204_original.bin"), "rb") as f:
        data = bytearray(f.read())
        
    ORIG_SIZE = len(data) # 86768
    
    # 1. Title Menus 1, 2, 3 (block 79264..79332)
    menus_123 = [
        {'off': 4032, 'text': 'เริ่มการเดินทาง'},
        {'off': 4036, 'text': 'สร้างบันทึก'},
        {'off': 4040, 'text': 'ลบบันทึก'},
    ]
    cur_off = 79264
    for m in menus_123:
        cyr_str = encode_thai_string(m['text'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1
        
    # 2. Title Menus 4, 5, 6, 7 (block 86672..86768)
    menus_4567 = [
        {'off': 6800, 'text': 'ตั้งค่ากราฟิก'},
        {'off': 6804, 'text': 'ตั้งค่าคีย์บอร์ด'},
        {'off': 7092, 'text': 'ตั้งค่าเมาส์'},
        {'off': 6808, 'text': 'ออกจากเกม'},
    ]
    cur_off = 86672
    for m in menus_4567:
        cyr_str = encode_thai_string(m['text'])
        utf8 = cyr_str.encode('utf-8') + b"\x00"
        data[cur_off : cur_off + len(utf8)] = utf8
        struct.pack_into("<I", data, m['off'], cur_off - 0x20)
        cur_off = (cur_off + len(utf8) + 1) & ~1

    # 3. Save prompt, Hero Selection, and All Graphics Settings (block 66624..68700)
    all_target_options = [
        # Save prompt
        {'off': 32,   'text': 'ต้องการสร้างบันทึกการเดินทางในช่องใด?', 'suffix': b'\x1bFH\x00'},
        
        # Hero Selection Dialogue & Prompts
        {'off': 40,   'text': 'เอาล่ะ โปรดเลือกผู้กล้าที่จะควบคุมในการผจญภัยในโลกนี้ การเลือกนี้จะไม่มีผลต่อเนื้อหาที่จะเข้าถึงได้ในเกม', 'suffix': b'\x00'},
        {'off': 44,   'text': 'โปรดเลือกผู้กล้า', 'suffix': b'\x00'},
        {'off': 48,   'text': 'ต่อไป โปรดตั้งชื่อให้แก่ผู้กล้าที่จะร่วมเดินทางไปด้วยกัน', 'suffix': b'\x00'},
        
        # All Graphics Settings Options & Values
        {'off': 4108, 'text': 'ยืนยัน', 'suffix': b'\x00'},
        {'off': 4628, 'text': 'คืนค่าเริ่มต้น', 'suffix': b'\x00'},
        {'off': 6812, 'text': 'แสดงผลเต็มจอ', 'suffix': b'\x00'},
        {'off': 6816, 'text': 'ความละเอียด', 'suffix': b'\x00'},
        {'off': 6820, 'text': 'เฟรมเรต', 'suffix': b'\x00'},
        {'off': 6824, 'text': 'คุณภาพกราฟิก', 'suffix': b'\x00'},
        {'off': 6828, 'text': '  จำนวนตัวละคร', 'suffix': b'\x00'},
        {'off': 6832, 'text': '  ระยะแสดงผล', 'suffix': b'\x00'},
        {'off': 6836, 'text': '  คุณภาพพื้นผิว', 'suffix': b'\x00'},
        {'off': 6840, 'text': '  คุณภาพเงา', 'suffix': b'\x00'},
        {'off': 6844, 'text': '  มิติแสงเงา', 'suffix': b'\x00'},
        {'off': 6848, 'text': '  การสะท้อนแสง', 'suffix': b'\x00'},
        {'off': 6852, 'text': '  ลำแสงส่องกระทบ', 'suffix': b'\x00'},
        {'off': 6856, 'text': '  ละอองอนุภาค', 'suffix': b'\x00'},
        {'off': 6860, 'text': '  แสงธรรมชาติรอบทิศทาง', 'suffix': b'\x00'},
        {'off': 6864, 'text': 'เลือกว่าจะแสดงผลแบบเต็มหน้าจอหรือแบบหน้าต่าง', 'suffix': b'\x00'},
        {'off': 6928, 'text': 'เปิด', 'suffix': b'\x00'},
        {'off': 6932, 'text': 'ปิด', 'suffix': b'\x00'},
        {'off': 6936, 'text': 'สูง', 'suffix': b'\x00'},
        {'off': 6940, 'text': 'ปานกลาง', 'suffix': b'\x00'},
        {'off': 6944, 'text': 'ต่ำ', 'suffix': b'\x00'},
        {'off': 6948, 'text': 'กำหนดเอง', 'suffix': b'\x00'},
        {'off': 7192, 'text': 'เปลี่ยนความละเอียด', 'suffix': b'\x00'},
        {'off': 7228, 'text': '  หมอกเชิงปริมาตร', 'suffix': b'\x00'},
        {'off': 7232, 'text': '  เงาจากแสงเฉพาะจุด', 'suffix': b'\x00'},
        {'off': 7244, 'text': 'ยืนยันการตั้งค่ากราฟิก', 'suffix': b'\x00'},
    ]
    
    cur_off = 66624
    for opt in all_target_options:
        cyr_str = encode_thai_string(opt['text'])
        suffix = opt.get('suffix', b'\x00')
        raw_b = cyr_str.encode('utf-8') + suffix
        data[cur_off : cur_off + len(raw_b)] = raw_b
        struct.pack_into("<I", data, opt['off'], cur_off - 0x20)
        print(f"    [+] Ptr {opt['off']:4d}: '{opt['text']}' -> off={cur_off} ({len(raw_b)}B)")
        cur_off = (cur_off + len(raw_b) + 1) & ~1
        
    assert cur_off <= 68700, f"Exceeded free space in block 3: {cur_off} > 68700"
    assert len(data) == ORIG_SIZE, f"Size changed: {len(data)} != {ORIG_SIZE}"
    print(f"[+] Entry 204 successfully created ({len(data)} bytes, 100% fits in original slot)")
    return bytes(data)

def main():
    print("==========================================================")
    print("[*] Generating Full Thai Addon Package with Fixed Sara Am")
    print("==========================================================")
    
    data_204 = build_entry_204()
    data_341 = build_entry_341()
    data_342 = build_entry_342()
    
    pad_341 = 1539328 - len(data_341)
    if pad_341 > 0:
        data_341 = data_341 + b'\x00' * pad_341

    pad_342 = 47616 - len(data_342)
    if pad_342 > 0:
        data_342 = data_342 + b'\x00' * pad_342

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
    print("[+] Fixed Sara Am (ต่ำ) as a precomposed ligature with zero gap!")
    print("[+] Injected All Graphics Settings and Hero Selection into dqh2_font_addons.bin!")

if __name__ == "__main__":
    main()
