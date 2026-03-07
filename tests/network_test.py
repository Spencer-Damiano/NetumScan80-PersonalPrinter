"""
tests/network_test.py — Smoke test for Ethernet printer connection.

Set the IP address of your NS8360 before running.

Usage:
    python tests/network_test.py
"""

from escpos.printer import Network

p = Network("192.168.1.x", profile="NT-80-V-UL")  # ← replace with your printer's IP
p.text("Hello from the network!\n")
p.cut()
