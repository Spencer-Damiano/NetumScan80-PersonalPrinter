"""
Tests/print_preview.py — Receipt print preview tool.

Renders a receipt to HTML (opens in browser) and PNG (opens in image viewer).
No printer required.

Usage:
    python Tests/print_preview.py
"""

import os
import sys
import tempfile
import webbrowser

# Step up one level from Tests/ to the project root so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.html_receipt import save_html, render_png, PRIORITY_LABELS
from Tests.CharLimitTest import build as build_ruler


# ── Preset samples ────────────────────────────────────────────────────────────
SAMPLES = [
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
]


def open_file(path: str):
    """Open a file with the system default application (Windows)."""
    os.startfile(path)


def preview(title: str, description: str, priority: int):
    """Render and open a receipt as both HTML and PNG."""
    tmp_dir = os.path.join(tempfile.gettempdir(), "receipt_preview")
    os.makedirs(tmp_dir, exist_ok=True)

    html_path = os.path.join(tmp_dir, "receipt.html")
    png_path  = os.path.join(tmp_dir, "receipt.png")

    # HTML → browser
    save_html(title, description, priority, html_path)
    webbrowser.open(f"file:///{html_path.replace(os.sep, '/')}")
    print(f"  HTML: {html_path}")

    # PNG → image viewer
    result = render_png(title, description, priority, png_path)
    if result:
        open_file(png_path)
        print(f"  PNG:  {png_path}")
    else:
        print("  PNG: skipped (see error above)")


def char_limit_test():
    """Prompt for a char count and render the marked lorem ruler at that length."""
    print()
    try:
        count = int(input("  Enter char count to test (e.g. 75): ").strip())
    except ValueError:
        print("  Invalid number, cancelling.")
        return

    ruler = build_ruler(limit=count)
    print(f"  Ruler ({count} chars): {ruler}\n")
    preview(f"Char Test {count}", ruler, 0)


def pick_sample():
    print("\n  Samples:")
    for i, s in enumerate(SAMPLES):
        label = PRIORITY_LABELS[s["priority"]]
        print(f"    {i + 1}. [{label}] {s['title']}")
    print("    4. Char limit test")
    print("    c. Custom")
    print("    q. Quit\n")

    choice = input("  > ").strip().lower()

    if choice == "q":
        return "quit"

    if choice == "4":
        char_limit_test()
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
        print()
        preview(title, description, priority)
        return "continue"

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(SAMPLES):
            s = SAMPLES[idx]
            print()
            preview(s["title"], s["description"], s["priority"])
            return "continue"
    except ValueError:
        pass

    print("  Invalid choice.")
    return "continue"


def main():
    print("\n  Receipt Print Preview")
    print("  " + "=" * 30)

    while True:
        result = pick_sample()
        if result == "quit":
            print("  Bye!")
            break
        print("  Done. Choose another or quit.\n")


if __name__ == "__main__":
    main()