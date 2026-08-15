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

**Decided 2026-08-14 (plan 004): the "warm & quiet" quad** — dark: sage
`#7fd091` / antique gold `#ce9d44` / terracotta `#cc6050` / steel `#60aeda`;
light: deep inks `#004e19` / `#836101` / `#b64461` / `#25729e`. Chosen from
three constraint-searched candidates rendered on real components (owner +
review concurred). Every value ≥4.5:1 on `--bg` and `--panel` in both themes;
all 6 status pairs ≥8 ΔE under protanopia/deuteranopia/tritanopia simulation
(Machado 2009, severity 1.0), normal-vision ≥15. The previous quad — which
happened to be Tailwind emerald/amber/red-400 — was replaced for its measured
failures (light ok 2.90:1; deutan collapse of ok/warn/crit at ΔE 4.1–5.5),
NOT for its provenance. Two hue choices are physics, not taste: light-theme
warn is golden ochre (sRGB has no dark high-chroma amber at 4.5:1 on warm
paper) and light-theme crit runs crimson (warm-red vs amber is not
protan-separable at this contrast). `scripts/check_contrast.py` gates the
floors in CI; changing these values again requires plan-004-grade CVD
validation, not just the gate.

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
| dossier | plum (registry seal) | `#b07cc6` | `#7a4d8f` |
| sluice | aqua (flow register) | `#5fcde4` | `#2a8ca8` |
| _(default)_ | neutral warm steel | `#b9a98c` | `#6f6552` |

When adding a tool, choose an accent that is (1) not another tool's, (2) not a
status hue, (3) legible on both themes, and record it here and as
`accents/<tool>.css`.

## Tool-local tokens: the prefix rule (Plan 005, 2026-08-14)

Shared tokens are unprefixed and defined only in `tokens.css`. A tool that
needs its own tokens (`--cw-topbar-h`, `--gp-grid-gap`) MUST prefix them with
its 2–3 letter tool prefix, so contract vocabulary and local vocabulary can
never collide, and a consumer can never shadow a contract value (redefining an
unprefixed token in tool CSS is a conformance failure — `check_patina.py`
enforces both directions). If a local token turns out to be generally useful,
promote it into this contract; don't drop the prefix locally.

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
