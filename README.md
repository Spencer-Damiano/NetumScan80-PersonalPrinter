# 🧾 Receipt Printer Task Manager

> Work in progress. Goal is a simple one-stop solution to print tasks and agendas to a thermal receipt printer — something physical instead of another screen notification.

Inspired by [CodingWithLewis/ReceiptPrinterAgent](https://github.com/CodingWithLewis/ReceiptPrinterAgent)

---

## Hardware

NetumScan NS8360 80mm POS Thermal Receipt Printer

## Driver

Download from [netumscan.com/pages/software-drivers](https://netumscan.com/pages/software-drivers) under **Thermal Printers 80mm** and follow the instructions there.

> The manual links to `www.cnfujun.com/d/33` — skip it, it's unreliable.

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Project structure

```
receipt-printer/
├── core/
│   ├── receipt.py        # ESC/POS text renderer
│   └── html_receipt.py   # HTML → PNG renderer
└── tests/
    ├── usb_test.py        # Smoke test — USB connection
    ├── network_test.py    # Smoke test — Ethernet connection
    ├── square_grid_test.py# Geometry / line-spacing calibration
    ├── char_limit.py      # Marked lorem ruler for char-limit testing
    ├── print_preview.py   # Preview receipts in browser / image viewer
    ├── print_one.py       # Print a single receipt
    └── print_all.py       # Print the full test suite
```

---

## Usage

### Text receipt (ESC/POS)

```python
from core.receipt import Receipt

r = Receipt(
    title="Buy Groceries",
    description="Pick up milk, eggs, bread, and coffee before 6pm.",
    priority=1,   # 0 Future  1 Low  2 Medium  3 High
)

print(r.preview())  # inspect in terminal
r.print()           # send to printer
```

### HTML → PNG receipt

```python
from core.html_receipt import render_png

render_png("Fix Login Bug", "Check the token validation logic.", priority=3, path="out.png")
```

### Ethernet (coming later)

The NS8360 has an Ethernet port. Once on your network, any device can print to it over TCP port 9100.

```python
from escpos.printer import Network

p = Network("192.168.1.x", profile="NT-80-V-UL")  # ← your printer's IP
p.text("Hello from the network!\n")
p.cut()
```