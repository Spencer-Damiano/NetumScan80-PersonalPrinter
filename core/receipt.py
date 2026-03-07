"""
core/receipt.py — ESC/POS text receipt renderer.

Fixed receipt size matches SquareGridTest.py:
  CHAR_WIDTH = 48  (characters per line)
  BODY_LINES = 15  (body is always exactly this many lines — padded or truncated)

Every receipt is the same physical size on the roll regardless of content.
Short descriptions pad with blank lines. Long descriptions truncate.

This module is imported by other systems to create and print receipts.
It is not run directly.
"""

import textwrap
from datetime import datetime

try:
    from escpos.printer import Win32Raw
    _ESCPOS_AVAILABLE = True
except ImportError:
    _ESCPOS_AVAILABLE = False


# ── Priority levels ───────────────────────────────────────────────────────────
PRIORITY_LABELS = {
    0: "FUTURE / BREAKDOWN",
    1: "LOW",
    2: "MEDIUM",
    3: "HIGH",
}

# ── Layout constants — match SquareGridTest.py exactly ───────────────────────
CHAR_WIDTH  = 48
BODY_LINES  = 15  # body is always exactly this tall
BORDER      = "=" * CHAR_WIDTH
THIN_BORDER = "-" * CHAR_WIDTH


class Receipt:
    """
    A single-task receipt with a fixed physical size.

    The body is always exactly BODY_LINES tall — short content is padded
    with blank lines, long content is truncated. This ensures every receipt
    is the same size on the roll regardless of what's in it.

    Parameters
    ----------
    title        : str — task title, printed in ALL CAPS and centered
    description  : str — body text, word-wrapped at CHAR_WIDTH
    priority     : int — 0 (Future/Breakdown), 1 (Low), 2 (Medium), 3 (High)
    printer_name : str — Windows printer name (default "POS-80")
    """

    def __init__(
        self,
        title: str,
        description: str,
        priority: int = 0,
        printer_name: str = "POS-80",
    ):
        if priority not in PRIORITY_LABELS:
            raise ValueError(f"Priority must be 0–3, got {priority}")

        self.title          = title.upper()
        self.description    = description
        self.priority       = priority
        self.priority_label = PRIORITY_LABELS[priority]
        self.printer_name   = printer_name
        self.timestamp      = datetime.now().strftime("%Y-%m-%d  %H:%M")

    def _build_lines(self) -> list[str]:
        """
        Return the full list of text lines that make up the receipt.
        The body section is always exactly BODY_LINES tall.
        """
        # ── Wrap description and enforce BODY_LINES ───────────────────────────
        wrapped = textwrap.wrap(self.description, width=CHAR_WIDTH)

        if len(wrapped) > BODY_LINES:
            # Truncate and mark the last line
            wrapped = wrapped[:BODY_LINES]
            wrapped[-1] = wrapped[-1][: CHAR_WIDTH - 3].rstrip() + "..."

        # Horizontal center — pad each line to CHAR_WIDTH
        wrapped = [f"{line:^{CHAR_WIDTH}}" for line in wrapped]

        # Vertical center — split remaining blank lines evenly above and below
        blank_lines = BODY_LINES - len(wrapped)
        top_pad     = blank_lines // 2
        bottom_pad  = blank_lines - top_pad
        wrapped     = [""] * top_pad + wrapped + [""] * bottom_pad

        lines = []

        # ── Header ────────────────────────────────────────────────────────────
        lines.append(BORDER)
        lines.append(f"{self.title:^{CHAR_WIDTH}}")
        lines.append(THIN_BORDER)
        lines.append(f"{'PRIORITY: ' + self.priority_label:^{CHAR_WIDTH}}")
        lines.append(BORDER)

        # ── Body (always exactly BODY_LINES) ──────────────────────────────────
        lines.extend(wrapped)

        # ── Footer ────────────────────────────────────────────────────────────
        lines.append(BORDER)
        lines.append(f"{self.timestamp:^{CHAR_WIDTH}}")
        lines.append(BORDER)

        return lines

    def preview(self) -> str:
        """Return a string preview of the receipt (no printing)."""
        return "\n".join(self._build_lines())

    def print(self) -> None:
        """Send the receipt to the printer."""
        if not _ESCPOS_AVAILABLE:
            raise RuntimeError("escpos is not installed. Run: pip install python-escpos")

        p = Win32Raw(self.printer_name, profile="NT-80-V-UL")

        # ── Reset & line spacing ──────────────────────────────────────────────
        p._raw(b"\x1b\x40")         # ESC @ — full reset
        p._raw(b"\x1b\x33\x00")     # ESC 3 0 — flush top feed
        p._raw(b"\x1b\x33\x18")     # ESC 3 24 — 3.4mm line spacing

        for line in self._build_lines():
            p.text(line + "\n")

        # ── Minimal bottom feed + cut ─────────────────────────────────────────
        p._raw(b"\x1b\x64\x00")     # ESC d 0 — minimum bottom feed
        p._raw(b"\x1d\x56\x42\x00") # GS V B — partial cut