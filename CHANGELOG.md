# patina changelog

patina is consumed by **vendoring**, so a consumer chooses when to take a new
version. That only works if a consumer can tell, without reading the diff, what
taking it will cost them. Every release therefore carries impact metadata
alongside its version.

## What the version number means

Semver here answers **consumer compatibility**, not visual magnitude:

- **major** — contract-breaking; the consumer must intervene. A token removed or
  renamed, a change to the vendor format or declaration schema, changed required
  semantics.
- **minor** — backward-compatible addition or an intentional family visual
  change. New tokens, palette values, new components, new advisory rules.
- **patch** — corrections that should not intentionally change consumer
  rendering or require adoption work.

**A palette change is minor, not major.** It invalidates visual baselines, but
it breaks no contract and requires no consumer code change. Teaching the estate
that every rendered change is "breaking" would make the version number useless
for the thing it is good at. What a consumer actually needs to know — will my
screenshots change, must a human look, do I have to edit code — is impact
metadata, and it is recorded per release:

- `visual-change:` intentional change to rendered output.
- `baseline-review:` a human must look at the rendered result before adopting.
- `consumer-code-change:` the consumer must edit code, not just re-sync.

If this ever needs to be more formal than a changelog block, a visual epoch
counter is the obvious next step. It does not need to be yet.

---

## 0.6.0 — 2026-10-02

```
visual-change: opt-in pt- reference components; existing component layers stay consumer-owned
baseline-review: yes, when first adopting the reference implementation
consumer-code-change: opt-in sync/checker flags, stylesheet link and macro imports
```

Plan 006's reference implementation now ships: the 14 catalog shapes in
`components.css`, Jinja macros in `macros/ui.j2`, applicable state sets and a
synthetic inventory example. Form validation reserves an error line and keeps
control heights/border widths stable. Collection states explain empty,
loading and unavailable data; zero and unknown values retain neutral styling.

`sync.sh --components <templates-dir>` delivers ownership-stamped components,
preflights collisions and preserves consumer tails byte-for-byte. `--adopt`
backs up hand-written destinations before replacement. The gate compares
component files against their own recorded source revisions; `.j2` templates
join normal colour/class checks. Default sync does not adopt a component layer.
The planned live agent-notes adoption remains open.

The shared theme normalizes saved preferences, labels the next action and
follows same-key storage changes across tabs. Theme conformance now compares
the vendored file with its recorded Git revision and reports newer source as
an optional upgrade. Dark-first behavior and token values are unchanged.

## 0.5.0 — 2026-08-15

```
visual-change:        yes
baseline-review:      required
consumer-code-change:  no
```

The first versioned release. Everything before this was unversioned (no tags,
six commits on `main`); consumers vendored by revision alone.

**Status palette rebuilt — "warm & quiet" (Plan 004).** The previous quad
happened to be Tailwind `emerald`/`amber`/`red-400` verbatim and was replaced
for measured failures, not for its provenance: light `--ok` sat at 2.90:1, and
`ok`/`warn`/`crit` collapsed to ΔE 4.1–5.5 under deuteranopia. Adopting this
changes every status colour a consumer renders — hence `baseline-review:
required`. No token was added, removed or renamed, so no code changes.

**Conformance gate hardened (Plan 005).** `sync.sh` now fails closed on
malformed or absent vendor markers instead of silently overwriting a
consumer's `tokens.css`; `--adopt` is the way through and takes a backup
first. `check_patina.py` gained `--upstream` (drift measured against the
revision a copy is stamped with, with a newer upstream reported as an
available upgrade rather than a failure), checks the consumer region below
`patina:end`, refuses a validly-stamped empty block, ratchets colour literals
by fingerprint rather than by count, requires a reason on `patina-allow`, and
self-verifies its own vendored bytes. `check_contrast.py` fails closed on any
value it cannot score.

**patina runs its own gates.** `design-gates.yml` runs the contrast gate, a
self-test that replays every known bypass and fails if any stops being
refused, and a vendor-then-check round trip. Previously neither script ran
anywhere while the docs claimed both were enforced in CI.

**Adoption declaration (`patina.toml`).** Consumers declare which conformance
facets they claim and by what mechanism. Consumer-owned: `sync.sh` never
writes or rewrites it. See `docs/adoption.md`.

**Docs.** `archetypes.md` and `content-model.md` added; Plan 006's reversal on
shared components recorded; plan records reconciled with what actually shipped.

### Adopting this release

Re-run `sync.sh`, then look at your rendered status colours before merging.
Existing consumers on the old quad are not broken — they are behind, and
`check_patina.py --upstream` will say so as a note rather than a failure.
