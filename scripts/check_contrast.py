#!/usr/bin/env python3
"""check_contrast.py -- patina's token contrast gate (plans 002/004).

Verifies WCAG 2.2 contrast floors for the tokens that carry meaning, in both
themes, against both binding surfaces (--bg and --panel):

  hard-fail (exit 1):
    --ok/--warn/--crit/--info  >= 4.5:1  (status renders as text)
    --text, --text-2           >= 4.5:1
    accents (default + every accents/*.css) >= 3:1 (non-text: focus ring,
    active nav; link text is usually also bold/underlined)

  warn-only (reported, never fails -- pending plan 002's quiet-tier decision):
    --text-3                   >= 4.5:1

The gate FAILS CLOSED on anything it cannot evaluate: a required token that is
missing from a theme, or whose value is not an opaque hex (oklch(), color-mix(),
rgb(), or a hex with an alpha channel), is an error rather than a silent skip.
Dropping out of the gate must never be the cheap path -- an earlier version
scored only `#rrggbb` values and would have let a token migrated to oklch()
disappear from the floors without a word.

CVD pairwise validation is NOT gated here -- it needs simulation matrices and
judgment; it is required plan-004-grade work when status values change (see
docs/token-contract.md). This gate only pins the floors that a careless edit
would silently break.

Usage: check_contrast.py [path-to-patina-checkout]   (default: script's repo)
"""

import re
import sys
from pathlib import Path

TEXT_FLOOR = 4.5
NONTEXT_FLOOR = 3.0

TEXT_TOKENS = ("--ok", "--warn", "--crit", "--info", "--text", "--text-2")
SURFACES = ("--bg", "--panel")

HEX_RE = re.compile(r"^#[0-9a-fA-F]+$")


def srgb_channel(c8):
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexval):
    h = hexval.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb_channel(r) + 0.7152 * srgb_channel(g) + 0.0722 * srgb_channel(b)


def contrast(fg, bg):
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def gradeable(value):
    """-> (ok, why-not). Only opaque 3- or 6-digit hex can be scored against a
    surface; alpha would need compositing, and non-hex needs a colour library."""
    if not HEX_RE.match(value):
        return False, f"{value} is not a hex colour (this gate cannot score it)"
    digits = len(value) - 1
    if digits in (4, 8):
        return False, f"{value} carries an alpha channel (not scoreable on a surface)"
    if digits not in (3, 6):
        return False, f"{value} is not a 3- or 6-digit hex"
    return True, ""


def parse_theme_blocks(text):
    """{theme: {token: raw-value}} from :root-level blocks. Values are kept
    verbatim, hex or not, so the caller can fail on the ones it cannot score."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    out = {}
    for m in re.finditer(r"(:root[^{]*)\{([^}]*)\}", text):
        selector = m.group(1)
        theme = "light" if re.search(r'\[data-theme\s*=\s*"light"\]', selector) else "dark"
        for d in re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);", m.group(2)):
            out.setdefault(theme, {})[d.group(1)] = d.group(2).strip()
    return out


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    tokens = parse_theme_blocks((root / "tokens.css").read_text(encoding="utf-8"))

    failures, warnings = [], []

    if set(tokens) != {"dark", "light"}:
        failures.append(
            f"tokens.css: expected both themes, parsed {sorted(tokens) or 'none'}"
        )

    def surfaces_for(theme):
        """The backgrounds a token is graded against; both must be scoreable."""
        found = []
        for surface in SURFACES:
            value = tokens[theme].get(surface)
            if value is None:
                failures.append(f"[{theme}] surface {surface} is not defined")
                continue
            ok, why = gradeable(value)
            if not ok:
                failures.append(f"[{theme}] surface {surface}: {why}")
                continue
            found.append((surface, value))
        return found

    def check(theme, name, value, floor, hard=True):
        ok, why = gradeable(value)
        if not ok:
            # Ungradeable is a failure, not a skip -- see module docstring.
            (failures if hard else warnings).append(f"[{theme}] {name}: {why}")
            return
        for surface, bg in surfaces_for(theme):
            ratio = contrast(value, bg)
            if ratio < floor:
                (failures if hard else warnings).append(
                    f"[{theme}] {name} {value} on {surface} {bg}: "
                    f"{ratio:.2f}:1 < {floor}:1"
                )

    for theme in sorted(tokens):
        for name in TEXT_TOKENS:
            if name not in tokens[theme]:
                failures.append(f"[{theme}] required token {name} is not defined")
                continue
            check(theme, name, tokens[theme][name], TEXT_FLOOR)
        if "--text-3" in tokens[theme]:
            check(theme, "--text-3", tokens[theme]["--text-3"], TEXT_FLOOR, hard=False)
        if "--accent" in tokens[theme]:
            check(theme, "--accent (default)", tokens[theme]["--accent"], NONTEXT_FLOOR)
        else:
            failures.append(f"[{theme}] required token --accent is not defined")

    accent_files = sorted((root / "accents").glob("*.css"))
    if not accent_files:
        failures.append("no accents/*.css found -- accent floors unverified")
    for accent_file in accent_files:
        accents = parse_theme_blocks(accent_file.read_text(encoding="utf-8"))
        for theme in ("dark", "light"):
            value = accents.get(theme, {}).get("--accent")
            if value is None:
                failures.append(
                    f"[{theme}] {accent_file.name}: no --accent for this theme"
                )
                continue
            check(theme, f"--accent ({accent_file.stem})", value, NONTEXT_FLOOR)

    for line in warnings:
        print(f"[warn] {line}  (pending plan 002)")
    for line in failures:
        print(f"[FAIL] {line}")
    if failures:
        print(f"\ncheck_contrast: {len(failures)} failure(s)")
        return 1
    print(f"check_contrast: clean ({len(warnings)} known plan-002 warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
