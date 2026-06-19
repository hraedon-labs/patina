# patina patterns catalog

A reference for the shared component shapes across the tool family. Tokens
(`tokens.css`) give every tool the same colour, type, and space palette. This
catalog goes one step further: it shows the **shapes** that tools reuse — the
topbar, stat strip, table, pill, and so on — so a new tool can build the same
instrument-panel feel without reverse-engineering an existing one.

Each tool owns its own component CSS with its own prefix (`cw-`, `gp-`, etc.).
patina does not ship component classes. The patterns below describe **what to
build and how to name it**, not a shared stylesheet.

## Naming convention

| Piece | Rule |
|-------|------|
| Prefix | 2–3 letters + hyphen: `cw-`, `gp-`, `ad-` |
| BEM style | Flat hyphenated names (`cw-stat-val`), not strict BEM |
| Modifiers | Bare class additions (`.active`, `.primary`, `.ok`) or `--` suffixes for layout variants |
| Tone/variant | Domain words (`.expired`, `.critical`, `.healthy`) mapped to status tokens |
| Utilities | Optional — cert-watch has a rich utility layer; gpo-lens keeps it lean |

## 1 — App shell

A full-viewport flex column: fixed topbar at the top, scrollable content below.

```
.<prefix>-app          flex-direction: column; height/min-height: 100vh
  .<prefix>-topbar     fixed top bar (see §2)
  .<prefix>-page       flex: 1; overflow: auto — the scrollable region
    .<prefix>-wrap     max-width: 1080px; margin: auto; padding → page content
```

Tokens: `--bg` on the app, `--panel` on the topbar, `--border` on topbar
bottom edge.

## 2 — Topbar + navigation

A flex row containing the brand, nav links, spacer, and action buttons.

```
.<prefix>-topbar       display: flex; align-items: center; height: 58px;
                        background: var(--panel); border-bottom: 1px solid var(--border)

  .<prefix>-wordmark   flex-shrink: 0; display: flex; align-items: center; gap: 8px
    .<prefix>-mark     accent-coloured icon or initial
    .<prefix>-name     font-family: var(--font-mono); font-weight: 600
    .<prefix>-ver      font-size: var(--fs-xs); color: var(--text-3)

  .<prefix>-nav        display: flex; gap: 2px; margin-left: 24px
    a                  padding: 6px 12px; border-radius: var(--radius-sm)
    a:hover            background: var(--panel-2)
    a.active           background: var(--panel-3); color: var(--accent)

  .<prefix>-spacer     flex: 1

  .<prefix>-iconbtn    width: 36px; height: 36px; display: flex;
                        align-items: center; justify-content: center;
                        border-radius: var(--radius-sm); cursor: pointer
                        background: transparent; border: none; color: var(--text-2)
  .<prefix>-iconbtn:hover  background: var(--panel-2)
```

Tokens: `--panel`, `--panel-2`, `--panel-3`, `--border`, `--text-2`, `--accent`,
`--radius-sm`, `--font-mono`.

## 3 — Buttons

```
.<prefix>-btn          display: inline-flex; align-items: center; gap: 6px;
                        font-size: var(--fs-sm); padding: 6px 14px;
                        border: 1px solid var(--border-2); border-radius: var(--radius);
                        background: var(--panel-2); color: var(--text);
                        cursor: pointer
.<prefix>-btn:hover    background: var(--panel-3)
.<prefix>-btn.primary  background: var(--btn-strong-bg); color: var(--btn-strong-text);
                        border-color: transparent
.<prefix>-btn:disabled opacity: 0.5; cursor: not-allowed
```

Tokens: `--panel-2`, `--panel-3`, `--border-2`, `--text`, `--radius`,
`--btn-strong-bg`, `--btn-strong-text`, `--fs-sm`.

## 4 — Inputs and fields

```
.<prefix>-field        margin-bottom: var(--space-3)
.<prefix>-label        display: block; font-size: var(--fs-sm);
                        color: var(--text-2); margin-bottom: 4px;
                        font-family: var(--font-mono)
.<prefix>-input,
.<prefix>-select       width: 100%; padding: 7px 10px;
                        background: var(--inset); border: 1px solid var(--border);
                        border-radius: var(--radius); color: var(--text);
                        font-size: var(--fs-sm)
.<prefix>-input:focus  border-color: var(--accent);
                        box-shadow: 0 0 0 2px var(--accent-soft);
                        outline: none
```

Tokens: `--inset`, `--border`, `--accent`, `--accent-soft`, `--text`, `--text-2`,
`--radius`, `--fs-sm`, `--space-3`, `--font-mono`.

## 5 — Panel / card

```
.<prefix>-panel        background: var(--panel); border: 1px solid var(--border);
                        border-radius: var(--radius-lg)
.<prefix>-panel.pad    padding: 16px 18px
```

Tokens: `--panel`, `--border`, `--radius-lg`.

## 6 — Stat strip

A grid of metric cards with hairline dividers — the dashboard "instrument
panel" feel.

```
.<prefix>-stats        display: grid; grid-template-columns: repeat(4, 1fr);
                        border: 1px solid var(--border); border-radius: var(--radius-lg);
                        overflow: hidden

.<prefix>-stat         padding: 14px 16px;
                        border-left: 1px solid var(--border)
.<prefix>-stat:first-child  border-left: none

.<prefix>-stat-label   font-family: var(--font-mono); font-size: 10.5px;
                        text-transform: uppercase; letter-spacing: 0.05em;
                        color: var(--text-3); margin-bottom: 4px
.<prefix>-stat-val     font-family: var(--font-mono); font-size: 24px;
                        font-weight: 600; font-variant-numeric: tabular-nums;
                        color: var(--text)
.<prefix>-stat-sub     font-size: var(--fs-xs); color: var(--text-3); margin-top: 2px
```

Tokens: `--border`, `--radius-lg`, `--text`, `--text-3`, `--font-mono`, `--fs-xs`.

## 7 — Pill (status indicator)

An inline-flex dot + label for status. No background, no border.

```
.<prefix>-pill         display: inline-flex; align-items: center; gap: 6px;
                        font-size: var(--fs-sm)
.<prefix>-pill .dot    width: 7px; height: 7px; border-radius: 50%;
                        flex-shrink: 0
```

Tone classes set `.dot` background and text color using status tokens:
`.critical` → `--crit`, `.warning` → `--warn`, `.healthy`/`.ok` → `--ok`,
`.muted`/`.neutral` → `--text-3`. Domain-specific names (`.expired`, `.high`,
`.low`) are fine — map them to the same status tokens.

Tokens: `--ok`, `--warn`, `--crit`, `--text-3`, `--fs-sm`.

## 8 — Chip (metadata tag)

An inline-flex bordered tag for metadata. Mono font.

```
.<prefix>-chip         display: inline-flex; align-items: center;
                        font-family: var(--font-mono); font-size: var(--fs-xs);
                        padding: 2px 8px; border: 1px solid var(--border-2);
                        border-radius: 4px; color: var(--text-2)
```

Tone classes recolor border + text: `.ok` → `--ok`, `.warn` → `--warn`,
`.crit` → `--crit`, `.accent` → `--accent`, `.muted` → `--text-3`.

Tokens: `--border-2`, `--text-2`, `--text-3`, `--ok`, `--warn`, `--crit`,
`--accent`, `--font-mono`, `--fs-xs`.

## 9 — Table

Mono uppercase headers, bordered rows, row-hover highlight.

```
.<prefix>-table-wrap   border: 1px solid var(--border); border-radius: var(--radius-lg);
                        overflow: hidden
.<prefix>-table        width: 100%; border-collapse: collapse
.<prefix>-table th     font-family: var(--font-mono); font-size: 10.5px;
                        text-transform: uppercase; letter-spacing: 0.05em;
                        color: var(--text-3); text-align: left;
                        padding: 10px 14px; border-bottom: 1px solid var(--border)
.<prefix>-table td     padding: 10px 14px; border-bottom: 1px solid var(--border);
                        font-size: var(--fs-sm)
.<prefix>-table tbody tr:hover  background: var(--row-hover)
```

Tokens: `--border`, `--radius-lg`, `--text-3`, `--row-hover`, `--font-mono`,
`--fs-sm`.

## 10 — Empty state

Centred placeholder when a view has no data.

```
.<prefix>-empty        text-align: center; padding: 48px 24px; color: var(--text-3)
.<prefix>-empty .ico   width: 48px; height: 48px; margin: 0 auto 12px;
                        border-radius: 50%; display: flex; align-items: center;
                        justify-content: center; background: var(--panel-2)
.<prefix>-empty .title font-size: var(--fs-md); font-weight: 600;
                        color: var(--text); margin-bottom: 4px
.<prefix>-empty .sub   font-size: var(--fs-sm); color: var(--text-3)
```

Tokens: `--panel-2`, `--text`, `--text-3`, `--fs-md`, `--fs-sm`.

## 11 — Callout / alert

A bordered block with optional icon for status messages.

```
.<prefix>-callout      display: flex; gap: 10px; padding: 12px 14px;
                        border: 1px solid var(--border); border-radius: var(--radius);
                        background: var(--panel-2)
.<prefix>-callout.warn border-color: var(--warn); background: var(--warn-soft)
.<prefix>-callout.crit border-color: var(--crit); background: var(--crit-soft)
.<prefix>-callout.info border-color: var(--info); background: var(--info-soft)
```

Tokens: `--panel-2`, `--border`, `--radius`, `--warn`, `--crit`, `--info`,
`--warn-soft`, `--crit-soft`, `--info-soft`.

## 12 — Drop zone

Dashed-border target for file drops.

```
.<prefix>-drop         border: 2px dashed var(--border-2); border-radius: var(--radius-lg);
                        padding: 32px; text-align: center; color: var(--text-3);
                        background: var(--inset)
.<prefix>-drop:hover   border-color: var(--accent); background: var(--accent-soft)
```

Tokens: `--border-2`, `--accent`, `--accent-soft`, `--inset`, `--text-3`,
`--radius-lg`.

## 13 — Breadcrumb

```
.<prefix>-breadcrumb   display: flex; align-items: center; gap: 6px;
                        font-size: var(--fs-sm); color: var(--text-3)
.<prefix>-breadcrumb a color: var(--text-2)
.<prefix>-breadcrumb a:hover  color: var(--accent)
.<prefix>-breadcrumb .sep    color: var(--text-3); opacity: 0.5
```

Tokens: `--text-2`, `--text-3`, `--accent`, `--fs-sm`.

## 14 — Chain / precedence

A vertical ladder of nodes with a connecting spine — used for certificate trust
chains and GPO precedence.

```
.<prefix>-chain        position: relative; padding-left: 28px
.<prefix>-chain .spine position: absolute; left: 9px; top: 0; bottom: 0;
                        width: 2px; background: var(--border)
.<prefix>-chain .node  position: relative; padding: 12px 0
.<prefix>-chain .node::before  content: ""; position: absolute; left: -24px;
                        top: 16px; width: 10px; height: 10px;
                        border-radius: 50%; border: 2px solid var(--accent);
                        background: var(--bg)
```

Tokens: `--border`, `--accent`, `--bg`.

---

## Adding a new tool

1. Choose a 2–3 letter prefix (`ad-`, `kp-`, etc.).
2. Start with the app shell (§1), topbar (§2), and buttons (§3) — they give
   you a recognisably "family" frame with minimal CSS.
3. Add stat strips, tables, pills, and chips as the tool's views need them.
4. Use the tokens from `token-contract.md` for every colour, size, and space —
   never hardcode a hex or pixel value.
5. Domain-specific patterns (posture grids, grade badges) are fine — just build
   them on the same tokens.
