"""
Tests/CharLimitTest.py — Generate a marked lorem string for char limit testing.

Each marker shows the exact character count at that point in the string,
factoring in the length of the marker text itself.

Usage:
    python Tests/CharLimitTest.py
    python Tests/CharLimitTest.py 150   ← generate only first N chars

The output can be pasted directly into the print preview custom option,
or the build() function can be imported and used programmatically.
"""

import sys
import os

# ── Raw lorem source ──────────────────────────────────────────────────────────
_LOREM = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim "
    "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat "
    "cupidatat non proident sunt in culpa qui officia deserunt mollit anim id "
    "est laborum sed perspiciatis unde omnis iste natus error sit voluptatem "
    "accusantium doloremque laudantium totam rem aperiam eaque ipsa quae ab "
    "illo inventore veritatis et quasi architecto beatae vitae dicta explicabo "
    "nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit "
    "sed quia consequuntur magni dolores eos qui ratione voluptatem sequi "
    "nesciunt neque porro quisquam est qui dolorem ipsum quia dolor sit amet "
    "consectetur adipisci velit sed quia non numquam eius modi tempora incidunt "
    "ut labore et dolore magnam aliquam quaerat voluptatem ut enim ad minima "
    "veniam quis nostrum exercitationem ullam corporis suscipit laboriosam nisi "
    "ut aliquid ex ea commodi consequatur quis autem vel eum iure reprehenderit "
    "qui in ea voluptate velit esse quam nihil molestiae consequatur vel illum "
    "qui dolorem eum fugiat quo voluptas nulla pariatur at vero eos et accusamus "
    "et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum "
    "deleniti atque corrupti quos dolores et quas molestias excepturi occaecati"
)


def build(limit: int = 2000, interval: int = 25) -> str:
    """
    Build a lorem string with count markers every `interval` characters.
    The marker text itself is factored into the running count so markers
    always reflect the true position in the final string.

    Args:
        limit:    Stop after this many total characters (including markers).
        interval: Insert a marker every this many characters.

    Returns:
        The marked string.
    """
    # Repeat lorem source if it's shorter than the requested limit
    source = (_LOREM + " ") * (limit // len(_LOREM) + 2)

    result      = ""
    count       = 0
    next_mark   = interval
    source_idx  = 0

    while count < limit and source_idx < len(source):
        char = source[source_idx]
        source_idx += 1

        result += char
        count  += 1

        if count == next_mark:
            marker  = f"[{next_mark}]"
            result += marker
            count  += len(marker)
            next_mark += interval

    return result[:limit]


if __name__ == "__main__":
    # Optional: pass a char limit as a command-line argument
    # e.g.  python Tests/CharLimitTest.py 150
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    ruler = build(limit)
    print(ruler)
    print(f"\nTotal chars: {len(ruler)}")