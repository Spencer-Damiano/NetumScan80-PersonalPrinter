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

# ── Layout constants ──────────────────────────────────────────────────────────
CHAR_WIDTH   = 48
MAX_LINES    = 20
CHAR_LIMIT   = CHAR_WIDTH * MAX_LINES  # hard ceiling, ~960 chars
BORDER       = "=" * CHAR_WIDTH
THIN_BORDER  = "-" * CHAR_WIDTH


class Receipt:
    """
    A single-task receipt.

    Parameters
    ----------
    title       : str  — task title, printed in ALL CAPS and centered
    description : str  — body text, word-wrapped at CHAR_WIDTH, max MAX_LINES lines
    priority    : int  — 0 (Future/Breakdown), 1 (Low), 2 (Medium), 3 (High)
    printer_name: str  — Windows printer name (default "POS-80")
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

        self.title        = title.upper()
        self.description  = description[:CHAR_LIMIT]
        self.priority     = priority
        self.priority_label = PRIORITY_LABELS[priority]
        self.printer_name = printer_name
        self.timestamp    = datetime.now().strftime("%Y-%m-%d  %H:%M")

    def _build_lines(self) -> list[str]:
        """Return the full list of text lines that make up the receipt body."""
        wrapped = textwrap.wrap(self.description, width=CHAR_WIDTH)

        # Enforce MAX_LINES on the description
        if len(wrapped) > MAX_LINES:
            wrapped = wrapped[:MAX_LINES]
            # Mark truncation on the last line
            last = wrapped[-1]
            wrapped[-1] = last[: CHAR_WIDTH - 3].rstrip() + "..."

        lines = []

        # ── Header ────────────────────────────────────────────────────────────
        lines.append(BORDER)
        lines.append(f"{self.title:^{CHAR_WIDTH}}")
        lines.append(THIN_BORDER)
        lines.append(f"{'PRIORITY: ' + self.priority_label:^{CHAR_WIDTH}}")
        lines.append(BORDER)

        # ── Body ──────────────────────────────────────────────────────────────
        lines.append("")
        lines.extend(wrapped)
        lines.append("")

        # ── Footer ────────────────────────────────────────────────────────────
        lines.append(THIN_BORDER)
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