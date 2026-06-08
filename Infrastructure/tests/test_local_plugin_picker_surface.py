import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SOURCE_PLUGIN_SKILLS = {
    "aidevcon": {
        "talk-azriel-executable-specs",
        "talk-baker-sadogursky-context-engineering-skills",
        "talk-batey-building-product-teams-age-of-ai",
        "talk-birgitta-closing-keynote",
        "talk-cormack-tests-lie-observability-ai",
        "talk-debois-agent-enablement",
        "talk-douglas-training-ai-on-your-own-code",
        "talk-dubnov-merge-rate-ai-adoption",
        "talk-farley-vibe-coding-best-we-can-do",
        "talk-firtman-web-mcp-agentic-web",
        "talk-foxwell-reinvention-dev-team",
        "talk-groetzinger-skills-everywhere",
        "talk-jones-odevo-ai-native-transformation",
        "talk-jourdan-pipelines-to-prompts",
        "talk-katsioloudes-code-security-ai",
        "talk-kerr-bipolar-disorder-dysregulation-ai",
        "talk-kushwaha-benchmarking-agent-era",
        "talk-lamis-context-engineering-dreaming",
        "talk-lawson-agent-experience",
        "talk-lopopolo-harness-engineering",
        "talk-luebken-embedding-pi-coding-agent",
        "talk-maleix-collective-intelligence",
        "talk-maple-aind-devcon-welcome",
        "talk-marsden-agent-desktops",
        "talk-martinelli-spec-driven-development",
        "talk-moss-skills-team-workflow",
        "talk-obstbaum-willoughby-vibes-to-metrics",
        "talk-overweg-one-brain-no-filtering",
        "talk-podjarny-skills-are-the-new-code",
        "talk-roberts-ai-native-brownfield",
        "talk-roberts-brownfield-ai-native",
        "talk-ruiz-agents-on-canvas-tldraw",
        "talk-scheire-artificial-intelligence",
        "talk-selajev-docker-sandboxes-agents",
        "talk-sloan-harness-engineering-beyond-code",
        "talk-smith-connecting-context-future-transports",
        "talk-stack-humans-architect-ai-writes-code",
        "talk-stoneham-product-brain",
        "talk-syme-agentic-repository-automation",
        "talk-tal-skills-security",
        "talk-thomas-ai-native-engineering",
        "talk-trieloff-browser-agents",
        "talk-walter-runtime-intelligence-agents",
        "talk-wilson-cq-stack-overflow-for-agents",
        "talk-wotherspoon-humans-vs-slop",
    },
    "harness-engineering": {
        "he-brainstorm",
        "he-code-review",
        "he-eval-report",
        "he-fix-bugs",
        "he-heartbeat",
        "he-improve",
        "he-linear-plan",
        "he-plan",
        "he-phase-work",
        "he-reconcile",
        "he-reframe",
        "he-reinforce",
        "he-router",
        "he-spec",
        "he-strategy",
        "he-work",
    },
    "plugin-factory": {
        "plugin-builder",
        "plugin-factory-router",
        "plugin-router",
    },
    "skill-factory": {
        "skill-builder",
        "skill-factory-router",
        "skill-refactor",
        "skillify",
    },
    "synaipse-harness": {
        "sy-brainstorm",
        "sy-eval-report",
        "sy-execution-plan",
        "sy-reconcile",
        "sy-reframe",
        "sy-reinforce",
        "sy-review",
        "sy-slice-spec",
        "sy-strategy",
        "sy-trace-plan",
        "sy-tracker-plan",
        "sy-work",
    },
}

EXPECTED_MARKETPLACE_SOURCE_PATHS = {
    "aidevcon": "./Plugins/aidevcon",
    "harness-engineering": "./Plugins/harness-engineering",
    "plugin-factory": "./Plugins/plugin-factory",
    "skill-factory": "./Plugins/skill-factory",
    "synaipse-harness": "./Plugins/synaipse-harness",
}

EXPECTED_PLUGIN_KEYWORDS = {
    "plugin-factory": {
        "plugin-factory-router",
        "plugin-router",
        "plugin-builder",
    },
    "skill-factory": {
        "skill-factory-router",
        "skill-builder",
        "skill-refactor",
        "skillify",
    },
    "synaipse-harness": {
        "sy-strategy",
        "sy-reframe",
        "sy-brainstorm",
        "sy-trace-plan",
        "sy-tracker-plan",
        "sy-slice-spec",
        "sy-execution-plan",
        "sy-work",
        "sy-review",
        "sy-eval-report",
        "sy-reconcile",
        "sy-reinforce",
    },
}

EXPECTED_SYNAIPSE_LIFECYCLE = [
    ("strategy", "sy-strategy", None, "reframe"),
    ("reframe", "sy-reframe", "strategy", "brainstorm"),
    ("brainstorm", "sy-brainstorm", "reframe", "trace-plan"),
    ("trace-plan", "sy-trace-plan", "brainstorm", "tracker-plan"),
    ("tracker-plan", "sy-tracker-plan", "trace-plan", "slice-spec"),
    ("slice-spec", "sy-slice-spec", "tracker-plan", "execution-plan"),
    ("execution-plan", "sy-execution-plan", "slice-spec", "work"),
    ("work", "sy-work", "execution-plan", "review"),
    ("review", "sy-review", "work", "eval-report"),
    ("eval-report", "sy-eval-report", "review", "reconcile"),
    ("reconcile", "sy-reconcile", "eval-report", "reinforce"),
    ("reinforce", "sy-reinforce", "reconcile", "strategy"),
]

LEGACY_SYNAIPSE_SKILL_NAMES = {
    "sy-spec",
    "sy-phase-work",
    "sy-improve",
    "sy-fix-bugs",
    "sy-router",
    "sy-heartbeat",
}

SYSTEM_BRIDGE_SKILL_NAMES = {
    "imagegen",
    "openai-docs",
    "plugin-creator",
    "plugin-installer",
    "skill-creator",
    "skill-installer",
}

EXPECTED_CACHE_ALIAS_SKILLS = {
    "plugin-factory": {
        "plugin-creator",
        "plugin-installer",
    },
}

HIDDEN_PICKER_COMPATIBILITY_SKILLS = {
    "he-goal-governor-archive",
    "he-ideate",
    "he-phase-heartbeat",
    "he-refactor",
    "he-refine",
    "he-reliability-review",
    "he-technical-review",
}

def _read_frontmatter_text(skill_md: Path) -> str:
    raw = skill_md.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return ""
    end = raw.find("\n---", 4)
    if end == -1:
        return ""
    return raw[4:end]


def _is_hidden_skill(skill_md: Path) -> bool:
    frontmatter = _read_frontmatter_text(skill_md)
    hidden_markers = (
        "runtime-visibility: hidden",
        "runtime_visibility: hidden",
        "command-visibility: none",
        "command_visibility: none",
        "lifecycle: deprecated",
        "lifecycle_state: archived",
    )
    return any(marker in frontmatter for marker in hidden_markers)


def _direct_visible_skill_names(skills_root: Path) -> set[str]:
    return {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir()
        and (child / "SKILL.md").exists()
        and not _is_hidden_skill(child / "SKILL.md")
    }


def _expected_cache_skill_names(plugin_name: str) -> set[str]:
    return (
        EXPECTED_SOURCE_PLUGIN_SKILLS[plugin_name]
        | EXPECTED_CACHE_ALIAS_SKILLS.get(plugin_name, set())
    ) - HIDDEN_PICKER_COMPATIBILITY_SKILLS


def _unexpected_system_bridge_skill_names(plugin_name: str, discovered: set[str]) -> set[str]:
    return discovered & (SYSTEM_BRIDGE_SKILL_NAMES - EXPECTED_CACHE_ALIAS_SKILLS.get(plugin_name, set()))


class LocalPluginPickerSurfaceTests(unittest.TestCase):
    def test_local_marketplace_lists_only_expected_local_plugins(self) -> None:
        """
        Verify the repository marketplace lists exactly the expected local plugins.
        
        Reads Plugins/marketplace.json and asserts the set of plugin `name` entries equals EXPECTED_SOURCE_PLUGIN_SKILLS.
        """
        marketplace_path = REPO_ROOT / "Plugins" / "marketplace.json"
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        names = {
            item["name"]
            for item in payload.get("plugins", [])
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }
        self.assertEqual(names, set(EXPECTED_SOURCE_PLUGIN_SKILLS))

    def test_local_marketplace_uses_canonical_agent_skills_identity(self) -> None:
        """
        Verify the local marketplace identity matches the runtime cache family.
        """
        marketplace_path = REPO_ROOT / "Plugins" / "marketplace.json"
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("name"), "agent-skills-local")

    def test_local_plugins_use_canonical_marketplace_source_paths(self) -> None:
        """
        Verify that each expected local plugin uses the canonical './Plugins/<plugin-name>' marketplace source path.
        
        Asserts that every plugin listed in the repository marketplace manifest exposes a `source.path` exactly equal to the canonical `./Plugins/<plugin-name>` value from EXPECTED_MARKETPLACE_SOURCE_PATHS.
        """
        marketplace_path = REPO_ROOT / "Plugins" / "marketplace.json"
        payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        by_name = {
            item["name"]: item
            for item in payload.get("plugins", [])
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        }

        for plugin_name, expected_path in EXPECTED_MARKETPLACE_SOURCE_PATHS.items():
            plugin = by_name[plugin_name]
            self.assertEqual(
                plugin.get("source", {}).get("path"),
                expected_path,
                f"{plugin_name} should use the canonical ./Plugins/<name> marketplace source path",
            )

    def test_local_plugins_use_first_level_skills_root(self) -> None:
        """
        Verify each expected plugin's `.codex-plugin/plugin.json` declares the skills root as "./skills/".
        
        Raises an assertion failure for any plugin whose `skills` field is not exactly "./skills/".
        """
        for plugin_name in EXPECTED_SOURCE_PLUGIN_SKILLS:
            manifest_path = REPO_ROOT / "Plugins" / plugin_name / ".codex-plugin" / "plugin.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload.get("skills"),
                "./skills/",
                f"{plugin_name} should expose plugin skills from ./skills/",
            )

    def test_local_plugins_expose_all_expected_skills_at_first_level(self) -> None:
        """
        Verify each expected local plugin exposes exactly the declared first-level skills.
        
        For each plugin in EXPECTED_SOURCE_PLUGIN_SKILLS, scan Plugins/<plugin>/skills for immediate subdirectories that contain a SKILL.md file and assert the set of those direct skill names equals the expected set; failures use the message "<plugin> first-level plugin picker surface drifted".
        """
        for plugin_name, expected_skill_names in EXPECTED_SOURCE_PLUGIN_SKILLS.items():
            skills_root = REPO_ROOT / "Plugins" / plugin_name / "skills"
            direct_skill_names = _direct_visible_skill_names(skills_root)
            self.assertEqual(
                direct_skill_names,
                expected_skill_names,
                f"{plugin_name} first-level plugin picker surface drifted",
            )

    def test_synaipse_harness_uses_deterministic_sdk_lifecycle_shape(self) -> None:
        """
        Verify SynAIpse exposes exactly the canonical stage lifecycle and SDK metadata files.
        """
        plugin_root = REPO_ROOT / "Plugins" / "synaipse-harness"
        skills_root = plugin_root / "skills"
        routing_map_path = plugin_root / "references" / "routing-map.json"
        routing_map = json.loads(routing_map_path.read_text(encoding="utf-8"))

        expected_stages = [stage for stage, _, _, _ in EXPECTED_SYNAIPSE_LIFECYCLE]
        expected_handles = [handle for _, handle, _, _ in EXPECTED_SYNAIPSE_LIFECYCLE]
        direct_skill_names = _direct_visible_skill_names(skills_root)

        self.assertEqual(expected_handles, [entry["handle"] for entry in routing_map["stages"]])
        self.assertEqual(expected_stages, routing_map["lifecycle_stage_order"])
        self.assertEqual(set(expected_handles), direct_skill_names)
        self.assertFalse(
            LEGACY_SYNAIPSE_SKILL_NAMES & direct_skill_names,
            "SynAIpse should not expose legacy or compatibility skills as picker entries",
        )

        for stage, handle, previous_stage, next_stage in EXPECTED_SYNAIPSE_LIFECYCLE:
            skill_dir = skills_root / handle
            skill_md = skill_dir / "SKILL.md"
            contract = skill_dir / "references" / "contract.yaml"
            evals = skill_dir / "references" / "evals.yaml"
            task_profile = skill_dir / "references" / "task-profile.json"
            openai_metadata = skill_dir / "agents" / "openai.yaml"

            for path in (skill_md, contract, evals, task_profile, openai_metadata):
                self.assertTrue(path.exists(), f"{handle} should include {path.relative_to(skill_dir)}")

            skill_frontmatter = _read_frontmatter_text(skill_md)
            self.assertIn(f"name: {handle}", skill_frontmatter)
            self.assertIn(f"sdk_stage: {stage}", skill_frontmatter)
            self.assertIn("lifecycle_state: active", skill_frontmatter)
            self.assertIn("command_visibility: orchestrator", skill_frontmatter)

            contract_text = contract.read_text(encoding="utf-8")
            expected_previous = previous_stage if previous_stage is not None else "none"
            self.assertIn(f"skill: {handle}", contract_text)
            self.assertIn(f"stage: {stage}", contract_text)
            self.assertIn(f"previous_stage: {expected_previous}", contract_text)
            self.assertIn(f"next_stage: {next_stage}", contract_text)

            evals_text = evals.read_text(encoding="utf-8")
            self.assertIn(f'skill_name: "{handle}"', evals_text)
            self.assertIn(f'stage: "{stage}"', evals_text)

            profile_payload = json.loads(task_profile.read_text(encoding="utf-8"))
            self.assertEqual(f"Plugins/synaipse-harness/skills/{handle}", profile_payload["scope_skill"])
            self.assertEqual(stage, profile_payload["sdk_stage"])

            openai_text = openai_metadata.read_text(encoding="utf-8")
            self.assertIn(f'sdk_stage: "{stage}"', openai_text)
            self.assertIn(f'handle: "{handle}"', openai_text)

    def test_local_plugins_expose_openai_metadata_for_first_level_skills(self) -> None:
        """
        Verify each expected first-level skill directory contains an agents/openai.yaml metadata file.
        
        For each plugin declared in EXPECTED_SOURCE_PLUGIN_SKILLS, the test checks every expected skill (sorted) under Plugins/<plugin>/skills/<skill>/agents/openai.yaml; any missing file paths are collected (relative to REPO_ROOT) and the test fails if the collection is non-empty.
        """
        for plugin_name, expected_skill_names in EXPECTED_SOURCE_PLUGIN_SKILLS.items():
            skills_root = REPO_ROOT / "Plugins" / plugin_name / "skills"
            missing = []
            for skill_name in sorted(expected_skill_names):
                skill_dir = skills_root / skill_name
                metadata_path = skill_dir / "agents" / "openai.yaml"
                if not metadata_path.exists():
                    missing.append(str(metadata_path.relative_to(REPO_ROOT)))
            self.assertEqual([], missing, f"{plugin_name} is missing skill-level OpenAI metadata")

    def test_local_plugin_manifests_describe_visible_skill_surface(self) -> None:
        """
        Validate that each local plugin manifest describes its visible skill surface.
        
        For every plugin listed in EXPECTED_PLUGIN_KEYWORDS, assert that the manifest's `keywords` include the expected visible-skill keywords and do not contain hidden system-bridge skills.
        """
        for plugin_name, expected_keywords in EXPECTED_PLUGIN_KEYWORDS.items():
            manifest_path = REPO_ROOT / "Plugins" / plugin_name / ".codex-plugin" / "plugin.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            keywords = set(payload.get("keywords", []))
            self.assertTrue(
                expected_keywords.issubset(keywords),
                f"{plugin_name} manifest keywords should include the visible skill surface",
            )
            self.assertFalse(
                SYSTEM_BRIDGE_SKILL_NAMES & keywords,
                f"{plugin_name} manifest should not advertise hidden system-bridge skills",
            )

    def test_runtime_cache_preserves_manifest_declared_skills(self) -> None:
        """
        Verify the generated local plugin cache preserves loader-declared skills.

        The runtime cache must remain a complete Codex loader package while
        exposing only one visible path for each skill identity.
        """
        runtime_root = REPO_ROOT / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local"
        if not runtime_root.exists():
            self.skipTest("local plugin runtime cache has not been generated")

        for plugin_name in EXPECTED_SOURCE_PLUGIN_SKILLS:
            expected_skill_names = _expected_cache_skill_names(plugin_name)
            plugin_root = runtime_root / plugin_name
            self.assertTrue(
                plugin_root.is_dir(),
                f"{plugin_name} should expose a runtime plugin cache root",
            )
            discovered: dict[str, list[str]] = {}
            for skill_md in sorted(plugin_root.rglob("SKILL.md")):
                rel = skill_md.relative_to(plugin_root).as_posix()
                if rel.startswith("references/"):
                    continue
                if _is_hidden_skill(skill_md):
                    continue
                discovered.setdefault(skill_md.parent.name, []).append(rel)

            duplicates = {
                name: paths for name, paths in discovered.items() if len(paths) > 1
            }
            self.assertEqual({}, duplicates, f"{plugin_name} runtime cache exposes duplicate skill identities")
            self.assertEqual(
                set(discovered),
                expected_skill_names,
                f"{plugin_name} runtime cache loader package drifted",
            )
            self.assertFalse(
                _unexpected_system_bridge_skill_names(plugin_name, set(discovered)),
                f"{plugin_name} runtime cache should not expose unrelated system bridge skills as personal skills",
            )

    def test_versioned_plugin_cache_preserves_manifest_declared_skills(self) -> None:
        """
        Verify the local versioned plugin cache preserves loader-declared skills.

        Some loader paths still inspect
        "Plugins/cache/agent-skills-local/<plugin>/<version>/skills".
        Keep that package cache aligned with the first-level plugin surface.
        """
        cache_root = REPO_ROOT / "Plugins" / "cache" / "agent-skills-local"
        if not cache_root.exists():
            self.skipTest("versioned local plugin cache has not been generated")

        for plugin_name in EXPECTED_SOURCE_PLUGIN_SKILLS:
            expected_skill_names = _expected_cache_skill_names(plugin_name)
            plugin_cache_root = cache_root / plugin_name
            self.assertTrue(
                plugin_cache_root.exists(),
                f"{plugin_name} should expose a versioned local cache root",
            )
            version_dirs = [
                child for child in plugin_cache_root.iterdir()
                if child.is_dir() and child.name not in {"local"}
            ]
            self.assertEqual(
                1,
                len(version_dirs),
                f"{plugin_name} should expose exactly one versioned local cache root",
            )
            skills_root = version_dirs[0] / "skills"
            self.assertTrue(
                skills_root.is_dir(),
                f"{plugin_name} should expose a versioned local cache skills root",
            )
            discovered_paths: dict[str, list[str]] = {}
            for skill_md in sorted(skills_root.rglob("SKILL.md")):
                if _is_hidden_skill(skill_md):
                    continue
                rel = skill_md.relative_to(skills_root).as_posix()
                discovered_paths.setdefault(skill_md.parent.name, []).append(rel)

            duplicates = {
                name: paths for name, paths in discovered_paths.items() if len(paths) > 1
            }
            self.assertEqual({}, duplicates, f"{plugin_name} versioned plugin cache exposes duplicate skill identities")
            self.assertEqual(
                expected_skill_names,
                set(discovered_paths),
                f"{plugin_name} versioned plugin cache picker surface drifted",
            )

    def test_delegated_home_plugin_mirror_prunes_command_surface_duplicates(self) -> None:
        """
        Verify the ask-engine user sync path prunes command-surface duplicate skills from home mirrors.
        """
        sync_source = REPO_ROOT / "Infrastructure" / "scripts" / "lib" / "ask" / "commands" / "skills_impl.py"
        source = sync_source.read_text(encoding="utf-8")
        mirror_function = source.split("def _refresh_home_plugin_mirrors(", 1)[1].split("def _sync_rooted_projection(", 1)[0]
        self.assertIn("prune_command_surface_duplicate_skill_entries", mirror_function)
        self.assertIn("Skipped replacing protected home plugin mirror", mirror_function)
        self.assertIn("except OSError as exc", mirror_function)
        self.assertNotIn("duplicate pruning belongs to runtime cache copies", mirror_function)

    def test_delegated_user_sync_refreshes_codex_profile_plugin_mirrors(self) -> None:
        """
        Verify the ask-engine user sync refreshes Codex profile plugin mirrors.
        """
        sync_source = REPO_ROOT / "Infrastructure" / "scripts" / "lib" / "ask" / "commands" / "skills_impl.py"
        source = sync_source.read_text(encoding="utf-8")
        user_sync = source.split("def _append_user_runtime_relinks(", 1)[1].split("def _ensure_real_plugin_mirror_root(", 1)[0]
        self.assertIn("_codex_profile_homes(home)", user_sync)
        self.assertIn('profile_home / "plugins"', user_sync)
        self.assertIn('profile_home / "Plugins"', user_sync)
        self.assertIn('profile_home / ".agents" / "plugins"', user_sync)


if __name__ == "__main__":
    unittest.main()
