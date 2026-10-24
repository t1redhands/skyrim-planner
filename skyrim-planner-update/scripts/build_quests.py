#!/usr/bin/env python3
"""Rebuild data/quests.json from the quest pages saved by `uesp_ingest.py --quests`.

    python3 scripts/build_quests.py            # data/source/quests.json -> data/quests.json
    python3 scripts/build_quests.py IN OUT     # other paths
"""
import json, re, sys, time
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 2 else ROOT / 'data' / 'source' / 'quests.json'
DEST = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'data' / 'quests.json'
P = json.load(open(SRC, encoding='utf-8'))['pages']
LINES = [  # (category suffix, questline label, dlc)
 ('Dawnguard-Quests-Volkihar Vampire Clan','Volkihar Vampire Clan','dawnguard'),('Dawnguard-Quests-Dawnguard','Dawnguard','dawnguard'),
 ('Dawnguard-Quests-Main Quest','Dawnguard main quest','dawnguard'),('Dawnguard-Quests-Side Quests','Dawnguard side quest','dawnguard'),
 ('Dragonborn-Quests-Side Quests','Dragonborn side quest','dragonborn'),('Hearthfire-Quests','Hearthfire','hearthfire'),
 ('Quests-Main Quest','Main quest','base'),('Quests-Companions','Companions','base'),('Quests-College of Winterhold','College of Winterhold','base'),
 ('Quests-Thieves Guild','Thieves Guild','base'),('Quests-Dark Brotherhood','Dark Brotherhood','base'),('Quests-Imperial Legion','Imperial Legion','base'),
 ('Quests-Stormcloaks','Stormcloaks','base'),('Quests-Daedric','Daedric quest','base'),('Quests-Divine','Divine quest','base'),
 ('Quests-Bards College','Bards College','base'),('Quests-Dungeon Quests','Dungeon quest','base'),('Quests-Side Quests','Side quest','base'),
 ('Dawnguard-Quests-Miscellaneous','Dawnguard side task','dawnguard'),('Dragonborn-Quests-Miscellaneous','Dragonborn side task','dragonborn'),
 ('Creation Club-Quests','Creation Club','cc'),('Dragonborn-Quests','Dragonborn main quest','dragonborn'),('Dawnguard-Quests','Dawnguard add-on','dawnguard')]
# Dawnguard main quest steps that only exist on one side of the vampire war
SIDE = {'A New Order': 'dawnguard', 'Prophet (Dawnguard)': 'dawnguard', 'The Bloodstone Chalice': 'volkihar', 'Prophet (Vampire)': 'volkihar'}
MINOR = ('Radiant','Miscellaneous','Non-Journal','Favors','Bounty','Tutorials','Thane','World Interactions')
def field(h, k):
    m = re.search(r'^\|\s*' + k + r'\s*=(.*?)(?=^\||^\}\})', h, re.S | re.M | re.I)
    return m.group(1).strip() if m else ''
def links(s): return [x for x in (re.sub(r'#.*$', '', l).split(':', 1)[-1].replace('_', ' ').strip() for l in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', s)) if x]
def plain(s):
    s = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', s); s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    s = re.sub(r'<br\s*/?>', '; ', s); s = re.sub(r'<[^>]+>', '', s); s = re.sub(r"'{2,}", '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*[,;]\s*(?=[,;])', '', s)          # ",;" or "; ;" -> one separator
    s = re.sub(r'\s*;\s*', '; ', s); s = re.sub(r'\s*,\s*', ', ', s)
    return s.strip(' ;,')
def qname(t): return re.sub(r'\s*\(quest\)$', '', t.split(':', 1)[-1])
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower().replace("'", "")).strip('-')
out, skipped = [], Counter()
for title, p in P.items():
    w = p['wikitext']; m = re.search(r'\{\{Quest Header(.*?)^\}\}', w, re.S | re.M)
    if not m: skipped['no header'] += 1; continue
    cats = p['categories']
    line = next(((lab, dlc) for suf, lab, dlc in LINES if any(c.endswith(suf) for c in cats)), None)
    minor = any(any(x in c for x in MINOR) for c in cats) and not line
    if not line: line = ('Miscellaneous' if minor else 'Other', 'dragonborn' if any('Dragonborn' in c for c in cats) else 'dawnguard' if any('Dawnguard' in c for c in cats) else 'base')
    if any(x in ' '.join(cats) for x in ('Radiant', 'Non-Journal')) and line[0] in ('Miscellaneous','Other'): skipped['radiant/non-journal'] += 1; continue
    h = m.group(0) + '\n'
    lv = lambda k: int(re.search(r'\d+', field(h, k)).group()) if re.search(r'\d+', field(h, k)) else None
    rew = field(h, 'Reward')
    q = {"id": slug(qname(title)), "name": qname(title), "page": title, "line": line[0], "dlc": line[1],
         "giver": plain(field(h, 'Giver'))[:160], "description": plain(field(h, 'description'))[:220],
         "reward": plain(rew)[:300], "rewardLinks": sorted(set(links(rew))),
         "prev": [n for n in (qname(l) for l in links(field(h, 'Prev'))) if n], "prevAny": ' or ' in field(h, 'Prev'),
         "next": [n for n in (qname(l) for l in links(field(h, 'Next'))) if n], "loc": plain(field(h, 'Loc'))[:160]}
    if q['name'] in SIDE: q['side'] = SIDE[q['name']]
    if lv('ReqLevel'): q['reqLevel'] = lv('ReqLevel')
    if lv('SuggLevel'): q['suggLevel'] = lv('SuggLevel')
    if minor or line[0] == 'Miscellaneous': q['minor'] = True
    out.append(q)
ids = Counter(q['id'] for q in out)
for q in out:
    if ids[q['id']] > 1: q['id'] = slug(q['page'])
json.dump({"license": "CC BY-SA 2.5; quest details from UESP (https://en.uesp.net/wiki/Skyrim:Quests), summarized.", "asOf": time.strftime("%Y-%m-%d"), "quests": sorted(out, key=lambda q: (q['line'], q['name']))},
          open(DEST, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print('quests', len(out), 'skipped', dict(skipped)); print(Counter(q['line'] for q in out).most_common(30))
print('with reqLevel', sum('reqLevel' in q for q in out), 'with prev', sum(bool(q['prev']) for q in out))
