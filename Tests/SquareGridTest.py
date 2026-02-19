from escpos.printer import Win32Raw

p = Win32Raw("POS-80", profile="NT-80-V-UL")

# Target: ~80mm tall receipt
# Default font line height is roughly 3.5-4mm
# 80mm / ~3.75mm per line ≈ 21 lines (including the cut margin)
# Adjust LINE_COUNT up or down based on what prints

LINE_COUNT = 21

p.text("=" * 32 + "\n")           # line 1  - top border
p.text(f"  80MM LENGTH TEST\n")   # line 2
p.text("=" * 32 + "\n")           # line 3

for i in range(4, LINE_COUNT):
    p.text(f"  line {i:02}\n")

p.text("=" * 32 + "\n")           # bottom border
p.cut()