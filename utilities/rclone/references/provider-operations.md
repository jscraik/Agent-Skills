# rclone Provider Operations

Read when: a user needs provider-specific remote setup, common transfer commands, large-file guidance, or troubleshooting detail that should not live in the wrapper.

Imported from the upstream `rclone` skill in `EveryInc/compound-engineering-plugin` commit `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`, adapted for the local utility skill.

## Purpose

Use `rclone` to upload, sync, inspect, and verify files across cloud storage providers and other remote backends.

## Setup check

Before any live `rclone` operation:
- verify `rclone` is installed
- verify remotes are configured
- test connectivity when a remote exists

Use `scripts/check_setup.sh` for the deterministic setup check.

## Install guidance

Typical install options:
- macOS: `brew install rclone`
- Linux script installer: `curl https://rclone.org/install.sh | sudo bash`
- distro packages such as `apt` or `dnf`

## Remote configuration

Interactive path:

```bash
rclone config
```

Common provider quick reference:

| Provider | Type | Key settings |
|---|---|---|
| AWS S3 | `s3` | access key, secret key, region |
| Cloudflare R2 | `s3` | access key, secret key, endpoint |
| Backblaze B2 | `b2` | key ID, application key |
| DigitalOcean Spaces | `s3` | access key, secret key, endpoint |
| Google Drive | `drive` | OAuth flow |
| Dropbox | `dropbox` | OAuth flow |

### Example: Cloudflare R2

```bash
rclone config create r2 s3 \
  provider=Cloudflare \
  access_key_id=YOUR_ACCESS_KEY \
  secret_access_key=YOUR_SECRET_KEY \
  endpoint=ACCOUNT_ID.r2.cloudflarestorage.com \
  acl=private
```

### Example: AWS S3

```bash
rclone config create aws s3 \
  provider=AWS \
  access_key_id=YOUR_ACCESS_KEY \
  secret_access_key=YOUR_SECRET_KEY \
  region=us-east-1
```

## Common operations

### Upload a single file

```bash
rclone copy /path/to/file.mp4 remote:bucket/path/ --progress
```

### Upload a directory

```bash
rclone copy /path/to/folder remote:bucket/folder/ --progress
```

### Sync a directory

Use only when mirror semantics are intended.

```bash
rclone sync /local/path remote:bucket/path/ --progress
```

### List remote contents

```bash
rclone ls remote:bucket/
rclone lsd remote:bucket/
```

### Preview a transfer

```bash
rclone copy /path remote:bucket/ --dry-run
```

## Useful flags

| Flag | Purpose |
|---|---|
| `--progress` | show transfer progress |
| `--dry-run` | preview without transferring |
| `-v` | verbose output |
| `--transfers=N` | control parallel transfers |
| `--bwlimit=RATE` | limit bandwidth |
| `--checksum` | compare by checksum |
| `--exclude=\"*.tmp\"` | exclude patterns |
| `--include=\"*.mp4\"` | include patterns |
| `--min-size=SIZE` | skip smaller files |
| `--max-size=SIZE` | skip larger files |

## Large file uploads

For large videos or archives, preserve chunking and retry guidance:

```bash
rclone copy large_video.mp4 remote:bucket/ --s3-chunk-size=64M --progress
```

```bash
rclone copy /path remote:bucket/ --progress --retries=5
```

## Verification

```bash
rclone check /local/file remote:bucket/file
rclone lsl remote:bucket/path/to/file
```

## Troubleshooting

```bash
rclone lsd remote:
rclone lsd remote: -vv
rclone config show remote
```

Local adaptation notes:
- keep secrets redacted in normal chat output
- treat `sync` as destructive and require clear intent
- prefer dry-run examples before live transfers unless the user explicitly wants execution-ready commands
