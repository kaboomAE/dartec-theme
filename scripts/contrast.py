"""WCAG 2.x contrast for every theme in themes/, in light and in dark.

    python scripts/contrast.py            # table, exit 1 if any pair fails
    python scripts/contrast.py --markdown # the same as a Markdown table

Each pair is a colour Home Assistant actually draws on another, with the bar
WCAG AA sets for it: 4.5:1 for text, 3:1 for icons and controls (1.4.11).
Variables a theme does not set fall back to Home Assistant's own defaults,
following the var() chains in the frontend's color.globals.ts.
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

TEXT, UI = 4.5, 3.0

# (label, foreground, background, bar)
PAIRS = [
    ("text on card", "primary-text-color", "card-background-color", TEXT),
    ("secondary text on card", "secondary-text-color", "card-background-color", TEXT),
    ("text on page", "primary-text-color", "primary-background-color", TEXT),
    ("secondary text on page", "secondary-text-color", "primary-background-color", TEXT),
    ("header text", "app-header-text-color", "app-header-background-color", TEXT),
    ("sidebar selected text", "sidebar-selected-text-color", "sidebar-background-color", TEXT),
    ("link (primary) on card", "primary-color", "card-background-color", TEXT),
    ("text on primary", "text-primary-color", "primary-color", TEXT),
    ("text on error", "text-primary-color", "error-color", TEXT),
    ("accent on card", "accent-color", "card-background-color", UI),
    ("icon on card", "state-icon-color", "card-background-color", UI),
    ("active on card", "state-active-color", "card-background-color", UI),
    ("AC cool on card", "state-climate-cool-color", "card-background-color", UI),
    ("AC dry on card", "state-climate-dry-color", "card-background-color", UI),
    ("AC fan on card", "state-climate-fan_only-color", "card-background-color", UI),
    ("light on on card", "state-light-on-color", "card-background-color", UI),
    ("switch on on card", "state-switch-on-color", "card-background-color", UI),
    ("cover on card", "state-cover-active-color", "card-background-color", UI),
    ("error on card", "error-color", "card-background-color", UI),
    ("warning on card", "warning-color", "card-background-color", UI),
    ("success on card", "success-color", "card-background-color", UI),
]

# Home Assistant's defaults for the variables above, where a theme leaves one
# unset (frontend src/resources/theme/color/color.globals.ts).
HA_DEFAULTS = {
    "text-primary-color": "#ffffff",
    "app-header-background-color": "var(--sidebar-background-color)",
    "app-header-text-color": "var(--sidebar-text-color)",
    "sidebar-text-color": "var(--primary-text-color)",
    "sidebar-selected-text-color": "var(--primary-color)",
    "state-icon-color": "#44739e",
    "state-active-color": "#ffc107",
    "state-climate-cool-color": "#2196f3",
    "state-climate-dry-color": "#ff9800",
    "state-climate-fan_only-color": "#00bcd4",
    "state-light-on-color": "var(--state-light-active-color)",
    "state-light-active-color": "#ffc107",
    "state-switch-on-color": "var(--state-switch-active-color)",
    "state-switch-active-color": "#ffc107",
    "state-cover-active-color": "#9c27b0",
}

# Brand reference pairs, reported but not themed (nothing here draws them).
BRAND = [
    ("tan #DDD6C4 on teal #1A6B6B", "#ddd6c4", "#1a6b6b"),
    ("tan #DDD6C4 on dark teal #0F4F4F", "#ddd6c4", "#0f4f4f"),
    ("warm grey #8F8368 on teal #1A6B6B", "#8f8368", "#1a6b6b"),
    ("white on teal #1A6B6B", "#ffffff", "#1a6b6b"),
]


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def resolve(values, key, seen=()):
    if key in seen:
        raise ValueError(f"var() loop at {key}")
    value = values.get(key, HA_DEFAULTS.get(key))
    if value is None:
        raise KeyError(f"{key} is not set and has no default here")
    value = str(value).strip()
    m = re.fullmatch(r"var\(--([\w-]+)\)", value)
    if m:
        return resolve(values, m.group(1), seen + (key,))
    if not re.fullmatch(r"#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?", value):
        raise ValueError(f"{key} is {value!r}; only opaque hex colours can be measured")
    return value.lower()


def themes():
    for path in sorted((ROOT / "themes").glob("*.yaml")):
        for name, theme in yaml.safe_load(path.read_text(encoding="utf-8")).items():
            base = {k: v for k, v in theme.items() if k != "modes"}
            for mode in ("light", "dark"):
                if mode not in theme.get("modes", {}):
                    raise SystemExit(f"{name}: no {mode} mode")
                yield name, mode, {**base, **theme["modes"][mode]}


def main(markdown=False):
    rows, failures = [], 0
    for name, mode, values in themes():
        for label, fg, bg, bar in PAIRS:
            f, b = resolve(values, fg), resolve(values, bg)
            r = ratio(f, b)
            ok = r >= bar
            failures += not ok
            rows.append((name, mode, label, f, b, r, bar, ok))

    if markdown:
        print("| Theme | Mode | Pair | Foreground | Background | Ratio | Bar | AA |")
        print("|---|---|---|---|---|---|---|---|")
        for name, mode, label, f, b, r, bar, ok in rows:
            print(f"| {name} | {mode} | {label} | `{f}` | `{b}` | {r:.2f} | {bar:g} | {'pass' if ok else '**FAIL**'} |")
        print()
        print("Brand reference (not drawn by these themes):")
        print()
        for label, f, b in BRAND:
            print(f"- {label}: {ratio(f, b):.2f}")
    else:
        for name, mode, label, f, b, r, bar, ok in rows:
            print(f"{'ok  ' if ok else 'FAIL'} {name:18} {mode:5} {label:24} {f} on {b}  {r:5.2f} (>= {bar:g})")
        print()
        for label, f, b in BRAND:
            print(f"brand  {label:36} {ratio(f, b):5.2f}")
    print()
    print(f"{len(rows) - failures} of {len(rows)} pairs pass WCAG AA.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main("--markdown" in sys.argv))
