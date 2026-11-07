#!/usr/bin/env python3
"""List which slides changed between two versions of a deck [A10]. Read-only.

usage: python3 deck_diff.py NEW.pptx [OLD.pptx]
With one argument, OLD is the newest earlier version beside NEW (same name apart from a version suffix).
Prints changed, added and removed slides, then the changed slides' text side by side, so a review can
confirm that only the requested slides moved. Python 3.8+ standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks"))
import guard  # noqa: E402


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    new = argv[1]
    old = argv[2] if len(argv) > 2 else guard.previous_version(new)
    if not old:
        print("No earlier version found beside %s; pass it explicitly." % os.path.basename(new))
        return 1
    print("Comparing %s -> %s" % (os.path.basename(old), os.path.basename(new)))
    changes = guard.deck_changes(old, new)
    if not changes:
        print("No slide text changed.")
        return 0
    for c in changes:
        print("- " + c)
    a, b = guard.slide_texts(old), guard.slide_texts(new)
    for c in changes:
        if c.startswith("changed "):
            for n in c[len("changed "):].split(", "):
                i = int(n) - 1
                print("\nSlide %s now: %s" % (n, b[i][:300] if i < len(b) else ""))
                if i < len(a):
                    print("Slide %s was: %s" % (n, a[i][:300]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
