import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.receipt import Receipt

lorem = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim "
    "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea"
)

limits = [100, 150, 200]

for limit in limits:
    r = Receipt(
        title=f"{limit} char limit test",
        description=lorem[:limit],
        priority=1,
    )
    print(r.preview())   # terminal preview before printing
    print()

# Uncomment to print all three:
for limit in limits:
    Receipt(title=f"{limit} char limit test", description=lorem[:limit], priority=1).print()