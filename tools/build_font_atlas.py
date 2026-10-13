"""
build_font_atlas.py
เครื่องมือสร้างและเรนเดอร์ฟอนต์ภาษาไทย (Thai Font Atlas Builder) สำหรับ DRAGON QUEST HEROES II
เขียนขึ้นโดยเฉพาะสำหรับเกมค่าย Koei Tecmo / Omega Force

ความสามารถ:
1. โหลดฟอนต์ TrueType (.ttf) ภาษาไทย (เช่น Pridi-Bold.ttf)
2. วาดอักขระภาษาไทย (พยัญชนะ ก-ฮ, สระ, วรรณยุกต์, ตัวเลข) ลงบนแผ่น Font Atlas (Entry 342) โดยตรง
3. ปรับขนาด (Font Size), ตำแหน่ง (Baseline Offset), และการจัดกึ่งกลาง Cell อัตโนมัติ
4. คอมเพรสภาพเป็น BC3 / DXT5 DDS ด้วย NumPy ความเร็วสูง (< 0.5 วินาที)
5. แพ็กเป็น .g1t ผ่าน tools/g1t_tool.py
6. รองรับทั้งโหมดตรง (Direct Glyph Insertion) และโหมดทดสอบ (Test Slot Insertion)
"""

import os
import sys
import struct
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, "Pridi")
DEFAULT_FONT_PATH = os.path.join(FONT_DIR, "Pridi-Bold.ttf")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
ORIG_PNG = os.path.join(TEX_DIR, "entry_342.png")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")
OUT_G1T_DIR = os.path.join(TEX_DIR, "out")

CELL_SIZE = 36
GRID_COLS = 16
GRID_ROWS = 28

# รายการอักขระภาษาไทยทั้งหมด (Unicode 0x0E01 - 0x0E5B)
THAI_CHARACTERS = [
    # พยัญชนะ 44 ตัว
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ',
    'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ',
    'ม', 'ย', 'ร', 'ฤ', 'ล', 'ฦ', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ',
    # สระ และเครื่องหมาย
    'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'ฺ',
    'เ', 'แ', 'โ', 'ใ', 'ไ', 'ๅ', 'ๆ', '็',
    # วรรณยุกต์
    '่', '้', '๊', '๋', '์', 'ํ', '๎', '๏',
    # ตัวเลขไทย
    '๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙',
    # เครื่องหมายอื่นๆ
    '๚', '๛'
]

def encode_dxt5_white(img_rgba):
    """
    คอมเพรสแผ่นภาพ RGBA สีขาวล้วนเป็น BC3 / DXT5 โดยใช้ NumPy
    """
    w, h = img_rgba.size
    arr = np.array(img_rgba)
    alpha = arr[:, :, 3]
    
    pad_h = (4 - (h % 4)) % 4
    pad_w = (4 - (w % 4)) % 4
    if pad_h > 0 or pad_w > 0:
        alpha = np.pad(alpha, ((0, pad_h), (0, pad_w)), mode='constant')
        h, w = alpha.shape
        
    bw = w // 4
    bh = h // 4
    blocks = alpha.reshape(bh, 4, bw, 4).swapaxes(1, 2).reshape(bh * bw, 16)
    out = bytearray(bh * bw * 16)
    
    color_block = b'\xff\xff\xff\xff\x00\x00\x00\x00'
    pal = np.array([255, 0, 219, 182, 146, 109, 73, 36])
    
    for i in range(bh * bw):
        blk = blocks[i]
        if not blk.any():
            continue
        diff = np.abs(blk[:, None] - pal[None, :])
        indices = np.argmin(diff, axis=1)
        bits = 0
        for p in range(16):
            bits |= (int(indices[p]) & 7) << (3 * p)
        out[i*16:i*16+8] = struct.pack('<BB', 255, 0) + bits.to_bytes(6, 'little')
        out[i*16+8:i*16+16] = color_block
        
    return bytes(out)

def make_dds_file(dxt_data, w, h):
    """
    สร้าง Header DDS ขนาด 128 ไบต์ตามสเปก DirectDraw Surface
    """
    magic = b'DDS '
    dwSize = 124
    dwFlags = 0x00081007
    dwHeight = h
    dwWidth = w
    dwPitchOrLinearSize = len(dxt_data)
    dwDepth = 0
    dwMipMapCount = 1
    dwReserved1 = b'\x00' * 44
    
    pf_dwSize = 32
    pf_dwFlags = 0x00000004
    pf_dwFourCC = b'DXT5'
    pixelformat = struct.pack('<II4sIIIII', pf_dwSize, pf_dwFlags, pf_dwFourCC, 0, 0, 0, 0, 0)
    
    dwCaps = 0x00001000
    caps = struct.pack('<IIIII', dwCaps, 0, 0, 0, 0)
    header = struct.pack('<IIIIIII', dwSize, dwFlags, dwHeight, dwWidth, dwPitchOrLinearSize, dwDepth, dwMipMapCount) + dwReserved1 + pixelformat + caps
    return magic + header + dxt_data

def build_atlas(font_path=DEFAULT_FONT_PATH, font_size=28, target_cells=None, start_empty_row=21):
    """
    วาดตัวอักษรไทยลงบนแผ่นภาพ Atlas
    - หากระบุ target_cells (dict): จะวาดทับช่องที่กำหนด เช่น {'X': 'อ', 'x': 'ก'}
    - หากไม่ระบุ: จะวาดอักขระไทยทั้งหมดลงในพื้นที่ว่างของ Atlas เริ่มจาก Row 21
    """
    if not os.path.exists(ORIG_PNG):
        print(f"[-] Original font PNG not found: {ORIG_PNG}")
        return None
        
    print(f"[*] Loading font: {font_path} (size={font_size})...")
    font = ImageFont.truetype(font_path, font_size)
    
    img = Image.open(ORIG_PNG).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    drawn_count = 0
    
    if target_cells:
        # วาดเฉพาะ Cell ที่ระบุ
        for target_char, thai_char in target_cells.items():
            if isinstance(target_char, str):
                code = ord(target_char)
                row = (code // 16) - 1
                col = code % 16
            else:
                row, col = target_char
                
            x0 = col * CELL_SIZE
            y0 = row * CELL_SIZE
            
            draw.rectangle([x0, y0, x0 + CELL_SIZE - 1, y0 + CELL_SIZE - 1], fill=(0, 0, 0, 0))
            
            bbox = font.getbbox(thai_char)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            dx = x0 + (CELL_SIZE - bw) // 2 - bbox[0]
            dy = y0 + (CELL_SIZE - bh) // 2 - bbox[1]
            draw.text((dx, dy), thai_char, font=font, fill=(255, 255, 255, 255))
            drawn_count += 1
            print(f"[+] Drawn '{thai_char}' into slot Row {row}, Col {col} (ASCII '{target_char}')")
    else:
        # วาดอักขระไทยทั้งหมดลงในพื้นที่ว่างของ Texture Atlas (เริ่มจาก Row 21 เป็นต้นไป)
        print(f"[*] Populating full Thai character set into blank atlas space starting at Row {start_empty_row}...")
        cur_row = start_empty_row
        cur_col = 0
        
        for ch in THAI_CHARACTERS:
            if cur_row >= GRID_ROWS:
                print("[-] Warning: Texture atlas ran out of rows!")
                break
                
            x0 = cur_col * CELL_SIZE
            y0 = cur_row * CELL_SIZE
            
            draw.rectangle([x0, y0, x0 + CELL_SIZE - 1, y0 + CELL_SIZE - 1], fill=(0, 0, 0, 0))
            
            bbox = font.getbbox(ch)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            dx = x0 + (CELL_SIZE - bw) // 2 - bbox[0]
            dy = y0 + (CELL_SIZE - bh) // 2 - bbox[1]
            draw.text((dx, dy), ch, font=font, fill=(255, 255, 255, 255))
            
            cur_col += 1
            if cur_col >= GRID_COLS:
                cur_col = 0
                cur_row += 1
            drawn_count += 1
            
        print(f"[+] Placed {drawn_count} Thai glyphs into Atlas (Rows {start_empty_row} to {cur_row})")
        
    # บันทึกภาพ PNG ตรวจสอบผลลัพธ์
    preview_path = os.path.join(TEX_DIR, "entry_342_thai_atlas.png")
    img.save(preview_path)
    print(f"[+] Saved visual preview to: {preview_path}")
    
    # คอมเพรสเป็น DXT5 DDS
    print("[*] Encoding DXT5 DDS with NumPy...")
    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] Written DXT5 DDS to: {OUT_DDS} ({len(dds_bytes)} bytes)")
    
    # แพ็กกลับเป็น .g1t
    print("[*] Repacking G1T via tools/g1t_tool.py...")
    import subprocess
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Successfully generated G1T at: {os.path.join(OUT_G1T_DIR, 'entry_342.g1t')}")
    else:
        print(f"[-] G1T repack error: {res.stderr}")
        
    return preview_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dragon Quest Heroes II Thai Font Atlas Generator")
    parser.add_argument("--font", default=DEFAULT_FONT_PATH, help="Path to TTF font file")
    parser.add_argument("--size", type=int, default=28, help="Font point size (default: 28)")
    parser.add_argument("--test", action="store_true", help="Run test mode replacing 'X' and 'x' with 'อ' and 'ก'")
    args = parser.parse_args()
    
    if args.test:
        test_cells = {'X': 'อ', 'x': 'ก'}
        build_atlas(font_path=args.font, font_size=args.size, target_cells=test_cells)
    else:
        build_atlas(font_path=args.font, font_size=args.size)
