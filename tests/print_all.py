"""
tests/print_all.py — Print all test cases to the thermal printer.

Prints all sample receipts plus a char-limit stress test back to back.
Make sure the printer is on and connected before running.

Usage:
    python tests/print_all.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.receipt import Receipt, CHAR_WIDTH
from tests.char_limit import build as build_ruler


TESTS = [
    {
        "title":       "Buy Groceries",
        "description": "Pick up milk, eggs, bread, and coffee from the store before 6pm.",
        "priority":    1,
    },
    {
        "title":       "Fix Login Bug",
        "description": (
            "Users on the auth refresh endpoint are getting 401 errors after "
            "token expiry. Check the validation logic."
        ),
        "priority":    3,
    },
    {
        "title":       "Plan Q3 Roadmap",
        "description": (
            "Draft feature roadmap for Q3. Include push notifications, "
            "dark mode, and new onboarding flow."
        ),
        "priority":    2,
    },
    {
        "title":       "Char Limit Test",
        "description": build_ruler(limit=CHAR_WIDTH * 15),
        "priority":    0,
    },
]


def main() -> None:
    print(f"\n  Print All Tests — {len(TESTS)} receipts queued")
    print("  " + "=" * 30)

    for i, test in enumerate(TESTS, start=1):
        print(f"\n  [{i}/{len(TESTS)}] {test['title']}")
        try:
            Receipt(test["title"], test["description"], test["priority"]).print()
            print("         Printed.")
        except Exception as e:
            print(f"         ERROR: {e}")

    print("\n  All done!")


if __name__ == "__main__":
    main()