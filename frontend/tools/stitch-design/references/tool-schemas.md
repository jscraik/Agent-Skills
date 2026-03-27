# Stitch MCP Tool Schemas

Format tool calls to the Stitch MCP server using these schemas.

## Project Management

### `list_projects`
```json
{}
```

### `get_project`
```json
{ "name": "projects/4044680601076201931" }
```

### `create_project`
```json
{ "title": "My New App" }
```

## Design Generation

### `generate_screen_from_text`
```json
{
  "projectId": "4044680601076201931",
  "prompt": "A modern landing page...",
  "deviceType": "DESKTOP"
}
```
`deviceType` options: `MOBILE`, `DESKTOP`, `TABLET`

### `edit_screens`
```json
{
  "projectId": "4044680601076201931",
  "selectedScreenIds": ["98b50e2ddc9943efb387052637738f61"],
  "prompt": "Change the background color to white (#ffffff)..."
}
```

## Screen Management

### `list_screens`
```json
{ "projectId": "4044680601076201931" }
```

### `get_screen`
```json
{
  "projectId": "4044680601076201931",
  "screenId": "98b50e2ddc9943efb387052637738f61",
  "name": "projects/4044680601076201931/screens/98b50e2ddc9943efb387052637738f61"
}
```

## Asset Download

After `generate_screen_from_text` or `edit_screens`, download assets from `outputComponents`:

- **HTML source**: `htmlCode.downloadUrl` → save as `.stitch/designs/{page}.html`
- **Screenshot**: `screenshot.downloadUrl` — append `=w{width}` where `{width}` is the screen's `width` value to get full resolution (Google CDN serves low-res thumbnails by default). Save as `.stitch/designs/{page}.png`

**Idempotency rule**: Before downloading, check if `.stitch/designs/{page}.html` and `.stitch/designs/{page}.png` already exist. If they do, ask the user whether to refresh from Stitch or reuse the existing local files.
