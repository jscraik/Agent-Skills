# Agent Skills Runtime Context

This context defines the project language for the agent-skills runtime projection and catalog surfaces. It exists so agents, validators, and docs use the same terms when changing skill visibility.

## Language

**Runtime Projection**:
A generated skill layout that determines which skills are first-level selectable by Codex.
_Avoid_: Runtime sync, skill tree

**Flat Runtime**:
A runtime projection where individual default-visible skills appear as first-level runtime entries.
_Avoid_: Legacy runtime, old layout

**Rooted Runtime**:
A runtime projection where first-level entries are root skill sets and individual skills are latent modules.
_Avoid_: Grouped runtime, clustered runtime

**Root Skill Set**:
A first-level runtime entry that routes to related latent skill modules.
_Avoid_: Category, folder, namespace

**Latent Skill Module**:
A skill that is discoverable through a root skill set or advanced catalog but is not a first-level runtime entry.
_Avoid_: Hidden skill, subskill

**System Bridge Skill**:
A system-lane compatibility entry that preserves external skill names without appearing as a first-level runtime entry.
_Avoid_: Alias, shim

**Plugin Lane**:
A plugin-owned skill route that remains available for plugin lifecycle work without becoming a default runtime entry.
_Avoid_: Plugin skill, plugin command

**Default Catalog**:
The normal user-facing skill list shown without advanced visibility.
_Avoid_: Basic catalog

**Advanced Catalog**:
The expanded skill list that includes latent modules, plugin lanes, and system bridge skills for inspection or maintenance.
_Avoid_: Full dump, all skills

## Relationships

- A **Runtime Projection** is either a **Flat Runtime** or a **Rooted Runtime**.
- A **Rooted Runtime** contains exactly the configured **Root Skill Sets** as first-level entries.
- A **Flat Runtime** contains individual **Default Catalog** skills as first-level entries.
- A **Root Skill Set** routes to one or more **Latent Skill Modules**.
- The **Default Catalog** is derived from the active **Runtime Projection**.
- The **Advanced Catalog** includes the **Default Catalog**, **Latent Skill Modules**, **Plugin Lanes**, and **System Bridge Skills**.
- **System Bridge Skills** live in the system lane and must not appear as first-level runtime entries.

## Example Dialogue

> **Dev:** "If we move to a **Rooted Runtime**, should `he-tdd` still appear as a first-level skill?"
> **Domain expert:** "No. `harness-engineering` is the **Root Skill Set**; `he-tdd` becomes a **Latent Skill Module** that the root routes to."

## Flagged Ambiguities

- "hidden skill" was used for both **Latent Skill Module** and **System Bridge Skill**. Resolution: use **Latent Skill Module** for intentionally routed non-first-level skills, and **System Bridge Skill** for compatibility entries in the system lane.
- "category" was used for both display grouping and **Root Skill Set** ownership. Resolution: use **Root Skill Set** only for runtime routing roots; use "category" only for rendered catalog grouping.
