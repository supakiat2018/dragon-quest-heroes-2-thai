"""
restore_original.py
สคริปต์กู้คืนข้อมูลเดิมกลับสู่เกม (Restore from Backup)
"""

import os
import struct
import shutil

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_ENTRY_204 = os.path.join(BASE_DIR, "backup", "entry_204_original.bin")
ORIGINAL_ENTRY_210 = os.path.join(BASE_DIR, "backup", "entry_210_original.bin")
ORIGINAL_DDS_340 = os.path.join(BASE_DIR, "backup", "entry_340.TEX0.dxt5.dds.bak")
BACKUP_IDX = os.path.join(BASE_DIR, "backup", "LINKDATA.IDX.bak")

def restore():
    idx_path = os.path.join(GAME_DIR, "LINKDATA.IDX")
    bin_path = os.path.join(GAME_DIR, "LINKDATA.BIN")
    
    # 1. คืนค่า LINKDATA.IDX
    if os.path.exists(BACKUP_IDX):
        print("[*] Restoring LINKDATA.IDX...")
        shutil.copy2(BACKUP_IDX, idx_path)
    
    # 2. คืนค่าไบต์ของ Entry 204 (Text ENG)
    if os.path.exists(ORIGINAL_ENTRY_204):
        with open(ORIGINAL_ENTRY_204, "rb") as f:
            orig_data = f.read()
        with open(idx_path, "rb") as f_idx:
            f_idx.seek(204 * 32)
            offset, size, zsize, zip_flag = struct.unpack("<QQQQ", f_idx.read(32))
        print(f"[*] Restoring Entry 204 (ENG) at offset {offset}...")
        with open(bin_path, "r+b") as f_bin:
            f_bin.seek(offset)
            f_bin.write(orig_data)
            
    # 3. คืนค่าไบต์ของ Entry 210 (Text CHT)
    if os.path.exists(ORIGINAL_ENTRY_210):
        with open(ORIGINAL_ENTRY_210, "rb") as f:
            orig_data = f.read()
        with open(idx_path, "rb") as f_idx:
            f_idx.seek(210 * 32)
            offset, size, zsize, zip_flag = struct.unpack("<QQQQ", f_idx.read(32))
        print(f"[*] Restoring Entry 210 (CHT) at offset {offset}...")
        with open(bin_path, "r+b") as f_bin:
            f_bin.seek(offset)
            f_bin.write(orig_data)
            
    # 4. คืนค่าไฟล์ DDS ต้นฉบับ
    dest_dds = os.path.join(BASE_DIR, "workspace", "tex_340", "entry_340.TEX0.dxt5.dds")
    if os.path.exists(ORIGINAL_DDS_340):
        shutil.copyfile(ORIGINAL_DDS_340, dest_dds)
        print("[*] Restored original font DDS to workspace/tex_340/")
    
    print("[+] Restoration complete! The game files are restored to their original state.")

if __name__ == "__main__":
    restore()

