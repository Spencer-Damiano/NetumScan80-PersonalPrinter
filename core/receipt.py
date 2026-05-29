"""
core/receipt.py — ESC/POS text receipt renderer.

Builds and prints fixed-size receipts to a Win32Raw thermal printer.
Every receipt is the same physical size on the roll regardless of content —
short descriptions pad with blank lines, long ones truncate.

Layout (48-char wide, Font A):
    ================================================  BORDER
                   TITLE GOES HERE
    ------------------------------------------------  THIN_BORDER
                  PRIORITY: HIGH
    ================================================  BORDER
    [body — always exactly BODY_LINES tall]
    ================================================  BORDER
                  2026-03-06  14:23
    ================================================  BORDER
"""

import textwrap
from datetime import datetime
from enum import IntEnum

try:
    from escpos.printer import Win32Raw
    _ESCPOS_AVAILABLE = True
except ImportError:
    _ESCPOS_AVAILABLE = False


# ── Layout ────────────────────────────────────────────────────────────────────

CHAR_WIDTH  = 48
BODY_LINES  = 15
BORDER      = "=" * CHAR_WIDTH
THIN_BORDER = "-" * CHAR_WIDTH


# ── Priority ──────────────────────────────────────────────────────────────────

class Priority(IntEnum):
    FUTURE = 0
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3

    # The 4 is for D - day and N is for day of week (0-6, Sunday–Saturday). might switch to 4 and N (1-7, Mon-Sun) if it turns out to be more intuitive.
    SUNDAY = 40
    MONDAY = 41
    TUESDAY = 42
    WEDNESDAY = 43
    THURSDAY = 44
    FRIDAY = 45
    SATURDAY = 46
    

    def label(self) -> str:
        return {
            Priority.FUTURE: "NOTE",
            Priority.LOW:    "CRAWL",
            Priority.MEDIUM: "WALK",
            Priority.HIGH:   "RUN",
            Priority.MONDAY: "MONDAY",
            Priority.TUESDAY: "TUESDAY",
            Priority.WEDNESDAY: "WEDNESDAY",
            Priority.THURSDAY: "THURSDAY",
            Priority.FRIDAY: "FRIDAY",
            Priority.SATURDAY: "SATURDAY",
            Priority.SUNDAY: "SUNDAY",
        }[self]


# Convenience alias so callers can do PRIORITY_LABELS[n] like before
PRIORITY_LABELS = {p.value: p.label() for p in Priority}


# ── Receipt ───────────────────────────────────────────────────────────────────

class Receipt:
    """
    A single-task receipt with a fixed physical size.

    Parameters
    ----------
    title        : Task title — printed in ALL CAPS and centered.
    description  : Body text — word-wrapped and vertically centered.
    priority     : 0 (Future/Breakdown), 1 (Low), 2 (Medium), 3 (High).
    printer_name : Windows printer name passed to Win32Raw.
    """

    def __init__(
        self,
        title: str,
        description: str,
        priority: int = 0,
        printer_name: str = "POS-80",
    ) -> None:
        if priority not in PRIORITY_LABELS:
            raise ValueError(f"invalid priority {priority!r}")

        self.title        = title.upper()
        self.description  = description
        self.priority     = Priority(priority)
        self.printer_name = printer_name
        self.timestamp    = datetime.now().strftime("%Y-%m-%d  %H:%M")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _body_lines(self) -> list[str]:
        """Word-wrap the description and fit it into exactly BODY_LINES lines."""
        wrapped = textwrap.wrap(self.description, width=CHAR_WIDTH)

        if len(wrapped) > BODY_LINES:
            wrapped = wrapped[:BODY_LINES]
            wrapped[-1] = wrapped[-1][: CHAR_WIDTH - 3].rstrip() + "..."

        # Horizontally center each line
        wrapped = [f"{line:^{CHAR_WIDTH}}" for line in wrapped]

        # Vertically center within BODY_LINES using blank padding
        blank      = BODY_LINES - len(wrapped)
        top_pad    = blank // 3
        bottom_pad = blank - top_pad
        return [""] * top_pad + wrapped + [""] * bottom_pad

    def _all_lines(self) -> list[str]:
        """Assemble the complete list of receipt lines."""
        return [
            BORDER,
            f"{self.title:^{CHAR_WIDTH}}",
            THIN_BORDER,
            f"{'PRIORITY: ' + self.priority.label():^{CHAR_WIDTH}}",
            BORDER,
            *self._body_lines(),
            BORDER,
            f"{self.timestamp:^{CHAR_WIDTH}}",
            BORDER,
        ]

    # ── Public API ────────────────────────────────────────────────────────────

    def preview(self) -> str:
        """Return the receipt as a plain-text string (no printing)."""
        return "\n".join(self._all_lines())

    def print(self) -> None:
        """Send the receipt to the thermal printer."""
        if not _ESCPOS_AVAILABLE:
            raise RuntimeError(
                "python-escpos is not installed — run: pip install python-escpos"
            )

        p = Win32Raw(self.printer_name, profile="NT-80-V-UL")

        p._raw(b"\x1b\x40")          # ESC @    — full printer reset
        p._raw(b"\x1b\x33\x00")      # ESC 3 0  — suppress top feed
        p._raw(b"\x1b\x33\x18")      # ESC 3 24 — restore 3.4 mm line spacing

        for line in self._all_lines():
            p.text(line + "\n")

        p._raw(b"\x1b\x64\x00")      # ESC d 0  — minimum bottom feed
        p._raw(b"\x1d\x56\x42\x00")  # GS V B   — partial cut