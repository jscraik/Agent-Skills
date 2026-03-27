# .stitch/metadata.json Schema

Persist this file after creating a project or generating screens. It stores all Stitch identifiers needed for future iterations, edits, and variants.

## Population workflow

1. After `create_project`, call `[prefix]:get_project` with the full resource name (`projects/{id}`) and save the response here.
2. After each `generate_screen_from_text`, call `[prefix]:get_project` again and update the `screens` map with the new screen's full metadata.

## Schema

```json
{
  "name": "projects/6139132077804554844",
  "projectId": "6139132077804554844",
  "title": "My App",
  "visibility": "PRIVATE",
  "createTime": "2026-03-04T23:11:25.514932Z",
  "updateTime": "2026-03-04T23:34:40.400007Z",
  "projectType": "PROJECT_DESIGN",
  "origin": "STITCH",
  "deviceType": "MOBILE",
  "designTheme": {
    "colorMode": "DARK",
    "font": "INTER",
    "roundness": "ROUND_EIGHT",
    "customColor": "#40baf7",
    "saturation": 3
  },
  "screens": {
    "index": {
      "id": "d7237c7d78f44befa4f60afb17c818c1",
      "sourceScreen": "projects/6139132077804554844/screens/d7237c7d78f44befa4f60afb17c818c1",
      "x": 0,
      "y": 0,
      "width": 390,
      "height": 1249
    },
    "about": {
      "id": "bf6a3fe5c75348e58cf21fc7a9ddeafb",
      "sourceScreen": "projects/6139132077804554844/screens/bf6a3fe5c75348e58cf21fc7a9ddeafb",
      "x": 549,
      "y": 0,
      "width": 390,
      "height": 1159
    }
  },
  "metadata": {
    "userRole": "OWNER"
  }
}
```

## Field reference

| Field | Description |
|-------|-------------|
| `name` | Full resource name (`projects/{id}`) — use for `get_project` calls |
| `projectId` | Numeric Stitch project ID — use for `generate_screen_from_text`, `list_screens` |
| `title` | Human-readable project title |
| `deviceType` | Target device: `MOBILE`, `DESKTOP`, `TABLET` |
| `designTheme` | Design system tokens: color mode, font, roundness, custom color, saturation |
| `screens` | Map of page slug → screen object |
| `screens[n].id` | Screen ID — use for `edit_screens` as `selectedScreenIds` |
| `screens[n].sourceScreen` | Full resource path — use for `get_screen` `name` parameter |
| `screens[n].width` / `height` | Screen dimensions — use for `=w{width}` URL suffix on screenshot downloads |
| `metadata.userRole` | User's role: `OWNER`, `EDITOR`, `VIEWER` |

## Screenshot download note

The Stitch `screenshot.downloadUrl` serves a low-resolution thumbnail by default.
To get the full-resolution image, append `=w{width}` to the URL before downloading,
where `{width}` is the screen's `width` value from this file.

```bash
# Example: screen width is 390
curl -o .stitch/designs/index.png "https://lh3.googleusercontent.com/.../photo.jpg=w390"
```

## Idempotency rule

Before downloading `.stitch/designs/{page}.html` or `.stitch/designs/{page}.png`, check if the files already exist.
If they do, ask the user whether to refresh from Stitch or reuse the existing local files.
Only re-download on explicit confirmation to avoid unnecessary API calls.
