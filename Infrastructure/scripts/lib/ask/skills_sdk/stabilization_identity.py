from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ALGORITHM = "skills-sdk.stabilization-patch-identity.v1"


def build_patch_identity(repo_root: Path, relative_paths: list[str]) -> dict[str, object]:
    """Hash stable files as sorted UTF-8 `path NUL sha256hex LF` records."""
    normalized = sorted(set(relative_paths), key=lambda value: value.encode("utf-8"))
    records: list[bytes] = []
    files: dict[str, str] = {}
    resolved_root = repo_root.resolve()
    for relative in normalized:
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"path must be repo-relative and not escape repo root: {relative}")
        path = (resolved_root / candidate).resolve()
        path.relative_to(resolved_root)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files[relative] = f"sha256:{digest}"
        records.append(relative.encode("utf-8") + b"\0" + digest.encode("ascii") + b"\n")
    identity = hashlib.sha256(b"".join(records)).hexdigest()
    return {
        "algorithm": ALGORITHM,
        "serialization": "UTF-8 relative_path NUL sha256hex LF; paths unique and sorted bytewise",
        "identity": f"sha256:{identity}",
        "paths": normalized,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    print(json.dumps(build_patch_identity(args.repo_root.resolve(), args.paths), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
