#!/usr/bin/env python3
"""
Run the Codex insight pipeline with:
1) mandatory project brief refresh
2) mandatory dynamic refresh
3) report generation with --dynamic
4) robust launch fallback (native open -> localhost server)
"""

from __future__ import annotations

import argparse
import html
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


HOME = Path.home()
CONFIG_ROOT = HOME / "dev" / "config" / "codex"
USAGE_ROOT = CONFIG_ROOT / "usage-data"
PROJECT_BRIEF = USAGE_ROOT / "project-brief.json"
DYNAMIC_JSON = USAGE_ROOT / "dynamic-insights.json"
REPORT_HTML = USAGE_ROOT / "report.html"
REPORT_PDF = USAGE_ROOT / "report.pdf"
FACETS_JSON = USAGE_ROOT / "facets" / "latest.json"
PID_FILE = USAGE_ROOT / ".insight-report-http.pid"
PORT_FILE = USAGE_ROOT / ".insight-report-http.port"

COLLECT_SCRIPT = CONFIG_ROOT / "scripts" / "collect-project-brief.py"
DYNAMIC_SCRIPT = CONFIG_ROOT / "scripts" / "dynamic_insights.py"
GENERATE_SCRIPT = CONFIG_ROOT / "scripts" / "generate-insight-report.py"

LIGHT_ROOT_BLOCK = """    :root {
      /* Canvas layers */
      --bg-base: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-hover: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-border: #e2e8f0;
      --bg-inset: #f1f5f9;
      --bg-track: #e2e8f0;

      /* Text — WCAG 2.2 AA on #ffffff and #f8fafc */
      --text-primary: #0f172a;
      --text-secondary: #334155;
      --text-tertiary: #475569;
      --text-muted: #64748b;

      /* Accents */
      --accent-blue: #2563eb;
      --accent-purple: #7c3aed;
      --accent-green: #059669;
      --accent-amber: #b45309;
      --accent-red: #dc2626;
      --accent-cyan: #0891b2;

      /* Semantic surfaces */
      --info-bg: #eff6ff;
      --info-border: #bfdbfe;
      --info-text: #1e40af;
      --success-bg: #f0fdf4;
      --success-border: #bbf7d0;
      --success-text: #166534;
      --warning-bg: #fffbeb;
      --warning-border: #fcd34d;
      --warning-text: #92400e;
      --error-bg: #fef2f2;
      --error-border: #fecaca;
      --error-text: #991b1b;

      /* Radius */
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-xl: 18px;
    }"""

LIGHT_THEME_OVERRIDES = """
    /* Light theme overrides injected by insight-report wrapper */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Design-system aligned light theme overrides */
    body {
      font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
      background: var(--bg-base) !important;
      background-image: none !important;
      color: var(--text-primary) !important;
    }
    .container {
      max-width: 960px !important;
      padding: 0 20px !important;
    }
    h2::before {
      content: none !important;
    }

    /* Navigation */
    .nav-toc {
      position: sticky !important;
      top: 10px !important;
      z-index: 20 !important;
      background: rgba(255, 255, 255, 0.96) !important;
      border: 1px solid var(--bg-card-border) !important;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08) !important;
      backdrop-filter: blur(8px);
    }
    .nav-toc a {
      background: var(--bg-base) !important;
      border: 1px solid var(--bg-card-border) !important;
      color: var(--text-secondary) !important;
    }
    .nav-toc a:hover {
      background: var(--info-bg) !important;
      color: var(--accent-blue) !important;
      border-color: var(--info-border) !important;
    }
    .nav-toc a.is-active {
      border-color: var(--info-border) !important;
      background: var(--info-bg) !important;
      color: var(--info-text) !important;
      box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.15);
    }

    /* Typography */
    h1 {
      background: none !important;
      -webkit-text-fill-color: initial !important;
      color: var(--text-primary) !important;
    }
    h2, h3, .stat-value, .area-name, .glance-title, .chart-title, .feedback-title {
      color: var(--text-primary) !important;
    }
    .subtitle, .section-intro, .area-desc, .bar-label, .bar-value, .feedback-detail, .friction-desc, .cmd-why, .stat-label {
      color: var(--text-tertiary) !important;
    }

    /* Semantic cards */
    .section-takeaway {
      color: var(--warning-text) !important;
      background: var(--warning-bg) !important;
      border-color: var(--warning-border) !important;
    }
    .big-win {
      background: var(--success-bg) !important;
      border-color: var(--success-border) !important;
    }
    .big-win-title {
      color: var(--success-text) !important;
    }
    .big-win-desc {
      color: var(--success-text) !important;
    }
    .friction-category {
      background: var(--error-bg) !important;
      border-color: var(--error-border) !important;
    }
    .friction-title {
      color: var(--error-text) !important;
    }
    .friction-desc {
      color: var(--error-text) !important;
    }

    /* Charts */
    .bar-track {
      background: var(--bg-track) !important;
    }
    .bar-label {
      width: auto !important;
      min-width: 110px !important;
      max-width: 160px !important;
      white-space: normal !important;
      line-height: 1.3 !important;
      color: var(--text-secondary) !important;
    }
    .bar-fill {
      min-width: 3px !important;
    }

    /* Code / examples */
    .friction-examples {
      background: var(--bg-base) !important;
      border: 1px solid var(--bg-card-border) !important;
      color: var(--text-tertiary) !important;
    }
    .cmd-code, .example-code, .copyable-prompt, .instruction-copy-code {
      background: var(--bg-base) !important;
      color: var(--text-primary) !important;
      border: 1px solid var(--bg-card-border) !important;
    }

    /* Surface cards */
    .project-area, .narrative, .key-insight, .instruction-item, .feature-card,
    .pattern-card, .chart-card, .horizon-card, .feedback-card, .data-source-card,
    .source-card, .section-card, .cluster-story-card, .stat, .glance-section {
      background: var(--bg-surface) !important;
      border: 1px solid var(--bg-card-border) !important;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06) !important;
    }

    /* Alerts */
    .release-alert-badge {
      border: 1px solid var(--warning-border) !important;
      background: var(--warning-bg) !important;
    }
    .release-alert-pill {
      color: var(--warning-text) !important;
      background: #fef3c7 !important;
    }
    .release-alert-text {
      color: var(--warning-text) !important;
    }

    /* Form controls */
    .timezone-select, .timezone-input {
      background: var(--bg-surface) !important;
      color: var(--text-secondary) !important;
      border: 1px solid var(--bg-card-border) !important;
    }

    /* Inline style fixes */
    [style*="color:#94a3b8"], [style*="color: #94a3b8"],
    [style*="color:#cbd5e1"], [style*="color: #cbd5e1"],
    [style*="color:#93c5fd"], [style*="color: #93c5fd"] {
      color: var(--text-secondary) !important;
    }
    [style*="background:#1e293b"], [style*="background: #1e293b"],
    [style*="background:#0f172a"], [style*="background: #0f172a"],
    [style*="background:#1e3a5f"], [style*="background: #1e3a5f"] {
      background: var(--bg-track) !important;
      color: var(--text-primary) !important;
    }
    [style*="border-top:1px solid #1e293b"], [style*="border-top: 1px solid #1e293b"] {
      border-top: 1px solid var(--bg-card-border) !important;
    }
    [style*="border-bottom:1px solid #0f172a"], [style*="border-bottom: 1px solid #0f172a"] {
      border-bottom: 1px solid var(--bg-card-border) !important;
    }
    [style*="border:1px solid rgba(255,255,255,0.09)"], [style*="border: 1px solid rgba(255,255,255,0.09)"],
    [style*="border:1px solid rgba(255,255,255,0.1)"], [style*="border: 1px solid rgba(255,255,255,0.1)"] {
      border-color: var(--bg-card-border) !important;
    }
    [style*="background:rgba(255,255,255,0.04)"], [style*="background: rgba(255,255,255,0.04)"] {
      background: var(--bg-base) !important;
    }
    [style*="color:#6b7394"], [style*="color: #6b7394"] {
      color: var(--text-muted) !important;
    }

    /* Specialty cards */
    .cognitive-load-card, .doc-health-card, .tdd-card, .ai-governance-card,
    .security-card, .flow-card, .growth-card {
      background: var(--bg-surface) !important;
      backdrop-filter: none !important;
      border: 1px solid var(--bg-card-border) !important;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06) !important;
    }
    .cognitive-load-card:hover, .doc-health-card:hover, .tdd-card:hover,
    .ai-governance-card:hover, .security-card:hover, .flow-card:hover, .growth-card:hover {
      border-color: #c7d4e3 !important;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08) !important;
    }
    .cognitive-header, .doc-header, .tdd-header, .ai-gov-header, .security-header, .card-header {
      border-bottom: 1px solid var(--bg-card-border) !important;
    }
    .cognitive-score, .doc-score, .security-score, .metric-value, .growth-score-value {
      font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
      letter-spacing: -0.01em !important;
    }
    .metric, .metric-pill, .insight-box, .doc-action, .cognitive-recommendation, .tdd-recommendation {
      background: var(--bg-base) !important;
      border: 1px solid var(--bg-card-border) !important;
      color: var(--text-secondary) !important;
      box-shadow: none !important;
    }
    .progress-track, .progress-bar-container {
      background: var(--bg-track) !important;
      border: none !important;
    }
    .progress-bar {
      box-shadow: none !important;
    }
    .status-badge {
      background: var(--info-bg) !important;
      border: 1px solid var(--info-border) !important;
      color: var(--info-text) !important;
    }
    .status-badge::before {
      animation: none !important;
    }

    /* Icons */
    .card-title[class*="icon-"] {
      display: flex !important;
      align-items: center !important;
      gap: 10px !important;
    }
    .card-title[class*="icon-"]::before, .inline-icon {
      content: "";
      display: inline-block;
      width: 16px;
      height: 16px;
      background-position: center;
      background-repeat: no-repeat;
      background-size: 16px 16px;
      flex-shrink: 0;
      vertical-align: -2px;
    }
    .card-title.icon-focus::before {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 12h4l3-8 4 16 3-8h4'/%3E%3C/svg%3E");
    }
    .card-title.icon-alert::before {
      background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z'/%3E%3Cline x1='12' x2='12' y1='9' y2='13'/%3E%3Cline x1='12' x2='12.01' y1='17' y2='17'/%3E%3C/svg%3E\");
    }
    .card-title.icon-security::before {
      background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2316a34a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/%3E%3C/svg%3E\");
    }
    .card-title.icon-growth::before {
      background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%237c3aed' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 17 9 11l4 4 7-7'/%3E%3Cpath d='M14 8h6v6'/%3E%3C/svg%3E\");
    }
    .inline-icon.icon-bolt {
      width: 14px;
      height: 14px;
      background-size: 14px 14px;
      background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23d97706' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M13 2 3 14h7l-1 8 10-12h-7l1-8z'/%3E%3C/svg%3E\");
    }

    /* Focus */
    a:focus-visible, button:focus-visible, summary:focus-visible, .nav-toc a:focus-visible {
      outline: 2px solid var(--accent-blue) !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18) !important;
      border-radius: 10px !important;
    }

    /* Motion */
    .instruction-item, .feature-card, .feedback-card, .friction-category, .big-win, .project-area {
      transition: transform 260ms cubic-bezier(0.22, 1, 0.36, 1),
                  box-shadow 260ms cubic-bezier(0.22, 1, 0.36, 1),
                  border-color 220ms ease,
                  opacity 220ms ease;
      transform: translateY(0);
    }
    .instruction-item:hover, .feature-card:hover, .feedback-card:hover,
    .friction-category:hover, .big-win:hover, .project-area:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 30px rgba(15, 23, 42, 0.11) !important;
      border-color: #c3d2e2 !important;
    }
    .insight-reveal {
      opacity: 0;
      transform: translateY(10px);
    }
    .insight-reveal.is-visible {
      opacity: 1;
      transform: translateY(0);
      transition: opacity 440ms cubic-bezier(0.22, 1, 0.36, 1),
                  transform 440ms cubic-bezier(0.22, 1, 0.36, 1);
      transition-delay: calc(var(--reveal-stagger, 0) * 48ms);
    }
    @media (prefers-reduced-motion: reduce) {
      .instruction-item, .feature-card, .feedback-card, .friction-category, .big-win, .project-area,
      .insight-reveal, .insight-reveal.is-visible {
        transition: none !important;
        transform: none !important;
        opacity: 1 !important;
      }
    }
    a {
      color: var(--accent-blue) !important;
    }
    .narrative-box {
      background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      border: 1px solid #f59e0b;
      border-radius: var(--radius-md);
      padding: 20px 24px;
      margin-bottom: 24px;
    }
    .narrative-title {
      font-size: 16px;
      font-weight: 700;
      color: #92400e;
      margin-bottom: 14px;
    }
    .narrative-sections {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .narrative-item {
      font-size: 14px;
      line-height: 1.6;
      color: #78350f;
    }
    .narrative-item strong {
      color: #92400e;
    }
    .scorecard-icon svg {
      display: block;
      margin: 0 auto;
    }
    .action-fix {
      font-size: 12px;
      color: var(--text-muted) !important;
      background: var(--bg-inset) !important;
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      margin: 0;
    }
    .action-fix code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-secondary) !important;
      background: var(--bg-base) !important;
      padding: 1px 4px;
      border-radius: 4px;
      border: 1px solid var(--bg-card-border) !important;
    }
    .at-a-glance {
      display: none !important;
    }
    .see-more { color: #b45309 !important; text-decoration: none; font-size: 13px; white-space: nowrap; font-weight: 600; }
    .see-more:hover { text-decoration: underline; }
    .fun-card { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; border-radius: var(--radius-md); padding: 18px 20px; margin: 20px 0 28px; text-align: center; }
    .fun-card-icon { font-size: 20px; margin-bottom: 8px; }
    .fun-card-quote { font-size: 16px; font-weight: 700; color: #92400e; line-height: 1.4; }
    .fun-card-detail { font-size: 13px; color: #78350f; margin-top: 6px; }
    .action-copy-btn { margin-left: auto; background: var(--bg-inset) !important; border: 1px solid var(--bg-card-border) !important; color: var(--text-secondary) !important; font-size: 11px; padding: 4px 10px; border-radius: var(--radius-sm); cursor: pointer; font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif; }
    .action-copy-btn:hover { background: var(--bg-base) !important; border-color: #c3d2e2 !important; }
    /* End light theme overrides */

"""

DASHBOARD_CSS = """
    /* Developer Dashboard (injected for all themes) */
    .dev-dashboard {
      margin: 28px 0 44px;
    }
    .scorecard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
      margin-bottom: 28px;
    }
    .scorecard {
      background: var(--bg-surface) !important;
      border: 1px solid var(--bg-card-border) !important;
      border-radius: var(--radius-md);
      padding: 18px 16px;
      text-align: center;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06) !important;
      transition: transform 200ms ease, box-shadow 200ms ease;
    }
    .scorecard:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.10) !important;
    }
    .scorecard-icon {
      font-size: 22px;
      margin-bottom: 6px;
    }
    .scorecard-value {
      font-size: 32px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary) !important;
      line-height: 1.1;
    }
    .scorecard-good .scorecard-value { color: var(--success-text) !important; }
    .scorecard-warn .scorecard-value { color: var(--warning-text) !important; }
    .scorecard-bad  .scorecard-value { color: var(--error-text) !important; }
    .scorecard-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary) !important;
      margin-top: 6px;
    }
    .scorecard-meta {
      font-size: 11px;
      color: var(--text-muted) !important;
      margin-top: 2px;
    }
    .action-board {
      margin-top: 28px;
    }
    .action-board-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary) !important;
      margin-bottom: 14px;
      letter-spacing: -0.01em;
    }
    .action-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }
    .action-card {
      background: var(--bg-surface) !important;
      border: 1px solid var(--bg-card-border) !important;
      border-radius: var(--radius-md);
      padding: 0;
      box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05) !important;
      transition: transform 200ms ease, box-shadow 200ms ease;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .action-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.09) !important;
    }
    .action-card-urgent { border-left: 4px solid var(--error-text) !important; }
    .action-card-improvement { border-left: 4px solid var(--success-text) !important; }
    .action-card-project { border-left: 4px solid var(--info-text) !important; }
    .action-header {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      padding: 14px 16px;
      border-bottom: 1px solid var(--bg-card-border) !important;
      background: rgba(255,255,255,0.02);
    }
    .action-header-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }
    .action-badge {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-radius: 999px;
      padding: 3px 10px;
      flex-shrink: 0;
    }
    .action-badge-urgent { background: var(--error-bg) !important; color: var(--error-text) !important; border: 1px solid var(--error-border) !important; }
    .action-badge-improvement { background: var(--success-bg) !important; color: var(--success-text) !important; border: 1px solid var(--success-border) !important; }
    .action-badge-project { background: var(--info-bg) !important; color: var(--info-text) !important; border: 1px solid var(--info-border) !important; }
    .action-header h3 {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-primary) !important;
      margin: 0;
      flex: 1 1 auto;
      line-height: 1.35;
    }
    .action-body {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(220px, 0.8fr);
      gap: 0;
    }
    @media (max-width: 720px) {
      .action-body {
        grid-template-columns: 1fr;
      }
    }
    .action-main {
      padding: 14px 16px;
      font-size: 13.5px;
      line-height: 1.65;
      color: var(--text-secondary) !important;
    }
    .action-meta {
      padding: 14px 16px;
      background: rgba(255,255,255,0.015);
      border-left: 1px solid var(--bg-card-border) !important;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    @media (max-width: 720px) {
      .action-meta {
        border-left: none !important;
        border-top: 1px solid var(--bg-card-border) !important;
      }
    }
    .action-meta-item {
      font-size: 12px;
      line-height: 1.55;
      color: var(--text-tertiary) !important;
    }
    .action-meta-label {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted) !important;
      display: block;
      margin-bottom: 2px;
    }
    .action-evidence {
      margin-top: 10px;
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      background: rgba(255,255,255,0.03);
      border: 1px dashed var(--bg-card-border) !important;
      font-size: 12px;
      line-height: 1.5;
      color: var(--text-muted) !important;
    }
    .action-card .evidence-citations {
      margin-top: 10px;
      border-top: none !important;
      padding-top: 0 !important;
    }
    .action-card .evidence-citations summary {
      font-size: 10px;
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--bg-card-border) !important;
    }
    .action-links {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 4px;
    }
    .action-link {
      font-size: 12px;
      font-weight: 600;
      color: var(--accent-blue) !important;
      text-decoration: none;
      padding: 5px 10px;
      border-radius: var(--radius-sm);
      background: var(--info-bg) !important;
      border: 1px solid var(--info-border) !important;
      transition: background 150ms ease;
    }
    .action-link:hover {
      background: #dbeafe !important;
      color: #1e40af !important;
    }
"""

def run_checked(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def assert_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise RuntimeError(f"Missing required {label}: {path}")


def assert_report_markers(report_html: Path, self_optimize: bool) -> None:
    html = read_text(report_html)
    if "Project Brief" not in html:
        raise RuntimeError("Missing report section marker: Project Brief")
    if "Data Sources & Accuracy" not in html and "Evidence & Limits" not in html:
        raise RuntimeError("Missing report section marker: Data Sources & Accuracy (or Evidence & Limits)")
    if self_optimize and "Self-Optimizing Recommendation Loop (v1)" not in html:
        raise RuntimeError("Missing required section marker: Self-Optimizing Recommendation Loop (v1)")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_open_port(preferred: int = 8765) -> int:
    for port in [preferred, preferred + 1, preferred + 2, preferred + 3, preferred + 4]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def get_native_open_command(target: str) -> list[str] | None:
    system = platform.system().lower()
    if system == "darwin":
        return ["open", target]
    if system == "linux":
        return ["xdg-open", target]
    if system == "windows":
        return ["cmd", "/c", "start", "", target]
    return None


def try_native_open(target: str) -> tuple[bool, str | None]:
    cmd = get_native_open_command(target)
    if not cmd:
        return False, "No platform-native open command available"
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        return True, None
    except Exception as exc:  # noqa: BLE001 - capture exact launch failure text
        return False, str(exc)


def start_or_reuse_localhost_server(root_dir: Path) -> tuple[int, bool]:
    if PID_FILE.exists() and PORT_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            port = int(PORT_FILE.read_text().strip())
            if pid_alive(pid):
                return port, True
        except Exception:  # noqa: BLE001
            pass

    port = get_open_port()
    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    proc = subprocess.Popen(  # noqa: S603,S607 - controlled local server command
        cmd,
        cwd=str(root_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(0.6)
    if proc.poll() is not None:
        raise RuntimeError("Failed to start localhost fallback server")
    PID_FILE.write_text(f"{proc.pid}\n", encoding="utf-8")
    PORT_FILE.write_text(f"{port}\n", encoding="utf-8")
    return port, False


def launch_report(report_html: Path) -> tuple[str, str]:
    opened, native_err = try_native_open(str(report_html))
    if opened:
        return "native-open", f"file://{report_html}"

    port, reused = start_or_reuse_localhost_server(report_html.parent)
    url = f"http://127.0.0.1:{port}/{report_html.name}"
    webbrowser.open(url)
    mode = "localhost-fallback-reused" if reused else "localhost-fallback-started"
    detail = native_err or "native open failed"
    print(f"Native launch unavailable: {detail}")
    print(f"Localhost fallback active: {url}")
    return mode, url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dynamic Codex insight report with launch fallback.")
    parser.add_argument("--days", type=int, default=None, help="Lookback window in days")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF report")
    parser.add_argument("--include-architecture", action="store_true", help="Include architecture diagrams")
    parser.add_argument("--self-optimize", action="store_true", help="Include self-optimization analysis")
    parser.add_argument("--theme", choices=["light", "dark"], default="dark", help="Report theme (default: dark)")
    parser.add_argument(
        "--theme-only",
        action="store_true",
        help="Apply theme to existing report.html without re-running data collection/generation",
    )
    parser.add_argument("--otel-root", default=str(HOME / ".agents" / "otel-collector"), help="OTEL collector root")
    parser.add_argument("--open", dest="open_report", action="store_true", default=True, help="Launch report after generation (default)")
    parser.add_argument("--no-open", dest="open_report", action="store_false", help="Do not launch report")
    return parser.parse_args()


def sanitize_existing_path(raw_path: str, label: str) -> str:
    path = Path(raw_path).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(f"{label} path does not exist: {path}")
    return str(path)


def strip_emoji(text: str) -> str:
    # Remove pictographic emoji characters that can slip in from upstream report content.
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)
    # Clean up common unicode control marks used in emoji compositions.
    text = text.replace("\uFE0F", "").replace("\u200D", "")
    return text


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_facets() -> dict:
    if not FACETS_JSON.exists():
        return {}
    try:
        return json.loads(FACETS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _extract_friction_categories(facets: dict) -> list[tuple[str, int]]:
    items: list[tuple[str, int]] = []
    raw = facets.get("friction_analysis", {}).get("categories", [])
    if not isinstance(raw, list):
        return items
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = (
            str(item.get("category") or item.get("name") or item.get("source_key") or "").strip()
            or "Uncategorized Friction"
        )
        count = _safe_int(item.get("count"), 0)
        if count <= 0:
            continue
        items.append((name, count))
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def _get_count_for(categories: list[tuple[str, int]], needle: str) -> int:
    needle_l = needle.lower()
    for name, count in categories:
        if needle_l in name.lower():
            return count
    return 0


def _find_category(categories: list[tuple[str, int]], needles: list[str]) -> tuple[str, int]:
    for name, count in categories:
        lowered = name.lower()
        if any(needle in lowered for needle in needles):
            return name, count
    return "", 0


def _get_multi_codexing_overlaps(facets: dict) -> int:
    raw = facets.get("charts", {}).get("multi_codexing", {}).get("overlap_events", 0)
    return _safe_int(raw, 0)


def _build_card_for_category(category: str, count: int, categories: list[tuple[str, int]]) -> dict[str, str]:
    lower = category.lower()
    policy_count = _get_count_for(categories, "policy")
    command_count = _get_count_for(categories, "command")
    path_count = _get_count_for(categories, "path") or _get_count_for(categories, "file")
    routing_count = _get_count_for(categories, "routing") or _get_count_for(categories, "skill")
    top_friction_line = ", ".join([f"{name} ({value})" for name, value in categories[:3]])

    if "policy" in lower or "permission" in lower:
        policy_value = policy_count or count
        return {
            "title": "Policy Calibration for Rejected Command Patterns",
            "detail": (
                f"{category} generated {policy_value} interruptions in this reporting window. "
                "Use a narrow, evidence-based allowlist model instead of broad trust expansion."
            ),
            "evidence": f"Evidence: top friction signatures this period were {top_friction_line}.",
            "prompt": (
                "## Policy Calibration (Dynamic)\n"
                f"- Current signal: {policy_value} policy/permission rejections\n"
                "- Keep baseline `approval_policy = \"on-request\"`\n"
                "- Add trusted prefixes only for repeated, safe command patterns\n"
                "- Keep destructive command families explicitly gated\n"
                "- Re-verify rejection trend in the next report window"
            ),
        }

    if "command" in lower:
        return {
            "title": "Adopt a command preflight phase in your Codex workflow.",
            "detail": (
                "Before multi-step shell workflows, run a deterministic preflight for cwd, binaries, and target paths."
            ),
            "evidence": (
                f"Evidence: command failures={command_count} and path/file issues={path_count} in this period."
            ),
            "prompt": (
                "## Command Preflight (Dynamic)\n"
                "1. Confirm cwd and repo root (`pwd` + expected path)\n"
                "2. Confirm binaries (`command -v rg fd jq python3`)\n"
                "3. Confirm targets (`test -e <path>` or `fd <name> <root>`)\n"
                "4. Prefer dry-run/check modes before destructive changes\n"
                f"Reason: this period saw {command_count} command failures and {path_count} path/file issues."
            ),
        }

    if "path" in lower or "file" in lower:
        return {
            "title": "Harden path contracts before command execution.",
            "detail": (
                f"{category} occurred {count} times. Formalize a path contract to prevent no-such-file and wrong-root detours."
            ),
            "evidence": (
                "Evidence: recurring file-resolution failures were visible in command output and retries."
            ),
            "prompt": (
                "## Path Contract Guardrail (Dynamic)\n"
                "- Resolve and print repo root before path-sensitive commands\n"
                "- Use `fd`/`rg --files` for discovery before edits or deletions\n"
                "- Validate every critical path with `test -e`\n"
                "- Prefer absolute file references in generated command chains"
            ),
        }

    if "routing" in lower or "skill" in lower:
        return {
            "title": "Add explicit skill-routing acknowledgement checks.",
            "detail": (
                f"{category} contributed {count} weighted interruptions. Tighten request-to-skill acknowledgement in first assistant turn."
            ),
            "evidence": (
                f"Evidence: routing mismatch signals (weighted) were {count}, with raw mismatch events at {routing_count or count}."
            ),
            "prompt": (
                "## Skill Routing Confirmation (Dynamic)\n"
                "- When user names a skill, echo skill + reason in first progress update\n"
                "- Confirm execution mode before broad repo edits\n"
                "- If routing is ambiguous, state chosen skill boundary explicitly"
            ),
        }

    if "parallel" in lower or "multi-codexing" in lower:
        return {
            "title": "Formalize parallel session coordination conventions.",
            "detail": (
                f"{category} surfaced {count} overlap events. Add branch, ownership, and merge rules for concurrent sessions."
            ),
            "evidence": (
                f"Evidence: detected {count} multi-session overlap events in this reporting window."
            ),
            "prompt": (
                "## Parallel Session Coordination (Dynamic)\n"
                "- Reserve one branch per active session scope\n"
                "- Define ownership boundaries before concurrent edits\n"
                "- Post merge-order and conflict strategy at session start\n"
                "- Require a final integration pass before PR handoff"
            ),
        }

    return {
        "title": f"Reduce friction in: {category}",
        "detail": (
            f"{category} appeared {count} times in this period. Add one guardrail for this lane and re-measure next run."
        ),
        "evidence": f"Evidence: top friction signatures this period were {top_friction_line}.",
        "prompt": (
            f"## Guardrail for {category}\n"
            "- Define one repeatable pre-check\n"
            "- Add one post-failure retry rule\n"
            "- Track trend in next insights report"
        ),
    }


def _build_dynamic_copy_payload(facets: dict) -> dict[str, object]:
    categories = _extract_friction_categories(facets)
    if not categories:
        return {}

    policy_name, policy_count = _find_category(categories, ["policy", "permission"])
    command_name, command_count = _find_category(categories, ["command"])
    path_name, path_count = _find_category(categories, ["path", "file"])
    routing_name, routing_count = _find_category(categories, ["routing", "skill"])
    parallel_count = _get_multi_codexing_overlaps(facets)

    if not policy_name:
        policy_name, policy_count = categories[0]
    if not command_name:
        command_name, command_count = categories[min(1, len(categories) - 1)]

    third_name = path_name or categories[min(2, len(categories) - 1)][0]
    third_count = path_count or categories[min(2, len(categories) - 1)][1]

    # Adaptive slot-3 selection: switch to routing or parallel guidance when either overtakes path friction.
    if routing_count > third_count and routing_name:
        third_name, third_count = routing_name, routing_count
    elif parallel_count > third_count:
        third_name, third_count = "Parallel Session Coordination", parallel_count

    cards = [
        _build_card_for_category(policy_name, policy_count, categories),
        _build_card_for_category(command_name, command_count, categories),
        _build_card_for_category(third_name, third_count, categories),
    ]
    return {"cards": cards[:3]}


def _rewrite_instruction_card_segment(segment: str, card: dict[str, str]) -> str:
    segment = re.sub(
        r"(<span style=\"font-weight:600; font-size:14px; color:var\(--text-primary\);\">).*?(</span>)",
        lambda m: f"{m.group(1)}{html.escape(card['title'])}{m.group(2)}",
        segment,
        count=1,
        flags=re.DOTALL,
    )
    segment = re.sub(
        r"(<div style=\"font-size:13px; color:var\(--text-secondary\); margin-bottom:10px; line-height:1\.6;\">).*?(</div>)",
        lambda m: f"{m.group(1)}{html.escape(card['detail'])}{m.group(2)}",
        segment,
        count=1,
        flags=re.DOTALL,
    )
    segment = re.sub(
        r"(<div class=\"instruction-evidence-note\">).*?(</div>)",
        lambda m: f"{m.group(1)}{html.escape(card['evidence'])}{m.group(2)}",
        segment,
        count=1,
        flags=re.DOTALL,
    )
    segment = re.sub(
        r"(<pre class=\"instruction-copy-code\">).*?(</pre>)",
        lambda m: f"{m.group(1)}{html.escape(card['prompt'])}{m.group(2)}",
        segment,
        count=1,
        flags=re.DOTALL,
    )
    return segment


def _apply_instruction_card_overrides(html_text: str, cards: list[dict[str, str]]) -> str:
    parts = html_text.split('<div class="instruction-item">')
    if len(parts) <= 1:
        return html_text
    limit = min(3, len(cards), len(parts) - 1)
    for idx in range(limit):
        parts[idx + 1] = _rewrite_instruction_card_segment(parts[idx + 1], cards[idx])
    return '<div class="instruction-item">'.join(parts)


def _apply_feedback_card_override(html_text: str, card: dict[str, str]) -> str:
    chunks = html_text.split('<div class="feedback-card team-card">', 1)
    if len(chunks) != 2:
        return html_text
    head, tail = chunks
    tail = re.sub(
        r"(<div class=\"feedback-detail\">).*?(</div>)",
        lambda m: f"{m.group(1)}{html.escape(card['detail'])}{m.group(2)}",
        tail,
        count=1,
        flags=re.DOTALL,
    )
    tail = re.sub(
        r"(<div class=\"feedback-evidence\">).*?(</div>)",
        lambda m: f"{m.group(1)}{html.escape(card['evidence'])}{m.group(2)}",
        tail,
        count=1,
        flags=re.DOTALL,
    )
    tail = re.sub(
        r"(<code class=\"copyable-prompt\">).*?(</code>)",
        lambda m: f"{m.group(1)}{html.escape(card['prompt'])}{m.group(2)}",
        tail,
        count=1,
        flags=re.DOTALL,
    )
    return f'{head}<div class="feedback-card team-card">{tail}'




def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _compute_health_score(facts: dict, facets: dict) -> int:
    total_tools = facts.get("tool_calls.total", {}).get("value", 1)
    friction = sum(
        v.get("value", 0)
        for k, v in facts.items()
        if k.startswith("friction.")
    )
    if total_tools <= 0:
        total_tools = 1
    raw = max(0, 100 - int((friction / total_tools) * 100))
    # Cap at 99 unless literally zero friction
    return 100 if raw > 99 and friction == 0 else min(99, raw)


def _skill_links_for(friction_name: str) -> list[tuple[str, str]]:
    lower = friction_name.lower()
    base = Path.home()
    skills_root = base / ".agents/skills"
    docs_root = base / "dev/agent-skills/docs/agents"
    if "policy" in lower or "permission" in lower:
        return [
            ("codex-home-audit skill", str(skills_root / "codex-home-audit/SKILL.md")),
            ("Security guide", str(docs_root / "06-security-and-governance.md")),
        ]
    if "command" in lower:
        return [
            ("Systematic debugging skill", str(skills_root / "systematic-debugging/SKILL.md")),
            ("Validation guide", str(docs_root / "04-validation.md")),
        ]
    if "path" in lower or "file" in lower:
        return [
            ("Backend engineer skill", str(skills_root / "backend-engineer/SKILL.md")),
            ("Fix mise skill", str(skills_root / "fix-mise/SKILL.md")),
        ]
    if "routing" in lower or "skill" in lower:
        return [
            ("Agents-md skill", str(skills_root / "agents-md/SKILL.md")),
            ("Agent routing guide", str(docs_root / "README.md")),
        ]
    if "latency" in lower or "performance" in lower or "slow" in lower:
        return [
            ("CE planning skill", str(skills_root / "ce-plan/SKILL.md")),
            ("Backend engineer skill", str(skills_root / "backend-engineer/SKILL.md")),
        ]
    if "automation" in lower or "stale" in lower:
        return [
            ("Automation architect skill", str(skills_root / "codex-automation-architect/SKILL.md")),
        ]
    return [
        ("Agent skills index", str(base / "dev/agent-skills/AGENTS.md")),
    ]


def _build_narrative_html(facts: dict, facets: dict, dynamic: dict, brief: dict) -> str:
    glance = facets.get("at_a_glance", {})
    if glance:
        sections: list[str] = []
        if glance.get("whats_working"):
            sections.append(
                f'<div class="narrative-item"><strong>What\'s working:</strong> '
                f'{html.escape(glance["whats_working"])} '
                f'<a href="#section-wins" class="see-more">See workflows →</a></div>'
            )
        if glance.get("whats_hindering"):
            sections.append(
                f'<div class="narrative-item"><strong>What\'s hindering you:</strong> '
                f'{html.escape(glance["whats_hindering"])} '
                f'<a href="#section-friction" class="see-more">See friction →</a></div>'
            )
        if glance.get("quick_wins"):
            sections.append(
                f'<div class="narrative-item"><strong>Quick win to try:</strong> '
                f'{html.escape(glance["quick_wins"])} '
                f'<a href="#section-features" class="see-more">See features →</a></div>'
            )
        if glance.get("ambitious_workflows"):
            sections.append(
                f'<div class="narrative-item"><strong>Ambitious workflows:</strong> '
                f'{html.escape(glance["ambitious_workflows"])} '
                f'<a href="#section-horizon" class="see-more">See what\'s next →</a></div>'
            )
        sections_html = "\n        ".join(sections)
        return f"""<div class="narrative-box">
      <div class="narrative-title">At a Glance</div>
      <div class="narrative-sections">
        {sections_html}
      </div>
    </div>"""

    # Fallback to synthesized narrative if at_a_glance is missing
    total_tools = facts.get("tool_calls.total", {}).get("value", 0)
    sessions = facts.get("sessions.analyzed_count", {}).get("value", 0)
    friction_cats = facets.get("friction_analysis", {}).get("categories", [])
    top_friction = friction_cats[0] if friction_cats else {}
    top_friction_name = top_friction.get("category", "None")
    top_friction_count = top_friction.get("count", 0)

    working = f"You drove {total_tools:,} tool calls across {sessions} sessions with solid execution velocity."
    hindering = f"<strong>{html.escape(top_friction_name)}</strong> caused {top_friction_count} interruptions — that's your clearest drag on throughput."

    quick_win = ""
    improvements = dynamic.get("improvements", [])
    if improvements:
        what = improvements[0].get("what", "")
        quick_win = f"{html.escape(what)}."

    project_watch = ""
    projects = brief.get("projects", [])
    at_risk = [p for p in projects if p.get("health") in ("yellow", "red") or p.get("blockers") not in ("none", "", None)]
    if at_risk:
        p = at_risk[0]
        project_watch = f"<strong>{html.escape(p.get('name', 'Project'))}</strong> is {html.escape(p.get('status', 'Unknown'))} with milestone <em>{html.escape(p.get('next_milestone', 'N/A'))}</em> due {html.escape(p.get('next_milestone_date', '?'))}."

    return f"""<div class="narrative-box">
      <div class="narrative-title">At a Glance</div>
      <div class="narrative-sections">
        <div class="narrative-item"><strong>What's working:</strong> {working}</div>
        <div class="narrative-item"><strong>What's hindering you:</strong> {hindering}</div>
        {f'<div class="narrative-item"><strong>Quick win to try:</strong> {quick_win}</div>' if quick_win else ''}
        {f'<div class="narrative-item"><strong>Project watch:</strong> {project_watch}</div>' if project_watch else ''}
      </div>
    </div>"""


def _build_fun_card_html(facets: dict) -> str:
    fun = facets.get("fun_ending", {})
    headline = fun.get("headline", "")
    detail = fun.get("detail", "")
    if not headline:
        return ""
    detail_html = f'<div class="fun-card-detail">{html.escape(detail)}</div>' if detail else ""
    return f"""<div class="fun-card">
      <div class="fun-card-icon">&#10022;</div>
      <div class="fun-card-quote">"{html.escape(headline)}"</div>
      {detail_html}
    </div>"""

def _build_scorecard_html(facts: dict, facets: dict) -> str:
    total_tools = facts.get("tool_calls.total", {}).get("value", 0)
    total_msgs = facts.get("messages.total", {}).get("value", 0)
    sessions = facts.get("sessions.analyzed_count", {}).get("value", 0)
    health = _compute_health_score(facts, facets)

    friction_cats = facets.get("friction_analysis", {}).get("categories", [])
    top_friction = friction_cats[0] if friction_cats else {}
    top_friction_name = top_friction.get("category", "None")
    top_friction_count = top_friction.get("count", 0)
    friction_pct = f"{top_friction_count / total_tools * 100:.1f}%" if total_tools else "0%"

    health_class = "scorecard-good" if health >= 85 else "scorecard-warn" if health >= 60 else "scorecard-bad"
    friction_class = "scorecard-bad" if top_friction_count > 200 else "scorecard-warn" if top_friction_count > 50 else "scorecard-good"

    # Simple SVG icons as data URIs for reliability
    icon_check = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
    icon_alert = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>'
    icon_bolt = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>'
    icon_chat = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'

    health_icon = icon_check if health >= 85 else icon_alert
    friction_icon = icon_alert if top_friction_count > 50 else '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>'

    return f"""<div class="scorecard-grid">
      <div class="scorecard {health_class}">
        <div class="scorecard-icon">{health_icon}</div>
        <div class="scorecard-value">{health}</div>
        <div class="scorecard-label">Health Score</div>
        <div class="scorecard-meta">Based on friction vs. tool volume</div>
      </div>
      <div class="scorecard scorecard-good">
        <div class="scorecard-icon">{icon_bolt}</div>
        <div class="scorecard-value">{total_tools:,}</div>
        <div class="scorecard-label">Tool Calls</div>
        <div class="scorecard-meta">{sessions} sessions analyzed</div>
      </div>
      <div class="scorecard {friction_class}">
        <div class="scorecard-icon">{friction_icon}</div>
        <div class="scorecard-value">{top_friction_count}</div>
        <div class="scorecard-label">{html.escape(top_friction_name)}</div>
        <div class="scorecard-meta">{friction_pct} of all calls</div>
      </div>
      <div class="scorecard scorecard-good">
        <div class="scorecard-icon">{icon_chat}</div>
        <div class="scorecard-value">{total_msgs:,}</div>
        <div class="scorecard-label">Messages</div>
        <div class="scorecard-meta">~{total_msgs // max(sessions, 1)} per session</div>
      </div>
    </div>"""


def _build_action_board_html(facets: dict, dynamic: dict, brief: dict) -> str:
    cards: list[str] = []

    # Primary source: operator brief actions (strategic, prioritized next moves)
    operator_brief = facets.get("operator_brief", {})
    operator_actions = operator_brief.get("actions", []) if isinstance(operator_brief, dict) else []

    def _dedupe_context(why_now: str, project_context: str) -> str:
        """Omit project_context if its core facts are already in why_now."""
        if not why_now or not project_context:
            return project_context
        # Simple containment heuristic: if >60% of project_context words appear in why_now, skip it
        ctx_words = set(project_context.lower().split())
        why_words = set(why_now.lower().split())
        if not ctx_words:
            return project_context
        overlap = len(ctx_words & why_words) / len(ctx_words)
        return "" if overlap > 0.6 else project_context

    def _urgency_icon(card_class: str) -> str:
        if "urgent" in card_class:
            return '<svg class="action-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>'
        if "project" in card_class:
            return '<svg class="action-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
        return '<svg class="action-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>'

    for idx, action in enumerate(operator_actions[:3]):
        if not isinstance(action, dict):
            continue
        if idx == 0:
            badge_class = "action-badge-urgent"
            card_class = "action-card-urgent"
            badge_text = "Fix first"
        else:
            badge_class = "action-badge-improvement"
            card_class = "action-card-improvement"
            badge_text = "Improve"

        detail = str(action.get("detail", "")).strip()
        why_now = str(action.get("why_now", "")).strip()
        impact = str(action.get("impact", "")).strip()
        evidence = str(action.get("evidence", "")).strip()
        project_context = _dedupe_context(why_now, str(action.get("project_context", "")).strip())

        meta_items: list[str] = []
        if why_now:
            meta_items.append(f'<div class="action-meta-item"><span class="action-meta-label">Why now</span>{html.escape(why_now)}</div>')
        if impact:
            meta_items.append(f'<div class="action-meta-item"><span class="action-meta-label">Impact</span>{html.escape(impact)}</div>')
        if project_context:
            meta_items.append(f'<div class="action-meta-item"><span class="action-meta-label">Context</span>{html.escape(project_context)}</div>')

        meta_html = "\n".join(meta_items)
        evidence_html = f'<div class="action-evidence">{html.escape(evidence)}</div>' if evidence else ""
        icon_html = _urgency_icon(card_class)

        cards.append(f"""<div class="action-card {card_class}">
          <div class="action-header">
            {icon_html}
            <span class="action-badge {badge_class}">{badge_text}</span>
            <h3>{html.escape(str(action.get("title", "Action")))}</h3>
          </div>
          <div class="action-body">
            <div class="action-main">
              {html.escape(detail)}
              {evidence_html}
            </div>
            {f'<div class="action-meta">{meta_html}</div>' if meta_html else ''}
          </div>
        </div>""")

    # Fallback: dynamic improvements when no operator actions exist
    if not cards:
        improvements = dynamic.get("improvements", [])
        for idx, imp in enumerate(improvements[:3]):
            what = imp.get("what", "Improvement")
            why = imp.get("why", "")
            how = imp.get("how", "")
            badge_class = "action-badge-improvement"
            card_class = "action-card-improvement"
            badge_text = "Improve"
            icon_html = _urgency_icon(card_class)
            cards.append(f"""<div class="action-card {card_class}">
              <div class="action-header">
                {icon_html}
                <span class="action-badge {badge_class}">{badge_text}</span>
                <h3>{html.escape(what)}</h3>
              </div>
              <div class="action-body">
                <div class="action-main">
                  {html.escape(why)}
                  <div class="action-evidence">{html.escape(how)}</div>
                </div>
              </div>
            </div>""")

    # Pad with project watch if we still have room
    if len(cards) < 3:
        projects = brief.get("projects", [])
        at_risk = [p for p in projects if p.get("health") in ("yellow", "red") or p.get("blockers") not in ("none", "", None)]
        if at_risk:
            p = at_risk[0]
            icon_html = _urgency_icon("action-card-project")
            cards.append(f"""<div class="action-card action-card-project">
              <div class="action-header">
                {icon_html}
                <span class="action-badge action-badge-project">Project</span>
                <h3>{html.escape(p.get("name", "Project"))} needs attention</h3>
              </div>
              <div class="action-body">
                <div class="action-main">
                  Status: {html.escape(p.get("status", "Unknown"))}. Next milestone: {html.escape(p.get("next_milestone", "N/A"))} (due {html.escape(p.get("next_milestone_date", "?"))}).
                </div>
              </div>
            </div>""")

    if not cards:
        return ""

    cards_html = "\n".join(cards)
    return f"""<div class="action-board">
      <h2 class="action-board-title">Do these next</h2>
      <div class="action-grid">{cards_html}</div>
    </div>"""


def _transform_to_developer_dashboard(html_text: str) -> str:
    """Replace the generic report top-section with a developer-focused dashboard."""
    facts = _load_json(USAGE_ROOT / "fact-snapshots" / "facts.json")
    facets = _load_json(FACETS_JSON)
    dynamic = _load_json(DYNAMIC_JSON)
    brief = _load_json(PROJECT_BRIEF)

    narrative = _build_narrative_html(facts, facets, dynamic, brief)
    scorecard = _build_scorecard_html(facts, facets)
    action_board = _build_action_board_html(facets, dynamic, brief)
    fun_card = _build_fun_card_html(facets)

    dashboard = f"""<div class="dev-dashboard">
      {narrative}
      {scorecard}
      {action_board}
      {fun_card}
    </div>"""

    new_top = f"""<h1>Codex Usage Insights</h1>
    <p class="subtitle">Developer dashboard &bull; actionable signals from your recent sessions</p>
    {dashboard}"""

    # Remove any existing dev-dashboard blocks to prevent duplication on re-runs
    updated = re.sub(
        r'<div class="dev-dashboard">[\s\S]*?</div>\s*(?=<h2)',
        '',
        html_text,
        flags=re.DOTALL,
    )

    # Replace from h1 through the first subtitle, preserving the first h2 that follows
    pattern = r'(<h1>Codex Usage Insights</h1>.*?)(<h2[^>]*>)'
    updated = re.sub(pattern, lambda m: new_top + '\n    ' + m.group(2), updated, count=1, flags=re.DOTALL)

    if '<div class="dev-dashboard">' not in updated:
        # Fallback: inject after the first subtitle
        updated = re.sub(
            r'(<p class="subtitle">.*?</p>)',
            lambda m: m.group(1) + '\n    ' + dashboard,
            html_text,
            count=1,
            flags=re.DOTALL,
        )

    return updated

def _inject_ui_polish_script(html_text: str) -> str:
    marker = "/* insight-ui-polish-v1 */"
    script = """
    /* insight-ui-polish-v1 */
    (() => {
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const revealTargets = Array.from(
        document.querySelectorAll(".instruction-item, .feature-card, .feedback-card, .friction-category, .big-win, .project-area")
      );

      revealTargets.forEach((el, idx) => {
        el.classList.add("insight-reveal");
        el.style.setProperty("--reveal-stagger", String(idx % 10));
      });

      if (!reduceMotion && "IntersectionObserver" in window) {
        const io = new IntersectionObserver((entries, observer) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        }, { rootMargin: "0px 0px -6% 0px", threshold: 0.12 });
        revealTargets.forEach((el) => io.observe(el));
      } else {
        revealTargets.forEach((el) => el.classList.add("is-visible"));
      }

      const tocLinks = Array.from(document.querySelectorAll(".nav-toc a[href^='#']"));
      const sections = tocLinks
        .map((a) => {
          const id = a.getAttribute("href");
          if (!id) return null;
          const section = document.querySelector(id);
          if (!section) return null;
          return { a, section };
        })
        .filter(Boolean);

      if (!sections.length) return;

      const onScroll = () => {
        const y = window.scrollY + 160;
        let active = sections[0];
        for (const item of sections) {
          if (item.section.offsetTop <= y) active = item;
        }
        sections.forEach((item) => item.a.classList.toggle("is-active", item === active));
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();

      window.copyActionPrompt = function(btn, text) {
        navigator.clipboard.writeText(text).then(function() {
          var original = btn.textContent;
          btn.textContent = "Copied!";
          setTimeout(function() { btn.textContent = original; }, 2000);
        });
      };
    })();
    """
    # Remove any previous version of the polish script
    if marker in html_text:
        html_text = re.sub(
            r"\n\s*/\* insight-ui-polish-v1 \*/[\s\S]*?\}\)\(\);",
            "",
            html_text,
            count=1,
        )

    if "</script>" in html_text:
        return html_text.replace("</script>", f"{script}\n  </script>", 1)
    return f"{html_text}\n<script>{script}</script>\n"


def apply_dynamic_recommendation_overrides(html_text: str) -> str:
    payload = _build_dynamic_copy_payload(_load_facets())
    if not payload:
        return _inject_ui_polish_script(html_text)
    cards = payload.get("cards", [])
    if not isinstance(cards, list) or not cards:
        return _inject_ui_polish_script(html_text)
    updated = _apply_instruction_card_overrides(html_text, cards)
    updated = _apply_feedback_card_override(updated, cards[0])
    return _inject_ui_polish_script(updated)


def apply_theme(report_html: Path, theme: str) -> None:
    html = read_text(report_html)
    updated = html
    if theme != "dark":
        updated = re.sub(
            r":root\s*\{.*?\}",
            LIGHT_ROOT_BLOCK,
            updated,
            count=1,
            flags=re.DOTALL,
        )
        if updated == html:
            raise RuntimeError("Could not locate :root block to apply light theme")
        mermaid_replacements = {
            "theme: 'dark'": "theme: 'neutral'",
            "primaryColor: '#1e293b'": "primaryColor: '#eef2ff'",
            "primaryTextColor: '#e8eaf0'": "primaryTextColor: '#0f172a'",
            "primaryBorderColor: '#334155'": "primaryBorderColor: '#cbd5e1'",
            "lineColor: '#475569'": "lineColor: '#64748b'",
            "secondaryColor: '#0f172a'": "secondaryColor: '#ffffff'",
            "tertiaryColor: '#1e293b'": "tertiaryColor: '#f8fafc'",
        }
        for old, new in mermaid_replacements.items():
            updated = updated.replace(old, new)
    icon_replacements = {
        '<div class="card-title">〰️ Focus & Flow State</div>': '<div class="card-title icon-focus">Focus & Flow State</div>',
        '<div class="card-title">🚨 AI Artifact Tracking</div>': '<div class="card-title icon-alert">AI Artifact Tracking</div>',
        '<div class="card-title">🔒 Security Posture</div>': '<div class="card-title icon-security">Security Posture</div>',
        '<div class="card-title">🍂 Knowledge Growth</div>': '<div class="card-title icon-growth">Knowledge Growth</div>',
        '<strong>💡 Insight:</strong>': '<strong>Insight:</strong>',
        '📉 ↑ Regressing': 'Regressing',
        '📅 Next:': 'Next:',
        '<span style="color:#f59e0b">⚡</span> Automation pulse:': '<span class="inline-icon icon-bolt" aria-hidden="true"></span> Automation pulse:',
    }
    for old, new in icon_replacements.items():
        updated = updated.replace(old, new)
    updated = _transform_to_developer_dashboard(updated)
    updated = apply_dynamic_recommendation_overrides(updated)
    updated = strip_emoji(updated)
    # Inject dashboard CSS for all themes (idempotent)
    if "/* Developer Dashboard (injected for all themes) */" not in updated:
        updated = updated.replace("</style>", f"{DASHBOARD_CSS}\n  </style>", 1)
    if theme != "dark":
        updated = re.sub(
            r"\n\s*/\* Light theme overrides injected by insight-report wrapper \*/[\s\S]*?/\* End light theme overrides \*/",
            "",
            updated,
        )
        updated = updated.replace("</style>", f"{LIGHT_THEME_OVERRIDES}\n  </style>", 1)
    report_html.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.theme_only:
        otel_root = sanitize_existing_path(args.otel_root, "OTEL root")

        run_checked(["python3", str(COLLECT_SCRIPT), "--output", str(PROJECT_BRIEF)])
        run_checked(["python3", str(DYNAMIC_SCRIPT), "--json", "--output", str(DYNAMIC_JSON)])

        cmd = [
            "python3",
            str(GENERATE_SCRIPT),
            "--brief",
            str(PROJECT_BRIEF),
            "--otel-root",
            otel_root,
            "--dynamic",
        ]
        if args.days is not None:
            cmd.extend(["--days", str(args.days)])
        if args.pdf:
            cmd.append("--pdf")
        if args.include_architecture:
            cmd.append("--include-architecture")
        if args.self_optimize:
            cmd.append("--self-optimize")
        run_checked(cmd)
    else:
        assert_exists(REPORT_HTML, "HTML report")
    apply_theme(REPORT_HTML, args.theme)

    if not args.theme_only:
        assert_exists(PROJECT_BRIEF, "project brief")
    assert_exists(REPORT_HTML, "HTML report")
    if not args.theme_only:
        assert_exists(FACETS_JSON, "facets json")
        assert_exists(DYNAMIC_JSON, "dynamic insights")
    if args.pdf:
        assert_exists(REPORT_PDF, "PDF report")
    if not args.theme_only:
        assert_report_markers(REPORT_HTML, self_optimize=args.self_optimize)

    launched_mode = "not-requested"
    launched_url = ""
    if args.open_report:
        launched_mode, launched_url = launch_report(REPORT_HTML)

    print("")
    print("Your shareable insights report is ready:")
    print(f"file://{REPORT_HTML}")
    if args.pdf:
        print(f"file://{REPORT_PDF}")
    if args.open_report:
        print(f"Launch mode: {launched_mode}")
        print(f"Launch URL: {launched_url}")
    print("")
    print("Want to dig into any section or try one of the suggestions?")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
