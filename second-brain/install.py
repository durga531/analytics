#!/usr/bin/env python3
"""Second-brain installer: non-destructive, path-parameterised. Run through install.sh.

usage: bash install.sh VAULT_PATH [--dry-run] [--yes] [--name NAME] [--os-dir DIR]
                       [--top-model fable] [--critic-model opus] [--main-model opus] [--care-model opus]
                       [--mid-model sonnet] [--small-model haiku] [--no-mcp] [--no-autostart]

Guarantees
- Never writes inside the operating-system folder (default 00-Operating-System) or .obsidian/plugins.
- Never moves, renames or deletes a note. Folder moves are only proposed (01-Inbox/Folder Mapping - Proposed.md).
- Never overwrites a file you changed. A file the kit installed earlier and you have not edited is updated;
  anything else that differs gets the kit version beside it as <name>.kit-new.
- Private data (kill list, fact-base numbers, folder mapping, digest) is generated inside the vault only.
Python 3.8+ standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

KIT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(KIT, "vault")
MANIFEST = os.path.join(".claude", ".kit-manifest.json")
TEXT_EXTS = (".md", ".json", ".py", ".sh", ".txt", ".base")
SIX = ["identity.md", "active-areas.md", "output-standards.md", "thinking-patterns.md", "templates.md",
       "recurring-asks.md"]
ROLE_KEYWORDS = {
    "invest": r"invest|equit|stock|portfolio|trading",
    "work": r"strateg|business|client|consult|engagement|\bwork\b|project",
    "self": r"personal|growth|\bself\b|health|fitness|journal|\blife\b",
    "learn": r"histor|philosoph|politic|govern|artificial|intelligence|\bai\b|econom|science|learn|book|culture|psycholog",
}
RULE_ROLE = {"work.md": "work", "invest.md": "invest", "self.md": "self", "learn.md": "learn"}
LOCAL_REST_API = os.path.join(".obsidian", "plugins", "obsidian-local-rest-api", "data.json")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def say(msg=""):
    print(msg, flush=True)


def ask(question, assume_yes):
    if assume_yes:
        return True
    try:
        return input("%s [y/N] " % question).strip().lower() in ("y", "yes")
    except EOFError:
        return False


def owner_name(os_dir):
    try:
        with open(os.path.join(os_dir, "identity.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return ""
    m = re.search(r"^## Who\s*\n+- ([^\n.]+)", text, flags=re.M)
    return m.group(1).split()[0].strip(" ,*") if m else ""


def topic_folders(vault, os_name):
    out = []
    for name in sorted(os.listdir(vault)):
        full = os.path.join(vault, name)
        if not os.path.isdir(full) or name.startswith(".") or name == os_name or re.match(r"^\d{2}-", name):
            continue
        out.append(name)
    return out


def roles_for(folder):
    return [role for role, rx in ROLE_KEYWORDS.items() if re.search(rx, folder, flags=re.I)]


def render(text, subs):
    for key, val in subs.items():
        text = text.replace(key, val)
    return text


def add_rule_paths(text, globs):
    """Append extra globs to the paths: list of a rule file's frontmatter."""
    if not globs:
        return text
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return text
    lines = m.group(1).split("\n")
    last = max(i for i, ln in enumerate(lines) if ln.strip().startswith("- "))
    extra = ['  - "%s/**"' % g.replace('"', '\\"') for g in globs]
    lines = lines[:last + 1] + extra + lines[last + 1:]
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


class Installer:
    def __init__(self, args):
        self.args = args
        self.vault = os.path.abspath(os.path.expanduser(args.vault))
        self.os_name = args.os_dir
        self.os_dir = os.path.join(self.vault, self.os_name)
        self.dry = args.dry_run
        self.actions = []
        self.manifest = {}
        self.new_manifest = {}

    # ------------------------------------------------------------ checks
    def preflight(self):
        if not os.path.isdir(self.vault):
            raise SystemExit("Vault folder not found: %s" % self.vault)
        if not os.path.isdir(os.path.join(self.vault, ".obsidian")):
            say("Note: no .obsidian folder here. Is this the vault root? Continuing.")
        missing = [f for f in SIX if not os.path.isfile(os.path.join(self.os_dir, f))]
        if missing:
            say("Note: %s/ is missing %s. The engine reads these files; add them, then re-run."
                % (self.os_name, ", ".join(missing)))
        try:
            with open(os.path.join(self.vault, MANIFEST), encoding="utf-8") as fh:
                self.manifest = json.load(fh)
        except (OSError, ValueError):
            self.manifest = {}

    # ------------------------------------------------------------ plan
    def subs(self):
        name = self.args.name or owner_name(self.os_dir) or "the owner"
        return {
            "__OWNER__": name, "__OS_DIR__": self.os_name,
            "__TOP_MODEL__": self.args.top_model, "__CRITIC_MODEL__": self.args.critic_model,
            "__MAIN_MODEL__": self.args.main_model, "__CARE_MODEL__": self.args.care_model,
            "__MID_MODEL__": self.args.mid_model, "__SMALL_MODEL__": self.args.small_model,
        }

    def role_globs(self):
        globs = {"invest": [], "work": [], "self": [], "learn": []}
        for folder in topic_folders(self.vault, self.os_name):
            for role in roles_for(folder):
                globs[role].append(folder)
        return globs

    def place(self, rel, data):
        """Decide what to do with one kit file; record the action."""
        dest = os.path.join(self.vault, rel)
        top = rel.replace(os.sep, "/").split("/")[0]
        if top == self.os_name or rel.replace(os.sep, "/").startswith(".obsidian/plugins/"):
            self.actions.append(("refuse", rel))
            return
        digest = sha(data)
        if not os.path.exists(dest):
            self.actions.append(("create", rel, data))
            self.new_manifest[rel] = digest
            return
        with open(dest, "rb") as fh:
            current = fh.read()
        if current == data:
            self.actions.append(("same", rel))
            self.new_manifest[rel] = digest
            return
        if self.manifest.get(rel) == sha(current):
            self.actions.append(("update", rel, data))
            self.new_manifest[rel] = digest
            return
        self.actions.append(("beside", rel, data))
        if rel in self.manifest:
            self.new_manifest[rel] = self.manifest[rel]

    def plan(self):
        subs = self.subs()
        globs = self.role_globs()
        for base, dirs, files in os.walk(SRC):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith((".pyc", ".DS_Store")):
                    continue
                full = os.path.join(base, f)
                rel = os.path.relpath(full, SRC)
                with open(full, "rb") as fh:
                    data = fh.read()
                if f.endswith(TEXT_EXTS):
                    text = render(data.decode("utf-8"), subs)
                    if f == "CLAUDE.md":  # @imports need spaces escaped
                        text = "\n".join(("@" + ln[1:].replace("\\ ", " ").replace(" ", "\\ "))
                                         if ln.startswith("@") else ln for ln in text.split("\n"))
                    if rel.replace(os.sep, "/").startswith(".claude/rules/") and f in RULE_ROLE:
                        text = add_rule_paths(text, globs[RULE_ROLE[f]])
                    data = text.encode("utf-8")
                if rel.replace(os.sep, "/").startswith(".obsidian/"):
                    if os.path.exists(os.path.join(self.vault, rel)):
                        self.actions.append(("keep-obsidian", rel))
                        continue
                self.place(rel, data)
        cfg = {
            "os_dir": self.os_name,
            "invest_globs": ["04-Invest/**"] + ["%s/**" % g for g in globs["invest"]],
            "resume_globs": ["**/*resume*", "**/*CV*", "**/*cv.*", "**/*cover letter*", "**/*cover-letter*"],
            "exempt_globs": ["%s/**" % self.os_name, ".claude/**", "99-Archive/**"],
            "topic_folders": {f: roles_for(f) for f in topic_folders(self.vault, self.os_name)},
        }
        self.place(os.path.join(".claude", "guard", "config.json"),
                   (json.dumps(cfg, indent=2) + "\n").encode("utf-8"))
        return globs

    # ------------------------------------------------------------ apply
    def write(self, rel, data):
        dest = os.path.join(self.vault, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        if rel.endswith((".py", ".sh")):
            os.chmod(dest, 0o755)

    def apply(self):
        for act in self.actions:
            kind, rel = act[0], act[1]
            if kind in ("create", "update"):
                self.write(rel, act[2])
            elif kind == "beside":
                self.write(rel + ".kit-new", act[2])
        with open(os.path.join(self.vault, MANIFEST), "w", encoding="utf-8") as fh:
            json.dump(self.new_manifest, fh, indent=1, sort_keys=True)

    def report(self):
        counts = {}
        for act in self.actions:
            counts[act[0]] = counts.get(act[0], 0) + 1
        say("Files: %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())))
        for act in self.actions:
            if act[0] in ("beside", "refuse", "update"):
                label = {"beside": "kept yours, kit copy saved as %s.kit-new" % act[1],
                         "refuse": "refused (protected path)", "update": "updated (kit file you had not edited)"}
                say("  %s: %s" % (act[1], label[act[0]]))

    # ------------------------------------------------------------ extras
    def run_tool(self, args, label):
        if self.dry:
            say("  would run: %s" % label)
            return
        out = subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=self.vault)
        for line in (out.stdout + out.stderr).strip().splitlines():
            say("  " + line)

    def private_layer(self):
        say("\nPrivate layer (generated inside the vault from your OS files, never in the repo):")
        guard = os.path.join(self.vault, ".claude", "hooks", "guard.py")
        mapper = os.path.join(self.vault, ".claude", "tools", "propose_mapping.py")
        if not self.dry and not os.path.exists(guard):
            say("  guard.py not installed; skipped")
            return
        self.run_tool([guard, "extract", self.vault, self.os_name], "guard.py extract (kill list, fact-base numbers)")
        self.run_tool([mapper, self.vault, "--os-dir", self.os_name], "propose_mapping.py (folder mapping proposal)")

    def autostart(self):
        if self.args.no_autostart or sys.platform != "darwin":
            return
        name = os.path.basename(self.vault.rstrip(os.sep))
        plist = os.path.expanduser("~/Library/LaunchAgents/com.secondbrain.obsidian.plist")
        if os.path.exists(plist):
            say("\nAutostart: already configured (%s)" % plist)
            return
        url = "obsidian://open?vault=" + urllib.parse.quote(name, safe="")
        body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                '<plist version="1.0">\n<dict>\n'
                '  <key>Label</key><string>com.secondbrain.obsidian</string>\n'
                '  <key>ProgramArguments</key>\n  <array><string>/usr/bin/open</string><string>%s</string></array>\n'
                '  <key>RunAtLoad</key><true/>\n</dict>\n</plist>\n') % url.replace("&", "&amp;")
        if self.dry:
            say("\nAutostart: would add a login item that opens this vault (%s)" % url)
            return
        if ask("\nOpen this vault in Obsidian automatically at every login?", self.args.yes):
            os.makedirs(os.path.dirname(plist), exist_ok=True)
            with open(plist, "w", encoding="utf-8") as fh:
                fh.write(body)
            say("Autostart: added %s (takes effect at next login)" % plist)

    def mcp_bridge(self):
        if self.args.no_mcp:
            return
        say("\nObsidian bridge (Local REST API plugin -> mcp-obsidian):")
        try:
            with open(os.path.join(self.vault, LOCAL_REST_API), encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            say("  Local REST API plugin settings not found. Enable the plugin in Obsidian, then re-run.")
            return
        key = data.get("apiKey") or ""
        port = str(data.get("port") or 27124)
        if not key:
            say("  The plugin has no API key yet. Open its settings once in Obsidian, then re-run.")
            return
        masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        server = {"type": "stdio", "command": "uvx", "args": ["mcp-obsidian"],
                  "env": {"OBSIDIAN_API_KEY": key, "OBSIDIAN_HOST": "127.0.0.1", "OBSIDIAN_PORT": port}}
        claude, uvx = shutil.which("claude"), shutil.which("uvx")
        if not uvx:
            say("  uvx not found. Install uv first (brew install uv), then re-run for the bridge.")
        if claude and uvx:
            exists = subprocess.run([claude, "mcp", "get", "obsidian"], capture_output=True, text=True,
                                    cwd=self.vault).returncode == 0
            if exists:
                say("  Claude Code already has an 'obsidian' MCP server for this vault; left unchanged.")
            elif self.dry:
                say("  would run: claude mcp add-json obsidian <config with key %s> --scope local" % masked)
            elif ask("  Add the 'obsidian' MCP server to Claude Code for this vault (local scope, key %s)?" % masked,
                     self.args.yes):
                out = subprocess.run([claude, "mcp", "add-json", "obsidian", json.dumps(server), "--scope", "local"],
                                     capture_output=True, text=True, cwd=self.vault)
                if out.returncode != 0:  # documented fallback: --env pairs, then another option, then the name
                    env = []
                    for k, v in server["env"].items():
                        env += ["--env", "%s=%s" % (k, v)]
                    out = subprocess.run([claude, "mcp", "add", "--scope", "local"] + env +
                                         ["--transport", "stdio", "obsidian", "--", "uvx", "mcp-obsidian"],
                                         capture_output=True, text=True, cwd=self.vault)
                say("  " + ((out.stdout or out.stderr).strip() or "done"))
        elif not claude:
            say("  Claude Code CLI not found; install it, then re-run for the bridge.")
        shown = dict(server, env=dict(server["env"], OBSIDIAN_API_KEY=masked))
        shown.pop("type")
        say("  Alternative: recent versions of the plugin also serve MCP themselves at https://127.0.0.1:%s/mcp/ "
            "(Bearer API key); Claude Code inside the vault needs no bridge at all because it reads the files directly." % port)
        say("  For the Claude desktop app, the same server goes under mcpServers in claude_desktop_config.json "
            "(skip if you already connected it):")
        say("  " + json.dumps({"mcpServers": {"obsidian": shown}}))

    def obsidian_notes(self):
        say("\nObsidian: core Daily notes points to 02-Daily with 08-Library/Templates/Daily (set only if you had "
            "no setting). Plugins are untouched. Dataview and Tasks power Home.md.")

    def prerequisites(self):
        say("\nTools the build skills use (install what is missing):")
        checks = [("claude", "Claude Code CLI", "see code.claude.com/docs"),
                  ("uvx", "uv (for the Obsidian MCP bridge)", "brew install uv"),
                  ("node", "Node.js (pptxgenjs and docx builds)", "brew install node"),
                  ("soffice", "LibreOffice (render to PDF)", "brew install --cask libreoffice"),
                  ("pdftoppm", "Poppler (render slide images)", "brew install poppler")]
        for exe, label, hint in checks:
            found = shutil.which(exe) or (exe == "soffice" and os.path.exists(
                "/Applications/LibreOffice.app/Contents/MacOS/soffice"))
            say("  [%s] %s%s" % ("x" if found else " ", label, "" if found else "  -> " + hint))

    def run(self):
        self.preflight()
        say("Second-brain installer%s" % (" (dry run: nothing is written)" if self.dry else ""))
        say("Vault: %s" % self.vault)
        globs = self.plan()
        folders = topic_folders(self.vault, self.os_name)
        say("Existing topic folders kept in place: %s" % (", ".join(folders) or "none"))
        for role in ("work", "invest", "self", "learn"):
            if globs[role]:
                say("  %s rules also cover: %s" % (role, ", ".join(globs[role])))
        if not self.dry:
            self.apply()
        self.report()
        self.private_layer()
        self.obsidian_notes()
        self.autostart()
        self.mcp_bridge()
        self.prerequisites()
        say("\nNext: cd into the vault, start Claude Code (claude), then run /onboard.")
        if any(a[0] == "beside" for a in self.actions):
            say("Some of your files were kept; /onboard walks you through merging the .kit-new copies.")
        say("Folder moves are proposed, not done: see 01-Inbox/Folder Mapping - Proposed.md.")


def main():
    p = argparse.ArgumentParser(description="Install the second-brain engine into an Obsidian vault.")
    p.add_argument("vault")
    p.add_argument("--name", default="")
    p.add_argument("--os-dir", default="00-Operating-System")
    p.add_argument("--top-model", default="fable")
    p.add_argument("--critic-model", default="opus")
    p.add_argument("--main-model", default="opus")
    p.add_argument("--care-model", default="opus")
    p.add_argument("--mid-model", default="sonnet")
    p.add_argument("--small-model", default="haiku")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--no-mcp", action="store_true")
    p.add_argument("--no-autostart", action="store_true")
    Installer(p.parse_args()).run()


if __name__ == "__main__":
    main()
