#!/usr/bin/env python3
"""
Skyrim Character Planner - UESP ingest, Phase 1 starter.

Pulls race pages from UESP through the MediaWiki API, caches the raw
wikitext, extracts each race's starting skill bonuses, writes
data/races.json (with source URLs for attribution), and checks the
results against the values hand-entered in the planner.

Run on your own machine:
    pip install requests mwparserfromhell
    python uesp_ingest.py            # fetch (or reuse cache) and check
    python uesp_ingest.py --refresh  # ignore the cache and refetch

UESP text is CC BY-SA 2.5. Keep the source URLs this script records and
credit UESP wherever the data appears.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import mwparserfromhell
import requests

API = "https://en.uesp.net/w/api.php"   # confirm the endpoint if requests fail
WIKI = "https://en.uesp.net/wiki/"
USER_AGENT = "SkyrimCharacterPlanner/0.1 (private fan tool; contact: you@example.com)"  # put your email here
DELAY_SECONDS = 3      # be gentle: UESP is volunteer-run and blocks aggressive bots
OUT = Path("data")
RAW = OUT / "raw"

RACE_PAGES = {
    "argonian": "Skyrim:Argonian", "breton": "Skyrim:Breton", "darkElf": "Skyrim:Dark Elf",
    "highElf": "Skyrim:High Elf", "imperial": "Skyrim:Imperial", "khajiit": "Skyrim:Khajiit",
    "nord": "Skyrim:Nord", "orc": "Skyrim:Orc", "redguard": "Skyrim:Redguard", "woodElf": "Skyrim:Wood Elf",
}

SKILL_IDS = {
    "one-handed": "oneHanded", "two-handed": "twoHanded", "archery": "archery", "marksman": "archery",
    "block": "block", "heavy armor": "heavyArmor", "smithing": "smithing", "alteration": "alteration",
    "conjuration": "conjuration", "destruction": "destruction", "illusion": "illusion",
    "restoration": "restoration", "enchanting": "enchanting", "light armor": "lightArmor",
    "sneak": "sneak", "lockpicking": "lockpicking", "pickpocket": "pickpocket", "speech": "speech",
    "alchemy": "alchemy",
}

# Values currently hand-entered in the planner (keep in sync with the page's RACES table)
PLANNER = {
    "argonian": ("lockpicking", ["alteration", "lightArmor", "pickpocket", "restoration", "sneak"]),
    "breton": ("conjuration", ["alchemy", "alteration", "illusion", "restoration", "speech"]),
    "darkElf": ("destruction", ["alchemy", "alteration", "illusion", "lightArmor", "sneak"]),
    "highElf": ("illusion", ["alteration", "conjuration", "destruction", "enchanting", "restoration"]),
    "imperial": ("restoration", ["block", "destruction", "enchanting", "heavyArmor", "oneHanded"]),
    "khajiit": ("sneak", ["alchemy", "archery", "lockpicking", "oneHanded", "pickpocket"]),
    "nord": ("twoHanded", ["block", "lightArmor", "oneHanded", "smithing", "speech"]),
    "orc": ("heavyArmor", ["block", "enchanting", "oneHanded", "smithing", "twoHanded"]),
    "redguard": ("oneHanded", ["alteration", "archery", "block", "destruction", "smithing"]),
    "woodElf": ("archery", ["alchemy", "lightArmor", "lockpicking", "pickpocket", "sneak"]),
}


def fetch_wikitext(session, title, refresh):
    cache = RAW / (title.replace(":", "_").replace(" ", "_") + ".wiki")
    if cache.exists() and not refresh:
        return cache.read_text(encoding="utf-8")
    resp = session.get(API, params={
        "action": "parse", "page": title, "prop": "wikitext", "format": "json", "formatversion": 2,
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"{title}: {data['error'].get('info')}")
    text = data["parse"]["wikitext"]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text, encoding="utf-8")
    time.sleep(DELAY_SECONDS)
    return text


def skill_ids(fragment):
    found = []
    for name in re.split(r",|\band\b", fragment.lower()):
        key = name.strip(" .*'")
        if key in SKILL_IDS:
            found.append(SKILL_IDS[key])
    return found


def parse_race(wikitext):
    """Find '+10 Skill' and '+5 A, B, C, D, E' lines in the race page's Skills section."""
    plain = mwparserfromhell.parse(wikitext).strip_code()

    def first_with_skills(pattern):
        # pages also mention things like "+10 Warmth", so take the first match that names skills
        for m in re.finditer(pattern, plain):
            ids = skill_ids(m.group(1))
            if ids:
                return ids
        return []

    return {
        "p10": first_with_skills(r"\+\s*10\s+([A-Za-z\- ]+)")[:1],
        "p5": first_with_skills(r"\+\s*5\s+([A-Za-z\-, ]+)"),
    }


def flatten(wikitext):
    """Wiki markup to plain-ish text, keeping template contents (perk tables often live in templates)."""
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", wikitext)   # [[Page|Text]] -> Text
    t = re.sub(r"'{2,}", "", t)                                       # bold / italic quotes
    t = re.sub(r"<[^>]+>", " ", t)                                    # html tags
    return re.sub(r"\s+", " ", t)


def perk_section(wikitext):
    code = mwparserfromhell.parse(wikitext)
    secs = code.get_sections(matches=r"Perks", flat=False)
    return str(secs[0]) if secs else wikitext


def check_perks(session, refresh, only_unverified=True):
    """Compare data/perks.json with each skill's UESP page. Writes data/raw/perk-check.txt."""
    perks_file = OUT / "perks.json"
    data = json.loads(perks_file.read_text(encoding="utf-8"))
    report, problems, checked = [], [], 0
    for skill, tree in data["trees"].items():
        if only_unverified and tree.get("verified"):
            continue
        title = "Skyrim:" + tree["source"].rsplit("Skyrim:", 1)[1].replace("_", " ")
        try:
            raw = perk_section(fetch_wikitext(session, title, refresh))
        except Exception as exc:
            problems.append(f"{skill}: fetch failed ({exc})")
            continue
        text = flatten(raw)
        low = text.lower()
        names = [p["name"] for p in tree["perks"]]
        # where each perk's own row starts: first mention of its name
        starts = sorted((low.find(n.lower()), n) for n in names if low.find(n.lower()) >= 0)
        tree_problems = []
        for p in tree["perks"]:
            pos = low.find(p["name"].lower())
            if pos < 0:
                tree_problems.append(f"'{p['name']}' not found on the page")
                continue
            later = [s for s, _ in starts if s > pos]
            window = text[pos: later[0] if later else pos + 800]
            for req in p["ranks"]:
                if req and not re.search(rf"(?<!\d){req}(?!\d)", window):
                    tree_problems.append(f"{p['name']}: requirement {req} not seen near the perk")
            for pre in p["prereq"]:
                pre_name = next(x["name"] for x in tree["perks"] if x["id"] == pre)
                if pre_name.lower() not in low:
                    tree_problems.append(f"{p['name']}: prerequisite '{pre_name}' not found on the page")
        checked += 1
        status = "OK" if not tree_problems else f"{len(tree_problems)} to review"
        print(f"{'OK ' if not tree_problems else '?? '} {skill} ({status})")
        problems += [f"{skill}: {x}" for x in tree_problems]
        report.append(f"===== {skill} ({title}) =====\n{status}\n" + "\n".join(tree_problems) + f"\n--- page text ---\n{text[:6000]}\n")
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "perk-check.txt").write_text("\n".join(report), encoding="utf-8")
    print(f"\nChecked {checked} trees. Full report: {RAW / 'perk-check.txt'}")
    if problems:
        print("\nNeeds a look (some may be false alarms from page formatting):")
        for p in problems:
            print("  -", p)
    else:
        print("Every perk name, requirement and prerequisite was found on UESP.")
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="refetch pages instead of using the cache")
    ap.add_argument("--perks", action="store_true", help="check data/perks.json against UESP instead of races")
    ap.add_argument("--all", action="store_true", help="with --perks, also recheck trees already marked verified")
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    if args.perks:
        sys.exit(0 if check_perks(session, args.refresh, only_unverified=not args.all) else 1)
    races, problems = {}, []

    for race_id, title in RACE_PAGES.items():
        try:
            parsed = parse_race(fetch_wikitext(session, title, args.refresh))
        except Exception as exc:  # keep going; report at the end
            problems.append(f"{race_id}: fetch/parse failed ({exc})")
            continue
        p10 = parsed["p10"][0] if parsed["p10"] else None
        races[race_id] = {"p10": p10, "p5": sorted(parsed["p5"]),
                          "source": WIKI + title.replace(" ", "_")}

        # validation
        if not p10 or len(parsed["p5"]) != 5:
            problems.append(f"{race_id}: could not read all bonuses (got +10={p10}, +5={parsed['p5']})")
            continue
        want10, want5 = PLANNER[race_id]
        if p10 != want10 or sorted(want5) != sorted(parsed["p5"]):
            problems.append(f"{race_id}: UESP says +10 {p10}, +5 {sorted(parsed['p5'])}; "
                            f"planner has +10 {want10}, +5 {sorted(want5)}")
        else:
            print(f"OK  {race_id}")

    OUT.mkdir(exist_ok=True)
    (OUT / "races.json").write_text(json.dumps({
        "license": "CC BY-SA 2.5, text from UESP (https://en.uesp.net)",
        "fetched": time.strftime("%Y-%m-%d"),
        "races": races,
    }, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT / 'races.json'} ({len(races)} races)")

    if problems:
        print("\nNeeds attention:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("All race bonuses match the planner.")


if __name__ == "__main__":
    main()
