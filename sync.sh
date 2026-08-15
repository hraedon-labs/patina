#!/usr/bin/env bash
# patina/sync.sh — vendor the shared design tokens into a consuming tool.
#
# Usage:
#   ./sync.sh [--no-theme] [--adopt] <accent> <target-static-dir> [checks-dir]
#
#   <accent>             name of an accents/<accent>.css file (e.g. gpo-lens)
#   <target-static-dir>  the tool's static root (must contain, or will get,
#                        a css/ subdir; fonts/ and theme.js land alongside)
#   [checks-dir]         where patina-check.py goes (default: the static root;
#                        pass the tool's tests/ dir to keep it out of the
#                        webroot)
#
#   --no-theme  the tool owns its theme bootstrap (e.g. a CSP-nonced inline
#               script, as cert-watch does); don't vendor theme.js. Pair with
#               check_patina.py's --no-theme.
#   --adopt     permit the FIRST sync into a tool that already has its own
#               css/tokens.css, or repair malformed markers. The existing file
#               is backed up to css/tokens.css.pre-patina-<timestamp> first.
#               Without this flag, sync refuses rather than overwrite.
#
# Example (from a patina checkout):
#   ./sync.sh gpo-lens   ../gpo-lens/src/gpo_lens/web/static
#   ./sync.sh --no-theme cert-watch ../cert-watch/src/cert_watch/static ../cert-watch/tests
#
# What it writes into <target-static-dir>:
#   css/tokens.css   = tokens.css + accents/<accent>.css (concatenated; the
#                      accent block overrides --accent). This file is VENDORED —
#                      do not edit it in the tool; edit patina and re-sync.
#                      The patina-owned content is wrapped in
#                      /* patina:begin <rev> sha256:<hash> */ ... /* patina:end */
#                      delimiters. A consumer MAY append its own CSS below the
#                      end marker; editing inside the block fails check_patina.py.
#                      The appended tail is preserved across re-syncs AND is
#                      checked like any other tool CSS — it is not a bypass.
#   theme.js         = the shared theme toggle (first line carries a
#                      // patina:sha256 stamp over the rest of the file);
#                      omitted with --no-theme
#   fonts/           = IBM Plex Mono woff2 + OFL licence
#   patina-check.py  = the conformance checker (Plan 005), stamped with a
#                      # patina:sha256 line so a consumer cannot quietly weaken
#                      the gate. Consumers run it in CI.
#
# The tool keeps its OWN component CSS (its cw-/gp- classes) in a separate file
# and links it after tokens.css. patina owns only the token contract + fonts +
# theme toggle.
#
# NOTE ON WHAT THE STAMP PROVES: the block hash lives next to the block, so on
# its own it proves integrity, not currency. For real drift detection the
# consumer's CI must run check_patina.py --upstream <patina-checkout>.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

want_theme=1
adopt=0
docs_dir=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --no-theme) want_theme=0; shift ;;
    --adopt)    adopt=1; shift ;;
    --docs)     docs_dir="${2:-}"; [ -n "$docs_dir" ] || { echo "error: --docs needs a directory" >&2; exit 2; }; shift 2 ;;
    -h|--help)  usage ;;
    --*)        echo "error: unknown flag: $1" >&2; exit 2 ;;
    *)          break ;;
  esac
done

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  usage
fi

accent="$1"
target="$2"
checks_dir="${3:-$target}"
accent_file="$here/accents/$accent.css"

if [ ! -f "$accent_file" ]; then
  echo "error: no accent file at $accent_file" >&2
  echo "available accents:" >&2
  ls "$here/accents" | sed 's/\.css$//;s/^/  /' >&2
  exit 1
fi
if [ ! -d "$target" ]; then
  echo "error: target dir does not exist: $target" >&2
  exit 1
fi

out="$target/css/tokens.css"

# ---------------------------------------------------------------------------
# Marker validation — FAIL CLOSED.
#
# The tail-preservation step below copies everything after /* patina:end */.
# If that marker is missing or duplicated, a naive run silently replaces the
# consumer's file with the vendored block and exits 0. That is the most likely
# first-run scenario (a tool that already hand-maintains tokens.css), so it
# must refuse rather than destroy. Every ambiguous shape is a stop.
# ---------------------------------------------------------------------------
# --adopt promises "the current file is backed up first", but only ever looked
# at $out. A greenfield consumer keeps its stylesheet somewhere else entirely
# (openbia's was static/openbia.css), so --adopt was accepted, did nothing, and
# said nothing -- the flag's guarantee silently not applying to the shape it
# exists to serve. Nothing was lost, but the operator was not told that.
if [ "$adopt" -eq 1 ] && [ ! -f "$out" ]; then
  echo "note: --adopt: no file at $out, so nothing was backed up." >&2
  echo "      If this tool's stylesheet lives elsewhere, it is untouched and" >&2
  echo "      still linked by your templates -- retire it deliberately." >&2
fi

if [ -f "$out" ]; then
  n_begin="$(grep -c '^/\* patina:begin .* \*/$' "$out" || true)"
  n_end="$(grep -c '^/\* patina:end \*/$' "$out" || true)"
  problem=""
  if [ "$n_begin" -eq 0 ] && [ "$n_end" -eq 0 ]; then
    problem="it has no patina markers (hand-maintained or legacy vendored copy)"
  elif [ "$n_begin" -ne 1 ] || [ "$n_end" -ne 1 ]; then
    problem="its markers are malformed ($n_begin begin, $n_end end; expected one of each)"
  elif [ "$(grep -n '^/\* patina:end \*/$' "$out" | cut -d: -f1)" -lt \
         "$(grep -n '^/\* patina:begin .* \*/$' "$out" | cut -d: -f1)" ]; then
    problem="patina:end appears before patina:begin"
  fi

  if [ -n "$problem" ]; then
    if [ "$adopt" -eq 0 ]; then
      cat >&2 <<EOF
error: refusing to overwrite $out
       because $problem.

       Everything below /* patina:end */ is preserved across a sync; without a
       well-formed marker pair there is no way to tell your CSS from patina's,
       and a plain overwrite would discard it silently.

       If this file is yours and you want to adopt patina, re-run with --adopt
       (the current file is backed up first). Otherwise fix the markers by hand.
EOF
      exit 1
    fi
    backup="$out.pre-patina-$(date +%Y%m%d%H%M%S)"
    cp "$out" "$backup"
    echo "note: --adopt: backed up existing tokens.css -> $backup" >&2
    rm -f "$out"
  fi
fi

mkdir -p "$target/css" "$target/fonts" "$checks_dir"

rev="$(git -C "$here" rev-parse --short HEAD 2>/dev/null || echo unknown)"

# Assemble the patina-owned block first so the stamp hashes exactly the bytes
# that land between the delimiters.
block="$(mktemp)"
tail_tmp="$(mktemp)"
trap 'rm -f "$block" "$tail_tmp"' EXIT
{
  cat "$here/tokens.css"
  echo ""
  cat "$accent_file"
} > "$block"
block_hash="$(sha256sum "$block" | cut -d' ' -f1)"

# A consumer may keep its own CSS below the end marker; preserve that tail
# across re-syncs so updating patina never eats tool-local additions. By the
# validation above, if $out exists here it has exactly one well-formed pair.
: > "$tail_tmp"
if [ -f "$out" ]; then
  awk 'found { print } /^\/\* patina:end \*\/$/ { found = 1 }' "$out" > "$tail_tmp"
fi

{
  echo "/* VENDORED FROM patina -- do not edit here. Edit patina and re-run sync.sh. */"
  echo "/* accent: $accent */"
  echo ""
  echo "/* patina:begin $rev sha256:$block_hash */"
  cat "$block"
  echo "/* patina:end */"
  cat "$tail_tmp"
} > "$out"

# theme.js gets a first-line stamp over the rest of its bytes.
if [ "$want_theme" -eq 1 ]; then
  theme_hash="$(sha256sum "$here/theme.js" | cut -d' ' -f1)"
  {
    echo "// patina:sha256 $theme_hash rev:$rev"
    cat "$here/theme.js"
  } > "$target/theme.js"
fi

cp "$here/fonts/"* "$target/fonts/"

# The checker is the enforcement mechanism, so it is the highest-leverage file
# to tamper with — stamp it too, under the shebang, hashing everything below.
check_src="$here/scripts/check_patina.py"
check_hash="$(tail -n +2 "$check_src" | sha256sum | cut -d' ' -f1)"
{
  head -n 1 "$check_src"
  echo "# patina:sha256 $check_hash rev:$rev"
  tail -n +2 "$check_src"
} > "$checks_dir/patina-check.py"
chmod +x "$checks_dir/patina-check.py"

# ---------------------------------------------------------------------------
# --docs: ship the RULES, not just the values.
#
# The estate's UIs are written by agents, and until now sync.sh vendored
# tokens, fonts, a theme toggle and a checker -- but not one line of the
# standard those things enforce. An agent working in a consumer had no local
# copy of the rules it was meant to follow. Adopting gpo-lens made the cost
# concrete, so the fix is deliberately boring: copy the docs, stamp them,
# verify them, stop.
# ---------------------------------------------------------------------------
version="$(cat "$here/VERSION" 2>/dev/null || echo unknown)"
if [ -n "$docs_dir" ]; then
  mkdir -p "$docs_dir"
  banner="<!-- VENDORED FROM patina $version ($rev) -- patina-owned. Do not edit,"
  banner="$banner reformat or lint this file; edit patina and re-run sync.sh. -->"
  entries=""
  for src in "$here"/docs/*.md; do
    name="$(basename "$src")"
    h="$(sha256sum "$src" | cut -d' ' -f1)"
    { echo "$banner"; cat "$src"; } > "$docs_dir/$name"
    [ -n "$entries" ] && entries="$entries,"
    entries="$entries
    \"$name\": \"$h\""
  done
  cat > "$docs_dir/patina-docs.json" <<JSON
{
  "patina_version": "$version",
  "patina_rev": "$rev",
  "note": "Hashes cover the SOURCE bytes; each vendored file carries one extra banner line above them.",
  "files": {$entries
  }
}
JSON
  cat > "$docs_dir/OWNERSHIP.md" <<'OWN'
# Who owns what in this directory

Everything in here except this file is **patina-owned**: vendored verbatim from
the patina repository and verified by `check_patina.py --docs`. Do not edit,
reformat, or lint these files. Exclude this directory from your formatter --
"vendored code stays byte-identical" and "all repository files satisfy our
formatter" are both correct rules, and they collide here.

**patina-owned** (upstream decides; a sync overwrites your changes):
  the vendored docs in this directory, `patina-check.py`, the patina block in
  `css/tokens.css`, `theme.js`, `fonts/`.

**Consumer-owned** (you decide; a sync never touches these):
  `patina.toml` -- your conformance declaration, including which facets you
  claim and the evidence for them; `UI-INVENTORY.md`; your surface briefs and
  any recorded deviations; your ratchet baseline; all of your own CSS,
  including anything below the `/* patina:end */` marker.

The standard is upstream-owned. What you claim about your adoption of it is
yours.
OWN
fi

echo "synced patina $version ($rev) -> $target"
echo "  css/tokens.css  (tokens + $accent accent; stamped sha256:${block_hash:0:12}...)"
if [ "$want_theme" -eq 1 ]; then
  echo "  theme.js        (stamped)"
else
  echo "  theme.js        (skipped: --no-theme)"
fi
echo "  fonts/          ($(ls "$here/fonts"/*.woff2 | wc -l | tr -d ' ') woff2 + licence)"
echo "  patina-check.py -> $checks_dir/ (stamped)"
if [ -n "$docs_dir" ]; then
  echo "  docs/           -> $docs_dir/ ($(ls "$here"/docs/*.md | wc -l | tr -d ' ') files + manifest + OWNERSHIP.md)"
fi
echo
echo "Wire the gate in the consumer's CI. For drift detection (not just"
echo "integrity), check out patina there and pass --upstream <patina-checkout>."
