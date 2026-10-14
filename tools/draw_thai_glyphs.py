"""
draw_thai_glyphs.py
วาดตัวอักษรไทยจากฟอนต์ Pridi (.ttf) ลงบน Font Sheet (Entry 342) โดยตรงด้วย Python
ไม่ต้องพึ่งพา bmfont64 หรือโปรแกรม GUI ภายนอก
"""

import os
import sys
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_342")
ORIG_PNG = os.path.join(TEX_DIR, "entry_342.png")
OUT_DDS = os.path.join(TEX_DIR, "entry_342.TEX0.dxt5.dds")

CELL_SIZE = 36
COLS = 16

def encode_dxt5_white(img_rgba):
    """
    คอมเพรสภาพ RGBA ขาวล้วน (Font Sheet) เป็น BC3 / DXT5 โดยใช้ NumPy ความเร็วสูง
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
    
    # Color block คงที่สำหรับสีขาว RGB (255, 255, 255): 0xFFFF 0xFFFF 0x00000000
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
    สร้างไฟล์ DDS ขนาด 128 ไบต์ตามมาตรฐาน DirectDraw Surface (DXT5)
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

def render_cluster_glyph(font, text, target_baseline=32, target_w=24, x_pad=2):
    """
    วาดตัวอักษรหรือคลัสเตอร์ (พยัญชนะ + สระบน + วรรณยุกต์) โดยวางบน Baseline เดียวกันเป๊ะ (Y=32)
    พร้อมปรับความกว้างแนวนอนให้อ้วนหนาพอดีกับระยะ Advance ของช่องเกม เพื่อให้ตัวอักษรทุกตัวชิดกันสวยงาม ไม่ห่าง
    """
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cell)
    bbox = font.getbbox(text)
    draw_x = 2 - bbox[0]
    draw_y = target_baseline - bbox[3]
    draw.text((draw_x, draw_y), text, font=font, fill=(255, 255, 255, 255))
    
    arr = np.array(cell)
    coords = np.argwhere(arr[:, :, 3] > 20)
    if len(coords) == 0:
        return cell
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    gw = max_x - min_x + 1
    gh = max_y - min_y + 1
    
    # ถ้าตัวอักษรเดี่ยวมีความกว้างแคบกว่า target_w ให้ยืดความกว้างแนวนอนให้เต็มช่อง Advance
    if gw < target_w:
        cropped = cell.crop((min_x, min_y, max_x + 1, max_y + 1))
        new_w = target_w if text not in ['เ', 'า', 'ไ', 'โ'] else max(gw, 22)
        stretched = cropped.resize((new_w, gh), Image.Resampling.LANCZOS)
        new_cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        new_cell.paste(stretched, (x_pad, min_y), stretched)
        return new_cell
    return cell

def render_glyphs_to_font(char_map, out_png_path=None):
    """
    วาดตัวอักษรไทยลงบนตำแหน่ง Cell ที่กำหนดใน Font Sheet
    char_map: dict {(row, col): 'ข้อความหรือคลัสเตอร์'}
    """
    print(f"[*] Loading clean original font sheet: {ORIG_PNG}...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    
    font_size = 38
    font = ImageFont.truetype(FONT_TTF, font_size)
    target_baseline = 32 # ฐานเส้นบรรทัดคงที่ Y=32
    
    for (row, col), text in char_map.items():
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        # วาด Glyph ลงใน Cell 36x36
        glyph_cell = render_cluster_glyph(font, text, target_baseline=target_baseline, x_pad=2)
        
        # เคลียร์พื้นที่เดิมใน Cell แล้ววางภาพใหม่ลงไป
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        print(f"[+] Rendered '{text}' into cell Row {row}, Col {col} (Baseline Y={target_baseline})")
        
    if out_png_path:
        img.save(out_png_path)
        print(f"[+] Saved modded PNG: {out_png_path}")
        
    print("[*] Compressing modded texture to DXT5...")
    dxt_bytes = encode_dxt5_white(img)
    dds_bytes = make_dds_file(dxt_bytes, img.width, img.height)
    
    with open(OUT_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] Exported DXT5 DDS to: {OUT_DDS} ({len(dds_bytes)} bytes)")
    
    # แพ็กกลับเป็น .g1t
    print("[*] Repacking G1T via tools/g1t_tool.py...")
    import subprocess
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, os.path.join(TEX_DIR, "out")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Successfully generated G1T at: {os.path.join(TEX_DIR, 'out', 'entry_342.g1t')}")
    else:
        print(f"[-] G1T repack error: {res.stderr}")
        
    return OUT_DDS

# แมปสำหรับประโยคทดสอบ: "กี่กี้กี๊กิ๋กัดทดสอเบภาษาไทยโดยจริง"
# ใช้เฉพาะ Cyrillic แถว 11 และ 12 (0xC0 ถึง 0xDF) เพื่อให้ Engine ใช้ระนาบ Baseline เดียวกันเป๊ะ 100%
THAI_UNITS_TO_SLOT = {
    (11,  0): 'กี่', # U+0410 (А)
    (11,  1): 'กี้', # U+0411 (Б)
    (11,  2): 'กี๊', # U+0412 (В)
    (11,  3): 'กิ๋', # U+0413 (Г)
    (11,  4): 'กั',  # U+0414 (Д)
    (11,  5): 'ด',   # U+0415 (Е)
    (11,  6): 'ท',   # U+0416 (Ж)
    (11,  7): 'ส',   # U+0417 (З)
    (11,  8): 'อ',   # U+0418 (И)
    (11,  9): 'เ',   # U+0419 (Й)
    (11, 10): 'บ',   # U+041A (К)
    (11, 11): 'ภ',   # U+041B (Л)
    (11, 12): 'า',   # U+041C (М)
    (11, 13): 'ษ',   # U+041D (Н)
    (11, 14): 'ไ',   # U+041E (О)
    (11, 15): 'ย',   # U+041F (П)
    (12,  0): 'โ',   # U+0420 (Р)
    (12,  1): 'จ',   # U+0421 (С)
    (12,  2): 'ริ',  # U+0422 (Т)
    (12,  3): 'ง',   # U+0423 (У)
    (12,  4): 'ก',   # U+0424 (Ф)
    (12,  5): 'ม',   # U+0425 (Х)
}

if __name__ == "__main__":
    render_glyphs_to_font(THAI_UNITS_TO_SLOT, os.path.join(TEX_DIR, "entry_342_test_thai.png"))



