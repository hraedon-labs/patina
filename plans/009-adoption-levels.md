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

### 1. Declared conformance facets  — BUILT 2026-08-15, see `docs/adoption.md`

> **This section replaced a ladder.** The first draft proposed L0→L1→L2→L3.
> External review (Sol, 2026-08-15) rejected the ladder and the argument was
> conclusive, so the ladder is recorded here as a retracted proposal rather
> than quietly deleted — the reasoning is the useful part.
>
> ~~L0 vendored → L1 contract-clean → L2 content-modelled → L3 structured, with
> `check_patina.py` enforcing exactly the declared level.~~ **RETRACTED.**
> Three faults, and the plan's own text contained the evidence for all three:
>
> - **Only one of the dependencies was real.** The contract check genuinely
>   cannot evaluate anything until a stamped block defines what the contract
>   *is*. Nothing else was ordered: an inventory does not require contract-clean
>   CSS, and a surface brief does not require an inventory. The ladder asserted
>   a dependency chain that does not exist.
> - **A scalar cannot say "not applicable".** "This tool stopped here" and "this
>   tier does not apply to this tool" are different facts, and a ladder can only
>   record the second as a shortfall. (The example first used here — "a
>   read-only analysis tool has no content model" — was itself falsified by
>   gpo-lens within the day; see §5. The structural point survives its own bad
>   example: gpo-lens's *structure* facet is legitimately `deferred` because six
>   of its pages match no archetype, and a ladder could only call that failure.)
> - **A number implies a direction.** If L3 exists, L3 is better, whatever the
>   prose says. The draft had to spend a paragraph disclaiming the semantics of
>   its own data structure, which is how you know the structure was wrong.

Each consumer commits a `patina.toml` at its repo root declaring each facet
independently, with the mechanism that decides it:

```toml
[patina]
version = "0.5.0"          # the patina release this tool tracks
accent  = "gpo-lens"
prefix  = "gp"

[conformance.vendor]
state = "enforced"

[conformance.contract]
state = "enforced"

[conformance.content_model]
state    = "attested"
evidence = "snapshot: create /ingest, delete /ingest/delete. triage (status + note): one form per row, /findings/{id}/triage. No second control for either."

[conformance.structure]
state = "deferred"
why   = "no surface briefs written; these page shapes have no vocabulary yet"
until = "the first page rewrite, or a second tool reaching for the diff view"
```

States: `enforced` · `advisory` · `attested` · `reviewed` · `deferred` ·
`not-applicable`. **patina fixes which are legal per facet**, so a tool cannot
declare `structure = "enforced"` when no script decides it — otherwise machine
proof, human review and author attestation become interchangeable in the
output, and typing them separately buys nothing.

Machine-decidability is not importance. "Every `var()` resolves" is trivial to
automate and comparatively unimportant; "this screen matches how the operator
thinks about the job" is the opposite. patina does not weaken a requirement
because a script cannot judge it — it says honestly which guarantees are
*mechanically proven* and which are *reviewed*.

Escape hatches cost something, on the same principle as the colour ratchet's
`patina-allow`: `deferred` needs an `until` (a trigger, not an excuse —
"deferred pending a second editing surface" is a decision, "deferred, not worth
it" is a graveyard), `not-applicable` needs a substantive `why`, `reviewed`
names the commit it was reviewed through so staleness is computable rather than
a timeless boolean, and omitting a facet fails outright because silence is the
condition this file exists to remove.

**No rollup score, deliberately.** A summary column would be read as
3/4-is-worse-than-4/4 and we would have reinvented levels with more syntax.

**[D1] — RESOLVED 2026-08-15.** Permanent partial adoption is legitimate and
now expressible. The applicability criterion took two revisions, and the second
one is the interesting part:

1. *"More than one record type with free-text fields"* — overfit to the
   incident that exposed the problem, the same error Plan 007 made when it
   banned a layout because one coworker's generic prompt reproduced it.
2. *"Persisted mutable domain state exposed through more than one reachable
   editing surface"* — better, and still wrong. gpo-lens retired it on contact:
   its triage note has exactly one editing surface and perfectly obvious
   ownership, and it is *still* persisted operator-authored domain state that
   the system should be able to account for.
3. **Final: content-model conformance applies to a tool that persists
   operator-editable domain state.** `not-applicable` is for genuinely
   read-only UIs, or state that is only incidental presentation/session
   preference. The old triggers become **risk multipliers** — how much
   attention the inventory deserves, not whether one is needed.

The lesson generalises past this rule: each revision moved from *the shape of
the incident* toward *the property that makes the check worth doing*. A tiny
tool with one mutable record type needs a ten-line inventory, not an argument
about whether it qualifies.

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

- **WI-1 — The declaration.** **DONE 2026-08-15** (as facets, not levels).
  `patina.toml` schema, `check_patina.py --declaration`, per-facet legal
  mechanisms, the required `why`/`until`/`reviewed_through` fields, and the
  facet report. cert-watch declares against it. Version semantics shipped
  alongside: `VERSION` + `CHANGELOG.md`, where semver answers consumer
  compatibility (a palette change is *minor* even though it invalidates every
  baseline) and per-release impact metadata answers what adopting costs
  (`visual-change`, `baseline-review`, `consumer-code-change`).
  Still open: [D1]'s applicability wording.
- **WI-2 — Restructure `archetypes.md`** per §2: banned modes normative,
  archetypes as examples, derivation method to an advisory appendix. [D2]
  (Plan 007's three orphaned bans were carried in on 2026-08-15 by the
  editorial pass, as "Banned failure modes that apply to every archetype" —
  which is already the shape this plan argues for, arrived at independently.
  What remains is demoting the archetype *taxonomy* and the derivation method.)
- **WI-3 — Deviation protocol** in `content-model.md` rule 5 + `archetypes.md`;
  delete the impossible same-PR amendment rule.
- **WI-4 — `sync.sh --docs`.** **DONE 2026-08-15.** Vendors patina's docs with
  a provenance banner, a manifest of source hashes, and `OWNERSHIP.md`;
  `check_patina.py --docs` verifies against the manifest and, with
  `--upstream`, against patina at the stamped revision. Same version semantics
  as the token block. [D3] resolved: vendor, don't point. Kept deliberately
  boring — no `patina status`, no path inference, no generated indexes.
  cert-watch and gpo-lens both carry the docs and both exclude them from ruff.
- **WI-5 — The content-model change gate.** **DONE 2026-08-15, advisory.**
  `scripts/check_content_model.py`. **[D4] resolved as advisory, and the
  blocking half is now explicitly deferred, not merely postponed.** The naive
  rule (templates changed ⇒ inventory must change) is only approximately
  correlated with the content model; as a *blocking* gate it would teach one
  behaviour — edit `UI-INVENTORY.md` until CI is green — and turn a review
  artifact into ceremony, because the correct inventory diff is frequently zero
  bytes. So the gate accepts either an inventory diff or a
  `Content-Model: reviewed-unchanged` commit trailer, and reports which. A
  trailer beats a file touch not because it is costly (no attestation can be)
  but because it cannot be mistaken for substantive work.
  Family rule now in `content-model.md`: **never make meaningless file
  modification the cheapest way to satisfy a semantic gate.**
  Still unbuilt: the duplicate-control detector — the half that would have
  caught the notes defect directly.
- **WI-6 — Estate status.** `patina status` walks the consumer repos, reads each
  `patina.toml`, runs the gate as declared, and prints the matrix. Do this
  **after** gpo-lens, so it is shaped by two real declarations rather than one.
  No rollup column.

### 5. What gpo-lens actually taught (2026-08-15)

The facet model was deliberately taken to a second consumer *while* it was
still being designed, because plans 004–008 accumulated their contradictions
precisely by not doing that. gpo-lens was chosen because its expected result
was **not** "all green". Findings, in order of how much they changed the model:

- **The doc's own worked example was wrong about the tool it named.**
  `adoption.md` used gpo-lens as the case for `content_model =
  "not-applicable"` — "read-only analysis; no persisted mutable domain state".
  Enumerating the write paths showed gpo-lens is read-only towards *Active
  Directory*, not towards *its own store*: it persists finding triage state
  including a 2000-character operator note, plus snapshot lifecycle. The
  criterion turns on persisted mutable domain state a user can edit, not on
  where the input comes from. Corrected in `adoption.md`; **"it's a reporting
  tool" is an intuition, not evidence.**
- **`attested` earned its place immediately.** gpo-lens has no
  `UI-INVENTORY.md` and no human has reviewed its content model, but its
  concepts and controls were enumerated concretely. `reviewed` would have
  overclaimed, `deferred` would have erased real work, `not-applicable` was
  false. The state that fit is the author-claim one.
- **`structure = deferred` is the honest answer and the reason the facet cannot
  be `enforced` anywhere.** Six gpo-lens pages (resultant, baseline_diff,
  golden_diff, conflicts, admx_coverage, briefing) match none of the five
  archetypes. They are not failure modes; they are shapes patina has no
  vocabulary for. This is the ladder's central defect reproduced in a real
  repo: under L0→L3 gpo-lens could never express this without appearing to
  have *failed* a tier it was never sensibly subject to.
- **The structure tier is calibrated on monitoring tools.** This is the finding
  with the longest reach. cert-watch's pages are dashboards, inventories and
  record details, and all five archetypes describe them — because all five were
  derived from cert-watch. gpo-lens's core pages are **comparisons and
  derivations**: a diff view (`baseline_diff`, `golden_diff`, `changelog`), a
  coverage reconciliation (`admx_coverage`), a per-principal evaluation trace
  (`resultant`), a lens-switched conflict table (`conflicts`). Their subject is
  a *relationship between two objects*, not a set of objects, and the archetype
  vocabulary has no entry for that whole category.

  Checked against the banned list, none of them is a failure mode. The nearest
  thing to a violation is `.gp-danger-remediation` at `--panel-2` inside a
  panel, and the second surface distinguishes remediation from findings — a
  reason beyond containment, which the rule as written permits.

  **This is the first real candidate for the deviation-harvest path**, and it
  arrives having already met patina's own stated trigger: a shape recurring in
  more than one place. Do not promote it on that basis alone — two tools can
  reach for the same wrong shape — but a "comparison" archetype is now the
  obvious next thing for patina to *earn* from the estate rather than invent.
- **`--fs-xs` had no answer in the standard.** `token-contract.md:67` gives the
  type scale as bare numbers with no statement of what each step is *for*, so
  "is 12px load-bearing here?" could not be answered from the contract; it had
  to be reasoned from gpo-lens's own internal consistency (its densest chrome
  already hardcodes 10.5px, so 11px is nowhere near the floor). **Open item:**
  the scale needs a line per step saying what it is for. A number with no job is
  a value nobody can defend or overrule.
- **Exactly one genuine token drift across a whole hand-synced consumer**
  (`--fs-xs`, 12px vs 11px). Of 25 differing values, 8 were the tool's own
  accent (not drift at all) and 16 were the deliberate status-quad change —
  i.e. the release-impact metadata (`visual-change: yes, baseline-review:
  required, consumer-code-change: no`) described this upgrade exactly.

### 6. What dossier taught (2026-08-15) — three defects in the gate, all patina's

Third consumer, and the most productive of the three. Every disagreement turned
out to be case (b): patina accusing a consumer of a violation it had not
committed.

- **There was no legal way to print.** dossier re-maps 13 contract tokens under
  `@media print`; the no-shadowing rule had no context exemption and patina
  ships no print values. patina defines exactly two rendering contexts and both
  are screen — paper is a third. A provenance tool whose printed record is an
  audit deliverable could not both print legibly and conform, and the only
  "compliant" routes were to stop printing or to re-plumb ~120 rules onto
  `--ds-*` aliases so its components stopped referencing contract tokens at all
  — destroying the thing the contract exists to protect. Fixed: at-rule-scoped
  re-mapping is legal with a stated reason, block-scoped. **patina still owes
  the real fix — shipping `@media print` values as a third context.** That is a
  family concern and it needs a design decision, so it is queued, not assumed.
- **BEM modifiers read as token declarations.** `TOKEN_DEF_RE` matched
  `.ds-btn--crit:hover` and accused dossier of shadowing a status colour — the
  most serious violation the contract has — on a line that declares nothing.
  The suggested remedy was to rename the class. Every consumer using BEM would
  have hit it.
- **The dead-class check could not see inside at-rules.** Brace-parity splitting
  made every selector in `@media`/`@supports` invisible, and inside those blocks
  scanned declarations as selectors. dossier's five "dead" classes were all
  defined, in media queries. gpo-lens's twelve were re-derived and hold.
- **`structure` had no `attested` state.** dossier completed a full archetype
  audit, came out clean, and had nowhere to put it. The same argument that put
  `attested` on `content_model` — `reviewed` means a human decided, which an
  agent-written change cannot claim — applies here, and omitting it from the
  facet where an agent audit is most often the *only* evidence was inconsistent.

Two results worth keeping beyond the fixes:

- **`activity_feed.html` is the negative control the banned-modes list needed.**
  dossier ships a page with the banned *name* and none of the banned
  *properties*: a dense filterable reverse-chronological table with absolute
  timestamps, no avatars, no cards. The ban is correctly scoped to card grammar
  plus relative time rather than to the noun — which is exactly the distinction
  Plan 007's retraction was about, now confirmed from the other direction.
- **The content-model facet found a real defect on its first serious use.**
  dossier's `review_note` and comment `body` are two free-text controls in the
  same rail of the same page, both operator prose about the same work item,
  both appended to the same event chain, both read back by the same helper into
  the same template slot, distinguished only by a CSS modifier — and one is
  silently discarded for non-verdict transitions. That is content-model rule 1
  exactly, found by applying the rule rather than by anyone tripping over it.
  Recorded in dossier's declaration; fixing it is design work.

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
