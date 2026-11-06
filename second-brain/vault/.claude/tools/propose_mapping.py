#!/usr/bin/env python3
"""Propose where existing topic-folder notes sit in the numbered taxonomy. Moves nothing.

usage: python3 propose_mapping.py VAULT [--os-dir 00-Operating-System]
Writes 01-Inbox/Folder Mapping - Proposed.md. An approved proposal (status: approved) is never overwritten.
Engagement names come from the vault's own active-areas.md, read locally. Python 3.8+ standard library only.
"""
import argparse
import datetime
import os
import re

OUT_REL = os.path.join("01-Inbox", "Folder Mapping - Proposed.md")
FOLDER_RULES = [  # (pattern on folder name, default destination parent, why)
    (r"personal|growth|\bself\b|health|fitness|journal", "05-Self", "personal growth belongs with reflection and life notes"),
    (r"invest|equit|stock|portfolio", "06-Learn", "economics concepts are knowledge; equity notes are routed to 04-Invest note by note"),
    (r"strateg|business", "06-Learn", "frameworks and business knowledge; engagement notes are routed to 03-Work note by note"),
    (r"artificial|intelligence|\bai\b", "06-Learn", "AI knowledge; tool, prompt and setup notes are routed to 08-Library"),
    (r"histor|philosoph|politic|govern|econom|science|culture|book", "06-Learn", "subject knowledge"),
]
EQUITY_HINT = re.compile(r"(?i)\b(thesis|action card|verdict|portfolio|ticker|stock|nse|bse|nasdaq|nyse|holding)\b")
LIBRARY_HINT = re.compile(r"(?i)(framework|template|playbook|checklist|toolkit|prompt|claude|mcp|setup|workflow|agent|obsidian)")
DEFAULT_WELCOME = re.compile(r"This is your new \*?vault\*?", re.I)


def read_head(path, n=4096):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(n)
    except OSError:
        return ""


def engagement_names(os_dir):
    """Map clean folder name -> list of match variants, from active-areas.md client and civic sections."""
    text = read_head(os.path.join(os_dir, "active-areas.md"), 10 ** 7)
    out, section = {}, ""
    for ln in text.splitlines():
        h2 = re.match(r"^## (.*)$", ln)
        if h2:
            section = h2.group(1).lower()
            continue
        if not ("client" in section or "independent" in section or "civic" in section):
            continue
        h = re.match(r"^### (?:\d+\.\s*)?(.+)$", ln)
        if not h:
            continue
        title = h.group(1).strip()
        head = re.split(r"\s*\(|,", title)[0].strip()
        variants = set()
        for part in re.split(r"\s*/\s*", head):
            if part:
                variants.add(part.strip())
        for inner in re.findall(r"\(([^)]*)\)", title):
            for part in re.split(r"[;,]", inner):
                part = part.strip()
                if part and len(part.split()) <= 4 and not re.search(r"\d", part):
                    variants.add(part)
        folder = re.sub(r"[\\/:*?\"<>|]+", "-", head).strip(" -") or title[:40]
        out[folder] = sorted(v for v in variants if len(v) >= 2)
    return out


def mentions(name, haystack):
    if len(name) <= 4 and name.upper() == name:
        return re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(name), haystack) is not None
    return re.search(r"(?i)(?<![a-z])%s(?![a-z])" % re.escape(name), haystack) is not None


def propose(vault, os_name):
    os_dir = os.path.join(vault, os_name)
    engagements = engagement_names(os_dir)
    folders, rows, collisions = [], {}, {}
    for base, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                collisions.setdefault(f.lower(), []).append(os.path.relpath(os.path.join(base, f), vault))
    for name in sorted(os.listdir(vault)):
        full = os.path.join(vault, name)
        if not os.path.isdir(full) or name.startswith(".") or name == os_name or re.match(r"^\d{2}-", name):
            continue
        parent, why = "", "no rule matched; left for your call"
        for rx, dest, reason in FOLDER_RULES:
            if re.search(rx, name, flags=re.I):
                parent, why = dest, reason
                break
        folders.append((name, ("%s/%s" % (parent, name)) if parent else "stay", why))
        items = []
        for base, dirs, files in os.walk(full):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                path = os.path.join(base, f)
                rel = os.path.relpath(path, vault)
                sub = os.path.relpath(base, full)
                hay = f + "\n" + read_head(path)
                dest, reason, conf = (("%s/%s%s" % (parent, name, "" if sub == "." else "/" + sub)) if parent else "",
                                      why, "rule" if parent else "review")
                hits = {}
                for folder, variants in engagements.items():
                    n = sum(1 for v in variants if mentions(v, hay))
                    if n:
                        hits[folder] = n
                if hits and re.search(r"strateg|business|politic|govern", name, flags=re.I):
                    best = max(hits, key=hits.get)
                    dest, reason = "03-Work/%s" % best, "mentions the %s engagement" % best
                    conf = "keyword" if len(hits) == 1 else "review"
                elif re.search(r"invest|equit|stock", name, flags=re.I) and EQUITY_HINT.search(hay):
                    dest, reason, conf = "04-Invest/Theses", "equity research note", "keyword"
                elif LIBRARY_HINT.search(f):
                    target = "08-Library/Prompts and Tools" if re.search(r"(?i)prompt|claude|mcp|setup|workflow|agent|obsidian", f) \
                        else "08-Library/Frameworks"
                    dest, reason, conf = target, "reusable tool or framework", "keyword"
                move = "yes" if dest and conf != "review" else "no"
                items.append((rel, move, dest or "stay", reason, conf))
        rows[name] = items
    root_rows = []
    for f in sorted(os.listdir(vault)):
        path = os.path.join(vault, f)
        if not (os.path.isfile(path) and f.endswith(".md")) or f in ("CLAUDE.md", "Home.md"):
            continue
        if DEFAULT_WELCOME.search(read_head(path)):
            root_rows.append((f, "yes", "99-Archive", "default Obsidian welcome note", "rule"))
        else:
            root_rows.append((f, "no", "stay", "root note; keep as a front page and link it from Home.md", "review"))
    dupes = {k: v for k, v in collisions.items() if len(v) > 1}
    return folders, rows, root_rows, dupes


def write(vault, os_name):
    out = os.path.join(vault, OUT_REL)
    try:
        with open(out, encoding="utf-8") as fh:
            if re.search(r"^status:\s*approved\s*$", fh.read(2000), flags=re.M):
                print("Folder mapping: an approved proposal exists; left unchanged.")
                return
    except OSError:
        pass
    folders, rows, root_rows, dupes = propose(vault, os_name)
    today = datetime.date.today().isoformat()
    L = ["---", "type: proposal", "status: proposed", "generated: %s" % today, "---",
         "# Folder mapping (proposed, nothing has moved)", "",
         "Your topic folders stay exactly where they are until you approve. The engine already works with them: the "
         "installer pointed the work, invest, self and learn rules at these folders.", "",
         "To approve: edit any row (change Move? to no, or change the destination), set `status: approved` above, "
         "then run `python3 .claude/tools/apply_mapping.py \"<vault path>\"` to preview and add `--apply` to move. "
         "Rows marked review default to no.", "",
         "## Folder level", "", "| Existing folder | Proposed home | Why |", "|---|---|---|"]
    for name, dest, why in folders:
        L.append("| %s | `%s` | %s |" % (name, dest, why))
    L += ["", "Alternative: keep every topic folder as it is and approve only the rows that clearly belong in 03-Work, "
          "04-Invest or 08-Library.", ""]
    for name, items in rows.items():
        L += ["## %s" % name, "", "| Note | Move? | Proposed destination | Why | Confidence |", "|---|---|---|---|---|"]
        if not items:
            L.append("| (no notes) | no | stay | empty folder | rule |")
        for rel, move, dest, reason, conf in items:
            L.append("| `%s` | %s | `%s` | %s | %s |" % (rel, move, dest, reason, conf))
        L.append("")
    L += ["## Notes at the vault root", "", "| Note | Move? | Proposed destination | Why | Confidence |",
          "|---|---|---|---|---|"]
    for rel, move, dest, reason, conf in root_rows:
        L.append("| `%s` | %s | `%s` | %s | %s |" % (rel, move, dest, reason, conf))
    if dupes:
        L += ["", "## Duplicate note names (links by name are ambiguous; rename one of each pair)", ""]
        for _, paths in sorted(dupes.items()):
            L.append("- " + "; ".join("`%s`" % p for p in paths))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    total = sum(len(v) for v in rows.values())
    moves = sum(1 for v in rows.values() for r in v if r[1] == "yes")
    print("Folder mapping: %d note(s) across %d folder(s); %d proposed moves; written to %s"
          % (total, len(rows), moves, OUT_REL))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--os-dir", default="00-Operating-System")
    a = ap.parse_args()
    write(os.path.abspath(os.path.expanduser(a.vault)), a.os_dir)
