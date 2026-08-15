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
