#!/usr/bin/env python3
"""
Sitemap Generator - Generates sitemap.xml from project routes.

Usage:
    python generate_sitemap.py <project-path> --domain https://example.com

Options:
    --domain    Required. The domain for URLs in the sitemap.
    --output    Output path (default: sitemap.xml in project root)
    --priority  Default priority (default: 0.7)

Outputs:
    - sitemap.xml with all discovered routes
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom


class SitemapGenerator:
    def __init__(self, project_path: str, domain: str):
        self.project_path = Path(project_path).resolve()
        self.domain = domain.rstrip('/')
        self.routes: List[Dict] = []
        self.framework: Optional[str] = None

    def generate(self) -> str:
        """Generate sitemap XML content."""
        self._detect_framework()
        self._discover_routes()
        return self._build_xml()

    def _detect_framework(self):
        """Detect the web framework being used."""
        indicators = {
            "next.js": ["next.config.js", "next.config.mjs", "app/layout.tsx", "pages/_app.tsx"],
            "astro": ["astro.config.mjs", "astro.config.ts"],
            "gatsby": ["gatsby-config.js", "gatsby-config.ts"],
            "static": ["index.html", "public/index.html"]
        }

        for framework, files in indicators.items():
            for file in files:
                if (self.project_path / file).exists():
                    self.framework = framework
                    print(f"Framework detected: {framework}")
                    return

        self.framework = "static"
        print("Framework: Static HTML assumed")

    def _discover_routes(self):
        """Discover all routes based on framework."""
        if self.framework == "next.js":
            self._discover_nextjs_routes()
        elif self.framework == "astro":
            self._discover_astro_routes()
        elif self.framework == "gatsby":
            self._discover_gatsby_routes()
        else:
            self._discover_static_routes()

        print(f"Routes discovered: {len(self.routes)}")

    def _discover_nextjs_routes(self):
        """Discover routes from Next.js app or pages directory."""
        # App Router
        app_dir = self.project_path / "app"
        if app_dir.exists():
            for page_file in app_dir.glob("**/page.tsx"):
                route = self._nextjs_path_to_route(page_file, app_dir)
                if route:
                    self.routes.append(route)

            for page_file in app_dir.glob("**/page.jsx"):
                route = self._nextjs_path_to_route(page_file, app_dir)
                if route:
                    self.routes.append(route)

        # Pages Router
        pages_dir = self.project_path / "pages"
        if pages_dir.exists():
            for page_file in pages_dir.glob("**/*.tsx"):
                route = self._nextjs_pages_to_route(page_file, pages_dir)
                if route:
                    self.routes.append(route)

            for page_file in pages_dir.glob("**/*.jsx"):
                route = self._nextjs_pages_to_route(page_file, pages_dir)
                if route:
                    self.routes.append(route)

    def _nextjs_path_to_route(self, page_file: Path, app_dir: Path) -> Optional[Dict]:
        """Convert Next.js App Router path to route."""
        relative = page_file.parent.relative_to(app_dir)
        path_str = str(relative)

        # Skip special routes
        if any(x in path_str for x in ["api", "_", "(", "@", "."]):
            return None

        # Convert path
        if path_str == ".":
            url_path = "/"
        else:
            url_path = "/" + path_str.replace("\\", "/")

        return self._create_route_entry(url_path, page_file)

    def _nextjs_pages_to_route(self, page_file: Path, pages_dir: Path) -> Optional[Dict]:
        """Convert Next.js Pages Router path to route."""
        relative = page_file.relative_to(pages_dir)
        path_str = str(relative)

        # Skip special files
        if any(x in path_str for x in ["_app", "_document", "_error", "api/", "404", "500"]):
            return None

        # Convert to URL path
        url_path = "/" + path_str.replace("\\", "/")
        url_path = re.sub(r"\.tsx?$", "", url_path)
        url_path = re.sub(r"/index$", "/", url_path)

        return self._create_route_entry(url_path, page_file)

    def _discover_astro_routes(self):
        """Discover routes from Astro pages directory."""
        pages_dir = self.project_path / "src" / "pages"
        if not pages_dir.exists():
            return

        for page_file in pages_dir.glob("**/*.astro"):
            route = self._astro_path_to_route(page_file, pages_dir)
            if route:
                self.routes.append(route)

        for page_file in pages_dir.glob("**/*.md"):
            route = self._astro_path_to_route(page_file, pages_dir)
            if route:
                self.routes.append(route)

        for page_file in pages_dir.glob("**/*.mdx"):
            route = self._astro_path_to_route(page_file, pages_dir)
            if route:
                self.routes.append(route)

    def _astro_path_to_route(self, page_file: Path, pages_dir: Path) -> Optional[Dict]:
        """Convert Astro path to route."""
        relative = page_file.relative_to(pages_dir)
        path_str = str(relative)

        # Skip dynamic routes and special files
        if "[" in path_str or path_str.startswith("_"):
            return None

        # Convert to URL path
        url_path = "/" + path_str.replace("\\", "/")
        url_path = re.sub(r"\.(astro|md|mdx)$", "", url_path)
        url_path = re.sub(r"/index$", "/", url_path)

        return self._create_route_entry(url_path, page_file)

    def _discover_gatsby_routes(self):
        """Discover routes from Gatsby pages directory."""
        pages_dir = self.project_path / "src" / "pages"
        if not pages_dir.exists():
            return

        for ext in ["tsx", "jsx", "js"]:
            for page_file in pages_dir.glob(f"**/*.{ext}"):
                relative = page_file.relative_to(pages_dir)
                path_str = str(relative)

                # Skip special files
                if path_str.startswith("_") or "404" in path_str:
                    continue

                url_path = "/" + path_str.replace("\\", "/")
                url_path = re.sub(r"\.(tsx|jsx|js)$", "", url_path)
                url_path = re.sub(r"/index$", "/", url_path)

                route = self._create_route_entry(url_path, page_file)
                if route:
                    self.routes.append(route)

    def _discover_static_routes(self):
        """Discover routes from static HTML files."""
        for html_file in self.project_path.glob("**/*.html"):
            # Skip common non-page files
            if any(x in str(html_file) for x in ["node_modules", "dist", ".next", "build"]):
                continue

            relative = html_file.relative_to(self.project_path)
            url_path = "/" + str(relative).replace("\\", "/")

            # Convert index.html to /
            url_path = re.sub(r"/index\.html$", "/", url_path)
            url_path = re.sub(r"\.html$", "/", url_path)

            route = self._create_route_entry(url_path, html_file)
            if route:
                self.routes.append(route)

    def _create_route_entry(self, url_path: str, file_path: Path) -> Dict:
        """Create a route entry with metadata."""
        # Determine priority based on path depth and type
        depth = url_path.count("/") - 1
        if url_path == "/":
            priority = 1.0
        elif depth == 0:
            priority = 0.8
        elif "blog" in url_path or "article" in url_path:
            priority = 0.6
        else:
            priority = max(0.5, 0.8 - (depth * 0.1))

        # Determine change frequency
        if url_path == "/":
            changefreq = "weekly"
        elif "blog" in url_path or "news" in url_path:
            changefreq = "weekly"
        elif "product" in url_path:
            changefreq = "daily"
        else:
            changefreq = "monthly"

        # Get last modified from file
        try:
            mtime = file_path.stat().st_mtime
            lastmod = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except:
            lastmod = datetime.now().strftime("%Y-%m-%d")

        return {
            "url": url_path,
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": round(priority, 1)
        }

    def _build_xml(self) -> str:
        """Build the sitemap XML."""
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # Sort routes by priority (descending) then URL
        sorted_routes = sorted(self.routes, key=lambda x: (-x["priority"], x["url"]))

        for route in sorted_routes:
            url_elem = ET.SubElement(urlset, "url")

            loc = ET.SubElement(url_elem, "loc")
            loc.text = self.domain + route["url"]

            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = route["lastmod"]

            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = route["changefreq"]

            priority = ET.SubElement(url_elem, "priority")
            priority.text = str(route["priority"])

        # Pretty print
        xml_str = ET.tostring(urlset, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + dom.toprettyxml(indent="  ").split("\n", 1)[1]


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_sitemap.py <project-path> --domain https://example.com")
        print("\nGenerates sitemap.xml from project routes.")
        print("\nOptions:")
        print("  --domain    Required. The domain for URLs in the sitemap.")
        print("  --output    Output path (default: sitemap.xml in project)")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.isdir(project_path):
        print(f"Error: '{project_path}' is not a valid directory")
        sys.exit(1)

    # Parse domain
    domain = None
    output_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            i += 1

    if not domain:
        print("Error: --domain is required")
        print("Example: python generate_sitemap.py ./project --domain https://example.com")
        sys.exit(1)

    generator = SitemapGenerator(project_path, domain)
    xml_content = generator.generate()

    # Output
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = Path(project_path) / "sitemap.xml"

    output_file.write_text(xml_content)
    print(f"\nSitemap written to: {output_file}")
    print(f"Total URLs: {len(generator.routes)}")


if __name__ == "__main__":
    main()
