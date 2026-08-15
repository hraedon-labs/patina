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


def parse_theme_blocks(text):
    """{theme: {token: hex}} from :root-level blocks; hex values only."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    out = {}
    for m in re.finditer(r"(:root[^{]*)\{([^}]*)\}", text):
        theme = "light" if "light" in m.group(1) else "dark"
        for d in re.finditer(r"(--[A-Za-z0-9_-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;", m.group(2)):
            out.setdefault(theme, {})[d.group(1)] = d.group(2)
    return out


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    tokens = parse_theme_blocks((root / "tokens.css").read_text(encoding="utf-8"))

    failures, warnings = [], []

    def check(theme, name, hexval, floor, hard=True):
        for surface in ("--bg", "--panel"):
            bg = tokens[theme].get(surface)
            if not bg:
                continue
            ratio = contrast(hexval, bg)
            if ratio < floor:
                line = (
                    f"[{theme}] {name} {hexval} on {surface} {bg}: "
                    f"{ratio:.2f}:1 < {floor}:1"
                )
                (failures if hard else warnings).append(line)

    for theme in tokens:
        for name in ("--ok", "--warn", "--crit", "--info", "--text", "--text-2"):
            if name in tokens[theme]:
                check(theme, name, tokens[theme][name], TEXT_FLOOR)
        if "--text-3" in tokens[theme]:
            check(theme, "--text-3", tokens[theme]["--text-3"], TEXT_FLOOR, hard=False)
        if "--accent" in tokens[theme]:
            check(theme, "--accent (default)", tokens[theme]["--accent"], NONTEXT_FLOOR)

    for accent_file in sorted((root / "accents").glob("*.css")):
        accents = parse_theme_blocks(accent_file.read_text(encoding="utf-8"))
        for theme, toks in accents.items():
            if "--accent" in toks:
                check(theme, f"--accent ({accent_file.stem})", toks["--accent"], NONTEXT_FLOOR)

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
