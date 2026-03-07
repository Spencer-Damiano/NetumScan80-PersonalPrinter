"""
tests/square_grid_test.py — Printer geometry and line-spacing calibration test.

Prints a bordered grid to verify character width, line height, and top/bottom
feed margins on the NS8360.

Usage:
    python tests/square_grid_test.py
"""

from escpos.printer import Win32Raw

# ── Geometry ──────────────────────────────────────────────────────────────────
# Total receipt: ~100 mm
# Top feed (dead space):    ~15 mm
# Bottom feed (dead space):  ~5 mm
# Target printable content: ~80 mm
#
# Font A: 48 chars/line, line height ~3.4 mm at ESC 3 0x18 spacing
# 80 mm / 3.4 mm ≈ 23–24 lines of content
# ─────────────────────────────────────────────────────────────────────────────

CHAR_WIDTH = 48
LINE_COUNT = 21   # tune to fill the ~80 mm content window
BORDER     = "=" * CHAR_WIDTH

p = Win32Raw("POS-80", profile="NT-80-V-UL")

p._raw(b"\x1b\x40")          # ESC @    — full printer reset
p._raw(b"\x1b\x33\x00")      # ESC 3 0  — suppress top feed
p._raw(b"\x1b\x33\x18")      # ESC 3 24 — restore 3.4 mm line spacing

p.text(BORDER + "\n")
p.text(f"{'80MM SQUARE TEST':^{CHAR_WIDTH}}\n")
p.text(BORDER + "\n")

for i in range(4, LINE_COUNT):
    p.text(f"{'line ' + f'{i:02}':<{CHAR_WIDTH}}\n")

p.text(BORDER + "\n")

p._raw(b"\x1b\x64\x00")      # ESC d 0  — minimum bottom feed
p._raw(b"\x1d\x56\x42\x00")  # GS V B   — partial cut
