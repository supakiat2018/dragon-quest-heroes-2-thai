"""
mod_exit_game.py
สคริปต์แก้ไขเมนู "Exit Game" เป็นข้อความตามต้องการ (ค่าเริ่มต้นคือ "ออกเกม")
เพื่อทดสอบการแสดงผลฟอนต์ภาษาไทยและระบบ Multi-byte UTF-8
"""

import struct
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
OUT_FILE = os.path.join(BASE_DIR, "workspace", "entry_204.bin")

def modify_exit_game(target_text="ออกเกม"):
    with open(SRC_FILE, "rb") as f:
        data = bytearray(f.read())
    
    print(f"[*] Original size: {len(data)} bytes")
    
    old_text = b"Exit Game\x00"
    old_offset = data.find(old_text)
    print(f"[*] Original 'Exit Game' at offset: {old_offset} (0x{old_offset:04x})")
    
    # Pointer table อยู่ที่ 0x1a98 (offset 6808)
    ptr_offset = 6808
    old_ptr_val = struct.unpack("<I", data[ptr_offset:ptr_offset+4])[0]
    expected_ptr = old_offset - 0x20
    assert old_ptr_val == expected_ptr, f"Pointer mismatch! Expected {expected_ptr}, got {old_ptr_val}"
    
# นำเข้า THAI_SLOTS จาก draw_thai_glyphs เพื่อให้รหัสตัวอักษรและตำแหน่งตรงกัน 100%
from draw_thai_glyphs import THAI_SLOTS

THAI_TO_CYR = {k: v['char'] for k, v in THAI_SLOTS.items()}


def tokenize_thai(text, mapping_keys):
    sorted_keys = sorted(mapping_keys, key=lambda x: -len(x))
    tokens = []
    i = 0
    while i < len(text):
        matched = False
        for k in sorted_keys:
            if text.startswith(k, i):
                tokens.append(k)
                i += len(k)
                matched = True
                break
        if not matched:
            tokens.append(text[i])
            i += 1
    return tokens

def modify_exit_game(target_text="กี่กี้กี๊กิ๋กัดทดสอเบภาษาไทยโดยจริง"):
    with open(SRC_FILE, "rb") as f:
        data = bytearray(f.read())
    
    print(f"[*] Original size: {len(data)} bytes")
    
    old_text = b"Exit Game\x00"
    old_offset = data.find(old_text)
    print(f"[*] Original 'Exit Game' at offset: {old_offset} (0x{old_offset:04x})")
    
    # Pointer table อยู่ที่ 0x1a98 (offset 6808)
    ptr_offset = 6808
    old_ptr_val = struct.unpack("<I", data[ptr_offset:ptr_offset+4])[0]
    expected_ptr = old_offset - 0x20
    assert old_ptr_val == expected_ptr, f"Pointer mismatch! Expected {expected_ptr}, got {old_ptr_val}"
    
    # Tokenize และแปลงเป็น Cyrillic PUA
    tokens = tokenize_thai(target_text, THAI_TO_CYR.keys())
    encoded_chars = "".join(THAI_TO_CYR.get(t, t) for t in tokens)
    new_bytes = encoded_chars.encode("utf-8") + b"\x00"
    print(f"[*] Target text: '{target_text}'")
    print(f"[*] Tokens: {tokens}")
    print(f"[*] Encoded: '{encoded_chars}'")
    print(f"[*] Hex bytes: {new_bytes.hex(' ')}")
    print(f"[*] Byte length: {len(new_bytes)} bytes (including null)")
    
    # หาพื้นที่ว่างส่วนท้ายของไฟล์ (Trailing zeros)
    last_used = len(data.rstrip(b"\x00"))
    append_offset = last_used + 1
    print(f"[*] Appending text at offset: {append_offset} (0x{append_offset:04x})")
    
    if append_offset + len(new_bytes) > len(data):
        data.extend(b"\x00" * (append_offset + len(new_bytes) - len(data)))
    
    # เขียนไบต์ใหม่ลงไป
    data[append_offset:append_offset+len(new_bytes)] = new_bytes
    
    # อัปเดต pointer: Pointer = File Offset - 0x20
    new_ptr_val = append_offset - 0x20
    struct.pack_into("<I", data, ptr_offset, new_ptr_val)
    print(f"[*] Updated pointer at {ptr_offset}: {old_ptr_val} -> {new_ptr_val} (0x{new_ptr_val:08x})")
    
    with open(OUT_FILE, "wb") as f:
        f.write(data)
    
    print(f"[+] Saved modded entry to: {OUT_FILE}")

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "กี่กี้กี๊กิ๋กัดทดสอเบภาษาไทยโดยจริง"
    modify_exit_game(text)
