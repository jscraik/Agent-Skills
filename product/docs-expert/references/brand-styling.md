# brAInwav Brand Styling

Use this reference when visual formatting or styling artifacts are requested.

## Overview

To access brAInwav's official brand identity and style resources, use this skill.

Keywords: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, brAInwav brand, visual formatting, visual design

## Brand Guidelines

### Colors

Main colors:

- Dark: #141413 - Primary text and dark backgrounds
- Light: #faf9f5 - Light backgrounds and text on dark
- Mid Gray: #b0aea5 - Secondary elements
- Light Gray: #e8e6dc - Subtle backgrounds

Accent colors:

- Orange: #d97757 - Primary accent
- Blue: #6a9bcc - Secondary accent
- Green: #788c5d - Tertiary accent

### Typography

- Headings: Poppins (with Arial fallback)
- Body text: Lora (with Georgia fallback)
- Note: Fonts should be pre-installed in your environment for best results

## Features

### Smart font application

- Applies Poppins font to headings (24pt and larger)
- Applies Lora font to body text
- Automatically falls back to Arial or Georgia if custom fonts are unavailable
- Preserves readability across all systems

### Text styling

- Headings (24pt+): Poppins font
- Body text: Lora font
- Smart color selection based on background
- Preserves text hierarchy and formatting

### Shape and accent colors

- Non-text shapes use accent colors
- Cycles through orange, blue, and green accents
- Maintains visual interest while staying on-brand

## Technical details

### Font management

- Uses system-installed Poppins and Lora fonts when available
- Provides automatic fallback to Arial (headings) and Georgia (body)
- No font installation required - works with existing system fonts
- For best results, pre-install Poppins and Lora fonts in your environment

### Color application

- Uses RGB color values for precise brand matching
- Applied via python-pptx's RGBColor class
- Maintains color fidelity across different systems
