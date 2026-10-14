"""
inject_inplace.py
สคริปต์ฉีด (Inject) entry_339.g1t และ entry_342.g1t แบบ In-place
โดยบีบอัดด้วย Koei Tecmo Chunk Compression (Zlib level 9)
แล้วเขียนทับลงใน Offset เดิมของ LINKDATA.BIN ตรงๆ 100%
ทำให้เกมโหลดได้ทันทีโดยไม่ต้องแก้ไขตาราง Offset ใน Engine
"""

import os
import sys
import struct
import zlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
BIN_PATH = os.path.join(GAME_DIR, "LINKDATA.BIN")
IDX_PATH = os.path.join(GAME_DIR, "LINKDATA.IDX")
BAK_IDX = os.path.join(BASE_DIR, "backup", "LINKDATA.IDX.bak")

def pack_entry_chunks(data, chunk_size=0x40000):
    full_size = len(data)
    chunks = (full_size + chunk_size - 1) // chunk_size
    zchunks = [zlib.compress(data[i*chunk_size : (i+1)*chunk_size], 9) for i in range(chunks)]
    buf = bytearray()
    buf.extend(struct.pack('<III', chunk_size, chunks, full_size))
    for z in zchunks:
        buf.extend(struct.pack('<I', 4 + len(z)))
    padding_offset = 0
    for z in zchunks:
        pos = len(buf)
        pad = (128 - ((pos - padding_offset) % 128)) % 128
        buf.extend(b'\x00' * pad)
        padding_offset = len(buf)
        buf.extend(struct.pack('<I', len(z)))
        buf.extend(z)
    return bytes(buf)

def inject_entry_inplace(entry_id, file_path):
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return False
        
    with open(file_path, "rb") as f:
        raw_data = f.read()
        
    packed = pack_entry_chunks(raw_data)
    
    with open(BAK_IDX, "rb") as f_bak:
        f_bak.seek(entry_id * 32)
        orig_off, orig_size, orig_zsize, orig_zip = struct.unpack("<QQQQ", f_bak.read(32))
        
    print(f"[*] Entry {entry_id}: Raw={len(raw_data)} -> Packed={len(packed)} (Orig Slot Limit={orig_zsize})")
    if len(packed) > orig_zsize:
        print(f"[-] Error: Packed data exceeds original slot limit ({len(packed)} > {orig_zsize})")
        return False
        
    pad_len = orig_zsize - len(packed)
    with open(BIN_PATH, "r+b") as f_bin:
        f_bin.seek(orig_off)
        f_bin.write(packed)
        if pad_len > 0:
            f_bin.write(b"\x00" * pad_len)
            
    with open(IDX_PATH, "r+b") as f_idx:
        f_idx.seek(entry_id * 32)
        f_idx.write(struct.pack("<QQQQ", orig_off, orig_size, orig_zsize, 1))
        
    print(f"[+] Entry {entry_id} successfully injected in-place to offset {orig_off}!")
    return True

if __name__ == "__main__":
    p339 = os.path.join(BASE_DIR, "workspace", "entry_339.g1t")
    p342 = os.path.join(BASE_DIR, "workspace", "tex_342", "out", "entry_342.g1t")
    inject_entry_inplace(339, p339)
    inject_entry_inplace(342, p342)
