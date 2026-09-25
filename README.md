# Dartec Theme

The official [Dartec Smart Homes](https://dartec.ae) themes for Home Assistant, each with light and dark modes in one theme.

| Theme | What it is |
|---|---|
| **Dartec** | The house theme: brand teal on warm cream and paper. Teal for everything interactive, a readable gold for lights that are on. |
| **Dartec Graphite** | Quiet warm-graphite surfaces with grey icons, and teal only where something is on. The theme for wall panels, and in dark mode for bedrooms at night. |

- **Light and dark** are both written in full; Home Assistant follows the device's setting.
- **Theme variables only.** No card-mod, no JavaScript, no images, nothing downloaded.
- **WCAG AA in both modes.** Text is at least 4.5:1 and icons and controls at least 3:1, checked on every change by [`scripts/contrast.py`](scripts/contrast.py).
- **No copper.** The Dartec brand reserves copper for content written by AI.

## Install

Homes managed by Dartec HA Manager receive these themes automatically. To install them by hand:

1. HACS → ⋮ → Custom repositories → add this repository (category: **Theme**), then download it.
2. Make sure `configuration.yaml` contains:
   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```
3. Restart Home Assistant, then pick **Dartec** or **Dartec Graphite** in your profile, or let your Dartec installer set it for the home.

Since Home Assistant 2026.2, a theme chosen in a person's own profile overrides the home's default theme.

Requires Home Assistant 2025.5 or later, the first release that reads the `ha-font-family-*` variables.

## Fonts

Both themes name Dartec's Arabic face, Lateef, and IBM Plex Mono for code. A theme can name a font but cannot load one, so these appear only on pages that load them; until then Arabic uses the device's own font. Latin text is Roboto, which Home Assistant ships itself. Dubai, the brand's Latin face, is not used: its licence does not allow it to be redistributed.

## Licence

The theme files are under the [MIT licence](LICENSE).

The licence covers the files, not the brand. The name "Dartec", including in these theme names, belongs to Dartec Smart Homes and is not licensed. If you publish a modified copy, give it and its themes a name of your own.
