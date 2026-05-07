"""
tests/print_preview.py — Terminal preview tool for receipts.

Renders a receipt as plain text in the terminal using Receipt.preview().
No printer required.

Usage:
    python tests/print_preview.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.receipt import Receipt, PRIORITY_LABELS
from tests.char_limit import build as build_ruler


SAMPLES = [
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
]


def preview(title: str, description: str, priority: int) -> None:
    """Print a receipt preview to the terminal."""
    r = Receipt(title, description, priority)
    print()
    print(r.preview())
    print()


def _char_limit_test() -> None:
    print()
    try:
        count = int(input("  Enter char count to test (e.g. 75): ").strip())
    except ValueError:
        print("  Invalid number, cancelling.")
        return

    ruler = build_ruler(limit=count)
    preview(f"Char Test {count}", ruler, 0)


def _pick_sample() -> str:
    print("\n  Samples:")
    for i, s in enumerate(SAMPLES):
        print(f"    {i + 1}. [{PRIORITY_LABELS[s['priority']]}] {s['title']}")
    print("    4. Char limit test")
    print("    c. Custom")
    print("    q. Quit\n")

    choice = input("  > ").strip().lower()

    if choice == "q":
        return "quit"

    if choice == "4":
        _char_limit_test()
        return "continue"

    if choice == "c":
        print()
        title       = input("  Title:       ").strip() or "Untitled"
        description = input("  Description: ").strip() or "No description."
        print("  Priority: " + ", ".join(f"{k}={v}" for k, v in PRIORITY_LABELS.items()))
        try:
            priority = int(input("  Priority #:  ").strip())
            if priority not in PRIORITY_LABELS:
                raise ValueError
        except ValueError:
            priority = 0
        preview(title, description, priority)
        return "continue"

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(SAMPLES):
            s = SAMPLES[idx]
            preview(s["title"], s["description"], s["priority"])
            return "continue"
    except ValueError:
        pass

    print("  Invalid choice.")
    return "continue"


def main() -> None:
    print("\n  Receipt Print Preview")
    print("  " + "=" * 30)

    while True:
        if _pick_sample() == "quit":
            print("  Bye!")
            break
        print("  Done. Choose another or quit.\n")


if __name__ == "__main__":
    main()