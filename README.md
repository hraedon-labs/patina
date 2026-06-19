# patina

The shared visual identity for the instrument-panel tool family — cert-watch,
gpo-lens, and their siblings. patina is the **coherence layer**: a small set of
design tokens, the family typeface, a theme toggle, and a script that vendors
them into each tool. It is intentionally not a component framework.

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

## Scope

**In:** the token contract, the family typeface, the theme toggle, the accent
registry, the vendoring script, and the rationale.

**Out / non-goals:** a component library or class framework (each tool keeps its
own components — for now; see `plans/001`); a build step or bundler; any
JavaScript framework; per-tool layout.

## Adding a new tool

1. Add `accents/<tool>.css` with a distinct, non-status accent (dark + light).
   Record the choice in `docs/token-contract.md`.
2. Run `sync.sh <tool> <its static dir>`.
3. Link `css/tokens.css` and load `theme.js` in the tool's base template; set
   `<html data-theme-key="<tool>-theme">`.
