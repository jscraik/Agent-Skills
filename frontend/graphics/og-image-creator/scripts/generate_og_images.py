#!/usr/bin/env python3
"""
Generate OG images for routes based on codebase analysis.

Usage:
    python generate_og_images.py [project_path]

Requirements:
    pip install playwright
    playwright install chromium

Input:
    og-analysis.json (from analyze_codebase.py)

Output:
    OG images in public/og/ directory
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from playwright.async_api import async_playwright

# OG image standard dimensions
OG_WIDTH = 1200
OG_HEIGHT = 630

def get_layout_template(page_type: str) -> str:
    """Get HTML template based on page type."""

    # Different templates for different page types
    templates = {
        'landing': '''
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 80px;">
                <h1 style="font-size: 72px; font-weight: 800; margin: 0 0 30px 0; line-height: 1.1; max-width: 900px;">{{title}}</h1>
                {{#description}}
                <p style="font-size: 32px; opacity: 0.8; margin: 0; max-width: 800px;">{{description}}</p>
                {{/description}}
            </div>
        ''',

        'article': '''
            <div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; padding: 60px 80px;">
                <div>
                    <div style="font-size: 20px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.6; margin-bottom: 30px;">Article</div>
                    <h1 style="font-size: 56px; font-weight: 700; margin: 0 0 20px 0; line-height: 1.2; max-width: 1000px;">{{title}}</h1>
                    {{#description}}
                    <p style="font-size: 28px; opacity: 0.7; margin: 0; max-width: 900px; line-height: 1.4;">{{description}}</p>
                    {{/description}}
                </div>
                {{#logo}}
                <div style="display: flex; align-items: center;">
                    <img src="{{logo}}" style="height: 40px;" />
                </div>
                {{/logo}}
            </div>
        ''',

        'product': '''
            <div style="display: flex; align-items: center; height: 100%; padding: 80px;">
                <div style="flex: 1;">
                    <h1 style="font-size: 64px; font-weight: 800; margin: 0 0 30px 0; line-height: 1.1;">{{title}}</h1>
                    {{#description}}
                    <p style="font-size: 28px; opacity: 0.8; margin: 0; line-height: 1.4;">{{description}}</p>
                    {{/description}}
                </div>
            </div>
        ''',

        'documentation': '''
            <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 60px 80px;">
                <div style="font-size: 20px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.6; margin-bottom: 20px;">Documentation</div>
                <h1 style="font-size: 60px; font-weight: 700; margin: 0 0 25px 0; line-height: 1.2; max-width: 1000px;">{{title}}</h1>
                {{#description}}
                <p style="font-size: 26px; opacity: 0.75; margin: 0; max-width: 900px; line-height: 1.4;">{{description}}</p>
                {{/description}}
            </div>
        ''',

        'about': '''
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 80px;">
                {{#logo}}
                <img src="{{logo}}" style="height: 100px; margin-bottom: 50px;" />
                {{/logo}}
                <h1 style="font-size: 64px; font-weight: 700; margin: 0 0 30px 0; line-height: 1.1; max-width: 900px;">{{title}}</h1>
                {{#description}}
                <p style="font-size: 30px; opacity: 0.8; margin: 0; max-width: 800px;">{{description}}</p>
                {{/description}}
            </div>
        ''',

        'general': '''
            <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 80px;">
                <h1 style="font-size: 64px; font-weight: 700; margin: 0 0 30px 0; line-height: 1.2; max-width: 1000px;">{{title}}</h1>
                {{#description}}
                <p style="font-size: 28px; opacity: 0.8; margin: 0; max-width: 900px; line-height: 1.4;">{{description}}</p>
                {{/description}}
            </div>
        '''
    }

    return templates.get(page_type, templates['general'])

def simple_mustache_render(template: str, data: Dict) -> str:
    """Simple mustache-like template rendering."""
    result = template

    # Replace {{variable}}
    for key, value in data.items():
        if value:
            result = result.replace(f'{{{{{key}}}}}', str(value))

    # Handle {{#variable}}...{{/variable}} blocks
    import re
    for key in data.keys():
        pattern = f'{{{{#{key}}}}}(.*?){{{{/{key}}}}}'
        if data.get(key):
            # Keep the content, remove the tags
            result = re.sub(pattern, r'\1', result, flags=re.DOTALL)
        else:
            # Remove the entire block
            result = re.sub(pattern, '', result, flags=re.DOTALL)

    return result

def generate_html(route: Dict, brand: Dict) -> str:
    """Generate complete HTML for a route's OG image."""

    # Get template for page type
    template = get_layout_template(route['type'])

    # Prepare data
    title = route['metadata'].get('title') or route['path'].strip('/').replace('-', ' ').title() or 'Home'
    description = route['metadata'].get('description', '')
    logo = brand.get('logo', '')

    # If logo is relative path, we need to handle it
    logo_url = ''
    if logo:
        # For local files, we'll use absolute path or data URI later
        logo_url = logo

    template_data = {
        'title': title,
        'description': description,
        'logo': logo_url
    }

    content_html = simple_mustache_render(template, template_data)

    # Determine colors
    primary_color = brand['colors'][0] if brand['colors'] else '#000000'
    background_color = '#ffffff'
    text_color = '#000000'

    # If primary color is dark, use it as background
    if is_dark_color(primary_color):
        background_color = primary_color
        text_color = '#ffffff'
    else:
        # Light primary color - use as accent or gradient
        background_color = f'linear-gradient(135deg, {primary_color}10 0%, {primary_color}30 100%)'

    # Determine font
    font_family = brand['fonts'][0] if brand['fonts'] else 'system-ui, -apple-system, sans-serif'

    # Build complete HTML
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                width: {OG_WIDTH}px;
                height: {OG_HEIGHT}px;
                background: {background_color};
                color: {text_color};
                font-family: {font_family};
                overflow: hidden;
            }}

            .container {{
                width: 100%;
                height: 100%;
                position: relative;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {content_html}
        </div>
    </body>
    </html>
    '''

    return html

def is_dark_color(hex_color: str) -> bool:
    """Determine if a hex color is dark."""
    hex_color = hex_color.lstrip('#')

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        return luminance < 0.5
    except:
        return False

async def generate_og_image(html: str, output_path: Path):
    """Generate OG image from HTML using Playwright."""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': OG_WIDTH, 'height': OG_HEIGHT})

        await page.set_content(html)

        # Wait for any fonts or images to load
        await page.wait_for_timeout(500)

        # Take screenshot
        await page.screenshot(path=output_path, type='png')

        await browser.close()

async def generate_all_images(project_path: Path, analysis: Dict):
    """Generate OG images for all routes."""

    routes = analysis['routes']
    brand = analysis['brand']

    # Create output directory
    og_dir = project_path / "public" / "og"
    og_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(routes)} OG images...")
    print(f"Output directory: {og_dir}")
    print("-" * 50)

    for i, route in enumerate(routes, 1):
        # Generate filename from route path
        filename = route['path'].strip('/').replace('/', '-') or 'home'
        filename = f"{filename}.png"

        output_path = og_dir / filename

        print(f"[{i}/{len(routes)}] {route['path']} ({route['type']}) -> {filename}")

        # Generate HTML
        html = generate_html(route, brand)

        # Generate image
        try:
            await generate_og_image(html, output_path)
            print(f"  ✓ Generated: {output_path.relative_to(project_path)}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("-" * 50)
    print(f"Generated {len(routes)} OG images in {og_dir.relative_to(project_path)}")

def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    if not project_path.exists():
        print(f"Error: Path {project_path} does not exist")
        sys.exit(1)

    # Load analysis
    analysis_file = project_path / "og-analysis.json"
    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found. Run analyze_codebase.py first.")
        sys.exit(1)

    with open(analysis_file, 'r') as f:
        analysis = json.load(f)

    print(f"Loaded analysis from: {analysis_file}")
    print(f"Framework: {analysis['framework']}")
    print(f"Routes: {len(analysis['routes'])}")
    print()

    # Generate images
    asyncio.run(generate_all_images(project_path, analysis))

    # Print next steps
    print("\nNext steps:")
    print("1. Review generated images in public/og/")
    print("2. Add OG image meta tags to your pages:")
    print('   <meta property="og:image" content="/og/[route].png" />')
    print("3. Test with opengraph.xyz or LinkedIn Post Inspector")

if __name__ == '__main__':
    main()
