#!/usr/bin/env python3
"""
Pro-Grade Favicon Generator

Generate professional-quality favicons with advanced visual effects using Pillow.
Supports drop shadows, inner glows, highlights, noise, gradients, and more.

For Lucide icons, uses cairosvg to render actual SVG paths with bezier curves.

Usage:
    python generate_favicon.py --letter A --bg "#6366f1" --output ./favicons/
    python generate_favicon.py --letter T --bg "#ec4899" --bg2 "#f97316" --style vibrant
    python generate_favicon.py --lucide package-plus --bg "#f97316" --bg2 "#ef4444" --output ./public/
"""

import argparse
import colorsys
import math
import os
import struct
import zlib
from io import BytesIO
from pathlib import Path
from typing import Literal

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    exit(1)

# Try to import cairosvg for Lucide icon rendering
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


# ============================================================================
# DESIGN TEMPLATES
# ============================================================================

TEMPLATES = {
    "modern": {
        "bg": "#6366f1",
        "bg2": "#8b5cf6",
        "fg": "#ffffff",
        "gradient": True,
        "shadow": 0.4,
        "highlight": 0.25,
        "inner_glow": 0.0,
        "noise": 0.0,
        "corner_radius": 0.22,
    },
    "vibrant": {
        "bg": "#ec4899",
        "bg2": "#f97316",
        "fg": "#ffffff",
        "gradient": True,
        "shadow": 0.5,
        "highlight": 0.3,
        "inner_glow": 0.2,
        "noise": 0.0,
        "corner_radius": 0.22,
    },
    "minimal": {
        "bg": "#18181b",
        "bg2": "#27272a",
        "fg": "#fafafa",
        "gradient": False,
        "shadow": 0.3,
        "highlight": 0.0,
        "inner_glow": 0.0,
        "noise": 0.05,
        "corner_radius": 0.18,
    },
    "glass": {
        "bg": "#3b82f6",
        "bg2": "#06b6d4",
        "fg": "#ffffff",
        "gradient": True,
        "shadow": 0.35,
        "highlight": 0.5,
        "inner_glow": 0.4,
        "noise": 0.03,
        "corner_radius": 0.24,
    },
    "neon": {
        "bg": "#0f172a",
        "bg2": "#1e293b",
        "fg": "#22d3ee",
        "gradient": True,
        "shadow": 0.6,
        "highlight": 0.0,
        "inner_glow": 0.6,
        "noise": 0.04,
        "corner_radius": 0.20,
    },
    "warm": {
        "bg": "#f59e0b",
        "bg2": "#ef4444",
        "fg": "#ffffff",
        "gradient": True,
        "shadow": 0.45,
        "highlight": 0.35,
        "inner_glow": 0.0,
        "noise": 0.0,
        "corner_radius": 0.22,
    },
    "forest": {
        "bg": "#22c55e",
        "bg2": "#14b8a6",
        "fg": "#ffffff",
        "gradient": True,
        "shadow": 0.4,
        "highlight": 0.25,
        "inner_glow": 0.0,
        "noise": 0.06,
        "corner_radius": 0.22,
    },
    "mono": {
        "bg": "#ffffff",
        "bg2": "#f4f4f5",
        "fg": "#18181b",
        "gradient": False,
        "shadow": 0.25,
        "highlight": 0.0,
        "inner_glow": 0.0,
        "noise": 0.0,
        "corner_radius": 0.18,
    },
}

# Standard favicon sizes
SIZES = [16, 32, 48, 64, 128, 180, 192, 512]

# ============================================================================
# LUCIDE ICON SVG PATHS
# Extract from node_modules/lucide-react/dist/esm/icons/[icon-name].js
# ============================================================================

LUCIDE_ICONS = {
    "package-plus": [
        '<path d="M16 16h6"/>',
        '<path d="M19 13v6"/>',
        '<path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l2-1.14"/>',
        '<path d="m7.5 4.27 9 5.15"/>',
        '<polyline points="3.29 7 12 12 20.71 7"/>',
        '<line x1="12" x2="12" y1="22" y2="12"/>',
    ],
    "rocket": [
        '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>',
        '<path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>',
        '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>',
        '<path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    ],
    "zap": [
        '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    ],
    "star": [
        '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
    ],
    "terminal": [
        '<polyline points="4 17 10 11 4 5"/>',
        '<line x1="12" x2="20" y1="19" y2="19"/>',
    ],
    "code": [
        '<polyline points="16 18 22 12 16 6"/>',
        '<polyline points="8 6 2 12 8 18"/>',
    ],
    "sparkles": [
        '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
        '<path d="M20 3v4"/>',
        '<path d="M22 5h-4"/>',
        '<path d="M4 17v2"/>',
        '<path d="M5 18H3"/>',
    ],
    "heart": [
        '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    ],
    "shield": [
        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    ],
    "flame": [
        '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    ],
    "globe": [
        '<circle cx="12" cy="12" r="10"/>',
        '<path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>',
        '<path d="M2 12h20"/>',
    ],
    "send": [
        '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/>',
        '<path d="m21.854 2.147-10.94 10.939"/>',
    ],
    "box": [
        '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>',
        '<path d="m3.3 7 8.7 5 8.7-5"/>',
        '<path d="M12 22V12"/>',
    ],
}


def render_lucide_icon(
    icon_name: str,
    size: int,
    bg_color: str = "#6366f1",
    bg_color2: str | None = None,
    fg_color: str = "#ffffff",
    corner_radius: float = 0.22,
) -> Image.Image | None:
    """
    Render a Lucide icon using cairosvg.
    
    Args:
        icon_name: Name of the Lucide icon (e.g., 'package-plus', 'rocket')
        size: Output size in pixels
        bg_color: Background color (hex)
        bg_color2: Gradient end color (hex), None for solid
        fg_color: Icon stroke color (hex)
        corner_radius: Corner radius as fraction (0-0.5)
    
    Returns:
        PIL Image with the rendered icon, or None if cairosvg not available
    """
    if not HAS_CAIROSVG:
        print(f"Warning: cairosvg not available. Install with: pip install cairosvg")
        print(f"         Also need native cairo: brew install cairo (macOS)")
        return None
    
    if icon_name not in LUCIDE_ICONS:
        print(f"Warning: Unknown icon '{icon_name}'. Available: {', '.join(LUCIDE_ICONS.keys())}")
        return None
    
    # Build SVG with icon paths
    icon_paths = "\n    ".join(LUCIDE_ICONS[icon_name])
    
    # Calculate scaling: Lucide uses 24x24 viewBox
    padding_ratio = 0.15
    icon_area = size * (1 - 2 * padding_ratio)
    scale = icon_area / 24
    offset = size * padding_ratio
    radius = int(size * corner_radius)
    
    # Build gradient or solid fill
    if bg_color2 and bg_color2 != bg_color:
        gradient_def = f'''<defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="{bg_color2}"/>
    </linearGradient>
  </defs>'''
        fill = "url(#bg)"
    else:
        gradient_def = ""
        fill = bg_color
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  {gradient_def}
  <rect width="{size}" height="{size}" rx="{radius}" fill="{fill}"/>
  <g transform="translate({offset}, {offset}) scale({scale})" 
     stroke="{fg_color}" stroke-width="2" fill="none" 
     stroke-linecap="round" stroke-linejoin="round">
    {icon_paths}
  </g>
</svg>'''
    
    # Render SVG to PNG
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    return Image.open(BytesIO(png_data)).convert('RGBA')


# ============================================================================
# COLOR UTILITIES
# ============================================================================

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend_colors(
    color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float
) -> tuple[int, int, int]:
    """Blend two colors by ratio (0.0 = color1, 1.0 = color2)."""
    return tuple(int(c1 + (c2 - c1) * ratio) for c1, c2 in zip(color1, color2))


def adjust_brightness(
    color: tuple[int, int, int], factor: float
) -> tuple[int, int, int]:
    """Adjust color brightness (factor > 1 = lighter, < 1 = darker)."""
    h, l, s = colorsys.rgb_to_hls(color[0] / 255, color[1] / 255, color[2] / 255)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))


# ============================================================================
# DRAWING UTILITIES
# ============================================================================

def create_rounded_mask(size: int, radius: float) -> Image.Image:
    """
    Create an anti-aliased rounded rectangle mask.
    
    Args:
        size: Image size in pixels
        radius: Corner radius as fraction of size (0-0.5)
    
    Returns:
        Grayscale mask image
    """
    # Create at 4x resolution for anti-aliasing
    scale = 4
    large_size = size * scale
    large_radius = int(radius * size * scale)

    mask = Image.new("L", (large_size, large_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (large_size - 1, large_size - 1)],
        radius=large_radius,
        fill=255,
    )

    # Downscale with anti-aliasing
    return mask.resize((size, size), Image.Resampling.LANCZOS)


def create_gradient(
    size: int,
    color1: tuple[int, int, int],
    color2: tuple[int, int, int],
    direction: Literal["diagonal", "vertical", "horizontal"] = "diagonal",
) -> Image.Image:
    """
    Create a smooth gradient image.
    
    Args:
        size: Image size in pixels
        color1: Starting color (RGB)
        color2: Ending color (RGB)
        direction: Gradient direction
    
    Returns:
        RGBA gradient image
    """
    img = Image.new("RGBA", (size, size))
    pixels = img.load()

    for y in range(size):
        for x in range(size):
            if direction == "diagonal":
                ratio = (x + y) / (2 * size - 2)
            elif direction == "vertical":
                ratio = y / (size - 1)
            else:  # horizontal
                ratio = x / (size - 1)

            color = blend_colors(color1, color2, ratio)
            pixels[x, y] = (*color, 255)

    return img


def add_noise(img: Image.Image, intensity: float) -> Image.Image:
    """
    Add subtle noise/grain texture to an image.
    
    Args:
        img: Source image
        intensity: Noise intensity (0-1)
    
    Returns:
        Image with noise applied
    """
    import random

    if intensity <= 0:
        return img

    width, height = img.size
    noise_img = Image.new("RGBA", (width, height))
    pixels = noise_img.load()

    for y in range(height):
        for x in range(width):
            noise = int((random.random() - 0.5) * 255 * intensity)
            gray = 128 + noise
            alpha = int(30 * intensity)
            pixels[x, y] = (gray, gray, gray, alpha)

    return Image.alpha_composite(img, noise_img)


# ============================================================================
# EFFECT LAYERS
# ============================================================================

def apply_drop_shadow(
    img: Image.Image, intensity: float, offset: float = 0.05, blur: float = 0.15
) -> Image.Image:
    """
    Apply drop shadow effect to the image.
    
    Args:
        img: Source image with transparency
        intensity: Shadow opacity (0-1)
        offset: Shadow offset as fraction of size
        blur: Shadow blur as fraction of size
    
    Returns:
        Image with drop shadow
    """
    if intensity <= 0:
        return img

    size = img.size[0]
    shadow_offset = int(size * offset * intensity)
    shadow_blur = int(size * blur * intensity)

    # Create shadow from alpha channel
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_alpha = img.split()[3]

    # Offset and blur the shadow
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_color = Image.new("RGBA", img.size, (0, 0, 0, int(255 * 0.3 * intensity)))
    shadow_layer.paste(shadow_color, (0, shadow_offset), shadow_alpha)

    if shadow_blur > 0:
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))

    # Composite: shadow behind original
    result = Image.alpha_composite(shadow_layer, img)
    return result


def apply_highlight(img: Image.Image, intensity: float) -> Image.Image:
    """
    Apply top highlight gradient effect.
    
    Args:
        img: Source image
        intensity: Highlight opacity (0-1)
    
    Returns:
        Image with highlight overlay
    """
    if intensity <= 0:
        return img

    size = img.size[0]

    # Create highlight gradient (bright at top, dark at bottom)
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = highlight.load()

    for y in range(size):
        for x in range(size):
            ratio = y / (size - 1)
            if ratio < 0.5:
                # Top half: white highlight
                alpha = int((1 - ratio * 2) * 80 * intensity)
                pixels[x, y] = (255, 255, 255, alpha)
            else:
                # Bottom half: slight darken
                alpha = int((ratio - 0.5) * 2 * 40 * intensity)
                pixels[x, y] = (0, 0, 0, alpha)

    return Image.alpha_composite(img, highlight)


def apply_inner_glow(img: Image.Image, intensity: float, mask: Image.Image) -> Image.Image:
    """
    Apply inner glow/ambient occlusion effect.
    
    Args:
        img: Source image
        intensity: Glow intensity (0-1)
        mask: Rounded rectangle mask
    
    Returns:
        Image with inner glow
    """
    if intensity <= 0:
        return img

    size = img.size[0]

    # Create radial gradient (bright center, dark edges)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = glow.load()

    center_x, center_y = size // 2, int(size * 0.4)  # Slightly above center

    for y in range(size):
        for x in range(size):
            # Distance from center (normalized)
            dx = (x - center_x) / (size * 0.5)
            dy = (y - center_y) / (size * 0.5)
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 1.0:
                # Inner bright area
                alpha = int((1 - distance) * 60 * intensity)
                pixels[x, y] = (255, 255, 255, alpha)
            else:
                # Outer dark area
                alpha = int(min(1, distance - 1) * 40 * intensity)
                pixels[x, y] = (0, 0, 0, alpha)

    # Apply mask
    glow.putalpha(
        Image.composite(glow.split()[3], Image.new("L", (size, size), 0), mask)
    )

    return Image.alpha_composite(img, glow)


# ============================================================================
# CONTENT RENDERING
# ============================================================================

def get_system_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | None:
    """
    Get a system font for text rendering.
    
    Args:
        size: Font size in pixels
        bold: Whether to use bold weight
    
    Returns:
        Font object or None if not found
    """
    # Common font paths by OS
    font_paths = [
        # macOS
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                continue

    # Fallback to default
    return ImageFont.load_default()


def render_letter(
    img: Image.Image,
    letter: str,
    color: tuple[int, int, int],
    shadow_intensity: float = 0.3,
) -> Image.Image:
    """
    Render a letter/monogram on the favicon.
    
    Args:
        img: Background image
        letter: Letter(s) to render
        color: Text color (RGB)
        shadow_intensity: Text shadow intensity
    
    Returns:
        Image with letter rendered
    """
    size = img.size[0]
    result = img.copy()
    draw = ImageDraw.Draw(result)

    # Font size based on letter count
    font_size = int(size * (0.4 if len(letter) > 1 else 0.55))
    font = get_system_font(font_size)

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), letter.upper(), font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center position with optical adjustment
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1] - int(size * 0.02)

    # Draw shadow first
    if shadow_intensity > 0 and size >= 32:
        shadow_offset = max(1, int(size * 0.02))
        shadow_color = (0, 0, 0, int(255 * 0.3 * shadow_intensity))
        
        # Create shadow layer
        shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text(
            (x, y + shadow_offset),
            letter.upper(),
            font=font,
            fill=shadow_color,
        )
        
        # Blur shadow
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(size * 0.02))
        result = Image.alpha_composite(result, shadow_layer)
        draw = ImageDraw.Draw(result)

    # Draw main text
    draw.text((x, y), letter.upper(), font=font, fill=(*color, 255))

    return result


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_favicon(
    size: int,
    letter: str = "A",
    bg_color: str = "#6366f1",
    bg_color2: str | None = None,
    fg_color: str = "#ffffff",
    use_gradient: bool = True,
    shadow_intensity: float = 0.4,
    highlight_intensity: float = 0.25,
    inner_glow_intensity: float = 0.0,
    noise_intensity: float = 0.0,
    corner_radius: float = 0.22,
) -> Image.Image:
    """
    Generate a professional-quality favicon.
    
    Args:
        size: Output size in pixels
        letter: Letter/monogram to display
        bg_color: Background color (hex)
        bg_color2: Gradient end color (hex), None for solid
        fg_color: Foreground/text color (hex)
        use_gradient: Whether to use gradient background
        shadow_intensity: Drop shadow intensity (0-1)
        highlight_intensity: Top highlight intensity (0-1)
        inner_glow_intensity: Inner glow intensity (0-1)
        noise_intensity: Noise/grain intensity (0-1)
        corner_radius: Corner radius as fraction (0-0.5)
    
    Returns:
        Generated favicon as RGBA Image
    """
    bg_rgb = hex_to_rgb(bg_color)
    bg2_rgb = hex_to_rgb(bg_color2) if bg_color2 else bg_rgb
    fg_rgb = hex_to_rgb(fg_color)

    # Create base with transparency
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Create rounded mask
    mask = create_rounded_mask(size, corner_radius)

    # Create background (gradient or solid)
    if use_gradient and bg_color2:
        background = create_gradient(size, bg_rgb, bg2_rgb, "diagonal")
    else:
        background = Image.new("RGBA", (size, size), (*bg_rgb, 255))

    # Apply mask to background
    background.putalpha(mask)

    # Apply effects in order
    img = Image.alpha_composite(img, background)

    # Inner glow
    if inner_glow_intensity > 0 and size >= 32:
        img = apply_inner_glow(img, inner_glow_intensity, mask)

    # Highlight
    if highlight_intensity > 0 and size >= 32:
        highlight_layer = apply_highlight(
            Image.new("RGBA", (size, size), (0, 0, 0, 0)), highlight_intensity
        )
        highlight_layer.putalpha(
            Image.composite(highlight_layer.split()[3], Image.new("L", (size, size), 0), mask)
        )
        img = Image.alpha_composite(img, highlight_layer)

    # Noise
    if noise_intensity > 0 and size >= 64:
        img = add_noise(img, noise_intensity)

    # Render letter
    img = render_letter(img, letter, fg_rgb, shadow_intensity)

    # Drop shadow (applied last, affects whole icon)
    if shadow_intensity > 0 and size >= 32:
        # Create a version with shadow
        shadow_canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        img = apply_drop_shadow(img, shadow_intensity * 0.5)

    return img


def generate_favicon_suite(
    output_dir: str,
    letter: str = "A",
    style: str | None = None,
    **kwargs,
) -> list[str]:
    """
    Generate a complete favicon suite with all standard sizes.
    
    Args:
        output_dir: Directory to save files
        letter: Letter/monogram to display
        style: Template name to use (overrides other settings)
        **kwargs: Override settings (bg_color, fg_color, etc.)
    
    Returns:
        List of generated file paths
    """
    # Apply template if specified
    settings = {}
    if style and style in TEMPLATES:
        template = TEMPLATES[style]
        settings = {
            "bg_color": template["bg"],
            "bg_color2": template["bg2"],
            "fg_color": template["fg"],
            "use_gradient": template["gradient"],
            "shadow_intensity": template["shadow"],
            "highlight_intensity": template["highlight"],
            "inner_glow_intensity": template["inner_glow"],
            "noise_intensity": template["noise"],
            "corner_radius": template["corner_radius"],
        }

    # Override with provided kwargs
    settings.update({k: v for k, v in kwargs.items() if v is not None})

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Generate each size
    for size in SIZES:
        favicon = generate_favicon(size, letter, **settings)

        if size == 180:
            filename = "apple-touch-icon.png"
        else:
            filename = f"favicon-{size}x{size}.png"

        filepath = os.path.join(output_dir, filename)
        favicon.save(filepath, "PNG")
        generated_files.append(filepath)
        print(f"  ✓ Generated {filename}")

    # Generate ICO file (16x16 + 32x32)
    ico_path = os.path.join(output_dir, "favicon.ico")
    create_ico_file(
        ico_path,
        [
            generate_favicon(16, letter, **settings),
            generate_favicon(32, letter, **settings),
        ],
    )
    generated_files.append(ico_path)
    print(f"  ✓ Generated favicon.ico")

    # Generate SVG
    svg_path = os.path.join(output_dir, "favicon.svg")
    create_svg_file(svg_path, letter, settings)
    generated_files.append(svg_path)
    print(f"  ✓ Generated favicon.svg")

    return generated_files


def generate_lucide_favicon_suite(
    output_dir: str,
    icon_name: str,
    style: str | None = None,
    **kwargs,
) -> list[str]:
    """
    Generate a complete favicon suite using a Lucide icon.
    
    Args:
        output_dir: Directory to save files
        icon_name: Lucide icon name (e.g., 'package-plus', 'rocket')
        style: Template name to use (overrides other settings)
        **kwargs: Override settings (bg_color, fg_color, etc.)
    
    Returns:
        List of generated file paths
    """
    # Apply template if specified
    settings = {}
    if style and style in TEMPLATES:
        template = TEMPLATES[style]
        settings = {
            "bg_color": template["bg"],
            "bg_color2": template["bg2"],
            "fg_color": template["fg"],
            "corner_radius": template["corner_radius"],
        }

    # Override with provided kwargs
    settings.update({k: v for k, v in kwargs.items() if v is not None})

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Generate each size
    for size in SIZES:
        favicon = render_lucide_icon(icon_name, size, **settings)
        if favicon is None:
            print(f"  ✗ Failed to generate {size}x{size} (cairosvg error)")
            continue

        if size == 180:
            filename = "apple-touch-icon.png"
        else:
            filename = f"favicon-{size}x{size}.png"

        filepath = os.path.join(output_dir, filename)
        favicon.save(filepath, "PNG")
        generated_files.append(filepath)
        print(f"  ✓ Generated {filename}")

    # Generate ICO file (16x16 + 32x32)
    ico_path = os.path.join(output_dir, "favicon.ico")
    ico_images = [
        render_lucide_icon(icon_name, 16, **settings),
        render_lucide_icon(icon_name, 32, **settings),
    ]
    if all(ico_images):
        create_ico_file(ico_path, ico_images)
        generated_files.append(ico_path)
        print(f"  ✓ Generated favicon.ico")

    # Generate SVG with actual Lucide paths
    svg_path = os.path.join(output_dir, "favicon.svg")
    create_lucide_svg_file(svg_path, icon_name, settings)
    generated_files.append(svg_path)
    print(f"  ✓ Generated favicon.svg")

    return generated_files


def create_lucide_svg_file(filepath: str, icon_name: str, settings: dict) -> None:
    """
    Create an SVG favicon file using Lucide icon paths.
    
    Args:
        filepath: Output SVG file path
        icon_name: Lucide icon name
        settings: Style settings dict
    """
    if icon_name not in LUCIDE_ICONS:
        return
    
    bg_color = settings.get("bg_color", "#6366f1")
    bg_color2 = settings.get("bg_color2", bg_color)
    fg_color = settings.get("fg_color", "#ffffff")
    corner_radius = settings.get("corner_radius", 0.22)

    rx = corner_radius * 32
    icon_paths = "\n    ".join(LUCIDE_ICONS[icon_name])
    
    # Scale: 24x24 Lucide → 32x32 favicon with padding
    # offset = 32 * 0.15 = 4.8, scale = (32 * 0.7) / 24 = 0.933
    scale = 0.933
    offset = 4.8

    if bg_color2 and bg_color2 != bg_color:
        gradient_def = f'''<defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="{bg_color2}"/>
    </linearGradient>
  </defs>'''
        fill = "url(#bg)"
    else:
        gradient_def = ""
        fill = bg_color

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  {gradient_def}
  <rect width="32" height="32" rx="{rx:.1f}" fill="{fill}"/>
  <g transform="translate({offset}, {offset}) scale({scale})" 
     stroke="{fg_color}" stroke-width="2" fill="none" 
     stroke-linecap="round" stroke-linejoin="round">
    {icon_paths}
  </g>
</svg>'''

    with open(filepath, "w") as f:
        f.write(svg)


def create_ico_file(filepath: str, images: list[Image.Image]) -> None:
    """
    Create an ICO file from multiple PNG images.
    
    Args:
        filepath: Output ICO file path
        images: List of PIL Images (should include 16x16 and 32x32)
    """
    # ICO format implementation
    icon_dir = BytesIO()

    # ICONDIR header
    icon_dir.write(struct.pack("<HHH", 0, 1, len(images)))

    image_data = []
    offset = 6 + len(images) * 16  # Header + entries

    for img in images:
        # Convert to RGBA if needed
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Save as PNG
        png_data = BytesIO()
        img.save(png_data, "PNG")
        png_bytes = png_data.getvalue()
        image_data.append(png_bytes)

        # ICONDIRENTRY
        width = img.size[0] if img.size[0] < 256 else 0
        height = img.size[1] if img.size[1] < 256 else 0
        icon_dir.write(
            struct.pack(
                "<BBBBHHII",
                width,  # Width
                height,  # Height
                0,  # Color palette
                0,  # Reserved
                1,  # Color planes
                32,  # Bits per pixel
                len(png_bytes),  # Size of image data
                offset,  # Offset to image data
            )
        )
        offset += len(png_bytes)

    # Write image data
    for data in image_data:
        icon_dir.write(data)

    with open(filepath, "wb") as f:
        f.write(icon_dir.getvalue())


def create_svg_file(filepath: str, letter: str, settings: dict) -> None:
    """
    Create an SVG favicon file.
    
    Args:
        filepath: Output SVG file path
        letter: Letter to display
        settings: Style settings dict
    """
    bg_color = settings.get("bg_color", "#6366f1")
    bg_color2 = settings.get("bg_color2", bg_color)
    fg_color = settings.get("fg_color", "#ffffff")
    use_gradient = settings.get("use_gradient", True)
    corner_radius = settings.get("corner_radius", 0.22)

    rx = corner_radius * 16  # Based on 32x32 viewBox

    gradient_def = ""
    fill = bg_color

    if use_gradient and bg_color2 != bg_color:
        gradient_def = f"""
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="{bg_color2}"/>
    </linearGradient>
  </defs>"""
        fill = "url(#bg)"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{gradient_def}
  <rect width="32" height="32" rx="{rx:.1f}" fill="{fill}"/>
  <text x="16" y="16" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="18" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="{fg_color}">{letter.upper()}</text>
</svg>"""

    with open(filepath, "w") as f:
        f.write(svg)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Command-line interface for favicon generation."""
    parser = argparse.ArgumentParser(
        description="Generate professional-quality favicons with advanced effects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --letter A --bg "#6366f1" --output ./favicons/
  %(prog)s --letter T --style vibrant --output ./public/
  %(prog)s --lucide package-plus --bg "#f97316" --bg2 "#ef4444" --output ./public/
  %(prog)s --lucide rocket --style vibrant --output ./icons/

Available styles: modern, vibrant, minimal, glass, neon, warm, forest, mono
Available icons: """ + ", ".join(LUCIDE_ICONS.keys()) + """
        """,
    )

    parser.add_argument(
        "--letter", "-l", help="Letter or monogram to display"
    )
    parser.add_argument(
        "--lucide", "-i", 
        choices=list(LUCIDE_ICONS.keys()),
        help="Use a Lucide icon (requires cairosvg: pip install cairosvg)"
    )
    parser.add_argument(
        "--bg", default="#6366f1", help="Background color in hex (default: #6366f1)"
    )
    parser.add_argument(
        "--bg2", help="Gradient end color in hex (default: same as --bg)"
    )
    parser.add_argument(
        "--fg", default="#ffffff", help="Foreground/text color (default: #ffffff)"
    )
    parser.add_argument(
        "--style",
        "-s",
        choices=list(TEMPLATES.keys()),
        help="Use a predefined style template",
    )
    parser.add_argument(
        "--output", "-o", default="./favicons", help="Output directory (default: ./favicons)"
    )
    parser.add_argument(
        "--no-gradient", action="store_true", help="Disable gradient background"
    )
    parser.add_argument(
        "--shadow", type=float, default=0.4, help="Shadow intensity 0-1 (default: 0.4)"
    )
    parser.add_argument(
        "--highlight", type=float, default=0.25, help="Highlight intensity 0-1 (default: 0.25)"
    )
    parser.add_argument(
        "--glow", type=float, default=0.0, help="Inner glow intensity 0-1 (default: 0)"
    )
    parser.add_argument(
        "--noise", type=float, default=0.0, help="Noise intensity 0-1 (default: 0)"
    )
    parser.add_argument(
        "--radius", type=float, default=0.22, help="Corner radius 0-0.5 (default: 0.22)"
    )

    args = parser.parse_args()

    # Validate: must have either --letter or --lucide
    if not args.letter and not args.lucide:
        args.letter = "A"  # Default
    
    print(f"\n🎨 Pro Favicon Generator")
    print(f"{'=' * 40}")
    
    if args.lucide:
        print(f"Lucide Icon: {args.lucide}")
        if not HAS_CAIROSVG:
            print("\n⚠️  Warning: cairosvg not installed!")
            print("   Install with: pip install cairosvg")
            print("   Also need native cairo: brew install cairo (macOS)")
            print("   Falling back to letter mode...\n")
            args.letter = args.lucide[0].upper()
            args.lucide = None
    else:
        print(f"Letter: {args.letter.upper()}")
    
    if args.style:
        print(f"Style: {args.style}")
    else:
        print(f"Background: {args.bg}" + (f" → {args.bg2}" if args.bg2 else ""))
        print(f"Foreground: {args.fg}")
    print(f"Output: {args.output}")
    print(f"{'=' * 40}\n")

    if args.lucide and HAS_CAIROSVG:
        # Generate using Lucide icon with cairosvg
        files = generate_lucide_favicon_suite(
            output_dir=args.output,
            icon_name=args.lucide,
            style=args.style,
            bg_color=args.bg if not args.style else None,
            bg_color2=args.bg2 if not args.style else None,
            fg_color=args.fg if not args.style else None,
            corner_radius=args.radius if not args.style else None,
        )
    else:
        # Generate using letter
        files = generate_favicon_suite(
            output_dir=args.output,
            letter=args.letter,
            style=args.style,
            bg_color=args.bg if not args.style else None,
            bg_color2=args.bg2 if not args.style else None,
            fg_color=args.fg if not args.style else None,
            use_gradient=not args.no_gradient if not args.style else None,
            shadow_intensity=args.shadow if not args.style else None,
            highlight_intensity=args.highlight if not args.style else None,
            inner_glow_intensity=args.glow if not args.style else None,
            noise_intensity=args.noise if not args.style else None,
            corner_radius=args.radius if not args.style else None,
        )

    print(f"\n✅ Generated {len(files)} files in {args.output}/")
    print("\nNext steps:")
    print("  1. Copy files to your project's public/ directory")
    print("  2. Add favicon links to your HTML <head>")
    print("  3. Update manifest.json if using PWA")


if __name__ == "__main__":
    main()

