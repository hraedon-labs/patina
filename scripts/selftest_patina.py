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

case(
    "edited token value WITH a recomputed stamp is caught by --upstream",
    True,
    lambda tmp, static: rewrite_block(
        static, get_block(static).replace("--crit: #cc6050", "--crit: #ff00ff"), True
    ),
    "--upstream",
    str(ROOT),
    expect="DRIFTED from upstream",
)

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


failed = [r for r in results if not r[0]]
for ok, name, code, out in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"      exit={code}")
        for line in out:
            print(f"      | {line}")
print(f"\nselftest_patina: {len(results) - len(failed)}/{len(results)} cases behaved")
sys.exit(1 if failed else 0)
