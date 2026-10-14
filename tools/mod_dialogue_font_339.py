"""
mod_dialogue_font_339.py
สคริปต์แก้ไขฟอนต์กล่องข้อความ / บทสนทนา / บันทึกการเดินทาง (entry_339.g1t)
นำตัวอักษรและวรรณยุกต์ภาษาไทย 29 ตัวชุดเดียวกับที่ใช้บนหน้าไตเติล
ไปใส่ทับในช่อง Cyrillic ของ entry_339 แล้วฉีดเข้าสู่ LINKDATA.BIN ทันที
"""

import os
import sys
import struct
import numpy as np
from PIL import Image, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from inject_entry import inject_entry
from mod_en_thai_menus import SLOTS, render_unstretched_glyph, FONT_TTF
from test_cell_encoder import encode_cell_dxt5

ORIG_G1T = os.path.join(BASE_DIR, "backup", "entry_339_original.g1t")
OUT_G1T = os.path.join(BASE_DIR, "workspace", "entry_339.g1t")

CYR_UPPER_339 = [chr(0x0410 + i) for i in range(32)]
CYR_UPPER_339.insert(6, chr(0x0401)) # Ё

CYR_LOWER_339 = [chr(0x0430 + i) for i in range(32)]
CYR_LOWER_339.insert(6, chr(0x0451)) # ё

def get_339_cell(char):
    if char in CYR_UPPER_339:
        idx = CYR_UPPER_339.index(char)
        if idx <= 25:
            return (3, 87 + idx)
        else:
            return (4, idx - 26)
    elif char in CYR_LOWER_339:
        idx = CYR_LOWER_339.index(char)
        return (4, 7 + idx)
    else:
        raise ValueError(f"Char {char} not found in Cyrillic alphabet")

def patch_dialogue_font_339():
    print(f"[*] Reading original dialogue font G1T: {ORIG_G1T}...")
    with open(ORIG_G1T, "rb") as f:
        g1t_data = bytearray(f.read())
    
    assert len(g1t_data) == 8388664, f"Unexpected G1T size: {len(g1t_data)}"
    
    font = ImageFont.truetype(FONT_TTF, 32)
    WIDTH = 4096
    BLOCKS_PER_ROW = WIDTH // 4 # 1024
    BLOCK_BYTES = 16
    SCANBAND_BYTES = BLOCKS_PER_ROW * BLOCK_BYTES # 16384 bytes
    G1T_HEADER_SIZE = 56
    
    print(f"[*] Patching 29 Thai glyphs into entry_339 cells...")
    for token, slot in SLOTS.items():
        ch = slot['char']
        r, c = get_339_cell(ch)
        
        # วาด Glyph ตัวอักษรไทย
        glyph_cell = render_unstretched_glyph(font, token, slot)
        
        # เข้ารหัส 36x36 RGBA ให้เป็น 9 แถวของบล็อก DXT5
        dxt_rows = encode_cell_dxt5(glyph_cell)
        
        # เขียนทับลงในบล็อกข้อมูล DXT5 ของ entry_339
        bx = c * 9
        by = r * 9
        for dy in range(9):
            block_row = by + dy
            offset = G1T_HEADER_SIZE + block_row * SCANBAND_BYTES + bx * BLOCK_BYTES
            g1t_data[offset : offset + 144] = dxt_rows[dy]
            
        print(f"    [+] '{token:>3s}' ({ch}) -> Row {r:2d}, Col {c:2d}")
        
    # บันทึกไฟล์ G1T ที่แก้ไขแล้ว
    with open(OUT_G1T, "wb") as f:
        f.write(g1t_data)
    print(f"[+] Successfully wrote modded G1T to: {OUT_G1T} ({len(g1t_data)} bytes)")
    
    # ฉีดเข้าสู่ LINKDATA.BIN
    print(f"[*] Injecting Entry 339 into LINKDATA.BIN...")
    success = inject_entry(339, OUT_G1T)
    if success:
        print("[+] Dialogue font Entry 339 successfully injected into game!")
    else:
        print("[-] Injection failed!")
    return success

if __name__ == "__main__":
    patch_dialogue_font_339()
