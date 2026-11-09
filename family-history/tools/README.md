# Family-history vault tools

Small Python scripts that keep an Obsidian family-history vault tidy and build a website from it. They are the working tools behind [genealogy.ramsei.ai](https://genealogy.ramsei.ai), generalised so they work for any family. Use them as they are, or hand them to an AI agent as a starting point (see part 6 and part 7 of [the starter prompt](../build-your-own-family-history-with-ai.md)).

They are **examples to adapt**, not a finished product. They assume the vault structure described in the prompt: a `People/` folder of notes with YAML properties such as `father`, `mother`, `born`, `died`, `side`, `evidence` and `ahnentafel`.

## What's here

| Folder | What it holds |
|---|---|
| `vault-tools/` | nine scripts that rebuild the vault's generated views, a `rebuild.sh` that runs them in order, and **`settings.py`, the only file you need to edit** |
| `site-scripts/` | two scripts for a [Quartz](https://quartz.jzhao.xyz) website: copy the vault into the site, then prepare the copy for publishing |
| `example-vault/` | a small **made-up** family (Jane Example and her ancestors) to try the tools on. Every person, place and source in it is fictional |

## The vault scripts

Copy `vault-tools/` into your vault as `_System/tools/`, edit `settings.py`, then run:

```bash
bash "_System/tools/rebuild.sh" "/path/to/your/vault"
```

| Script | What it does |
|---|---|
| `settings.py` | everything specific to one family: the root person, the anchor ancestors and their numbers, the four sides, the living-person rule, the folders, the task groups and the website notice |
| `recompute.py` | works out each person's ancestor number (ahnentafel), generation and relationship ("2nd great-grandmother") from the father and mother links |
| `canvases.py` | one Obsidian canvas per side, ancestors coloured by evidence level |
| `timeline.py` | a canvas of everyone laid out by lifetime, one lane per side, with History events along the top |
| `completeness.py` | `Dashboards/Completeness.md`: how complete each field is, how full each generation is, and every gap |
| `migration.py` | `Dashboards/Migration routes.md`: each ancestor's dated residences as a route and a country path |
| `descent.py` | for every double ancestor (pedigree collapse), each route down to the root person |
| `backlinks.py` | a generated "Narratives and research" section on every person and place, listing the notes that mention them |
| `todo.py` | `Research/To-do.md`: open questions, conflicts, AI and human tasks, blockers, and the **edges** (ancestors with an unknown parent, with what has been tried) |
| `check.py` | a health check, run last: broken links, unparseable properties, untagged tasks, undated search-log entries, missing fields and **possible living people** |

The vault scripts use only the Python standard library. `check.py` also checks YAML if PyYAML is installed.

## The site scripts

Put them in your Quartz site's `scripts/` folder. Your own home page and about page go in `site/` in the same repository.

```bash
VAULT="/path/to/your/vault" ./scripts/sync-vault.sh
npx quartz build --serve
```

`sync-vault.sh` copies the vault into `content/`, leaving out `_System/`, canvases, `Research/Private/`, drafts, the to-do hub and the AI rules files. To keep more notes off the site, list them in `scripts/site-exclude.txt`. Then it runs `prepare-content.py`, which edits only the copy:

- **leaves out anyone who may be living**, and the root person's own note;
- shows each person's conflicts and search log as "Open questions" and "Research log" sections;
- adds a line of descent to each ancestor;
- writes one family-tree page per side;
- replaces paths to files on your computer with "an offline copy";
- turns links to unpublished notes into plain text;
- adds the research notice and the record's compiled date to every page;
- leaves out attachments that no published page uses.

It needs PyYAML (`pip install pyyaml`).

**Check before you publish.** The living-person rule is a safety net, not a guarantee. Read what changed before every push.

## Try it

```bash
bash example-vault/_System/tools/rebuild.sh example-vault
```

Then open `example-vault` in Obsidian. Peter Smith (a made-up relative born in 1950) is flagged by `check.py` as possibly living, and the site scripts leave him out.

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), like the rest of this repository.
