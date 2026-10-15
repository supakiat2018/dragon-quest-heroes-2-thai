# -*- coding: utf-8 -*-
"""
translate_entry_00099.py
Translates entry_00099_Stats_Attributes.csv
"""

import csv

MAP_99 = {
    "Maximum HP": "HP สูงสุด",
    "Maximum MP": "MP สูงสุด",
    "Strength": "พลังกาย",
    "Resilience": "ความอดทน",
    "Wisdom": "สติปัญญา",
    "Deftness": "ความคล่องแคล่ว",
    "Attack": "พลังโจมตี",
    "Defence": "พลังป้องกัน",
    "Critical Hit Chance": "อัตราติดคริติคอล",
    "Tension Build Rate": "อัตราสะสมเทนชัน",
    "Magical Resistance": "ความต้านทานเวทมนตร์",
    "Instant Death Resistance": "ความต้านทานความตายฉับพลัน",
    "More Yggdrasil Leaves": "จำนวนใบไม้อิกดราซิลเพิ่มขึ้น",
    "Mini Medal Drop Rate": "อัตราดรอปเหรียญมินิเมดัล",
    "Tension Up When Damaged": "เพิ่มเทนชันเมื่อได้รับความเสียหาย",
    "Chance of No MP Cost": "โอกาสไม่เสีย MP",
    "Longer High-Tension Period": "ยืดระยะเวลาไฮเทนชัน",
    "Chance to Revive Instantly on Death": "โอกาสฟื้นคืนชีพทันทีเมื่อตาย",
    "Quake/Roar Resistance": "ต้านทานแผ่นดินไหว/เสียงคำราม",
    "Coup de Grâce Damage": "ความเสียหายท่าไม้ตายคูปเดอกราซ",
    "Damage to Weak Points": "ความเสียหายเมื่อโจมตีจุดอ่อน",
    "360-Degree Block": "ป้องกันรอบทิศทาง 360 องศา",
    "Gold Earned": "เหรียญทองที่ได้รับ",
    "Experience Earned": "ค่าประสบการณ์ที่ได้รับ",
    "Lower Damage, More Criticals": "ดาเมจลดลงแต่คริติคอลบ่อยขึ้น",
    "Cast Kamikazee on Death": "ร่ายเมกันเตะสละชีพเมื่อตาย",
    "Att./Def. Increases Last Longer": "บัฟเพิ่มพลังโจมตี/ป้องกันอยู่นานขึ้น",
    "Death Blow Survival Chance": "โอกาสรอดชีวิตจากการโจมตีถึงตาย",
    "Roar Resistance": "ต้านทานเสียงคำราม",
    "Reduced Damage When Frozen": "ลดความเสียหายขณะถูกแช่แข็ง",
    "Reduced Damage When Blocking": "ลดความเสียหายขณะตั้งการ์ดป้องกัน",
    "Defence Increases Boosted": "เพิ่มประสิทธิภาพบัฟป้องกัน",
    "Attack Increases Boosted": "เพิ่มประสิทธิภาพบัฟโจมตี",
    "Damage Up, MP Regeneration Down": "พลังโจมตีเพิ่มขึ้นแต่ฟื้นฟู MP ลดลง",
    "MP Cost Up, Skill Chrg. Time Down": "ใช้ MP เพิ่มขึ้นแต่ชาร์จสกิลเร็วขึ้น",
    "Resist Slowing": "ต้านทานสภาวะเคลื่อนไหวช้า",
    "Damage Occasionally Ignored": "มีโอกาสมองข้ามความเสียหาย",
    "Mild MP Regeneration": "ฟื้นฟู MP เล็กน้อย",
    "Mild HP Regeneration": "ฟื้นฟู HP เล็กน้อย",
    "Shorter Quake Stumble Duration": "ลดระยะเวลาเสียหลักจากแผ่นดินไหว",
    "Shorter Seal Duration": "ลดระยะเวลาถูกสะกดเวท",
    "Shorter Sleep Duration": "ลดระยะเวลาหลับใหล",
    "Shorter Poison Duration": "ลดระยะเวลาติดพิษ",
    "Shorter Bedazzle Duration": "ลดระยะเวลาตาพร่ามัว",
    "Shorter Curse Duration": "ลดระยะเวลาติดคำสาป",
    "Ability Damage": "ความเสียหายจากอบิลิตี้",
    "Spell Damage": "ความเสียหายจากคาถา",
    "Breath Resistance": "ต้านทานลมหายใจเพลิง/ไอพิษ",
    "Tension Up When Some Foes Beaten": "เพิ่มเทนชันเมื่อกำจัดศัตรู",
    "Critical Spell Rate": "อัตราคริติคอลของคาถา",
    "Reduced Dance Effect": "ลดผลกระทบจากการถูกบังคับเต้นรำ",
    "Chance of Free Revival": "โอกาสฟื้นคืนชีพโดยไม่เสียแต้ม",
    "Improved Dodging": "เพิ่มประสิทธิภาพการกลิ้งหลบ",
    "More Item Drops": "เพิ่มอัตราดรอปไอเทม",
    "Attack Up When Low on HP": "พลังโจมตีเพิ่มขึ้นเมื่อ HP เหลือน้อย",
    "Defence Up When Low on HP": "พลังป้องกันเพิ่มขึ้นเมื่อ HP เหลือน้อย",
    "Criticals Up When Low on HP": "คริติคอลเพิ่มขึ้นเมื่อ HP เหลือน้อย",
    "Damage to Flying Monsters": "ความเสียหายต่อมอนสเตอร์บินได้",
    "Strength of Monster Minions": "พละกำลังของสมุนมอนสเตอร์",
    "Status Effect Resistance": "ต้านทานสถานะผิดปกติ",
    "Helping Hand from Healix": "ความช่วยเหลือจากโฮมิรอน",
    "HP of Person/Object Defended": "HP ของเป้าหมาย/บุคคลที่ต้องปกป้อง",
    "Chance of Poisoning upon Attack": "มีโอกาสสร้างสถานะพิษเมื่อโจมตี",
    "Chance to Bedazzle upon Attack": "มีโอกาสสร้างสถานะตาพร่าเมื่อโจมตี",
    "Chance of Instadeath upon Attack": "มีโอกาสสังหารทันทีเมื่อโจมตี",
    "Chance to Divide upon Attack": "มีโอกาสแยกร่างเมื่อโจมตี",
    "Attacks Can Reduce Defence": "การโจมตีมีโอกาสลดพลังป้องกันศัตรู",
    "Metal Monster Encounters Up": "เพิ่มโอกาสพบเจอมอนสเตอร์ตระกูลเมทัล",
    "Ignore Enemy Block": "โจมตีทะลุการป้องกันของศัตรู",
    "Blast Resistance": "ต้านทานแรงระเบิด",
    "No Recoil When Attacked": "ไม่ชะงักเมื่อถูกโจมตี",
    "Ingredient Drop Rate": "อัตราดรอปวัตถุดิบ",
    "Medicinal Herb Drop Rate": "อัตราดรอปสมุนไพรรักษา",
    "Status Ailment Resistance": "ต้านทานอาการผิดปกติ",
    "HP Down, Spell Resistance Up": "HP ลดลงแต่ต้านทานเวทมนตร์เพิ่มขึ้น",
    "Magical Might": "พลังโจมตีเวทมนตร์",
    "Recover HP on Attack": "ฟื้นฟู HP เมื่อโจมตี",
    "Chance to Stun": "มีโอกาสทำให้ศัตรูชะงักงัน",
    "Critical Hits on Weak Points": "คริติคอลเมื่อโจมตีโดนจุดอ่อน",
    "Occasionally Can't Help Dancing": "เผลอเต้นรำโดยไม่รู้ตัวเป็นครั้งคราว",
    "Occasionally Cursed": "ติดคำสาปเป็นครั้งคราว",
    "Status Ailments Last Longer": "สถานะผิดปกติต่อศัตรูอยู่นานขึ้น",
    "Gain Tension When Dancing": "เพิ่มเทนชันเมื่อเต้นรำ",
    "Can Pass on Own Ailments When Hit": "ส่งต่อสถานะผิดปกติของตนเองเมื่อถูกโจมตี",
    "Regenerate HP While Sleeping": "ฟื้นฟู HP ขณะหลับใหล",
    "Reduced Tag Trick MP Cost": "ลดการใช้ MP ของแท็กทริก",
    "Increased Tag Trick Damage": "เพิ่มความเสียหายของแท็กทริก",
    "Substitution Medals Last Longer": "เหรียญมอนสเตอร์แปลงร่างอยู่นานขึ้น",
    "Substitution Monsters Are Stronger": "มอนสเตอร์แปลงร่างแข็งแกร่งขึ้น",
    "More Magic Water": "จำนวนน้ำมนตราเพิ่มขึ้น",
    "Critical Hits Occasionally Ignored": "มีโอกาสมองข้ามความเสียหายคริติคอล",
    "Attack Up When Ally Slain": "พลังโจมตีเพิ่มขึ้นเมื่อเพื่อนร่วมทีมตาย",
    "Defence Up When Ally Slain": "พลังป้องกันเพิ่มขึ้นเมื่อเพื่อนร่วมทีมตาย",
    "Tension Up When Ally Slain": "เพิ่มเทนชันเมื่อเพื่อนร่วมทีมตาย",
    "Increased Status Ailment Chance": "เพิ่มโอกาสสร้างสถานะผิดปกติ",
    "HP Regen. When Damaged at Full MP": "ฟื้นฟู HP เมื่อโดนโจมตีขณะที่ MP เต็ม",
    "Gold Up, Experience Down": "ได้รับเหรียญทองเพิ่มขึ้นแต่ค่าประสบการณ์ลดลง",
    "Experience Up, Proficiency Down": "ได้รับค่าประสบการณ์เพิ่มขึ้นแต่ความชำนาญลดลง",
    "Proficiency Up, Gold Down": "ได้รับความชำนาญเพิ่มขึ้นแต่เหรียญทองลดลง",
    "Damage Up with Status Ailments": "โจมตีแรงขึ้นตามจำนวนสถานะผิดปกติ",
    "Increased Critical Damage": "เพิ่มความเสียหายคริติคอล",
    "Increased Critical Spell Damage": "เพิ่มความเสียหายคริติคอลของคาถา",
    "Magical Might Up, Max. HP Down": "พลังเวทเพิ่มขึ้นแต่ HP สูงสุดลดลง",
    "Max. MP Up, Max. HP Down": "MP สูงสุดเพิ่มขึ้นแต่ HP สูงสุดลดลง",
    "Sometimes Resist Status Ailments": "มีโอกาสต้านทานสถานะผิดปกติ",
    "Fire Damage Up with Heavy Wands": "เพิ่มความเสียหายธาตุไฟเมื่อถือคทาเวทมนตร์",
    "Wind Damage Up with Heavy Wands": "เพิ่มความเสียหายธาตุลมเมื่อถือคทาเวทมนตร์",
    "Lightning Dmg. Up with Heavy Wands": "เพิ่มความเสียหายธาตุสายฟ้าเมื่อถือคทาเวทมนตร์",
    "Explosion Dmg. Up with Heavy Wands": "เพิ่มความเสียหายธาตุระเบิดเมื่อถือคทาเวทมนตร์",
    "Dark Damage Up with Heavy Wands": "เพิ่มความเสียหายธาตุมืดเมื่อถือคทาเวทมนตร์",
    "Sometimes Attract Foes' Attention": "ดึงดูดความสนใจของศัตรูเป็นครั้งคราว",
    "Get Targeted More": "ตกเป็นเป้าหมายโจมตีบ่อยขึ้น",
    "Avoid Some Monster Battles": "หลีกเลี่ยงการต่อสู้กับมอนสเตอร์บางส่วน",
    "Chance to Auto-Defend": "มีโอกาสตั้งการ์ดป้องกันอัตโนมัติ",
    "Damage Up with Small Party": "โจมตีแรงขึ้นเมื่อมีสมาชิกในปาร์ตี้น้อย",
    "MP Recovers When Low on HP": "ฟื้นฟู MP เมื่อ HP เหลือน้อย",
    "Tension Up When Low on HP": "เพิ่มเทนชันเมื่อ HP เหลือน้อย",
    "Reduced Freeze Time": "ลดระยะเวลาถูกแช่แข็ง",
    "Reduced Damage from Poison": "ลดความเสียหายจากพิษ",
    "Increased Kamikazee Power": "เพิ่มอานุภาพคาถาสละชีพเมกันเตะ",
    "Bedazzlement Resistance": "ต้านทานอาการตาพร่ามัว",
    "Seal Resistance": "ต้านทานการถูกสะกดเวทมนตร์",
    "Healstone Power": "ประสิทธิภาพของหินรักษา",
    "HP/MP Up at Max. Tension": "เพิ่ม HP/MP เมื่อเทนชันเต็มขีดสุด",
    "Recover MP on Critical Hit": "ฟื้นฟู MP เมื่อโจมตีติดคริติคอล",
    "Movement Speed": "ความเร็วในการเคลื่อนที่",
    "Bigger Arrows": "ขยายขนาดของลูกศรธนู",
    "Absorb More MP from Slimes": "ดูดซับ MP จากสไลม์ได้มากขึ้น",
    "More Gold Nuglets from Slimes": "ได้รับเศษทองคำจากสไลม์มากขึ้น",
    "Hit Metal Slimes More Easily": "โจมตีโดนสไลม์ตระกูลเมทัลง่ายขึ้น",
    "Quick Tension Gain When Fired Up": "สะสมเทนชันได้อย่างรวดเร็วเมื่อฮึกเหิม",
}

def translate_99():
    target_csv = "text_csv/categories/entry_00099_Stats_Attributes.csv"
    with open(target_csv, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    updated = 0
    for r in reader:
        eng = r["OriginalEnglish"].strip()
        if not eng:
            continue
        if eng in MAP_99:
            r["ThaiTranslation"] = MAP_99[eng]
            updated += 1
        else:
            print(f"[!] Warning: Missing in 99: '{eng}'")

    with open(target_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

    print(f"[SUCCESS] Updated {updated} lines in {target_csv}!")

if __name__ == "__main__":
    translate_99()
