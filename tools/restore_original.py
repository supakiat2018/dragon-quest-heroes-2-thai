"""
restore_original.py
สคริปต์กู้คืนข้อมูลเดิมกลับสู่เกม (Restore from Backup)
"""

import os
import struct
import shutil

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_ENTRY = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
BACKUP_IDX = os.path.join(BASE_DIR, "backup", "LINKDATA.IDX.bak")

def restore():
    idx_path = os.path.join(GAME_DIR, "LINKDATA.IDX")
    bin_path = os.path.join(GAME_DIR, "LINKDATA.BIN")
    
    if not os.path.exists(ORIGINAL_ENTRY):
        print(f"[-] Original backup entry not found: {ORIGINAL_ENTRY}")
        return
    
    with open(ORIGINAL_ENTRY, "rb") as f:
        orig_data = f.read()
    
    # 1. คืนค่า LINKDATA.IDX
    if os.path.exists(BACKUP_IDX):
        print("[*] Restoring LINKDATA.IDX...")
        shutil.copy2(BACKUP_IDX, idx_path)
    
    # 2. คืนค่าไบต์ของ Entry 204 ใน LINKDATA.BIN ตรง offset เดิม (2250752)
    with open(idx_path, "rb") as f_idx:
        f_idx.seek(204 * 32)
        offset, size, zsize, zip_flag = struct.unpack("<QQQQ", f_idx.read(32))
    
    print(f"[*] Writing original bytes back to offset {offset}...")
    with open(bin_path, "r+b") as f_bin:
        f_bin.seek(offset)
        f_bin.write(orig_data)
    
    print("[+] Restoration complete! The game files are restored to their original state.")

if __name__ == "__main__":
    restore()
