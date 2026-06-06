from __future__ import annotations

import ast
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_CONTRACT_MODULES = (
    REPO_ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py",
    REPO_ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py",
    REPO_ROOT / "Infrastructure/scripts/lib/ask/envelope.py",
)


class TestSkillsSdkNoAnyContracts(unittest.TestCase):
    def test_public_contract_modules_do_not_use_any(self) -> None:
        offenders: list[str] = []
        for path in PUBLIC_CONTRACT_MODULES:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == "Any":
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
                if isinstance(node, ast.Attribute) and node.attr == "Any":
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
