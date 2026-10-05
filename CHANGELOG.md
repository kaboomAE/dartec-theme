# Changelog

Each version is a GitHub release with a tag of the same name; HACS installs the release, not the branch. Theme names never change between versions, because homes store their default theme by name.

## v1.3.0

Four new themes, completing the family the owner approved in [#1](https://github.com/kaboomAE/dartec-theme/issues/1). **Dartec** and **Dartec Graphite** are unchanged, so homes that use them see nothing new.

### New themes

- **Dartec Glass**: frosted, translucent cards (`ha-card-background` with `ha-card-backdrop-filter`) over a teal gradient ground (`lovelace-background`), with 14 px corners. No photograph and no download: the ground is a gradient. The top bar stays solid. Blur is costly to draw, so Glass is for phones and capable tablets, not wall panels.
- **Dartec Glass Lite**: Glass's colours and ground with solid cards and no blur, for wall panels and slower tablets.
- **Dartec Soft**: borderless paper cards on the brand's two-layer shadow in light mode, a hairline edge instead of a shadow in dark mode, 12 px corners.
- **Dartec Material**: tonal surfaces from a Material 3 "tonal spot" scheme generated from the brand teal #1A6B6B, with the dark ground lifted off near-black; 16 px cards with no border or shadow.

Each is in `themes/dartec.yaml` beside the other two, sets light and dark in full, uses theme variables only, and names Lateef and IBM Plex Mono as Dartec and Graphite do.

### Changes from the approved drafts

- The font stack is the one v1.2.0 ships (`'Dartec Lateef', Roboto, …`). The drafts named Dubai first, whose licence does not allow it to be redistributed.
- Covers use `state-cover-active-color`, which Home Assistant reads, instead of the drafts' `state-cover-open-color`.
- Text on the light dark-mode teal is ink, not white, as in Dartec and Graphite.
- Light-mode warning is `#c96e05` in Glass, Glass Lite and Material, as in Graphite: the drafts' `#d97706` was 2.89:1, 2.99:1 and 2.75:1 on their cards, below the 3:1 for icons. The drafts' contrast table did not measure warnings.
- Info colour, the sidebar's selected item and the dark-mode code editor are set to match each theme.

### Checks

- `scripts/contrast.py` now measures views whose ground is a gradient and glass cards: every pair on a card or the page is measured against each colour of the gradient, with a translucent card blended over it, and the worst ratio counts. Dialogs, which use the solid `card-background-color`, are measured too. **252 of 252 pairs pass WCAG AA** across the six themes; Dartec's and Graphite's 84 figures are unchanged.
- New `scripts/check_themes.py`, run in CI: each file loads as Home Assistant's themes map, no key is set twice, every theme writes light and dark with the core colours, every colour value is valid, and nothing uses card-mod, `url()`, JavaScript or copper.

## v1.2.0 (2026-09-25)

- **Dartec, corrected:** the accent is brand teal instead of copper; the AC's cool, dry and fan modes, lights that are on and moving covers use brand colours; dark-mode text on teal is ink. Fonts use the `ha-font-family-*` variables Home Assistant reads since 2025.5.
- **New: Dartec Graphite**, the panel and night theme.
- MIT licence for the files (the name "Dartec" is not licensed). Requires Home Assistant 2025.5 or later.
- `scripts/contrast.py` checks WCAG AA on every change: 84 of 84 pairs pass.

## v1.1.0 (2026-08-26)

- The theme is renamed from `DarTec` to `Dartec`, per the brand guidelines. Re-apply it after updating: the theme's key changed.

## v1.0.0 (2026-08-25)

- First release: teal primary, copper accent, warm neutrals, light and dark modes.
