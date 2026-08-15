# Plan 005 — conformance gate (drift detection becomes mechanical)

**Status:** partially executed, record corrected 2026-08-15. **WI-1 (stamp +
delimiters in `sync.sh`, `scripts/check_patina.py`), WI-2 (smoke test on
sluice) and WI-3 (cert-watch reconciliation) are done and shipped.** WI-4
(dossier extraction), WI-5 (gpo-lens + switchboard) and WI-6 (optional
`impeccable detect` evaluation) are **open**. **Owner:** patina + each consumer.
**Pilot substrate: cert-watch** (owner's call, 2026-08-14) — it is the hardest
case (forked token names), so passing there proves the mechanism.
~~sluice is the smoke test (already clean).~~ **CORRECTED 2026-08-15:** sluice
was the smoke test and WI-2 ran, but "already clean" was wrong — see WI-2 and
"Open question: sluice" below.

## Problem

Every patina enforcement point is aspirational prose, and every one of them
failed:

- The "do not edit" banner: dossier wrote ~830 lines of `ds-` components into
  its vendored `tokens.css` (flagged in its 2026-07-01 reflection, still open).
- "Keep names and values in sync by hand": gpo-lens hand-syncs; its `theme.js`
  has silently diverged.
- The contract itself: cert-watch forked — same values, renamed tokens
  (`--sp-1..6` for `--space-1..6`, no `-soft` family, private additions) — so a
  mechanical re-sync would now break it.
- Plan 001 (adoption) still says "not started" while two tools carry vendored
  banners — the record drifted from reality too. (That instance is fixed:
  `plans/001` carries a corrected status paragraph as of 2026-08-14. The
  general problem is not — this plan's own status line was wrong until
  2026-08-15.)
- The source repo was not cloned on the dev machine until 2026-08-14. An
  invisible source of truth is no source of truth.

Nothing anywhere fails when a vendored copy diverges. Prose asks; only tests
refuse.

## Direction

patina ships the check; consumers run it in CI.

1. **Stamp on sync.** `sync.sh` writes a header line into the vendored file:
   `/* patina <short-commit> sha256:<hash of the patina-owned block> */`.
   The patina-owned block is delimited (`/* patina:begin */ ... /* patina:end */`)
   so a consumer may append below it but never edit inside it.
2. **`scripts/check_patina.py`** (stdlib-only Python — every family tool is
   Python; no Node dependency): given a consumer's static dir,
   - **conformance:** recompute the delimited block's hash; fail on mismatch;
   - **contract names:** every `--token` referenced in the tool's component CSS
     that is not defined by the tool must exist in the contract. New rule this
     plan adds to `docs/token-contract.md`: shared tokens are unprefixed;
     tool-owned extension tokens MUST carry the tool prefix (`--cw-topbar-h`,
     not `--topbar-h`) so contract and local vocabulary cannot collide;
   - **literal ratchet:** count raw colour/size literals (`#hex`, `rgb(`,
     bare `px` in declarations) outside the vendored file, against a committed
     allowlist + count file. The count ONLY GOES DOWN (the cert-watch
     `test_no_inline_styles.py` ratchet pattern, generalised). This makes
     deterministic what Hallmark's gate 48 leaves to model self-grading —
     "mid-render token improvisation" is the documented way agent edits erode
     a system.
3. **Consumers** add one CI step invoking the vendored check (the script itself
   is vendored by `sync.sh` so air-gapped repos need no cross-repo fetch).

## Work items

- **WI-1 — DONE.** Stamp + delimiters in `sync.sh`; `scripts/check_patina.py`
  with the three checks above and a `--report` mode that prints per-consumer
  drift status (for the periodic estate audit).
- **WI-2 — DONE (executed; the result was a finding, not a pass).** Smoke test
  on sluice. ~~Should pass untouched; proves no false positives on a clean
  consumer.~~ It does not pass. Re-run 2026-08-15,
  `check_patina.py --report <sluice static dir>` reports **3 failures**: no
  stamped patina block in `tokens.css` (unstamped legacy vendored copy — it
  predates WI-1's stamp), no `patina:sha256` stamp on `theme.js`, and no ratchet
  baseline. The token-contract check passes (29 names referenced, all resolve,
  0 tool-local). So the smoke test proved the gate *fires* on a legacy consumer,
  not that it is quiet on a clean one — sluice was never a clean consumer.
  Whether sluice gets re-synced to clear this is the open question below, not a
  foregone conclusion.
- **WI-3 — DONE.** cert-watch reconciliation (the pilot). Map `--sp-*` back to
  `--space-*` (values already identical); add the missing `-soft` family;
  re-prefix its private tokens (`--expired`, `--accent-fg`, `--backdrop`,
  `--pad-panel`, `--pad-page`, `--topbar-h`) to `--cw-*` or propose the
  genuinely general ones for the contract; re-vendor via `sync.sh`; visual
  baselines must stay green (cert-watch already has the screenshot CI to prove
  no pixel change). This also completes Plan 001 WI-2 at last.
- **WI-4 — OPEN — dossier extraction.** Move the ~830 `ds-` lines to
  `dossier.css` below the delimited block; re-vendor; gate on.
- **WI-5 — OPEN — gpo-lens + switchboard.** gpo-lens: adopt the vendored file
  (Plan 001 WI-1). switchboard: fresh adoption — new accent in `accents/`,
  registry entry. ~~(note: `docs/token-contract.md` accent table is missing
  sluice today; fix that while in there)~~ — **stale, removed 2026-08-15:** the
  sluice row is in the accent table (`docs/token-contract.md`, "Accent
  registry"); switchboard's is the one still absent, and it lands with this
  work item.
- **WI-6 — OPEN — Timeboxed evaluation (optional): `impeccable detect`.** Run
  pbakaus/impeccable's deterministic scanner against cert-watch's *rendered*
  pages (its page-level rules skip Jinja fragments — scan saved responses or
  URLs, not templates). Keep it only if it catches real defects the gate and
  visual baselines miss; it is a complement, not the mechanism of record.

## Open question: sluice's status (unresolved — owner call)

**This is the single record of the question.** `plans/004` WI-4 says "sluice
decommissioned, skip"; this plan made sluice the smoke test and names it in an
acceptance criterion; the accent registry still carries it. Those cannot all be
right, and no agent should resolve it by picking whichever line it read last.
Both plans now point here.

**What is known** (checked 2026-08-15, all first-hand):

- The repo exists at `~/projects/personal/sluice` and its last commit is
  2026-08-03 — a dependabot ruff bump. Last substantive commit: 2026-07-28.
- **Nothing in sluice's own record says it is decommissioned.** No note in its
  `README.md`, `AGENTS.md`, or plan set (which runs 001–014, none of them a
  wind-down plan).
- It still has a live web UI: `src/sluice/static/css/tokens.css`, carrying
  patina's "VENDORED FROM patina — do not edit here" banner and
  `/* accent: sluice */`.
- It is in patina's accent registry (`docs/token-contract.md`) and has
  `accents/sluice.css`.
- It **fails** the gate today — 3 failures, see WI-2. It is not "already clean".
- **The likely origin of the "decommissioned" claim, and why it does not
  support it:** switchboard's `AGENTS.md` ("Relationship to sluice
  (historical)") records that *switchboard* removed its sluice **dependency** in
  its Plan 018, vendoring the flow-control core it used. That retires a *code
  coupling*, and it is easy to misread as "sluice is gone". It says nothing
  about sluice the service being run or shut down, and switchboard is not
  sluice's owner. (Unverified either way: how much traffic, if any, sluice
  still carries.)

**What is NOT known:** whether sluice is still deployed/wanted; whether it
should be re-synced onto the current tokens and stamp, frozen as-is, or dropped
from the registry.

**Until the owner decides, the operative rule is:** sluice is *unresolved*, not
decommissioned and not a clean consumer. Do not re-sync it as routine work, do
not remove its accent, and do not count it in "all consumers pass" claims.

## Acceptance

- Editing inside a vendored block, or adding an off-token literal, fails CI in
  cert-watch. (**Amended 2026-08-15:** sluice was named here too; it is
  unresolved — see above — so it cannot be an acceptance criterion for this
  plan. Restore it if the owner decides sluice stays.)
- `check_patina.py --report` shows each consumer's drift status; dossier and
  cert-watch reconciled. (The "five consumers" figure — cert-watch, dossier,
  gpo-lens, sluice, switchboard — depends on the sluice question and on
  switchboard's not-yet-started adoption in WI-5.)
- The prefix rule is recorded in `docs/token-contract.md`. **DONE** — see
  "Tool-local tokens: the prefix rule".

## If declined

Drift remains undetectable and every rule in Plans 004/006/007/008 rests on
the same prose that already failed four times. This plan is the load-bearing
one; decline it and the rest should be re-scoped to cert-watch-local work.
