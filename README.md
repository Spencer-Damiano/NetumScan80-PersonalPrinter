# 🧾 Receipt Printer Task Manager

> Work in progress. Goal is a simple one-stop solution to print tasks and agendas to a thermal receipt printer — something physical instead of another screen notification.

Inspired by [CodingWithLewis/ReceiptPrinterAgent](https://github.com/CodingWithLewis/ReceiptPrinterAgent)

---

## Hardware

NetumScan NS8360 80mm POS Thermal Receipt Printer

## Driver

Download from [netumscan.com/pages/software-drivers](https://netumscan.com/pages/software-drivers) under Thermal Printers 80mm. Follow instructions there.

> The manual links to `www.cnfujun.com/d/33` — skip it, it's unreliable.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```python
from escpos.printer import Win32Raw

p = Win32Raw("POS-80", profile="NT-80-V-UL")
p.text("Hello, it works!\n")
p.cut()
```

## Ethernet (coming later)

The NS8360 has an Ethernet port. Once on your network, any device can print to it over TCP port 9100.

```python
from escpos.printer import Network

p = Network("192.168.1.x", profile="NT-80-V-UL")
p.text("Hello from the network!\n")
p.cut()
```