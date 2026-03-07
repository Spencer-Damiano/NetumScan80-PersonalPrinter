"""
tests/print_one.py — Print a single receipt to the thermal printer.

Useful for tuning layout without printing the whole suite.
Edit the RECEIPT dict below to test whatever you want.

Usage:
    python tests/print_one.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.receipt import Receipt, CHAR_WIDTH
from tests.char_limit import build as build_ruler


# ── Edit this to change what gets printed ─────────────────────────────────────
RECEIPT = {
    # "title":       "Char Limit Test",
    # "description": build_ruler(limit=CHAR_WIDTH * 15),
    # "priority":    0,
    "title":       "Buy Groceries",
    "description": "Pick up milk, eggs, bread, and coffee from the store before 6pm.",
    "priority":    1,
}
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    r = Receipt(RECEIPT["title"], RECEIPT["description"], RECEIPT["priority"])

    print(f"\n  print_one — '{r.title}'")
    print(r.preview())

    try:
        r.print()
        print("  Done!")
    except Exception as e:
        print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()