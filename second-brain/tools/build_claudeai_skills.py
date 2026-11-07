#!/usr/bin/env python3
"""Build claude.ai-ready skill zips from the kit's Claude Code skills.

usage: python3 build_claudeai_skills.py OUT_DIR [--name NAME] [--os-dir 00-Operating-System]

claude.ai accepts only name, description, license, compatibility, metadata and allowed-tools in a skill's
frontmatter, so model, effort, context, agent and argument-hint are stripped. Placeholders are rendered, and a
short "In chat" note is added so the skill works without the vault's hooks and scripts.
Writes one <skill>.zip per skill (folder <skill>/SKILL.md inside) plus ALL-SKILLS.zip. Standard library only.
"""
import argparse
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(HERE, "..", "vault", ".claude", "skills")
ALLOWED = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
MODELS = {"__TOP_MODEL__": "Fable", "__CRITIC_MODEL__": "Opus", "__MAIN_MODEL__": "Opus",
          "__CARE_MODEL__": "Opus", "__MID_MODEL__": "Sonnet", "__SMALL_MODEL__": "Haiku"}
CHAT_NOTE = """> **In chat or a Project:** the vault's hooks and scripts do not run here. Use the six operating-system
> files from the Project's knowledge (or the Obsidian connection in the desktop app) wherever this skill says to
> read __OS_DIR__ files, skip steps that run `python3 .claude/...` scripts, and apply the hard mandates yourself:
> no em dashes; equity verdicts only BUY, ACCUMULATE, HOLD, WATCH or AVOID; client decks are final decks; resume
> numbers only from the locked fact base; never fabricate; build on the latest file version. Best model for this
> skill: __BEST__.
"""


def convert(text, owner, os_dir):
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        raise ValueError("no frontmatter")
    fm, body = m.group(1), text[m.end():]
    best = "Opus"
    keep = []
    for ln in fm.split("\n"):
        key = ln.split(":", 1)[0].strip()
        if key == "model":
            best = MODELS.get(ln.split(":", 1)[1].strip(), "Opus")
        if key in ALLOWED:
            keep.append(ln)
    note = CHAT_NOTE.replace("__BEST__", best)
    out = "---\n" + "\n".join(keep) + "\n---\n" + note + "\n" + body
    for k, v in MODELS.items():
        out = out.replace(k, v)
    return out.replace("__OWNER__", owner).replace("__OS_DIR__", os_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--name", default="the owner")
    ap.add_argument("--os-dir", default="00-Operating-System")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = sorted(d for d in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))
    all_zip = zipfile.ZipFile(os.path.join(a.out, "ALL-SKILLS.zip"), "w", zipfile.ZIP_DEFLATED)
    for n in names:
        with open(os.path.join(SKILLS, n, "SKILL.md"), encoding="utf-8") as fh:
            text = convert(fh.read(), a.name, a.os_dir)
        if re.search(r"__[A-Z_]+__", text) or chr(0x2014) in text:
            raise SystemExit("unrendered placeholder or em dash in " + n)
        with zipfile.ZipFile(os.path.join(a.out, n + ".zip"), "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("%s/SKILL.md" % n, text)
        all_zip.write(os.path.join(a.out, n + ".zip"), n + ".zip")
    all_zip.close()
    print("Built %d claude.ai skill zips in %s" % (len(names), a.out))


if __name__ == "__main__":
    main()
