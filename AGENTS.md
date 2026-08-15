# AGENTS.md — patina

patina is the shared visual identity (design tokens + fonts + theme toggle +
sync script) for the tool family. Read `README.md` for the what/why and
`docs/token-contract.md` for the canonical token list.

## What patina is (and isn't)

- It is a **token contract + shared assets + the conformance gate**, not a
  *packaged* Python project. It does ship Python — `scripts/check_patina.py`,
  `scripts/check_contrast.py`, and the family plumbing checks — but they are
  stdlib-only scripts run directly (and vendored into consumers by `sync.sh`),
  not a library. There is still no `pyproject.toml`, no package, no build step,
  by design. Don't add one to "match the other projects"; the family's
  deterministic-core/collector conventions are for data tools, and most do not
  apply here.
- **It is not *only* tokens any more (amended 2026-08-14, Plan 006, ratified by
  the owner).** patina will also ship a reference component implementation —
  `components.css` (neutral `pt-` prefix) + `macros/ui.j2` — that new tools
  vendor wholesale; existing tools keep their prefixes and adopt
  opportunistically. This reverses the old "intentionally not a component
  framework" charter line: prose describing shapes is a re-implementation task
  for every agent that reads it, and four parallel component layers were the
  measured result. **Ratified, not built** — Plan 006 WI-2/3/4 are open, so
  neither file exists yet; `docs/patterns.md` is still the whole delivery.
- It is consumed **vendored** (copied via `sync.sh`), not installed as a
  dependency. The chosen tradeoff: zero coupling and no install-time wiring, at
  the cost of re-running `sync.sh` to propagate changes.

## Hard rules

- **`tokens.css` is the single source of truth.** Never edit a vendored copy
  inside a consuming tool — edit here and re-run `sync.sh`. Vendored files carry
  a "do not edit" banner.
- **Accent is the only thing a tool overrides.** Everything else (surfaces,
  text, status, type, spacing) is shared verbatim so the family stays coherent.
  Accents are for links/focus/wordmark/active-nav — **never** for status
  (ok/warn/crit have their own tokens).
- **Pure ASCII in `.ps1`/`.css`/`.js` that ships to Windows tools.** The family
  hosts on IIS; PowerShell 5.1 mis-parses non-ASCII (em-dashes, smart quotes)
  in files without a BOM. Use `--` not `—`, `'` not `’`.
- **Fonts are OFL** (see `fonts/LICENSE-IBM-Plex-Mono.txt`); keep that licence
  alongside the woff2 whenever they're copied.
- **No work-domain identifiers** in committed files (family rule). patina holds
  only generic CSS/JS/fonts, so this is easy to keep true — keep it that way.

## Conventions require decisions

Family rule (owner, 2026-08-14): a convention that never went through an
explicit decision — a plan, a recorded rationale — is **not set in stone**,
however old or widespread. Some things become conventions by lack of focus
rather than by choice (the status quad was Tailwind's defaults verbatim for a
year; nobody chose that). When work touches a convention, check whether it was
decided; if it merely accreted, it is revisable, and proposing the
first-principles alternative is in scope. Once decided, record the decision
where the value lives (`docs/token-contract.md`, the relevant plan) so it
stops being revisable by accident in the other direction.

Two guards on the rule itself (from the 2026-08-14 blind review of Plan 007,
where the first draft banned a layout for being an LLM attractor and the
review overturned it):

- **The rule-test.** Every new patina rule must name the actual failure it
  prevents or the operator decision it improves. "A model would produce
  this" is not a failure; a rule that can't pass the test is design-system
  gardening. Provenance is never a defect — if a stock value or a common
  shape is measurably optimal, use it shamelessly and record why.
- **Blind review for identity decisions.** When a rule or grammar is being
  ratified, show an evaluator the rendered options WITHOUT the rationale.
  If the rationale and the pixels disagree, believe the pixels first and
  re-examine the rationale.

## Conventions that DO carry over from the family

- Theme is dark-by-default, driven by `data-theme` on `<html>`, set before paint.
- The family CSP is `script-src 'self'` (no inline JS) — that's why `theme.js`
  is an external file, not an inline `<script>`.
- Keep changes small and legible; match the surrounding token style.

## Changing tokens

A token change ripples to every tool. Prefer additive changes. If you change a
shared value, note it and re-sync each consuming tool deliberately (each tool's
vendored `css/tokens.css` is regenerated, not merged).

## Adoption doctrine (empirical, after four consumers)

Written down 2026-08-15 after cert-watch, gpo-lens, dossier and openbia. Short
on purpose — this is what the adoptions actually taught, not a plan.

1. **An adoption tests both sides.** It is not the standard judging a consumer,
   and it is not legacy consumers being grandfathered. It is a bidirectional
   test that finds the defect on whichever side is wrong. dossier is the clean
   example: patina was wrong about print-context shadowing, patina's checker
   was buggy in two places, patina's facet vocabulary was incomplete — *and*
   dossier turned out to be genuinely wrong about `review_note` versus comment
   `body`.
2. **When conformance pushes toward a worse architecture, investigate the rule
   before changing the consumer.** When a gate systematically rewards
   circumvention, the gate is wrong. The print rule's cheapest compliance route
   was to re-plumb components onto tool-local aliases so they stopped
   referencing contract tokens at all: greener checker, weaker contract.
3. **Every checker false positive becomes a permanent regression fixture**,
   built from the syntax that actually fooled it. See
   `scripts/selftest_patina.py`.
4. **Local needs are legal when explicitly scoped.** Recurrence *within* a
   consumer establishes a local pattern; independent recurrence *across*
   consumers triggers review for promotion — review, not automatic promotion.
   This applies to page archetypes and to rendering contexts alike.
5. **A semantic rule is validated by whether it finds real defects**, not by
   whether consumers can be made green. The content-model rule found dossier's
   duplicated control before anyone knew that defect existed. That is the
   difference between a standard and a bug checklist.

### Two derived rules for the checker

- **The severity of a mechanically enforced rule sets the required confidence
  of its detector.** A cosmetic advisory can tolerate noise. A blocking
  accusation of contract corruption cannot — `TOKEN_DEF_RE` told dossier it had
  shadowed a status colour, on a line that declared nothing, and the implied
  remedy was to damage valid CSS.
- **Do not indefinitely add regex cleverness to emulate CSS grammar.** The
  brace-parity bug is the warning. If the checker needs materially more
  understanding of the grammar than it has now, a real parser is the safer
  answer than another clever pattern.

### Choosing the next consumer

Pick the most **structurally different** remaining tool, not the messiest.
Heterogeneous consumers act as fuzz cases for the design system, and the open
question is which of patina's assumptions are family invariants versus
cert-watch coincidences. cert-watch exposed the danger of deriving structure
from generic archetypes; gpo-lens exposed assumptions about read-only tools,
attestation and relationship-centric pages; dossier exposed rendering-context
assumptions, parser defects and facet vocabulary. Internal completeness is
worth much less right now than the next different consumer.
