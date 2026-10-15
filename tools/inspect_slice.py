import sys
import json

file_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].isdigit() else 'tools/dlc_p1a.json'
start = int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0)
end = int(sys.argv[3]) if len(sys.argv) > 3 else (start + 60)

data = json.load(open(file_path, encoding='utf-8'))
for i in range(start, min(end, len(data))):
    item = data[i]
    print(f"{i} [{item['StringIndex']}]: {item['OriginalEnglish']}")
