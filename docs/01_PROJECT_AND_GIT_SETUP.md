# 01. การตั้งชื่อโปรเจกต์และอัปโหลดขึ้น GitHub

## 1. คำแนะนำการตั้งชื่อ Repository (ตามภาพหน้าจอ GitHub)
แนะนำชื่อที่สั้น กระชับ ชัดเจน และสากล:

| ชื่อ Repository ที่แนะนำ | ความหมาย | เหมาะสำหรับ |
|---|---|---|
| **`DQH2-Thai`** *(แนะนำ)* | สั้น จำง่าย เป็นสากลสำหรับม็อดภาษา | โปรเจกต์หลัก |
| **`dragon-quest-heroes-2-thai`** | ค้นหาเจอง่ายบน Google/GitHub | คนทั่วไปค้นหา |
| **`DQH2-TH-Translation`** | บ่งบอกชัดเจนว่าเป็นม็อดแปลภาษา | ทีมงาน/คอมมูนิตี้ |

**Description ที่แนะนำ:**
> Dragon Quest Heroes II Thai Translation Mod & Research Tools (โปรเจกต์ม็อดแปลภาษาไทย ดราก้อนเควสต์ ฮีโร่ส์ 2)

---

## 2. โครงสร้างโฟลเดอร์ในโปรเจกต์ (Clean Directory Layout)

```text
DRAGON QUEST HEROES™ II/
├── .gitignore             # ป้องกันไม่ให้อัปโหลดไฟล์ใหญ่ (.bin, .idx, .rar) ขึ้น Git
├── README.md              # หน้าแรกอธิบายโปรเจกต์
├── docs/                  # โฟลเดอร์เอกสารคู่มือ (.md)
│   ├── 01_PROJECT_AND_GIT_SETUP.md   # การตั้งชื่อและ Git
│   ├── 02_LINKDATA_STRUCTURE.md      # โครงสร้าง LINKDATA.IDX / BIN
│   ├── 03_TEXT_AND_POINTERS.md       # โครงสร้างตารางข้อความและ Pointer
│   └── 04_FONT_AND_THAI_GUIDE.md     # คู่มือทำฟอนต์และแก้ปัญหาภาษาไทย
├── tools/                 # โค้ดสคริปต์ Python สำหรับแยก/ประกอบไฟล์
│   ├── find_text.py       # ค้นหาข้อความใน LINKDATA
│   ├── mod_exit_game.py   # สคริปต์ทดสอบแก้ข้อความและชี้ Pointer
│   ├── inject_entry.py    # สคริปต์ฉีดข้อมูลเข้าเกม
│   └── restore_original.py# สคริปต์กู้คืนไฟล์เดิม
├── backup/                # ไฟล์แท้สำรองก่อนแก้ (ห้ามลบ)
└── workspace/             # ไฟล์ที่กำลังทำงานและแก้ไข
```

---

## 3. ขั้นตอนการนำขึ้น GitHub ด้วยคำสั่ง Git
เปิด PowerShell หรือ Git Bash ในโฟลเดอร์นี้:

```powershell
# 1. เริ่มต้น Git Repository
git init

# 2. เพิ่มไฟล์ทั้งหมด (ไฟล์ใหญ่จะถูก .gitignore กันไว้อัตโนมัติ)
git add .

# 3. Commit ครั้งแรก
git commit -m "Initial commit: DQH2 Thai Mod structure, docs, and extraction tools"

# 4. เชื่อมกับ GitHub (เปลี่ยนชื่อตามที่คุณสร้าง)
git branch -M main
git remote add origin https://github.com/supakiat2018/DQH2-Thai.git

# 5. Push ขึ้น GitHub
git push -u origin main
```
