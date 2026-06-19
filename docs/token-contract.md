# The patina token contract

This is the canonical list of design tokens every family tool shares, the rules
for using them, and the per-tool accent registry. It is the design spine of
patina: change it deliberately, because a change here ripples to every tool.

## Principle

Coherence comes from **shared token names and values**, not shared component
classes. Two tools can have entirely different components and still read as one
product line if they draw every colour, size, and space from these tokens.
A tool that hardcodes a hex value or a pixel size outside this contract is where
drift begins.

## Tokens

All are CSS custom properties on `:root`, themed via `:root[data-theme="…"]`.

### Surfaces (warm charcoal dark / warm paper light)
`--bg` `--bg-soft` `--panel` `--panel-2` `--panel-3` `--inset` `--border`
`--border-2` — a low-to-high elevation ramp. Backgrounds and hairlines only.

### Text
`--text` (primary) `--text-2` (secondary) `--text-3` (muted/labels).

### Accent (the one per-tool override)
`--accent` `--accent-2` `--accent-soft` (tint bg) `--accent-line` (tinted
border). Links, focus rings, wordmark, active nav. **Never** status.

### Status (shared verbatim — do not re-tint per tool)
`--ok` `--warn` `--crit` `--info`, each with a matching `*-soft` tint.

### Type
Faces: `--font-sans` (system UI), `--font-mono` (IBM Plex Mono — figures,
labels, identifiers). Scale: `--fs-xs` 11 · `--fs-sm` 12.5 · `--fs-base` 13.5 ·
`--fs-md` 15 · `--fs-lg` 18 · `--fs-xl` 22 · `--fs-2xl` 30 (px). Use
`.tnum` for tabular figures.

### Space / shape
`--space-1`…`--space-6` (4px base). `--radius-sm` `--radius` `--radius-md`
`--radius-lg`. `--shadow`, `--row-hover`.

### Base helpers shipped in `tokens.css`
`.mono` `.tnum` `.muted`, link + `:focus-visible` styling, scrollbar, and a
`prefers-reduced-motion` reset. Everything else is the tool's own components.

## Accent registry

Each tool picks one distinct, non-status accent. "Same metal, different finish."

| Tool | Finish | Dark | Light |
|------|--------|------|-------|
| cert-watch | struck bronze (certificate seal) | `#c9a25a` | `#8a6a28` |
| gpo-lens | verdigris (patinated bronze) | `#5fb3a3` | `#2c7d6e` |
| _(default)_ | neutral warm steel | `#b9a98c` | `#6f6552` |

When adding a tool, choose an accent that is (1) not another tool's, (2) not a
status hue, (3) legible on both themes, and record it here and as
`accents/<tool>.css`.

## Shared component patterns

Each tool keeps its own component CSS with its own class prefix (cert-watch
`cw-`, gpo-lens `gp-`). Tokens are shared; component classes are not. A future
step could extract the genuinely common components into a neutral-prefixed
`components.css` that patina also vendors — that decision is deferred to
`plans/001`.

In the meantime, **`patterns.md`** catalogs the shared component shapes
(topbar, stat strip, table, pill, chip, callout, panel, empty state, etc.)
with canonical structure, token usage, and naming conventions. New tools should
follow those patterns so the family stays visually coherent even without a
shared stylesheet. The rule stands: **share tokens and shapes, not class
names.**
