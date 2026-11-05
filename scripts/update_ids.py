#!/usr/bin/env python3
"""Keep data/ids.json in step with the data files.

Share links store items by their position in these lists instead of by name, which
keeps links short. The lists only ever grow: new ids are added at the end and old
ones are never removed or reordered, so links made today keep working after the
data is refreshed.

    python3 scripts/update_ids.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


def load(name):
    return json.load(open(DATA / f'{name}.json', encoding='utf-8'))


def current():
    perks = load('perks')
    trees = perks['trees'] if isinstance(perks['trees'], list) else [dict(id=k, **v) for k, v in perks['trees'].items()]
    ranks = []
    for t in trees:
        for p in t['perks']:
            for i in range(len(p['ranks'])):
                ranks.append(f"{p['id']}#{i}")
    gear = load('gear'); alch = load('alchemy'); hh = load('household'); sc = load('scrolls')
    return {
        'perk': ranks,
        'gear': [i['id'] for i in gear['items']],
        'ench': [e['name'] for e in gear.get('enchantments', {}).get('list', [])],
        'shout': [s['id'] for s in load('shouts')['shouts']],
        'spell': [s['id'] for s in load('spells')['spells']],
        'buff': [b['id'] for b in load('buffs')['buffs']],
        'quest': [q['id'] for q in load('quests')['quests']],
        'stone': [s['id'] for s in load('stones')['stones']],
        'effect': [e['id'] for e in alch['effects']],
        'ingredient': [i['id'] for i in alch['ingredients']],
        'recipe': [r['id'] for r in alch['recipes']],
        'scroll': [s['id'] for s in sc['scrolls']],
        'spider': [s['id'] for s in sc['spiders']],
        'follower': [f['id'] for f in hh['followers']],
        'spouse': [s['id'] for s in hh['spouses']],
        'home': [h['id'] for h in hh['homes'] + hh['factionHomes']],
        'pet': [x['id'] for x in hh.get('pets', [])],
        'collection': [c['id'] for c in load('collections')['collections']] if (DATA / 'collections.json').exists() else [],
        'citem': [f"{c['id']}/{it['id']}" for c in load('collections')['collections'] for it in c['items']] if (DATA / 'collections.json').exists() else [],
    }


def main():
    path = DATA / 'ids.json'
    old = json.load(open(path)) if path.exists() else {'note': 'Append-only lists used by share links. Never remove or reorder entries.', 'lists': {}}
    added = 0
    for key, ids in current().items():
        lst = old['lists'].setdefault(key, [])
        have = set(lst)
        for i in dict.fromkeys(ids):
            if i not in have:
                lst.append(i); have.add(i); added += 1
    json.dump(old, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'ids.json: {added} new id(s) added.')


if __name__ == '__main__':
    main()
