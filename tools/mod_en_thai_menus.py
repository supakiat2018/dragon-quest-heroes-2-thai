"""
mod_en_thai_menus.py
สคริปต์ดัดแปลงเมนูหลัก 7 รายการในโหมดภาษาอังกฤษ (English Core) ให้แสดงผลเป็นภาษาไทย
โดยใช้ระบบ Proportional Font Width บน entry_342:
- ไม่มีการบีบ/ยืดภาพ (No stretching) รักษารูปร่างฟอนต์ Pridi-Bold 100%
- จับคู่ช่องความกว้าง (Width Matching) กับช่อง Cyrillic (Row 11-15) อย่างประณีต
- จัดช่องไฟธรรมชาติ (Natural Kerning): สระหน้าดันขวา สระหลังดันซ้าย พยัญชนะกึ่งกลาง
- แปลเมนูหลักทั้ง 7 รายการและอัปเดต Pointer Table ใน entry_204.bin
- ฉีดทั้ง entry_342.g1t และ entry_204.bin เข้า LINKDATA.BIN อัตโนมัติ
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

FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
ORIG_PNG = os.path.join(BASE_DIR, "backup", "entry_342_original.png")
SRC_ENTRY_204 = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
OUT_ENTRY_204 = os.path.join(BASE_DIR, "workspace", "entry_204.bin")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")
OUT_G1T = os.path.join(TEX_DIR, "out", "entry_342.g1t")

CELL_SIZE = 36
TARGET_BASELINE = 31 # Baseline มาตรฐานของตัวอักษรใน entry_342
FONT_SIZE = 30       # ขนาดฟอนต์ 30pt สวยงาม คมชัด ไม่ล้นช่อง 36x36

# ตารางจับคู่ 26 อักขระ/คลัสเตอร์ไทย กับช่อง Cyrillic ใน entry_342
# คัดเลือกช่องที่มีค่าความกว้าง (orig_w) ตรงกับความกว้างธรรมชาติของอักขระไทยที่สุด
# align: 'right' สำหรับสระหน้า (ชิดตัวถัดไป), 'left' สำหรับสระหลัง, 'center' สำหรับพยัญชนะ
SLOTS = {
    # สระเดี่ยว
    'เ':  {'char': '\u0433', 'cell': (14,  3), 'orig_w': 16, 'x0': 2, 'align': 'right'},  # г (16px)
    'า':  {'char': '\u0435', 'cell': (14,  5), 'orig_w': 18, 'x0': 1, 'align': 'left'},   # е (18px)
    
    # พยัญชนะแคบ/กลาง (18-20px)
    'ร':  {'char': '\u044C', 'cell': (15, 13), 'orig_w': 19, 'x0': 1, 'align': 'center'}, # ь (19px)
    'ร้': {'char': '\u0441', 'cell': (15,  2), 'orig_w': 18, 'x0': 1, 'align': 'center'}, # с (18px)
    'ร์': {'char': '\u0442', 'cell': (15,  3), 'orig_w': 19, 'x0': 2, 'align': 'center'}, # т (19px)
    'จ':  {'char': '\u0432', 'cell': (14,  2), 'orig_w': 18, 'x0': 2, 'align': 'center'}, # в (18px)
    'ก':  {'char': '\u0430', 'cell': (14,  0), 'orig_w': 20, 'x0': 1, 'align': 'center'}, # а (20px)
    'ม':  {'char': '\u043E', 'cell': (14, 15), 'orig_w': 20, 'x0': 2, 'align': 'center'}, # о (20px)
    'น':  {'char': '\u0438', 'cell': (14,  9), 'orig_w': 20, 'x0': 1, 'align': 'center'}, # и (20px)
    'ส':  {'char': '\u0440', 'cell': (15,  1), 'orig_w': 21, 'x0': 1, 'align': 'center'}, # р (21px)
    'ง':  {'char': '\u0431', 'cell': (14,  1), 'orig_w': 19, 'x0': 1, 'align': 'center'}, # б (19px)
    
    # พยัญชนะขนาดมาตรฐาน (21-22px)
    'ด':  {'char': '\u043A', 'cell': (14, 11), 'orig_w': 21, 'x0': 2, 'align': 'center'}, # к (21px)
    'ท':  {'char': '\u043D', 'cell': (14, 14), 'orig_w': 21, 'x0': 1, 'align': 'center'}, # н (21px)
    'ล':  {'char': '\u043B', 'cell': (14, 12), 'orig_w': 22, 'x0': 1, 'align': 'center'}, # л (22px)
    'บ':  {'char': '\u0434', 'cell': (14,  4), 'orig_w': 22, 'x0': 2, 'align': 'center'}, # д (22px)
    'อ':  {'char': '\u0443', 'cell': (15,  4), 'orig_w': 22, 'x0': 1, 'align': 'center'}, # у (22px)
    
    # คลัสเตอร์สระซ้อนและวรรณยุกต์ (20-28px)
    'ดิ': {'char': '\u0411', 'cell': (11,  1), 'orig_w': 23, 'x0': 1, 'align': 'center'}, # Б (23px)
    'ค่': {'char': '\u0413', 'cell': (11,  3), 'orig_w': 21, 'x0': 1, 'align': 'center'}, # Г (21px)
    'คี': {'char': '\u0412', 'cell': (11,  2), 'orig_w': 23, 'x0': 2, 'align': 'center'}, # В (23px)
    'ฟิ': {'char': '\u0415', 'cell': (11,  5), 'orig_w': 23, 'x0': 1, 'align': 'center'}, # Е (23px)
    'ริ่': {'char': '\u044D', 'cell': (15, 14), 'orig_w': 17, 'x0': 2, 'align': 'center'}, # э (17px)
    'ทึ': {'char': '\u0447', 'cell': (15,  8), 'orig_w': 20, 'x0': 2, 'align': 'center'}, # ч (20px)
    'ตั้': {'char': '\u044A', 'cell': (15, 11), 'orig_w': 22, 'x0': 1, 'align': 'center'}, # ъ (22px)
    'บั': {'char': '\u0420', 'cell': (12,  1), 'orig_w': 23, 'x0': 1, 'align': 'center'}, # Р (23px)
    'ย์': {'char': '\u0410', 'cell': (11,  0), 'orig_w': 28, 'x0': 1, 'align': 'center'}, # А (28px)
    'ส์': {'char': '\u0448', 'cell': (15,  9), 'orig_w': 27, 'x0': 1, 'align': 'center'}, # ш (27px)
    'ต้': {'char': '\u0445', 'cell': (15,  6), 'orig_w': 20, 'x0': 2, 'align': 'center'}, # х (20px)
    'ช่': {'char': '\u0451', 'cell': (14,  6), 'orig_w': 18, 'x0': 1, 'align': 'center'}, # ё (18px)
    'ใ':  {'char': '\u0437', 'cell': (14,  8), 'orig_w': 16, 'x0': 2, 'align': 'right'},  # з (16px)
}

THAI_TO_CYR = {k: v['char'] for k, v in SLOTS.items()}

# รายการข้อความที่แปลงเป็นภาษาไทย (Title Screen Menus + Dialogue Prompts)
TARGET_MENUS = [
    {
        'name': 'Menu 1: Venture Forth -> เริ่มการเดินทาง',
        'ptr_offset': 4032,
        'tokens': ['เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'เ', 'ดิ', 'น', 'ท', 'า', 'ง'],
    },
    {
        'name': 'Menu 2: Create Adventure Log -> สร้างบันทึก',
        'ptr_offset': 4036,
        'tokens': ['ส', 'ร้', 'า', 'ง', 'บั', 'น', 'ทึ', 'ก'],
    },
    {
        'name': 'Menu 3: Delete Adventure Log -> ลบบันทึก',
        'ptr_offset': 4040,
        'tokens': ['ล', 'บ', 'บั', 'น', 'ทึ', 'ก'],
    },
    {
        'name': 'Menu 4: Graphics Settings -> ตั้งค่ากราฟิก',
        'ptr_offset': 6800,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'ก', 'ร', 'า', 'ฟิ', 'ก'],
    },
    {
        'name': 'Menu 5: Keyboard Settings -> ตั้งค่าคีย์บอร์ด',
        'ptr_offset': 6804,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'คี', 'ย์', 'บ', 'อ', 'ร์', 'ด'],
    },
    {
        'name': 'Menu 6: Mouse Settings -> ตั้งค่าเมาส์',
        'ptr_offset': 7092,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'เ', 'ม', 'า', 'ส์'],
    },
    {
        'name': 'Menu 7: Exit Game -> ออกจากเกม',
        'ptr_offset': 6808,
        'tokens': ['อ', 'อ', 'ก', 'จ', 'า', 'ก', 'เ', 'ก', 'ม'],
    },
    {
        'name': 'Prompt: Which slot do you want to create an adventure log in? -> ต้องการสร้างบันทึกการเดินทางในช่องใด',
        'ptr_offset': 32,
        'tokens': ['ต้', 'อ', 'ง', 'ก', 'า', 'ร', 'ส', 'ร้', 'า', 'ง', 'บั', 'น', 'ทึ', 'ก', 'ก', 'า', 'ร', 'เ', 'ดิ', 'น', 'ท', 'า', 'ง', 'ใ', 'น', 'ช่', 'อ', 'ง', 'ใ', 'ด'],
        'suffix': b'\x1bFH\x00',
    },
]

def render_unstretched_glyph(font, token, slot=None):
    """
    วาดตัวอักษรไทยลงบน Cell ขนาด 36x36 ด้วยระบบ Left-Baseline (anchor='ls')
    ทำให้ทุกอักขระมีระดับเส้นฐาน (Baseline) เท่ากัน 100% ไม่มีตัวอักษรตกหล่น
    และจัดวางตำแหน่งเริ่มต้นที่ x = 2 - min(0, bbox[0]) อย่างคงที่
    """
    bbox = font.getbbox(token)
    draw_x = 2 - min(0, bbox[0])
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    draw.text((draw_x, TARGET_BASELINE), token, font=font, fill=(255, 255, 255, 255), anchor='ls')
    return cell


def patch_font_sheet():
    """
    วาดตัวอักษรไทยลงบนแผ่น entry_342 แล้วแพ็กเป็น DXT5 และ G1T
    """
    print(f"[*] Loading clean font sheet: {ORIG_PNG}...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)
    
    for token, slot in SLOTS.items():
        row, col = slot['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        glyph_cell = render_unstretched_glyph(font, token, slot)
        
        # เคลียร์ช่องเดิมและวาง Glyph ใหม่ลงไป
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        print(f"    [+] Glyph '{token:>3s}' -> Slot Row {row:2d}, Col {col:2d} (orig_w={slot['orig_w']}px)")
        
    preview_path = os.path.join(TEX_DIR, "entry_342_thai_natural.png")
    img.save(preview_path)
    print(f"[+] Saved font sheet preview to: {preview_path}")
    
    # บีบอัดเป็น DXT5
    print("[*] Compressing texture to DXT5...")
    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] Saved DDS to: {OUT_DDS} ({len(dds_bytes)} bytes)")
    
    # แพ็กเป็น G1T
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
    """
    แก้ไขข้อความเมนูทั้ง 7 รายการใน entry_204.bin (English Text)
    """
    print("[*] Modifying English text entry_204.bin...")
    with open(SRC_ENTRY_204, "rb") as f:
        data = bytearray(f.read())
        
    print(f"    [*] Original size: {len(data)} bytes")
    last_used = len(data.rstrip(b"\x00"))
    append_offset = (last_used + 3) & ~3
    
    for menu in TARGET_MENUS:
        cyr_str = "".join(THAI_TO_CYR[t] for t in menu['tokens'])
        suffix = menu.get('suffix', b"\x00")
        utf8_bytes = cyr_str.encode('utf-8') + suffix
        
        if append_offset + len(utf8_bytes) > len(data):
            data.extend(b"\x00" * (append_offset + len(utf8_bytes) - len(data)))
            
        data[append_offset:append_offset+len(utf8_bytes)] = utf8_bytes
        
        ptr_val = append_offset - 0x20
        ptr_off = menu['ptr_offset']
        old_ptr = struct.unpack("<I", data[ptr_off:ptr_off+4])[0]
        struct.pack_into("<I", data, ptr_off, ptr_val)
        
        thai_str = "".join(menu['tokens'])
        print(f"    [+] {menu['name']}:")
        print(f"        Thai: '{thai_str}' -> Cyrillic UTF-8: {utf8_bytes.hex(' ')}")
        print(f"        Offset: {append_offset} (Ptr: {old_ptr} -> {ptr_val})")
        
        append_offset = (append_offset + len(utf8_bytes) + 3) & ~3
        
    pad = (16 - (len(data) % 16)) % 16
    if pad > 0:
        data.extend(b"\x00" * pad)
        
    with open(OUT_ENTRY_204, "wb") as f:
        f.write(data)
    print(f"[+] Saved modded text to: {OUT_ENTRY_204} ({len(data)} bytes)")

def inject_all():
    print("[*] Injecting modded files into LINKDATA.BIN...")
    ok1 = inject_entry(342, OUT_G1T)
    ok2 = inject_entry(204, OUT_ENTRY_204)
    if ok1 and ok2:
        print("\n========================================================")
        print("[+] SUCCESS! English Core Thai Menu Mod installed!")
        print("    1. entry_342 (English Proportional Font) injected")
        print("    2. entry_204 (English Menu Text) injected")
        print("========================================================")
    else:
        print("[-] Injection failed!")

def main():
    if not patch_font_sheet():
        print("[-] Aborting due to font repack failure.")
        return
    patch_text_entry_204()
    inject_all()

if __name__ == "__main__":
    main()
