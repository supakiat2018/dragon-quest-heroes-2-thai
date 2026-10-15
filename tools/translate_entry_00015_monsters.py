# -*- coding: utf-8 -*-
"""
translate_entry_00015_monsters.py
Translates entry_00015_Monsters.csv with canonical Thai Dragon Quest names.
"""

import csv
import os

MONSTER_MAP = {
    # 1. Slimes
    "slime": "สไลม์",
    "she-slime": "ชีสไลม์",
    "metal slime": "เมทัลสไลม์",
    "healslime": "ฮีลสไลม์",
    "cureslime": "เคียวร์สไลม์",
    "king slime": "คิงสไลม์",
    "king cureslime": "คิงเคียวร์สไลม์",
    "metal king slime": "เมทัลคิงสไลม์",
    "bubble slime": "บับเบิ้ลสไลม์",
    "liquid metal slime": "ฮากุเรเมทัล",
    "slime knight": "สไลม์ไนท์",
    "metal slime knight": "เมทัลสไลม์ไนท์",
    "agoomulator": "สไลม์รวมร่าง",

    # 2. Drackies
    "dracky": "ดรากี้",
    "drackyma": "ดรากี้ม่า",
    "drackmage": "ดราคเมจ",

    # 3. Skeletons & Zombies
    "skeleton": "โครงกระดูก",
    "skeleton soldier": "ทหารโครงกระดูก",
    "dark skeleton": "โครงกระดูกทมิฬ",
    "walking corpse": "ซากศพเดินได้",
    "corpse corporal": "คอร์ปส์คอร์ปอรัล",
    "toxic zombie": "ซอมบี้พิษ",
    "ghoul": "กูล",
    "zombie gladiator": "ซอมบี้กลาดิเอเตอร์",
    "hell gladiator": "เฮลกลาดิเอเตอร์",
    "mummy": "มัมมี่",
    "mummy boy": "มัมมี่บอย",
    "blood mummy": "บลัดมัมมี่",
    "bone baron": "บอนบารอน",
    "wight king": "ไวท์คิง",
    "wight priest": "ไวท์พรีสต์",
    "veteran wight priest": "สุดยอดไวท์พรีสต์",

    # 4. Beasts & Cats
    "jailcat": "แมวลายคุก",
    "candy cat": "แคนดี้แคท",
    "terror tabby": "แมวลายคลั่ง",
    "veteran candy cat": "สุดยอดแคนดี้แคท",
    "great sabrecat": "เกรตเซเบอร์แคท",
    "silver sabrecat": "ซิลเวอร์เซเบอร์แคท",
    "winged sabrecat": "เซเบอร์แคทติดปีก",
    "veteran great sabrecat": "สุดยอดเกรตเซเบอร์แคท",
    "missing lynx": "ลิงซ์ล่องหน",
    "veteran missing lynx": "สุดยอดลิงซ์ล่องหน",
    "draguar": "จากัวร์มังกร",
    "hellion": "เฮลเลียน",

    # 5. Demons & Imps
    "imp": "อิมป์",
    "minidemon": "มินิเดมอน",
    "archdemon": "อาร์ชเดมอน",
    "belial": "เบลิอัล",
    "veteran belial": "สุดยอดเบลิอัล",
    "pazuzu": "พาซูซู",
    "veteran pazuzu": "สุดยอดพาซูซู",
    "barbatos": "บาร์บาทอส",
    "demon-at-arms": "เดมอนแอทอาร์มส์",
    "batmandrill": "แบทแมนดริลล์",
    "silvapithecus": "ซิลวาพิเทคัส",
    "moosifer": "มูซิเฟอร์",
    "master moosifer": "มาสเตอร์มูซิเฟอร์",
    "veteran master moosifer": "สุดยอดมาสเตอร์มูซิเฟอร์",
    "pruslas": "พรุสลาส",
    "veteran pruslas": "สุดยอดพรุสลาส",
    "hell niño": "เฮลนีโญ",
    "low djinks": "ยักษ์จินนี่น้อย",
    "high djinks": "ยักษ์จินนี่ใหญ่",
    "zamtasm": "แซมแทสซึม",
    "loss leader": "ลอสลีดเดอร์",

    # 6. Golems & Statues
    "golem": "โกเลม",
    "stone golem": "สโตนโกเลม",
    "gold golem": "โกลด์โกเลม",
    "living statue": "รูปปั้นมีชีวิต",
    "stone guardian": "สโตนการ์เดียน",
    "ice sculpture": "ประติมากรรมน้ำแข็ง",

    # 7. Machines
    "killing machine": "คิลเลอร์แมชชีน",
    "overkilling machine": "โอเวอร์คิลเลอร์แมชชีน",
    "überkilling machine": "อูเบอร์คิลเลอร์แมชชีน",
    "hunter mech": "ฮันเตอร์เมค",
    "Type G0": "ไทป์ G0",
    "crimson killing machine": "คิลเลอร์แมชชีนสีชาด",
    "autombaton": "หุ่นกลอัตโนมัติ",

    # 8. Knights & Armours
    "restless armour": "เกราะพเนจร",
    "infernal armour": "เกราะนรก",
    "lethal armour": "เกราะสังหาร",
    "knight errant": "อัศวินพเนจร",
    "knight aberrant": "ไนท์แอบเบอร์แรนต์",
    "knight abhorrent": "ไนท์แอบฮอร์เรนต์",
    "veteran knight aberrant": "สุดยอดไนท์แอบเบอร์แรนต์",
    "grim rider": "กริมไรเดอร์",
    "night rider": "ไนท์ไรเดอร์",
    "roseguardin": "โรสการ์เดียน",
    "Samson Knight": "อัศวินแซมสัน",

    # 9. Trolls & Giants
    "troll": "โทรลล์",
    "boss troll": "บอสโทรลล์",
    "stout troll": "สเตาต์โทรลล์",
    "great troll": "เกรตโทรลล์",
    "treasure troll": "เทรเชอร์โทรลล์",
    "gigantes": "กิกันเตส",
    "Atlas": "แอตลาส",
    "Ultimate Atlas": "อัลติเมทแอตลาส",
    "night clubber": "ไนท์คลับเบอร์",
    "veteran night clubber": "สุดยอดไนท์คลับเบอร์",

    # 10. Dragons
    "green dragon": "มังกรเขียว",
    "blue dragon": "มังกรฟ้า",
    "dread dragon": "มังกรทมิฬ",
    "hacksaurus": "แฮ็กซอรัส",
    "axesaurus": "แอ็กซ์ซอรัส",
    "tyrantosaurus": "ไทรันโตซอรัส",
    "drakulard": "ดราคูลาร์ด",
    "veteran drakulard": "สุดยอดดราคูลาร์ด",

    # 11. Bird & Flying Monsters
    "chimaera": "คิเมร่า",
    "hocus chimaera": "โฮคัสคิเมร่า",
    "cosmic chimaera": "คอสมิกคิเมร่า",
    "hawk man": "ฮอว์กแมน",
    "gargoyle": "การ์กอยล์",
    "gryphon": "กริฟฟอน",
    "war gryphon": "วอร์กริฟฟอน",
    "jamirus": "จามิรัส",

    # 12. Platypunks & Hoods
    "platypunk": "โมมอนจา",
    "splatypunk": "สแปลทิพังก์",
    "Crack-billed platypunk": "โมมอนจาปากน้ำแข็ง",
    "veteran platypunk": "สุดยอดโมมอนจา",
    "hammerhood": "แฮมเมอร์ฮูด",
    "brownie": "บราวนี่",
    "dark brownie": "ดาร์กบราวนี่",
    "hoodlum": "ฮูดลัม",
    "hood": "จอมโจรมีฮู้ด",
    "heavy hood": "เฮฟวี่ฮูด",
    "veteran hood": "สุดยอดจอมโจรมีฮู้ด",
    "bodkin archer": "บ็อดกินอาร์เชอร์",
    "bodkin bowyer": "บ็อดกินโบว์เยอร์",
    "bodkin fletcher": "บ็อดกินเฟลตเชอร์",
    "bodkin bloodbow": "บ็อดกินบลัดโบว์",
    "tomb bowyer": "พลธนูสุสาน",
    "Robbin' 'Ood": "คานดาทะ",
    "Merry Man": "สมุนโจร",

    # 13. Chests & Bags
    "cannibox": "หีบกินคน",
    "mimic": "มิมิก",
    "Pandora's box": "กล่องแพนโดร่า",
    "goodybag": "ถุงสมบัติ",
    "bag o' laughs": "ถุงหัวเราะ",

    # 14. Elementals, Ghosts & Spirits
    "rockbomb": "ร็อคบอมบ์",
    "bomboulder": "บอมโบลเดอร์",
    "grinade": "กรีเนด",
    "obstrocktion": "ออบสตร็อคชัน",
    "ghost": "ผีโกสต์",
    "spitegeist": "สไปท์ไกสต์",
    "fightgeist": "ไฟต์ไกสต์",
    "lost soul": "วิญญาณหลงทาง",
    "tortured soul": "วิญญาณทุกข์ทรมาน",
    "shade": "เฉด",
    "shadow": "แชโดว์",
    "silhouette": "ซิลูเอท",
    "dancing flame": "เปลวเพลิงเริงระบำ",
    "firespirit": "จิตวิญญาณแห่งไฟ",
    "frostburn": "ฟรอสต์เบิร์น",
    "freezing fog": "สายหมอกเยือกแข็ง",
    "cumaulus": "คิวมูลัส",
    "cloud surfer": "ผู้ท่องเมฆา",
    "muddy hand": "มือโคลน",
    "bloody hand": "มือโลหิต",
    "man o' war": "แมงกะพรุนพิษ",
    "mud mannequin": "หุ่นโคลน",
    "multicolour mannequin": "หุ่นหลากสี",
    "magic marionette": "หุ่นเชิดมนตรา",

    # 15. Sanguini
    "teeny sanguini": "ทีนี่แซงกวินี่",
    "pink sanguini": "พิงค์แซงกวินี่",
    "genie sanguini": "จีนี่แซงกวินี่",

    # 16. Plants
    "treeface": "หน้าต้นไม้",
    "treevil": "ต้นไม้ปีศาจ",
    "antiquitree": "พฤกษาโบราณ",
    "mandrake major": "แมนเดรกเมเจอร์",
    "mandrake marauder": "แมนเดรกมารอเดอร์",
    "mandrake marshal": "แมนเดรกมาร์แชล",

    # 17. Snow & Furry
    "powie yowie": "โพวี่โยวี่",
    "sasquash": "ซาสควอช",
    "sweaty yeti": "สเว็ตตี้เยติ",

    # 18. Magic users
    "magus": "เมกัส",
    "sorcerer": "ซอร์เซอเรอร์",
    "shaman": "ชาแมน",
    "hellcaster": "เฮลคาสเตอร์",

    # 19. Bosses & Special Gatekeepers
    "mawkeeper": "ผู้พิทักษ์ประตูมิติ",
    "float-o-copier": "เครื่องจำลองลอยฟ้า",
    "sand sniper": "สไนเปอร์ทะเลทราย",
    "tomb terror": "ความสะพรึงแห่งสุสาน",
    "tombinator": "ทอมบิเนเตอร์",
    "glade invader": "ผู้รุกรานพงไพร",
    "dungeon master": "ผู้คุมดันเจียน",
    "Balzack": "บัลแซค",
    "Big Bad Balzack": "จอมมารบัลแซค",
    "Dhuran": "ดูรัน",
    "Marquis de Léon": "มาร์ควิส เดอ เลออน",
    "Lionidas": "ไลโอนิดาส",
    "Lord Lionidas": "ลอร์ดไลโอนิดาส",
    "Field Marshal Donk": "จอมพล ดองค์",
    "Abominable Showman": "นักแสดงสุดสะพรึง",
    "Absolutely Abominable Showman": "ยอดนักแสดงสุดสะพรึง",
    "Fractos": "ฟรักทอส",
    "Fractos Unfettered": "ฟรักทอส ร่างปลดปล่อย",
    "Full-On Fractos": "ฟรักทอส ร่างแท้จริง",
    "Full-On Fractos Unfettered": "ฟรักทอส ร่างแท้จริงปลดปล่อย",
    "Estark": "เอสทาร์ก",
    "Estark Extreme": "เอสทาร์ก เอ็กซ์ตรีม",
    "Dragonlord": "ราชามังกร",
    "Dread Dragonlord": "ราชามังกรผู้น่าสะพรึง",
    "Devastating Dragonlord": "ราชามังกรผู้ทำลายล้าง",
    "Whameses": "วาเมเซส",
    "bullion": "บูลเลียน",

    # 20. Party Shadow Bosses & Allies
    "Lazarel": "ราเซล",
    "Teresa": "เทเรเซีย",
    "Cesar": "ซีซาร์",
    "mysterious swordsman": "นักดาบลึกลับ",
    "mysterious martial artist": "นักสู้ลึกลับ",
    "Maya": "มาเนีย",
    "Sinister Cesar": "ซีซาร์แห่งความมืด",
    "Demonic Desdemona": "เดสเดโมน่าปีศาจ",
    "Evil Alena": "อาลีน่าปีศาจ",
    "Cruel Kiryl": "คริฟต์ใจร้าย",
    "Malign Maya": "มาเนียปีศาจ",
    "Malicious Meena": "มีเนียปีศาจ",
    "Tainted Torneko": "ทอร์เนโก้ต้องมนตร์",
    "Tainted Terry": "เทอร์รี่ต้องมนตร์",
    "Callous Carver": "ฮัสซันไร้ปรานี",
    "Malevolent Maribel": "มาริเบลใจร้าย",
    "Gruff Ruff": "กาโบผู้ดุร้าย",
    "Jaundiced Jessica": "เจสสิก้าผู้เคียดแค้น",
    "Unpleasant Angelo": "คูเคิลผู้ร้ายกาจ",
    "Hard-Hearted Healix": "โฮมิรอนใจหิน",
    "Dunisian soldier": "ทหารดูนีเซีย",
    "Ingenian soldier": "ทหารอินเกเนีย",
    "Ingenian royal guard": "องครักษ์หลวงอินเกเนีย",
    "Kadavan commander": "ผู้บัญชาการคาดาวา",
    "King of Accordia": "กษัตริย์แห่งออร์คาเนีย",
    "Queen of Ingenia": "ราชินีแห่งอินเกเนีย",
    "King of Kadava": "กษัตริย์แห่งคาดาวา",
    "King of Klor": "กษัตริย์แห่งคลอร์",
    "King of Al-Khazam": "กษัตริย์แห่งอัลคาซัม",
    "Cranked-Up King of Kadava": "กษัตริย์คาดาวาคลุ้มคลั่ง",
    "Cranked-Up King of Klor": "กษัตริย์คลอร์คลุ้มคลั่ง",
    "Cranked-Up King of Al-Khazam": "กษัตริย์อัลคาซัมคลุ้มคลั่ง",
    "Cranked-Up King of Accordia": "กษัตริย์ออร์คาเนียคลุ้มคลั่ง",
}

def translate_monsters_file():
    target_csv = "text_csv/categories/entry_00015_Monsters.csv"
    with open(target_csv, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    updated = 0
    # Process in chunks of 8
    for i in range(0, len(reader), 8):
        chunk = reader[i:i+8]
        disp_name = chunk[1]["OriginalEnglish"].strip() if len(chunk) > 1 else ""
        
        if not disp_name:
            continue
            
        thai_name = MONSTER_MAP.get(disp_name)
        if not thai_name:
            print(f"[!] Warning: No translation for '{disp_name}' at slot {i//8}")
            continue

        # Offset 0: singular lowercase
        chunk[0]["ThaiTranslation"] = thai_name
        # Offset 1: display name
        chunk[1]["ThaiTranslation"] = thai_name
        # Offset 2: empty
        chunk[2]["ThaiTranslation"] = ""
        # Offset 3: plural
        chunk[3]["ThaiTranslation"] = thai_name
        # Offsets 4, 5, 6, 7: English grammatical articles (the, a, some)
        # In Thai, articles do not exist, so we keep ThaiTranslation as empty string ""
        for off in range(4, 8):
            if off < len(chunk):
                chunk[off]["ThaiTranslation"] = ""

        updated += 1

    with open(target_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

    print(f"[SUCCESS] Updated {updated} monster slots in {target_csv}!")

if __name__ == "__main__":
    translate_monsters_file()
