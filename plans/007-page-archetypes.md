# Plan 007 — page archetypes and banned defaults (structure tier 2)

**Status:** WI-1/WI-2/WI-3 executed 2026-08-14; **WI-2 decided the OPPOSITE of
this plan's proposal** — see Outcome. WI-4 (wire archetype selection into the
skill, Plan 008 WI-5) is **open**. **Owner:** patina.

> **Reading this plan (marked up 2026-08-15).** The Outcome section is the
> decision of record. The `## Problem` and `## Direction` sections below it are
> the *pre-reversal* argument, kept as history because the reversal is the
> interesting part. Everything struck through is **RETRACTED and not in force**;
> unstruck text there survived. Do not implement from a struck line.

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

## Problem — largely RETRACTED (history; see Outcome)

~~Structural sameness, not visual sameness, is the AI fingerprint.~~
**RETRACTED.** The blind review overturned this framing: the chain "common →
LLM prior → AI fingerprint → credibility problem → avoid" only establishes its
first two links.

The concrete incident stands as an **observation**; only the inference from it
was wrong. In 2026-08, cert-watch's dashboard — four stat callouts over a
chart-and-table stack — was replicated near-exactly when a coworker asked an AI
tool for a *vulnerability* dashboard. That is evidence the shape is
**conventional**, not that it is wrong.

~~That layout is the single most statistically dominant dashboard shape in LLM
training data; tokens cannot fix it, because the tell is the skeleton. The
credibility cost is real: work that reads as "the default the machine emits"
gets discounted, whatever its quality.~~ **RETRACTED.** What survives is
narrower and is what `archetypes.md` implements: a generic skeleton filled with
*generic content* reads as machine output. The fix is semantic specificity, not
skeleton avoidance.

~~Today `patterns.md` §6 promotes the stat strip as a family pattern, i.e. the
catalog codifies the attractor.~~ **RETRACTED — and it turned out to be
backwards.** §6 was not wrong for promoting the stat strip; the ratified
dashboard grammar *is* a stat strip. §6 was wrong for describing it as
non-clickable decorative metric cards, which is the failure mode
`archetypes.md` bans. Fixed in `patterns.md` §6 on 2026-08-15: segmented
clickable cells on one surface.

**This half survives and became Tier 1:** the shapes that carry no tell
(tables, fields, chips, empty states) had no more standing than the ones that
do — the catalog didn't distinguish them.

## Direction — two-tier structure SURVIVED; the dashboard grammar was REVERSED

`docs/archetypes.md`, structured in two tiers. **This part shipped as
proposed:**

- **Tier 1 — invisible shapes** (table, field, chip, pill, callout, empty
  state, breadcrumb, chain): standardize aggressively, no differentiation
  needed. Nobody clocks a table as machine-made. *(Extended 2026-08-15: Tier 1
  also covers "the frame" — app shell and topbar, `patterns.md` §§1–2 — which
  the original split silently left untiered.)*
- **Tier 2 — page archetypes**: each entry states the canonical family layout,
  **names the banned default explicitly, and records why it is banned.** Models
  regress to attractors unless the prohibition is explicit and reasoned in
  context (Hallmark's documented experience: parity instructions smuggle banned
  patterns back in); an unexplained rule will be optimized away by the next
  agent session. ~~(dashboard, record detail, settings, activity log)~~ —
  **four when proposed, five as shipped:** Dashboard, **Inventory**, Record
  detail, Settings, Activity/log. Inventory was added by the reversal (mockup
  B's filter-bar count chips became the inventory's count grammar rather than
  the dashboard's), so any statement of "the four Tier-2 archetypes" is stale.

**Proposed dashboard grammar (the identity decision of WI-2) — RETRACTED in
full. Both reviewers chose the opposite. Preserved as history:**

- ~~**The primary object table leads the page.** The tool's job is its objects;
  the first viewport answers "what needs attention", not "how many things
  exist".~~ Reversed: the ratified grammar is summary → trend → urgent objects.
  The premise was not wrong — the first viewport *does* answer "what needs
  attention" — but a semantically loaded summary answers it faster than the
  table's first rows do.
- ~~**Counts live on the filter bar as clickable scopes** — `expiring-30d (12)`
  is a filter you can click, not a poster. A count you can act on is a tool; a
  count in a bubble is decoration.~~ **Half-survived, relocated.** The
  clickable-scope idea was mockup B's real contribution and is now the
  *Inventory* archetype's count grammar. On the Dashboard it was superseded by
  a stronger version of the same insight (WI-3 review, Q4): the strip's cells
  are *themselves* the clickable scopes, so the summary and the filter are one
  control. The "count in a bubble is decoration" claim was the specific error
  the review named — it jumped from information straight to representation and
  misread large labeled filter controls as decorative KPIs.
- ~~At most a **narrow summary rail** for genuinely cross-cutting posture; the
  four-stat hero row is demoted to "use sparingly, never the family
  signature".~~ **RETRACTED.** No demotion happened. And a one-row side rail is
  now itself banned by `archetypes.md`'s "One persistent page grid" rule, on
  independent grounds — it destabilizes the page's vertical axis.

**Banned defaults to name in v1** (disposition recorded 2026-08-15 — they had
been sitting in neither state, never carried into `archetypes.md` and never
withdrawn):

- ~~the 4-stat-card hero over chart+table (dashboard)~~ — **RETRACTED**, not
  banned. It is the ratified Dashboard grammar, in its segmented-clickable form.
  What *is* banned in its place is the **decorative summary**: stat cards
  without operational meaning.
- hero → 3-feature-cards grammar (any page) — **CARRIED**, with a why, into
  `archetypes.md` → "Banned failure modes that apply to every archetype".
- card-in-card nesting — **CARRIED**, same place.
- centered-everything on data pages — **CARRIED**, same place, narrowed to
  content *alignment* (the centered max-width page column is the family grid
  and stays).

## Work items

- **WI-1 — DONE.** Write `docs/archetypes.md` with the two tiers, the ~~four~~
  **five** Tier-2 archetypes, banned defaults + rationale. Demote `patterns.md`
  §6 with a pointer. *(Shipped; the cross-archetype banned defaults were added
  2026-08-15, and §6's body — not just its pointer — was corrected then too.)*
- **WI-2 — DONE (decided the opposite of the proposal).** Dashboard grammar
  decision (human). Two rendered mockups of the cert-watch dashboard content:
  (a) current stat-strip layout, (b) object-first + counts-on-filters. Side by
  side, both themes. Binary choice. **Both the owner and the blind review chose
  (a)** — see Outcome.
- **WI-3 — DONE.** cert-watch assessment (pilot). Map the two ratified
  archetypes onto cert-watch's real IA (post-055: Certificates at `/`, Posture,
  Activity, Settings — there is no separate dashboard page). Deliverable:
  `plans/007-wi3-assessment-cert-watch.md`, reviewed by reviewer + owner, with
  the prototype result. ~~Proposal to assess: `/` takes the Inventory grammar
  (full table + filter-bar count chips), `/posture` takes the Dashboard grammar
  (summary strip + expiry histogram with the +30d marker + urgent shortlist).~~
  **That proposal was WITHDRAWN by the assessment itself** — it died on the
  facts of `posture.html` (a distinct analytic domain, not a general dashboard)
  and on the finding that Plan 055 had already implemented most of the ratified
  dashboard grammar on `/`. Outcome: Option A modified. The reshape is a
  cert-watch plan and an owner call.
- **WI-4 — OPEN — Wire into the skill** (Plan 008 WI-5, also open): archetype
  selection becomes a stated step — an agent building a page names its
  archetype out loud before writing markup, and pages must record their
  archetype in the surface brief. Blocked on the skill existing at all.

## Acceptance

- **MET** — `docs/archetypes.md` exists; every Tier-2 entry has a banned-default
  line with a why, plus (2026-08-15) the cross-archetype set.
- **MET** — the dashboard grammar decision is recorded (it went the other way):
  after this plan it is a decision, not an accident.
- **MET** — cert-watch assessment delivered with screenshots.

## If declined

The family keeps standardizing whatever shape the model emits first. The
coworker-replication incident recurs with each new dashboard, and the
distinctive token layer keeps getting spent on structurally generic pages.
