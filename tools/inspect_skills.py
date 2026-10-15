import json
import sys

with open('tools/skills_list.json', encoding='utf-8') as f:
    skills = json.load(f)

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 30

for x in skills[start:start+count]:
    print(f"[{x['slot']:3d}] {x['name']:25s} | {x['desc']}")
