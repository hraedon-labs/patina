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
#   theme.js         = the shared theme toggle
#   fonts/           = IBM Plex Mono woff2 + OFL licence
#
# The tool keeps its OWN component CSS (its cw-/gp- classes) in a separate file
# and links it after tokens.css. patina owns only the token contract + fonts +
# theme toggle.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -ne 2 ]; then
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

accent="$1"
target="$2"
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

mkdir -p "$target/css" "$target/fonts"

out="$target/css/tokens.css"
{
  echo "/* VENDORED FROM patina — do not edit here. Edit patina and re-run sync.sh. */"
  echo "/* accent: $accent */"
  echo ""
  cat "$here/tokens.css"
  echo ""
  cat "$accent_file"
} > "$out"

cp "$here/theme.js" "$target/theme.js"
cp "$here/fonts/"* "$target/fonts/"

echo "synced patina -> $target"
echo "  css/tokens.css  (tokens + $accent accent)"
echo "  theme.js"
echo "  fonts/          ($(ls "$here/fonts"/*.woff2 | wc -l | tr -d ' ') woff2 + licence)"
