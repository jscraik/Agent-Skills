# Internationalization and Localization

Last verified: 2026-01-01

Use this when UI includes user-facing text or directional icons.

## Text length and wrapping
- Allow 30-50% text expansion for translation.
- Prefer wrapping over truncation; use ellipsis only when necessary.
- Avoid fixed-height containers for text.

## RTL and bidi
- Mirror directional UI (chevrons, back/forward, sliders).
- Verify reading order and focus order are correct in RTL.
- Use `dir="auto"` for mixed RTL/LTR content.

## Numbers, dates, and units
- Use locale-aware formatting for numbers, dates, and currencies.
- Avoid hard-coded separators or date formats.

## Font and glyph coverage
- Ensure chosen fonts support target scripts.
- Provide fallbacks when glyphs are missing.
