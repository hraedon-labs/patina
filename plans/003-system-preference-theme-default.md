# Plan 003 — system-preference theme default

**Status:** Draft — proposed 2026-07-29. **Evidence arrived 2026-08-15 (openbia
adoption):** this is no longer a preference question. `theme.js:14` is
`localStorage.getItem(KEY) || "dark"`, applied unconditionally, and
`prefers-color-scheme` is consulted nowhere in patina. There is **no
consumer-settable default**, so a light-first tool cannot express itself
through the shared bootstrap at all — it must bypass it. openbia did: synced
`--no-theme` and pinned `<html data-theme="light">` server-side, **losing
automatic dark mode it previously had**. openbia is a stakeholder-intake and
management-report tool, not a console; dark-by-default is a cert-watch
inheritance, and the mechanism offers no way to say so. Note openbia ships no
JavaScript at all (offline-bundle requirement), so any fix must have a JS-free
path — a cookie set by a plain `GET /theme/{dark,light}` link qualifies, and is
incidental presentation state rather than domain state. **Human decision required — family
identity call.** Dark-by-default is currently a stated family convention
(AGENTS.md: "Theme is dark-by-default"); this plan proposes changing the
*initial* default to follow the user's OS preference while keeping dark as the
design-reference theme. Owner: patina. File affected: `theme.js` (shared,
vendored per-tool by `sync.sh`).

## Problem

Every family tool first paints dark, regardless of the user's environment
preference. In the office/regulated settings several of these tools serve
(cert-watch, dossier), light is the primary reading environment and print is a
real journey; forcing dark on first visit costs every new user one manual
toggle and reads as a preference the tool made for them. dossier's visual-pass
review (2026-07-29) raised this as the one foundational default worth revisiting.

## Proposal

Change only the *initial* value — nothing about the toggle, persistence, or
pre-paint wiring:

```js
// today
function get() {
  try { return localStorage.getItem(KEY) || "dark"; } catch (e) { return "dark"; }
}

// proposed
function get() {
  try {
    var stored = localStorage.getItem(KEY);
    if (stored) return stored;
  } catch (e) {}
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
}
```

Properties preserved:

- synchronous, external-file, pre-paint application (CSP `script-src 'self'`
  untouched; no inline JS);
- an explicit user toggle always wins forever after (localStorage unchanged);
- dark remains the family reference theme for screenshots/marketing;
- per-tool scoping via `data-theme-key` untouched.

## Escape hatch (recommended)

Add an optional per-tool pin so a tool that must stay dark-first (e.g. a kiosk
panel) can declare it without forking the file:

```html
<html data-theme-key="cw-theme" data-theme-default="dark">
```

When `data-theme-default` is present it is used as the no-preference fallback
instead of the media query. Pure ASCII only in `theme.js` (PowerShell 5.1
parsing rule).

## Work items

- **WI-1 — Decision (human).** Adopt system-following default, or keep
  dark-first. This is a look-and-feel identity decision across every tool —
  not an agent call.
- **WI-2 — Implement + unit-check.** Apply the diff (with or without the pin
  hatch), verify no flash either order, verify stored preference still wins,
  verify a browser reporting neither preference still gets dark.
- **WI-3 — Re-sync the family.** `sync.sh` each consumer; verifier per tool:
  clear-site-data visit in both OS modes paints the expected theme.

## Acceptance

- First visit follows `prefers-color-scheme`; explicit toggle overrides; stored
  values from current deployments keep working (no migration, same key).
- Family screenshots/docs state which theme is the reference render.

## If declined

dossier can achieve its own system-following default without touching patina:
ship a `dossier`-scoped variant of the bootstrap (the deviation cost is one
small vendored-asset drift, recorded in the dossier repo). The family keeps
dark-first everywhere else.
