# Plan 007 WI-3 — cert-watch landing-page assessment (for external review)

2026-08-14. This is the WI-3 deliverable: the ratified archetypes
(`docs/archetypes.md`) applied to cert-watch's real IA, with options and a
recommendation. It is written for a second opinion — disagreement welcome,
especially on the review questions at the end.

## Headline finding

The original WI-3 proposal ("`/` takes the Inventory grammar, `/posture`
takes the Dashboard grammar") **does not survive contact with the actual
templates**, and the assessment is better news than the proposal assumed:
**plan 055 already implemented most of the ratified dashboard grammar,
including the counts-as-scopes idea.** The landing page's own template
comment (dashboard.html:103) reads:

> `Stat strip: the cells ARE the urgency filter`

Each stat card is a link that filters the table below it and carries an
active state — Tracked / Expired / Critical (<7d) / Warning (7–29d) /
Healthy, with zero-renders-neutral subtitles ("none" / "needs attention").
The 2026-08 mockup B relocated an idea the product already had, which is
part of why it lost.

## Ground truth (branch redesign/ui-v2 @ a427356)

**`/` (Certificates, the landing page):** clickable stat strip (5 urgency
cells) → filter bar (search + segmented pivot: All / By issuer / By owner /
By method / Calendar) → the full certificate table, urgency-sorted, with
sortable columns, expansion rows, hover actions → add-drawer. Per-row
"scanned <timestamp>" sublines. A global health strip in base.html shows
scanner problems and stays hidden when quiet.

**`/posture`:** a genuinely different domain, not a general dashboard —
fleet TLS grade, weak primitives (SHA-1 / RSA<2048 / weak curves), key
families, grades-over-time, TLS versions, plus SC-081 readiness and
compliance as sibling views. Repurposing this page as "the dashboard" would
displace real analytic content and mislabel expiry operations as posture.
**The original WI-3 mapping is therefore withdrawn** (recorded here per the
conventions-require-decisions rule: it was proposed before reading
posture.html, and died on facts).

## The derivation, applied

Operator questions for the landing page (archetypes.md method), and where
each is answered today:

| Question | Today | Verdict |
|---|---|---|
| Anything wrong right now? | Expired + Critical cells, in-viewport, zero-neutral | answered |
| What needs attention soon? | Warning cell (7–29d); table urgency sort | answered |
| Is a wall of future work coming? | Calendar **pivot view** — behind one click, replaces the table when active | **gap (partial)** |
| What do I work on first? | Table's default urgency sort | answered |
| Is coverage/posture OK? | Fleet grade lives on /posture (one nav click); **no unmonitored/pending count anywhere on `/`** | **gap (partial)** |
| Can I trust this is current? | Health strip (loud only on failure) + per-row scan stamps | answered (adequate) |

Two real gaps. Everything else the ratified grammar asks for is present.

## Options

**Option 0 — accept as-is.** Write the surface brief documenting the above,
close WI-3. The two gaps persist: the trend needs a click, and a fleet with
5 unscanned hosts can look all-healthy on the landing page (the unmonitored
blind spot is arguably the operationally dangerous one).

**Option A — close the gaps in place (recommended).** No IA change, no new
pages:
1. **Always-visible expiry distribution** — a compact 12-month histogram
   with the `+30d` alerting boundary drawn on it, between the strip and the
   filter bar. The calendar pivot stays for the detailed view; the
   histogram answers "is a wall coming?" at a glance. (Data already exists —
   the calendar view computes it.)
2. **Surface the coverage blind spot** — an "Unmonitored" count with
   never-scanned/pending semantics, clickable like the other cells.
3. **Fleet grade as a quiet cross-reference, not a cell** — a small
   "Posture B− →" link near the strip. Rationale: it is /posture's
   headline, a different domain's answer; the landing page should point at
   it, not duplicate it. (Reviewer may disagree — Q2 below.)
4. The V1 notes merge and the strip's semantic rules (already largely met)
   ride along.

**Option B — split Dashboard and Certificates pages** (the reviewer's
earlier division, taken literally). Landing `/` = summary + trend + urgent
shortlist; `/certificates` = chips + full inventory. Clean separation, but
at today's scale it costs a fifth nav domain (055 just cut 7 → 4), puts the
full list two clicks away, and duplicates the strip/chip counts across two
pages — the exact duplication the owner disliked in mockup B. **Recorded as
the growth path, not the current answer**, with an explicit trigger: split
when the urgency-sorted table's actionable head plus the trend no longer fit
the first ~2 viewports (roughly: hundreds of certs with dozens in the
warning bands, sustained).

**Option C — repurpose /posture as the dashboard.** Withdrawn on facts (see
Ground truth).

## Impact and sequencing (Option A)

One template (dashboard.html) + its route handing the histogram data +
strip addition; no schema change (unmonitored derives from existing host
state); e2e visual baselines re-generate in CI — already required by the
palette adoption on this branch, so the two visual changes can share one
re-baseline. Rides the existing `patina/reconcile-tokens` branch or a
follow-up; either way it lands after PR #21's owner validation, which
remains the sequencing gate for everything on this stack. Effort: small —
comparable to one 055 page conversion.

## Review outcome (2026-08-14 — reviewer + owner: Option A, modified)

The reviewer concurred with Option A and answered the five questions; the
owner agreed. The modifications, all adopted:

- **Derivation corrected:** "coverage" and "posture" are different
  questions. Coverage ("can I trust the known-state answers?") IS a
  landing-page requirement — its omission is an epistemic failure, the most
  serious finding of this assessment. Posture ("security quality of the
  estate") is /posture's question and appears on `/` only as a quiet
  cross-reference (opposite end of the strip row, grade mildly emphasized) —
  it is not a missing dashboard metric. Both corrections now live in
  archetypes.md.
- **Q1 (histogram): not a requirement — prototype it.** Test: not "does it
  change slowly" but *what bad decision becomes more likely one click away*
  (weak answer here: noticing a busy month late). Middle ground to try
  first: a ~50–70px compact expiry horizon integrated into the page, not a
  boxed chart. Reject if it pushes the actionable table head below the fold
  on an ordinary laptop viewport.
- **Q2 (fleet grade): quiet cross-reference, strongly.** The strip has a
  clean semantic contract — "these are scopes over the inventory immediately
  below" — and posture doesn't filter that population, so it must not look
  like a sixth cell.
- **Q3 (unmonitored): neither cell nor mere chip — a coverage exception
  control with state-dependent prominence.** Unmonitored is orthogonal to
  the urgency partition (and may count hosts, not certificates — verify
  before building). 0 → very quiet "Coverage complete"; >0 → warning
  prominence; scanner failure → the global health strip takes over.
  Exception-driven salience, not a permanent yellow card.
- **Q4 (cards): they earn substantial click targets, not "cards."** Keep
  the single-surface segmented strip, compress vertical padding. New patina
  rule extracted (now in archetypes.md): summary values may be prominent
  and persistent when the summary is itself an interaction with the primary
  object set — prefer integrated scopes over decorative metric cards.
- **Q5 (split trigger): viewport consumption rejected as the trigger.**
  Scale is solved by search/filter/pagination, not URLs. Replace with
  intent divergence: split overview from inventory only when two
  independently substantial workflows (estate awareness vs. certificate
  investigation) force each other's hierarchy or controls to compromise —
  symptoms: multiple necessary analytical views, bulk actions/saved
  filters, users visiting for awareness without the inventory (or vice
  versa), divergent URL/state/time-horizon needs. May never trigger at any
  count; could trigger at 100.
- **Method addendum (the most useful WI-3 finding):** three layers, not
  two — information → interaction model → representation. The original
  mockup-B critique jumped from information to representation and misread
  large labeled filter controls as decorative KPIs. Now in archetypes.md
  step 3.

Target landing page: clickable urgency strip (compressed) + coverage
exception control + quiet `Posture B− →` link → optionally the compact
expiry horizon if the prototype earns its height → search/pivots → full
urgency-sorted inventory.

## Questions for the reviewer (as originally posed)

1. **The trend's cost:** an always-visible histogram spends ~120px of
   first-viewport height on every visit to answer a question that changes
   slowly. Worth it, or is the calendar pivot (one click) actually the
   right cost for a slow-moving answer?
2. **Fleet grade on the landing page:** quiet link (my position — it's
   another domain's headline) or full strip cell (posture is part of
   "anything wrong?")?
3. **Unmonitored:** sixth strip cell, or a quiet chip next to the strip?
   A sixth cell crowds the band and unmonitored is a *coverage* fact, not
   an *urgency* bucket — but it's also the blind spot, and quiet may be
   too quiet.
4. **Representation of the strip itself:** the clickable cards earn their
   size by being filter targets; the denser one-line status band reads
   better but makes five click targets harder. Is clickability a good
   enough reason to keep cards?
5. **The Option B trigger:** is "urgent head + trend no longer fit ~2
   viewports" the right split condition, or should the single hybrid page
   be considered permanent at any scale?
