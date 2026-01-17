#!/usr/bin/env python3
"""
Analyze a codebase to discover routes, brand identity, and prepare for OG image generation.

Usage:
    python analyze_codebase.py [project_path]

Output:
    analysis.json with routes, brand colors, fonts, logo paths, and page categorization
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def detect_framework(project_path: Path) -> str:
    """Detect the framework used in the project."""
    package_json = project_path / "package.json"

    if not package_json.exists():
        return "unknown"

    with open(package_json, 'r') as f:
        try:
            pkg = json.load(f)
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

            if 'next' in deps:
                return 'nextjs'
            elif 'astro' in deps:
                return 'astro'
            elif 'react-router-dom' in deps or 'react-router' in deps:
                return 'react-router'
            elif 'react' in deps:
                return 'react'

        except json.JSONDecodeError:
            pass

    return "unknown"

def find_nextjs_routes(project_path: Path) -> List[Dict]:
    """Find routes in a Next.js project (app router and pages router)."""
    routes = []

    # App router
    app_dir = project_path / "app"
    if app_dir.exists():
        for page_file in app_dir.rglob("page.{tsx,ts,jsx,js}"):
            route_path = page_file.parent.relative_to(app_dir)
            route_str = "/" + str(route_path).replace("\\", "/")

            # Clean up route groups and handle root
            route_str = re.sub(r'/\([^)]+\)', '', route_str)
            route_str = re.sub(r'/+', '/', route_str)
            if route_str == "/.":
                route_str = "/"

            metadata = extract_metadata_from_file(page_file)
            page_type = categorize_page(route_str, metadata)

            routes.append({
                "path": route_str,
                "file": str(page_file.relative_to(project_path)),
                "type": page_type,
                "metadata": metadata,
                "router": "app"
            })

    # Pages router
    pages_dir = project_path / "pages"
    if pages_dir.exists():
        for page_file in pages_dir.rglob("*.{tsx,ts,jsx,js}"):
            # Skip _app, _document, api routes
            if page_file.name.startswith('_') or 'api' in page_file.parts:
                continue

            route_path = page_file.relative_to(pages_dir)
            route_str = "/" + str(route_path.with_suffix('')).replace("\\", "/")

            if route_str.endswith("/index"):
                route_str = route_str[:-6] or "/"

            metadata = extract_metadata_from_file(page_file)
            page_type = categorize_page(route_str, metadata)

            routes.append({
                "path": route_str,
                "file": str(page_file.relative_to(project_path)),
                "type": page_type,
                "metadata": metadata,
                "router": "pages"
            })

    return routes

def find_astro_routes(project_path: Path) -> List[Dict]:
    """Find routes in an Astro project."""
    routes = []
    pages_dir = project_path / "src" / "pages"

    if not pages_dir.exists():
        return routes

    for page_file in pages_dir.rglob("*.{astro,md,mdx}"):
        route_path = page_file.relative_to(pages_dir)
        route_str = "/" + str(route_path.with_suffix('')).replace("\\", "/")

        if route_str.endswith("/index"):
            route_str = route_str[:-6] or "/"

        metadata = extract_metadata_from_file(page_file)
        page_type = categorize_page(route_str, metadata)

        routes.append({
            "path": route_str,
            "file": str(page_file.relative_to(project_path)),
            "type": page_type,
            "metadata": metadata,
            "framework": "astro"
        })

    return routes

def find_react_routes(project_path: Path) -> List[Dict]:
    """Find routes in a React SPA (best effort)."""
    routes = []

    # Look for common route definition patterns
    src_dir = project_path / "src"
    if not src_dir.exists():
        return routes

    for file_path in src_dir.rglob("*.{tsx,ts,jsx,js}"):
        content = file_path.read_text(errors='ignore')

        # Look for react-router Route definitions
        route_matches = re.findall(r'<Route\s+path=["\']([^"\']+)["\']', content)
        for route_path in route_matches:
            if route_path and not route_path.startswith(':'):
                routes.append({
                    "path": route_path,
                    "file": str(file_path.relative_to(project_path)),
                    "type": categorize_page(route_path, {}),
                    "metadata": {},
                    "framework": "react-router"
                })

    # Deduplicate
    seen = set()
    unique_routes = []
    for route in routes:
        if route['path'] not in seen:
            seen.add(route['path'])
            unique_routes.append(route)

    return unique_routes

def extract_metadata_from_file(file_path: Path) -> Dict:
    """Extract title and description from a file."""
    metadata = {}

    try:
        content = file_path.read_text(errors='ignore')

        # Look for title
        title_patterns = [
            r'<title>([^<]+)</title>',
            r'title:\s*["\']([^"\']+)["\']',
            r'<h1[^>]*>([^<]+)</h1>',
            r'title:\s*[\'"]([^\'"]+)[\'"]',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata['title'] = match.group(1).strip()
                break

        # Look for description
        desc_patterns = [
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
            r'description:\s*["\']([^"\']+)["\']',
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata['description'] = match.group(1).strip()
                break

    except Exception:
        pass

    return metadata

def categorize_page(route: str, metadata: Dict) -> str:
    """Categorize a page based on its route and metadata."""
    route_lower = route.lower()
    title_lower = metadata.get('title', '').lower()

    # Homepage
    if route == '/' or route == '/index':
        return 'landing'

    # Common page types
    if any(x in route_lower for x in ['/blog', '/post', '/article', '/news']):
        return 'article'

    if any(x in route_lower for x in ['/product', '/shop', '/store', '/item']):
        return 'product'

    if any(x in route_lower for x in ['/doc', '/guide', '/api', '/reference']):
        return 'documentation'

    if any(x in route_lower for x in ['/about', '/team', '/contact', '/company']):
        return 'about'

    # Check title for hints
    if any(x in title_lower for x in ['blog', 'article', 'post']):
        return 'article'

    return 'general'

def extract_brand_colors(project_path: Path) -> List[str]:
    """Extract brand colors from CSS, Tailwind config, or other sources."""
    colors = []

    # Check Tailwind config
    tailwind_configs = [
        project_path / "tailwind.config.js",
        project_path / "tailwind.config.ts",
    ]

    for config_file in tailwind_configs:
        if config_file.exists():
            content = config_file.read_text(errors='ignore')

            # Extract hex colors
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
            colors.extend(hex_colors)

            # Extract color names and their values
            color_matches = re.findall(r'(\w+):\s*["\']?(#[0-9a-fA-F]{6})["\']?', content)
            if color_matches:
                colors.extend([color[1] for color in color_matches])

    # Check CSS files for custom properties
    for css_file in project_path.rglob("*.css"):
        if 'node_modules' in str(css_file):
            continue

        content = css_file.read_text(errors='ignore')
        hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
        colors.extend(hex_colors)

    # Deduplicate and return top colors
    unique_colors = list(dict.fromkeys(colors))
    return unique_colors[:10]  # Return top 10 unique colors

def extract_fonts(project_path: Path) -> List[str]:
    """Extract font families used in the project."""
    fonts = []

    # Check CSS files
    for css_file in project_path.rglob("*.css"):
        if 'node_modules' in str(css_file):
            continue

        content = css_file.read_text(errors='ignore')

        # Look for font-family declarations
        font_matches = re.findall(r'font-family:\s*([^;]+);', content)
        fonts.extend(font_matches)

    # Check Tailwind config
    tailwind_configs = [
        project_path / "tailwind.config.js",
        project_path / "tailwind.config.ts",
    ]

    for config_file in tailwind_configs:
        if config_file.exists():
            content = config_file.read_text(errors='ignore')
            font_matches = re.findall(r'fontFamily:\s*{([^}]+)}', content, re.DOTALL)
            if font_matches:
                fonts.extend(font_matches)

    # Clean and deduplicate
    cleaned_fonts = []
    for font in fonts:
        # Remove quotes, brackets, and clean up
        cleaned = re.sub(r'[\[\]"\']', '', font)
        cleaned = cleaned.split(',')[0].strip()
        if cleaned and cleaned not in cleaned_fonts:
            cleaned_fonts.append(cleaned)

    return cleaned_fonts[:5]  # Return top 5 fonts

def find_logo(project_path: Path) -> Optional[str]:
    """Find the logo file in the project."""
    common_logo_paths = [
        "public/logo.svg",
        "public/logo.png",
        "public/images/logo.svg",
        "public/images/logo.png",
        "public/assets/logo.svg",
        "public/assets/logo.png",
        "src/assets/logo.svg",
        "src/assets/logo.png",
        "assets/logo.svg",
        "assets/logo.png",
    ]

    for logo_path in common_logo_paths:
        full_path = project_path / logo_path
        if full_path.exists():
            return logo_path

    # Search for logo files
    for ext in ['.svg', '.png', '.jpg']:
        for logo_file in project_path.rglob(f"*logo*{ext}"):
            if 'node_modules' not in str(logo_file):
                return str(logo_file.relative_to(project_path))

    return None

def analyze_codebase(project_path: Path) -> Dict:
    """Perform full codebase analysis."""
    framework = detect_framework(project_path)

    print(f"Detected framework: {framework}")

    # Find routes based on framework
    routes = []
    if framework == 'nextjs':
        routes = find_nextjs_routes(project_path)
    elif framework == 'astro':
        routes = find_astro_routes(project_path)
    elif framework in ['react-router', 'react']:
        routes = find_react_routes(project_path)

    print(f"Found {len(routes)} routes")

    # Extract brand
    colors = extract_brand_colors(project_path)
    fonts = extract_fonts(project_path)
    logo = find_logo(project_path)

    print(f"Extracted {len(colors)} colors, {len(fonts)} fonts")
    if logo:
        print(f"Found logo: {logo}")

    return {
        "framework": framework,
        "routes": routes,
        "brand": {
            "colors": colors,
            "fonts": fonts,
            "logo": logo
        }
    }

def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

    if not project_path.exists():
        print(f"Error: Path {project_path} does not exist")
        sys.exit(1)

    print(f"Analyzing codebase at: {project_path.resolve()}")
    print("-" * 50)

    analysis = analyze_codebase(project_path)

    # Save to JSON
    output_file = project_path / "og-analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print("-" * 50)
    print(f"Analysis saved to: {output_file}")

    # Summary
    print("\nSummary:")
    print(f"  Framework: {analysis['framework']}")
    print(f"  Routes: {len(analysis['routes'])}")
    print(f"  Page types:")

    type_counts = {}
    for route in analysis['routes']:
        page_type = route['type']
        type_counts[page_type] = type_counts.get(page_type, 0) + 1

    for page_type, count in sorted(type_counts.items()):
        print(f"    - {page_type}: {count}")

    print(f"\n  Brand colors: {len(analysis['brand']['colors'])}")
    print(f"  Fonts: {len(analysis['brand']['fonts'])}")
    print(f"  Logo: {analysis['brand']['logo'] or 'Not found'}")

if __name__ == '__main__':
    main()
