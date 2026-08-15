# Plan 008 — content-model contract + the patina skill (the missing layer)

**Status:** partially executed, record corrected 2026-08-15. **WI-1**
(`docs/content-model.md`) and **WI-2** (cert-watch `UI-INVENTORY.md`) are
**done**. **WI-3** (the notes adjudication) was **DECIDED by the owner
2026-08-14** — the cert-watch implementation is queued, not built. **WI-4**
(detector), **WI-5** (skill) and **WI-6** (surface briefs) are **open** — which
means `scripts/check_content_model.py`, `skills/patina-ui/`, and every
`ui/surfaces/<route>.md` do not exist anywhere in the estate yet, and
`docs/content-model.md` says so in its Enforcement section. **Owner:** patina;
pilot in cert-watch. This is the layer no external tool provides — Hallmark's unit of
analysis is the page's visual system, Impeccable's is the element; neither
sees information architecture. It is also the layer where the estate's actual
cited failure lives.

## Problem

A single cert-watch certificate page surfaces **seven free-text fields from
two tables via three editing surfaces and four write endpoints**; two of them
are near-identical 10,000-char notes textareas whose placeholder text invites
each other's content. Cause (from git): two features landed two months apart
(`certificates.notes` from the design handoff; `hosts.notes` from BC-020 for
certless hosts, then also exposed on the cert page) and nobody reconciled,
because no rule exists at the concept level. Decisive evidence that the layer
is missing: **Plan 055 — a dedicated rationalization pass — saw the symptom
("host notes editable in 3 places") and could not act on it**, because its
rules governed controls ("one segmented control, one toggle"), not concepts.
Visual regression, token gates, and lint are all blind here: two duplicate
notes boxes are perfectly pixel-consistent.

## Direction

### `docs/content-model.md` — the rules

1. **One concept, one control.** Each concept a record exposes (ownership,
   procedure notes, tags, ...) has exactly one editing control across the UI.
   A proposed second free-text field on a record must either merge into the
   existing one or carry a visibly distinct scope — in its label AND wherever
   the list view shows it. "Distinct in the maintainer's head" does not count.
2. **Same noun, same verb, everywhere.** One term per concept across pages,
   labels, buttons, and docs; pick one of Delete/Remove, one of Note/Comment,
   and use it product-wide. If the save action looks different in two places,
   one of them is wrong. (Impeccable's operate/clarify rules — the sharpest
   external statement of this.)
3. **Say each idea once per surface.** A status or label rendered in several
   slots of the same panel is template wiring, not information.
4. **The inventory is part of the PR.** Every repo keeps `UI-INVENTORY.md`:
   record type → concepts → the one control that edits each → write endpoints.
   Adding a field, control, or editing surface without diffing the inventory
   in the same PR fails review. The inventory is small on purpose — it is a
   table of ownership, not documentation.
5. **Surface briefs.** Each page keeps `ui/surfaces/<route>.md`: one short
   file — intent, archetype (Plan 007), concepts owned, concepts deliberately
   NOT shown. An agent editing a page reads its brief first; a feature that
   contradicts the brief amends the brief in the same PR, never silently.
   (Impeccable's mechanism, adoptable as a pure file convention.)

### `scripts/check_content_model.py` — the advisory detector

Heuristic, stdlib-only, advisory severity: flag ≥2 same-type free-text
controls (`textarea`, text `input`) bound to one record container in a rendered
page; flag duplicate visible labels within a container. This extends the one
external detector aimed at this class (Impeccable's `repeated-container-text`)
from repeated *text* to repeated *controls*. Advisory because IA judgments
need a human — the check's job is to force the conversation the notes fields
never got.

### `skills/patina-ui/` — delivery into agent context

A standard not in context does not exist; every prose convention in this
estate that relied on being remembered has already failed once. The skill
(source-controlled here, installed to `~/.claude/skills/`) triggers on UI work
in family repos and loads: the token contract summary + prefix rule (005), the
component/state rules (006), archetypes + banned defaults with rationale
(007), the content-model rules (this plan), the embarrassment checklist
(populated/empty × dark/light, read the words, zero is neutral), and the
review protocol: **owner review = rendered screenshots + a recommendation +
binary choices; never open-ended taste questions.**

## Work items

- **WI-1 — DONE.** Write `docs/content-model.md` (the five rules, with the
  cert-watch notes case as the worked example — rules without their motivating
  failure get optimized away).
- **WI-2 — DONE.** cert-watch pilot: `UI-INVENTORY.md`. The 2026-08-14 survey data
  is essentially the draft (7 fields, endpoints, surfaces already enumerated).
  Include the latent 8th field (`hosts.expected_issuers`, surfaced nowhere).
- **WI-3 — The notes adjudication (human).** ~~Present both options as
  rendered screenshots.~~ **DECIDED 2026-08-14 (owner, from 3-way render):
  Option 1 — merge to ONE host-scoped notes field.** `certificates.notes`
  migrates (concat) into `hosts.notes` and the column is dropped; the cert
  page gets a single "Notes" panel scoped "operational notes for this host";
  the placeholder stops inviting owner/runbook (structured fields own those);
  certless hosts keep notes (BC-020's need). Rationale: the structured fields
  already own the content cert-notes solicited, host notes must exist
  regardless, and the host/cert scope distinction proved invisible at 1:1.
  Implementation is a cert-watch change (migration + template + endpoint
  removal) — queued, not yet built. Recorded in cert-watch UI-INVENTORY.md.
- **WI-4 — OPEN — Detector.** Build + run advisory in cert-watch CI against
  rendered pages; tune until it flags the (pre-fix) notes case and nothing
  spurious. Not started: `scripts/check_content_model.py` does not exist.
- **WI-5 — OPEN — Author + install the skill.** Trigger on UI-bearing family
  repos; verify it actually loads in a fresh session touching cert-watch
  templates. Not started: `skills/patina-ui/` does not exist.
- **WI-6 — OPEN — Surface briefs for cert-watch's four domains** (Certificates,
  Posture, Activity, Settings) as the worked example other repos copy.

## Acceptance

- cert-watch has an inventory (**met**), four surface briefs (**not met** —
  WI-6), and a recorded notes decision (**met** — WI-3, decided; implementation
  queued); the detector runs advisory in its CI (**not met** — WI-4).
- The skill demonstrably fires on UI work and carries all four layers' rules.
- A test PR adding a duplicate concept control gets caught (by detector or by
  inventory-diff review) — the class of defect that survived Plan 055 can no
  longer land silently.

## If declined

The token, component, and archetype layers still leave the estate blind to
the defect class that motivated this whole review; accretion resumes at the
concept level, one BC-020 at a time.
