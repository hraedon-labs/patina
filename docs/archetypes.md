# patina page archetypes (structure tier 2)

`patterns.md` covers component shapes. This document covers whole pages — how
a tool's screens are laid out — in two tiers with different rules. It exists
because of a specific, dated lesson (Plan 007): **structural sameness is the
AI fingerprint, not visual sameness.** In 2026-08 the family's four-stat
dashboard layout was replicated near-exactly by an AI tool given a generic
"vulnerability dashboard" prompt — because that layout *is* the statistical
default. Distinctive tokens spent on a default skeleton still read as
machine output, and that costs credibility.

## Tier 1 — invisible shapes: standardize aggressively

Tables, form fields, chips, pills, callouts, empty states, breadcrumbs,
chains (`patterns.md` §§4, 7–14). These carry no authorship signal — nobody
clocks a table as machine-made. Use the canonical shapes everywhere, without
variation for variation's sake. Coherence here is pure win.

## Tier 2 — page archetypes: deliberate grammar, named banned defaults

Every page names its archetype (in its surface brief — see
`content-model.md`). Each archetype below states the family layout, the
**banned default**, and *why* it is banned — the why stays in this file
because an unexplained rule gets optimized away by the next agent session
that finds the default more natural. If a page genuinely needs a different
structure, amend this file in the same PR; never override locally.

### Dashboard (the tool's landing view)

**Family grammar (pending WI-2 ratification — mockups A/B):**

- **The primary object table leads the page.** The first viewport answers
  "what needs attention", not "how many things exist".
- **Counts live on the filter bar as clickable scopes** — `expiring-30d (12)`
  is a filter you can click, not a poster. A count you can act on is a tool;
  a count in a bubble is decoration.
- At most a **narrow summary rail** for genuinely cross-cutting posture
  (grade, next expiry, last scan). One rail, not a row of heroes.

**Banned default:** the four-stat-card hero row above a chart-and-table
stack. *Why:* it is the single most common dashboard shape in AI training
data and the layout every generic prompt produces; it also inverts priority —
it spends the best screen real estate restating what the table already shows.
`patterns.md` §6 (stat strip) is hereby demoted: legal inside a rail or a
posture page, never as the landing hero.

### Record detail (one certificate, one GPO, one host)

**Family grammar:** identity header (`page_head`: name, status pill, scope
chip), then panels in *task order* — what the operator checks first goes
first. Every concept appears **once**; the single editing control for each
concept lives with its display (see `content-model.md` rule 1). Related
records are links, not embedded editors.

**Banned default:** the "everything panel" — a detail page that grows one
panel per feature shipped, each with its own free-text field and save button.
*Why:* this is accretion's natural shape (cert-watch's detail page reached
seven free-text fields via four endpoints before Plan 055); panels-per-feature
mirrors git history, not operator tasks.

### Settings

**Family grammar:** sectioned single column, one route per section
(`/settings/{section}`), persistent section nav. Each setting states its
effect in one sentence next to the control. Dangerous actions are separated
and labeled by consequence ("Delete 47 records"), not by severity theater.

**Banned default:** the card grid of settings tiles, and toggles whose labels
name the mechanism ("Enable feature flag X") instead of the outcome. *Why:*
tile grids force equal visual weight onto unequal decisions; mechanism labels
outsource the thinking to the reader.

### Activity / log

**Family grammar:** a dense, filterable, reverse-chronological table —
timestamp (mono, `tnum`), actor, action, object-as-link. Filters follow the
dashboard's counts-on-filters rule. Zero decoration: the log IS the content.

**Banned default:** the social-media "activity feed" of avatar cards with
relative timestamps ("3 hours ago") and icon badges. *Why:* card feeds cut
row density 3–5× and relative time is useless in an audit context; both are
consumer-app grammar leaking into an operations tool.

## Applying this file

- An agent building or reshaping a page states the archetype out loud before
  writing markup, and records it in the page's surface brief.
- A page that matches a banned default is a review finding even if every
  token and component on it is conformant.
- New archetypes (wizard, report, diff view …) get added here — with a banned
  default and a why — before the first page ships in that shape.
