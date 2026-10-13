"""
inject_entry.py
สคริปต์ฉีด (Inject) ไฟล์ Entry (เช่น entry_204.bin) กลับเข้าไปใน LINKDATA.BIN ของเกม
พร้อมตรวจสอบความปลอดภัยและสำรองข้อมูลอัตโนมัติ
"""

import os
import struct
import shutil

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODDED_ENTRY = os.path.join(BASE_DIR, "workspace", "entry_204.bin")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

def inject_entry_204():
    idx_path = os.path.join(GAME_DIR, "LINKDATA.IDX")
    bin_path = os.path.join(GAME_DIR, "LINKDATA.BIN")
    
    if not os.path.exists(MODDED_ENTRY):
        print(f"[-] Modded file not found: {MODDED_ENTRY}")
        return
    
    with open(MODDED_ENTRY, "rb") as f:
        modded_data = f.read()
    
    modded_size = len(modded_data)
    print(f"[*] Modded entry size: {modded_size} bytes")
    
    # อ่านข้อมูล Entry 204 จาก LINKDATA.IDX
    with open(idx_path, "rb") as f_idx:
        f_idx.seek(204 * 32)
        offset, orig_size, orig_zsize, zip_flag = struct.unpack("<QQQQ", f_idx.read(32))
    
    print(f"[*] Current Entry 204 in LINKDATA: offset={offset}, size={orig_size}, zsize={orig_zsize}, zip={zip_flag}")
    
    # ตรวจสอบการสำรองข้อมูล
    backup_idx = os.path.join(BACKUP_DIR, "LINKDATA.IDX.bak")
    if not os.path.exists(backup_idx):
        print(f"[*] Creating backup of LINKDATA.IDX to {backup_idx}...")
        shutil.copy2(idx_path, backup_idx)
    
    # กรณีขนาดเท่าเดิม (86768 bytes) และไม่บีบอัด: เขียนทับตรง Offset เดิมได้ทันทีอย่างปลอดภัย
    if modded_size == orig_size and zip_flag == 0:
        print(f"[*] In-place injection: writing {modded_size} bytes directly to LINKDATA.BIN at offset {offset}...")
        with open(bin_path, "r+b") as f_bin:
            f_bin.seek(offset)
            f_bin.write(modded_data)
        print("[+] In-place injection successful!")
    else:
        # กรณีขนาดใหญ่ขึ้น: นำไปเขียนต่อท้าย LINKDATA.BIN (Append to end of BIN) และอัปเดต IDX
        print("[*] Expanded entry injection: appending to end of LINKDATA.BIN...")
        with open(bin_path, "r+b") as f_bin:
            f_bin.seek(0, os.SEEK_END)
            end_pos = f_bin.tell()
            # จัด alignment 128 bytes
            aligned_pos = (end_pos + 127) & ~127
            if aligned_pos > end_pos:
                f_bin.write(b"\x00" * (aligned_pos - end_pos))
            new_offset = aligned_pos
            f_bin.seek(new_offset)
            f_bin.write(modded_data)
            # เติม padding ให้ครบ alignment 128
            tail_pad = (128 - (len(modded_data) % 128)) % 128
            if tail_pad > 0:
                f_bin.write(b"\x00" * tail_pad)
        
        # อัปเดต LINKDATA.IDX
        with open(idx_path, "r+b") as f_idx:
            f_idx.seek(204 * 32)
            f_idx.write(struct.pack("<QQQQ", new_offset, modded_size, modded_size, 0))
        
        print(f"[+] Expanded injection successful! New offset: {new_offset}, size: {modded_size}")

if __name__ == "__main__":
    inject_entry_204()
