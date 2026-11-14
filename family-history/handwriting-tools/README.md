# Handwriting-model tools

The Python scripts behind [Train a handwriting model for your parish registers](../train-a-handwriting-model-for-your-parish-registers.md). They are written up from the study that is fine-tuning `trocr-kurrent-bern-parish-registers` on the Reformed parish registers of canton Bern (1555–1875, German Kurrent), and generalised so they work for any script and archive.

> **Work in progress.** The study is still running: the larger test set, the human check and publishing are not done yet. These scripts change with it.

They are **examples to adapt**, not a finished product. Everything specific to one project is in **`config.py`**.

## Setup

```bash
python3 -m venv htr-env && source htr-env/bin/activate
pip install torch transformers kraken pypdfium2 pillow pyarrow
```

`kraken` finds the text lines; `transformers` runs and fine-tunes TrOCR. A GPU helps a lot: Apple silicon (MPS) or NVIDIA (CUDA) are picked up automatically.

## The pipeline, in order

| Step | Script | What it does |
|---|---|---|
| 1 | *(you)* | Download the register PDFs into `registers/` (or set `HTR_REGISTERS`), gently: one at a time, with pauses |
| 2 | *(you)* | List the pages in `selection.json` (test set) or `selection-train-rN.json` (a training round): `[{"id": "parish01_i116", "file": "Parish/Parish_01*", "image": 116, "note": "baptisms 1700"}]` |
| 3 | `render.py [selection.json]` | renders each page to a grayscale PNG in `pages/` |
| 4 | `segment.py [selection.json]` | cuts each page into numbered line images (`lines/<page>/L001.png …`) with kraken, plus an overlay for checking |
| 5 | `sheets.py [selection.json]` | drops specks and fragments, and makes numbered sheets of 12 lines for the AI readers |
| 6 | `blind-reading.md` | the prompt for the two blind AI readers, one helper per page per model |
| 7 | `build_reference.py PAGE …` | compares the two readings: *agreed*, *close*, *disputed* or *noise*; writes `reference/<page>.consensus.tsv` and a review list |
| 8 | `adjudication_sheets.py PAGE` | enlarged sheets of the lines to settle on the image |
| 9 | *(you or the AI)* | settle lines in `review/<page>.decisions.tsv` (`line`, `text`, `note`; empty text = leave the line out) |
| 10 | `make_training.py PAGE …` | writes `training/<page>.tsv`: verified lines only, never `[?]`, with the conventions applied |
| 11 | `finetune.py BASE RUN [EPOCHS]` | fine-tunes the base model; refuses test pages and volumes; holds out whole validation pages; keeps the best epoch |
| 12 | `run_trocr.py PAGE MODEL NAME` | reads a page's lines with a model (base, or your checkpoint) |
| 13 | `score.py PAGE PAGE.verified.tsv` | character error rate (strict and loose) of every reader on a fully verified page |
| 14 | `score_consensus.py MODEL …` | the same on the consensus pages (a weaker check) |
| – | `agreement.py` | how much the two AI readers disagree, per page: a difficulty ranking |
| – | `conventions.py` | the character rules from your transcription guidelines, applied to training data and scores alike |
| – | `lookup_names.py` | gentle, cached look-ups of surnames and place names (a Swiss example; swap in your own references) |

## Rules built in

- Test pages and their whole volumes can never enter training (`finetune.py` refuses them).
- A training line must be confirmed to the character; `[?]` lines never enter.
- Validation uses whole held-out pages, so the score reflects unseen hands.
- Every result is a file you can keep: readings, references, decisions, logs.

## Licence

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), like the rest of this repository. Base models and datasets you use keep their own licences: credit them in your model card.
