"""
mod_cjk_thai_menu.py
สคริปต์อัตโนมัติสำหรับดัดแปลงเมนูหลัก 7 รายการในโหมดภาษาจีน (Traditional Chinese)
ให้แสดงผลเป็นภาษาไทยด้วยระบบ CJK PUA Glyph Replacement:
1. วาดตัวอักษรไทย/คลัสเตอร์ (Pridi-Bold) ลงในช่องตัวอักษรจีน (0xA440..0xA459, Row 3 Col 69..94) บน entry_340
2. แพ็กกลับเป็น entry_340.g1t
3. แก้ไขข้อความใน entry_210.bin ให้ชี้ไปยังตัวอักษรจีนที่แทนที่ด้วยภาษาไทย
4. ทำการฉีด (Inject) ทั้งสองไฟล์เข้าสู่ LINKDATA.BIN และอัปเดต LINKDATA.IDX
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

FONT_TTF = os.path.join(BASE_DIR, "Pridi", "Pridi-Bold.ttf")
SRC_ENTRY_210 = os.path.join(BASE_DIR, "backup", "entry_210_original.bin")
OUT_ENTRY_210 = os.path.join(BASE_DIR, "workspace", "entry_210.bin")
DDS_PATH = os.path.join(BASE_DIR, "workspace", "tex_340", "entry_340.TEX0.dxt5.dds")
TEX_DIR = os.path.join(BASE_DIR, "workspace", "tex_340")
OUT_G1T = os.path.join(TEX_DIR, "out", "entry_340.g1t")

CELL_SIZE = 36
WIDTH = 4096
HEIGHT = 8192
BLOCKS_PER_ROW = WIDTH // 4 # 1024
BLOCK_BYTES = 16
SCANBAND_BYTES = BLOCKS_PER_ROW * BLOCK_BYTES # 16384
DDS_HEADER_SIZE = 128

# 26 ตัวอักษรและคลัสเตอร์ภาษาไทยสำหรับ 7 เมนูหลัก
# แมปจับคู่กับอักษรจีน 26 ตัวแรกของชุด Big5 มาตรฐาน (0xA440 - 0xA459)
# ซึ่งอยู่ใน Row 3 คอลัมน์ 69 ถึง 94 ใน Font Atlas (entry_340)
TOKEN_LIST = [
    # (Thai Token, Big5 Chinese Character, Lead Byte, Trail Byte)
    ('เ',   '一', 0xA4, 0x40), # Row 3, Col 69
    ('ริ่',  '乙', 0xA4, 0x41), # Row 3, Col 70
    ('ม',   '丁', 0xA4, 0x42), # Row 3, Col 71
    ('ก',   '七', 0xA4, 0x43), # Row 3, Col 72
    ('า',   '乃', 0xA4, 0x44), # Row 3, Col 73
    ('ร',   '九', 0xA4, 0x45), # Row 3, Col 74
    ('ดิ',  '了', 0xA4, 0x46), # Row 3, Col 75
    ('น',   '二', 0xA4, 0x47), # Row 3, Col 76
    ('ท',   '人', 0xA4, 0x48), # Row 3, Col 77
    ('ง',   '兒', 0xA4, 0x49), # Row 3, Col 78
    ('ส',   '入', 0xA4, 0x4A), # Row 3, Col 79
    ('ร้',  '八', 0xA4, 0x4B), # Row 3, Col 80
    ('บั',  '几', 0xA4, 0x4C), # Row 3, Col 81
    ('ทึ',  '刀', 0xA4, 0x4D), # Row 3, Col 82
    ('ล',   '刁', 0xA4, 0x4E), # Row 3, Col 83
    ('บ',   '力', 0xA4, 0x4F), # Row 3, Col 84
    ('ตั้', '匕', 0xA4, 0x50), # Row 3, Col 85
    ('ค่',  '十', 0xA4, 0x51), # Row 3, Col 86
    ('ฟิ',  '卜', 0xA4, 0x52), # Row 3, Col 87
    ('คี',  '又', 0xA4, 0x53), # Row 3, Col 88
    ('ย์',  '三', 0xA4, 0x54), # Row 3, Col 89
    ('อ',   '下', 0xA4, 0x55), # Row 3, Col 90
    ('ร์',  '丈', 0xA4, 0x56), # Row 3, Col 91
    ('ด',   '上', 0xA4, 0x57), # Row 3, Col 92
    ('ส์',  '丫', 0xA4, 0x58), # Row 3, Col 93
    ('จ',   '丸', 0xA4, 0x59), # Row 3, Col 94
]

THAI_TO_CJK = {item[0]: item[1] for item in TOKEN_LIST}

# 7 เมนูหลัก พร้อมการแยกโทเคนภาษาไทย
TARGET_MENUS = [
    {
        'name': 'Menu 1: Venture Forth (開始冒險 -> เริ่มการเดินทาง)',
        'ptr_offset': 4032,
        'tokens': ['เ', 'ริ่', 'ม', 'ก', 'า', 'ร', 'เ', 'ดิ', 'น', 'ท', 'า', 'ง'],
    },
    {
        'name': 'Menu 2: Create Adventure Log (建立冒險之書 -> สร้างบันทึก)',
        'ptr_offset': 4036,
        'tokens': ['ส', 'ร้', 'า', 'ง', 'บั', 'น', 'ทึ', 'ก'],
    },
    {
        'name': 'Menu 3: Delete Adventure Log (刪除冒險之書 -> ลบบันทึก)',
        'ptr_offset': 4040,
        'tokens': ['ล', 'บ', 'บั', 'น', 'ทึ', 'ก'],
    },
    {
        'name': 'Menu 4: Graphics Settings (圖像設定 -> ตั้งค่ากราฟิก)',
        'ptr_offset': 6800,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'ก', 'ร', 'า', 'ฟิ', 'ก'],
    },
    {
        'name': 'Menu 5: Keyboard Settings (鍵盤設定 -> ตั้งค่าคีย์บอร์ด)',
        'ptr_offset': 6804,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'คี', 'ย์', 'บ', 'อ', 'ร์', 'ด'],
    },
    {
        'name': 'Menu 6: Mouse Settings (滑鼠設定 -> ตั้งค่าเมาส์)',
        'ptr_offset': 7092,
        'tokens': ['ตั้', 'ง', 'ค่', 'า', 'เ', 'ม', 'า', 'ส์'],
    },
    {
        'name': 'Menu 7: Exit Game (結束遊戲 -> ออกจากเกม)',
        'ptr_offset': 6808,
        'tokens': ['อ', 'อ', 'ก', 'จ', 'า', 'ก', 'เ', 'ก', 'ม'],
    },
]

def encode_cell_dxt5(cell_img):
    """
    เข้ารหัสภาพ RGBA ขนาด 36x36 เป็น DXT5 (9 แถว แถวละ 9 บล็อก บล็อกละ 16 ไบต์ รวม 1,296 ไบต์)
    """
    arr = np.array(cell_img)
    alpha = arr[:, :, 3]
    color_block = b'\xff\xff\xff\xff\x00\x00\x00\x00'
    pal = np.array([255, 0, 219, 182, 146, 109, 73, 36])
    
    rows_dxt = []
    for by in range(9):
        row_bytes = bytearray(9 * 16)
        for bx in range(9):
            blk = alpha[by*4:(by+1)*4, bx*4:(bx+1)*4].flatten()
            if not blk.any():
                alpha_block = b'\x00\x00\x00\x00\x00\x00\x00\x00'
                row_bytes[bx*16:(bx+1)*16] = alpha_block + color_block
            else:
                diff = np.abs(blk[:, None] - pal[None, :])
                indices = np.argmin(diff, axis=1)
                bits = 0
                for p in range(16):
                    bits |= (int(indices[p]) & 7) << (3 * p)
                alpha_block = struct.pack('<BB', 255, 0) + bits.to_bytes(6, 'little')
                row_bytes[bx*16:(bx+1)*16] = alpha_block + color_block
        rows_dxt.append(bytes(row_bytes))
    return rows_dxt

def patch_font_dds():
    """
    วาดตัวอักษรไทย 26 ตัวลงในช่อง Big5 0xA440..0xA459 (Row 3, Col 69..94) ของ entry_340
    """
    print("[*] Patching Font Atlas entry_340.TEX0.dxt5.dds...")
    font = ImageFont.truetype(FONT_TTF, 30)
    
    with open(DDS_PATH, "r+b") as f:
        for idx, (thai_token, cjk_char, b1, b2) in enumerate(TOKEN_LIST):
            r = 3
            c = 69 + idx
            
            # วาดตัวอักษรไทยลงบน 36x36
            cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cell)
            draw.text((CELL_SIZE // 2, 27), thai_token, font=font, fill=(255, 255, 255, 255), anchor="ms")
            
            # แปลงเป็น DXT5 9 แถว
            cell_dxt_rows = encode_cell_dxt5(cell)
            
            bx = c * 9
            by = r * 9
            for dy in range(9):
                block_row = by + dy
                band_offset = DDS_HEADER_SIZE + block_row * SCANBAND_BYTES
                offset = band_offset + bx * BLOCK_BYTES
                f.seek(offset)
                f.write(cell_dxt_rows[dy])
                
            print(f"    [+] Glyph '{thai_token:>3s}' -> CJK '{cjk_char}' (Row {r}, Col {c})")
            
    print("[+] Successfully patched all 26 Thai glyphs into font sheet!")

def repack_g1t():
    """
    เรียก g1t_tool.py เพื่อแพ็กไฟล์ DDS กลับเป็น entry_340.g1t
    """
    print("[*] Repacking entry_340.g1t via g1t_tool.py...")
    out_dir = os.path.join(TEX_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "g1t_tool.py"), "import", TEX_DIR, out_dir]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Successfully repacked entry_340.g1t ({os.path.getsize(OUT_G1T)} bytes)")
        return True
    else:
        print(f"[-] Repack error:\n{res.stderr}")
        return False

def patch_text_entry_210():
    """
    แก้ไขข้อความเมนูทั้ง 7 รายการใน entry_210.bin
    """
    print("[*] Modifying Chinese text entry_210.bin...")
    with open(SRC_ENTRY_210, "rb") as f:
        data = bytearray(f.read())
        
    print(f"    [*] Original size: {len(data)} bytes")
    
    # กำหนดตำแหน่งเขียนต่อท้าย
    last_used = len(data.rstrip(b"\x00"))
    append_offset = (last_used + 3) & ~3 # 4-byte aligned
    
    for menu in TARGET_MENUS:
        # แปลงโทเคนไทยเป็นข้อความตัวอักษรจีน UTF-8
        cjk_str = "".join(THAI_TO_CJK[t] for t in menu['tokens'])
        utf8_bytes = cjk_str.encode('utf-8') + b"\x00"
        
        # ขยายไฟล์หากพื้นที่ไม่พอ
        if append_offset + len(utf8_bytes) > len(data):
            data.extend(b"\x00" * (append_offset + len(utf8_bytes) - len(data)))
            
        data[append_offset:append_offset+len(utf8_bytes)] = utf8_bytes
        
        # คำนวณค่า Pointer: Pointer = File Offset - 0x20
        ptr_val = append_offset - 0x20
        ptr_off = menu['ptr_offset']
        old_ptr = struct.unpack("<I", data[ptr_off:ptr_off+4])[0]
        struct.pack_into("<I", data, ptr_off, ptr_val)
        
        thai_str = "".join(menu['tokens'])
        print(f"    [+] {menu['name']}:")
        print(f"        Thai: '{thai_str}' -> Encoded CJK: '{cjk_str}'")
        print(f"        Offset: {append_offset} (Ptr: {old_ptr} -> {ptr_val})")
        
        append_offset = (append_offset + len(utf8_bytes) + 3) & ~3
        
    # เติม padding ให้ขนาดหาร 16 ลงตัว
    pad = (16 - (len(data) % 16)) % 16
    if pad > 0:
        data.extend(b"\x00" * pad)
        
    with open(OUT_ENTRY_210, "wb") as f:
        f.write(data)
    print(f"[+] Saved modded text to: {OUT_ENTRY_210} ({len(data)} bytes)")

def inject_all():
    """
    ฉีดทั้ง entry_340.g1t และ entry_210.bin เข้า LINKDATA.BIN
    """
    print("[*] Injecting modded files into LINKDATA.BIN...")
    ok1 = inject_entry(340, OUT_G1T)
    ok2 = inject_entry(210, OUT_ENTRY_210)
    if ok1 and ok2:
        print("\n========================================================")
        print("[+] SUCCESS! Thai Menu Mod (CJK) installed successfully!")
        print("    1. entry_340 (Font Sheet) injected")
        print("    2. entry_210 (Traditional Chinese Text) injected")
        print("========================================================")
    else:
        print("[-] Injection failed!")

def main():
    patch_font_dds()
    if not repack_g1t():
        print("[-] Aborting due to repack failure.")
        return
    patch_text_entry_210()
    inject_all()

if __name__ == "__main__":
    main()
