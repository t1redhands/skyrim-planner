# Skyrim Character Planner

A browser-based planner for building a *Skyrim* character from creation to level 60: perks, attributes, gear, household and a quest plan that fits the character.

**Open the planner:** <https://t1redhands.github.io/skyrim-planner/>

It covers the base game, Dawnguard, Hearthfire, Dragonborn and the Anniversary Edition's Creation Club content. Everything runs in your browser. There's nothing to install and no account to make.

## What it does

You plan in three milestones: **by level 20**, **by level 40** and **by level 60**. Each choice is tied to the milestone you want it by, and the planner checks whether the plan can work.

| Step | What you plan |
| --- | --- |
| 1. Identity | Name, race, alignment and class (23 classes, from Acrobat to Witchhunter), whether the character becomes a werewolf or vampire (with matching quests, gear, buffs and stone), sides and allegiances, plus free-form role-play notes. Sides cover the Civil War, Dawnguard, the Dark Brotherhood (join or destroy) and Paarthurnax (spare or kill); factions you join (Companions, College of Winterhold, Thieves Guild, Bards College) put their questlines into the plan as Priority. Alignment decides which questlines the quest plan suggests. "Suggest a plan" fills in a starting build for the chosen class. |
| 2. Perks and attributes | Perks in all 18 skill trees and the milestone for each, and how your level-ups split between Health, Magicka and Stamina. You get one perk per level, and the planner works out the skill levels each perk needs. |
| 3. Loadout | Standing Stones, shouts (how many words, and where you'll get them), spells, weapons, apparel (including faction and specialty gear), potions with a full ingredient list, food, scrolls and spider scrolls, and signature moves: named combinations of shouts, spells, potions and enchantments. Weapons and apparel are marked **Main build** (end-game gear), **Collect** (printed as a checklist with the collections) or **Incidental** (used along the way); main-build quests go in Priority, the rest in Selected. Standard gear can be marked as found or crafted, and given one or two enchantments. |
| 4. Household | Followers, a spouse, homes and pets, with the ones that suit your build marked. |
| 5. Collections | Checklists for skill books, Dragon Priest masks, Daedric artifacts, other artifacts, dragon claws, the Stones of Barenziah, the Black Books, the Litany of Larceny, East Empire pendants, and the display spots in the Creation Club homes Myrwatch, Tundra Homestead, Bloodchill Cavern and Shadowfoot Sanctum. Tick the items you want (or want a whole collection) and set a milestone, and their quests go into the quest plan. You tick items off as found in Play mode. |
| 6. Quest plan | A quest list built from your choices: **Expedite** quests give something the build needs, **Priority** quests suit the character, and **Selected** are your own extras. Add a whole questline at once (the main story, a faction, an add-on), then change any single quest's priority. Prerequisites are added automatically and move up with the quests that need them, and quests your Civil War or Dawnguard side locks out are left out. A quest browser filters every quest by questline, place, add-on, status and level. |
| 7. Summary | The whole build on one page, a printable build sheet, and a build code to save or share. The build sheet puts the build on page one and the checklists (shopping list, quests and collections) on the pages after. |

## Play mode

When the character is ready, **Play mode** in the header turns the planner into a play-through guide. **Back to plan** returns to the plan at any time, and edits there show up in Play mode straight away.

- **Now** shows your level, your attributes and perks so far, and the in-game date. It lists what's due before your next milestone: perks, quests to expedite, gear, Standing Stones and collection items. Overdue items are flagged, and the next quests in your plan come after.
- **Level up** asks which attribute you raised (suggesting the one your plan needs next) and which perk you took. The perk list starts with your plan's perks, and a perk you take that isn't in the plan can be added to it. You can also save a perk for later and record it when you spend it.
- **Collections** lists the items you want, to tick off as you find them.
- **Journal** keeps a dated log. Level-ups, finished quests and finds are written in as you mark them, and you can add your own entries and edit any of them. Each entry has an in-game date (day, month, year and time); the weekday fills in from the date, counting from the game's start on Sundas, 17th of Last Seed, 4E 201.
- **Download as text** saves the journal as a plain text file to edit in a word processor. **Export journal file** saves the whole character, plan and journal as a `.json` file that **Import a journal file** loads on another device.

Share links and build codes carry your progress (level, perks and attributes taken, quests done, items found, the in-game date) but not the journal.

**Survival Mode** can be switched on in the Identity step. The planner then uses Survival's carry weight (150 to start; the Steed Stone and Extra Pockets add 50) and adds notes wherever it changes things: race bonuses, healing, warmth, food, potions, shrines, travel and leveling. Most items, quests, perks, people and places link to their UESP page.

Warnings marked ⚠ flag anything that can't happen as planned, such as gear that isn't available by its milestone or a shout whose words come from a quest your side skips.

## Saving and sharing builds

- Your current build saves automatically in your browser.
- **Save in this browser** keeps a named copy you can reload later.
- **Copy build code** gives you a block of text that holds the whole build. Paste it into **Load from a build code** on any device to open the same build.
- **Copy share link** gives you a link that opens the build directly. Links are kept short by storing each item as its position in `data/ids.json` instead of by name. That list only ever grows, so old links keep working after the data is refreshed.

Builds are stored only in your own browser. Nothing is sent anywhere.

## License

The planner's code and original content (`index.html`, the scripts and this README) are dedicated to the public domain under **[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)**; see [LICENSE](LICENSE). Use, copy, change and share them however you like, with no permission or credit needed.

The game data in `data/` is the exception. It's summarized from wiki text licensed CC BY-SA, so it stays under CC BY-SA: if you reuse it, credit UESP and the Elder Scrolls Wiki and share it under the same terms.

## Credits

Game data comes from community wikis and is summarized:

- **[UESP, the Unofficial Elder Scrolls Pages](https://en.uesp.net/wiki/Skyrim:Skyrim)**, used under [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). This covers perks, leveling, races, Standing Stones, spells, gear, enchantments, alchemy, food, scrolls, followers, marriage, homes, quests and collections.
- **[The Skyforge](https://theskyforge.ning.com/groups/tes-character-building/forum/character-build-classes-of-the-elder-scrolls)**: the class list, adapted into short descriptions, skill focus and attribute splits.
- **[The Elder Scrolls Wiki](https://elderscrolls.fandom.com/wiki/Dragon_Shouts)**, used under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). This covers shout word locations and Daedric artifact quests.

Each data file in `data/` names the pages it came from. Because the source text is CC BY-SA, the data files are shared under the same terms. The planner's **About and credits** button lists every source with the date of its data.

This is an unofficial fan project. *The Elder Scrolls*, *Skyrim* and related names are trademarks of Bethesda Softworks and ZeniMax Media. The planner isn't made or endorsed by them, or by UESP or the Elder Scrolls Wiki.

## What's in this repository

```
index.html              The whole planner: page, styles and code in one file
LICENSE                 CC0 1.0 public domain dedication (code and original content)
data/                   Game data the planner loads (JSON)
  source/               Raw UESP pages the data is built from, plus the latest data check report
scripts/
  build_quests.py       Rebuilds data/quests.json from the saved quest pages
  check_data.py         Lists anything new on UESP that the planner doesn't have yet
  update_ids.py         Adds new ids to data/ids.json, the append-only list share links use
uesp_ingest.py          Downloads UESP pages and checks races and perks against them
update-data.sh          Monthly refresh: download, rebuild, check, push
```

## Running it yourself

The planner loads its data with `fetch`, so opening `index.html` straight from your disk won't work. Serve the folder instead:

```
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Keeping the data current

`update-data.sh` runs once a month from cron on the maintainer's server. It:

1. downloads fresh copies of the UESP pages the planner uses, every Skyrim quest page, and the items page of every Creation Club Creation
2. rebuilds `data/quests.json` and adds any new ids to `data/ids.json`
3. checks races and perks against UESP, and writes `data/source/CHECK_REPORT.md` listing any new items, followers, homes, ingredients or enchantments that UESP has and the planner doesn't
4. commits and pushes the results

If any download fails, nothing is pushed. Most of the data was checked and summarized by hand, so new items in the report are added by hand too. After reviewing the report, run `python3 scripts/check_data.py --baseline` to mark the current list as reviewed.

The ingest script needs Python 3 with `requests` and `mwparserfromhell`:

```
sudo apt install python3-requests python3-mwparserfromhell
```

It identifies itself to UESP with this repository's URL and waits between requests, as UESP asks.
