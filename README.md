# DRAGON QUEST HEROES™ II - Thai Translation Project

โปรเจกต์ม็อดแปลภาษาไทยสำหรับเกม **DRAGON QUEST HEROES™ II** (PC Steam) โดยอาศัยระบบ **English Core Proportional Typography** บนฟอนต์ `entry_342` และข้อความ `entry_204.bin`

---

## ความคืบหน้าปัจจุบัน (Current Progress)

### 1. เมนูหลัก Title Screen (7 รายการ)
* **เริ่มการเดินทาง** *(Venture Forth)*
* **สร้างบันทึก** *(Create Adventure Log)*
* **ลบบันทึก** *(Delete Adventure Log)*
* **ตั้งค่ากราฟิก** *(Graphics Settings)*
* **ตั้งค่าคีย์บอร์ด** *(Keyboard Settings)*
* **ตั้งค่าเมาส์** *(Mouse Settings)*
* **ออกจากเกม** *(Exit Game)*

### 2. ไดอะล็อกและข้อความระบบ (System & Dialogue)
* **ต้องการสร้างบันทึกการเดินทางในช่องใด?** *(Which slot do you want to create an adventure log in?)*

### 3. จุดเด่นของระบบฟอนต์ (Typography Highlights)
* **Proportional Font Width:** ตัวอักษรแต่ละตัวมีความกว้างตามสัดส่วนจริง (16–23px) ไม่มีการบีบ/ยืดภาพ (Zero distortion)
* **Natural Kerning:** สระหน้า (`เ`, `ใ`) ชิดขวาแนบพยัญชนะตัวถัดไป, สระหลัง (`า`) ชิดซ้ายแนบพยัญชนะตัวหน้า คำต่อกันเป็นธรรมชาติ
* **3-Tier Cluster Stacking:** รองรับคลัสเตอร์ 3 ชั้น (`ตั้`, `ริ่`) จัดวางไม้หันอากาศ/สระอิ ซ้อนกับไม้โท/ไม้เอก อย่างประณีต ไม่ทับกันเป็นก้อนและไม่ตกขอบ
* **Russian Cyrillic Slot Mapping:** ถอดรหัสพิกัด Cyrillic 66 ช่องใน `entry_342` ได้แม่นยำ 100% พร้อมรองรับตัวอักษร Yo (`ё` / `Ё`)

---

## โครงสร้างโฟลเดอร์ (Folder Structure)

* **`backup/`**: เก็บไฟล์ต้นฉบับแท้ก่อนเริ่มแก้ไข (`entry_204_original.bin`, `entry_342_original.png`, `LINKDATA.IDX.bak`)
* **`docs/`**: เอกสารและคู่มือทางเทคนิค (.md)
* **`tools/`**: สคริปต์เครื่องมือแปลงไฟล์, ถอดรหัส, และฉีดไฟล์เข้าเกม
* **`workspace/`**: ไฟล์งานระหว่างดัดแปลงและพรีวิวภาพ

---

## เครื่องมือสำคัญใน `tools/`

1. **`mod_en_thai_menus.py`**: สคริปต์หลักสำหรับสร้าง Font Sheet ภาษาไทย, คอมเพรส DXT5, รีแพ็ก G1T, แปลข้อความและอัปเดต Pointer Table ใน `entry_204.bin` และฉีดเข้า `LINKDATA.BIN`
2. **`inject_entry.py`**: เครื่องมือฉีด Entry ใดๆ เข้า `LINKDATA.BIN` โดยตรง ทั้งแบบ In-place และ Appended
3. **`g1t_tool.py`**: เครื่องมือถอดและรวมไฟล์ Texture รูปแบบ G1T / DDS ของ Koei Tecmo
4. **`restore_original.py`**: สคริปต์กู้คืนไฟล์ต้นฉบับแท้กลับเข้าเกมได้ทันที
5. **`exact_cyrillic_table.py`**: ตารางจับคู่อักษร Cyrillic 66 ตัวตรงตามพิกัด Row/Col ใน `entry_342`
6. **`test_all_44_thai.py`**: สคริปต์ทดสอบเรนเดอร์พยัญชนะไทย 44 ตัว (ก–ฮ)
