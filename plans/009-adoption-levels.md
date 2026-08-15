# Plan 009 — adoption levels (making partial conformance legitimate and visible)

**Status:** Proposed 2026-08-15. **Owner:** patina + every consumer.
**Human decisions required** — marked **[D1]**–**[D4]** below.
Depends on Plan 005 (the gate); reshapes the normative force of Plan 007.

## Problem

Plans 004–008 built four layers — tokens, components, page archetypes, content
model — and gave them all the same normative voice. "Every page names its
archetype." "Every UI-bearing repo keeps `UI-INVENTORY.md`." But the layers are
not equally adoptable, and the gap is not small.

Measured against the estate as it actually is:

| Obligation | Decidable by | Work for a second consumer |
|---|---|---|
| Vendored + stamped tokens, no drift | a script | mechanical, minutes |
| Contract clean (prefix rule, var() resolve, ratchet) | a script | bounded, hours |
| `UI-INVENTORY.md` per record type | a reviewer, in minutes | bounded, ~a page per record type |
| Surface brief per page | a reviewer | ~22 files for gpo-lens, each needing a derivation |
| **Name each page's archetype** | **nobody, today** | **unbounded** |

The last row is where adoption stops. gpo-lens ships `resultant.html`,
`baseline_diff.html`, `golden_diff.html`, `conflicts.html`, `admx_coverage.html`;
dossier ships `review_queue.html`, `break_glass.html`, `evidence_integrity.html`.
Essentially none are a Dashboard, Inventory, Record detail, Settings or Activity
page. `docs/archetypes.md` then says new archetypes get added "before the first
page ships in that shape" — but those pages shipped months ago. So conformance
means inventing six to ten archetypes, each needing a named failure mode and a
blind rendered review, filed as PRs **in a different repo** — while
`archetypes.md` simultaneously instructs a deviating page to "amend this file in
the same PR", which is impossible: patina is consumed by vendoring, and `docs/`
isn't even vendored. A gpo-lens PR cannot touch a patina file. Ever.

Three consequences, all live:

1. **The rational move for a consumer is to take the token gate and ignore
   everything above it.** That is precisely the outcome this branch exists to
   prevent, and it is what the incentives currently produce.
2. **Partial adoption is invisible.** Nothing distinguishes "gpo-lens considered
   the archetype tier and deferred it" from "nobody ever looked." Both render as
   silence. An estate-wide standard whose compliance state cannot be printed is
   not a standard.
3. **The rules aren't where the work is.** `sync.sh` vendors `tokens.css`,
   `theme.js`, `fonts/` and `patina-check.py`. It does not vendor a single line
   of `docs/`. The estate's UIs are written by agents; an agent working in
   gpo-lens has no local copy of the standard it is meant to follow. Plan 006
   already made this argument about components ("prose for humans instead of code
   for machines") and it applies with more force to the rules themselves.

This plan does not add a layer. It makes the existing layers adoptable by
matching each one's normative force to what can actually decide it, and by
making a consumer's position on the ladder a committed, visible fact.

## Direction

### 1. Declared conformance levels

Each consumer commits a `patina.toml` at its repo root:

```toml
[patina]
level  = 1            # what this tool currently guarantees
accent = "gpo-lens"
prefix = "gp"
static = "src/gpo_lens/web/static"
```

| Level | Guarantees | Decided by |
|---|---|---|
| **L0 vendored** | tokens vendored + stamped; no drift from upstream | script |
| **L1 contract-clean** | L0 + no contract-token shadowing, every `var()` resolves, prefix rule, colour ratchet | script |
| **L2 content-modelled** | L1 + `UI-INVENTORY.md` exists and is diffed by any PR touching templates or routes; no concept with two editing controls | script (diff rule) + reviewer (concepts) |
| **L3 structured** | L2 + every page has a surface brief; no page instantiates a banned failure mode | reviewer |

`check_patina.py` reads the declaration and enforces **exactly** that level —
no more, so a consumer at L1 gets a clean, meaningful green rather than a wall
of failures about surface briefs it never promised; and no less, so the level is
a real commitment rather than a wish.

The point is the declaration, not the ladder. **A tool may sit at L1
indefinitely and be in good standing.** What it may not do is be at L1 without
saying so. Raising a level is a commit, with a diff, at a moment someone chose.
Lowering one is too — which is the honest way to record "we tried L3 on this
tool and it wasn't worth it."

This also makes the estate's state a one-line query rather than an
archaeology exercise: today, answering "which tools conform?" took a review pass
across four repos, and the answer was "cert-watch, and only since yesterday."

**[D1]** Is L2 expected of every UI-bearing tool eventually, or is L1 a
legitimate permanent resting place for a tool whose UI is small (sluice) or
whose pages are all one archetype? My recommendation: L1 permanent is fine and
should be said out loud; L2 is expected only where a tool has more than one
record type with free-text fields — that is the condition that produced the
notes defect in the first place.

### 2. The archetype set becomes open; the banned modes carry the normative weight

Today `archetypes.md` is a closed taxonomy plus an instruction to extend it
before shipping. Invert that:

- **Normative at L3:** a page (a) does not instantiate a banned failure mode,
  and (b) has a surface brief whose first line is the operator questions it
  answers, in decision order.
- **Non-normative:** the five archetypes are *worked examples of the
  derivation*, not a set of boxes every page must fall into. The 60-line
  "Deriving a page" method moves to an advisory appendix — it is good thinking
  and unusable as a gate (its own worked example shows two readings of the same
  question, one called strong and one weak, with no criterion separating them).

The banned failure modes are the falsifiable core and should be treated as the
product: "the everything panel", "the card grid of settings tiles", "the social-
media activity feed of avatar cards with relative timestamps". Each is
recognizable in a screenshot, each carries a why. Plan 007's three orphaned
bans (hero → 3-feature-cards, card-in-card nesting, centered-everything on data
pages) belong here too.

Under this shape `baseline_diff.html` needs no ratification ceremony. It needs a
surface brief and an absence of banned shapes. **Promotion to a named archetype
becomes a reward for observed recurrence — a shape appearing in two or more
tools — rather than a prerequisite for shipping the first one.** That also
fixes the blind-review problem by making it rare: blind review gates archetype
*promotion*, which happens a few times a year, not every page.

**[D2]** Does demoting the derivation method to advisory lose something you
wanted enforced? It is the newest and most-invested text on the branch, and I am
proposing it not be a gate. My reading is that it earns its place as the
document that teaches the reasoning, and loses nothing by not pretending to
adjudicate.

### 3. Deviation is recorded locally and promoted asynchronously

Replace "amend this file in the same PR; never override locally" — impossible
across a vendored boundary — with a path that exists:

- A page whose shape patina doesn't cover records it in its own surface brief:
  `archetype: local/diff-view — deviation; patina-proposal: <link or none>`.
- **The deviation is legal immediately.** Nothing blocks the consumer's PR.
- patina harvests deviations across consumers when convenient. Two independent
  tools reaching for the same shape is the evidence that it is a family pattern
  rather than one tool's local need.

This is the only escalation compatible with vendoring, and it inverts the
evidence flow in the right direction: the estate tells patina what the standard
should be, instead of patina guessing ahead of the estate.

### 4. Vendor the rules, not just the values

`sync.sh` gains `--docs`, vendoring a stamped `patina/` directory into the
consumer (`token-contract.md`, `patterns.md`, `archetypes.md`,
`content-model.md`, plus `patina.toml`). Same delimiters, same hash, same
staleness story as `tokens.css`.

An agent editing gpo-lens then reads the standard from the repo it is working
in. This is Plan 006's own argument — code for machines, not prose for humans —
applied to the rules themselves, and it is the cheapest of the four moves.

**[D3]** Vendoring docs means the standard is duplicated into every consumer
and can go stale there. The stamp makes staleness *detectable*, not impossible.
The alternative is a pointer (a URL in `patina.toml`) that an agent may not
follow. I recommend vendoring — a stale local copy that the gate flags beats a
current remote copy nobody reads.

## Work items

- **WI-1 — Ratify the level model (human).** [D1]. Then `patina.toml` schema +
  `check_patina.py --level` (it already has every L0/L1 check; the work is
  reading the declaration and scoping the checks to it).
- **WI-2 — Restructure `archetypes.md`** per §2: banned modes normative,
  archetypes as examples, derivation method to an advisory appendix. [D2]
  (Plan 007's three orphaned bans were carried in on 2026-08-15 by the
  editorial pass, as "Banned failure modes that apply to every archetype" —
  which is already the shape this plan argues for, arrived at independently.
  What remains is demoting the archetype *taxonomy* and the derivation method.)
- **WI-3 — Deviation protocol** in `content-model.md` rule 5 + `archetypes.md`;
  delete the impossible same-PR amendment rule.
- **WI-4 — `sync.sh --docs`** + stamped docs block + `patina.toml`. [D3]
- **WI-5 — The inventory-diff check.** `content-model.md` rule 4 currently says
  it is "enforced in review, not code", but it is the most mechanical rule in
  the whole content-model tier: a PR that touches `templates/` or `routes/`
  without touching `UI-INVENTORY.md` is a one-line CI check against the diff.
  It is also the rule aimed squarely at the defect class that motivated the
  tier. **[D4]** — this reverses a stated decision, so it needs one: make it
  code (advisory first, then blocking), or leave it to review?
  My recommendation: ship it advisory now, blocking at L2.
- **WI-6 — Estate status.** `patina status` walks the consumer repos, reads each
  `patina.toml`, runs the gate at its declared level, and prints the ladder.
  Cheap, and it is the artifact that makes levels real rather than decorative.

## Acceptance

- Every consumer repo declares a level, and the declaration is enforced.
- gpo-lens and dossier can reach a *named, honest* level without inventing a
  single archetype.
- A deviating page has a legal path that does not require editing another repo.
- "Which tools conform, to what?" is answered by running a command.

## If declined

The four layers keep one voice and one implied deadline. Consumers keep taking
the token gate and skipping the rest, because that is the only bounded part —
and because nothing records that they did, the estate cannot tell the difference
between a decision and an oversight. The archetype tier stays a research
programme with a gate in front of it, and the standards that were written to
stop drift accumulate their own.
