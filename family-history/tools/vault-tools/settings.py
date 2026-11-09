"""Settings for the vault scripts: everything specific to one family lives here.

Copy this folder to `_System/tools/` in your vault and edit the values below.
Every other script imports this file, so nothing else needs changing.
"""

# The person the tree is built for: ahnentafel number 1. Usually you, so a
# living person: their note (if any) carries no details and is never published.
ROOT_PERSON = "Jane Example"          # note title in People/, or a name if there is no note
ROOT_LABEL = "Jane"                   # how generated pages refer to them ("Jane's tree")

# Anchors: people whose ahnentafel numbers you know. recompute.py walks up the
# father/mother links from here (father of n = 2n, mother = 2n + 1).
# Usually the four grandparents (4-7). If your parents have died and have notes,
# you can anchor them as 2 and 3 instead.
ANCHORS = {
    "Albert Smith (1901–1975)": 4,     # father's father
    "Rose Baker (1904–1990)": 5,       # father's mother
    "Tomasz Nowak (1898–1960)": 6,     # mother's father
    "Maria Kowalska (1902–1981)": 7,   # mother's mother
}

# The four grandparents' lines ("sides"), by ahnentafel number. Used for the
# canvases, timeline lanes, to-do grouping and completeness tables. Each
# person's `side` property should use one of these labels.
SIDES = {4: "Smith", 5: "Baker", 6: "Nowak", 7: "Kowalska"}

# Who counts as possibly living: no death recorded and born after this year,
# or no birth year and within this many generations of the root person.
# check.py warns about them; the website script leaves them out.
LIVING_BORN_AFTER = 1925
LIVING_MAX_GENERATION = 3

# Folders whose notes are listed in the "Narratives and research" section of
# each person and place (backlinks.py). Match your vault's folders.
BACKLINK_FOLDERS = ["Stories", "History", "Research", "Communities", "Governments", "Sources"]

# Bookkeeping notes that mention almost everyone; left out of backlinks and to-do.
BOOKKEEPING_NOTES = {"Research log", "Human tasks and blockers", "Open questions", "To-do"}

# Timeline canvas: first year on the ruler.
TIMELINE_START = 1600

# Words that sort tasks into groups on the to-do hub (regular expressions).
# Add your own archives, parishes, newspapers or book titles.
AI_TASK_GROUPS = [
    ("Church and parish registers", r"register|baptis|parish|church book|banns|burial"),
    ("Censuses, civil and land records", r"census|certificate|probate|deed|tax|land|naturali[sz]|passenger|manifest|ship"),
    ("Newspapers and obituaries", r"obituar|newspaper|periodical|column"),
    ("Books and online texts", r"book|read |transcribe|PDF|archive\.org|translation|article|chapter"),
    ("Parents and origins to trace", r"parents|origin|trace|identify|find .{0,30}(?:father|mother)|who was"),
]
HUMAN_TASK_GROUPS = [
    ("Sign-ins, subscriptions and purchases", r"sign|subscri|purchase|buy|pay|account"),
    ("Letters, emails and archive requests", r"send|letter|email|ask |request|write to|contact|order|obtain"),
    ("Books and papers to photograph", r"photograph|scan|copy of|pages|index"),
    ("DNA", r"DNA"),
    ("Decisions and checks", r"decide|check|confirm|verify|look"),
]

# ---- Website (used by site-scripts/prepare-content.py) ----

# Added to the foot of every published page. Say plainly how the research was made.
SITE_NOTICE = (
    "This is an AI-assisted family-history project: AI did much of the searching, "
    "transcription, translation and writing. Not every source, link or conclusion "
    "has been checked by a person, so please read it in that light."
)

# Notes kept off the site that other notes still link to: the link becomes this text.
SITE_UNPUBLISHED = {
    "Human tasks and blockers": "a list of tasks that need a person (not published)",
    "Research log": "the research log (not published)",
}

# Name of the folder beside the vault that holds large files. Mentions of
# files in it are replaced with "an offline copy" on the site.
ARCHIVE_FOLDER = "Family Tree Archive"
