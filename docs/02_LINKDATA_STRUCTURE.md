# โครงสร้างไฟล์เกม Dragon Quest Heroes II

## 1. ที่ตั้งไฟล์เกมแท้
* `C:\Program Files (x86)\Steam\steamapps\common\DRAGON QUEST HEROES™ II\`

## 2. ไฟล์หลักที่บรรจุข้อมูล (LINKDATA Archive)
เกมใช้เอนจินของ **Koei Tecmo (Omega Force)** ข้อมูลเกือบทั้งหมดถูกแพ็กรวมกันใน:
* **`LINKDATA.IDX`** (ขนาด 374,656 bytes):
  * สารบัญระบุตำแหน่งของไฟล์ย่อยทั้งหมด **11,708 ไฟล์**
  * แต่ละรายการ (Entry) มีขนาด **32 bytes** ประกอบด้วย:
    1. `Offset` (8 bytes, uint64) — ตำแหน่งเริ่มต้นใน LINKDATA.BIN
    2. `Size` (8 bytes, uint64) — ขนาดข้อมูลเมื่อแตกแล้ว
    3. `ZSize` (8 bytes, uint64) — ขนาดข้อมูลที่บีบอัด
    4. `ZipFlag` (8 bytes, uint64) — สถานะการบีบอัด (0 = ไม่บีบอัด, 1 = บีบอัด zlib)
* **`LINKDATA.BIN`** (ขนาด 12,763,314,432 bytes / ~12.7 GB):
  * กล่องรวมข้อมูลจริง Alignment ของแต่ละบล็อกคือ 128 bytes (`0x80`)

## 3. ไฟล์ Entry สำคัญที่ค้นพบ
* **`Entry 204` (เมนูหลัก Title Screen & Main Menu):**
  * Offset ใน BIN: `2,250,752` (`0x225800`)
  * ขนาด: `86,768 bytes`
  * บีบอัด: **ไม่ได้บีบอัด (ZipFlag = 0)**
  * มีข้อความเมนูหลักครบทั้งหมด: `Venture Forth`, `Create Adventure Log`, `Delete Adventure Log`, `Graphics Settings`, `Keyboard Settings`, `Exit Game`
* **`Entry 190`**: คู่มือวิธีเล่นเบื้องต้น (416 bytes)
* **`Entry 316`**: เมนูตั้งค่ากราฟิกขั้นสูง (1,392 bytes)
