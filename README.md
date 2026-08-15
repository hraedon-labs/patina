# patina

The shared visual identity for the instrument-panel tool family — cert-watch,
gpo-lens, and their siblings. patina is the **coherence layer**: a small set of
design tokens, the family typeface, a theme toggle, and a script that vendors
them into each tool — plus, decided 2026-08-14, a **reference component
implementation** that new tools vendor wholesale (see Scope; decided, not yet
built).

## Why it exists

Several local-first infrastructure/security tools were growing their own
look. They should read as one product line — same surfaces, type, spacing, and
status colours — while each keeps a distinct accent. patina makes that contract
explicit and copyable instead of re-derived per tool (which is how drift
starts).

The metaphor: **same metal, different finish.** A warm-charcoal "instrument
panel, not a cold SaaS night theme." cert-watch is the struck bronze of a
certificate seal; gpo-lens is verdigris, the blue-green patina of aged bronze.
Every tool shares the metal (the neutrals, type, spacing, status hues) and
overrides one thing: `--accent`.

## What's in here

| Path | What it is |
|------|------------|
| `tokens.css` | **The contract.** Surfaces, text, status colours, type scale, space scale, radii, fonts, base element styles — as CSS custom properties. Source of truth. |
| `accents/<tool>.css` | One small file per tool that overrides `--accent` (dark + light). `cert-watch` = bronze, `gpo-lens` = verdigris. |
| `theme.js` | Dark/light toggle. Loads in `<head>` before paint; key is per-tool via `data-theme-key`. |
| `fonts/` | IBM Plex Mono (self-hosted woff2, OFL). |
| `sync.sh` | Vendors the above into a tool's static dir. |
| `docs/token-contract.md` | The canonical token list and the rules for using it. |
| `docs/patterns.md` | Component patterns catalog — shared shapes for topbar, tables, pills, etc. |
| `docs/archetypes.md` | Page archetypes (structure tier 2) — how whole screens are laid out, with banned failure modes. |
| `docs/content-model.md` | The concept layer — which concepts a record exposes and where each one lives. |
| `scripts/` | The conformance gate (`check_patina.py`) and the contrast gate (`check_contrast.py`), stdlib-only. |

## How a tool consumes patina

Vendored, not installed. From a patina checkout:

```bash
./sync.sh gpo-lens ../gpo-lens/src/gpo_lens/web/static
```

That writes into the tool's static dir:

- `css/tokens.css` — `tokens.css` + that tool's accent, concatenated. **Vendored;
  do not edit in the tool.** Re-run `sync.sh` to update.
- `theme.js`
- `fonts/`

The tool links `css/tokens.css`, then its **own** component stylesheet (its
`cw-`/`gp-` classes) built on the tokens. patina owns the tokens, fonts, and
toggle; the tool owns its components. *(That last split is what Plan 006
changes for new tools — see Scope. Existing tools keep it.)*

## Scope

**In:** the token contract, the family typeface, the theme toggle, the accent
registry, the vendoring script, the conformance gate (`scripts/check_patina.py`,
`scripts/check_contrast.py`), the structure and content-model docs
(`docs/patterns.md`, `docs/archetypes.md`, `docs/content-model.md`), and the
rationale.

**Also in, decided 2026-08-14 (Plan 006, ratified by the owner):** a **reference
component implementation** — a neutral `pt-`-prefixed `components.css` plus a
Jinja macro library (`macros/ui.j2`), vendored by `sync.sh` alongside the
tokens. New tools adopt it wholesale and write no component CSS of their own.
*Why the reversal of the old "intentionally not a component framework"
position:* that stance was reasoned for human autonomy — each tool's author
keeps freedom at the component layer — but the estate's UIs are written by
agents, and for an agent a prose catalog is a description to re-implement from
scratch per tool. Measured 2026-08-14: four parallel component layers
implementing the same 14 shapes with drifting details. Full rationale in
`docs/token-contract.md` and `plans/006`.

**Status of that decision: ratified, not built.** Neither `components.css` nor
`macros/ui.j2` exists yet — Plan 006 WI-2 (extract), WI-3 (prove on a thin
consumer), WI-4 (document) are open. Until they ship, `docs/patterns.md` is the
whole delivery of the shared shapes and every tool still implements them itself.

**Out / non-goals:** a *mandatory* class framework — existing tools keep their
own prefixes (`cw-`, `gp-`, `ds-`) and adopt the reference implementation
opportunistically, e.g. when a page is rebuilt anyway (retrofit is permitted
where the initial pain is worth the downstream simplification, but opportunistic
is the default; assess per tool when its UI is next touched); a build step or
bundler; any JavaScript framework; per-tool layout.

## Adding a new tool

1. Add `accents/<tool>.css` with a distinct, non-status accent (dark + light).
   Record the choice in `docs/token-contract.md`.
2. Run `sync.sh <tool> <its static dir>`.
3. Link `css/tokens.css` and load `theme.js` in the tool's base template; set
   `<html data-theme-key="<tool>-theme">`.
