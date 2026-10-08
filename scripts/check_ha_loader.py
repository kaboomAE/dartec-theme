"""Load the themes the way Home Assistant does, and check every name resolves.

    pip install annotatedyaml==1.0.2   # Home Assistant's own YAML loader
    python scripts/check_ha_loader.py  # exit 1 on any problem

The Dartec names are YAML aliases of the Baytec blocks. PyYAML resolves them,
but Home Assistant reads theme files through its own loader (annotatedyaml,
the C loader where it is available) under `!include_dir_merge_named themes`,
as HACS installs them into `themes/<repository>/`. This builds that layout in
a temporary folder, loads it through that loader, and checks that every theme
in the file arrives under its own name, with each Dartec name equal to its
Baytec twin.
"""
import pathlib
import shutil
import sys
import tempfile

import yaml
from annotatedyaml import loader

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND_NAME, OLD_NAME = "Baytec", "Dartec"


def main():
    expected = {}
    for path in sorted((ROOT / "themes").glob("*.yaml")):
        expected.update(yaml.safe_load(path.read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as tmp:
        config = pathlib.Path(tmp)
        installed = config / "themes" / "dartec-theme"
        installed.mkdir(parents=True)
        for path in (ROOT / "themes").glob("*.yaml"):
            shutil.copy(path, installed / path.name)
        (config / "configuration.yaml").write_text(
            "frontend:\n  themes: !include_dir_merge_named themes\n", encoding="utf-8")
        themes = loader.load_yaml(str(config / "configuration.yaml"))["frontend"]["themes"]
    problems = []
    for name, theme in expected.items():
        if name not in themes:
            problems.append(f"{name}: not loaded")
        elif dict(themes[name]) != theme:
            problems.append(f"{name}: loaded differently from the file")
        if name.startswith(OLD_NAME):
            twin = BRAND_NAME + name[len(OLD_NAME):]
            if twin in themes and themes[name] != themes[twin]:
                problems.append(f"{name}: differs from {twin} as Home Assistant loads it")
    for p in problems:
        print(f"FAIL {p}")
    c_loader = getattr(loader, "HAS_C_LOADER", None)
    print(f"Home Assistant's loader (C loader: {c_loader}) loaded {len(themes)} themes: "
          f"{', '.join(sorted(themes))}")
    print("Every theme loads under its name." if not problems else f"{len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
