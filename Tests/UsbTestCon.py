from escpos.printer import Win32Raw

p = Win32Raw("POS-80", profile="NT-80-V-UL")
p.text("Hello, it works!\n")
p.cut()