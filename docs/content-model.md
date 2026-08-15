# patina content-model contract (the concept layer)

Tokens keep the family's colours coherent; patterns and archetypes keep its
shapes coherent. This layer keeps its **meaning** coherent: which concepts a
record exposes, and where each one lives. It exists because nothing else —
not visual regression, not token gates, not lint — can see the defect class
that motivated it: two duplicate controls are perfectly pixel-consistent.

## The worked example (why these rules exist)

cert-watch's certificate page, as shipped through a *dedicated redesign*
(Plan 055), surfaced seven free-text fields from two tables via three editing
surfaces and four write endpoints. Two were near-identical 10,000-character
"notes" textareas — one on the host row, one on the certificate row — whose
placeholder text invited each other's content, plus that of the structured
owner and runbook fields eight lines up. Cause: two features landed two
months apart and nobody reconciled, because no rule existed at the concept
level. The redesign unified *controls* ("one toggle, one chip") and couldn't
touch this, because its rules never named *concepts*. These rules do.

## The rules

1. **One concept, one control.** Each concept a record exposes (ownership,
   procedure notes, tags, …) has exactly one editing control across the whole
   UI. A proposed second free-text field on a record must either merge into
   the existing one or carry a visibly distinct scope — in its label AND
   wherever list views show it. "Distinct in the maintainer's head" does not
   count; if the two labels need a parenthetical to tell apart, they are one
   concept.

2. **Same noun, same verb, everywhere.** One term per concept across pages,
   labels, buttons, docs. Pick one of Delete/Remove, one of Note/Comment, one
   of Host/Server — and use it product-wide. If the save action looks
   different in two places, one of them is wrong.

3. **Say each idea once per surface.** A status or label rendered in several
   slots of the same panel is template wiring, not information. If the
   heading already states it, the body adds something or disappears.

4. **The inventory is part of the PR.** Every UI-bearing repo keeps
   `UI-INVENTORY.md`: record type → concepts → the one control that edits
   each → write endpoints. Adding a field, control, or editing surface
   without diffing the inventory in the same PR fails review. The inventory
   is a table of ownership, not documentation — if it takes more than a page
   per record type, it is doing the wrong job.

5. **Surface briefs.** Each page keeps `ui/surfaces/<route>.md` — a few
   lines: intent, archetype (`archetypes.md`), concepts owned, concepts
   deliberately NOT shown. An agent editing a page reads its brief first. A
   feature that contradicts the brief amends the brief in the same PR, never
   silently. The "NOT shown" line is load-bearing: it is how the next
   feature learns that an omission was a decision.

## Review questions (apply to any accreted page)

- Is this concept already editable somewhere else?
- Do two controls on this page compete for the same operator intent?
- Does any placeholder or help text invite content that another field owns?
- Would a new operator know, without asking, which field a renewal procedure
  goes in?

## Enforcement

- `scripts/check_content_model.py` (advisory): flags ≥2 same-type free-text
  controls bound to one record container in a rendered page, and duplicate
  visible labels within a container. Advisory because IA judgments need a
  human — the check's job is to force the conversation the notes fields
  never got.
- The inventory-diff rule (rule 4) is enforced in review, not code: a PR
  touching templates/routes that doesn't touch `UI-INVENTORY.md` gets asked
  why.
