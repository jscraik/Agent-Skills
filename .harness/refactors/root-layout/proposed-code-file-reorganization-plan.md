# Proposed Code File Reorganization Plan

**Target Directory:** `Infrastructure/scripts/` 
*(Note: As `src/x` does not exist in this project, I identified `Infrastructure/scripts` as the likely intended target since it is heavily cluttered with 111 flat files. If you meant a different directory, please clarify!)*

## 1. Rationale and Justification

Currently, `Infrastructure/scripts` operates as a monolith of 111 unstructured files encompassing test suites, codebase linters, telemetry building, graph generation, synchronization binaries, and more. This flat structure creates massive cognitive overload, making it difficult for developers and AI agents to intuitive understand system boundaries and locate related scripts.

### Goals of Reorganization:
1. **Reduce Mental Overhead:** A developer shouldn't have to scroll past 25 `test_*.py` and `validate_*.py` files just to find the `sync_skills.sh` script.
2. **Localize Functional Context:** Grouping scripts by their domain (e.g., `skill-graph`, `runtime-separation`, `validation`) allows shared helpers to remain close to their consumers.
3. **Safe Calling:** We will create wrapper entry points or update CI caller paths so existing configurations like `validate_all.sh` and `check-environment.sh` do not fail.
4. **Preserve Invocation Boundaries:** Complex scripts like `test_validate_all_runtime_separation.py` dynamically replace binary sub-commands with execution stubs, which means moving the targets natively requires updating the stub injection patterns.

---

## 2. Proposed Folder Structure

I propose breaking the monolith into the following domain-driven subdirectories under `Infrastructure/scripts/`:

```text
Infrastructure/scripts/
├── testing/                 # All `test_*.py` regression suites
├── runtime-separation/      # Artifact builders, verifiers, and validators for the runtime-separation pipeline
├── skill-graph/             # Gen-graph, query-graph, graph artifacts, and adjacency scripts
├── validation-and-linting/  # Standalone linters (docs, SKILL format, codebase) and `verify_*` guardrails
├── lifecycle-and-sync/      # Core operators: sync_skills, sync_mcp, plugins, projection integrity
├── codex-preflight/         # Environment setup and preflights (codex-preflight.sh, etc.)
└── lib/                     # (Existing) Core library resources (e.g., ask CLI engine)
```

### 2.1 Drill-Down by Directory

#### **A. `testing/`** *(Moving 16+ files)*
All automated regression tests currently pollute the main ops folder.
* **Files:** `test_codex_env_common.py`, `test_plugin_*.py`, `test_skill_*.py`, `test_validate_all_runtime_separation.py`, `test_wiki_*.py`
* **Justification:** Python's `unittest` framework dynamically discovers tests. Placing these in `testing/` stops them from obscuring active functional scripts while satisfying modern Python repository convention (often `/tests/` but leaving it under scripts keeps infrastructure together).

#### **B. `runtime-separation/`** *(Moving 10+ files)*
This domain manages the highly specific capability of verifying separation of tools across active Codex homes.
* **Files:** `build_runtime_separation_current.py`, `compare_runtime_separation_baseline.py`, `scan_runtime_separation_consumers.py`, `validate_runtime_separation_*.py`, `verify_runtime_separation_*.py`
* **Justification:** Tightly-coupled domain with very specific internal dependencies.

#### **C. `skill-graph/`** *(Moving ~10 files)*
Code that operates the local DAG logic and dependencies between skills.
* **Files:** `gen-skill-graph.py`, `query-graph.py`, `build-adjacency-yaml.py`, `graph-diff.py`, `bootstrap_recursive_skill_graph_artifacts.py`
* **Justification:** Abstract math/graph operations shouldn't mix with basic bash lintings.

#### **D. `validation-and-linting/`** *(Moving 20+ files)*
All quality gate scripts that either output "0" (success) or non-zero (failure) but *do not manipulate/sync local state*.
* **Files:** `docs_lint.py`, `lint_*.sh`, `validate_plan_graphs.sh`, `validate_skill_authoring_family.sh`, `verify_ask_cli_*.py`, `check-doc-style.sh`, `check-staged-secrets.sh`
* **Justification:** CI and pre-push runners need clear pointers to validation stages.

#### **E. `lifecycle-and-sync/`** *(Moving 10+ files)*
Core synchronisation tooling that writes or changes operational state.
* **Files:** `sync_skills.sh`, `sync_mcp.py`, `sync_projection_trees.sh`, `projection_integrity.py`, `codex_env_common.sh`

#### **F. Root Modularity (What Stays in `/scripts`)**
* **Files:** `validate_all.sh`, `check-environment.sh`
* **Justification:** These are the canonical, top-level gateways into running scripts. They should remain in their canonical location and route into folders to preserve standard developer muscle-memory (`./Infrastructure/scripts/validate_all.sh`).

---

## 3. Safe Refactoring Strategy (Mitigating Breakages)

If we proceed with this execution, I will implement it progressively in three safe steps:

### **Step 1: Module Restructuring & Git Moves**
- Use `git mv` to shift files into the mapped directories above to preserve file history.
- Add `__init__.py` markers if internal imports exist between moved Python sources (so `from lib.ask...` or similar python imports don't break module resolution).

### **Step 2: Caller Path Resolution (The Risky Part)**
This is where system-breakage commonly occurs. My extraction analysis shows that files like `validate_all.sh` and `check-environment.sh` explicitly execute scripts via local paths (e.g. `Infrastructure/scripts/lifecycle-and-sync/validate_projection_integrity.sh`).
- **Bash Scripts:** I will batch-replace intra-script executions globally to point to the new subdirectories. I will ensure `bash` or `source` directives dynamically reference `$(dirname "$0")/sub-folder/...` to permit execution from any CWD.
- **Python Scripts:** I will verify that `subprocess.check_call` invocations correctly target paths. For example, `test_validate_all_runtime_separation.py` creates execution "stubs" by replacing paths; I must meticulously align its AST with the moved directories.
- **CI Configurations (`.circleci/`, `.github/`, `.git/hooks`):** CI workflows frequently run these scripts. I will modify YAML paths natively to reflect the moved targets.

### **Step 3: Verification (No-Brainer Sanity Check)**
- After updates, I will run `./Infrastructure/scripts/validate_all.sh`, `make test`, and `./Infrastructure/scripts/check-environment.sh`.
- The migration is ONLY successful if the full CI test suite runs flawlessly. 

---

### Request for Approval
Does this `Infrastructure/scripts` reorganization strategy match the type of cleanup you were hoping for, or were you specifically hoping to reorganize another domain (e.g. your external source components)? Let me know if you would like me to proceed with executing Step 1 and 2!
