# Brand Assets

This directory contains brAInwav brand assets for use in this repository's documentation.

## Files

| File | Purpose |
|------|---------|
| `brand-mark.webp` | Primary mark (1x) |
| `brand-mark@2x.webp` | Retina mark (2x) |
| `brand-mark.png` | Fallback PNG (1x) |
| `brand-mark@2x.png` | Fallback PNG (2x) |

## Usage

### README Footer

Use this snippet at the bottom of root README files:

```md
---

<img
  src="./skills-sdk/brand/brand-mark.webp"
  srcset="./skills-sdk/brand/brand-mark.webp 1x, ./skills-sdk/brand/brand-mark@2x.webp 2x"
  alt="brAInwav"
  height="28"
  align="left"
/>

<br clear="left" />

**brAInwav**
_from demo to duty_
```

### ASCII Fallback

For non-graphical environments:

```text
brAInwav
from demo to duty
```

## Rules

- Use the mark in root README footers only
- Do not use as a watermark inside technical docs
- Do not reword the tagline
- Always include `alt` text for accessibility
