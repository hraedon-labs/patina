# patina

The shared visual identity for the instrument-panel tool family — cert-watch,
gpo-lens, dossier, sluice, and touchstone. patina is the **coherence layer**: a
small set of design tokens, the family typeface, a theme toggle, and a script
that vendors them into each tool. It is intentionally not a component framework.

## Why it exists

Several local-first infrastructure/security tools were growing their own
look. They should read as one product line — same surfaces, type, spacing, and
status colours — while each keeps a distinct accent. patina makes that contract
explicit and copyable instead of re-derived per tool (which is how drift
starts).

The metaphor: **same metal, different finish.** A warm-charcoal "instrument
panel, not a cold SaaS night theme." The finishes are cert-watch's struck bronze
(certificate seal, dark `#c9a25a`, light `#8a6a28`); gpo-lens's verdigris
(patinated bronze, dark `#5fb3a3`, light `#2c7d6e`); dossier's plum (registry
seal, dark `#b07cc6`, light `#7a4d8f`); sluice's aqua (flow/water register, dark
`#5fcde4`, light `#2a8ca8`); and touchstone's cupric (copper salts, dark
`#86c05a`, light `#4a7a24`). Every tool shares the metal (the neutrals, type,
spacing, status hues) and overrides one thing: `--accent`.

## What's in here

| Path | What it is |
|------|------------|
| `tokens.css` | **The contract.** Surfaces, text, status colours, type scale, space scale, radii, fonts, base element styles — as CSS custom properties. Source of truth. |
| `accents/<tool>.css` | One small file per tool that overrides `--accent` (dark + light): `cert-watch` = struck bronze, `gpo-lens` = verdigris, `dossier` = plum, `sluice` = aqua, `touchstone` = cupric. |
| `theme.js` | Dark/light toggle. Loads in `<head>` before paint; key is per-tool via `data-theme-key`. |
| `fonts/` | IBM Plex Mono (self-hosted woff2, OFL). |
| `sync.sh` | Vendors the above into a tool's static dir. |
| `docs/token-contract.md` | The canonical token list and the rules for using it. |
| `docs/patterns.md` | Component patterns catalog — shared shapes for topbar, tables, pills, etc. |

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
toggle; the tool owns its components.

The toggle restores only the exact saved values `dark` and `light`. Missing,
invalid, or unavailable local storage falls back to dark before first paint.
Loading the theme leaves storage untouched; an explicit toggle saves the new
preference under the tool's `data-theme-key` (or `patina-theme` by default).

## Scope

**In:** the token contract, the family typeface, the theme toggle, the accent
registry, the vendoring script, and the rationale.

**Out / non-goals:** a component library or class framework (each tool keeps its
own components — for now; see `plans/001`); a build step or bundler; any
JavaScript framework; per-tool layout.

## Tests

Run `node scripts/test-theme.js` for the theme toggle and `scripts/test-sync.sh`
for vendoring.

## Adding a new tool

1. Add `accents/<tool>.css` with a distinct, non-status accent (dark + light).
   Record the choice in `docs/token-contract.md`.
2. Run `sync.sh <tool> <its static dir>`.
3. Link `css/tokens.css` and load `theme.js` in the tool's base template; set
   `<html data-theme-key="<tool>-theme">`.
