import os
from random import choice
from pathlib import Path

from cloudbot import hook

_HANBS_DIR = Path(__file__).parent / "data" / "hanbs"


def _load_hanbs():
    """Load all .txt files from the hanbs data directory."""
    hanbs = []
    if _HANBS_DIR.is_dir():
        for f in sorted(_HANBS_DIR.iterdir()):
            if f.is_file() and f.suffix == ".txt" and not f.name.startswith("_"):
                text = f.read_text(encoding="utf-8").strip()
                if text:
                    hanbs.append(text)
    return hanbs


HANBS = _load_hanbs()


@hook.command("hanb", autohelp=False)
def hanb(text: str):
    """- Prints a random hanb"""
    if not HANBS:
        return "No hanbs found in data directory."
    ranb = choice(HANBS)
    return ranb.split("\n")
