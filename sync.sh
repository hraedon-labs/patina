#!/usr/bin/env bash
# patina/sync.sh — vendor the shared design tokens into a consuming tool.
#
# Usage:
#   ./sync.sh <accent> <target-static-dir>
#
#   <accent>             name of an accents/<accent>.css file (e.g. gpo-lens)
#   <target-static-dir>  the tool's static root (must contain, or will get,
#                        a css/ subdir; fonts/ and theme.js land alongside)
#
# Example (from a patina checkout):
#   ./sync.sh gpo-lens   ../gpo-lens/src/gpo_lens/web/static
#   ./sync.sh cert-watch ../cert-watch/src/cert_watch/static
#
# What it writes into <target-static-dir>:
#   css/tokens.css   = tokens.css + accents/<accent>.css (concatenated; the
#                      accent block overrides --accent). This file is VENDORED —
#                      do not edit it in the tool; edit patina and re-sync.
#                      The patina-owned content is wrapped in
#                      /* patina:begin <rev> sha256:<hash> */ ... /* patina:end */
#                      delimiters. A consumer MAY append its own CSS below the
#                      end marker; editing inside the block fails check_patina.py.
#   theme.js         = the shared theme toggle (first line carries a
#                      // patina:sha256 stamp over the rest of the file)
#   fonts/           = IBM Plex Mono woff2 + OFL licence
#   patina-check.py  = the conformance checker (Plan 005). Consumers run it in
#                      CI; pass an optional third argument to sync.sh to put it
#                      somewhere else (e.g. the tool's tests/ dir).
#
# The tool keeps its OWN component CSS (its cw-/gp- classes) in a separate file
# and links it after tokens.css. patina owns only the token contract + fonts +
# theme toggle.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
  exit 2
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

mkdir -p "$target/css" "$target/fonts" "$checks_dir"

rev="$(git -C "$here" rev-parse --short HEAD 2>/dev/null || echo unknown)"

# Assemble the patina-owned block first so the stamp hashes exactly the bytes
# that land between the delimiters.
block="$(mktemp)"
trap 'rm -f "$block"' EXIT
{
  cat "$here/tokens.css"
  echo ""
  cat "$accent_file"
} > "$block"
block_hash="$(sha256sum "$block" | cut -d' ' -f1)"

out="$target/css/tokens.css"

# A consumer may keep its own CSS below the end marker; preserve that tail
# across re-syncs so updating patina never eats tool-local additions.
tail_tmp="$(mktemp)"
if [ -f "$out" ]; then
  awk 'found { print } /^\/\* patina:end \*\// { found = 1 }' "$out" > "$tail_tmp"
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
rm -f "$tail_tmp"

# theme.js gets a first-line stamp over the rest of its bytes.
theme_hash="$(sha256sum "$here/theme.js" | cut -d' ' -f1)"
{
  echo "// patina:sha256 $theme_hash rev:$rev"
  cat "$here/theme.js"
} > "$target/theme.js"

cp "$here/fonts/"* "$target/fonts/"
cp "$here/scripts/check_patina.py" "$checks_dir/patina-check.py"

echo "synced patina ($rev) -> $target"
echo "  css/tokens.css  (tokens + $accent accent; stamped sha256:${block_hash:0:12}...)"
echo "  theme.js        (stamped)"
echo "  fonts/          ($(ls "$here/fonts"/*.woff2 | wc -l | tr -d ' ') woff2 + licence)"
echo "  patina-check.py -> $checks_dir/"
