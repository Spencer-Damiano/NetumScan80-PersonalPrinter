from escpos.printer import Win32Raw

p = Win32Raw("POS-80", profile="NT-80-V-UL")

# ── Printer geometry ──────────────────────────────────────────────────────────
# Total receipt: 100mm
# Top feed (dead space): ~15mm  ← trying to suppress this
# Bottom feed (dead space): ~5mm ← trying to suppress this
# Target printable content: ~80mm
#
# Font A: 48 chars/line, line height ~3.4mm at ESC 3 0x18 spacing
# 80mm / 3.4mm ≈ 23–24 lines of content
# ─────────────────────────────────────────────────────────────────────────────

CHAR_WIDTH = 48
LINE_COUNT = 21  # tune this to fill the 80mm content window

# ── Reset printer to clean state ──────────────────────────────────────────────
p._raw(b"\x1b\x40")         # ESC @ — full printer reset

# ── Suppress top margin ───────────────────────────────────────────────────────
# Try zeroing the top-of-form feed that many ESC/POS printers apply
# before the first printable character.
p._raw(b"\x1b\x33\x00")     # ESC 3 0 — momentarily set spacing to 0 (may flush the top feed)
p._raw(b"\x1b\x33\x18")     # ESC 3 24 — restore to 24/180" (~3.4mm) for readable line spacing

# ── Content ───────────────────────────────────────────────────────────────────
BORDER = "=" * CHAR_WIDTH

p.text(BORDER + "\n")
p.text(f"{'80MM SQUARE TEST':^{CHAR_WIDTH}}\n")
p.text(BORDER + "\n")

for i in range(4, LINE_COUNT):
    label = f"line {i:02}"
    p.text(f"{label:<{CHAR_WIDTH}}\n")

p.text(BORDER + "\n")

# ── Minimal bottom feed before cut ───────────────────────────────────────────
p._raw(b"\x1b\x64\x00")     # ESC d 0 — feed 0 extra lines (minimum bottom margin)
p._raw(b"\x1d\x56\x42\x00") # GS V B 0 — partial cut