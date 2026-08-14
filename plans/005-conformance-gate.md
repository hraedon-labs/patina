# Plan 005 — conformance gate (drift detection becomes mechanical)

**Status:** Draft — proposed 2026-08-14. **Owner:** patina + each consumer.
**Pilot substrate: cert-watch** (owner's call, 2026-08-14) — it is the hardest
case (forked token names), so passing there proves the mechanism. sluice is the
smoke test (already clean).

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
  banners — the record drifted from reality too.
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

- **WI-1 — Stamp + delimiters in `sync.sh`; write `check_patina.py`** with the
  three checks above and a `--report` mode that prints per-consumer drift
  status (for the periodic estate audit).
- **WI-2 — Smoke test on sluice.** Should pass untouched; proves no false
  positives on a clean consumer.
- **WI-3 — cert-watch reconciliation (the pilot).** Map `--sp-*` back to
  `--space-*` (values already identical); add the missing `-soft` family;
  re-prefix its private tokens (`--expired`, `--accent-fg`, `--backdrop`,
  `--pad-panel`, `--pad-page`, `--topbar-h`) to `--cw-*` or propose the
  genuinely general ones for the contract; re-vendor via `sync.sh`; visual
  baselines must stay green (cert-watch already has the screenshot CI to prove
  no pixel change). This also completes Plan 001 WI-2 at last.
- **WI-4 — dossier extraction.** Move the ~830 `ds-` lines to `dossier.css`
  below the delimited block; re-vendor; gate on.
- **WI-5 — gpo-lens + switchboard.** gpo-lens: adopt the vendored file (Plan
  001 WI-1). switchboard: fresh adoption — new accent in `accents/`, registry
  entry (note: `docs/token-contract.md` accent table is missing sluice today;
  fix that while in there).
- **WI-6 — Timeboxed evaluation (optional): `impeccable detect`.** Run
  pbakaus/impeccable's deterministic scanner against cert-watch's *rendered*
  pages (its page-level rules skip Jinja fragments — scan saved responses or
  URLs, not templates). Keep it only if it catches real defects the gate and
  visual baselines miss; it is a complement, not the mechanism of record.

## Acceptance

- Editing inside a vendored block, or adding an off-token literal, fails CI in
  cert-watch and sluice.
- `check_patina.py --report` shows all five consumers' drift status; dossier
  and cert-watch reconciled.
- The prefix rule is recorded in `docs/token-contract.md`.

## If declined

Drift remains undetectable and every rule in Plans 004/006/007/008 rests on
the same prose that already failed four times. This plan is the load-bearing
one; decline it and the rest should be re-scoped to cert-watch-local work.
