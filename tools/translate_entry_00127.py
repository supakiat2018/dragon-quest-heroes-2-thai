# -*- coding: utf-8 -*-
"""
translate_entry_00127.py
Translates entry_00127_Skill_Types.csv
"""

import csv

MAP_127 = {
    # Names
    "Bang-Based": "สายอิโอ",
    "Flame Breath": "ลมหายใจเพลิง",
    "Sizz-Based": "สายกิระ",
    "Chain Sickle": "โซ่เคียว",
    "Cutting Edge": "คมดาบขยายใหญ่",
    "Whack-Based": "สายซาคิ",
    "Rubblerouser-Based": "สายจิบาริอา",
    "Knuckle Sandwich": "หมัดตรงทรงพลัง",
    "Parallax": "คลื่นสั่นสะเทือนปฐพี",
    "Zap-Based": "สายไรเดอิน",
    "Flying Knee": "เข่าลอย",
    "Zam-Based": "สายดอลม่า",
    "Needle Shot": "ศรเข็มพิษ",
    "Woosh-Based": "สายบากิ",
    "Quickfire Caster": "ร่ายมนตร์ฉับไว",
    "Power Throw": "ขว้างพลัง",
    "Flying Fist": "หมัดบิน",
    "Crack-Based": "สายเฮียโดะ",
    "Miracle Moon": "จันทราปาฏิหาริย์",
    "Maelstrom": "วังวนพายุ",
    "Frizz-Based": "สายเมร่า",
    "Crackerwhack": "ขวานผ่าปฐพี",
    "Reheal-Based": "สายรีโฮอิมี่",
    "Maulstrom": "คลื่นสลายพายุ",

    # Descriptions
    "Blasts enemies in front with an intense explosion.": "ระเบิดศัตรูเบื้องหน้าด้วยแรงระเบิดอันรุนแรง",
    "Belches blazing hot\\nbreath all over enemies\\nin front.": "พ่นลมหายใจร้อนระอุ\\nใส่ศัตรูทั้งหมด\\nที่อยู่เบื้องหน้า",
    "An ancient incantation that fires forth a racing pillar of flame.": "คาถาโบราณที่ยิงเสาเพลิงพุ่งทะยานไปข้างหน้า",
    "Swings a slicing device on a long chain in a lethal lacerating arc.": "กวัดแกว่งโซ่ติดใบเคียวสังหารเป็นวงกว้างเพื่อเฉือนศัตรู",
    "Increases the size of the sword, then swings down with serious force.": "ขยายขนาดของดาบให้ใหญ่ยักษ์ แล้วฟาดฟันลงมาด้วยพละกำลังมหาศาล",
    "A cursed incantation that sends an enemy to the hereafter.": "คาถาต้องสาปที่จะส่งศัตรูไปสู่ยมโลกในทันที",
    "Draws a secret sigil on the ground that sends stone spikes springing up after a slight delay.": "สลักอักขระลับลงบนพื้นดินเพื่อเรียกเสาหินหนามพุ่งแทงขึ้นมาหลังจากหน่วงเวลาชั่วครู่",
    "A powerful punch produced by focusing force into the fist.": "รวมสมาธิและพละกำลังทั้งหมดไว้ที่กำปั้นแล้วปล่อยหมัดอันทรงพลังออกไป",
    "A strike that sends a shockwave shuddering through the earth.": "ฟาดโจมตีส่งคลื่นกระแทกให้พื้นปฐพีสั่นสะเทือน",
    "A bolt from the blue that strikes foes in front.": "สายฟ้าฟาดจากฟากฟ้าผ่าลงใส่ศัตรูเบื้องหน้า",
    "Dives forward to deliver a bent-legged blow.": "พุ่งตัวไปข้างหน้าแล้วกระโดดแทงเข่าเข้าใส่อย่างจัง",
    "Fires forth bullet-like blobs of black energy.": "ยิงกระสุนพลังงานด้านมืดพุ่งเข้าใส่ศัตรู",
    "An advanced arrow attack with a high chance of a critical hit.": "การยิงธนูขั้นสูงที่มีโอกาสติดคริติคอลสูงเป็นพิเศษ",
    "Stirs up a wicked whirlwind that damages foes in front.": "เรียกพายุหมุนอันรุนแรงขึ้นมาสร้างความเสียหายแก่ศัตรูเบื้องหน้า",
    "Allows attack spells to be cast without any waiting time at all.": "ช่วยให้สามารถร่ายคาถาโจมตีได้โดยไม่มีเวลาหน่วงเลยแม้แต่น้อย",
    "Mows down foes in your path with a shining boomerang.": "กวาดล้างศัตรูในเส้นทางด้วยบูมเมอแรงอันเจิดจ้า",
    "An uplifting uppercut that sends enemies skyward.": "อัปเปอร์คัตเสยขึ้นฟ้าส่งศัตรูลอยละลิ่วขึ้นสู่อากาศ",
    "Flings forth a flurry of ice balls that can freeze foes solid.": "ซัดก้อนน้ำแข็งรัวใส่ศัตรูซึ่งสามารถแช่แข็งเป้าหมายให้หยุดนิ่งได้",
    "Chops chumps into chunks with a storm of spinning sickles.": "ฟันสับศัตรูให้ขาดเป็นชิ้นๆ ด้วยพายุเคียวหมุนสังหาร",
    "Creates a vast vortex that sucks in surrounding monsters.": "สร้างวังวนพายุขนาดยักษ์ที่ดูดมอนสเตอร์โดยรอบเข้ามา",
    "Flings forth a ball of fire.": "ยิงลูกไฟเพลิงเข้าใส่ศัตรู",
    "Swings the axe down from overhead with earth-shattering strength.": "เงื้อขวานเหนือศีรษะแล้วจามลงมาด้วยพละกำลังถล่มพสุธา",
    "Inscribes an ephemeral circle which heals all allies within it for a while.": "สลักวงแหวนเวทมนตร์ที่จะช่วยฟื้นฟูพลังชีวิตให้เพื่อนร่วมทีมทุกคนที่อยู่ภายในเป็นระยะเวลาหนึ่ง",
    "A short, sharp shockwave that shreds foes over a wide area.": "คลื่นกระแทกสั้นๆ แต่เฉียบคมที่จะฉีกร่างศัตรูเป็นวงกว้าง",
}

def translate_127():
    target_csv = "text_csv/categories/entry_00127_Skill_Types.csv"
    with open(target_csv, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    updated = 0
    for r in reader:
        eng = r["OriginalEnglish"].strip()
        if not eng:
            continue
        if eng in MAP_127:
            r["ThaiTranslation"] = MAP_127[eng]
            updated += 1
        else:
            print(f"[!] Warning: Missing in 127: '{eng}'")

    with open(target_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

    print(f"[SUCCESS] Updated {updated} lines in {target_csv}!")

if __name__ == "__main__":
    translate_127()
