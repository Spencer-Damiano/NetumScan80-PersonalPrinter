from escpos.printer import Network

p = Network("192.168.1.x", profile="NT-80-V-UL") # ADD OWN IP ADDRESS HERE
p.text("Hello from the network!\n")
p.cut()