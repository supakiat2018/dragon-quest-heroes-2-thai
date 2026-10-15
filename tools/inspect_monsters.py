import json

with open('tools/monsters_list.json', encoding='utf-8') as f:
    monsters = json.load(f)

with open('tools/all_monsters.txt', 'w', encoding='utf-8') as out:
    for k, v in monsters.items():
        if v['disp']:
            out.write(f"{int(k):3d} | {v['sing']:30s} | {v['disp']:30s} | {v['plur']}\n")
        else:
            out.write(f"{int(k):3d} | (EMPTY)\n")

print("Dumped to tools/all_monsters.txt")
