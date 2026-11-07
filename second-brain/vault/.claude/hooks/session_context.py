#!/usr/bin/env python3
"""SessionStart hook: live context plus a digest of the operating-system files.

identity.md and output-standards.md load in full through the @imports in CLAUDE.md (they are too large
for hook output, which Claude Code caps at about 10,000 characters). This hook adds, within that cap:
  1. live context: date and time, today's must-dos, inbox count, open tasks due, reviews due;
  2. a digest of the other four files: routing implication, closed debates, the template index (T1..Tn)
     and one status line per active area; plus each file's freshness.
Never fails the session: any error prints nothing and exits 0. Python 3.8+ standard library only.
"""
import datetime
import json
import os
import re
import sys
import time

BUDGET = 9500
OS_FILES = ["identity.md", "active-areas.md", "output-standards.md", "thinking-patterns.md",
            "templates.md", "recurring-asks.md"]
SKIP_DIRS = {".obsidian", ".claude", ".git", ".trash", "node_modules", "99-Archive"}
DELIVERABLE_EXTS = (".pptx", ".xlsx", ".docx", ".pdf")


def root_dir():
    return os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def os_dir_name(root):
    try:
        with open(os.path.join(root, ".claude", "guard", "config.json"), encoding="utf-8") as fh:
            return json.load(fh).get("os_dir", "00-Operating-System")
    except Exception:
        return "00-Operating-System"


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return ""


def frontmatter_value(text, key):
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.S)
    if not m:
        return ""
    for ln in m.group(1).splitlines():
        if ln.startswith(key + ":"):
            return ln.split(":", 1)[1].strip().strip("\"'")
    return ""


def section_lines(text, heading_rx, stop_rx=r"^#{1,2} "):
    out, on = [], False
    for ln in text.splitlines():
        if re.match(heading_rx, ln):
            on = True
            continue
        if on and re.match(stop_rx, ln):
            break
        if on:
            out.append(ln)
    return out


def live_context(root, today):
    lines = ["## Live context (session start)",
             "- Now: %s" % datetime.datetime.now().strftime("%A %d %B %Y, %H:%M")]
    daily = os.path.join(root, "02-Daily", today.isoformat() + ".md")
    if os.path.exists(daily):
        must = section_lines(read(daily), r"^#{2,3} Must do", r"^#{2,3} ")
        items = [m.strip() for m in must if m.strip().startswith("- [")][:6]
        lines.append("- Today's note: 02-Daily/%s.md%s" % (today.isoformat(), "" if items else " (no must-dos yet)"))
        lines += ["  " + i for i in items]
    else:
        lines.append("- No daily note for today. If the owner is starting the day, offer /today.")
    inbox = os.path.join(root, "01-Inbox")
    if os.path.isdir(inbox):
        n = len([f for f in os.listdir(inbox) if f.endswith(".md") and not f.startswith(".")])
        lines.append("- Inbox: %d item(s)%s" % (n, " (over ten: suggest /ingest)" if n > 10 else ""))
    due, reviews, scanned, start = 0, [], 0, time.time()
    iso = today.isoformat()
    deliverables = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if f.lower().endswith(DELIVERABLE_EXTS) and not f.startswith("~$"):
                fp = os.path.join(base, f)
                try:
                    deliverables.append((os.path.getmtime(fp), os.path.relpath(fp, root)))
                except OSError:
                    pass
            if not f.endswith(".md"):
                continue
            scanned += 1
            if scanned > 6000 or time.time() - start > 1.5:
                break
            text = read(os.path.join(base, f))
            for m in re.finditer(r"^\s*- \[ \].*?\U0001F4C5\s*(\d{4}-\d{2}-\d{2})", text, flags=re.M):
                if m.group(1) <= iso:
                    due += 1
            rv = frontmatter_value(text, "review_on")
            if re.match(r"\d{4}-\d{2}-\d{2}$", rv) and rv <= iso:
                reviews.append("[[%s]] (%s)" % (f[:-3], rv))
    if due:
        lines.append("- Open tasks due today or overdue: %d (see Home)" % due)
    if reviews:
        lines.append("- Reviews due: " + ", ".join(sorted(reviews)[:8]))
    if deliverables:
        lines.append("- Latest working files (M6: build on the newest version; say which):")
        for mt, rel in sorted(deliverables, reverse=True)[:8]:
            lines.append("  %s  %s" % (datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M"), rel))
    return lines


def digest(root, osd):
    out = ["## Operating-system digest (%s)" % osd,
           "identity.md and output-standards.md are loaded in full via CLAUDE.md. Read any other file in full "
           "whenever the task touches it."]
    base = os.path.join(root, osd)
    fresh, missing = [], []
    texts = {}
    for name in OS_FILES:
        t = read(os.path.join(base, name))
        texts[name] = t
        if not t:
            missing.append(name)
        else:
            fresh.append("%s %s" % (name[:-3], frontmatter_value(t, "updated") or "?"))
    out.append("- Updated: " + "; ".join(fresh))
    if missing:
        out.append("- MISSING: " + ", ".join(missing) + ". Tell the owner; do not guess their contents.")
    ra = section_lines(texts.get("recurring-asks.md", ""), r"^## Routing implication", r"^## ")
    ra = [ln for ln in ra if ln.strip() and not ln.startswith("Related:")]
    if ra:
        out.append("### Routing implication (recurring-asks.md)")
        out += ra
    cd = section_lines(texts.get("thinking-patterns.md", ""), r"^## Closed debates", r"^## ")
    cd = [ln for ln in cd if ln.strip()]
    if cd:
        out.append("### Closed debates, never reopen (thinking-patterns.md)")
        out += cd
    tix = []
    for ln in texts.get("templates.md", "").splitlines():
        m = re.match(r"^### (\d+)\.\s+(.*)$", ln)
        if m:
            title = re.sub(r"\s*\[.*?\]\s*$", "", m.group(2))
            tix.append("T%s %s" % (m.group(1), title[:60]))
    if tix:
        out.append("### Template index (templates.md; cite by T-number)")
        out.append("; ".join(tix))
    areas = []
    current = ""
    for ln in texts.get("active-areas.md", "").splitlines():
        h = re.match(r"^#{3,4} (.*)$", ln)
        if h:
            current = h.group(1).strip()
            continue
        s = re.match(r"^- Status(?:\s*\([^)]*\))?:\s*(.*)$", ln)
        if s and current:
            status = s.group(1).strip()
            areas.append("- %s: %s" % (current[:60], status[:150] + ("..." if len(status) > 150 else "")))
            current = ""
    if areas:
        out.append("### Active areas, status (active-areas.md)")
        out += areas
    return out


def main():
    root = root_dir()
    osd = os_dir_name(root)
    today = datetime.date.today()
    try:
        live = live_context(root, today)
    except Exception:
        live = []
    try:
        dig = digest(root, osd)
    except Exception:
        dig = []
    claude_md = read(os.path.join(root, "CLAUDE.md"))
    warn = []
    if claude_md and ("@%s/identity.md" % osd) not in claude_md:
        warn = ["- WARNING: CLAUDE.md does not import %s/identity.md and output-standards.md. "
                "Offer /onboard to merge CLAUDE.md.kit-new." % osd]
    text = "\n".join(live + warn + [""] + dig)
    if len(text) > BUDGET:
        keep = "\n".join(live + warn + [""])
        room = BUDGET - len(keep) - 80
        text = keep + "\n".join(dig)[:max(0, room)] + "\n[digest truncated; read the OS files directly]"
    sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
