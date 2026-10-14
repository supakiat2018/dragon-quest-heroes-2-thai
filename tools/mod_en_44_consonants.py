"""
mod_en_44_consonants.py
สคริปต์วาดพยัญชนะไทยครบ 44 ตัว (ก-ฮ) + สระ เ, า ลงบนแผ่นภาพ entry_342
และเปลี่ยนข้อความเมนู 6 บรรทัดแรกเป็นพยัญชนะไทยหาร 6 ตามที่ผู้ใช้ระบุ:
- บรรทัด 1: ก ข ฃ ค ฅ ฆ ง
- บรรทัด 2: จ ฉ ช ซ ฌ ญ ฎ
- บรรทัด 3: ฏ ฐ ฑ ฒ ณ ด ต
- บรรทัด 4: ถ ท ธ น บ ป ผ
- บรรทัด 5: ฝ พ ฟ ภ ม ย ร ล
- บรรทัด 6: ว ศ ษ ส ห ฬ อ ฮ
- บรรทัด 7: ออกจากเกม
"""

import os
import sys
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
from inject_entry import inject_entry
from draw_thai_glyphs import encode_dxt5_white, make_dds_file
from exact_cyrillic_table import CYR_MAP

FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
ORIG_PNG = os.path.join(BASE_DIR, "backup", "entry_342_original.png")
SRC_ENTRY_204 = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
OUT_ENTRY_204 = os.path.join(BASE_DIR, "workspace", "entry_204.bin")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")
OUT_G1T = os.path.join(TEX_DIR, "out", "entry_342.g1t")

CELL_SIZE = 36
TARGET_BASELINE = 32
FONT_SIZE = 32

# อ่านความกว้าง orig_w และ x0 ของทุกช่อง Cyrillic จากไฟล์ต้นฉบับ
orig_img = Image.open(ORIG_PNG)
slots_info = {}
for ch, (r, c) in CYR_MAP.items():
    cell = np.array(orig_img.crop((c*36, r*36, (c+1)*36, (r+1)*36)))[:, :, 3]
    coords = np.argwhere(cell > 30)
    if len(coords) > 0:
        x0 = coords[:, 1].min()
        x1 = coords[:, 1].max()
        w = x1 - x0 + 1
    else:
        x0 = 1
        w = 20
    slots_info[ch] = {'char': ch, 'cell': (r, c), 'orig_w': w, 'x0': x0}

# แมปพยัญชนะไทย 44 ตัว + สระ เ, า เข้ากับช่อง Cyrillic
# 14 ตัวเดิมที่ยืนยันความสมบูรณ์แบบแล้ว
MAPPING_44 = {
    'เ': 'г', # \u0433 (Row 14, Col 3, w=16)
    'า': 'е', # \u0435 (Row 14, Col 5, w=18)
    'ก': 'а', # \u0430 (Row 14, Col 0, w=20)
    'จ': 'в', # \u0432 (Row 14, Col 2, w=18)
    'ด': 'к', # \u043A (Row 14, Col 11, w=21)
    'บ': 'д', # \u0434 (Row 14, Col 4, w=22)
    'ล': 'л', # \u043B (Row 14, Col 12, w=22)
    'น': 'и', # \u0438 (Row 14, Col 9, w=20)
    'ท': 'н', # \u043D (Row 14, Col 14, w=21)
    'ม': 'о', # \u043E (Row 14, Col 15, w=20)
    'ง': 'п', # \u043F (Row 15, Col 0, w=21)
    'ส': 'р', # \u0440 (Row 15, Col 1, w=20)
    'อ': 'у', # \u0443 (Row 15, Col 4, w=22)
    'ร': 'ь', # \u044C (Row 15, Col 13, w=19)
    
    # 30 ตัวที่เหลือ แมปลงในช่องว่าง Cyrillic ที่ว่างอยู่
    'ข': 'А', # \u0410 (Row 11, Col 0, w=28)
    'ฃ': 'Б', # \u0411 (Row 11, Col 1, w=23)
    'ค': 'В', # \u0412 (Row 11, Col 2, w=23)
    'ฅ': 'Г', # \u0413 (Row 11, Col 3, w=21)
    'ฆ': 'Д', # \u0414 (Row 11, Col 4, w=29)
    'ฉ': 'Е', # \u0415 (Row 11, Col 5, w=23)
    'ช': 'Ё', # \u0401 (Row 11, Col 6, w=24)
    'ซ': 'Ж', # \u0416 (Row 11, Col 7, w=34)
    'ฌ': 'З', # \u0417 (Row 11, Col 8, w=21)
    'ญ': 'И', # \u0418 (Row 11, Col 9, w=26)
    'ฎ': 'Й', # \u0419 (Row 11, Col 10, w=26)
    'ฏ': 'К', # \u041A (Row 11, Col 11, w=26)
    'ฐ': 'Л', # \u041B (Row 11, Col 12, w=28)
    'ฑ': 'М', # \u041C (Row 11, Col 13, w=32)
    'ฒ': 'Н', # \u041D (Row 11, Col 14, w=26)
    'ณ': 'О', # \u041E (Row 11, Col 15, w=26)
    'ต': 'П', # \u041F (Row 12, Col 0, w=25)
    'ถ': 'Р', # \u0420 (Row 12, Col 1, w=23)
    'ธ': 'С', # \u0421 (Row 12, Col 2, w=24)
    'ป': 'Т', # \u0422 (Row 12, Col 3, w=24)
    'ผ': 'У', # \u0423 (Row 12, Col 4, w=24)
    'ฝ': 'Ф', # \u0424 (Row 12, Col 5, w=27)
    'พ': 'Х', # \u0425 (Row 12, Col 6, w=27)
    'ฟ': 'Ц', # \u0426 (Row 12, Col 7, w=27)
    'ภ': 'Ч', # \u0427 (Row 12, Col 8, w=26)
    'ย': 'Ш', # \u0428 (Row 12, Col 9, w=31)
    'ว': 'Щ', # \u0429 (Row 12, Col 10, w=32)
    'ศ': 'Ъ', # \u042A (Row 12, Col 11, w=28)
    'ษ': 'Ы', # \u042B (Row 12, Col 12, w=31)
    'ห': 'Ь', # \u042C (Row 12, Col 13, w=24)
    'ฬ': 'Э', # \u042D (Row 12, Col 14, w=25)
    'ฮ': 'Ю', # \u042E (Row 12, Col 15, w=32)
}

# 6 บรรทัดพยัญชนะไทยหาร 6 + บรรทัดที่ 7 ออกจากเกม
MENU_LINES = [
    {
        'ptr_offset': 4032,
        'thai_text': 'ก ข ฃ ค ฅ ฆ ง',
        'desc': 'Line 1 (7 chars)'
    },
    {
        'ptr_offset': 4036,
        'thai_text': 'จ ฉ ช ซ ฌ ญ ฎ',
        'desc': 'Line 2 (7 chars)'
    },
    {
        'ptr_offset': 4040,
        'thai_text': 'ฏ ฐ ฑ ฒ ณ ด ต',
        'desc': 'Line 3 (7 chars)'
    },
    {
        'ptr_offset': 6800,
        'thai_text': 'ถ ท ธ น บ ป ผ',
        'desc': 'Line 4 (7 chars)'
    },
    {
        'ptr_offset': 6804,
        'thai_text': 'ฝ พ ฟ ภ ม ย ร ล',
        'desc': 'Line 5 (8 chars)'
    },
    {
        'ptr_offset': 7092,
        'thai_text': 'ว ศ ษ ส ห ฬ อ ฮ',
        'desc': 'Line 6 (8 chars)'
    },
    {
        'ptr_offset': 6808,
        'thai_text': 'ออกจากเกม',
        'desc': 'Line 7 (Exit Game)'
    },
]

def render_token(font, token, slot_char):
    slot = slots_info[slot_char]
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    
    bbox = font.getbbox(token)
    draw_x = 2 - bbox[0]
    draw_y = TARGET_BASELINE - bbox[3]
    draw.text((draw_x, draw_y), token, font=font, fill=(255, 255, 255, 255))
    
    arr = np.array(cell)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return cell
        
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    gw = max_x - min_x + 1
    gh = max_y - min_y + 1
    
    cropped = cell.crop((min_x, min_y, max_x + 1, max_y + 1))
    target_w = slot['orig_w']
    x0 = slot['x0']
    
    # วางกึ่งกลางความกว้างของช่อง โดยไม่ยืดตัวหนังสือเด็ดขาด
    paste_x = x0 + max(0, (target_w - gw) // 2)
    
    new_cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    new_cell.paste(cropped, (paste_x, min_y), cropped)
    return new_cell

def patch_font_texture():
    print(f"[*] Loading clean font sheet: {ORIG_PNG}...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)
    
    print("[*] Drawing all 44 consonants + 2 vowels into font atlas...")
    for thai_char, cyr_char in MAPPING_44.items():
        slot = slots_info[cyr_char]
        row, col = slot['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        glyph_cell = render_token(font, thai_char, cyr_char)
        
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        print(f"    [+] '{thai_char}' -> Cyr '{cyr_char}' (Row {row:2d}, Col {col:2d}, w={slot['orig_w']}px)")
        
    preview_p = os.path.join(TEX_DIR, "entry_342_all_44_thai.png")
    img.save(preview_p)
    print(f"[+] Saved atlas preview to: {preview_p}")
    
    print("[*] Compressing texture to DXT5...")
    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)
        
    print("[*] Repacking G1T via g1t_tool.py...")
    out_dir = os.path.join(TEX_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, out_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Successfully repacked entry_342.g1t ({os.path.getsize(OUT_G1T)} bytes)")
        return True
    else:
        print(f"[-] G1T repack error: {res.stderr}")
        return False

def patch_text_entry_204():
    print("[*] Modifying English text entry_204.bin with 44 Thai consonants...")
    with open(SRC_ENTRY_204, "rb") as f:
        data = bytearray(f.read())
        
    last_used = len(data.rstrip(b"\x00"))
    append_offset = (last_used + 3) & ~3
    
    for item in MENU_LINES:
        raw_text = item['thai_text']
        # แปลงข้อความไทยเป็น Cyrillic UTF-8
        encoded_chars = []
        for ch in raw_text:
            if ch in MAPPING_44:
                encoded_chars.append(MAPPING_44[ch])
            else:
                encoded_chars.append(ch) # space or other chars
        cyr_str = "".join(encoded_chars)
        utf8_bytes = cyr_str.encode('utf-8') + b"\x00"
        
        if append_offset + len(utf8_bytes) > len(data):
            data.extend(b"\x00" * (append_offset + len(utf8_bytes) - len(data)))
            
        data[append_offset:append_offset+len(utf8_bytes)] = utf8_bytes
        
        ptr_val = append_offset - 0x20
        ptr_off = item['ptr_offset']
        old_ptr = struct.unpack("<I", data[ptr_off:ptr_off+4])[0]
        struct.pack_into("<I", data, ptr_off, ptr_val)
        
        print(f"    [+] {item['desc']}:")
        print(f"        Thai: '{raw_text}' -> Cyr: '{cyr_str}'")
        print(f"        Offset: {append_offset} (Ptr: {old_ptr} -> {ptr_val})")
        
        append_offset = (append_offset + len(utf8_bytes) + 3) & ~3
        
    pad = (16 - (len(data) % 16)) % 16
    if pad > 0:
        data.extend(b"\x00" * pad)
        
    with open(OUT_ENTRY_204, "wb") as f:
        f.write(data)
    print(f"[+] Saved modded entry_204 to: {OUT_ENTRY_204} ({len(data)} bytes)")

def inject_all():
    print("[*] Injecting modded files into LINKDATA.BIN...")
    ok1 = inject_entry(342, OUT_G1T)
    ok2 = inject_entry(204, OUT_ENTRY_204)
    if ok1 and ok2:
        print("\n========================================================")
        print("[+] SUCCESS! 44 Consonants Test Mod installed successfully!")
        print("    1. entry_342 (44 Thai Consonants Font) injected")
        print("    2. entry_204 (6 Lines Consonants Text) injected")
        print("========================================================")
    else:
        print("[-] Injection failed!")

def main():
    if not patch_font_texture():
        print("[-] Aborted due to font repack failure.")
        return
    patch_text_entry_204()
    inject_all()

if __name__ == "__main__":
    main()
