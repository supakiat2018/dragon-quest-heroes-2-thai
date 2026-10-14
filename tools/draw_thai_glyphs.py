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

def render_slot_glyph(font, text, info, target_baseline=32):
    """
    วาด Glyph ลงใน Cell 36x36 โดย:
    1. วางบน Baseline เดียวกันเป๊ะ (Y=32)
    2. ปรับความกว้าง (Width) และตำแหน่ง X (min_x) ให้ตรงกับ Slot เดิมของ Engine เป๊ะ 100%
       ทำให้ไม่มีช่องว่าง (Gaps) ค้างอยู่ระหว่างตัวอักษร และตัวอักษรทุกตัวชิดกันสวยงาม
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
    
    target_w = info['orig_w']
    cropped = cell.crop((min_x, min_y, max_x + 1, max_y + 1))
    if gw != target_w:
        stretched = cropped.resize((target_w, gh), Image.Resampling.LANCZOS)
    else:
        stretched = cropped
        
    new_cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    new_cell.paste(stretched, (info['min_x'], min_y), stretched)
    return new_cell

# ตาราง Slot ประจำแต่ละหน่วยอักขระ/คลัสเตอร์
# คัดเลือก Slot ที่ความกว้าง (Advance Width) สัมพันธ์กับขนาดธรรมชาติของอักษรไทย
# เพื่อกำจัดปัญหาช่องว่าง (Gaps) อย่างสมบูรณ์ 100%
THAI_SLOTS = {
    # คลัสเตอร์ที่มีสระบน/วรรณยุกต์ (ใช้ Slot ตัวพิมพ์ใหญ่กว้าง 21-29px)
    'กี่': {'char': '\u0410', 'cell': (11,  0), 'orig_w': 28, 'min_x': 1}, # А (28px)
    'กี้': {'char': '\u0411', 'cell': (11,  1), 'orig_w': 23, 'min_x': 1}, # Б (23px)
    'กี๊': {'char': '\u0412', 'cell': (11,  2), 'orig_w': 23, 'min_x': 2}, # В (23px)
    'กิ๋': {'char': '\u0413', 'cell': (11,  3), 'orig_w': 21, 'min_x': 1}, # Г (21px)
    'กั':  {'char': '\u0414', 'cell': (11,  4), 'orig_w': 29, 'min_x': 1}, # Д (29px)
    'ด':   {'char': '\u0415', 'cell': (11,  5), 'orig_w': 23, 'min_x': 1}, # Е (23px)
    'ท':   {'char': '\u0401', 'cell': (11,  6), 'orig_w': 24, 'min_x': 1}, # Ё (24px, U+0401)
    
    # พยัญชนะและสระเดี่ยว (แมปลงใน Slot ตัวพิมพ์เล็กที่มีความกว้างพอดี 16-24px)
    'ส':   {'char': '\u043F', 'cell': (15,  0), 'orig_w': 21, 'min_x': 1}, # п (21px)
    'อ':   {'char': '\u0440', 'cell': (15,  1), 'orig_w': 21, 'min_x': 1}, # р (21px)
    'เ':   {'char': '\u0433', 'cell': (14,  3), 'orig_w': 16, 'min_x': 1}, # г (16px - แคบพิเศษ ชิดตัวถัดไปเป๊ะ)
    'บ':   {'char': '\u0434', 'cell': (14,  4), 'orig_w': 22, 'min_x': 1}, # д (22px)
    'ภ':   {'char': '\u043B', 'cell': (14, 12), 'orig_w': 22, 'min_x': 1}, # л (22px)
    'า':   {'char': '\u0435', 'cell': (14,  5), 'orig_w': 18, 'min_x': 1}, # е (18px - พอดีสระอา)
    'ษ':   {'char': '\u0443', 'cell': (15,  4), 'orig_w': 22, 'min_x': 1}, # у (22px)
    'ไ':   {'char': '\u0441', 'cell': (15,  2), 'orig_w': 18, 'min_x': 1}, # с (18px - พอดีสระไอ)
    'ย':   {'char': '\u043A', 'cell': (14, 11), 'orig_w': 21, 'min_x': 1}, # к (21px)
    'โ':   {'char': '\u0451', 'cell': (14,  6), 'orig_w': 18, 'min_x': 1}, # ё (18px - พอดีสระโอ, U+0451)
    'จ':   {'char': '\u0446', 'cell': (15,  7), 'orig_w': 21, 'min_x': 1}, # ц (21px)
    'ริ':  {'char': '\u043C', 'cell': (14, 13), 'orig_w': 24, 'min_x': 1}, # м (24px)
    'ง':   {'char': '\u044F', 'cell': (16,  0), 'orig_w': 21, 'min_x': 1}, # я (21px)
    'ก':   {'char': '\u0416', 'cell': (11,  7), 'orig_w': 24, 'min_x': 1}, # Ж (24px)
    'ม':   {'char': '\u0417', 'cell': (11,  8), 'orig_w': 24, 'min_x': 1}, # З (24px)
}

def render_glyphs_to_font(slot_dict, out_png_path=None):
    """
    วาดตัวอักษรไทยลงบนตำแหน่ง Cell ที่กำหนดใน Font Sheet
    """
    print(f"[*] Loading clean original font sheet: {ORIG_PNG}...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    
    font_size = 38
    font = ImageFont.truetype(FONT_TTF, font_size)
    target_baseline = 32 # ฐานเส้นบรรทัดคงที่ Y=32
    
    for text, info in slot_dict.items():
        row, col = info['cell']
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        # วาด Glyph ลงใน Cell 36x36
        glyph_cell = render_slot_glyph(font, text, info, target_baseline=target_baseline)
        
        # เคลียร์พื้นที่เดิมใน Cell แล้ววางภาพใหม่ลงไป
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        print(f"[+] Rendered '{text}' into cell Row {row:2d}, Col {col:2d} [Char: {info['char']}, orig_w={info['orig_w']}px]")
        
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

if __name__ == "__main__":
    render_glyphs_to_font(THAI_SLOTS, os.path.join(TEX_DIR, "entry_342_test_thai.png"))




