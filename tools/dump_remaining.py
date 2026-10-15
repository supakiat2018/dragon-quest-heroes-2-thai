import json
import sys

with open('tools/skills_list.json', encoding='utf-8') as f:
    skills = json.load(f)

start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 133
end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 270

for i, x in enumerate(skills[start_idx:end_idx], start=start_idx):
    print(f"[{i}] slot:{x['slot']:3d} | {x['name']:30s} | {x['desc']}")
