#!/usr/bin/env python3
"""Exercise theme vendoring through the actual CLI and disposable Git history.

No network, consumer repository, or installed test framework is needed.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ThemeUpstreamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="patina-theme-upstream-")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.up = self.work / "patina"
        shutil.copytree(
            ROOT, self.up,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache"),
        )
        self.git("init", "-q")
        self.commit("initial fixture")
        self.pin = self.git("rev-parse", "--short", "HEAD").strip()
        self.static = self.work / "static"
        self.static.mkdir()
        subprocess.run(
            [str(self.up / "sync.sh"), "cert-watch", str(self.static), str(self.work)],
            check=True, stdout=subprocess.DEVNULL,
        )
        self.theme = self.static / "theme.js"
        self.body = self.theme.read_text(encoding="utf-8").split("\n", 1)[1]
        self.assertEqual(self.run_gate("--update-ratchet").returncode, 0)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.up), *args], text=True)

    def commit(self, message):
        self.git("add", ".")
        self.git(
            "-c", "user.name=theme selftest",
            "-c", "user.email=theme-selftest@example.invalid",
            "commit", "-qm", message,
        )

    def run_gate(self, *args):
        return subprocess.run(
            [sys.executable, str(self.work / "patina-check.py"), str(self.static),
             "--prefix", "tl", "--ratchet-file", str(self.work / "ratchet.json"), *args],
            capture_output=True, text=True,
        )

    def write_theme(self, body, rev):
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        revision = "" if rev is None else f" rev:{rev}"
        self.theme.write_text(
            f"// patina:sha256 {digest}{revision}\n{body}", encoding="utf-8",
        )

    def assert_result(self, proc, success, message):
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode == 0, success, output)
        self.assertIn(message, output)

    def test_current_theme_matches_recorded_revision(self):
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), True,
            "theme.js matches patina at its stamped rev",
        )

    def test_edited_body_still_fails_without_upstream(self):
        self.theme.write_text(self.theme.read_text() + "// local change\n")
        self.assert_result(self.run_gate(), False, "theme.js: bytes differ from stamp")

    def test_local_stamp_checks_integrity_when_upstream_is_omitted(self):
        self.write_theme(self.body + "// local change\n", self.pin)
        self.assert_result(self.run_gate(), True, "theme.js intact")

    def test_changed_and_restamped_body_does_not_match_recorded_revision(self):
        self.write_theme(self.body + "// local change\n", self.pin)
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), False, "theme.js DRIFTED",
        )

    def test_newer_committed_theme_is_an_upgrade(self):
        (self.up / "theme.js").write_text(self.body + "// available update\n")
        self.commit("advance theme")
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), True,
            "theme.js upgrade is available",
        )

    def test_uncommitted_upstream_edit_does_not_change_the_reference(self):
        (self.up / "theme.js").write_text(self.body + "// unfinished work\n")
        proc = self.run_gate("--upstream", str(self.up))
        self.assert_result(proc, True, "theme.js matches patina at its stamped rev")
        self.assertNotIn("theme.js upgrade is available", proc.stdout)

    def test_syncing_uncommitted_theme_does_not_claim_the_old_revision(self):
        (self.up / "theme.js").write_text(self.body + "// unfinished work\n")
        subprocess.run(
            [str(self.up / "sync.sh"), "cert-watch", str(self.static), str(self.work)],
            check=True, stdout=subprocess.DEVNULL,
        )
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), False,
            "commit the change in patina and re-sync",
        )

    def test_theme_and_tokens_may_have_independent_valid_pins(self):
        old_theme = self.theme.read_bytes()
        (self.up / "theme.js").write_text(self.body + "// available update\n")
        self.commit("advance theme")
        subprocess.run(
            [str(self.up / "sync.sh"), "cert-watch", str(self.static), str(self.work)],
            check=True, stdout=subprocess.DEVNULL,
        )
        self.theme.write_bytes(old_theme)
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), True,
            "theme.js upgrade is available",
        )

    def test_legacy_hash_only_stamp_still_checks_integrity(self):
        self.write_theme(self.body, None)
        self.assert_result(self.run_gate(), True, "theme.js intact")

    def test_upstream_requires_a_recorded_theme_revision(self):
        self.write_theme(self.body, None)
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), False,
            "theme.js: no revision in its stamp",
        )

    def test_missing_recorded_revision_is_reported(self):
        self.write_theme(self.body, "0123456789012345678901234567890123456789")
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), False,
            "theme.js: stamped revision",
        )

    def test_revision_without_theme_file_is_reported(self):
        (self.up / "theme.js").unlink()
        self.commit("fixture without theme")
        self.write_theme(self.body, self.git("rev-parse", "--short", "HEAD").strip())
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), False,
            "does not contain theme.js",
        )

    def test_new_head_without_theme_does_not_invalidate_existing_pin(self):
        (self.up / "theme.js").unlink()
        self.commit("fixture without theme")
        self.assert_result(
            self.run_gate("--upstream", str(self.up)), True,
            "theme.js matches patina at its stamped rev",
        )

    def test_no_theme_consumer_does_not_require_a_theme_file(self):
        self.theme.unlink()
        proc = self.run_gate("--no-theme", "--upstream", str(self.up))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("theme.js", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
