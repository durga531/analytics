#!/usr/bin/env python3
"""Second-brain guard: enforces the owner's hard mandates as Claude Code hooks.

Modes (first argument):
  pre      PreToolUse on Write|Edit|MultiEdit|NotebookEdit: block content that breaks a mandate
  post     PostToolUse on Bash: lint files the command just wrote (text and pptx/docx/xlsx)
  stop     Stop: check the final chat answer; ask for a rewrite once if it breaks a mandate
  prompt   UserPromptSubmit: inject the build preflight (M6), mandate reminders and the FORGE trigger
  lint     CLI: python3 guard.py lint FILE...   (same checks as post, prints a report, exit 1 on violations)
  extract  CLI: python3 guard.py extract VAULT  (rebuild kill-list.txt and fact-base-numbers.txt from the OS files)

Mandates (see CLAUDE.md): M1 no em dashes; M2 equity verdicts BUY / ACCUMULATE / HOLD / WATCH / AVOID only,
no sell, trim, exit, reduce, stop-loss or tax-loss suggestions; M3 client decks are final decks, no
version-control language; M4 resume numbers only from the locked fact base, kill list never returns.

Fail-safe: hook modes never crash the session. Disable for a while: create .claude/guard/OFF or set SB_GUARD_OFF=1.
Python 3.8+ standard library only.
"""
import fnmatch
import html
import json
import os
import re
import sys
import time
import zipfile

EM_DASH = chr(0x2014)  # built from its code point so this file itself never contains the character
GUARD_DIR = os.path.join(".claude", "guard")
DEFAULT_CONFIG = {
    "os_dir": "00-Operating-System",
    "invest_globs": ["04-Invest/**"],
    "resume_globs": ["**/*resume*", "**/*CV*", "**/*cv.*", "**/*cover letter*", "**/*cover-letter*"],
    "exempt_globs": ["00-Operating-System/**", ".claude/**", "99-Archive/**"],
}
TEXT_EXTS = (".md", ".txt", ".html", ".htm", ".csv", ".json", ".js", ".mjs", ".py", ".tsv")
OFFICE_EXTS = (".pptx", ".docx", ".xlsx")

# ---------------------------------------------------------------- patterns
VERDICT_FIELD = re.compile(
    r"(?i)\b(?:verdict|action|call|recommendation|rating|stance)\b\s*[:|=\-]?\s*[*_`]*\s*"
    r"(strong\s+sell|sell|trim|exit|reduce|book\s+profits?|take\s+profits?)\b")
UPPER_VERDICT = re.compile(r"(?<![\w/-])(STRONG SELL|SELL|TRIM|EXIT|REDUCE)(?![\w/-])")
HOLDING_ACTION = re.compile(
    r"(?i)\b(sell(?:ing)?|trim(?:ming)?|exit(?:ing)?|reduc(?:e|ing)|cut(?:ting)?|lighten(?:ing)?|offload(?:ing)?|dump(?:ing)?)\b"
    r"\s+(?:your|the|this|that|our|some|part\s+of|half\s+of|all\s+of|\d+\s*%\s+of)?\s*(?:the\s+)?"
    r"(?:position|positions|stake|stakes|holding|holdings|exposure|allocation|shares|stock|stocks|name|names|"
    r"units|etf|etfs|fund|funds)\b")
PROFIT_TAKING = re.compile(
    r"(?i)\b(book(?:ing)?\s+(?:partial\s+)?profits?|take\s+(?:partial\s+)?profits?|profit[\s-]booking|"
    r"partial(?:ly)?\s+exit|exit\s+(?:fully|partially|completely)|rotate\s+out\s+of)\b")
STOP_LOSS = re.compile(r"(?i)\b(stop[\s-]?loss(?:es)?|trailing\s+stop|tax[\s-]loss(?:\s+harvest\w*)?)\b")
EQUITY_PROMPT = re.compile(
    r"(?i)\b(stocks?|shares?|equit(?:y|ies)|portfolio|ticker|holdings?|invest(?:ing|ment)?|valuation|"
    r"nse|bse|nasdaq|nyse|action card|mutual funds?|buy levels?)\b")
EQUITY_CONTENT = re.compile(r"(?i)\baction card\b|\bverdict\b")
RESUME_PROMPT = re.compile(
    r"(?i)\b(resume|résumé|cv|curriculum vitae|cover letter|application answers?|"
    r"linkedin (?:summary|headline|about)|job application)\b")
EDIT_PROMPT = re.compile(
    r"(?i)\b(change|fix|update|edit|modify|correct|replace|rework|redo|tweak|amend|remove|add)\b.{0,60}?"
    r"\b(slides?|deck|page|header|title|workbook|sheet|tab|resume|cv|bullets?|exec(?:utive)? summary)\b"
    r"|\bslides?\s+\d+")
BUILD_PROMPT = re.compile(
    r"(?i)\b(deck|slides?|pptx|ppt|powerpoint|storyline|storyboard|playbook|workbook|xlsx|excel|"
    r"docx|resume|cv|rebuild|rewrite|revise|headers?|template|exec(?:utive)? summary)\b")
VERSION_LANGUAGE = [
    (re.compile(r"(?i)\bwhat(?:'s|\s+has)?\s+changed\b"), "what changed"),
    (re.compile(r"(?i)\bwhat\s+moved\b"), "what moved"),
    (re.compile(r"(?i)\bchanges?\s+(?:since|from|vs\.?|versus)\s+(?:v\d|version|the\s+last|last|previous)\b"),
     "changes since a version"),
    (re.compile(r"(?i)\bversion\s+(?:history|notes?|log)\b"), "version notes"),
    (re.compile(r"(?i)\bchange\s?log\b"), "change log"),
    (re.compile(r"(?i)\bversion\s+\d"), "version number"),
    (re.compile(r"(?<![\w.])v\d+(?:\.\d+)?(?![\w.])"), "version tag such as v5"),
    (re.compile(r"[\[(](?:NEW|New|new|UPDATED|Updated|REVISED|Revised)[\])]"), "new or updated tag"),
    (re.compile(r"(?<![\w-])NEW(?![\w-])"), "NEW tag"),
]
PLACEHOLDERS = [
    (re.compile(r"(?i)\bx{3,}\b"), "xxx placeholder"),
    (re.compile(r"(?i)\bplaceholder\b"), "placeholder text"),
    (re.compile(r"(?i)\bprofile overview\b"), "template placeholder 'Profile overview'"),
    (re.compile(r"(?i)\bclick to (?:add|edit)\b"), "template prompt text"),
    (re.compile(r"(?i)\blorem ipsum\b"), "lorem ipsum"),
    (re.compile(r"(?i)\bdummy (?:subtitle|text|title)\b"), "dummy text"),
]
PERSONA_LEAK = re.compile(
    r"(?i)\b(senior (?:mckinsey|bain|bcg) partner|as an ai\b|language model|claude|chatgpt|"
    r"for you and me|kkr partner|hedge[- ]fund partner)\b")
GENERIC_BANNED = ["synergy", "leverage", "holistic", "robust", "seamless", "best-in-class"]
ABBREVIATIONS = ["spec", "specs", "mgmt", "govt", "approx", "mfg", "qty", "dept", "w.r.t.", "yoy%"]
HEDGED_VERBS = re.compile(r"(?i)\b(helping|supporting|assisted in|helped to)\b")
MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
NUMBER_TOKEN = re.compile(
    r"(?<![\w.'’/#-])([$₹€£]\s?)?(\d[\d,]*(?:\.\d+)?)\s?"
    r"(%|x|X|B|bn|Bn|M|Mn|mn|K|k|Cr|cr|crore|lakh|L)?(\+)?(?![\w])")
NUMBER_TOKEN_LOOSE = re.compile(
    r"(?<![\w.])([$\u20b9\u20ac\u00a3]\s?)?(\d[\d,]*(?:\.\d+)?)\s?"
    r"(%|x|X|B|bn|Bn|M|Mn|mn|K|k|Cr|cr|crore|lakh|L)?(\+)?(?![\w])")
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20}


# ---------------------------------------------------------------- helpers
def project_dir(payload=None):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or (payload or {}).get("cwd") or os.getcwd()
    return os.path.abspath(d)


def load_config(root):
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(os.path.join(root, GUARD_DIR, "config.json"), encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    except Exception:
        pass
    return cfg


def guard_off(root):
    return os.environ.get("SB_GUARD_OFF") == "1" or os.path.exists(os.path.join(root, GUARD_DIR, "OFF"))


def rel_path(path, root):
    try:
        rp = os.path.relpath(os.path.abspath(path), root)
    except ValueError:
        rp = path
    return rp.replace(os.sep, "/")


def match_globs(rel, globs):
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    for g in globs or []:
        gl = g.lower()
        if fnmatch.fnmatch(low, gl):
            return True
        if gl.startswith("**/") and fnmatch.fnmatch(base, gl[3:]):
            return True
    return False


def read_lines(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln.rstrip("\n") for ln in fh]
    except Exception:
        return []


def snippet(line, at=None, width=90):
    line = line.strip()
    if at is None or len(line) <= width:
        return line[:width]
    start = max(0, at - width // 2)
    return ("..." if start else "") + line[start:start + width] + "..."


# ---------------------------------------------------------------- checks
def check_em_dash(text, where=""):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        pos = line.find(EM_DASH)
        if pos >= 0:
            out.append("M1 em dash%s line %d: %s" % (where, i, snippet(line, pos)))
    return out


def check_equity(text, where=""):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for rx, label in ((VERDICT_FIELD, "sell-type verdict"), (UPPER_VERDICT, "sell-type verdict"),
                          (HOLDING_ACTION, "sell, trim, exit or reduce suggestion"),
                          (PROFIT_TAKING, "profit-taking or exit suggestion"),
                          (STOP_LOSS, "stop-loss or tax-loss language")):
            m = rx.search(line)
            if m:
                out.append("M2 %s%s line %d: %s" % (label, where, i, snippet(line, m.start())))
                break
    return out


def load_kill_list(root):
    pats = []
    for ln in read_lines(os.path.join(root, GUARD_DIR, "kill-list.txt")):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            pats.append([p.strip().lower() for p in ln.split("&&") if p.strip()])
    return pats


def check_kill_list(text, root, where=""):
    out = []
    pats = load_kill_list(root)
    if not pats:
        return out
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for parts in pats:
            if all(p in low for p in parts):
                out.append("M4 kill-list claim '%s'%s line %d: %s" % (" + ".join(parts), where, i, snippet(line)))
    return out


def norm_number(num, unit):
    try:
        val = float(num.replace(",", ""))
    except ValueError:
        return None, None
    u = (unit or "").lower()
    u = {"bn": "b", "mn": "m", "crore": "cr", "l": "lakh"}.get(u, u)
    return val, u


def load_fact_numbers(root):
    vals, pairs = set(), set()
    for ln in read_lines(os.path.join(root, GUARD_DIR, "fact-base-numbers.txt")):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^([\d.,]+)\s*([a-z%]*)$", ln)
        if not m:
            continue
        v, u = norm_number(m.group(1), m.group(2))
        if v is None:
            continue
        vals.add(v)
        if u:
            pairs.add((v, u))
    return vals, pairs


def check_fact_numbers(text, root, where=""):
    vals, pairs = load_fact_numbers(root)
    if not vals:
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*\d+[.)]\s", line):
            line = re.sub(r"^\s*\d+[.)]\s", "", line)
        for m in NUMBER_TOKEN.finditer(line):
            raw = m.group(2)
            v, u = norm_number(raw, m.group(3))
            if v is None:
                continue
            digits = raw.replace(",", "").replace(".", "")
            if not u and len(digits) == 4 and 1990 <= v <= 2039:
                continue  # a year
            if not u and len(digits) >= 10:
                continue  # a phone number; contact details come from identity.md
            if not u and v <= 31:
                around = line[max(0, m.start() - 12):m.end() + 12].lower()
                if re.search(MONTHS, around):
                    continue  # a calendar day
            if (u and (v, u) in pairs) or (not u and v in vals):
                continue
            out.append("M4 number not in the locked fact base%s line %d: '%s' in: %s"
                       % (where, i, m.group(0).strip(), snippet(line, m.start())))
    return out


def output_rules(root, cfg):
    """Banned and extreme word lists parsed from output-standards.md (private); generic fallback."""
    banned, extreme = list(GENERIC_BANNED), []
    for ln in read_lines(os.path.join(root, cfg.get("os_dir", "00-Operating-System"), "output-standards.md")):
        low = ln.lower()
        if low.startswith("- banned words") or low.startswith("- banned informal words"):
            body = ln.split("):", 1)[-1] if "):" in ln else ln.split(":", 1)[-1]
            body = body.split(". Source")[0].split(". Sources")[0]
            for w in re.split(r",|/", body):
                w = w.strip().strip(".").strip()
                w = re.sub(r"\s*\(.*?\)\s*", " ", w).strip()
                if w and len(w) <= 30:
                    banned.append(w.lower())
        if low.startswith("- no extreme or absolute statements"):
            m = re.search(r"\(([^)]*)\)", ln)
            if m:
                extreme = [w.strip().lower() for w in m.group(1).split(",") if w.strip()]
    return sorted(set(banned)), extreme


def office_text(path):
    """Yield (location, text, is_title) for pptx slides and notes, docx paragraphs, xlsx strings."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if path.lower().endswith(".pptx"):
            def num(n):
                m = re.search(r"(\d+)\.xml$", n)
                return int(m.group(1)) if m else 0
            for n in sorted([n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=num):
                xml = z.read(n).decode("utf-8", "replace")
                for shape in re.findall(r"<p:sp>.*?</p:sp>|<p:sp .*?</p:sp>", xml, flags=re.S):
                    is_title = bool(re.search(r'<p:ph[^>]*type="(?:title|ctrTitle)"', shape))
                    paras = re.findall(r"<a:p>.*?</a:p>|<a:p .*?</a:p>", shape, flags=re.S)
                    text = "\n".join(html.unescape("".join(re.findall(r"<a:t>([^<]*)</a:t>", p))) for p in paras)
                    if text.strip():
                        yield "slide %d" % num(n), text, is_title
            for n in sorted([n for n in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)], key=num):
                xml = z.read(n).decode("utf-8", "replace")
                text = html.unescape(" ".join(re.findall(r"<a:t>([^<]*)</a:t>", xml)))
                if text.strip():
                    yield "notes %d" % num(n), text, False
        elif path.lower().endswith(".docx"):
            xml = z.read("word/document.xml").decode("utf-8", "replace")
            paras = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)
            text = "\n".join(html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))) for p in paras)
            yield "document", text, False
        elif path.lower().endswith(".xlsx"):
            if "xl/sharedStrings.xml" in names:
                xml = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
                yield "shared strings", html.unescape("\n".join(re.findall(r"<t[^>]*>([^<]*)</t>", xml))), False
            errors = 0
            for n in names:
                if re.match(r"xl/worksheets/sheet\d+\.xml$", n):
                    xml = z.read(n).decode("utf-8", "replace")
                    errors += len(re.findall(r't="e"[^>]*>(?:<f>.*?</f>)?<v>#', xml))
                    inline = html.unescape("\n".join(re.findall(r"<is><t[^>]*>([^<]*)</t></is>", xml)))
                    if inline.strip():
                        yield n, inline, False
            if errors:
                yield "formula errors", "__FORMULA_ERRORS__ %d" % errors, False


def office_integrity(path):
    """[C2] The package must be a sound zip whose XML parts all parse; returns an error string or ''."""
    import xml.etree.ElementTree as ET
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad:
                return "corrupt zip member %s" % bad
            for n in z.namelist():
                if n.endswith((".xml", ".rels")):
                    try:
                        ET.fromstring(z.read(n))
                    except ET.ParseError as exc:
                        return "malformed XML in %s (%s)" % (n, exc)
    except zipfile.BadZipFile as exc:
        return "not a valid Office package (%s)" % exc
    except OSError as exc:
        return "cannot read file (%s)" % exc
    return ""


def slide_texts(path):
    """Ordered list of whole-slide texts for a pptx (used by the version diff)."""
    slides = {}
    for loc, text, _ in office_text(path):
        if loc.startswith("slide "):
            n = int(loc.split()[1])
            slides[n] = slides.get(n, "") + "\n" + " ".join(text.split())
    return [slides[k].strip() for k in sorted(slides)]


def version_base(stem):
    return re.sub(r"(?i)([ _-]?v\d+(?:[._]\d+)?|\s*\(\d+\)|[ _-]?copy|[ _-]?final)$", "", stem).strip().lower()


def previous_version(path):
    folder, name = os.path.split(os.path.abspath(path))
    stem, ext = os.path.splitext(name)
    base, best = version_base(stem), None
    try:
        mine = os.path.getmtime(path)
        for f in os.listdir(folder):
            fs, fe = os.path.splitext(f)
            if f == name or fe.lower() != ext.lower() or version_base(fs) != base:
                continue
            fp = os.path.join(folder, f)
            mt = os.path.getmtime(fp)
            if mt <= mine and (best is None or mt > best[0]):
                best = (mt, fp)
    except OSError:
        return None
    return best[1] if best else None


def deck_changes(old, new):
    """[A10] Which slides differ between two versions, for review against the request."""
    import difflib
    a, b = slide_texts(old), slide_texts(new)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "replace":
            out.append("changed %s" % ", ".join(str(j + 1) for j in range(j1, j2)))
        elif tag == "insert":
            out.append("added %s" % ", ".join(str(j + 1) for j in range(j1, j2)))
        elif tag == "delete":
            out.append("removed old %s" % ", ".join(str(i + 1) for i in range(i1, i2)))
    return out


def lint_file(path, root, cfg, context_resume=False):
    """Return (blocking, warnings) for one file."""
    block, warn = [], []
    rel = rel_path(path, root)
    exempt = match_globs(rel, cfg.get("exempt_globs"))
    invest = match_globs(rel, cfg.get("invest_globs")) and not exempt
    resume = (match_globs(rel, cfg.get("resume_globs")) or context_resume) and not exempt
    low = path.lower()
    if low.endswith(OFFICE_EXTS):
        problem = office_integrity(path)
        if problem:
            return ["C2 file would need repair: %s. Rebuild or repair it so it opens cleanly" % problem], []
        try:
            parts = list(office_text(path))
        except Exception as exc:  # noqa: BLE001
            return ["C2 file does not open as a valid Office package (%s); run the repair step" % exc], []
        if low.endswith(".xlsx") and re.search(r"(?i)data[ _-]?request", os.path.basename(path)):
            try:
                with zipfile.ZipFile(path) as z:
                    sheets = len(re.findall(r"<sheet\b", z.read("xl/workbook.xml").decode("utf-8", "replace")))
                if sheets > 2:
                    warn.append("A6 data-request workbook has %d tabs; keep at most two exact tables tabs" % sheets)
            except Exception:  # noqa: BLE001
                pass
        if low.endswith(".pptx"):
            prev = previous_version(path)
            if prev:
                try:
                    changes = deck_changes(prev, path)
                    warn.append("A10 versus %s: %s. Confirm only the requested slides changed"
                                % (os.path.basename(prev), "; ".join(changes) or "no slide text changed"))
                except Exception:  # noqa: BLE001
                    pass
        banned, extreme = output_rules(root, cfg)
        is_deck = low.endswith(".pptx")
        exec_slides = set(loc for loc, text, _ in parts if re.search(r"(?i)executive summary", text))
        for loc, text, is_title in parts:
            if text.startswith("__FORMULA_ERRORS__"):
                warn.append("%d cell(s) hold formula errors; workbooks must have none" % int(text.split()[-1]))
                continue
            where = " (%s)" % loc
            block += check_em_dash(text, where)
            if invest or EQUITY_CONTENT.search(text):
                block += check_equity(text, where)
            if resume:
                block += check_kill_list(text, root, where)
                block += check_fact_numbers(text, root, where)
                if HEDGED_VERBS.search(text):
                    warn.append("hedged ownership verb%s; use outcome-first verbs" % where)
            if is_deck and not loc.startswith("notes"):
                for rx, label in VERSION_LANGUAGE:
                    m = rx.search(text)
                    if m:
                        block.append("M3 version-control language (%s)%s: %s" % (label, where, snippet(text, m.start())))
                        break
                for rx, label in PLACEHOLDERS:
                    m = rx.search(text)
                    if m:
                        block.append("leftover %s%s: %s" % (label, where, snippet(text, m.start())))
                        break
                lowtext = " " + re.sub(r"[^a-z0-9%\- ]", " ", text.lower()) + " "
                hits = [w for w in banned if " %s " % w in lowtext]
                if hits:
                    warn.append("banned word(s) %s%s" % (", ".join(sorted(set(hits))[:6]), where))
                abbr = [a for a in ABBREVIATIONS if " %s " % a in lowtext]
                if abbr:
                    warn.append("abbreviation(s) %s%s; write them out" % (", ".join(abbr), where))
                if loc in exec_slides and extreme:
                    xs = [w for w in extreme if re.search(r"(?i)\b%s\b" % re.escape(w), text)]
                    if xs:
                        warn.append("A13 extreme word(s) %s on an executive summary%s" % (", ".join(xs), where))
            if is_deck:
                m = PERSONA_LEAK.search(text)
                if m:
                    warn.append("B6 private instruction or persona text in the deck%s: %s" % (where, snippet(text, m.start())))
            if is_deck and not loc.startswith("notes"):
                if is_title:
                    t = " ".join(text.split())
                    if len(t) > 120:
                        warn.append("headline over 120 characters%s" % where)
                    if re.search(r"[,;:]", t):
                        warn.append("headline contains a comma, semicolon or colon%s" % where)
                    if re.search(r"(?i),\s*not\s", t):
                        warn.append("'X, not Y' headline construction%s" % where)
                    xs = [w for w in extreme if re.search(r"(?i)\b%s\b" % re.escape(w), t)]
                    if xs:
                        warn.append("extreme word(s) %s in headline%s" % (", ".join(xs), where))
    else:
        text = "\n".join(read_lines(path))
        block += check_em_dash(text)
        if invest or (EQUITY_CONTENT.search(text) and not exempt):
            block += check_equity(text)
        if resume:
            block += check_kill_list(text, root)
            block += check_fact_numbers(text, root)
    return block, warn


def content_from_tool(tool_name, ti):
    if tool_name == "Write":
        return ti.get("content") or ""
    if tool_name == "Edit":
        return ti.get("new_string") or ""
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string") or "" for e in ti.get("edits") or [])
    if tool_name == "NotebookEdit":
        return ti.get("new_source") or ""
    return ""


# ---------------------------------------------------------------- transcript
def last_exchange(transcript_path):
    """Return (last user prompt text, final assistant text after it)."""
    user_text, assistant_parts = "", []
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception:
        return "", ""
    for raw in lines:
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        kind = obj.get("type")
        msg = obj.get("message") or {}
        content = msg.get("content")
        if kind == "user":
            texts = []
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        texts.append(c.get("text") or "")
            joined = "\n".join(t for t in texts if t).strip()
            if joined and not obj.get("isMeta"):
                user_text, assistant_parts = joined, []
        elif kind == "assistant":
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        assistant_parts.append(c.get("text") or "")
            elif isinstance(content, str):
                assistant_parts.append(content)
    return user_text, "\n".join(assistant_parts)


# ---------------------------------------------------------------- modes
def mode_pre(payload, root, cfg):
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    text = content_from_tool(tool, ti)
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if not text:
        return 0
    rel = rel_path(path, root) if path else ""
    exempt = match_globs(rel, cfg.get("exempt_globs")) if rel else False
    problems = check_em_dash(text)
    if not exempt and (match_globs(rel, cfg.get("invest_globs")) or EQUITY_CONTENT.search(text)):
        problems += check_equity(text)
    if not exempt and rel and match_globs(rel, cfg.get("resume_globs")):
        problems += check_kill_list(text, root) + check_fact_numbers(text, root)
    if not problems:
        return 0
    reason = ("Blocked by the second-brain guard (%s). Fix and retry:\n- %s\n"
              "Em dashes: use commas, semicolons or colons. Equity: verdicts only BUY, ACCUMULATE, HOLD, WATCH or "
              "AVOID, with pause triggers instead of exits or stops. Resume: use only fact-base numbers and never a "
              "kill-list claim." % (rel or tool, "\n- ".join(problems[:12])))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    sys.stderr.write(reason + "\n")
    return 2


def start_marker(root, payload):
    key = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("tool_use_id") or "last"))[:80] or "last"
    return os.path.join(root, GUARD_DIR, ".bash-start-%s" % key)


def mode_prebash(payload, root, cfg):
    """PreToolUse on Bash: remember when the command started, so post only lints files it wrote."""
    try:
        os.makedirs(os.path.join(root, GUARD_DIR), exist_ok=True)
        with open(start_marker(root, payload), "w", encoding="utf-8") as fh:
            fh.write("%.3f" % time.time())
    except OSError:
        pass
    return 0


def command_start(root, payload):
    path = start_marker(root, payload)
    try:
        with open(path, encoding="utf-8") as fh:
            started = float(fh.read().strip())
        os.remove(path)
        return started - 0.5
    except (OSError, ValueError):
        return time.time() - 120.0


def candidate_files(command, cwd, since):
    """Files this command wrote: paths it names, plus Office files under cwd, modified after `since`."""
    exts = TEXT_EXTS + OFFICE_EXTS
    ext_rx = "|".join(re.escape(e.lstrip(".")) for e in exts)
    found = set()
    for m in re.finditer(r'"([^"]+\.(?:%s))"|\'([^\']+\.(?:%s))\'|((?:[^\s"\'<>|;&])+\.(?:%s))(?=[\s"\';|&)]|$)'
                         % (ext_rx, ext_rx, ext_rx), command):
        p = next(g for g in m.groups() if g)
        p = os.path.expanduser(p)
        found.add(p if os.path.isabs(p) else os.path.join(cwd, p))
    for base, dirs, files in walk_limited(cwd, 3):
        for f in files:
            if f.lower().endswith(OFFICE_EXTS):
                found.add(os.path.join(base, f))
    out = []
    for p in found:
        try:
            if os.path.isfile(p) and os.path.getmtime(p) >= since:
                out.append(p)
        except OSError:
            pass
    return sorted(out)


def walk_limited(top, depth):
    top = os.path.abspath(top)
    base_depth = top.rstrip(os.sep).count(os.sep)
    for base, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        if base.count(os.sep) - base_depth >= depth:
            dirs[:] = []
        yield base, dirs, files


def mode_post(payload, root, cfg):
    if (payload.get("tool_name") or "") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or root
    blocks, warns = [], []
    for fp in candidate_files(command, cwd, command_start(root, payload)):
        b, w = lint_file(fp, root, cfg)
        rel = rel_path(fp, root)
        blocks += ["%s: %s" % (rel, x) for x in b]
        warns += ["%s: %s" % (rel, x) for x in w]
    if blocks:
        msg = ("Second-brain guard: the files this command wrote break a hard mandate. Fix them before going on.\n- %s"
               % "\n- ".join(blocks[:15]))
        if warns:
            msg += "\nAlso fix (standards):\n- " + "\n- ".join(warns[:10])
        sys.stderr.write(msg + "\n")
        return 2
    if warns:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
                                                 "Second-brain lint (standards to fix before delivery):\n- "
                                                 + "\n- ".join(warns[:12])}}))
    return 0


def mode_stop(payload, root, cfg):
    if payload.get("stop_hook_active"):
        return 0
    tp = payload.get("transcript_path") or ""
    user_text, answer = last_exchange(tp) if tp else ("", "")
    if isinstance(payload.get("last_assistant_message"), str) and payload["last_assistant_message"].strip():
        answer = payload["last_assistant_message"]
    if not answer:
        return 0
    problems = check_em_dash(answer)
    if EQUITY_PROMPT.search(user_text) or EQUITY_CONTENT.search(answer):
        problems += check_equity(answer)
    if RESUME_PROMPT.search(user_text):
        problems += check_kill_list(answer, root) + check_fact_numbers(answer, root)
    if not problems:
        return 0
    reason = ("Your last answer breaks a hard mandate. Rewrite the affected part and give the corrected text in full:\n- %s\n"
              "Em dashes become commas, semicolons or colons. Equity verdicts are BUY, ACCUMULATE, HOLD, WATCH or AVOID "
              "only; no sell, trim, exit, reduce, stop-loss or tax-loss suggestions. Resume numbers come only from the "
              "locked fact base; a number that is not a claim (a word count, a date) can stay if you say so."
              % "\n- ".join(problems[:12]))
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


FORGE_NOTE = ("FORGE trigger (T2): do not answer directly. Run the /forge protocol: draft in full, have the critic "
              "agent grade the draft PASS or FAIL on the eight T2 gates, revise only failed items, at most three "
              "passes, then show only the final answer and the two-line CHECK footer; name any gate still failing.")


def mode_prompt(payload, root, cfg):
    prompt = payload.get("prompt") or ""
    notes = []
    if re.match(r"\s*FORGE\s*:", prompt, flags=re.I):
        notes.append(FORGE_NOTE)
    if BUILD_PROMPT.search(prompt) or EDIT_PROMPT.search(prompt):
        notes.append("Build preflight (M6): before editing, find the latest version of the working file (version number "
                     "and modified time; prefer the file the owner last shared or edited) and say which one you build on. "
                     "Re-read the rules that apply: output-standards.md (deck, resume, or Excel and data rules), the "
                     "engagement's area in active-areas.md and any engagement rule set in templates.md. Change only what "
                     "was asked. Client decks are final decks: no version-control content (M3).")
    if EQUITY_PROMPT.search(prompt):
        notes.append("Equity mandate (M2): verdicts only BUY, ACCUMULATE, HOLD, WATCH or AVOID. No sell, trim, exit, "
                     "reduce, stop-loss or tax-loss suggestions on holdings. Follow T10; prices carry an IST timestamp; "
                     "every decision-driving claim is graded.")
    if RESUME_PROMPT.search(prompt):
        notes.append("Resume mandate (M4): numbers only from the locked fact base (T50); kill-list claims never return; "
                     "plain text in chat when text is asked for.")
    if notes:
        print("\n\n".join(notes))
    return 0


# ---------------------------------------------------------------- extract (installer and /onboard)
def section(lines, start_rx, level_rx=r"^#{2,3} "):
    out, on = [], False
    for ln in lines:
        if re.match(start_rx, ln):
            on = True
            continue
        if on and re.match(level_rx, ln):
            break
        if on:
            out.append(ln)
    return out


def balanced_after(text, marker):
    i = text.find(marker)
    if i < 0:
        return ""
    i += len(marker)
    depth, j = 1, i
    while j < len(text) and depth:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
        j += 1
    return text[i:j - 1]


def split_items(body):
    items, cur, quote = [], "", False
    for ch in body:
        if ch in "\"“”":
            quote = not quote
            cur += ch
        elif ch == "," and not quote:
            items.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur.strip())
    return items


def kill_patterns(os_dir):
    text = "\n".join(read_lines(os.path.join(os_dir, "output-standards.md")))
    body = balanced_after(text, "Kill list never returns (")
    pats, skipped = [], []
    for item in split_items(body):
        it = item.replace("\"", "").replace("“", "").replace("”", "").strip().strip(".")
        if not it:
            continue
        if re.match(r"(?i)(fabricated|invented|fake|made[- ]up|imaginary|false)\b", it):
            skipped.append(it)
            continue
        m = re.match(r"^(.+?)\s+at\s+(.+)$", it)
        if m:
            pats.append("%s && %s" % (m.group(1).strip(), m.group(2).strip()))
            continue
        m = re.match(r"^(.+?)\s+for\s+(.+)$", it)
        if m and "/" in m.group(1):
            for part in m.group(1).split("/"):
                pats.append("%s && %s" % (part.strip(), m.group(2).strip()))
            continue
        pats.append(it)
        m = re.match(r"^(\d+(?:\.\d+)?x)\s+(.+)$", it)
        if m:
            pats.append("%s %s" % (m.group(2), m.group(1)))
    return pats, skipped


def fact_numbers(os_dir):
    found = set()
    tpl = read_lines(os.path.join(os_dir, "templates.md"))
    chunks = section(tpl, r"^### 50\.", r"^### ")
    ident = read_lines(os.path.join(os_dir, "identity.md"))
    for name in ("Roles and employers", "Education and recognition"):
        for ln in section(ident, r"^## %s" % name, r"^## "):
            ln = re.sub(r"\([^)]*(?:earlier|said|kill|although|differed|conflict)[^)]*\)", "", ln, flags=re.I)
            sentences = re.split(r"(?<=\.)\s+", ln)
            chunks.append(" ".join(s for s in sentences if "kill list" not in s.lower()))
    for ln in chunks:
        ln = re.split(r"\bSources?:", ln)[0]
        for m in NUMBER_TOKEN_LOOSE.finditer(ln):
            v, u = norm_number(m.group(2), m.group(3))
            if v is None:
                continue
            val = ("%f" % v).rstrip("0").rstrip(".")
            found.add(val + (u if u and u != "+" else ""))
            found.add(val)
        for w, n in NUMBER_WORDS.items():
            if re.search(r"\b%s\b" % w, ln, flags=re.I):
                found.add(str(n))
    return sorted(found, key=lambda s: (float(re.match(r"[\d.]+", s).group(0)), s))


def mode_extract(vault, os_name="00-Operating-System", force=False):
    os_dir = os.path.join(vault, os_name)
    gdir = os.path.join(vault, GUARD_DIR)
    os.makedirs(gdir, exist_ok=True)
    report = []
    kl = os.path.join(gdir, "kill-list.txt")
    if force or not os.path.exists(kl):
        pats, skipped = kill_patterns(os_dir)
        with open(kl, "w", encoding="utf-8") as fh:
            fh.write("# Kill list (private). One claim per line, case-insensitive; '&&' means both on the same line.\n")
            fh.write("# Generated from %s/output-standards.md; edit freely, the guard reads this file.\n" % os_name)
            for s in skipped:
                fh.write("# not machine-checkable, enforced by the fact-base number check: %s\n" % s)
            fh.write("\n".join(pats) + ("\n" if pats else ""))
        report.append("kill-list.txt: %d pattern(s)" % len(pats))
    else:
        report.append("kill-list.txt: kept (already exists)")
    fb = os.path.join(gdir, "fact-base-numbers.txt")
    if force or not os.path.exists(fb):
        nums = fact_numbers(os_dir)
        with open(fb, "w", encoding="utf-8") as fh:
            fh.write("# Locked fact-base numbers (private). Resume text may only use these numbers (years and dates are\n")
            fh.write("# always allowed). Generated from templates.md T50 and identity.md; add a line to allow a number.\n")
            fh.write("\n".join(nums) + ("\n" if nums else ""))
        report.append("fact-base-numbers.txt: %d value(s)" % len(nums))
    else:
        report.append("fact-base-numbers.txt: kept (already exists)")
    return report


# ---------------------------------------------------------------- main
def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "extract":
        vault = os.path.abspath(argv[2]) if len(argv) > 2 else project_dir()
        os_name = argv[3] if len(argv) > 3 else load_config(vault).get("os_dir", "00-Operating-System")
        for line in mode_extract(vault, os_name, force="--force" in argv):
            print(line)
        return 0
    if mode == "lint":
        root = project_dir()
        cfg = load_config(root)
        bad = 0
        for fp in argv[2:]:
            if fp.startswith("--"):
                continue
            b, w = lint_file(fp, root, cfg, context_resume="--resume" in argv)
            print("%s: %s" % (fp, "OK" if not (b or w) else ""))
            for x in b:
                print("  BLOCK " + x)
            for x in w:
                print("  WARN  " + x)
            bad += len(b)
        return 1 if bad else 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    root = project_dir(payload)
    if guard_off(root):
        return 0
    cfg = load_config(root)
    handler = {"pre": mode_pre, "prebash": mode_prebash, "post": mode_post, "stop": mode_stop,
               "prompt": mode_prompt}.get(mode)
    if not handler:
        return 0
    try:
        return handler(payload, root, cfg)
    except Exception:  # never break the session
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
