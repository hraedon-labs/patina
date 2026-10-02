# Plan 006 — shared components + macros (deciding Plan 001 WI-3)

**Status:** RATIFIED 2026-08-14 (owner) — WI-1 done. Patina ships the
reference implementation; new tools vendor it. Amendment to the original
proposal, also from the owner: existing tools MAY be retrofitted when the
initial pain is worth the downstream simplification — retrofit is permitted,
opportunistic remains the default; assess per-tool when its UI is next
touched. **WI-1's deliverable actually landed 2026-08-15** — it had been marked
done on the strength of the decision alone, while four documents still stated
the reversed position. The decision and its rationale are now recorded in
`README.md` (Scope), `AGENTS.md` ("What patina is (and isn't)"),
`docs/token-contract.md` ("Shared component patterns") and `docs/patterns.md`
(intro). **2026-10-02: WI-2 and WI-4 delivered locally**, with reference code,
ownership gates, template tests and a synthetic inventory example. WI-3's
live agent-notes adoption remains open and was outside this non-AOS pass.
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

- **WI-1 — DONE** (decided 2026-08-14; recorded in the docs 2026-08-15).
  Ratify the reversal (human). The charter said "intentionally not a component
  framework"; this plan amends that to "a reference implementation new tools
  vendor". Recorded in README scope, AGENTS.md, `docs/token-contract.md`, and
  `docs/patterns.md`.
- **WI-2 — DONE 2026-10-02 — Extract.** Built `components.css` + `macros/ui.j2` from cert-watch's
  macros and `patterns.md`; every shape gets its state set; ASCII-only (family
  IIS rule).
- **WI-3 — OPEN — Prove on a thin consumer.** agent-notes is the cheapest live
  candidate (8 templates, currently unstyled): adopt tokens + components
  wholesale; it becomes the reference example of "new tool, zero own CSS".
- **WI-4 — DONE 2026-10-02 — Document.** `patterns.md` sections point at their `pt-` counterparts;
  add "when to extend vs. when to request" — a tool needing a new shape adds it
  to patina (with states) or prefixes it as tool-local; never per-page CSS.
  (This kills the cert-watch `NEEDED-CSS.md` wishlist pattern by giving the
  request a real path.)

## Acceptance

- **NOT MET (WI-3)** — agent-notes runs the family look with no component CSS
  of its own.
- **MET 2026-10-02 (WI-2)** — the state-set rule is checkable: every `pt-` component
  section documents its states inline; the empty state exists for every
  collection-rendering shape.
- **MET 2026-08-15 (WI-1)** — charter + token-contract updated with the
  decision and its rationale.

## Implementation and verification, 2026-10-02

The catalog's 14 shapes now have scoped CSS sections with their applicable
states. The macro vocabulary starts from cert-watch's status/stat/empty/caller
patterns; domain-specific urgency filters, icons, charts and grades remain in
the consumer. Fields/selects/buttons share a 36px control height, reserved
error slots and fixed border widths. Status always includes text; zero and
unknown counts are neutral. The frame retains the shared page grid and wraps
its chrome on narrow screens. No token values or theme default changed.

`sync.sh --components <templates-dir>` is opt-in and delivers delimited,
hashed CSS and Jinja blocks. It preflights collisions before token writes,
backs up unmarked originals only with `--adopt`, and preserves consumer tails.
The checker verifies both components against their own pinned source revision;
new source revisions are upgrade notices. `.j2` files join normal CSS/class
checks. Existing sync behavior and existing consumers remain unchanged.
Source components are LF-pinned by `.gitattributes`; checks accept Git's CRLF
transport in a consumer while retaining byte-exact local tails. This prevents
a normal Windows checkout from being reported as corrupted source. Edited and
restamped content still fails comparison with its recorded Git revision.

Verification: 19 disposable-source ownership/sync tests, 22 real Jinja macro
tests, the existing 45 conformance cases and 64 Chromium cases. Browser cases
cover normal/filtered/empty/loading/error/long/wide-content pages in both themes at
1280, 720, 375 and 320px, real scope navigation, native required validation,
label focus, disabled controls, file selection, stable error geometry and
local table scrolling without page overflow. The example has no component
CSS of its own. This is synthetic proof, not a claim that WI-3's live
consumer acceptance is met.
The existing contrast gate retains its four known Plan 002 warnings for
muted text; this change does not alter those token values or claim full-page
WCAG conformance.

## If declined

patterns.md stays prose; the fifth and sixth tools re-implement the catalog
again and the drift surface keeps growing linearly with the estate.
