# Plan 002 — quiet-tier contrast floor (--text-3 meets WCAG 2.2 AA)

**Status:** Draft — proposed 2026-07-29. Blocks dossier Plan 024 Phase 5
qualification (WCAG 2.2 AA) and weakens every face that renders metadata in
the quiet tier. **Human decision required:** the exact replacement values (the
quiet tier is family identity; candidates below are measured, not chosen).
**Owner:** patina. **Surfaces:** `#3d3a32`-adjacent decisions ripple to every
tool via `sync.sh`.

## Problem

`--text-3` is the family's de-emphasis tier (table headers, timestamps,
metadata labels, helper copy). Measured against the token surfaces with the
WCAG 2.2 relative-luminance formula:

| Theme | Surface | Current contrast | AA floor (normal text) |
|---|---|---|---|
| dark (`#767065`) | `--bg` `#0e0d0b` | 3.96:1 | 4.5:1 |
| dark (`#767065`) | `--panel` `#181612` | 3.68:1 | 4.5:1 |
| light (`#938c7c`) | `--bg` `#f3f0e9` | 2.94:1 | 4.5:1 |
| light (`#938c7c`) | `--panel` `#fbfaf6` | 3.20:1 | 4.5:1 |

Every consuming tool inherits the failure wherever real information rides the
quiet tier. dossier's `feat/ui-visual-pass` branch (2026-07-29) shipped a local
workaround — information-bearing microcopy in `--text-2`, `--text-3` demoted to
decorative-only — but that is a per-tool patch over a family bug.

## Direction

Raise the quiet tier's luminance in both themes while keeping it visibly
quieter than `--text-2` (currently 8.05:1 dark / 6.1:1 light) and keeping the
warm-gray hue family (R >= G >= B, low chroma). Measured candidates:

| Token | Candidate | on `--bg` | on `--panel` | vs `--text-2` |
|---|---|---|---|---|
| `--text-3` dark | `#8b857a` | 5.30 | 4.93 | 8.05 |
| `--text-3` dark (alt) | `#8f887c` | 5.53 | 5.15 | 8.05 |
| `--text-3` light | `#6f6859` | 4.86 | 5.29 | 6.10 |
| `--text-3` light (alt) | `#6b6456` | 5.15 | 5.61 | 6.10 |

## Work items

- **WI-1 — Values decision (human).** Pick from the candidate table or adjudge
  fresh values against the same formula (script in WI-3). Record the choice in
  `docs/token-contract.md` next to `--text-3`'s entry, including the floor it
  must never again fall below (4.5:1 on `--bg` and `--panel`, both themes).
- **WI-2 — Apply + document.** Edit `tokens.css` (both theme blocks), bump the
  header comment noting the contract change, and re-run `sync.sh <tool>` for
  each consumer (gpo-lens, cert-watch, dossier, sluice) — deliberately, one PR
  per tool, per the family vendoring rule.
- **WI-3 — Contrast gate.** Add a tiny `check-contrast.py` (stdlib-only): fail
  if any declared text/status/accent token falls under 4.5:1 on its declared
  surfaces (text pairs) or 3:1 (non-text UI/focus indicators). Run it in
  patina's CI so future token edits can't regress the floor.
- **WI-4 — Per-tool verification.** For each consuming tool after re-sync:
  before/after screenshots of one dense metadata page per theme, and grep the
  tool's component CSS for deliberate `text-3`-as-content uses that may now
  look louder (quantify: how much louder is the answer).

## Acceptance

- `--text-3` >= 4.5:1 on `--bg` and `--panel` in both themes, verified by the
  gate script in CI.
- Every consuming tool re-synced; no tool reports a visual regression it
  wants rolled back.
- dossier relaxes its local `--text-2` workaround (dossier Plan 026, WI-3).

## If declined

dossier's `feat/ui-visual-pass` workaround is self-contained and stays; other
tools inherit the AA failure. The fallback is a copied quiet-tier override per
tool — exactly the drift patina exists to prevent.
