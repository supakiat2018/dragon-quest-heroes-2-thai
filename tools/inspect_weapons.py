import json
import sys

with open('tools/weapons_list.json', encoding='utf-8') as f:
    weapons = json.load(f)

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 30

for x in weapons[start:start+count]:
    print(f"[{x['slot']:3d}] {x['name']:25s} | {x['desc']}")
