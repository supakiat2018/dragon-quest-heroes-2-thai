import csv
import re
import glob

def clean_thai_text(text):
    if not text:
        return text
        
    cleaned = text
    
    # 1. Remove English phrases in parentheses e.g. (Bracing Bough), (Knight Aberrant), (Full Screen)
    # But do NOT touch tags like <FH>, <FG>, etc.
    cleaned = re.sub(r'\s*\([A-Za-z0-9\s\-\.\'\’\/]+\)', '', cleaned)
    
    # Clean any internal double spaces left from removed parentheses (preserve leading indentation)
    cleaned = re.sub(r'(?<=\S)  +', ' ', cleaned)
    
    # 2. Convert Thai written numbers to Arabic numerals 1234567890
    number_replacements = [
        ('หนึ่งเหรียญทอง', '1 เหรียญทอง'),
        ('หนึ่งเหรียญ', '1 เหรียญ'),
        ('หนึ่งคน', '1 คน'),
        ('สองคน', '2 คน'),
        ('สามคน', '3 คน'),
        ('สี่คน', '4 คน'),
        ('ทั้งสองคน', 'ทั้ง 2 คน'),
        ('ทั้งสองฝ่าย', 'ทั้ง 2 ฝ่าย'),
        ('ทั้งสองข้าง', 'ทั้ง 2 ข้าง'),
        ('ทั้งสอง', 'ทั้ง 2'),
        ('หนึ่งลูก', '1 ลูก'),
        ('หนึ่งดอก', '1 ดอก'),
        ('หนึ่งอัน', '1 อัน'),
        ('หนึ่งชิ้น', '1 ชิ้น'),
        ('หนึ่งข้อเสนอ', '1 ข้อเสนอ'),
        ('หนึ่งข้อ', '1 ข้อ'),
        ('หนึ่งช่อง', '1 ช่อง'),
        ('หนึ่งใบ', '1 ใบ'),
        ('เป็นสองเท่า', 'เป็น 2 เท่า'),
        ('สองเท่า', '2 เท่า'),
        ('สามเท่า', '3 เท่า'),
        ('สักสองสามที', 'สัก 2-3 ครั้ง'),
        ('สองสามที', '2-3 ครั้ง'),
        ('ทั้งสี่บาน', 'ทั้ง 4 บาน'),
        ('สี่บาน', '4 บาน'),
        ('สี่ทิศ', '4 ทิศ'),
    ]
    for old, new in number_replacements:
        cleaned = cleaned.replace(old, new)
        
    # 3. Ensure clean spacing between Thai letters and Arabic digits
    cleaned = re.sub(r'([\u0E00-\u0E7F])(\d+)', r'\1 \2', cleaned)
    cleaned = re.sub(r'(\d+)([\u0E00-\u0E7F])', r'\1 \2', cleaned)
    # Remove any unintended double spaces created
    cleaned = re.sub(r'(?<=\S)  +', ' ', cleaned)
        
    return cleaned

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys() if reader else []
        
    changes = 0
    updated_rows = []
    for row in reader:
        orig = row.get('ThaiTranslation', '')
        new_val = clean_thai_text(orig)
        if orig != new_val:
            changes += 1
            row['ThaiTranslation'] = new_val
        updated_rows.append(row)
        
    if changes > 0:
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        print(f"Updated {file_path}: {changes} lines modified.")
    else:
        print(f"No changes needed for {file_path}.")
    return changes

def sync_master_csv():
    category_files = glob.glob('text_csv/categories/entry_*.csv')
    translation_map = {} # (EntryID, StringIndex) -> ThaiTranslation
    for cfile in category_files:
        with open(cfile, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                eid = row['EntryID']
                sidx = row['StringIndex']
                th = row.get('ThaiTranslation', '')
                if th.strip():
                    translation_map[(eid, sidx)] = th
                    
    master_file = 'text_csv/dqh2_all_english_text.csv'
    with open(master_file, 'r', encoding='utf-8-sig') as f:
        master_rows = list(csv.DictReader(f))
        fieldnames = master_rows[0].keys()
        
    synced = 0
    for row in master_rows:
        key = (row['EntryID'], row['StringIndex'])
        if key in translation_map:
            if row['ThaiTranslation'] != translation_map[key]:
                row['ThaiTranslation'] = translation_map[key]
                synced += 1
                
    with open(master_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(master_rows)
        
    print(f"Master CSV synced: {synced} lines updated with new translations.")

if __name__ == '__main__':
    targets = sorted(glob.glob('text_csv/categories/entry_*.csv'))
    total_mod = 0
    for t in targets:
        total_mod += process_file(t)
    print(f"Total lines modified across category files: {total_mod}")
    sync_master_csv()

