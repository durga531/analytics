#!/usr/bin/env python3
"""Apply an APPROVED folder mapping. Dry run by default; --apply moves files. Never overwrites, never deletes.

usage: python3 apply_mapping.py VAULT [--apply]
Reads 01-Inbox/Folder Mapping - Proposed.md, which must carry `status: approved`. Moves only rows whose Move?
cell is yes. Logs every move to 99-Archive/Moves Log.md and lists path-style links that may need fixing.
Python 3.8+ standard library only.
"""
import argparse
import datetime
import os
import re

PROPOSAL = os.path.join("01-Inbox", "Folder Mapping - Proposed.md")
LOG = os.path.join("99-Archive", "Moves Log.md")
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(yes|no)\s*\|\s*`([^`]+)`\s*\|", re.I)
PROTECTED = (".obsidian", ".claude", "00-Operating-System")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    vault = os.path.abspath(os.path.expanduser(a.vault))
    path = os.path.join(vault, PROPOSAL)
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        raise SystemExit("No proposal found at %s. Run propose_mapping.py first." % PROPOSAL)
    if not re.search(r"^status:\s*approved\s*$", text, flags=re.M):
        raise SystemExit("The proposal is not approved. Set `status: approved` in its frontmatter first.")
    plan, problems = [], []
    for ln in text.splitlines():
        m = ROW.match(ln)
        if not m or m.group(2).lower() != "yes":
            continue
        src_rel, dest_dir_rel = m.group(1), m.group(3).rstrip("/")
        if dest_dir_rel == "stay":
            continue
        src = os.path.normpath(os.path.join(vault, src_rel))
        dest = os.path.normpath(os.path.join(vault, dest_dir_rel, os.path.basename(src)))
        if not src.startswith(vault + os.sep) or not dest.startswith(vault + os.sep):
            problems.append("outside the vault: %s" % src_rel)
        elif any(os.path.relpath(p, vault).split(os.sep)[0] in PROTECTED for p in (src, dest)):
            problems.append("protected path: %s" % src_rel)
        elif not os.path.isfile(src):
            problems.append("missing source: %s" % src_rel)
        elif os.path.exists(dest):
            problems.append("destination exists, skipped: %s" % os.path.relpath(dest, vault))
        else:
            plan.append((src, dest))
    for src, dest in plan:
        print("%s %s -> %s" % ("move" if a.apply else "would move", os.path.relpath(src, vault),
                               os.path.relpath(dest, vault)))
    for p in problems:
        print("skip: " + p)
    if not a.apply:
        print("Dry run: %d move(s). Add --apply to move them." % len(plan))
        return
    moved = []
    for src, dest in plan:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.rename(src, dest)
        moved.append((src, dest))
    if moved:
        log = os.path.join(vault, LOG)
        new = not os.path.exists(log)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        with open(log, "a", encoding="utf-8") as fh:
            if new:
                fh.write("# Moves log\n\n| Date | From | To |\n|---|---|---|\n")
            today = datetime.date.today().isoformat()
            for src, dest in moved:
                fh.write("| %s | `%s` | `%s` |\n" % (today, os.path.relpath(src, vault), os.path.relpath(dest, vault)))
    stale = []
    olds = [os.path.relpath(s, vault)[:-3] for s, _ in moved]
    for base, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            with open(os.path.join(base, f), encoding="utf-8", errors="replace") as fh:
                body = fh.read()
            for old in olds:
                if "[[%s" % old in body or "](%s" % old.replace(" ", "%20") in body:
                    stale.append("%s links to %s by path" % (os.path.relpath(os.path.join(base, f), vault), old))
    print("Moved %d note(s); logged in %s." % (len(moved), LOG))
    for s in stale:
        print("check link: " + s)
    if not stale:
        print("No path-style links to the moved notes; name links keep working.")


if __name__ == "__main__":
    main()
