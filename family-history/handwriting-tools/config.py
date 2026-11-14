"""Settings for the handwriting-model scripts: everything specific to one project lives here.

The scripts keep their working data next to themselves (pages/, lines/, model-readings/,
reference/, review/, training/, checkpoints/). Large files: keep this folder out of Git,
or ignore those subfolders.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Where the downloaded register PDFs are. A selection file's "file" pattern is matched inside it.
REGISTERS_DIR = os.environ.get("HTR_REGISTERS", os.path.join(HERE, "registers"))

# The two independent AI readers whose blind readings make the consensus. These are the
# file names their readings are saved under: model-readings/<page>/<name>.tsv
READER_A, READER_B = "opus-5.5", "fable-5.1"

# Rendering and line filtering
RENDER_LONG_SIDE = 3600          # pixels on the long side of each rendered page
MIN_LINE_WIDTH, MIN_LINE_HEIGHT = 220, 28   # smaller crops are specks or fragments
LINES_PER_SHEET = 12

# Test pages that are fully verified (excluded from the consensus scoring, which covers the rest).
VERIFIED_PAGES = []              # e.g. ["parishA01_i116", "parishB06_i085"]

# Fine-tuning
VALIDATION_PAGES = []            # whole pages held out for validation, about 10 % of the lines
EPOCHS, BATCH, LEARNING_RATE, SEED = 8, 8, 2e-5, 7
# Optional mix-in of the base model's own training lines, to limit forgetting.
# Parquet files with "image" ({"bytes": ...}) and "text" columns, in MIX_DIR. Empty list = no mix-in.
MIX_DIR = os.path.join(HERE, "base-mix")
MIX_FILES = []
MIX_SHARE, MIX_POOL = 0.25, 1500


def device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
