"""Structure checks for every theme file in themes/.

    python scripts/check_themes.py   # exit 1 on any problem

Each file must load as Home Assistant's `frontend: themes:` map: theme names
mapping to string variables, with an optional `modes` holding `light` and
`dark`, each a map of strings (the frontend's THEME_SCHEMA). On top of that,
for these themes:

- no key appears twice in any map (PyYAML would silently keep the last one);
- every theme writes both light and dark, and each mode sets the core colours;
- every colour value is valid: a hex colour, rgb()/rgba() in range, var(), or a
  gradient made of those;
- theme variables only: no card-mod, no JavaScript, no url() (no images or
  downloads);
- no copper, which the brand reserves for content written by AI;
- every theme is published under its Baytec name and its Dartec name (the
  company's name until 2026-10, which homes may still store as their default),
  and the two are identical.
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Every mode of every theme sets these itself rather than inheriting them.
CORE = [
    "primary-background-color", "secondary-background-color", "card-background-color",
    "primary-text-color", "secondary-text-color", "disabled-text-color", "divider-color",
    "primary-color", "accent-color", "text-primary-color",
    "state-icon-color", "state-active-color",
    "error-color", "warning-color", "success-color",
    "sidebar-background-color",
]

# Theme names start with the brand, and every theme is shipped under both.
BRAND_NAME, OLD_NAME = "Baytec", "Dartec"

# The copper accents of v1.1.0 (light and dark).
COPPER = {"#a8551f", "#e08b52"}

HEX = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![0-9a-zA-Z])"
NUM = r"\s*(\d+(?:\.\d+)?)\s*"
RGB = rf"rgba?\({NUM},{NUM},{NUM}(?:,{NUM})?\)"
VAR = r"var\(--[a-z0-9_-]+(?:\s*,\s*[^()]+)?\)"
GRADIENT = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(")


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _no_duplicates(loader, node, deep=False):
    seen = {}
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key {key!r} (first at line {seen[key] + 1})",
                key_node.start_mark)
        seen[key] = key_node.start_mark.line
    return loader.construct_mapping(node, deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def colour_problems(key, value):
    """Problems with the colours in one value; [] if it holds none or all are valid."""
    problems = []
    for m in re.finditer(r"#[0-9a-zA-Z]+", value):
        if not re.fullmatch(HEX, m.group()):
            problems.append(f"{key}: {m.group()!r} is not a hex colour")
    for m in re.finditer(r"rgba?\([^)]*\)", value):
        rm = re.fullmatch(RGB, m.group())
        if not rm:
            problems.append(f"{key}: {m.group()!r} is not a valid rgb()/rgba()")
            continue
        r, g, b, a = rm.groups()
        if not all(0 <= float(c) <= 255 for c in (r, g, b)):
            problems.append(f"{key}: {m.group()!r} has a channel outside 0-255")
        if m.group().startswith("rgba(") and a is None:
            problems.append(f"{key}: {m.group()!r} has no alpha")
        if a is not None and not 0 <= float(a) <= 1:
            problems.append(f"{key}: {m.group()!r} has an alpha outside 0-1")
    if key.endswith("-color") and not re.fullmatch(rf"{HEX}|{RGB}|{VAR}", value.strip()):
        problems.append(f"{key}: {value!r} is not a single colour")
    if key.endswith("-background") and not (
            re.fullmatch(rf"{HEX}|{RGB}|{VAR}|none|transparent", value.strip())
            or GRADIENT.match(value.strip())):
        problems.append(f"{key}: {value!r} is neither a colour nor a gradient")
    if GRADIENT.match(value.strip()) and value.count("(") != value.count(")"):
        problems.append(f"{key}: unbalanced parentheses")
    return problems


def check_vars(where, mapping):
    problems = []
    if not isinstance(mapping, dict) or not mapping:
        return [f"{where}: must be a non-empty map"]
    for key, value in mapping.items():
        if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", key):
            problems.append(f"{where}: {key!r} is not a theme variable name")
            continue
        if not isinstance(value, str):
            problems.append(f"{where}: {key} must be a quoted string, got {type(value).__name__}")
            continue
        low = value.lower()
        if "card-mod" in key or "card-mod" in low:
            problems.append(f"{where}: {key} uses card-mod")
        if "url(" in low or "javascript" in low or "<" in low:
            problems.append(f"{where}: {key} loads something ({value!r})")
        for hex_ in re.findall(HEX, low):
            if hex_ in COPPER:
                problems.append(f"{where}: {key} is copper ({hex_})")
        problems += [f"{where}: {p}" for p in colour_problems(key, value)]
    return problems


def check_file(path):
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except yaml.YAMLError as e:
        return [f"{path.name}: {e}"], []
    if not isinstance(data, dict) or not data:
        return [f"{path.name}: must be a map of theme names"], []
    problems, names = [], []
    for name, theme in data.items():
        names.append(name)
        where = f"{path.name}: {name}"
        if not isinstance(name, str) or not name.startswith((BRAND_NAME, OLD_NAME)):
            problems.append(f"{where}: theme names start with '{BRAND_NAME}' or '{OLD_NAME}'")
        if not isinstance(theme, dict):
            problems.append(f"{where}: must be a map")
            continue
        modes = theme.get("modes")
        base = {k: v for k, v in theme.items() if k != "modes"}
        problems += check_vars(f"{where}", base)
        if not isinstance(modes, dict) or set(modes) != {"light", "dark"}:
            problems.append(f"{where}: modes must be exactly light and dark")
            continue
        for mode in ("light", "dark"):
            problems += check_vars(f"{where} ({mode})", modes[mode])
            if isinstance(modes[mode], dict):
                missing = [k for k in CORE if k not in modes[mode]]
                if missing:
                    problems.append(f"{where} ({mode}): does not set {', '.join(missing)}")
    return problems, names


def twin_problems(themes):
    """Every Baytec theme has a Dartec twin with the same content, and back.

    A home stores its default theme by name. Dropping or changing a Dartec
    name sends a home that stores it to Home Assistant's stock look, and a
    Baytec theme that drifts from its twin changes the look on Apply.
    """
    problems = []
    for name, theme in themes.items():
        if not isinstance(name, str):
            continue
        for mine, other in ((BRAND_NAME, OLD_NAME), (OLD_NAME, BRAND_NAME)):
            if name.startswith(mine):
                twin = other + name[len(mine):]
                if twin not in themes:
                    problems.append(f"{name}: no {twin!r} beside it")
                elif themes[twin] != theme:
                    problems.append(f"{name}: differs from {twin!r}")
    return problems


def main():
    files = sorted((ROOT / "themes").glob("*.yaml"))
    if not files:
        print("no theme files in themes/")
        return 1
    problems, names, themes = [], [], {}
    for path in files:
        p, n = check_file(path)
        problems += p
        names += n
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            themes.update(data)
    if len(names) != len(set(names)):
        problems.append("a theme name is used twice across files")
    problems += twin_problems(themes)
    for p in problems:
        print(f"FAIL {p}")
    print(f"{len(names)} themes in {len(files)} file(s): {', '.join(names)}")
    print("All structure checks pass." if not problems else f"{len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
