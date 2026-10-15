# -*- coding: utf-8 -*-
"""
translate_entry_00253.py
Translates entry_00253_Monster_Medals.csv
"""

import csv
import re

MEDALS_MAP = {
    "sand sniper": "สไนเปอร์ทะเลทราย",
    "Sand Sniper": "สไนเปอร์ทะเลทราย",
    "sand snipers": "สไนเปอร์ทะเลทราย",
    "Badly Behaved Bodkin": "บ็อดกินจอมเกเร",
    "badly behaved bodkin": "บ็อดกินจอมเกเร",
    "badly behaved bodkins": "บ็อดกินจอมเกเร",
    "Barrier Guardian": "ผู้พิทักษ์ม่านพลัง",
    "barrier guardian": "ผู้พิทักษ์ม่านพลัง",
    "barrier guardians": "ผู้พิทักษ์ม่านพลัง",
    "Bodkin Fletcher": "บ็อดกินเฟลตเชอร์",
    "bodkin fletcher": "บ็อดกินเฟลตเชอร์",
    "bodkin fletchers": "บ็อดกินเฟลตเชอร์",
    "Cranked-Up Kings of Accordia": "กษัตริย์แห่งออร์คาเนียคลุ้มคลั่ง",
    "cranked-up Kings of Accordia": "กษัตริย์แห่งออร์คาเนียคลุ้มคลั่ง",
    "Dungeon Masher": "จอมทุบดันเจียน",
    "dungeon masher": "จอมทุบดันเจียน",
    "dungeon mashers": "จอมทุบดันเจียน",
    "Dungeon Master": "ผู้คุมดันเจียน",
    "dungeon master": "ผู้คุมดันเจียน",
    "dungeon masters": "ผู้คุมดันเจียน",
    "Dynamic Duo": "คู่หูพลังเทอร์โบ",
    "Dynamic Duos": "คู่หูพลังเทอร์โบ",
    "Field Marshal Donk": "จอมพล ดองค์",
    "Field Marshal Donks": "จอมพล ดองค์",
    "Glade Invader": "ผู้รุกรานพงไพร",
    "glade invader": "ผู้รุกรานพงไพร",
    "glade invaders": "ผู้รุกรานพงไพร",
    "Hacksaurus": "แฮ็กซอรัส",
    "hacksaurus": "แฮ็กซอรัส",
    "hacksauruses": "แฮ็กซอรัส",
    "Imp": "อิมป์",
    "imp": "อิมป์",
    "imps": "อิมป์",
    "Impish Imp": "อิมป์จอมซน",
    "impish imp": "อิมป์จอมซน",
    "impish imps": "อิมป์จอมซน",
    "Kadavan Commander": "ผู้บัญชาการคาดาวา",
    "Kadavan commander": "ผู้บัญชาการคาดาวา",
    "Kadavan commanders": "ผู้บัญชาการคาดาวา",
    "King of Al-Khazam": "กษัตริย์แห่งอัลคาซัม",
    "Kings of Al-Khazam": "กษัตริย์แห่งอัลคาซัม",
    "King of Harba": "กษัตริย์แห่งฮาร์บา",
    "Kings of Harba": "กษัตริย์แห่งฮาร์บา",
    "Kings of Accordia": "กษัตริย์แห่งออร์คาเนีย",
    "Major Arcana": "อาร์คานาผู้ยิ่งใหญ่",
    "Major Arcanas": "อาร์คานาผู้ยิ่งใหญ่",
    "Major Domo": "พ่อบ้านเมเจอร์โดโม",
    "Major Domos": "พ่อบ้านเมเจอร์โดโม",
    "Merry Master-Thief": "จอมโจรผู้เริงร่า",
    "merry master-thief": "จอมโจรผู้เริงร่า",
    "merry master-thieves": "จอมโจรผู้เริงร่า",
    "Merry Minnow": "ปลาซิวผู้เริงร่า",
    "merry minnow": "ปลาซิวผู้เริงร่า",
    "merry minnows": "ปลาซิวผู้เริงร่า",
    "Merry Mobster": "นักเลงผู้เริงร่า",
    "merry mobster": "นักเลงผู้เริงร่า",
    "merry mobsters": "นักเลงผู้เริงร่า",
    "Merry Mugger": "จอมจี้ชิงทรัพย์ผู้เริงร่า",
    "merry mugger": "จอมจี้ชิงทรัพย์ผู้เริงร่า",
    "merry muggers": "จอมจี้ชิงทรัพย์ผู้เริงร่า",
    "Messenger": "ผู้ส่งสาร",
    "messenger": "ผู้ส่งสาร",
    "messengers": "ผู้ส่งสาร",
    "Mischievous Magus": "เมกัสจอมซน",
    "mischievous magus": "เมกัสจอมซน",
    "mischievous magi": "เมกัสจอมซน",
    "Moustachioed Merchant": "พ่อค้าไว้หนวด",
    "moustachioed merchant": "พ่อค้าไว้หนวด",
    "moustachioed merchants": "พ่อค้าไว้หนวด",
    "Queen of Ingenia": "ราชินีแห่งอินเกเนีย",
    "Queens of Ingenia": "ราชินีแห่งอินเกเนีย",
    "Roguish Ruffian": "อันธพาลจอมกวน",
    "roguish ruffian": "อันธพาลจอมกวน",
    "roguish ruffians": "อันธพาลจอมกวน",
    "Runaway Rogue": "จอมโจรหลบหนี",
    "runaway rogue": "จอมโจรหลบหนี",
    "runaway rogues": "จอมโจรหลบหนี",
    "Samson Knight": "อัศวินแซมสัน",
    "Samson Knights": "อัศวินแซมสัน",
    "Slime": "สไลม์",
    "slime": "สไลม์",
    "slimes": "สไลม์",
    "Watchman o' War": "แมงกะพรุนยามศึก",
    "watchman o' war": "แมงกะพรุนยามศึก",
    "watchmen o' war": "แมงกะพรุนยามศึก",
    "NOT USED": "ไม่ได้ใช้งาน",
}

def get_thai_medal(eng):
    eng = eng.strip()
    if not eng:
        return ""
    if eng in ["the", "a", "an", "some"]:
        return ""
        
    if eng in MEDALS_MAP:
        return MEDALS_MAP[eng]
        
    # Check Hood A..L
    m = re.match(r"^Hood ([A-Z])s?$", eng)
    if m:
        letter = m.group(1)
        return f"จอมโจรมีฮู้ด {letter}"
        
    # Check Harban Soldier A..E
    m = re.match(r"^Harban Soldier ([A-Z])s?$", eng)
    if m:
        letter = m.group(1)
        return f"ทหารฮาร์บา {letter}"

    # Check Dungeon Master A..H
    m = re.match(r"^Dungeon Master ([A-Z])s?$", eng)
    if m:
        letter = m.group(1)
        return f"ผู้คุมดันเจียน {letter}"

    # Check Tombinator A..B
    m = re.match(r"^Tombinator ([A-Z])s?$", eng)
    if m:
        letter = m.group(1)
        return f"ทอมบิเนเตอร์ {letter}"

    return eng

def translate_253():
    target_csv = "text_csv/categories/entry_00253_Monster_Medals.csv"
    with open(target_csv, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    updated = 0
    for r in reader:
        eng = r["OriginalEnglish"].strip()
        if not eng:
            continue
        th = get_thai_medal(eng)
        r["ThaiTranslation"] = th
        updated += 1

    with open(target_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reader)

    print(f"[SUCCESS] Updated {updated} lines in {target_csv}!")

if __name__ == "__main__":
    translate_253()
