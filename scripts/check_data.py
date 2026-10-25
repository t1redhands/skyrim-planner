#!/usr/bin/env python3
"""Compare the UESP pages saved in data/source/ with the planner's data files.

Most of the planner's data (gear, followers, homes, ingredients, enchantments) was
checked and summarized by hand, so it isn't rebuilt automatically. This script
spots what UESP has added since: names listed on a source page that the planner
doesn't have yet. It writes data/source/CHECK_REPORT.md and prints a summary.

Names that were already left out on purpose are kept in
data/source/check_baseline.json, so only new ones are reported.

    python3 scripts/check_data.py              # report new names
    python3 scripts/check_data.py --baseline   # accept everything listed now as known
"""
import json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, SRC = ROOT / 'data', ROOT / 'data' / 'source'
BASELINE = SRC / 'check_baseline.json'

# source page -> which planner names it should be compared with
PAGES = {
    'Skyrim_Unique_Weapons': 'gear', 'Skyrim_Unique_Armor': 'gear', 'Skyrim_Unique_Jewelry': 'gear',
    'Skyrim_Unique_Clothing': 'gear', 'Skyrim_Artifacts': 'gear', 'Skyrim_Leveled_Items': 'gear',
    'Skyrim_Weapons': 'gear', 'Skyrim_Armor': 'gear', 'Skyrim_Clothing': 'gear', 'Skyrim_Jewelry': 'gear',
    'Skyrim_Followers': 'household', 'Skyrim_Marriage': 'household', 'Skyrim_Houses': 'household',
    'Skyrim_Specialty_Gear': 'gear', 'Skyrim_Vigil_Armor': 'gear', 'Skyrim_Amulets_of_the_Divines': 'gear', 'Skyrim_Staves': 'gear',
    'Skyrim_Ingredients': 'alchemy', 'Skyrim_Food': 'alchemy', 'Skyrim_Enchantments': 'enchantments', 'Skyrim_Spells': 'spells',
}

LINK = r'\[\[(?:Skyrim|SR|Dawnguard|Dragonborn|Hearthfire):([^|\]#]+)(?:\|([^\]]+))?\]\]'


def norm(s):
    s = re.sub(r'\{\{[^}]*\}\}|<[^>]+>|\'{2,}', '', s)
    s = re.sub(r'\s*\((?:effect|item|skyrim|quest|ingredient|place|npc|follower|dawnguard|dragonborn|cc|creation club)\)\s*$', '', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s.replace('_', ' ')).strip().lower()
    return re.sub(r'^the ', '', s)


def listed(wiki):
    """Names a page lists: section headings and the first cell of table rows."""
    out = set()
    for line in wiki.split('\n'):
        m = re.match(r'^={3,4}\s*(.*?)\s*={3,4}\s*$', line)
        if m:
            h = m.group(1); lm = re.search(LINK, h)
            out.add(norm(lm.group(2) or lm.group(1)) if lm else norm(h))
            continue
        m = re.match(r'^[|!]\s*(?:[^|\[]*\|)?\s*' + LINK, line)
        if m:
            out.add(norm(m.group(2) or m.group(1)))
    return {n for n in out if n and len(n) < 60}


def known():
    k = {'gear': set(), 'household': set(), 'alchemy': set(), 'enchantments': set(), 'spells': set()}
    sp = DATA / 'spells.json'
    if sp.exists(): k['spells'] = {norm(s['name']) for s in json.load(open(sp, encoding='utf-8'))['spells']}
    gear = json.load(open(DATA / 'gear.json', encoding='utf-8'))
    k['gear'] = {norm(i['name']) for i in gear['items']}
    k['enchantments'] = {norm(e['name']) for e in gear.get('enchantments', {}).get('list', [])}
    hh = json.load(open(DATA / 'household.json', encoding='utf-8'))
    for key, val in hh.items():
        if isinstance(val, list):
            k['household'] |= {norm(x['name']) for x in val if isinstance(x, dict) and 'name' in x}
        elif isinstance(val, dict):
            for sub in val.values():
                if isinstance(sub, list):
                    k['household'] |= {norm(x['name']) for x in sub if isinstance(x, dict) and 'name' in x}
    al = json.load(open(DATA / 'alchemy.json', encoding='utf-8'))
    for key in ('ingredients', 'recipes', 'effects'):
        k['alchemy'] |= {norm(x['name']) for x in al.get(key, []) if 'name' in x}
    return k


def main():
    have, found, missing_pages = known(), {}, []
    for page, kind in PAGES.items():
        f = SRC / f'{page}.wiki'
        if not f.exists():
            missing_pages.append(page); continue
        names = listed(f.read_text(encoding='utf-8'))
        found[page] = sorted(n for n in names if n not in have[kind])
    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    if '--baseline' in sys.argv:
        BASELINE.write_text(json.dumps(found, indent=1, ensure_ascii=False))
        print(f'Baseline saved: {sum(map(len, found.values()))} names marked as known.')
        return 0
    new = {p: [n for n in names if n not in set(base.get(p, []))] for p, names in found.items()}
    new = {p: n for p, n in new.items() if n}
    lines = [f'# Data check, {time.strftime("%Y-%m-%d")}', '']
    if new:
        lines += ['UESP lists these names that the planner doesn\'t have yet. Some may be new to the game or newly documented; '
                  'others may be things the planner leaves out on purpose. Ask Claude to review them, or run '
                  '`python3 scripts/check_data.py --baseline` to mark them all as known.', '']
        for p, names in new.items():
            lines += [f'## {p.replace("_", " ").replace("Skyrim ", "Skyrim:")}', ''] + [f'- {n}' for n in names] + ['']
    else:
        lines += ['Nothing new: every name on the source pages is in the planner or was already reviewed.', '']
    if missing_pages:
        lines += ['Source pages not saved yet (run `uesp_ingest.py --dump`): ' + ', '.join(missing_pages), '']
    (SRC / 'CHECK_REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    total = sum(map(len, new.values()))
    print(f'Data check: {total} new name(s) on UESP' + (' (see data/source/CHECK_REPORT.md)' if total else '') + '.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
