"""Tests for the second-brain guard and session hooks. Synthetic fixtures only: no owner data.

Run: python3 -m unittest discover -s second-brain/tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.join(HERE, "..", "vault", ".claude", "hooks")
GUARD = os.path.join(HOOKS, "guard.py")
CONTEXT = os.path.join(HOOKS, "session_context.py")
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
EM = chr(0x2014)  # never a literal: the kit must contain no em dash characters

OUTPUT_STANDARDS = """---
title: Output Standards
updated: 2026-01-01
---
# Output Standards
## Formatting bans
- Banned words (house list): synergy, paradigm, frobnicate. Source: test.
- Banned informal words in client decks (test client): widget soup, jazz hands. Sources: test.
- No extreme or absolute statements in client slides (never, nothing, zero). Source: test.
## Resume rules
- Numbers only from the locked fact base; vary order and emphasis by role, never the numbers. Kill list never returns (3x Golden Spoon, "top 0.01%", "led" at Acme Corp, Moon Mill, buy-side/sell-side for Fake Deal, invented values). Source: test.
"""
TEMPLATES = """---
title: Templates
updated: 2026-01-01
---
# Templates
### 1. Answer structure [mine]
Body.
### 50. Resume architecture [mine]
- Locked numbers (fact base): Golden Spoon 1x (top 3 of 9,000); 41% churn cut; $2.4B+ aggregate; 7,700+ outlets across 21 cities; Rs 12.5 Cr payout.
### 51. Outreach deck [directed]
Body.
"""
IDENTITY = """---
title: Identity
updated: 2026-01-01
---
# Identity
## Who
- Test Person. Source: test.
## Roles and employers
- Analyst, Example Co, Jan 2015 to Mar 2019; team of 12. Source: test.
## Education and recognition
- Degree, Example University, rank 9 of 350 (an earlier chat said 9 of 999). Source: test.
## Interests
- None.
"""
RECURRING = """---
updated: 2026-01-01
---
# Recurring Asks
## Routing implication for the second brain
- Top model: asks 2, 3.
- Small model or script: asks 5.
"""
THINKING = """---
updated: 2026-01-01
---
# Thinking Patterns
## Closed debates (do not reopen)
- Debate one stays closed.
## Working habits
- x
"""
ACTIVE = """---
updated: 2026-01-01
---
# Active Areas
## Client work
### 1. Alpha programme
- Status: live and moving. More detail here.
"""


def make_pptx(path, slides, notes=None):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        for i, (title, body) in enumerate(slides, 1):
            xml = ('<p:sld xmlns:p="%s" xmlns:a="%s"><p:cSld><p:spTree>'
                   '<p:sp><p:nvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
                   '<p:txBody><a:p><a:r><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
                   '<p:sp><p:txBody><a:p><a:r><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
                   '</p:spTree></p:cSld></p:sld>') % (NS_P, NS_A, title, body)
            z.writestr("ppt/slides/slide%d.xml" % i, xml)
        for i, text in enumerate(notes or [], 1):
            z.writestr("ppt/notesSlides/notesSlide%d.xml" % i,
                       '<p:notes xmlns:p="%s" xmlns:a="%s"><a:t>%s</a:t></p:notes>' % (NS_P, NS_A, text))


def make_docx(path, paragraphs):
    with zipfile.ZipFile(path, "w") as z:
        body = "".join('<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % p for p in paragraphs)
        z.writestr("word/document.xml", '<w:document xmlns:w="%s"><w:body>%s</w:body></w:document>' % (NS_W, body))


def make_xlsx(path, sheets):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", "<workbook><sheets>%s</sheets></workbook>" % "".join(
            '<sheet name="S%d" sheetId="%d"/>' % (i, i) for i in range(1, sheets + 1)))
        z.writestr("xl/sharedStrings.xml", "<sst><si><t>Table one</t></si></sst>")


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="sb guard 'test' ")
        osd = os.path.join(cls.root, "00-Operating-System")
        os.makedirs(osd)
        for name, text in (("output-standards.md", OUTPUT_STANDARDS), ("templates.md", TEMPLATES),
                           ("identity.md", IDENTITY), ("recurring-asks.md", RECURRING),
                           ("thinking-patterns.md", THINKING), ("active-areas.md", ACTIVE)):
            with open(os.path.join(osd, name), "w", encoding="utf-8") as fh:
                fh.write(text)
        gdir = os.path.join(cls.root, ".claude", "guard")
        os.makedirs(gdir)
        with open(os.path.join(gdir, "config.json"), "w", encoding="utf-8") as fh:
            json.dump({"os_dir": "00-Operating-System",
                       "invest_globs": ["04-Invest/**", "Economics and Investing/**"],
                       "resume_globs": ["**/*resume*", "**/*CV*"],
                       "exempt_globs": ["00-Operating-System/**", ".claude/**", "99-Archive/**"]}, fh)
        out = subprocess.run([sys.executable, GUARD, "extract", cls.root], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def run_hook(self, mode, payload):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root)
        env.pop("SB_GUARD_OFF", None)
        p = subprocess.run([sys.executable, GUARD, mode], input=json.dumps(payload), capture_output=True,
                           text=True, env=env, cwd=self.root)
        return p.returncode, p.stdout, p.stderr

    def bash_cycle(self, command, make, tool_use_id):
        """Simulate PreToolUse(Bash) -> the command writing files -> PostToolUse(Bash).
        Each case runs from its own folder so cases cannot see each other's fresh files."""
        cwd = os.path.join(self.root, "case-" + tool_use_id)
        os.makedirs(cwd, exist_ok=True)
        time.sleep(0.6)
        self.run_hook("prebash", {"tool_name": "Bash", "tool_use_id": tool_use_id, "cwd": cwd,
                                  "tool_input": {"command": command}})
        time.sleep(0.05)
        make()
        return self.run_hook("post", {"tool_name": "Bash", "tool_use_id": tool_use_id, "cwd": cwd,
                                      "tool_input": {"command": command}})

    def path(self, rel):
        full = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        return full

    def write(self, rel, content):
        return self.run_hook("pre", {"tool_name": "Write", "cwd": self.root,
                                     "tool_input": {"file_path": os.path.join(self.root, rel), "content": content}})

    # ---------- extraction
    def test_extract_kill_list(self):
        with open(os.path.join(self.root, ".claude", "guard", "kill-list.txt"), encoding="utf-8") as fh:
            kl = fh.read()
        for expected in ("3x Golden Spoon", "Golden Spoon 3x", "top 0.01%", "led && Acme Corp", "Moon Mill",
                         "buy-side && Fake Deal", "sell-side && Fake Deal"):
            self.assertIn(expected, kl)
        self.assertIn("# not machine-checkable", kl)

    def test_extract_fact_numbers_excludes_superseded(self):
        with open(os.path.join(self.root, ".claude", "guard", "fact-base-numbers.txt"), encoding="utf-8") as fh:
            nums = set(ln.strip() for ln in fh if ln.strip() and not ln.startswith("#"))
        for expected in ("41%", "2.4b", "7700", "21", "12.5cr", "9000", "350", "12"):
            self.assertIn(expected, nums)
        self.assertNotIn("999", nums)

    # ---------- M1 em dash
    def test_em_dash_blocked_everywhere(self):
        code, out, err = self.write("06-Learn/note.md", "A claim %s with a dash." % EM)
        self.assertEqual(code, 2)
        self.assertIn("deny", out)
        self.assertIn("M1", err)

    def test_em_dash_blocked_even_in_exempt_paths(self):
        code, _, _ = self.write("00-Operating-System/templates.md", "Text %s here" % EM)
        self.assertEqual(code, 2)

    def test_clean_text_allowed(self):
        code, out, err = self.write("06-Learn/note.md", "A clean claim; with a colon: fine.")
        self.assertEqual((code, out, err), (0, "", ""))

    def test_edit_and_multiedit(self):
        code, _, _ = self.run_hook("pre", {"tool_name": "Edit", "tool_input": {
            "file_path": os.path.join(self.root, "x.md"), "old_string": "a", "new_string": "b %s c" % EM}})
        self.assertEqual(code, 2)
        code, _, _ = self.run_hook("pre", {"tool_name": "MultiEdit", "tool_input": {
            "file_path": os.path.join(self.root, "x.md"), "edits": [{"new_string": "ok"}, {"new_string": EM}]}})
        self.assertEqual(code, 2)

    # ---------- M2 equity
    def test_sell_verdict_blocked_in_invest_path(self):
        code, _, err = self.write("04-Invest/Theses/ABC.md", "Verdict: SELL\nConviction: M")
        self.assertEqual(code, 2)
        self.assertIn("M2", err)

    def test_mandate_line_itself_is_allowed(self):
        code, _, err = self.write("04-Invest/prompt.md",
                                  "Verdicts only BUY, ACCUMULATE, HOLD, WATCH or AVOID. No sell, trim, exit, reduce, "
                                  "stop-loss or tax-loss suggestions on existing holdings.")
        self.assertEqual(code, 0, err)

    def test_existing_topic_folder_is_invest_scope(self):
        code, _, _ = self.write("Economics and Investing/ABC.md", "Consider a stop-loss at 1,200.")
        self.assertEqual(code, 2)

    def test_allowed_verdicts_pass(self):
        code, _, _ = self.write("04-Invest/Theses/ABC.md",
                                "Verdict: ACCUMULATE\nPause triggers: margin below 12%\nSell-side consensus is mixed.\n"
                                "Promoter exit in 2019 is noted. Reducing debt is the priority.")
        self.assertEqual(code, 0)

    def test_holding_actions_blocked(self):
        for text in ("Trim the stake by 20%.", "Exit your position before results.", "Book profits in this name.",
                     "Use a trailing stop.", "Harvest a tax-loss here.",
                     "Consider trimming the position after results.", "Reducing exposure makes sense here."):
            code, _, _ = self.write("04-Invest/Theses/ABC.md", text)
            self.assertEqual(code, 2, text)

    def test_action_card_content_outside_invest_path(self):
        code, _, _ = self.write("03-Work/memo.md", "ACTION CARD\nVerdict: Reduce")
        self.assertEqual(code, 2)

    def test_where_to_exit_framework_not_flagged_outside_equity(self):
        code, _, _ = self.write("03-Work/frame.md", "Where to play, how to win and where to exit.")
        self.assertEqual(code, 0)

    def test_exempt_os_dir_allows_legacy_verdict_words(self):
        code, _, _ = self.write("00-Operating-System/templates.md", "Legacy engine output: Reduce or Sell.")
        self.assertEqual(code, 0)

    # ---------- M4 resume
    def test_kill_list_blocked_in_resume(self):
        code, _, err = self.write("05-Self/Career/Resume - Target.md", "Won 3x Golden Spoon for distribution work.")
        self.assertEqual(code, 2)
        self.assertIn("kill-list", err)

    def test_kill_list_cooccurrence(self):
        code, _, _ = self.write("05-Self/Career/resume.md", "Led the merger integration at Acme Corp.")
        self.assertEqual(code, 2)
        code, _, _ = self.write("05-Self/Career/resume.md", "Supported diligence at Acme Corp across $2.4B+ of deals.")
        self.assertEqual(code, 0)

    def test_unlocked_number_blocked_in_resume(self):
        code, _, err = self.write("05-Self/Career/resume.md", "Cut churn 55% across 21 cities.")
        self.assertEqual(code, 2)
        self.assertIn("55%", err)

    def test_locked_numbers_years_and_dates_allowed(self):
        code, _, err = self.write("05-Self/Career/resume.md",
                                  "Cut churn 41% across 7,700+ outlets in 21 cities; Rs 12.5 Cr payout.\n"
                                  "Analyst, Jan 2015 to Mar 2019; team of 12; joined on 14 Jan 2015.")
        self.assertEqual(code, 0, err)

    def test_numbers_not_checked_outside_resume(self):
        code, _, _ = self.write("06-Learn/stats.md", "Inflation was 55% in that year.")
        self.assertEqual(code, 0)

    # ---------- post (Bash-written files)
    def test_post_blocks_fresh_deck_with_version_language(self):
        deck = self.path("case-t1/03-Work/deck-a.pptx")
        code, _, err = self.bash_cycle("python3 build.py --out 03-Work/deck-a.pptx", lambda: make_pptx(
            deck, [("Distribution growth is flat like-for-like", "What changed since v4: slide 7 moved")]), "t1")
        self.assertEqual(code, 2)
        self.assertIn("M3", err)

    def test_post_blocks_em_dash_in_notes_and_placeholders(self):
        deck = self.path("case-t2/03-Work/sub/deck-b.pptx")
        code, _, err = self.bash_cycle("node build.js", lambda: make_pptx(
            deck, [("Coverage drives most of the gap", "xxx")], notes=["Say this %s then that" % EM]), "t2")
        self.assertEqual(code, 2)
        self.assertIn("M1", err)
        self.assertIn("placeholder", err)

    def test_post_clean_deck_warns_but_passes(self):
        deck = self.path("case-t3/03-Work/deck-c.pptx")
        code, out, err = self.bash_cycle("python3 x.py 03-Work/deck-c.pptx", lambda: make_pptx(
            deck, [("Three levers explain most of the gap, never the price", "Synergy across the network")]), "t3")
        self.assertEqual(code, 0, err)
        self.assertIn("synergy", out)
        self.assertIn("extreme word", out)
        self.assertIn("comma", out)

    def test_post_ignores_files_not_written_by_the_command(self):
        old = self.path("case-t4/06-Learn/old.md")
        with open(old, "w", encoding="utf-8") as fh:
            fh.write("Old note %s with a dash\n" % EM)
        own_deck = self.path("case-t4/03-Work/owner-saved.pptx")
        make_pptx(own_deck, [("Owner edit", "What changed %s by hand" % EM)])
        past = time.time() - 30
        os.utime(old, (past, past))
        os.utime(own_deck, (past, past))
        code, out, err = self.bash_cycle("cat '06-Learn/old.md'", lambda: None, "t4")
        self.assertEqual((code, err), (0, ""))

    def test_post_blocks_markdown_written_by_shell(self):
        target = self.path("case-t5/06-Learn/new note.md")
        def make():
            with open(target, "w", encoding="utf-8") as fh:
                fh.write("Fresh text %s written by a heredoc\n" % EM)
        code, _, err = self.bash_cycle("cat > '06-Learn/new note.md' <<EOF", make, "t5")
        self.assertEqual(code, 2)
        self.assertIn("M1", err)

    def test_post_blocks_resume_docx(self):
        doc = self.path("case-t6/05-Self/Career/CV Target.docx")
        code, _, err = self.bash_cycle("node cv.js > '05-Self/Career/CV Target.docx'", lambda: make_docx(
            doc, ["Analyst, Example Co", "Raised share 9.9% across 21 cities"]), "t6")
        self.assertEqual(code, 2)
        self.assertIn("9.9%", err)

    def test_post_rejects_broken_office_file(self):
        bad = self.path("case-t7/03-Work/broken.pptx")
        def make():
            with open(bad, "w") as fh:
                fh.write("not a zip")
        code, _, err = self.bash_cycle("cp a 03-Work/broken.pptx", make, "t7")
        self.assertEqual(code, 2)
        self.assertIn("repair", err)


    # ---------- v2 checks from the coverage audit
    def test_post_blocks_malformed_slide_xml(self):
        deck = self.path("case-t8/03-Work/bad-xml.pptx")
        def make():
            with zipfile.ZipFile(deck, "w") as z:
                z.writestr("ppt/slides/slide1.xml", "<p:sld><p:cSld><unclosed></p:sld>")
        code, _, err = self.bash_cycle("python3 build.py", make, "t8")
        self.assertEqual(code, 2)
        self.assertIn("C2", err)

    def test_post_warns_data_request_with_three_tabs(self):
        wb = self.path("case-t9/03-Work/Data request v1.xlsx")
        code, out, err = self.bash_cycle("python3 dr.py", lambda: make_xlsx(wb, 3), "t9")
        self.assertEqual(code, 0, err)
        self.assertIn("A6", out)

    def test_post_warns_extreme_words_on_executive_summary(self):
        deck = self.path("case-t10/03-Work/summary.pptx")
        code, out, err = self.bash_cycle("python3 b.py", lambda: make_pptx(
            deck, [("Executive summary", "Distribution has zero coverage today")]), "t10")
        self.assertEqual(code, 0, err)
        self.assertIn("A13", out)

    def test_post_warns_persona_text_in_notes(self):
        deck = self.path("case-t11/03-Work/notes.pptx")
        code, out, err = self.bash_cycle("python3 b.py", lambda: make_pptx(
            deck, [("Coverage drives most of the gap", "Body")], notes=["Write this like a senior McKinsey partner"]), "t11")
        self.assertEqual(code, 0, err)
        self.assertIn("B6", out)

    def test_post_reports_changed_slides_against_previous_version(self):
        old = self.path("case-t12/03-Work/Playbook v4.pptx")
        make_pptx(old, [("Lay of the land is stable", "a"), ("Partners under-earn today", "b"), ("Plan", "c")])
        past = time.time() - 60
        os.utime(old, (past, past))
        new = self.path("case-t12/03-Work/Playbook v5.pptx")
        code, out, err = self.bash_cycle("python3 b.py", lambda: make_pptx(
            new, [("Lay of the land is stable", "a"), ("Partners earn less than peers", "b"), ("Plan", "c")]), "t12")
        self.assertEqual(code, 0, err)
        self.assertIn("A10 versus Playbook v4.pptx: changed 2", out)

    def test_stop_prefers_last_assistant_message(self):
        tp = self.transcript("Summarise this", "Clean transcript text.")
        _, out, _ = self.run_hook("stop", {"transcript_path": tp, "last_assistant_message": "Live text %s here" % EM})
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_prompt_preflight_on_edit_requests(self):
        _, out, _ = self.run_hook("prompt", {"prompt": "change the header on slide 7 to something sharper"})
        self.assertIn("Build preflight", out)
        _, out, _ = self.run_hook("prompt", {"prompt": "remove that slide the partner mentioned"})
        self.assertIn("Build preflight", out)

    # ---------- stop
    def transcript(self, user, answer):
        tp = os.path.join(self.root, "t.jsonl")
        with open(tp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": "earlier"}}) + "\n")
            fh.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "old %s" % EM}]}}) + "\n")
            fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": user}}) + "\n")
            fh.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read"}]}}) + "\n")
            fh.write(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}}) + "\n")
            fh.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": answer}]}}) + "\n")
        return tp

    def test_stop_blocks_em_dash_once(self):
        tp = self.transcript("Summarise this", "Here %s the answer" % EM)
        code, out, _ = self.run_hook("stop", {"transcript_path": tp, "stop_hook_active": False})
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["decision"], "block")
        code, out, _ = self.run_hook("stop", {"transcript_path": tp, "stop_hook_active": True})
        self.assertEqual(out, "")

    def test_stop_ignores_earlier_turns(self):
        tp = self.transcript("Summarise this", "Clean answer: no dashes here.")
        code, out, _ = self.run_hook("stop", {"transcript_path": tp, "stop_hook_active": False})
        self.assertEqual(out, "")

    def test_stop_equity_context(self):
        tp = self.transcript("Analyse ABC stock for my portfolio", "Verdict: SELL. Take profits on the stake.")
        _, out, _ = self.run_hook("stop", {"transcript_path": tp})
        self.assertIn("M2", json.loads(out)["reason"])
        tp = self.transcript("Analyse ABC stock for my portfolio", "Verdict: WATCH. Pause triggers listed.")
        _, out, _ = self.run_hook("stop", {"transcript_path": tp})
        self.assertEqual(out, "")

    def test_stop_resume_context(self):
        tp = self.transcript("Tailor my resume for this role", "- Won 3x Golden Spoon; cut churn 41%")
        _, out, _ = self.run_hook("stop", {"transcript_path": tp})
        self.assertIn("kill-list", json.loads(out)["reason"])

    # ---------- prompt
    def test_prompt_injections(self):
        _, out, _ = self.run_hook("prompt", {"prompt": "FORGE: should I take the offer?"})
        self.assertIn("FORGE trigger", out)
        _, out, _ = self.run_hook("prompt", {"prompt": "Update slides 28 and 30 in the deck"})
        self.assertIn("Build preflight", out)
        _, out, _ = self.run_hook("prompt", {"prompt": "Look at my portfolio holdings"})
        self.assertIn("Equity mandate", out)
        _, out, _ = self.run_hook("prompt", {"prompt": "hello"})
        self.assertEqual(out, "")

    # ---------- switch and robustness
    def test_off_switch_and_bad_input(self):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root, SB_GUARD_OFF="1")
        p = subprocess.run([sys.executable, GUARD, "pre"], input=json.dumps({"tool_name": "Write", "tool_input": {
            "file_path": "x.md", "content": EM}}), capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0)
        p = subprocess.run([sys.executable, GUARD, "pre"], input="not json", capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=self.root))
        self.assertEqual(p.returncode, 0)

    def test_generated_kit_text_has_no_em_dash(self):
        kit = os.path.join(HERE, "..")
        offenders = []
        for base, dirs, files in os.walk(kit):
            for f in files:
                if f.endswith((".md", ".py", ".sh", ".json", ".txt")):
                    with open(os.path.join(base, f), encoding="utf-8") as fh:
                        if EM in fh.read():
                            offenders.append(os.path.join(base, f))
        self.assertEqual(offenders, [])


class SessionContextTests(unittest.TestCase):
    def test_digest_under_cap_and_contains_sections(self):
        root = tempfile.mkdtemp(prefix="sb ctx ")
        try:
            osd = os.path.join(root, "00-Operating-System")
            os.makedirs(osd)
            for name, text in (("output-standards.md", OUTPUT_STANDARDS), ("templates.md", TEMPLATES),
                               ("identity.md", IDENTITY), ("recurring-asks.md", RECURRING),
                               ("thinking-patterns.md", THINKING), ("active-areas.md", ACTIVE)):
                with open(os.path.join(osd, name), "w", encoding="utf-8") as fh:
                    fh.write(text)
            p = subprocess.run([sys.executable, CONTEXT], capture_output=True, text=True,
                               env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
            self.assertEqual(p.returncode, 0)
            self.assertLess(len(p.stdout), 10000)
            for marker in ("Live context", "Routing implication", "Closed debates", "T50 Resume architecture",
                           "Alpha programme"):
                self.assertIn(marker, p.stdout)
            os.makedirs(os.path.join(root, "03-Work"))
            open(os.path.join(root, "03-Work", "Deck v2.pptx"), "w").close()
            p = subprocess.run([sys.executable, CONTEXT], capture_output=True, text=True,
                               env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
            self.assertIn("Latest working files", p.stdout)
            self.assertIn("Deck v2.pptx", p.stdout)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
