# Plan 004 — status palette rebuild (de-Tailwind + CVD validation)

**Status:** Draft — proposed 2026-08-14 (first-principles review of patina's
stylistic choices). **Human decision required:** final values are a family
identity call; candidates must be presented as rendered swatches on real
components, both themes, side by side — not as hex lists. **Owner:** patina.
Companion to Plan 002 (quiet-tier contrast floor) — same gate script, different
tokens.

## Problem

The dark-theme status quad was never designed; it is Tailwind's default
palette verbatim:

| Token | patina value | Tailwind name |
|---|---|---|
| `--ok` | `#34d399` | emerald-400, exact |
| `--warn` | `#fbbf24` | amber-400, exact |
| `--crit` | `#f87171` | red-400, exact |
| `--ok` (light) | `#15a34a` | green-600 is `#16a34a` — one digit off |

This is a convention by accretion, not decision: the one part of the contract
that is the statistical LLM default, sitting inside the file whose job is to
keep the family from looking like the default. It has also never been
CVD-validated — downstream evidence: cert-watch Plan 055 had to merge its
crit/expired presentation because the adjacency failed colour-vision-deficiency
simulation. The status hues also read cool/saturated against the warm-charcoal
surfaces (the neutrals were designed; the status colours were pasted).

## Direction

Rebuild the quad deliberately. Keep the semantic hue anchors (green = ok,
amber = warn, red = crit, blue = info) — status semantics benefit from
convention; the *values* should not be stock. Constraints for candidates:

- Harmonise with the warm surface family (nudge hue/chroma toward the warm
  axis; the current values sit in Tailwind's cool-neutral gamut).
- Pass the dataviz skill's palette validator (it ships a runnable checker and
  CVD simulation) for pairwise distinguishability under deuteranopia,
  protanopia, and tritanopia — including the ok/warn and warn/crit adjacencies
  that actually co-occur in tables.
- Meet Plan 002's floors on `--bg` and `--panel`, both themes: 4.5:1 where the
  token carries text, 3:1 where it is a non-text indicator (dots, borders).
- `*-soft` tints stay derived from the chosen values (same alpha treatment as
  today).

## Work items

- **WI-1 — Measure candidates (agent).** Produce 2–3 candidate quads with the
  validator + contrast numbers attached, rendered on real component samples
  (pill, chip, callout, table row) in both themes.
- **WI-2 — Values decision (human).** Side-by-side rendered comparison, binary
  or ternary choice. Record the chosen values AND the rejected stock-Tailwind
  finding in `docs/token-contract.md` so the decision is durable.
- **WI-3 — Apply + gate.** Edit both theme blocks in `tokens.css`; extend Plan
  002's `check-contrast.py` (WI-3 there) to cover the status quad and its
  `-soft` tints so a future edit cannot regress to unvalidated values.
- **WI-4 — Re-sync deliberately.** One PR per consumer (sluice, dossier;
  gpo-lens and cert-watch after Plan 005 reconciliation), before/after
  screenshots of a status-dense view per theme.
- **WI-5 — Downstream re-evaluation.** With a CVD-validated quad, revisit
  cert-watch's crit/expired merge: keep the merge if the new adjacency still
  fails simulation, un-merge if it now passes. Either way record the result.

## Acceptance

- No status token in `tokens.css` equals a Tailwind palette value.
- Validator + CVD simulation pass recorded in the plan folder; contrast gate
  covers the quad in CI.
- Consumers re-synced with no regression the owner wants rolled back.

## If declined

The family keeps stock status colours. That is a legitimate choice (convention
aids recognition) — but it must then be recorded in `docs/token-contract.md`
as a decision with rationale, so it stops being an accident. The CVD gap
remains and WI-5's cert-watch merge stays permanent.
