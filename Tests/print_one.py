"""
Tests/PrintOne.py — Print a single receipt to the thermal printer.

Useful for tuning character limits and layout without printing the whole suite.
Edit the RECEIPT dict at the top to test whatever you want.

Usage:
    python Tests/PrintOne.py
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.html_receipt import render_png, DESCRIPTION_CHAR_LIMIT
from Tests.CharLimitTest import build as build_ruler
from escpos.printer import Win32Raw

PRINTER_NAME = "POS-80"

# ── Edit this to change what gets printed ─────────────────────────────────────
RECEIPT = {
    # "title": "Char Test 550",
    # "description": build_ruler(limit=DESCRIPTION_CHAR_LIMIT),
    # "priority": 0,
    "title": "Buy Groceries",
    "description": "Pick up milk, eggs, bread, and coffee from the store before 6pm.",
    "priority": 1,
}
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print(f"\n  PrintOne — sending '{RECEIPT['title']}' to {PRINTER_NAME}")

    tmp_dir = os.path.join(tempfile.gettempdir(), "receipt_preview")
    os.makedirs(tmp_dir, exist_ok=True)
    png_path = os.path.join(tmp_dir, "print_one.png")

    # Render PNG
    result = render_png(RECEIPT["title"], RECEIPT["description"], RECEIPT["priority"], png_path)
    if not result:
        print("  ERROR: could not render PNG — check imgkit/Selenium setup")
        return

    print(f"  PNG rendered: {png_path}")

    # Send to printer
    try:
        p = Win32Raw(PRINTER_NAME, profile="NT-80-V-UL")
        p._raw(b"\x1b\x40")          # ESC @ — reset
        p._raw(b"\x1b\x33\x00")      # ESC 3 0 — suppress top feed
        p.image(png_path, impl="bitImageColumn", center=True)
        p._raw(b"\x1b\x64\x04")      # ESC d 4 — small bottom feed before cut
        p._raw(b"\x1d\x56\x42\x00")  # GS V B — partial cut
        print("  Done!")
    except Exception as e:
        print(f"  ERROR: could not print — {e}")


if __name__ == "__main__":
    main()