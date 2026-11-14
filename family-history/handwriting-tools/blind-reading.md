# Blind-reading helper prompt

The prompt each AI reader gets, one helper per page per model, run as separate background helpers. Two strong models read every page independently (their names are `READER_A` and `READER_B` in `config.py`); a smaller model can be added for comparison.

Replace the placeholders:
- `<DESCRIPTION>`: place, record type, period and script only, e.g. "baptism register of a Reformed parish, 1730s (German Kurrent)". No names, no hints.
- `<SHEETS>`: the full path to `lines/<PAGE>/sheets/`.
- `<OUTPUT>`: the full path to `model-readings/<PAGE>/<READER>.tsv`.

---

Blind handwriting-recognition test. Transcribe old handwriting from a historical register: <DESCRIPTION>.

INPUT: the sheet images in <SHEETS> (sheet01.png, sheet02.png, … in order). Each sheet shows cropped text lines, each with a red line number at its left.

RULES (for a fair test):
- Use your tools only to list that one sheets folder and to view ONLY those sheet images. Do not read, list or search any other file or folder (no references, reviews, training files or other readings; no .txt/.tsv/.json/.md). No web search.
- Diplomatic transcription of each numbered line: original spelling, special letters, umlauts, abbreviations and punctuation as written; no modernising or expanding. Crops may cut words at either end; transcribe only what is visible.
- Partly readable word: best reading followed by [?]. Unreadable word: [?]. Line with no readable text: [noise].
- Confidence per line: high, medium or low.

OUTPUT: write a UTF-8 tab-separated file to <OUTPUT>, header `line	text	confidence`, one row per numbered line in order. Reply with one line: the number of lines transcribed.
