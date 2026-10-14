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

def render_normalized_glyph(font, ch, target_h=25, x_pad=2, y_top=7):
    """
    วาดและปรับขนาดตัวอักษรให้มีความสูง (Height) เท่ากันทุกตัวเป๊ะๆ
    พร้อมจัดตำแหน่ง X และ Y ให้ชิดและวางบนเส้นบรรทัดเดียวกัน
    """
    scratch = Image.new('RGBA', (70, 70), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(scratch)
    sdraw.text((15, 15), ch, font=font, fill=(255, 255, 255, 255))
    
    arr = np.array(scratch)
    coords = np.argwhere(arr[:, :, 3] > 20)
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    orig_w = max_x - min_x + 1
    orig_h = max_y - min_y + 1
    
    cropped = scratch.crop((min_x, min_y, max_x + 1, max_y + 1))
    
    # ยืด/สเกลความสูงให้เท่ากับ target_h เท่ากันทุกตัวอักษร (เช่น ก เดิมเตี้ยกว่า อ จะถูกยืดให้สูงเท่ากันเป๊ะ)
    new_w = int(round(orig_w * (target_h / orig_h)))
    scaled = cropped.resize((new_w, target_h), Image.Resampling.LANCZOS)
    
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    cell.paste(scaled, (x_pad, y_top), scaled)
    return cell

def render_glyphs_to_font(char_map, out_png_path=None):
    """
    วาดตัวอักษรไทยลงบนตำแหน่ง Cell ที่กำหนด พร้อมปรับสเกลให้สูงเท่ากันทุกตัว
    char_map: dict เช่น {(11, 15): ('อ', 7), (11, 0): ('ก', 7), (11, 13): ('ม', 8)}
    """
    print(f"[*] Loading clean original font sheet: {ORIG_PNG}...")
    img = Image.open(ORIG_PNG).convert("RGBA")
    
    font_size = 44
    font = ImageFont.truetype(FONT_TTF, font_size)
    target_h = 25 # ความสูงมาตรฐานเท่ากันทุกตัวอักษร
    
    for target_slot, val in char_map.items():
        if isinstance(val, tuple):
            thai_char, y_top = val
        else:
            thai_char, y_top = val, 7
            
        if isinstance(target_slot, str):
            code = ord(target_slot)
            row = (code // 16) - 1
            col = code % 16
        else:
            row, col = target_slot
            
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        
        # เรนเดอร์ Glyph ที่ปรับความสูงเท่ากันแล้ว
        glyph_cell = render_normalized_glyph(font, thai_char, target_h=target_h, x_pad=2, y_top=y_top)
        
        # เคลียร์พื้นที่เดิมใน Cell แล้ววางภาพใหม่ลงไป
        blank = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        img.paste(blank, (x0, y0))
        img.paste(glyph_cell, (x0, y0), glyph_cell)
        print(f"[+] Rendered '{thai_char}' into cell Row {row}, Col {col} (Height={target_h}px, Y_top={y_top})")
        
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
    # ใช้ช่อง Cyrillic (Row 11 & Row 14) เป็น PUA เฉพาะ เพื่อไม่กระทบตัวอักษรภาษาอังกฤษ
    # ทุกตัวถูก Normalize ให้สูง 25px เท่ากันเป๊ะ (รวม ก และ เ)
    # Row 11: Col 15 = 'О' (0x041E) -> 'อ' (y_top=7)
    # Row 11: Col 0  = 'А' (0x0410) -> 'ก' (y_top=7, ยืดสูง 25px เท่า อ เป๊ะ)
    # Row 14: Col 3  = 'г' (0x0433) -> 'เ' (y_top=7, ช่องแคบ Advance 17px เพื่อให้สระชิดแน่น)
    # Row 11: Col 13 = 'М' (0x041C) -> 'ม' (y_top=8, ปรับระดับลง 1px ให้อยู่ระนาบเดียวกับตัวอื่นพอดี ไม่ลอย)
    cyrillic_pua_map = {
        (11, 15): ('อ', 7),
        (11, 0):  ('ก', 7),
        (14, 3):  ('เ', 7),
        (11, 13): ('ม', 8)
    }
    render_glyphs_to_font(cyrillic_pua_map, os.path.join(TEX_DIR, "entry_342_test_thai.png"))



