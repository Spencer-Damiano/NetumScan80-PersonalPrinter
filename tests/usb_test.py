"""
tests/usb_test.py — Smoke test for USB printer connection.

Usage:
    python tests/usb_test.py
"""

from escpos.printer import Win32Raw

p = Win32Raw("POS-80", profile="NT-80-V-UL")
p.text("Hello from USB!\n")
p.cut()
