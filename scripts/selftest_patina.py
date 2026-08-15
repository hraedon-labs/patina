#!/usr/bin/env python3
"""selftest_patina.py -- prove the conformance gate actually refuses.

Every case here is a hole that a 2026-08-15 adversarial audit walked through
while check_patina.py reported "clean". A gate nobody tests is prose with a
shebang, so these are regression tests for the refusals themselves, not for
the happy path.

Builds a throwaway consumer with sync.sh in a temp dir, mutates it, and asserts
the gate's exit code and message. Stdlib only; no pytest dependency in patina.

Usage: selftest_patina.py [path-to-patina-checkout]
Exit:  0 all cases behaved, 1 otherwise.
"""

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PY = sys.executable

results = []


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_consumer(tmp):
    """A freshly vendored, conformant consumer with one tool CSS file."""
    static = tmp / "static"
    (static / "css").mkdir(parents=True)
    (static / "css" / "tool.css").write_text(
        ".x { color: var(--text); background: var(--panel); }\n", encoding="utf-8"
    )
    proc = subprocess.run(
        [str(ROOT / "sync.sh"), "--no-theme", "cert-watch", str(static), str(tmp)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"sync.sh failed to build fixture:\n{proc.stderr}"
    return static


def gate(tmp, static, *extra):
    return subprocess.run(
        [
            PY,
            str(tmp / "patina-check.py"),
            str(static),
            "--prefix",
            "tl",
            "--no-theme",
            "--ratchet-file",
            str(tmp / "ratchet.json"),
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def baseline(tmp, static):
    gate(tmp, static, "--update-ratchet")


def case(name, want_fail, mutate, *gate_args, expect=None, rebaseline=False):
    """mutate(tmp, static) -> None. Asserts exit code, and that `expect`
    appears in the output when given. `rebaseline` re-records the ratchet after
    the mutation, modelling a reviewer who accepted the change deliberately."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = build_consumer(tmp)
        baseline(tmp, static)
        mutate(tmp, static)
        if rebaseline:
            baseline(tmp, static)
        proc = gate(tmp, static, *gate_args)
        out = proc.stdout + proc.stderr
        failed = proc.returncode != 0
        ok = failed == want_fail and (expect is None or expect in out)
        results.append((ok, name, proc.returncode, out.strip().splitlines()))


def rewrite_block(static, new_block, restamp):
    """Replace the vendored block; optionally recompute the stamp over it."""
    p = static / "css" / "tokens.css"
    text = p.read_text(encoding="utf-8")
    m = re.search(
        r"(^/\* patina:begin (\S+) sha256:)([0-9a-f]{64})( \*/$\n)(.*?)(^/\* patina:end \*/$)",
        text,
        re.M | re.S,
    )
    assert m, "fixture lost its markers"
    stamp = sha(new_block) if restamp else m.group(3)
    p.write_text(
        text[: m.start()]
        + m.group(1)
        + stamp
        + m.group(4)
        + new_block
        + m.group(6)
        + text[m.end() :],
        encoding="utf-8",
    )


def get_block(static):
    text = (static / "css" / "tokens.css").read_text(encoding="utf-8")
    return re.search(r"^/\* patina:begin .*? \*/$\n(.*?)^/\* patina:end \*/$", text, re.M | re.S).group(1)


# --- the cases -------------------------------------------------------------

case(
    "clean vendored consumer passes",
    False,
    lambda tmp, static: None,
)

case(
    "edited token value without restamping fails",
    True,
    lambda tmp, static: rewrite_block(
        static, get_block(static).replace("--crit: #cc6050", "--crit: #ff00ff"), False
    ),
    expect="EDITED after vendoring",
)

# The edited-and-re-stamped case lives in selftest_upstream_version_semantics
# instead: it needs an upstream whose working tree and HEAD agree, or the case
# passes whenever this checkout merely has uncommitted changes -- i.e. for the
# wrong reason.

case(
    "violations appended below patina:end are not exempt",
    True,
    lambda tmp, static: (static / "css" / "tokens.css").open("a", encoding="utf-8").write(
        "\n:root { --bg: #ff0000; }\n.evil { color: #123456; }\n"
    ),
    expect="redefines contract token",
)

case(
    "a validly stamped EMPTY block fails instead of disabling the checks",
    True,
    lambda tmp, static: rewrite_block(static, "", True),
    expect="defines no tokens",
)

case(
    "swapping one colour literal for another fails the fingerprint ratchet",
    True,
    lambda tmp, static: (static / "css" / "tool.css").write_text(
        ".x { color: var(--text); background: var(--panel); }\n"
        ".y { color: #bada55; }\n",
        encoding="utf-8",
    ),
    expect="NEW violation",
)

case(
    "patina-allow without a reason is refused",
    True,
    lambda tmp, static: (static / "css" / "tool.css").write_text(
        ".y { color: #bada55; } /* patina-allow */\n", encoding="utf-8"
    ),
    expect="without a reason",
)

case(
    "a NEW exemption trips the exemption ratchet (hatches are reviewed, not free)",
    True,
    lambda tmp, static: (static / "css" / "tool.css").write_text(
        ".y { color: #bada55; } /* patina-allow: brand mark, fixed by contract */\n",
        encoding="utf-8",
    ),
    expect="exemption ratchet",
)

case(
    "a BASELINED exemption with a reason exempts the line",
    False,
    lambda tmp, static: (static / "css" / "tool.css").write_text(
        ".x { color: var(--text); }\n"
        ".y { color: #bada55; } /* patina-allow: brand mark, fixed by contract */\n",
        encoding="utf-8",
    ),
    rebaseline=True,
)

case(
    "a duplicated end marker is reported as malformed, not as an edit",
    True,
    lambda tmp, static: (static / "css" / "tokens.css").open("a", encoding="utf-8").write(
        "\n/* patina:end */\n"
    ),
    expect="malformed vendor markers",
)

case(
    "an edited vendored checker refuses to run",
    True,
    lambda tmp, static: (tmp / "patina-check.py").open("a", encoding="utf-8").write(
        "# tampered\n"
    ),
    expect="differ from its stamp",
)

case(
    "removing a baselined violation passes (cleanup is never punished)",
    False,
    lambda tmp, static: (static / "css" / "tool.css").write_text(
        ".x { color: var(--text); }\n", encoding="utf-8"
    ),
)


# --- sync.sh refusal (its own fixture shape, no gate involved) -------------

def selftest_sync_refuses():
    """sync.sh must not overwrite a hand-maintained tokens.css. This is the
    data-loss case: the awk tail-extraction silently yields nothing when the
    end marker is absent."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = tmp / "static"
        (static / "css").mkdir(parents=True)
        target = static / "css" / "tokens.css"
        target.write_text("/* mine */\n.IRREPLACEABLE { color: red; }\n", encoding="utf-8")
        proc = subprocess.run(
            [str(ROOT / "sync.sh"), "--no-theme", "cert-watch", str(static), str(tmp)],
            capture_output=True,
            text=True,
        )
        survived = "IRREPLACEABLE" in target.read_text(encoding="utf-8")
        ok = proc.returncode != 0 and survived
        results.append(
            (
                ok,
                "sync.sh refuses to overwrite an unmarked tokens.css",
                proc.returncode,
                (proc.stdout + proc.stderr).strip().splitlines(),
            )
        )

        # ...and --adopt is the documented way through, with a backup.
        proc = subprocess.run(
            [
                str(ROOT / "sync.sh"), "--no-theme", "--adopt",
                "cert-watch", str(static), str(tmp),
            ],
            capture_output=True,
            text=True,
        )
        backups = list((static / "css").glob("tokens.css.pre-patina-*"))
        ok = (
            proc.returncode == 0
            and len(backups) == 1
            and "IRREPLACEABLE" in backups[0].read_text(encoding="utf-8")
        )
        results.append(
            (
                ok,
                "sync.sh --adopt backs the old file up before vendoring",
                proc.returncode,
                (proc.stdout + proc.stderr).strip().splitlines(),
            )
        )


selftest_sync_refuses()


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )


def _commit(repo, msg):
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c", "user.email=selftest@example.invalid",
        "-c", "user.name=selftest",
        "commit", "-qm", msg,
    )


def selftest_upstream_version_semantics():
    """A newer patina is an available upgrade, not a conformance failure.

    The first version of check_upstream compared against the upstream WORKING
    TREE, so a single commit to patina reported every consumer in the estate as
    DRIFTED -- reintroducing exactly the cross-repo coupling vendoring exists to
    avoid. Drift is measured against the revision the copy is stamped with.

    Built from a copied-and-committed patina so the fixture's working tree and
    HEAD agree by construction, rather than depending on this checkout's state.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        up = tmp / "patina-up"
        shutil.copytree(ROOT, up, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        _git(up, "init", "-q")
        _commit(up, "fixture")

        static = tmp / "static"
        (static / "css").mkdir(parents=True)
        (static / "css" / "tool.css").write_text(
            ".x { color: var(--text); }\n", encoding="utf-8"
        )
        subprocess.run(
            [str(up / "sync.sh"), "--no-theme", "cert-watch", str(static), str(tmp)],
            capture_output=True,
            text=True,
        )
        ratchet = tmp / "ratchet.json"

        def run(*extra):
            return subprocess.run(
                [
                    PY, str(tmp / "patina-check.py"), str(static),
                    "--prefix", "tl", "--no-theme",
                    "--ratchet-file", str(ratchet), *extra,
                ],
                capture_output=True,
                text=True,
            )

        run("--update-ratchet")

        proc = run("--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "matches patina at its stamped rev" in out,
                "a current vendored copy verifies against its stamped rev",
                proc.returncode,
                out.strip().splitlines(),
            )
        )

        # patina moves on. The consumer has not changed and is still conformant.
        tokens = up / "tokens.css"
        tokens.write_text(
            tokens.read_text(encoding="utf-8").replace(
                "--info: #60aeda", "--info: #60aedb"
            ),
            encoding="utf-8",
        )
        _commit(up, "advance patina")
        proc = run("--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "upgrade is available" in out,
                "a newer upstream is reported as an upgrade, never a failure",
                proc.returncode,
                out.strip().splitlines(),
            )
        )

        # Editing the block and re-computing its stamp defeats the integrity
        # check by construction; the pinned-rev comparison is what catches it.
        toks = static / "css" / "tokens.css"
        text = toks.read_text(encoding="utf-8")
        m = re.search(
            r"(^/\* patina:begin \S+ sha256:)([0-9a-f]{64})( \*/$\n)(.*?)(^/\* patina:end \*/$)",
            text,
            re.M | re.S,
        )
        tampered = m.group(4).replace("--crit: #cc6050", "--crit: #ff00ff")
        toks.write_text(
            text[: m.start()] + m.group(1) + sha(tampered) + m.group(3)
            + tampered + m.group(5) + text[m.end() :],
            encoding="utf-8",
        )
        proc = run("--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "DRIFTED from patina" in out,
                "an edited-and-re-stamped block is caught against its pinned rev",
                proc.returncode,
                out.strip().splitlines(),
            )
        )

        # Vendored docs follow the same version semantics as the token block.
        docs = tmp / "vendor-docs"
        docs.mkdir()
        subprocess.run(
            [
                str(up / "sync.sh"), "--no-theme", "--docs", str(docs),
                "cert-watch", str(static), str(tmp),
            ],
            capture_output=True, text=True,
        )
        proc = run("--docs", str(docs), "--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "vendored docs intact" in out,
                "docs: vendored rules verify against their manifest and patina",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        # patina's docs move on; the consumer is behind, not broken.
        adoc = up / "docs" / "adoption.md"
        adoc.write_text(adoc.read_text(encoding="utf-8") + "\n<!-- later -->\n", encoding="utf-8")
        _commit(up, "advance a doc")
        proc = run("--docs", str(docs), "--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "upgrade is available, not a failure" in out,
                "docs: an upstream doc change is an upgrade, never a failure",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        # Editing a vendored rule locally is drift.
        (docs / "content-model.md").write_text("# mine now\n", encoding="utf-8")
        proc = run("--docs", str(docs))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "banner removed" in out,
                "docs: an edited vendored rule is refused",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        # A stamp naming a revision that no longer exists cannot be verified.
        toks.write_text(
            re.sub(
                r"(/\* patina:begin )\S+( sha256:)",
                r"\g<1>deadbeef\g<2>",
                toks.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )
        proc = run("--upstream", str(up))
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "does not exist" in out,
                "a stamped rev absent from upstream is refused, not guessed",
                proc.returncode,
                out.strip().splitlines(),
            )
        )


selftest_upstream_version_semantics()


DECL_BASE = """[patina]
version = "0.5.0"
accent = "cert-watch"

[conformance.vendor]
state = "enforced"

[conformance.contract]
state = "enforced"
"""

DECL_NA_MODEL = """
[conformance.content_model]
state = "not-applicable"
why = "read-only analysis tool, no persisted mutable state"
"""

DECL_OK = DECL_BASE + DECL_NA_MODEL + """
[conformance.structure]
state = "deferred"
why = "no surface briefs written yet"
until = "the first page rewrite, or a second tool reaching for this shape"
"""


def selftest_declaration():
    """The declaration is what makes partial adoption legitimate, so its
    refusals matter as much as the gate's. Every case below is an escape hatch
    that would otherwise make "all green" cheap and therefore meaningless."""
    cases = [
        ("an honest partial declaration passes", DECL_OK, False, ""),
        (
            "a facet cannot claim a mechanism that does not exist",
            DECL_BASE + DECL_NA_MODEL + '\n[conformance.structure]\nstate = "enforced"\n',
            True,
            "cannot be 'enforced'",
        ),
        (
            "deferred without a trigger is refused",
            DECL_BASE + DECL_NA_MODEL
            + '\n[conformance.structure]\nstate = "deferred"\nwhy = "not worth doing right now"\n',
            True,
            "needs a substantive `until`",
        ),
        (
            "not-applicable without a real reason is refused",
            DECL_BASE
            + '\n[conformance.content_model]\nstate = "not-applicable"\nwhy = "n/a"\n'
            + '\n[conformance.structure]\nstate = "not-applicable"\nwhy = "n/a"\n',
            True,
            "needs a substantive `why`",
        ),
        (
            "omitting a facet is refused -- silence is what this file removes",
            DECL_BASE
            + '\n[conformance.structure]\nstate = "not-applicable"\nwhy = "read-only analysis tool, no editing"\n',
            True,
            "no claim made for content_model",
        ),
        (
            "an invented facet is refused",
            DECL_OK + '\n[conformance.vibes]\nstate = "enforced"\n',
            True,
            "unknown conformance facet",
        ),
        (
            "attested without evidence is refused -- it is the agent-authored "
            "estate's honest state and must record the most, not the least",
            DECL_BASE
            + '\n[conformance.content_model]\nstate = "attested"\n'
            + '\n[conformance.structure]\nstate = "not-applicable"\nwhy = "read-only analysis tool, no editing"\n',
            True,
            "needs a substantive `evidence`",
        ),
        (
            "attested WITH evidence passes",
            DECL_BASE
            + '\n[conformance.content_model]\nstate = "attested"\nevidence = "one concept one control: snapshot via /ingest, triage via /findings/{id}/triage"\n'
            + '\n[conformance.structure]\nstate = "not-applicable"\nwhy = "read-only analysis tool, no editing"\n',
            False,
            "",
        ),
    ]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = build_consumer(tmp)
        baseline(tmp, static)
        for name, body, want_fail, expect in cases:
            decl = tmp / "patina.toml"
            decl.write_text(body, encoding="utf-8")
            proc = gate(tmp, static, "--declaration", str(decl))
            out = proc.stdout + proc.stderr
            ok = (proc.returncode != 0) == want_fail and (not expect or expect in out)
            results.append((ok, name, proc.returncode, out.strip().splitlines()))


selftest_declaration()


def selftest_undefined_classes():
    """A class named in markup with no rule renders as an unstyled div, and no
    other check in the gate notices. cert-watch shipped `cw-gap-9` referenced
    for months while undefined; gpo-lens's adoption surfaced twelve more,
    including an entire posture grid."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = build_consumer(tmp)
        (static / "css" / "tool.css").write_text(
            ".tl-panel { color: var(--text); }\n", encoding="utf-8"
        )
        tpl = tmp / "templates"
        tpl.mkdir()
        (tpl / "page.html").write_text(
            '<div class="tl-panel">ok</div>\n', encoding="utf-8"
        )

        def run(*extra):
            return subprocess.run(
                [
                    PY, str(tmp / "patina-check.py"), str(static),
                    "--prefix", "tl", "--no-theme", "--extra", str(tpl),
                    "--ratchet-file", str(tmp / "ratchet.json"), *extra,
                ],
                capture_output=True,
                text=True,
            )

        run("--update-ratchet")
        proc = run()
        results.append(
            (
                proc.returncode == 0 and "has a rule" in proc.stdout,
                "undefined classes: fully-styled markup passes",
                proc.returncode,
                [],
            )
        )

        (tpl / "page.html").write_text(
            '<div class="tl-panel"><span class="tl-ghost">x</span></div>\n',
            encoding="utf-8",
        )
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "tl-ghost" in out,
                "undefined classes: a class with no rule anywhere fails",
                proc.returncode,
                out.strip().splitlines()[:3],
            )
        )

        # Dynamic names cannot be checked, and guessing would teach people to
        # distrust the gate.
        (tpl / "page.html").write_text(
            '<div class="tl-panel"><span class="{{ tone }}">x</span></div>\n',
            encoding="utf-8",
        )
        proc = run()
        results.append(
            (
                proc.returncode == 0,
                "undefined classes: template-computed names are skipped, not guessed",
                proc.returncode,
                (proc.stdout + proc.stderr).strip().splitlines()[:3],
            )
        )


selftest_undefined_classes()


def selftest_css_grammar_boundaries():
    """Every syntax that has fooled this checker becomes a permanent fixture.

    The severity of a mechanically enforced rule sets the required confidence
    of its detector: `.ds-btn--crit:hover` was reported as shadowing a status
    colour, which is the strongest accusation the contract makes, on a line
    that declares nothing. A cosmetic advisory can tolerate noise; a blocking
    claim of contract corruption cannot.

    Standing limit, recorded rather than tested: do NOT keep adding regex
    cleverness to emulate CSS grammar. If the checker needs materially more
    understanding than this, a real parser is the safer answer.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = build_consumer(tmp)
        tpl = tmp / "templates"
        tpl.mkdir()
        (tpl / "p.html").write_text(
            '<div class="tl-a tl-b tl-c tl-d">x</div>\n', encoding="utf-8"
        )
        (static / "css" / "tool.css").write_text(
            # pseudo-class after a BEM modifier
            ".tl-a--crit:hover { color: var(--crit); }\n"
            # selectors nested in @supports
            "@supports (display: grid) {\n  .tl-a { color: var(--text); }\n}\n"
            # selectors nested two at-rules deep
            "@media print {\n  @supports (color: red) {\n"
            "    .tl-b { color: var(--text); }\n  }\n}\n"
            # a declaration VALUE that looks like a class, inside a nested
            # at-rule -- must not mint a definition
            "@media screen {\n  .tl-c { content: \".tl-phantom\"; }\n}\n"
            ".tl-d { color: var(--text); }\n",
            encoding="utf-8",
        )

        def run(*extra):
            return subprocess.run(
                [
                    PY, str(tmp / "patina-check.py"), str(static),
                    "--prefix", "tl", "--no-theme", "--extra", str(tpl),
                    "--ratchet-file", str(tmp / "ratchet.json"), *extra,
                ],
                capture_output=True, text=True,
            )

        run("--update-ratchet")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0,
                "CSS grammar boundaries: BEM + @supports + nested at-rules all read correctly",
                proc.returncode, out.strip().splitlines()[:5],
            )
        )

        # The phantom must not become a definition that masks a real dead class.
        (tpl / "p.html").write_text(
            '<div class="tl-a tl-b tl-c tl-d tl-phantom">x</div>\n', encoding="utf-8"
        )
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "tl-phantom" in out,
                "a class name appearing only in a declaration value is not a definition",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )


selftest_css_grammar_boundaries()


def selftest_regression_from_adoptions():
    """Defects the three adoptions found in the gate itself. Each was patina
    accusing a consumer of a violation the consumer had not committed."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        static = build_consumer(tmp)
        tpl = tmp / "templates"
        tpl.mkdir()

        def run(*extra):
            return subprocess.run(
                [
                    PY, str(tmp / "patina-check.py"), str(static),
                    "--prefix", "tl", "--no-theme", "--extra", str(tpl),
                    "--ratchet-file", str(tmp / "ratchet.json"), *extra,
                ],
                capture_output=True, text=True,
            )

        # dossier: a BEM modifier is not a custom-property declaration, and
        # `.x--crit:hover` is not shadowing a status colour.
        (static / "css" / "tool.css").write_text(
            ".tl-btn--primary:hover { color: var(--text); }\n"
            ".tl-btn--crit:hover { color: var(--crit); }\n",
            encoding="utf-8",
        )
        (tpl / "p.html").write_text(
            '<a class="tl-btn--primary">x</a><a class="tl-btn--crit">y</a>\n',
            encoding="utf-8",
        )
        run("--update-ratchet")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0,
                "BEM modifiers are not token declarations (`.x--crit:hover`)",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        # dossier: selectors inside @media were invisible, so responsive and
        # print-only classes were reported dead.
        (static / "css" / "tool.css").write_text(
            "@media print {\n  .tl-only-print { color: var(--text); }\n}\n"
            ".tl-normal { color: var(--text); }\n",
            encoding="utf-8",
        )
        (tpl / "p.html").write_text(
            '<div class="tl-only-print tl-normal">x</div>\n', encoding="utf-8"
        )
        run("--update-ratchet")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "has a rule" in out,
                "classes defined inside @media are not reported dead",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        # dossier: re-mapping contract tokens for a context patina does not
        # define (paper) is legal WITH a reason, and refused without one.
        (static / "css" / "tool.css").write_text(
            "@media print {\n  :root { --bg: #fff; --text: #000; }\n}\n",
            encoding="utf-8",
        )
        (tpl / "p.html").write_text("<div>x</div>\n", encoding="utf-8")
        run("--update-ratchet")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode != 0 and "with no stated reason" in out,
                "an unexplained at-rule re-map of a contract token is refused",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )

        (static / "css" / "tool.css").write_text(
            "@media print {\n"
            "  /* patina-allow-context: paper is not a context patina defines; the\n"
            "     substrate colour is not the document's to choose */\n"
            "  :root { --bg: #fff; --text: #000; }\n"
            "}\n",
            encoding="utf-8",
        )
        run("--update-ratchet")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "re-mapped inside at-rules" in out,
                "an at-rule re-map WITH a stated reason is legal and reported",
                proc.returncode, out.strip().splitlines()[:6],
            )
        )

        # `patina-allow-context:` contains `patina-allow` as a substring, so
        # the colour-literal scanner must not read a legitimate context reason
        # as an allow with no reason. Overlapping marker names, found by the
        # fixture above rather than in a consumer.
        results.append(
            (
                "without a reason" not in out,
                "the context marker is not mistaken for a bare colour allow",
                proc.returncode, out.strip().splitlines()[:4],
            )
        )


selftest_regression_from_adoptions()


def selftest_content_model():
    """The advisory content-model gate must accept BOTH answers -- an updated
    inventory and an explicit attestation that nothing changed -- and must say
    which one it got. If only the file edit satisfies it, the cheapest way to
    green is to touch the file, and the artifact stops meaning anything."""
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "consumer"
        (repo / "templates").mkdir(parents=True)
        (repo / "UI-INVENTORY.md").write_text("# inventory\n", encoding="utf-8")
        (repo / "templates" / "page.html").write_text("<p>a</p>\n", encoding="utf-8")
        _git(repo, "init", "-q")
        _commit(repo, "base")
        base = (_git(repo, "rev-parse", "HEAD").stdout or "").strip()

        script = str(ROOT / "scripts" / "check_content_model.py")

        def run(*extra):
            return subprocess.run(
                [PY, script, "--repo", str(repo), "--base", base, *extra],
                capture_output=True,
                text=True,
            )

        # 1. UI change, nothing recorded, nothing attested.
        (repo / "templates" / "page.html").write_text("<p>b</p>\n", encoding="utf-8")
        _commit(repo, "tweak the page")
        proc = run()
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "UI-affecting file(s) changed" in out,
                "content model: an unrecorded UI change is reported (advisory, exit 0)",
                proc.returncode,
                out.strip().splitlines()[:4],
            )
        )
        proc = run("--blocking")
        results.append(
            (
                proc.returncode == 1,
                "content model: --blocking turns the same finding into a failure",
                proc.returncode,
                [],
            )
        )

        # 2. The same change, attested as reviewed-unchanged.
        (repo / "templates" / "page.html").write_text("<p>c</p>\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(
            repo,
            "-c", "user.email=selftest@example.invalid",
            "-c", "user.name=selftest",
            "commit", "-qm",
            "tweak again\n\nContent-Model: reviewed-unchanged",
        )
        proc = run("--blocking")
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "attested unchanged" in out,
                "content model: a trailer attestation satisfies it, and says so",
                proc.returncode,
                out.strip().splitlines()[:3],
            )
        )

        # 3. An actual inventory diff, reported distinctly from an attestation.
        (repo / "UI-INVENTORY.md").write_text("# inventory\n\n- notes\n", encoding="utf-8")
        _commit(repo, "record the new concept")
        proc = run("--blocking")
        out = proc.stdout + proc.stderr
        results.append(
            (
                proc.returncode == 0 and "inventory updated" in out,
                "content model: an inventory diff is reported distinctly from an attestation",
                proc.returncode,
                out.strip().splitlines()[:3],
            )
        )


selftest_content_model()


failed = [r for r in results if not r[0]]
for ok, name, code, out in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"      exit={code}")
        for line in out:
            print(f"      | {line}")
print(f"\nselftest_patina: {len(results) - len(failed)}/{len(results)} cases behaved")
sys.exit(1 if failed else 0)
