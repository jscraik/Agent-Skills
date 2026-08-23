# Browser and Local Preview

## Purpose

Keep local preview fallback guidance available without loading it into every
repo task.

## Local Files

When browser tooling cannot access local files directly, serve the relevant
directory with Python:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory <preview-root>
```

Replace `<preview-root>` with the directory that contains the files to preview,
then open `http://127.0.0.1:8000/` in the browser tool.
