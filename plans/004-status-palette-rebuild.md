# Plan 004 — status palette rebuild (de-Tailwind + CVD validation)

**Status:** WI-1/WI-2/WI-3 executed 2026-08-14. Candidate **A "warm & quiet"**
chosen (owner + review, from rendered component swatches, both themes, vs the
incumbent and candidate B). Values + full rationale recorded in
`docs/token-contract.md`; floors gated by `scripts/check_contrast.py` (which
also reports plan 002's known `--text-3` warnings without failing on them).
WI-4 re-sync: cert-watch done (pilot); dossier blocked on its `ds-` extraction
(Plan 005 WI-4 — a re-sync today would destroy the 830 lines edited into its
unstamped vendored file); gpo-lens/switchboard land with their adoption
(Plan 005 WI-5); ~~sluice decommissioned, skip~~ — **CORRECTED 2026-08-15: not
established.** Nothing in sluice's own repo records a decommission, its vendored
copy is live, and it is still in the accent registry; the likely origin of the
claim is switchboard dropping its sluice *dependency*, which is a different
fact. sluice is skipped for now because its status is **unresolved**, not
because it is retired. The single record of that open question, with everything
known, is in `plans/005` ("Open question: sluice's status").
WI-5 CLOSED 2026-08-14 (owner concurred with measurement): the un-merge is
impossible — light-theme `--cw-expired` `#c41d6f` vs the new crit `#b64461`
is ΔE 6.4 under NORMAL vision (floor 15) and 2.2 under deuteranopia. The
crit/expired presentation merge is permanent; "expired" is distinguished by
its label (secondary encoding). `--cw-expired` can be retired from cert-watch
when convenient.
**Owner:** patina. Companion to Plan 002 (quiet-tier contrast floor).

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

- **WI-1 — DONE — Measure candidates (agent).** Produce 2–3 candidate quads with
  the validator + contrast numbers attached, rendered on real component samples
  (pill, chip, callout, table row) in both themes. (The measurements were made
  and reported; the underlying data was never committed — see Acceptance.)
- **WI-2 — DONE — Values decision (human).** Side-by-side rendered comparison, binary
  or ternary choice. Record the chosen values AND the rejected stock-Tailwind
  finding in `docs/token-contract.md` so the decision is durable.
- **WI-3 — DONE — Apply + gate.** Edit both theme blocks in `tokens.css`; extend
  Plan 002's `check-contrast.py` (WI-3 there) to cover the status quad and its
  `-soft` tints so a future edit cannot regress ~~to unvalidated values~~
  **below the contrast floors** (precise as of 2026-08-15: the gate covers the
  floors only; CVD is not gated — see Acceptance).
- **WI-4 — PARTIAL — Re-sync deliberately.** One PR per consumer (dossier; gpo-lens and
  cert-watch after Plan 005 reconciliation; ~~sluice~~ **held pending the open
  question in `plans/005`** — it was listed here and simultaneously written off
  as decommissioned in the status line above, which is the contradiction that
  correction resolves), before/after screenshots of a status-dense view per
  theme.
- **WI-5 — CLOSED (see Status).** Downstream re-evaluation. With a CVD-validated quad, revisit
  cert-watch's crit/expired merge: keep the merge if the new adjacency still
  fails simulation, un-merge if it now passes. Either way record the result.

## Acceptance

- ~~Every status token passes the contrast floors and CVD gates, verified by
  the extended gate script in CI.~~ **Reconciled 2026-08-15 — this overstated
  the script.** Split into what is mechanical and what is not:
  - *Mechanical:* every status token passes the WCAG contrast floors on `--bg`
    and `--panel`, both themes, verified by `scripts/check_contrast.py`. (That
    script is being wired into patina's CI by a parallel workstream.)
  - *Not mechanical, and no script computes it:* the CVD pairwise
    distinguishability of the quad. `check_contrast.py`'s own docstring says CVD
    validation is deliberately not gated there — it needs simulation matrices
    and judgment. There is **no "extended gate script"** doing CVD in this repo
    or any consumer. The CVD numbers in `docs/token-contract.md` are a recorded
    one-time manual measurement; changing status values requires redoing that
    measurement by hand, and CI will not notice if you skip it.

  (Amended 2026-08-14 after review: the original "no token equals a Tailwind
  value" criterion was wrong — provenance is not a defect. The defects are the
  measured ones: light-theme ok at 2.9:1, deutan collapse of ok/warn/crit. If a
  stock value were optimal, we would use it shamelessly; candidates were
  produced by constraint search, not by avoiding Tailwind.)
- ~~Validator + CVD simulation pass recorded in the plan folder.~~ **NOT MET —
  open item, unassigned (raised 2026-08-15).** `git ls-files plans/` returns
  only `.md` files: no validator output, no simulation matrix, no candidate
  data was ever committed. The ΔE figures quoted in `docs/token-contract.md`
  are therefore unreproducible from this repo. Either re-derive and commit the
  record (a `plans/004-validation/` folder), or amend this criterion to say the
  measurement is deliberately transient — an owner call, not an agent's.
- Consumers re-synced with no regression the owner wants rolled back.

## If declined

The family keeps stock status colours. That is a legitimate choice (convention
aids recognition) — but it must then be recorded in `docs/token-contract.md`
as a decision with rationale, so it stops being an accident. The CVD gap
remains and WI-5's cert-watch merge stays permanent.
