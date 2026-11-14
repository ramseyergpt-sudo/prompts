"""Character conventions from your GUIDELINES.md, shared by make_training.py and the scorers.

These are the rules of the Bern study (German Kurrent, 2026-11-08). Edit them to match your own guidelines.
"""
import re, unicodedata


def conventions(t):
    t = unicodedata.normalize("NFD", t or "")
    t = t.replace("ſ", "s")                                   # §2 long s written s
    t = re.sub(r"([nm])\u0304", "\\1\u0303", t)               # §3 stroke over n/m: combining tilde (OCR-D)
    t = unicodedata.normalize("NFC", t)                       # composed letters, so \w sees ä, ü, ñ
    t = t.replace("–", "—")                                   # §6 one dash form
    t = re.sub(r"(?<=\w)[-=⸗]\s*$", "¬", t)                   # §6 line-end hyphen joined to a word: ¬
    t = re.sub(r"=\s*$", "¬", t)                              # §6 double stroke at line end, any form
    t = re.sub(r"^[=⸗]", "¬", t)                              # §6 repeated hyphen at line start
    t = re.sub(r"(?<=\w)=(?=\w)", "-", t)                     # §6 hyphen inside a compound
    return unicodedata.normalize("NFC", t)
