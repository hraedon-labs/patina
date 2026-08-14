# Plan 006 — shared components + macros (deciding Plan 001 WI-3)

**Status:** Draft — proposed 2026-08-14. Decides the question Plan 001 WI-3
parked. **Human decision required:** WI-1 ratifies the direction reversal.
**Owner:** patina. Depends on Plan 005 (the gate is what makes shared code
safe to share).

## Problem

"Share tokens and shapes, not class names" was reasoned for human autonomy:
each tool's author keeps freedom at the component layer. But the estate's UIs
are written by agents, not authors — and for an agent, `docs/patterns.md` is a
description it re-implements from scratch per tool. The result, measured
2026-08-14: four parallel component layers (`cw-` ~40 sections, `ds-` ~830
lines, gpo-lens's own, sluice's per-page CSS) that implement the same 14 shapes
with drifting details. Every re-implementation is a drift surface. The
patterns catalog was the right idea with the wrong delivery: prose for humans
instead of code for machines.

## Direction

Hybrid, weighted by cost:

- **patina ships a reference implementation**: `components.css` (neutral
  `pt-` prefix) + `macros/ui.j2` (Jinja macro library), both seeded from
  cert-watch's `macros/ui.html` + `patterns.md`'s 14 shapes. `sync.sh` gains a
  `--components` flag to vendor them (delimited + stamped per Plan 005).
- **New tools adopt it wholesale** — a new tool stands up the family frame
  with zero component CSS of its own.
- **Existing tools keep their prefixes.** Retrofitting four working component
  layers is churn without user-visible benefit. They may adopt per-component
  opportunistically (e.g. when a page is rebuilt anyway).
- **Every component ships its full state set** where applicable: empty,
  loading, error, disabled — not just the happy path. Happy-path-only
  components are why agent-built UIs degrade under real conditions; the empty
  state is part of the component, not an afterthought.
- **Form grammar included** (field/label/help/error slots): reserve the error
  slot's height (`min-height: 1lh`) so validation doesn't shift layout; state
  changes never alter `border-width` (background/outline/box-shadow only);
  input height equals adjacent button height. (Borrowed from Hallmark's
  interaction-and-states rules — the one cluster there that is engineering,
  not taste.)

## Work items

- **WI-1 — Ratify the reversal (human).** The charter says "intentionally not
  a component framework"; this plan amends that to "a reference implementation
  new tools vendor". One-line decision, recorded in README scope + charter.
- **WI-2 — Extract.** Build `components.css` + `macros/ui.j2` from cert-watch's
  macros and `patterns.md`; every shape gets its state set; ASCII-only (family
  IIS rule).
- **WI-3 — Prove on a thin consumer.** agent-notes is the cheapest live
  candidate (8 templates, currently unstyled): adopt tokens + components
  wholesale; it becomes the reference example of "new tool, zero own CSS".
- **WI-4 — Document.** `patterns.md` sections point at their `pt-` counterparts;
  add "when to extend vs. when to request" — a tool needing a new shape adds it
  to patina (with states) or prefixes it as tool-local; never per-page CSS.
  (This kills the cert-watch `NEEDED-CSS.md` wishlist pattern by giving the
  request a real path.)

## Acceptance

- agent-notes runs the family look with no component CSS of its own.
- The state-set rule is checkable: every `pt-` component section documents its
  states inline; the empty state exists for every collection-rendering shape.
- Charter + token-contract updated with the decision and its rationale.

## If declined

patterns.md stays prose; the fifth and sixth tools re-implement the catalog
again and the drift surface keeps growing linearly with the estate.
