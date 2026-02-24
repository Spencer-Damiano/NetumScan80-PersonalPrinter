"""
Tests/PrintAllTests.py — Print all test cases to the thermal printer.

Prints all sample receipts plus the 550-char limit test back to back.
Make sure the printer is on and connected before running.

Usage:
    python Tests/PrintAllTests.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.html_receipt import render_png, DESCRIPTION_CHAR_LIMIT
from Tests.CharLimitTest import build as build_ruler
from escpos.printer import Win32Raw
from PIL import Image
import tempfile

PRINTER_NAME = "POS-80"

# ── Test cases ────────────────────────────────────────────────────────────────
TESTS = [
    {
        "title": "Buy Groceries",
        "description": "Pick up milk, eggs, bread, and coffee from the store before 6pm.",
        "priority": 1,
    },
    {
        "title": "Fix Login Bug",
        "description": (
            "Users on the auth refresh endpoint are getting 401 errors after "
            "token expiry. Check the validation logic."
        ),
        "priority": 3,
    },
    {
        "title": "Plan Q3 Roadmap",
        "description": (
            "Draft feature roadmap for Q3. Include push notifications, "
            "dark mode, and new onboarding flow."
        ),
        "priority": 2,
    },
    {
        "title": "Char Test 550",
        "description": build_ruler(limit=550),
        "priority": 0,
    },
]


def print_receipt(png_path: str, p: Win32Raw):
    """Send a PNG image to the printer."""
    p._raw(b"\x1b\x40")          # ESC @ — reset
    p._raw(b"\x1b\x33\x00")      # ESC 3 0 — suppress top feed
    p.image(png_path, impl="bitImageColumn", center=True)
    p._raw(b"\x1b\x64\x04")      # ESC d 4 — small bottom feed before cut
    p._raw(b"\x1d\x56\x42\x00")  # GS V B — partial cut


def main():
    print("\n  Print All Tests")
    print("  " + "=" * 30)
    print(f"  {len(TESTS)} receipts queued\n")

    tmp_dir = os.path.join(tempfile.gettempdir(), "receipt_preview")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        p = Win32Raw(PRINTER_NAME, profile="NT-80-V-UL")
    except Exception as e:
        print(f"  ERROR: Could not connect to printer '{PRINTER_NAME}'\n  {e}")
        return

    for i, test in enumerate(TESTS, 1):
        print(f"  [{i}/{len(TESTS)}] Printing: {test['title']} ...")

        png_path = os.path.join(tmp_dir, f"test_{i}.png")
        result   = render_png(test["title"], test["description"], test["priority"], png_path)

        if not result:
            print(f"         Skipped — could not render PNG")
            continue

        try:
            print_receipt(png_path, p)
            print(f"         Done.")
        except Exception as e:
            print(f"         ERROR: {e}")

    print("\n  All done!")


if __name__ == "__main__":
    main()