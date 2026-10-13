# DRAGON QUEST HEROES™ II - Thai Translation Project

โปรเจกต์ศึกษาโครงสร้างไฟล์และเครื่องมือแปลภาษาไทยสำหรับเกม DRAGON QUEST HEROES™ II (PC Steam)

## สารบัญเอกสาร (Documentation)
* [01. การตั้งชื่อโปรเจกต์และ Git](docs/01_PROJECT_AND_GIT_SETUP.md)
* [02. โครงสร้างไฟล์ LINKDATA](docs/02_LINKDATA_STRUCTURE.md)
* [03. โครงสร้างตารางข้อความและ Pointer](docs/03_TEXT_AND_POINTERS.md)
* [04. คู่มือฟอนต์และแนวทางภาษาไทย](docs/04_FONT_AND_THAI_GUIDE.md)

## โครงสร้างโฟลเดอร์
* **`backup/`**: เก็บไฟล์ต้นฉบับแท้ก่อนเริ่มแก้ไข
* **`docs/`**: เอกสารและคู่มือทางเทคนิค (.md)
* **`tools/`**: สคริปต์เครื่องมือแปลงไฟล์และทดสอบ
* **`workspace/`**: ไฟล์งานที่กำลังดัดแปลง

## เครื่องมือใน `tools/`
1. `find_text.py`: ค้นหาข้อความในไฟล์ยักษ์ `LINKDATA.BIN`
2. `mod_exit_game.py`: ทดสอบเปลี่ยนคำว่า Exit Game เป็นความยาว 18 ตัวอักษร ด้วยวิธี Append & Repoint
3. `inject_entry.py`: ฉีดไฟล์ที่แก้แล้วกลับเข้าเกม
4. `restore_original.py`: กู้คืนไฟล์แท้เดิมกลับเข้าเกม
