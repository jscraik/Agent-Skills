#!/usr/bin/env python3
"""
SEO Analyzer - Analyzes a web project codebase for SEO issues and opportunities.

Usage:
    python analyze_seo.py <project-path>

Outputs:
    - Framework detection
    - Current SEO implementation status
    - Missing elements by priority
    - Page-by-page recommendations
    - Structured data opportunities
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List, Any


class SEOAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.framework: Optional[str] = None
        self.pages: List[Dict[str, Any]] = []
        self.issues: Dict[str, List[str]] = defaultdict(list)
        self.findings: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        """Run complete SEO analysis."""
        print(f"Analyzing: {self.project_path}\n")

        self._detect_framework()
        self._find_pages()
        self._check_robots_txt()
        self._check_sitemap()
        self._analyze_meta_tags()
        self._check_structured_data()
        self._generate_report()

        return self.findings

    def _detect_framework(self):
        """Detect the web framework being used."""
        indicators = {
            "next.js": [
                "next.config.js", "next.config.mjs", "next.config.ts",
                ".next", "app/layout.tsx", "pages/_app.tsx"
            ],
            "astro": [
                "astro.config.mjs", "astro.config.ts", ".astro"
            ],
            "gatsby": [
                "gatsby-config.js", "gatsby-config.ts", "gatsby-node.js"
            ],
            "react": [
                "src/App.tsx", "src/App.jsx", "src/index.tsx"
            ],
            "vue": [
                "vue.config.js", "nuxt.config.js", "nuxt.config.ts"
            ],
            "static": [
                "index.html", "public/index.html"
            ]
        }

        for framework, files in indicators.items():
            for file in files:
                if (self.project_path / file).exists():
                    self.framework = framework
                    print(f"Framework detected: {framework.upper()}")
                    return

        self.framework = "unknown"
        print("Framework: Unknown (will check for static HTML)")

    def _find_pages(self):
        """Find all page files based on framework."""
        page_patterns = {
            "next.js": [
                "app/**/page.tsx", "app/**/page.jsx", "app/**/page.js",
                "pages/**/*.tsx", "pages/**/*.jsx", "pages/**/*.js"
            ],
            "astro": [
                "src/pages/**/*.astro", "src/pages/**/*.md", "src/pages/**/*.mdx"
            ],
            "gatsby": [
                "src/pages/**/*.tsx", "src/pages/**/*.jsx", "src/pages/**/*.js"
            ],
            "react": [
                "src/pages/**/*.tsx", "src/pages/**/*.jsx",
                "src/routes/**/*.tsx", "src/routes/**/*.jsx"
            ],
            "static": [
                "*.html", "**/*.html"
            ]
        }

        patterns = page_patterns.get(self.framework, page_patterns["static"])

        for pattern in patterns:
            for path in self.project_path.glob(pattern):
                if self._should_include_page(path):
                    self.pages.append({
                        "path": str(path.relative_to(self.project_path)),
                        "full_path": str(path),
                        "type": self._determine_page_type(path)
                    })

        print(f"Pages found: {len(self.pages)}")
        for page in self.pages[:10]:  # Show first 10
            print(f"  - {page['path']} ({page['type']})")
        if len(self.pages) > 10:
            print(f"  ... and {len(self.pages) - 10} more")
        print()

    def _should_include_page(self, path: Path) -> bool:
        """Filter out non-page files."""
        exclude_patterns = [
            "_app", "_document", "_error", "layout", "loading",
            "error", "not-found", "template", "default",
            "api/", "_middleware", "middleware"
        ]
        path_str = str(path)
        return not any(p in path_str for p in exclude_patterns)

    def _determine_page_type(self, path: Path) -> str:
        """Categorize page type based on path and content."""
        path_str = str(path).lower()

        if "blog" in path_str or "post" in path_str or "article" in path_str:
            return "article"
        if "product" in path_str or "shop" in path_str or "store" in path_str:
            return "product"
        if "about" in path_str:
            return "about"
        if "contact" in path_str:
            return "contact"
        if "pricing" in path_str:
            return "pricing"
        if "doc" in path_str or "guide" in path_str or "help" in path_str:
            return "documentation"
        if "faq" in path_str:
            return "faq"
        if path.name in ["index.html", "page.tsx", "page.jsx", "index.astro"]:
            parent = path.parent.name
            if parent in ["app", "pages", "src", ""]:
                return "landing"

        return "general"

    def _check_robots_txt(self):
        """Check for robots.txt file."""
        robots_locations = ["robots.txt", "public/robots.txt", "static/robots.txt"]

        for location in robots_locations:
            robots_path = self.project_path / location
            if robots_path.exists():
                content = robots_path.read_text()
                self.findings["robots_txt"] = {
                    "exists": True,
                    "path": location,
                    "has_sitemap": "sitemap" in content.lower(),
                    "allows_all": "Disallow:" not in content or "Disallow: \n" in content
                }
                print(f"robots.txt: Found at {location}")
                return

        self.findings["robots_txt"] = {"exists": False}
        self.issues["critical"].append("Missing robots.txt file")
        print("robots.txt: NOT FOUND")

    def _check_sitemap(self):
        """Check for sitemap configuration."""
        sitemap_locations = [
            "sitemap.xml", "public/sitemap.xml", "static/sitemap.xml"
        ]

        # Check for static sitemap
        for location in sitemap_locations:
            sitemap_path = self.project_path / location
            if sitemap_path.exists():
                self.findings["sitemap"] = {
                    "exists": True,
                    "type": "static",
                    "path": location
                }
                print(f"Sitemap: Found static at {location}")
                return

        # Check for dynamic sitemap configuration
        if self.framework == "next.js":
            for sitemap_file in ["app/sitemap.ts", "app/sitemap.js"]:
                if (self.project_path / sitemap_file).exists():
                    self.findings["sitemap"] = {
                        "exists": True,
                        "type": "dynamic",
                        "path": sitemap_file
                    }
                    print(f"Sitemap: Found dynamic at {sitemap_file}")
                    return

        if self.framework == "astro":
            config_path = self.project_path / "astro.config.mjs"
            if config_path.exists():
                content = config_path.read_text()
                if "sitemap" in content.lower():
                    self.findings["sitemap"] = {
                        "exists": True,
                        "type": "integration",
                        "path": "astro.config.mjs"
                    }
                    print("Sitemap: Found @astrojs/sitemap integration")
                    return

        self.findings["sitemap"] = {"exists": False}
        self.issues["high"].append("Missing sitemap.xml or sitemap generation")
        print("Sitemap: NOT FOUND")

    def _analyze_meta_tags(self):
        """Analyze meta tag implementation across pages."""
        print("\nAnalyzing meta tags...")

        meta_findings = {
            "pages_with_title": 0,
            "pages_with_description": 0,
            "pages_with_og": 0,
            "pages_with_twitter": 0,
            "pages_with_canonical": 0,
            "issues": []
        }

        for page in self.pages[:20]:  # Analyze first 20 pages
            content = Path(page["full_path"]).read_text()

            has_title = self._check_meta_tag(content, "title")
            has_desc = self._check_meta_tag(content, "description")
            has_og = self._check_meta_tag(content, "og:")
            has_twitter = self._check_meta_tag(content, "twitter:")
            has_canonical = self._check_meta_tag(content, "canonical")

            if has_title:
                meta_findings["pages_with_title"] += 1
            if has_desc:
                meta_findings["pages_with_description"] += 1
            if has_og:
                meta_findings["pages_with_og"] += 1
            if has_twitter:
                meta_findings["pages_with_twitter"] += 1
            if has_canonical:
                meta_findings["pages_with_canonical"] += 1

            if not has_title:
                meta_findings["issues"].append(f"Missing title: {page['path']}")
            if not has_desc:
                meta_findings["issues"].append(f"Missing description: {page['path']}")

        self.findings["meta_tags"] = meta_findings

        pages_analyzed = min(len(self.pages), 20)
        print(f"  Pages with title: {meta_findings['pages_with_title']}/{pages_analyzed}")
        print(f"  Pages with description: {meta_findings['pages_with_description']}/{pages_analyzed}")
        print(f"  Pages with Open Graph: {meta_findings['pages_with_og']}/{pages_analyzed}")
        print(f"  Pages with Twitter Cards: {meta_findings['pages_with_twitter']}/{pages_analyzed}")
        print(f"  Pages with canonical: {meta_findings['pages_with_canonical']}/{pages_analyzed}")

    def _check_meta_tag(self, content: str, tag_type: str) -> bool:
        """Check if a meta tag type exists in content."""
        patterns = {
            "title": [
                r"<title>", r"title:", r"title=", r'"title":'
            ],
            "description": [
                r'name="description"', r'name=\'description\'',
                r"description:", r'"description":'
            ],
            "og:": [
                r'property="og:', r"property='og:", r"openGraph"
            ],
            "twitter:": [
                r'name="twitter:', r"name='twitter:", r"twitter:"
            ],
            "canonical": [
                r'rel="canonical"', r"rel='canonical'", r"canonical:"
            ]
        }

        for pattern in patterns.get(tag_type, []):
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _check_structured_data(self):
        """Check for structured data implementation."""
        print("\nChecking structured data...")

        schema_found = {
            "organization": False,
            "website": False,
            "article": False,
            "product": False,
            "faq": False,
            "breadcrumb": False
        }

        # Check for JSON-LD in pages
        for page in self.pages[:20]:
            content = Path(page["full_path"]).read_text()

            if "application/ld+json" in content or "@context" in content:
                if '"Organization"' in content or "'Organization'" in content:
                    schema_found["organization"] = True
                if '"WebSite"' in content or "'WebSite'" in content:
                    schema_found["website"] = True
                if '"Article"' in content or "'Article'" in content:
                    schema_found["article"] = True
                if '"Product"' in content or "'Product'" in content:
                    schema_found["product"] = True
                if '"FAQPage"' in content or "'FAQPage'" in content:
                    schema_found["faq"] = True
                if '"BreadcrumbList"' in content or "'BreadcrumbList'" in content:
                    schema_found["breadcrumb"] = True

        self.findings["structured_data"] = schema_found

        found_schemas = [k for k, v in schema_found.items() if v]
        if found_schemas:
            print(f"  Found schemas: {', '.join(found_schemas)}")
        else:
            print("  No structured data found")
            self.issues["high"].append("No structured data (JSON-LD) implemented")

    def _generate_report(self):
        """Generate final analysis report."""
        self.findings["framework"] = self.framework
        self.findings["total_pages"] = len(self.pages)
        self.findings["page_types"] = defaultdict(int)

        for page in self.pages:
            self.findings["page_types"][page["type"]] += 1

        self.findings["page_types"] = dict(self.findings["page_types"])

        # Calculate overall score
        score = 100

        if not self.findings.get("robots_txt", {}).get("exists"):
            score -= 10
        if not self.findings.get("sitemap", {}).get("exists"):
            score -= 15

        meta = self.findings.get("meta_tags", {})
        pages_analyzed = min(len(self.pages), 20) or 1

        title_ratio = meta.get("pages_with_title", 0) / pages_analyzed
        desc_ratio = meta.get("pages_with_description", 0) / pages_analyzed
        og_ratio = meta.get("pages_with_og", 0) / pages_analyzed

        score -= int((1 - title_ratio) * 20)
        score -= int((1 - desc_ratio) * 15)
        score -= int((1 - og_ratio) * 10)

        structured = self.findings.get("structured_data", {})
        if not any(structured.values()):
            score -= 15

        self.findings["score"] = max(0, score)
        self.findings["issues"] = dict(self.issues)

    def print_report(self):
        """Print formatted analysis report."""
        print("\n" + "=" * 60)
        print("SEO ANALYSIS REPORT")
        print("=" * 60)

        print(f"\nOverall Score: {self.findings['score']}/100")
        print(f"Framework: {self.findings['framework'].upper()}")
        print(f"Total Pages: {self.findings['total_pages']}")

        print("\nPage Types:")
        for ptype, count in self.findings["page_types"].items():
            print(f"  {ptype}: {count}")

        if self.findings["issues"]:
            print("\n" + "-" * 40)
            print("ISSUES FOUND")
            print("-" * 40)

            for priority, issues in self.findings["issues"].items():
                if issues:
                    print(f"\n{priority.upper()} Priority:")
                    for issue in issues[:5]:  # Show first 5
                        print(f"  • {issue}")

        print("\n" + "-" * 40)
        print("RECOMMENDATIONS")
        print("-" * 40)

        recommendations = self._get_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['title']}")
            print(f"   {rec['description']}")
            print(f"   Priority: {rec['priority']}")

    def _get_recommendations(self) -> List[Dict[str, str]]:
        """Generate prioritized recommendations."""
        recommendations = []

        if not self.findings.get("robots_txt", {}).get("exists"):
            recommendations.append({
                "title": "Add robots.txt",
                "description": "Create a robots.txt file to control crawler access and link to sitemap.",
                "priority": "CRITICAL"
            })

        if not self.findings.get("sitemap", {}).get("exists"):
            recommendations.append({
                "title": "Add XML Sitemap",
                "description": f"Implement sitemap generation for {self.framework} to help search engines discover all pages.",
                "priority": "HIGH"
            })

        meta = self.findings.get("meta_tags", {})
        if meta.get("pages_with_description", 0) < len(self.pages):
            recommendations.append({
                "title": "Add Meta Descriptions",
                "description": "Ensure all pages have unique, compelling meta descriptions (150-160 characters).",
                "priority": "HIGH"
            })

        if meta.get("pages_with_og", 0) < len(self.pages):
            recommendations.append({
                "title": "Add Open Graph Tags",
                "description": "Implement Open Graph tags for better social media sharing previews.",
                "priority": "MEDIUM"
            })

        structured = self.findings.get("structured_data", {})
        if not structured.get("organization"):
            recommendations.append({
                "title": "Add Organization Schema",
                "description": "Add Organization JSON-LD to homepage for knowledge panel eligibility.",
                "priority": "MEDIUM"
            })

        # Page-type specific recommendations
        if self.findings["page_types"].get("article") and not structured.get("article"):
            recommendations.append({
                "title": "Add Article Schema",
                "description": "Implement Article structured data on blog/article pages for rich results.",
                "priority": "HIGH"
            })

        if self.findings["page_types"].get("product") and not structured.get("product"):
            recommendations.append({
                "title": "Add Product Schema",
                "description": "Implement Product structured data on product pages for price/availability in search.",
                "priority": "HIGH"
            })

        if self.findings["page_types"].get("faq") and not structured.get("faq"):
            recommendations.append({
                "title": "Add FAQ Schema",
                "description": "Implement FAQPage structured data for expandable FAQ results in search.",
                "priority": "MEDIUM"
            })

        return recommendations


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_seo.py <project-path>")
        print("\nAnalyzes a web project for SEO issues and opportunities.")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.isdir(project_path):
        print(f"Error: '{project_path}' is not a valid directory")
        sys.exit(1)

    analyzer = SEOAnalyzer(project_path)
    analyzer.analyze()
    analyzer.print_report()

    # Optionally output JSON
    if "--json" in sys.argv:
        print("\n" + "-" * 40)
        print("JSON OUTPUT")
        print("-" * 40)
        print(json.dumps(analyzer.findings, indent=2))


if __name__ == "__main__":
    main()
