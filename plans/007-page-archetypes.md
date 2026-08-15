# Plan 007 — page archetypes and banned defaults (structure tier 2)

**Status:** WI-1/WI-2 executed 2026-08-14; **WI-2 decided the OPPOSITE of
this plan's proposal** — see Outcome. **Owner:** patina.

## Outcome (2026-08-14) — the decision, and the reversal

Mockups A (stat-strip dashboard) and B (object-first, counts-on-filters) were
built with identical data and reviewed two ways: by the owner, and blind (an
external evaluator judging pixels without this plan's rationale). **Both chose
A.** The blind review also identified the reasoning error in this plan's
Problem section: the chain "common → LLM prior → AI fingerprint → credibility
problem → avoid" only establishes its first two links, and "the layout a
generic prompt won't produce" is not a design criterion — a generic prompt
also won't produce many terrible layouts. The replicated-by-a-generic-prompt
incident is evidence the shape is *conventional*, not that it is *wrong*.

What survives of the original concern: a generic skeleton filled with generic
content does read as machine output. The fix is semantic specificity — stats
with operational thresholds, a domain-bucketed trend with the `+30d` alerting
boundary drawn on it, urgency-ordered lists, zero-renders-neutral — not
skeleton avoidance.

Ratified into `docs/archetypes.md`: **Dashboard** = summary → trend → urgent
objects (mockup A's grammar, with the semantic-loading rules); **Inventory**
= scopes → objects, with mockup B's filter-bar count chips — B's real
contribution — as the inventory's count grammar. Two archetypes, not one
forced onto both jobs. Also adopted from the review: **the rule-test** —
every new patina rule must name the actual failure it prevents or the
operator decision it improves (now in AGENTS.md).

## Problem

Structural sameness, not visual sameness, is the AI fingerprint. Concrete
incident (2026-08): cert-watch's dashboard — four stat callouts over a
chart-and-table stack — was replicated near-exactly when a coworker asked an
AI tool for a *vulnerability* dashboard. That layout is the single most
statistically dominant dashboard shape in LLM training data; tokens cannot fix
it, because the tell is the skeleton. The credibility cost is real: work that
reads as "the default the machine emits" gets discounted, whatever its quality.

Today `patterns.md` §6 promotes the stat strip as a family pattern, i.e. the
catalog codifies the attractor. Meanwhile the shapes that carry no tell
(tables, fields, chips, empty states) have no more standing than the ones that
do — the catalog doesn't distinguish them.

## Direction

`docs/archetypes.md`, structured in two tiers:

- **Tier 1 — invisible shapes** (table, field, chip, pill, callout, empty
  state, breadcrumb, chain): standardize aggressively, no differentiation
  needed. Nobody clocks a table as machine-made.
- **Tier 2 — page archetypes** (dashboard, record detail, settings, activity
  log): each entry states the canonical family layout, **names the banned
  default explicitly, and records why it is banned.** Models regress to
  attractors unless the prohibition is explicit and reasoned in context
  (Hallmark's documented experience: parity instructions smuggle banned
  patterns back in); an unexplained rule will be optimized away by the next
  agent session.

Proposed dashboard grammar (the identity decision of WI-2):

- **The primary object table leads the page.** The tool's job is its objects;
  the first viewport answers "what needs attention", not "how many things
  exist".
- **Counts live on the filter bar as clickable scopes** — `expiring-30d (12)`
  is a filter you can click, not a poster. A count you can act on is a tool; a
  count in a bubble is decoration.
- At most a **narrow summary rail** for genuinely cross-cutting posture; the
  four-stat hero row is demoted to "use sparingly, never the family
  signature".

Banned defaults to name in v1: the 4-stat-card hero over chart+table
(dashboard); hero → 3-feature-cards grammar (any page); card-in-card nesting;
centered-everything on data pages.

## Work items

- **WI-1 — Write `docs/archetypes.md`** with the two tiers, the four Tier-2
  archetypes, banned defaults + rationale. Demote `patterns.md` §6 with a
  pointer.
- **WI-2 — Dashboard grammar decision (human).** Two rendered mockups of the
  cert-watch dashboard content: (a) current stat-strip layout, (b) object-first
  + counts-on-filters. Side by side, both themes. Binary choice.
- **WI-3 — cert-watch assessment (pilot).** Map the two ratified archetypes
  onto cert-watch's real IA (post-055: Certificates at `/`, Posture,
  Activity, Settings — there is no separate dashboard page). Proposal to
  assess: `/` takes the Inventory grammar (full table + filter-bar count
  chips), `/posture` takes the Dashboard grammar (summary strip + expiry
  histogram with the +30d marker + urgent shortlist). Produce the assessment
  and screenshots; the reshape, if any, is a cert-watch plan and an owner
  call.
- **WI-4 — Wire into the skill** (Plan 008): archetype selection becomes a
  stated step — an agent building a page names its archetype out loud before
  writing markup, and pages must record their archetype in the surface brief.

## Acceptance

- `docs/archetypes.md` exists; every Tier-2 entry has a banned-default line
  with a why.
- The dashboard grammar decision is recorded (either way) — after this plan it
  is a decision, not an accident.
- cert-watch assessment delivered with screenshots.

## If declined

The family keeps standardizing whatever shape the model emits first. The
coworker-replication incident recurs with each new dashboard, and the
distinctive token layer keeps getting spent on structurally generic pages.
