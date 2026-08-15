# Adopting patina — the conformance declaration

A consumer commits a `patina.toml` at its repo root saying which parts of
patina it claims, and by what mechanism. `check_patina.py --declaration
patina.toml` validates the claims and reports them.

**This file is consumer-owned.** `sync.sh` never writes or rewrites it. The
standard is upstream-owned; the adoption declaration is downstream-owned. That
boundary is the point: patina says what conformance *means*, each tool says
what it *claims*, and no sync can quietly change a tool's answer.

```toml
[patina]
version = "0.5.0"        # the patina release this tool tracks
accent  = "gpo-lens"
prefix  = "gp"           # tool-local tokens must carry --gp-
static  = "src/gpo_lens/web/static"

[conformance.vendor]
state = "enforced"

[conformance.contract]
state = "enforced"

[conformance.content_model]
state = "attested"
note  = "no UI-INVENTORY.md yet; concepts and their single controls enumerated below"

[conformance.structure]
state = "deferred"
why   = "no surface briefs written; these page shapes have no vocabulary yet"
until = "the first page rewrite, or a second tool reaching for the diff view"
```

> **"Read-only tool" is a claim about the wrong thing.** This example first
> declared gpo-lens's content model `not-applicable` on the grounds that it is a
> read-only analysis tool. Adopting patina in gpo-lens on 2026-08-15 showed that
> was false: gpo-lens is read-only towards *Active Directory*, not towards *its
> own store*. It persists finding triage state — including a 2000-character
> operator note, which is the precise concept class that motivated this facet —
> and snapshot lifecycle. The facet turns on whether the tool persists mutable
> domain state a user can edit, not on where its input comes from. Enumerate the
> write paths before claiming `not-applicable`; "it's a reporting tool" is an
> intuition, not evidence.

## Why facets and not levels

The first draft of Plan 009 proposed a ladder — L0 vendored, L1 contract-clean,
L2 content-modelled, L3 structured. It was wrong, and the plan contained the
evidence against it. Only one of those dependencies is real: the contract check
cannot evaluate anything until a stamped block defines what the contract *is*.
Nothing about a `UI-INVENTORY.md` requires contract-clean CSS, and nothing about
a surface brief requires an inventory.

Two things settle it:

- **A scalar cannot say "not applicable."** "This tool stopped at L1" and "this
  tier does not apply to this tool" are completely different facts, and the
  second is the common case — a read-only analysis tool has no content model to
  inventory, and never will. A ladder can only record it as a shortfall.
- **A number implies a direction.** If L3 exists, L3 is better, whatever the
  prose says; people and agents optimise toward it. The plan had to spend a
  paragraph disclaiming the semantics of its own data structure, which is how
  you know the structure was wrong.

For the same reason there is **no rollup score**. A summary column would be read
as 3/4-is-worse-than-4/4 and we would have reinvented levels with more syntax.
The matrix is the answer; the facets mean different things and collapsing them
destroys the information that justified separating them.

## States, and what each one costs

| state | meaning | required |
|---|---|---|
| `enforced` | a script decides it, and it blocks | — |
| `advisory` | a script checks it, and it does not block | — |
| `attested` | the author claims it per change (see below) | — |
| `reviewed` | a human decided it | `reviewed_through` |
| `deferred` | deliberately not done yet | `why`, `until` |
| `not-applicable` | this facet does not apply to this tool | `why` |

**patina fixes which states are legal per facet.** A tool cannot declare
`structure = "enforced"`, because no script decides whether a page expresses an
operator's mental model. Allowing the claim would make machine proof, human
review and author attestation interchangeable in the output — and the point of
typing them separately is that they are not.

Machine-decidability is not importance. "Every `var()` resolves" is trivial to
automate and comparatively unimportant; "this screen matches how the operator
thinks about the job" is the opposite. patina does not weaken a requirement
because a script cannot judge it. It states honestly that some guarantees mean
*mechanically proven* and others mean *reviewed*.

**`deferred` needs a trigger, not an excuse.** `until = "pending a second
editing surface"` is a decision with a condition attached. `why = "not worth
doing"` alone is a standards graveyard, and the gate refuses it.

**`not-applicable` needs a reason** for the same cause the colour ratchet's
`patina-allow` needs one: an unexplained exemption is a disabled check with
better manners. Without this, a tool declares everything `not-applicable` and
shows all green.

**`reviewed` names a commit, not a date.** A date tells you when somebody
looked; a revision lets the tool work out whether anything relevant happened
afterwards. `patina status` can then distinguish *reviewed*, *reviewed but N
commits have landed since*, and *never reviewed*. Scoping staleness to
UI-relevant paths — templates, styles, the routes that render them — is the
obvious refinement and is deliberately not built yet; storing the revision is
the part that matters.

## Attestation

Some semantic gates have a correct answer of "nothing changed." The content
model is one: plenty of template edits do not touch it. A gate that demands a
`UI-INVENTORY.md` diff on every template change teaches exactly one behaviour —
edit the file until CI goes green — and converts a review artifact into
ceremonial churn.

So the claim is made as a commit trailer:

```
Content-Model: reviewed-unchanged
```

You cannot make attestation expensive; an agent can produce any ceremony we
invent. You *can* make it legible. A trailer is better than touching a file
precisely because nobody can mistake it for substantive work — it gives a
reviewer a discrete claim to accept or challenge.

The general rule, which cost us a real bug to learn: **never make meaningless
file modification the cheapest way to satisfy a semantic gate.** The colour
ratchet was a single integer, so swapping one violation for another passed while
removing one turned CI red — the cheap path pointed away from the goal. Agents
find that immediately.

Attested facets are reported as `attested`, never as `enforced`.

## Versions

`version` is the patina release the tool tracks; the stamp inside the vendored
`tokens.css` records the revision actually vendored. With `--upstream` the gate
checks they agree, so a declaration cannot drift from reality.

A newer patina is **not** a conformance failure — it is an available upgrade,
reported as a note. Otherwise every commit to patina turns the whole estate red
and vendoring has bought nothing. See `CHANGELOG.md` for what a version bump
means and for the per-release impact metadata (`visual-change`,
`baseline-review`, `consumer-code-change`) that tells you what adopting one
actually costs.

## Deviation

A page whose shape patina has no vocabulary for records that in its own surface
brief and carries on:

```
archetype: local/diff-view — deviation; patina-proposal: <link or none>
```

The deviation is legal immediately; nothing blocks the consumer. patina harvests
deviations across tools when convenient, and a shape reaching for the same
solution in two independent tools is a good **trigger for review** — not
automatic promotion, since two tools can make the same mistake independently.

The rule this replaces ("if a page needs a different structure, amend
`archetypes.md` in the same PR") described a monorepo we do not have. patina is
a separate repository consumed by copy; a gpo-lens PR cannot touch a patina
file, so as written every legitimate deviation was a process violation.
