"""
mod_dialogue_font_341.py
สคริปต์แก้ไขฟอนต์กล่องข้อความ / บทสนทนา / บันทึกการเดินทางในเกมจริง (entry_341.g1t)
ซึ่งเป็นฟอนต์หลักขนาด 4096x8192 ที่เกมโหลดไปใช้ในการแสดงผลกล่องสนทนา Save/Load!
นำตัวอักษรและวรรณยุกต์ภาษาไทย 29 ตัวชุดเดียวกับที่ใช้บนหน้าไตเติล (SLOTS)
เขียนทับลงในช่อง Cyrillic (Row 8, Col 19-84) ของ entry_341.g1t
แล้วบีบอัดและฉีด In-place ทับ Offset 45,149,440 ใน LINKDATA.BIN
"""

import os
import sys
import struct
import numpy as np
from PIL import Image, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

from mod_en_thai_menus import SLOTS, render_unstretched_glyph, FONT_TTF
from test_cell_encoder import encode_cell_dxt5
from inject_inplace import pack_entry_chunks, inject_entry_inplace

ORIG_G1T = os.path.join(BASE_DIR, "backup", "entry_341_original.g1t")
OUT_G1T = os.path.join(BASE_DIR, "workspace", "entry_341.g1t")

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

def patch_and_inject_341():
    print(f"[*] Reading original dialogue font G1T: {ORIG_G1T}...")
    with open(ORIG_G1T, "rb") as f:
        g1t_data = bytearray(f.read())
    
    assert len(g1t_data) == 33554488, f"Unexpected G1T size: {len(g1t_data)}"
    
    font = ImageFont.truetype(FONT_TTF, 32)
    WIDTH = 4096
    BLOCKS_PER_ROW = WIDTH // 4 # 1024
    BLOCK_BYTES = 16
    SCANBAND_BYTES = BLOCKS_PER_ROW * BLOCK_BYTES # 16384 bytes
    G1T_HEADER_SIZE = 56
    
    print(f"[*] Patching 29 Thai glyphs into entry_341 (Row 8 cells)...")
    for token, slot in SLOTS.items():
        ch = slot['char']
        r, c = get_341_cell(ch)
        
        # วาด Glyph ตัวอักษรไทย
        glyph_cell = render_unstretched_glyph(font, token, slot)
        
        # เข้ารหัส 36x36 RGBA ให้เป็น 9 แถวของบล็อก DXT5
        dxt_rows = encode_cell_dxt5(glyph_cell)
        
        # เขียนทับลงในบล็อกข้อมูล DXT5 ของ entry_341
        bx = c * 9
        by = r * 9
        for dy in range(9):
            block_row = by + dy
            offset = G1T_HEADER_SIZE + block_row * SCANBAND_BYTES + bx * BLOCK_BYTES
            g1t_data[offset : offset + 144] = dxt_rows[dy]
            
        print(f"    [+] '{token:>3s}' ({ch}) -> Row {r:2d}, Col {c:2d} (x={c*36}..{(c+1)*36})")
        
    os.makedirs(os.path.dirname(OUT_G1T), exist_ok=True)
    with open(OUT_G1T, "wb") as f:
        f.write(g1t_data)
    print(f"[+] Saved patched G1T to {OUT_G1T}")
    
    print(f"[*] Injecting entry_341.g1t into LINKDATA.BIN in-place...")
    success = inject_entry_inplace(341, OUT_G1T)
    if success:
        print("[SUCCESS] entry_341.g1t injected successfully!")
    else:
        print("[-] Injection failed!")
    return success

if __name__ == "__main__":
    patch_and_inject_341()
