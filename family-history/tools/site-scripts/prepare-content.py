"""Prepare the vault copy in content/ for a public Quartz site.

Run by sync-vault.sh after copying. Edits only content/, never the vault:
  - removes notes about people who may be living (and the root person's own note);
  - renames the History "date:" property, which Quartz would read as a page date;
  - shows each person's conflicts and search log as readable sections;
  - adds each ancestor's line of descent, from the ahnentafel numbers;
  - writes one family-tree page per side (a nested list of ancestors);
  - replaces pointers to files on your computer with "an offline copy";
  - turns links to unpublished notes into plain text;
  - adds the research notice and the record's compiled date to every page;
  - removes attachments that no published page links to or embeds.

Settings (root person, sides, living rule, notice) come from the vault's
_System/tools/settings.py, so the vault and the site agree.

    python3 scripts/prepare-content.py content/ "/path/to/vault"
"""

import re
import runpy
import sys
from datetime import date
from pathlib import Path

import yaml  # pip install pyyaml

CONTENT = Path(sys.argv[1])
VAULT = Path(sys.argv[2])
S = runpy.run_path(str(VAULT / "_System" / "tools" / "settings.py"))

NOTICE = f"\n\n> [!info] About this research\n> {S['SITE_NOTICE']}\n"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


def split(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None, "", text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = None
    return data, m.group(0), text[m.end():]


def year(value):
    m = re.search(r"\d{4}", str(value or ""))
    return int(m.group()) if m else None


def as_list(value):
    if not value:
        return []
    return value if isinstance(value, list) else [value]


def is_living(stem, data):
    if stem == S["ROOT_PERSON"]:
        return True
    if not isinstance(data, dict) or data.get("type") != "person":
        return False
    if data.get("died"):
        return False
    born = year(data.get("born"))
    if born:
        return born > S["LIVING_BORN_AFTER"]
    generation = data.get("generation")
    return isinstance(generation, int) and generation <= S["LIVING_MAX_GENERATION"]


# ---- Conflicts and search log as readable sections

def log_entry(entry):
    m = re.match(r"(\d{4}-\d{2}-\d{2}):\s*(.*)", str(entry), re.S)
    return f"**{m.group(1)}:** {m.group(2)}" if m else str(entry)


def research_sections(data):
    if not isinstance(data, dict):
        return ""
    out = ""
    conflicts = as_list(data.get("conflicts"))
    if conflicts:
        out += "\n\n## Open questions\n\n" + "\n".join(f"- {c}" for c in conflicts)
    log = as_list(data.get("search_log"))
    if log:
        out += "\n\n## Research log\n\n" + "\n".join(f"- {log_entry(e)}" for e in log)
    return out


# ---- Files on your computer: never publish paths

LOCAL_SPAN = re.compile(
    r"`((?:\.\./|~/|/Users/|/home/|[A-Z]:\\|" + re.escape(S["ARCHIVE_FOLDER"]) + r"/)[^`]*)`"
)


def drop_local_paths(body):
    def offline(m):
        return "an offline folder" if m.group(1).endswith(("/", "\\", "*")) else "an offline copy"
    return LOCAL_SPAN.sub(offline, body)


def unlink_unpublished(body):
    for name, text in S["SITE_UNPUBLISHED"].items():
        body = re.sub(rf"\[\[{re.escape(name)}(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", text, body)
    return body


# ---- Line of descent, from the ahnentafel numbers

def relation(number, sex):
    steps = number.bit_length() - 1
    noun = {"M": "father", "F": "mother"}.get(str(sex)[:1].upper(), "parent")
    if steps == 1:
        return noun
    if steps == 2:
        return "grand" + noun
    if steps == 3:
        return "great-grand" + noun
    n = steps - 2
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix} great-grand{noun}"


def ahnentafel_index():
    index = {}
    for path in (CONTENT / "People").glob("*.md"):
        data, _, _ = split(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for n in as_list(data.get("ahnentafel")):
                if str(n).isdigit():
                    index[int(n)] = (path.stem, data.get("sex"))
    return index


def descent_section(data, index):
    numbers = sorted(int(n) for n in as_list(data.get("ahnentafel")) if str(n).isdigit() and int(n) >= 2)
    if not numbers:
        return ""
    blocks = []
    for i, start in enumerate(numbers, 1):
        title = "Line of descent" if len(numbers) == 1 else f"Line {i} of {len(numbers)}"
        lines = [f"**{title}** (ancestor no. {start})", ""]
        n = start
        while n >= 2:
            label = "this person" if n == start else relation(n, index.get(n, (None, "M" if n % 2 == 0 else "F"))[1])
            if n in index:
                lines.append(f"- [[{index[n][0]}]]: {label}")
            elif n in (2, 3):
                lines.append(f"- {S['ROOT_LABEL']}'s {'father' if n == 2 else 'mother'} (not shown)")
            else:
                lines.append(f"- *not yet identified*: {label}")
            n //= 2
        lines.append(f"- {S['ROOT_LABEL']}")
        blocks.append("\n".join(lines))
    intro = "This person appears in the family tree more than once (pedigree collapse).\n\n" if len(numbers) > 1 else ""
    return "## Line of descent\n\n" + intro + "\n\n".join(blocks) + "\n\n"


def add_descent(data, body, index):
    # The vault's own "Lines of descent" block (descent.py) is replaced by this one.
    body = re.sub(r"^## Lines of descent\n+<!-- descent:start.*?<!-- descent:end -->\n*", "", body, flags=re.M | re.S)
    block = descent_section(data, index)
    if not block:
        return body
    first = re.search(r"^## ", body, re.M)
    if not first:
        return body.rstrip() + "\n\n" + block
    return body[: first.start()] + block + body[first.start():]


def compiled_line(data):
    if not isinstance(data, dict) or not data.get("updated"):
        return ""
    try:
        when = date.fromisoformat(str(data["updated"])[:10])
    except ValueError:
        return ""
    return f"\n\n*Record compiled {when.day} {when:%B %Y}.*"


# ---- Main pass over every note

ANCESTORS = ahnentafel_index()
removed = []
for path in sorted(CONTENT.rglob("*.md")):
    data, front, body = split(path.read_text(encoding="utf-8"))
    if is_living(path.stem, data):
        removed.append(path.stem)
        path.unlink()
        continue
    front = re.sub(r"^date: ", "event_date: ", front, flags=re.M)
    front = re.sub(r"^archive_file: .*\n", "", front, flags=re.M)
    if isinstance(data, dict) and data.get("type") == "person":
        body = add_descent(data, body, ANCESTORS)
    body = drop_local_paths(body.rstrip() + research_sections(data))
    body = unlink_unpublished(body)
    path.write_text(front + body + compiled_line(data) + NOTICE, encoding="utf-8")
for name in removed:
    print(f"Left out (possibly living): {name}")

# The living filter may have removed people listed in the index.
ANCESTORS = {n: v for n, v in ANCESTORS.items() if (CONTENT / "People" / f"{v[0]}.md").exists()}

# ---- Family-tree pages: one per side, a nested list (father above mother)

repeats = {}
for name, _ in ANCESTORS.values():
    repeats[name] = repeats.get(name, 0) + 1


def tree_lines(n, depth):
    if n not in ANCESTORS:
        return []
    name = ANCESTORS[n][0]
    mark = " ↺" if repeats[name] > 1 else ""
    lines = ["  " * depth + f"- [[{name}]]{mark}"]
    for parent in (2 * n, 2 * n + 1):
        lines += tree_lines(parent, depth + 1)
    return lines


pages = []
trees = CONTENT / "Family trees"
for n, side in S["SIDES"].items():
    lines = tree_lines(n, 0)
    if not lines:
        continue
    trees.mkdir(exist_ok=True)
    title = f"{side} side"
    pages.append((title, len(lines)))
    (trees / f"{title}.md").write_text(
        f'---\ntitle: "{title}"\n---\n\n'
        f"{S['ROOT_LABEL']}'s ancestors on the {side} side. Each person's **father is listed above their mother**, "
        "one level further in. **↺** marks someone who appears more than once in the tree.\n\n"
        + "\n".join(lines) + "\n" + NOTICE, encoding="utf-8")
if pages:
    (trees / "index.md").write_text(
        '---\ntitle: "Family trees"\n---\n\n' + "\n".join(f"- [[{t}]] ({c} ancestors)" for t, c in pages) + "\n" + NOTICE,
        encoding="utf-8")
    print("Family trees: " + ", ".join(f"{t} ({c})" for t, c in pages))

# ---- Publish only attachments that a page shows or links to

LINK = re.compile(r"\[\[([^\]|#]+)|\]\(([^)#\s]+)")
referenced = set()
for path in CONTENT.rglob("*.md"):
    for wiki, md in LINK.findall(path.read_text(encoding="utf-8")):
        target = Path((wiki or md).strip().replace("%20", " "))
        referenced.update({target.name, target.stem})
pruned = 0
attachments = CONTENT / "Attachments"
if attachments.exists():
    for path in sorted(attachments.rglob("*")):
        if path.is_file() and path.suffix != ".md" and not {path.name, path.stem} & referenced:
            path.unlink()
            pruned += 1
    for folder in sorted(attachments.rglob("*"), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
print(f"Attachments not linked from any page, left out: {pruned}")

# ---- Links to notes that are not on the site become plain text (no 404s)

known = set()
for f in CONTENT.rglob("*"):
    if f.is_file():
        known.update({f.stem.lower(), f.name.lower()})
        if f.suffix == ".md":
            data, _, _ = split(f.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                known.update(str(a).lower() for a in as_list(data.get("aliases")))
WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]+))?\]\]")
dead = {}


def unlink_dead(m):
    target = m.group(1).strip().rstrip("\\").strip()
    base = target.split("/")[-1].lower()
    if base in known or target.lower() in known or base.removesuffix(".md") in known:
        return m.group(0)
    dead[target] = dead.get(target, 0) + 1
    return m.group(3) or target.split("/")[-1]


for f in CONTENT.rglob("*.md"):
    data, front, body = split(f.read_text(encoding="utf-8"))
    new_body = WIKILINK.sub(unlink_dead, body)
    if new_body != body:
        f.write_text(front + new_body, encoding="utf-8")
print(f"Links to notes not on the site, made plain text: {sum(dead.values())} ({len(dead)} notes)")
