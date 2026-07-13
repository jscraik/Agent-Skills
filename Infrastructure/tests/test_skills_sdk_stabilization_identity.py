from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_identity import ALGORITHM, build_patch_identity  # noqa: E402


class TestStabilizationPatchIdentity(unittest.TestCase):
    def test_identity_recomputes_from_declared_serialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "b.txt").write_text("b", encoding="utf-8")
            (root / "a.txt").write_text("a", encoding="utf-8")
            payload = build_patch_identity(root, ["b.txt", "a.txt", "a.txt"])
            records = b"".join(
                path.encode("utf-8")
                + b"\0"
                + str(payload["files"][path]).removeprefix("sha256:").encode("ascii")
                + b"\n"
                for path in payload["paths"]
            )

        self.assertEqual(payload["algorithm"], ALGORITHM)
        self.assertEqual(payload["paths"], ["a.txt", "b.txt"])
        self.assertEqual(payload["identity"], f"sha256:{hashlib.sha256(records).hexdigest()}")


if __name__ == "__main__":
    unittest.main()
