"""
mod_exit_game.py
สคริปต์แก้ไขคำว่า "Exit Game" เป็น "xxxxxxxxxxxxxxxxxx" เพื่อทดสอบความยาวตัวอักษร
โดยใช้วิธี 'เขียนต่อท้ายในพื้นที่ว่างแล้วแก้ Pointer ชี้ไป' (Append & Repoint Method)
"""

import struct
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILE = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
OUT_FILE = os.path.join(BASE_DIR, "workspace", "entry_204.bin")

def main():
    with open(SRC_FILE, "rb") as f:
        data = bytearray(f.read())
    
    print(f"[*] Original size: {len(data)} bytes")
    
    # ตรวจสอบตำแหน่งเดิมของ Exit Game
    old_text = b"Exit Game\x00"
    old_offset = data.find(old_text)
    print(f"[*] Original 'Exit Game' found at file offset: {old_offset} (0x{old_offset:04x})")
    
    # Pointer table อยู่ที่ 0x1a98 (offset 6808)
    ptr_offset = 6808
    old_ptr_val = struct.unpack("<I", data[ptr_offset:ptr_offset+4])[0]
    expected_ptr = old_offset - 0x20
    print(f"[*] Pointer at offset {ptr_offset}: {old_ptr_val} (expected: {expected_ptr})")
    assert old_ptr_val == expected_ptr, "Pointer mismatch!"
    
    # ข้อความใหม่ที่จะทดสอบ
    new_text = "xxxxxxxxxxxxxxxxxx".encode("utf-8") + b"\x00"
    print(f"[*] New text: '{new_text[:-1].decode()}' (length: {len(new_text)} bytes including null)")
    
    # หาตำแหน่งว่างส่วนท้ายของไฟล์ (Trailing zeros)
    last_used = len(data.rstrip(b"\x00"))
    append_offset = last_used + 1 # เริ่มเขียนต่อจาก byte สุดท้าย
    print(f"[*] Appending new text at file offset: {append_offset} (0x{append_offset:04x})")
    
    # ตรวจสอบว่ามีพื้นที่ว่างพอในขนาดไฟล์เดิมหรือไม่
    if append_offset + len(new_text) > len(data):
        # ถ้าเกิน ให้ขยายขนาดไฟล์
        data.extend(b"\x00" * (append_offset + len(new_text) - len(data)))
    
    # เขียนข้อความใหม่ลงในพื้นที่ว่าง
    data[append_offset:append_offset+len(new_text)] = new_text
    
    # คำนวณค่า Pointer ใหม่: Pointer = File Offset - 0x20
    new_ptr_val = append_offset - 0x20
    struct.pack_into("<I", data, ptr_offset, new_ptr_val)
    print(f"[*] Updated pointer at {ptr_offset}: {old_ptr_val} -> {new_ptr_val} (0x{new_ptr_val:08x})")
    
    # บันทึกไฟล์ใหม่
    with open(OUT_FILE, "wb") as f:
        f.write(data)
    
    print(f"[+] Successfully saved modded file to: {OUT_FILE}")
    print(f"[+] Modded file size: {len(data)} bytes")

if __name__ == "__main__":
    main()
