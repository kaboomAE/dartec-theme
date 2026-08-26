# Dartec Theme

The official [Dartec Smart Homes](https://dartec.ae) theme for Home Assistant — teal primary, copper accent, warm neutrals, with light and dark modes.

Homes managed by Dartec HA Manager receive this theme automatically. Manual installation:

1. HACS → ⋮ → Custom repositories → add this repo (category: **Theme**), then download it.
2. Ensure `configuration.yaml` contains:
   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```
3. Restart Home Assistant, then pick **Dartec** in your profile — or let your Dartec installer set it fleet-wide.
