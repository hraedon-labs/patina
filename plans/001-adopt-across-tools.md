# Plan 001 — adopt patina across the family

**Goal:** make patina the real source of the family's tokens — cert-watch and
gpo-lens consume it via `sync.sh` instead of each carrying a hand-maintained
copy — and decide the shared-component question.

Status: charter / not started. patina ships the assets + `sync.sh`; no tool
consumes it yet (both still carry their own `tokens.css`).

## Work items

### WI-1 — Vendor patina into gpo-lens
gpo-lens currently has a single `static/css/tokens.css` containing both the
shared tokens **and** its `gp-` components (precedence chain, posture grid, drop
zone, error page, etc.).
- Split it: shared tokens move out; `gp-` components become
  `static/css/components.css`.
- `sync.sh gpo-lens <static>` writes the vendored `css/tokens.css`.
- base.html links `css/tokens.css` then `css/components.css`; set
  `data-theme-key="gpol-theme"`; replace gpo-lens's own `theme.js` with the
  vendored one.
- Verify the UI is pixel-unchanged (it should be — same values), locally and on
  the IIS deployment (mvmcitest01:8443).

### WI-2 — Vendor patina into cert-watch
cert-watch's `tokens.css` is larger (more components) and uses `cw-`. Same split:
shared tokens → patina-vendored; `cw-` components stay in cert-watch. Reconcile
any token drift between cert-watch's current values and patina's (patina was
seeded from these, so differences should be nil — confirm).

### WI-3 — Decide the shared-component strategy
Either keep components per-tool (status quo, tokens-only sharing) or extract a
neutral-prefixed `components.css` into patina and migrate both tools' templates.
Decision + rationale recorded in `docs/token-contract.md` ("Open question").

### WI-4 — Seed adcs-lens
adcs-lens has no web UI yet. When it gains one, it adopts patina from day one:
add `accents/adcs-lens.css`, run `sync.sh`. No retrofit needed.

## Acceptance
- At least one tool (gpo-lens) builds its UI from a `sync.sh`-vendored
  `tokens.css` with no visual regression.
- `docs/token-contract.md` records the shared-component decision.
- A token change in patina, re-synced, demonstrably propagates to the tool.
