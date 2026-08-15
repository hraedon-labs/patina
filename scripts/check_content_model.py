#!/usr/bin/env python3
"""check_content_model.py -- the content-model change gate (Plan 008 WI-4).

ADVISORY BY DEFAULT. It prints and exits 0 unless you pass --blocking.

The rule it serves (content-model.md rule 4): a change that adds, removes or
relocates a field, control or editing surface must diff `UI-INVENTORY.md` in
the same change. The defect class is ambiguous ownership of mutable domain
state -- cert-watch's `hosts.notes` reached five write paths across two control
types because two features landed two months apart and nobody reconciled them.

Why this is not simply "templates changed => inventory must change":

  That heuristic is mechanical and only approximately correlated with what we
  care about. Plenty of template edits do not touch the content model, so as a
  BLOCKING rule it teaches exactly one behaviour -- modify UI-INVENTORY.md
  somehow until CI goes green -- and converts a review artifact into ceremonial
  churn. The correct inventory diff is very often zero bytes.

  So the gate accepts either answer, and distinguishes them in its output:

    inventory updated    the change is recorded
    attested unchanged   a commit in the range carries the trailer
                           Content-Model: reviewed-unchanged

  You cannot make attestation expensive -- an agent can produce any ceremony we
  invent. You can make it LEGIBLE. A trailer is better than touching a file
  precisely because nobody can mistake it for substantive work: it gives a
  reviewer a discrete claim to accept or challenge.

  General rule, learned from patina's own colour ratchet: never make meaningless
  file modification the cheapest way to satisfy a semantic gate.

Usage:
  check_content_model.py --base <ref> [--repo .] [--inventory UI-INVENTORY.md]
                         [--path templates] [--path routes] ... [--blocking]

Exit: 0 advisory (always) or clean; 1 only with --blocking and an unmet change.
"""

import argparse
import subprocess
import sys
from pathlib import Path

TRAILER = "Content-Model:"
ATTESTATION = "reviewed-unchanged"
DEFAULT_PATHS = ("templates", "routes", "views", "handlers")


def git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    return proc.stdout if proc.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--base", required=True, help="ref to diff against (e.g. main)")
    ap.add_argument("--inventory", default="UI-INVENTORY.md")
    ap.add_argument(
        "--path",
        action="append",
        default=[],
        help=f"path fragment marking UI-affecting files (default: {', '.join(DEFAULT_PATHS)})",
    )
    ap.add_argument(
        "--blocking",
        action="store_true",
        help="exit 1 when a UI-affecting change is neither recorded nor attested",
    )
    args = ap.parse_args()

    markers = tuple(args.path) or DEFAULT_PATHS
    rng = f"{args.base}..HEAD"

    changed = git(args.repo, "diff", "--name-only", rng)
    if changed is None:
        print(f"[skip] cannot diff {rng} in {args.repo}", file=sys.stderr)
        return 0
    files = [f for f in changed.splitlines() if f.strip()]
    if not files:
        print("check_content_model: no changes in range")
        return 0

    ui_files = [f for f in files if any(m in f for m in markers)]
    if not ui_files:
        print(f"check_content_model: no UI-affecting files in {rng}")
        return 0

    if any(f.endswith(args.inventory) for f in files):
        print(
            f"check_content_model: inventory updated -- {args.inventory} is in "
            f"the same range as {len(ui_files)} UI-affecting file(s)"
        )
        return 0

    log = git(args.repo, "log", "--format=%B%x00", rng) or ""
    attesting = [
        c for c in log.split("\x00") if f"{TRAILER} {ATTESTATION}" in c
    ]
    if attesting:
        subject = attesting[0].strip().splitlines()[0][:70]
        print(
            f"check_content_model: attested unchanged -- a commit in {rng} "
            f"carries `{TRAILER} {ATTESTATION}` ({subject})"
        )
        return 0

    print(f"check_content_model: {len(ui_files)} UI-affecting file(s) changed in {rng}")
    for f in ui_files[:10]:
        print(f"  {f}")
    if len(ui_files) > 10:
        print(f"  ... and {len(ui_files) - 10} more")
    print(
        f"\n{args.inventory} was not updated and no commit attests the content "
        "model was reviewed. Do one of:\n"
        f"  - update {args.inventory} (a concept gained, lost or moved a control), or\n"
        f"  - add `{TRAILER} {ATTESTATION}` as a commit trailer if it genuinely "
        "did not change.\n"
        "The second is a real answer, not a workaround: most template edits do "
        "not touch the content model."
    )
    return 1 if args.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
