import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(module_name: str, relative_path: str):
    """
    Load a Python module from a file path relative to the repository root and return the imported module.
    
    Parameters:
        module_name (str): The name to assign to the loaded module.
        relative_path (str | os.PathLike): Path relative to the repository root pointing to the module file.
    
    Returns:
        module: The imported module object.
    
    Raises:
        RuntimeError: If the module spec or its loader cannot be created for the resolved file path.
    """
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parse_plain_review = load_module(
    "parse_plain_review",
    "Plugins/coderabbit/skills/code_quality_review/code-review/scripts/parse_plain_review.py",
)
fetch_unresolved_threads = load_module(
    "fetch_unresolved_threads",
    "Plugins/coderabbit/skills/code_quality_review/autofix/scripts/fetch_unresolved_threads.py",
)


class TestParsePlainReview(unittest.TestCase):
    def test_parse_groups_headings_and_tagged_lines(self) -> None:
        text = """
        Critical:
        - Null pointer panic in cache handler
        Warnings:
        - [warning] Retry loop lacks jitter
        Info:
        - [info] Consider extracting helper
        """

        payload = parse_plain_review.parse_plain_output(text)

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["findings"]["critical"], ["Null pointer panic in cache handler"])
        self.assertEqual(payload["findings"]["warning"], ["Retry loop lacks jitter"])
        self.assertEqual(payload["findings"]["info"], ["Consider extracting helper"])
        self.assertTrue(payload["actions"][0].startswith("[CRITICAL]"))

    def test_parse_collects_unclassified_bullets_when_no_heading(self) -> None:
        text = """
        - orphan bullet one
        - orphan bullet two
        """
        payload = parse_plain_review.parse_plain_output(text)
        self.assertEqual(payload["findings"]["critical"], [])
        self.assertEqual(payload["findings"]["warning"], [])
        self.assertEqual(payload["findings"]["info"], [])
        self.assertEqual(
            payload["findings"]["unclassified"],
            ["orphan bullet one", "orphan bullet two"],
        )
        self.assertEqual(payload["risk_note"], "No critical or warning issues detected.")


class TestFetchUnresolvedThreads(unittest.TestCase):
    def test_extract_filters_resolved_and_non_coderabbit_authors(self) -> None:
        """
        Verifies that only unresolved review thread comments authored by `coderabbitai` are extracted.
        
        Provides three thread fixtures: an unresolved thread with a `coderabbitai` comment, an unresolved thread with a non-Coderabbit author, and a resolved thread authored by a bot. Asserts that the extractor returns exactly the unresolved `coderabbitai` comment and that its `comment_id` and `path` match the expected values.
        """
        threads = [
            {
                "isResolved": False,
                "path": "src/a.ts",
                "line": 12,
                "startLine": 11,
                "comments": {
                    "nodes": [
                        {"databaseId": 10, "body": "fix this", "author": {"login": "coderabbitai"}}
                    ]
                },
            },
            {
                "isResolved": False,
                "path": "src/b.ts",
                "line": 20,
                "startLine": 20,
                "comments": {"nodes": [{"databaseId": 11, "body": "note", "author": {"login": "human"}}]},
            },
            {
                "isResolved": True,
                "path": "src/c.ts",
                "line": 30,
                "startLine": 30,
                "comments": {
                    "nodes": [
                        {
                            "databaseId": 12,
                            "body": "resolved",
                            "author": {"login": "coderabbitai[bot]"},
                        }
                    ]
                },
            },
        ]

        results = fetch_unresolved_threads._extract_unresolved_threads(threads)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["comment_id"], 10)
        self.assertEqual(results[0]["path"], "src/a.ts")

    def test_collect_review_threads_paginates(self) -> None:
        """
        Verifies that _collect_review_threads paginates GraphQL responses and aggregates nodes from multiple pages.
        
        Patches the GraphQL runner to return two pages of review thread data and asserts that the collected nodes preserve order across pages and that the GraphQL call is invoked once per page.
        """
        first = {
            "data": {
                "repository": {
                    "pullRequest": {
                        "reviewThreads": {
                            "nodes": [{"id": "T1"}],
                            "pageInfo": {"hasNextPage": True, "endCursor": "CURSOR_1"},
                        }
                    }
                }
            }
        }
        second = {
            "data": {
                "repository": {
                    "pullRequest": {
                        "reviewThreads": {
                            "nodes": [{"id": "T2"}],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        }

        with patch.object(
            fetch_unresolved_threads,
            "_run_gh_graphql",
            side_effect=[first, second],
        ) as mocked:
            result = fetch_unresolved_threads._collect_review_threads("o", "r", 123)

        self.assertEqual([node["id"] for node in result], ["T1", "T2"])
        self.assertEqual(mocked.call_count, 2)
        # Ensure page-2 fetch uses page-1 endCursor.
        self.assertIn("CURSOR_1", repr(mocked.call_args_list[1]))


if __name__ == "__main__":
    unittest.main()
