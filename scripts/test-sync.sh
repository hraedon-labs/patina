#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/patina-sync.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

fail() {
  echo "test-sync: $*" >&2
  exit 1
}

for accent_file in "$root"/accents/*.css; do
  accent="$(basename "$accent_file" .css)"
  target="$tmp/$accent target"
  mkdir "$target"

  "$root/sync.sh" "$accent" "$target" >/dev/null

  {
    printf '%s\n' '/* VENDORED FROM patina — do not edit here. Edit patina and re-run sync.sh. */'
    printf '/* accent: %s */\n\n' "$accent"
    cat "$root/tokens.css"
    printf '\n'
    cat "$accent_file"
  } >"$tmp/expected.css"

  cmp "$tmp/expected.css" "$target/css/tokens.css" ||
    fail "$accent produced incorrect vendored CSS"
  cmp "$root/theme.js" "$target/theme.js" ||
    fail "$accent installed theme.js incorrectly"

  for asset in "$root"/fonts/*; do
    name="$(basename "$asset")"
    cmp "$asset" "$target/fonts/$name" ||
      fail "$accent installed $name incorrectly"
  done
  for name in \
    ibm-plex-mono-latin-400.woff2 \
    ibm-plex-mono-latin-500.woff2 \
    ibm-plex-mono-latin-600.woff2 \
    LICENSE-IBM-Plex-Mono.txt; do
    [ -f "$target/fonts/$name" ] || fail "$accent did not install $name"
  done
done

check_wrong_arity() {
  local name="$1"
  shift
  local target="$tmp/wrong arity $name target"
  local stdout="$tmp/wrong-arity-$name.stdout"
  local stderr="$tmp/wrong-arity-$name.stderr"
  mkdir "$target"

  set +e
  "$root/sync.sh" "$@" >"$stdout" 2>"$stderr"
  local status=$?
  set -e
  [ "$status" -eq 2 ] || fail "$name wrong arity returned status $status, not 2"
  case "$(<"$stdout")" in
    *"Usage:"*) ;;
    *) fail "$name wrong arity did not print usage" ;;
  esac
  [ ! -s "$stderr" ] || fail "$name wrong arity wrote to stderr"
  if compgen -G "$target/*" >/dev/null; then
    fail "$name wrong arity produced output"
  fi
}

check_wrong_arity zero
check_wrong_arity one dossier
check_wrong_arity extra dossier "$tmp/wrong arity extra target" unexpected

mkdir "$tmp/failure target"
if "$root/sync.sh" not-an-accent "$tmp/failure target" >/dev/null 2>&1; then
  fail "unknown accent unexpectedly succeeded"
fi
if "$root/sync.sh" dossier "$tmp/missing target" >/dev/null 2>&1; then
  fail "missing target unexpectedly succeeded"
fi

mkdir "$tmp/bin" "$tmp/copy failure target"
printf '#!/bin/sh\nexit 23\n' >"$tmp/bin/cp"
chmod +x "$tmp/bin/cp"
set +e
PATH="$tmp/bin:$PATH" \
  "$root/sync.sh" dossier "$tmp/copy failure target" >/dev/null 2>&1
status=$?
set -e
[ "$status" -eq 23 ] || fail "copy failure returned status $status, not 23"

echo "test-sync: all accents passed"
