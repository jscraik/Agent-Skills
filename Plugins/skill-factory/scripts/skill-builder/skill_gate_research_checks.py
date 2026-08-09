from skill_gate_core import *  # noqa: F403

def check_research_scope_focus(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    corpus = f"{doc.frontmatter.get('description', '')}\n{doc.body}"
    surfaces = _research_surface_count(corpus)
    focus_signals = _focus_language_count(corpus)

    if surfaces >= 6 and focus_signals == 0:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_SCOPE_OVERBUNDLED",
            "Skill/package scope looks broad across many surfaces without explicit narrowing guidance. Prefer the smallest viable package boundary first.",
            evidence=f"surfaces={surfaces}",
        ))
    elif surfaces >= 4 and focus_signals <= 1:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_SCOPE_BROAD",
            "Skill/package scope may be too broad for a first pass. Add explicit guidance like 'start with 2-3 focused surfaces' or 'keep scope tight'.",
            evidence=f"surfaces={surfaces}",
        ))

    return out


def check_research_example_quality(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    examples_text = _find_section_text(doc.body, ["examples", "example prompts"])
    if not examples_text:
        return out

    examples = re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+.+$", examples_text)
    quoted_examples = re.findall(r'`[^`]{10,}`|"[^"\n]{10,}"', examples_text)
    if len(examples) + len(quoted_examples) < 2:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EXAMPLES_THIN",
            "Examples section is present but thin. Add 2-3 realistic trigger prompts or worked examples.",
            evidence="## Examples",
        ))

    realism_signals = ("when the user asks", "user says", "github", "convert", "validate", "inspect", "migrate")
    realism_hits = sum(1 for signal in realism_signals if signal in examples_text.lower())
    if realism_hits == 0:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EXAMPLES_SYNTHETIC",
            "Examples look abstract or template-like. Prefer realistic user requests and concrete workflows.",
            evidence="## Examples",
        ))

    return out


def check_research_eval_prompt_realism(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    skill_dir = doc.path.parent
    evals_path = skill_dir / "references" / "evals.yaml"
    if not evals_path.exists():
        return out

    try:
        obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        out.append(Finding(Level.WARN, "RESEARCH_EVALS_PARSE", f"Could not parse evals.yaml for realism checks: {exc}"))
        return out

    if not isinstance(obj, dict) or not isinstance(obj.get("cases"), list):
        return out

    skill_name = str(doc.frontmatter.get("name", "")).strip().lower()
    cases = [case for case in obj["cases"] if isinstance(case, dict)]
    trigger_cases = [
        case for case in cases
        if case.get("should_trigger") is not False and str(case.get("category", "")).strip().lower() != "negative"
    ]
    if not trigger_cases:
        return out

    natural_request_tokens = ("please", "can you", "help me", "github", "convert", "validate", "build", "inspect")
    placeholder_tokens = ("todo", "tbd", "lorem ipsum", "example prompt", "test prompt", "placeholder")
    action_tokens = (
        "audit",
        "block",
        "build",
        "check",
        "clean",
        "compare",
        "convert",
        "create",
        "debug",
        "delete",
        "diagnose",
        "fix",
        "gate",
        "generate",
        "inspect",
        "merge",
        "migrate",
        "monitor",
        "plan",
        "prove",
        "prune",
        "pull",
        "push",
        "report",
        "review",
        "route",
        "rotate",
        "summarize",
        "sweep",
        "validate",
    )

    def text_has_concrete_context(text: str) -> bool:
        words = re.findall(r"[a-z0-9][a-z0-9_-]*", text.lower())
        if len(words) < 6:
            return False
        if any(token in text.lower() for token in placeholder_tokens):
            return False
        return any(token in words for token in action_tokens)

    def case_has_concrete_context(case: dict[str, object]) -> bool:
        prompt = str(case.get("prompt") or "")
        if any(token in prompt.lower() for token in placeholder_tokens):
            return False
        context = "\n".join(
            str(case.get(field) or "")
            for field in (
                "prompt",
                "unit",
                "given",
                "should",
                "expected_behavior",
                "why_realistic",
            )
        )
        return text_has_concrete_context(context)

    leaky = 0
    realistic = 0
    realism_denominator = 0
    weak_declared: List[str] = []
    missing_realistic = 0
    invalid_realistic: List[str] = []
    for case in trigger_cases:
        prompt = str(case.get("prompt", "")).strip().lower()
        if skill_name and skill_name in prompt:
            leaky += 1
        declared_realistic = case.get("realistic")
        case_id = str(case.get("id") or case.get("name") or "<unnamed>")
        if isinstance(declared_realistic, bool):
            if declared_realistic is False:
                continue
            realism_denominator += 1
            if case_has_concrete_context(case):
                realistic += 1
            else:
                weak_declared.append(case_id)
            continue
        if "realistic" in case:
            invalid_realistic.append(case_id)
        else:
            missing_realistic += 1
        realism_denominator += 1
        if case_has_concrete_context(case) or any(token in prompt for token in natural_request_tokens):
            realistic += 1

    if leaky / len(trigger_cases) > 0.5:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_LEAKY",
            "Most positive eval prompts mention the skill name directly. Prefer natural user phrasing to test real routing behavior.",
            evidence=f"leaky={leaky}/{len(trigger_cases)}",
        ))

    if invalid_realistic:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_REALISTIC_FIELD_INVALID",
            "`realistic` fields in eval cases must be boolean true/false when present.",
            evidence=", ".join(invalid_realistic[:5]),
        ))

    if missing_realistic:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_REALISTIC_FIELD_MISSING",
            "Some trigger eval cases omit `realistic: true|false`; explicit declarations prevent style-word heuristics from becoming the source of truth.",
            evidence=f"missing={missing_realistic}/{len(trigger_cases)}",
        ))

    if weak_declared:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_DECLARED_REALISTIC_WEAK",
            "Some eval cases declare `realistic: true` but lack concrete task context; natural request wording is only supporting evidence.",
            evidence=", ".join(weak_declared[:5]),
        ))

    if realism_denominator and realistic / realism_denominator < 0.34:
        out.append(Finding(
            Level.WARN,
            "RESEARCH_EVALS_UNREALISTIC",
            "Positive eval prompts look synthetic. Honor explicit `realistic: true|false`; use natural request wording only as supporting evidence.",
            evidence=f"realistic={realistic}/{realism_denominator}",
        ))

    return out



def check_contract_and_evals(skill_dir: Path, *, require_contract: bool, require_evals: bool) -> List[Finding]:
    out: List[Finding] = []
    refs_dir = skill_dir / "references"

    contract_path = refs_dir / "contract.yaml"
    evals_path = refs_dir / "evals.yaml"

    if require_contract:
        if not contract_path.exists():
            out.append(Finding(Level.FAIL, "CONTRACT_MISSING", "Missing references/contract.yaml (required for gold)."))
        else:
            try:
                contract = _read_yaml_mapping(contract_path)
                required_keys = ["purpose", "triggers", "inputs", "outputs", "non_goals", "risks"]
                missing = [k for k in required_keys if k not in contract]
                if missing:
                    out.append(Finding(Level.FAIL, "CONTRACT_KEYS_MISSING", f"contract.yaml missing keys: {', '.join(missing)}"))

                if "triggers" in contract and not isinstance(contract["triggers"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_TRIGGERS_SHAPE", "`triggers` must be a list."))
                if "inputs" in contract and not isinstance(contract["inputs"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_INPUTS_SHAPE", "`inputs` must be a list."))
                if "outputs" in contract and not isinstance(contract["outputs"], list):
                    out.append(Finding(Level.FAIL, "CONTRACT_OUTPUTS_SHAPE", "`outputs` must be a list."))
            except Exception as e:
                out.append(Finding(Level.FAIL, "CONTRACT_INVALID", f"contract.yaml invalid: {e}"))

    if require_evals:
        if not evals_path.exists():
            out.append(Finding(Level.FAIL, "EVALS_MISSING", "Missing references/evals.yaml (required for gold)."))
        else:
            try:
                obj = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
                if not isinstance(obj, dict) or "cases" not in obj or not isinstance(obj["cases"], list):
                    out.append(Finding(Level.FAIL, "EVALS_SHAPE", "evals.yaml must be a mapping with `cases: [ ... ]`."))
                else:
                    if "schema_version" in obj and not isinstance(obj["schema_version"], (str, int, float)):
                        out.append(Finding(Level.FAIL, "EVALS_SCHEMA_VERSION_SHAPE", "`schema_version` must be a scalar when provided."))
                    cases = obj["cases"]
                    if len(cases) < 3:
                        out.append(Finding(Level.FAIL, "EVALS_TOO_FEW", "Provide at least 3 evaluation cases (happy/edge/failure)."))

                    for i, c in enumerate(cases, 1):
                        if not isinstance(c, dict):
                            out.append(Finding(Level.FAIL, "EVALS_CASE_INVALID", f"Case #{i} must be a mapping."))
                            continue
                        for k in ["name", "prompt", "acceptance"]:
                            if k not in c:
                                out.append(Finding(Level.FAIL, "EVALS_CASE_KEYS", f"Case #{i} missing `{k}`."))
                        if "acceptance" in c and not isinstance(c["acceptance"], list):
                            out.append(Finding(Level.FAIL, "EVALS_ACCEPTANCE_SHAPE", f"Case #{i} `acceptance` must be a list."))
                        elif isinstance(c.get("acceptance"), list):
                            for j, assertion in enumerate(c["acceptance"], 1):
                                if _is_bare_acceptance_string(assertion):
                                    out.append(Finding(
                                        Level.FAIL,
                                        "EVALS_ACCEPTANCE_BARE_STRING",
                                        (
                                            f"Case #{i} acceptance #{j} is a bare string, which the live runner treats as an exact contains assertion. "
                                            "Use a typed assertion such as `{type: regex, value: ...}` or explicit `contains:` shorthand."
                                        ),
                                        evidence=str(assertion)[:120],
                                    ))

                        # v2 optional fields (backward compatible)
                        if "id" in c and not isinstance(c["id"], str):
                            out.append(Finding(Level.FAIL, "EVALS_CASE_ID_SHAPE", f"Case #{i} `id` must be a string when provided."))
                        if "should_trigger" in c and not isinstance(c["should_trigger"], bool):
                            out.append(Finding(Level.FAIL, "EVALS_SHOULD_TRIGGER_SHAPE", f"Case #{i} `should_trigger` must be boolean when provided."))
                        if "prepend_skill" in c and not isinstance(c["prepend_skill"], bool):
                            out.append(Finding(Level.FAIL, "EVALS_PREPEND_SKILL_SHAPE", f"Case #{i} `prepend_skill` must be boolean when provided."))
                        if "output_schema" in c and not isinstance(c["output_schema"], str):
                            out.append(Finding(Level.FAIL, "EVALS_OUTPUT_SCHEMA_SHAPE", f"Case #{i} `output_schema` must be a string path when provided."))

                        if "category" in c:
                            allowed_categories = {"happy", "edge", "negative", "pressure"}
                            if not isinstance(c["category"], str) or c["category"].strip().lower() not in allowed_categories:
                                out.append(Finding(
                                    Level.FAIL,
                                    "EVALS_CATEGORY_INVALID",
                                    f"Case #{i} `category` must be one of: {', '.join(sorted(allowed_categories))}.",
                                ))

                        if "deterministic_checks" in c and not isinstance(c["deterministic_checks"], dict):
                            out.append(Finding(
                                Level.FAIL,
                                "EVALS_DETERMINISTIC_CHECKS_SHAPE",
                                f"Case #{i} `deterministic_checks` must be a mapping when provided.",
                            ))
                        if "budgets" in c and not isinstance(c["budgets"], dict):
                            out.append(Finding(
                                Level.FAIL,
                                "EVALS_BUDGETS_SHAPE",
                                f"Case #{i} `budgets` must be a mapping when provided.",
                            ))
                        elif isinstance(c.get("budgets"), dict):
                            min_signal = c["budgets"].get(EXPECTED_SIGNAL_BUDGET_KEY)
                            if min_signal is not None and parse_min_expected_signal_score(c["budgets"]) is None:
                                out.append(Finding(
                                    Level.FAIL,
                                    "EVALS_MIN_EXPECTED_SIGNAL_SCORE_SHAPE",
                                    f"Case #{i} `budgets.{EXPECTED_SIGNAL_BUDGET_KEY}` must be numeric when provided.",
                                ))

                        if "expected_signals" in c:
                            signals = c["expected_signals"]
                            if not isinstance(signals, dict):
                                out.append(Finding(
                                    Level.FAIL,
                                    "EVALS_EXPECTED_SIGNALS_SHAPE",
                                    f"Case #{i} `expected_signals` must be a mapping when provided.",
                                ))
                            else:
                                for signal_key, signal_value in signals.items():
                                    if signal_key not in EXPECTED_SIGNAL_KEYS:
                                        out.append(Finding(
                                            Level.WARN,
                                            "EVALS_EXPECTED_SIGNALS_UNKNOWN_KEY",
                                            (
                                                f"Case #{i} `expected_signals.{signal_key}` is not used by the local eval runner. "
                                                f"Known keys: {', '.join(sorted(EXPECTED_SIGNAL_KEYS))}."
                                            ),
                                        ))
                                    if not isinstance(signal_value, list):
                                        out.append(Finding(
                                            Level.FAIL,
                                            "EVALS_EXPECTED_SIGNALS_LIST_SHAPE",
                                            f"Case #{i} `expected_signals.{signal_key}` must be a list.",
                                        ))
            except Exception as e:
                out.append(Finding(Level.FAIL, "EVALS_INVALID", f"evals.yaml invalid: {e}"))

    return out


def check_repo_references(doc: SkillDoc) -> List[Finding]:
    out: List[Finding] = []
    skill_dir = doc.path.parent

    scripts = _iter_files(skill_dir, "scripts")
    refs = _iter_files(skill_dir, "references")
    assets = _iter_files(skill_dir, "assets")

    body = doc.body

    if scripts:
        names = [p.name for p in scripts]
        if not _has_any(body, ["scripts/"] + names):
            out.append(Finding(Level.WARN, "REPO_SCRIPTS_UNREFERENCED", "scripts/ exists but is not referenced in SKILL.md."))

    for rel_dir, files in [("references", refs), ("assets", assets)]:
        if files:
            names = [p.name for p in files]
            if not _has_any(body, [f"{rel_dir}/"] + names):
                out.append(Finding(Level.WARN, f"REPO_{rel_dir.upper()}_UNREFERENCED", f"{rel_dir}/ exists but is not referenced in SKILL.md."))

    return out
__all__ = [name for name in globals() if not name.startswith("__")]
