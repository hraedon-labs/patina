#!/usr/bin/env python3
"""Stdlib-only reference-component sync and conformance checks (Plan 006).

Use disposable Git checkouts and consumers; never synchronize a real tool.
Run directly: python3 scripts/selftest_components.py
"""

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "component_gate", ROOT / "scripts/check_patina.py"
)
gate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate_module)


class ComponentChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="patina-components-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / "upstream"
        self.upstream.mkdir()
        for name in (
            ".gitattributes",
            "sync.sh",
            "tokens.css",
            "components.css",
            "theme.js",
            "VERSION",
            "macros/ui.j2",
            "scripts/check_patina.py",
            "accents/cert-watch.css",
        ):
            target = self.upstream / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        shutil.copytree(ROOT / "fonts", self.upstream / "fonts")
        self.git("init", "-q")
        self.git("config", "user.name", "Component Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.commit()
        self.static = self.root / "static"
        self.static.mkdir()
        self.templates = self.root / "templates"
        self.css = self.static / "css/components.css"
        self.macro = self.templates / "macros/ui.j2"

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.upstream), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Synthetic source snapshot")

    def sync(self, *flags, components=True):
        command = [str(self.upstream / "sync.sh"), *flags]
        if components:
            command += ["--components", str(self.templates)]
        return subprocess.run(
            command + ["cert-watch", str(self.static), str(self.root)],
            capture_output=True,
            text=True,
        )

    def check(self, upstream=True):
        gate = gate_module.Gate()
        gate_module.check_component(
            gate, self.css, "components.css", self.upstream if upstream else None
        )
        gate_module.check_component(
            gate, self.macro, "macros/ui.j2", self.upstream if upstream else None
        )
        return gate

    def restamp(self, path):
        text = path.read_bytes().decode()
        patterns = (
            (gate_module.JINJA_BEGIN_RE, gate_module.JINJA_END_RE)
            if path.suffix == ".j2"
            else (gate_module.BEGIN_RE, gate_module.END_RE)
        )
        _rev, stamp, block, _tail, _offset = gate_module.split_vendored(text, *patterns)
        path.write_text(
            text.replace(stamp, hashlib.sha256(block.encode()).hexdigest(), 1)
        )

    def test_default_sync_does_not_adopt_components(self):
        self.assertEqual(self.sync(components=False).returncode, 0)
        self.assertFalse(self.css.exists())
        self.assertFalse(self.macro.exists())

    def test_clean_component_sync_matches_its_recorded_revision(self):
        self.assertEqual(self.sync().returncode, 0)
        self.assertFalse(self.check().failures)

    def test_each_component_is_required_when_opted_in(self):
        for path in (self.css, self.macro):
            with self.subTest(path=path.name):
                self.assertEqual(self.sync().returncode, 0)
                path.unlink()
                self.assertTrue(self.check().failures)

    def test_css_and_macro_edits_fail_integrity(self):
        for path in (self.css, self.macro):
            with self.subTest(path=path.name):
                self.assertEqual(self.sync().returncode, 0)
                path.write_text(path.read_text().replace("pt-btn", "pt-edited", 1))
                self.assertTrue(self.check(upstream=False).failures)

    def test_restamped_edits_fail_upstream_comparison(self):
        for path in (self.css, self.macro):
            with self.subTest(path=path.name):
                self.assertEqual(self.sync().returncode, 0)
                path.write_text(path.read_text().replace("pt-btn", "pt-edited", 1))
                self.restamp(path)
                self.assertFalse(self.check(upstream=False).failures)
                self.assertTrue(
                    any("DRIFTED" in failure for failure in self.check().failures)
                )

    def test_uncommitted_upstream_edits_do_not_change_reference(self):
        self.assertEqual(self.sync().returncode, 0)
        (self.upstream / "components.css").write_text("/* uncommitted source */\n")
        self.assertFalse(self.check().failures)

    def test_newer_upstream_is_an_upgrade_not_a_failure(self):
        self.assertEqual(self.sync().returncode, 0)
        source = self.upstream / "components.css"
        source.write_text(source.read_text() + "/* additive source update */\n")
        self.commit()
        checked = self.check()
        self.assertFalse(checked.failures)
        self.assertTrue(any("upgrade is available" in note for note in checked.notes))

    def test_macro_and_css_can_have_independent_valid_revisions(self):
        self.assertEqual(self.sync().returncode, 0)
        old_macro = self.macro.read_bytes()
        source = self.upstream / "components.css"
        source.write_text(source.read_text() + "/* additive source update */\n")
        self.commit()
        self.assertEqual(self.sync().returncode, 0)
        self.macro.write_bytes(old_macro)
        self.assertFalse(self.check().failures)

    def test_consumer_tails_survive_resync_and_do_not_change_owned_hashes(self):
        self.assertEqual(self.sync().returncode, 0)
        tails = [
            ".local { color: var(--text); }\n",
            "{% macro local() %}Local{% endmacro %}\n",
        ]
        for path, tail in zip((self.css, self.macro), tails):
            path.write_text(path.read_text() + tail)
        self.assertEqual(self.sync().returncode, 0)
        for path, tail in zip((self.css, self.macro), tails):
            self.assertTrue(path.read_text().endswith(tail))
        self.assertFalse(self.check().failures)

    def test_unmarked_component_refusal_happens_before_tokens_change(self):
        self.assertEqual(self.sync(components=False).returncode, 0)
        tokens = self.static / "css/tokens.css"
        original = tokens.read_bytes()
        self.macro.parent.mkdir(parents=True)
        self.macro.write_text("{% macro mine() %}Hand written{% endmacro %}\n")
        self.assertNotEqual(self.sync().returncode, 0)
        self.assertEqual(tokens.read_bytes(), original)
        self.assertIn("Hand written", self.macro.read_text())
        self.assertFalse(self.css.exists())

    def test_nonterminated_consumer_tails_survive_byte_for_byte(self):
        self.assertEqual(self.sync().returncode, 0)
        tails = [
            b"/* local tail */\r\n.local { color: var(--text); }",
            b"{# local tail #}\r\n{% macro local() %}Local{% endmacro %}",
        ]
        for path, tail in zip((self.css, self.macro), tails):
            path.write_bytes(path.read_bytes() + tail)
        self.assertEqual(self.sync().returncode, 0)
        for path, tail in zip((self.css, self.macro), tails):
            self.assertTrue(path.read_bytes().endswith(tail))
        self.assertFalse(self.check().failures)

    def test_adopt_preserves_each_hand_written_file_in_a_backup(self):
        self.css.parent.mkdir(parents=True)
        self.macro.parent.mkdir(parents=True)
        for path in (self.css, self.macro):
            path.write_text("Original hand-written content\n")
        self.assertEqual(self.sync("--adopt").returncode, 0)
        for path in (self.css, self.macro):
            backups = list(path.parent.glob(path.name + ".pre-patina-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "Original hand-written content\n")
        self.assertFalse(self.check().failures)

    def test_duplicate_and_reversed_markers_are_refused(self):
        for path in (self.css, self.macro):
            for kind in ("duplicate", "reversed"):
                with self.subTest(path=path.name, kind=kind):
                    self.assertEqual(self.sync("--adopt").returncode, 0)
                    lines = path.read_text().splitlines(keepends=True)
                    if kind == "duplicate":
                        lines.append(lines[1])
                    else:
                        lines[1], lines[-1] = lines[-1], lines[1]
                    path.write_text("".join(lines))
                    self.assertTrue(self.check().failures)
                    self.assertNotEqual(self.sync().returncode, 0)

    def test_unknown_recorded_revision_fails(self):
        self.assertEqual(self.sync().returncode, 0)
        for path in (self.css, self.macro):
            text = path.read_text()
            path.write_text(
                text.replace(self.git("rev-parse", "--short", "HEAD"), "0000000")
            )
        self.assertTrue(self.check().failures)

    def test_windows_checkout_line_endings_preserve_ownership_and_resync(self):
        self.assertEqual(self.sync().returncode, 0)
        for path in (self.css, self.macro):
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertFalse(self.check().failures)
        self.assertEqual(self.sync().returncode, 0)
        self.assertFalse(self.check().failures)

    def test_source_checkout_keeps_lf_even_with_git_autocrlf(self):
        self.git("config", "core.autocrlf", "true")
        for source in ("components.css", "macros/ui.j2"):
            (self.upstream / source).unlink()
        self.git("checkout", "HEAD", "--", "components.css", "macros/ui.j2")
        for source in ("components.css", "macros/ui.j2"):
            self.assertNotIn(b"\r\n", (self.upstream / source).read_bytes())
        self.assertEqual(self.sync().returncode, 0)
        self.assertFalse(self.check().failures)

    def test_missing_component_flag_argument_fails_before_writes(self):
        proc = subprocess.run(
            [str(self.upstream / "sync.sh"), "--components"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertFalse((self.static / "css/tokens.css").exists())

    def run_gate(self, *args):
        return subprocess.run(
            [
                sys.executable,
                str(self.root / "patina-check.py"),
                str(self.static),
                "--components",
                str(self.templates),
                "--extra",
                str(self.templates),
                "--prefix",
                "pt",
                "--ratchet-file",
                str(self.root / "ratchet.json"),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def test_jinja_tail_colour_literals_do_not_escape_the_gate(self):
        self.assertEqual(self.sync().returncode, 0)
        self.assertEqual(self.run_gate("--update-ratchet").returncode, 0)
        self.macro.write_text(
            self.macro.read_text() + '<div style="color:#123456">Local</div>\n'
        )
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("colour-literal ratchet", result.stdout)

    def test_literal_jinja_class_names_must_have_rules(self):
        self.assertEqual(self.sync().returncode, 0)
        self.assertEqual(self.run_gate("--update-ratchet").returncode, 0)
        self.macro.write_text(
            self.macro.read_text() + '<div class="pt-missing">Local</div>\n'
        )
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("pt-missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
