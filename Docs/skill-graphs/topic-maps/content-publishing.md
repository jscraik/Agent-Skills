---
type: moc
name: content-publishing
description: "Skills for creating, adapting, and publishing content across video, slides, YouTube, and written media — covering scripting, visual walkthroughs, and transcript extraction."
covers:
  - video-production
  - youtube
  - presentations
  - transcripts
---

# Content & Publishing

> Skills for creating, adapting, and publishing content across video, slides, YouTube, and written media.

## Table of Contents
- [Video Production & AI Video](#video-production--ai-video)
- [YouTube Strategy](#youtube-strategy)
- [Slides & Presentations](#slides--presentations)
- [Written Content & Transcripts](#written-content--transcripts)

---

## Video Production & AI Video

- [[sora]] — Generate, remix, poll, list, download Sora videos via the OpenAI video API; batch generation.
- [[remotion]] — Best-practice guidance for Remotion (React video): compositions, timing, assets, audio, captions, rendering.

## YouTube Strategy

- [[youtube-titles-thumbnails]] — Generate SEO/CTR-optimized YouTube title and thumbnail text options with variants and rationale.
- [[youtube-hooks-scripts]] — Create high-retention hooks and full scripts for technical YouTube videos tailored to topic, audience, and length.

## Slides & Presentations

- [[slides]] — Create, edit, analyze, and validate `.pptx` slide decks with PptxGenJS, editable PowerPoint output, and overflow checks.
- [[visual-explainer]] — Generate beautiful, self-contained HTML pages to visually explain systems, code changes, plans, or data.

## Written Content & Transcripts

- [[video-transcript-downloader]] — Extract, summarize, and download video/audio/subtitles using yt-dlp/ffmpeg.
- [[markdown-converter]] — Convert source files into Markdown outputs using the bundled converter workflow.
- [[spreadsheet]] — Create, edit, analyze, and format spreadsheets (.xlsx, .csv, .tsv) with formula-aware workflows.
- [[llm-wiki]] — Build and maintain a persistent markdown wiki from source material and transcripts.

---

## Pipelines

- YouTube workflow: [[youtube-hooks-scripts]] → [[youtube-titles-thumbnails]] → (record and upload).
- Demo walkthrough: [[visual-explainer]] → [[slides]] → [[remotion]] → upload.
- Research-to-publish: [[video-transcript-downloader]] → [[llm-wiki]] → [[markdown-converter]].

## Cross-links

- Need images or assets? [[imagegen]], [[sora]], [[favicon-generator]] are in [[frontend-ui]].
- Topic maps: [[frontend-ui]] | [[product-strategy]]
