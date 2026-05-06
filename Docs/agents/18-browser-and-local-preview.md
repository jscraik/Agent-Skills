# Browser and Local Preview

## Purpose

Keep local preview fallback guidance available without loading it into every
repo task.

## Local Files

When browser tooling cannot access local files directly, serve the relevant
directory with Python:

```bash
python3 -m http.server
```

Run the server from the directory that contains the files you need to preview,
then open the localhost URL in the browser tool.
