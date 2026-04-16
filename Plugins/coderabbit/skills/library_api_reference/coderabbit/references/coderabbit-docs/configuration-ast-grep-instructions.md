---
source: https://docs.coderabbit.ai/configuration/ast-grep-instructions
---

# AST-based path instructions

CodeRabbit supports review instructions based on Abstract Syntax Tree (AST) patterns, powered by `ast-grep` — a Rust-based tool that uses the tree-sitter parser to generate AST rules for popular languages, written by Herrington Darkholme. This feature has a learning curve and is recommended for users already comfortable with YAML configuration.

**Further reading:**

- Abstract Syntax Tree — Wikipedia
- `ast-grep` rule configuration guide

## Setup

Use the ast-grep Playground to design and test rules on source code snippets before adding them to your project.

```yaml
reviews:
  tools:
    ast-grep:
      essential_rules: true # option to enable essential security rules
      rule_dirs:
        - "custom-name"
      packages:
        - "myorg/myawesomepackage" # custom package name following the format organization/repository
```

## The rule object

The rule object is the core concept of the `ast-grep` rule system — every other feature is built on top of it.
Below is the full list of fields in a rule object. Every field is optional and can be omitted, but at least one field must be present. A node matches a rule if and only if it satisfies all fields in the rule object.

```yaml
rule:
  # atomic rule
  pattern: "search.pattern"
  kind: "tree_sitter_node_kind"
  regex: "rust|regex"
  # relational rule
  inside: { pattern: "sub.rule" }
  has: { kind: "sub_rule" }
  follows: { regex: "can|use|any" }
  precedes: { kind: "multi_keys", pattern: "in.sub" }
  # composite rule
  all: [{ pattern: "match.all" }, { kind: "match_all" }]
  any: [{ pattern: "match.any" }, { kind: "match_any" }]
  not: { pattern: "not.this" }
  matches: "utility-rule"
```

## Rule categories

These three categories can be composed together to create more complex rules.

> Read the `ast-grep` documentation for detailed guides.

### Atomic rule

An atomic rule defines the most basic matching rule: whether a syntax node matches or not. There are three kinds: `pattern`, `kind`, and `regex`.

> Official documentation: Atomic Rule

### Relational rule

A relational rule defines the relationship between two syntax nodes. There are four kinds: `inside`, `has`, `follows`, and `precedes`.
All four relational rules accept a sub-rule object as their value. The sub-rule matches the surrounding node; the relational rule itself matches the target node.

> Official documentation: Relational Rule

```yaml
rule:
  pattern: await $PROMISE
  inside:
    kind: for_in_statement
    stopBy: end
```

### Composite rule

A composite rule defines the logical relationship between multiple sub-rules. There are three kinds: `all`, `any`, and `not`.
**`all`** — matches if all sub-rules match:

```yaml
rule:
  all:
    - pattern: console.log('Hello World');
    - kind: expression_statement
```

**`any`** — matches if any sub-rule matches:

```yaml
rule:
  any:
    - pattern: var a = $A
    - pattern: const a = $A
    - pattern: let a = $A
```

**`not`** — applies negation; matches if the sub-rule does not match:

```yaml
rule:
  pattern: console.log($GREETING)
  not:
    pattern: console.log('Hello World')
```

> Official documentation: Composite Rule

## Reusing rules as utilities

`ast-grep` uses YAML for rule representation, which means rule objects cannot be directly reused across rule files. Utility rules solve this.

### Local utility rule

Local utility rules are defined in the `utils` field of the config file. `utils` is a string-keyed dictionary.

```yaml
utils:
  is-literal:
    any:
      - kind: string
      - kind: number
      - kind: boolean
rule:
  matches: is-literal
```

### Global utility rule

Global utility rules are defined in a separate file and are available across all rule configurations in the project.
To create global utility rules, create a `rules` directory and a `utils` directory at the root of your project:

```
my-awesome-project   # project root
  |- rules           # rule directory
  | |- my-rule.yml
  |- utils           # utils directory
  | |- is-literal.yml
```

Add both directories to `.coderabbit.yaml` under `tools.ast-grep`:

```yaml
reviews:
  tools:
    ast-grep:
      essential_rules: true
      rule_dirs:
        - "rules"
      util_dirs:
        - "utils"
      packages:
        - "my-awesome-org/my-awesome-package" # public repository containing ast-grep rules
```

Example utility rule file:

```yaml
# is-literal.yml
id: is-literal
language: TypeScript
rule:
  any:
    - kind: "false"
    - kind: undefined
    - kind: "null"
    - kind: "true"
    - kind: regex
    - kind: number
    - kind: string
```

> Official documentation: Utility Rule

## Packages

A package is a collection of `ast-grep` rules that can be shared across multiple projects.

### CodeRabbit packages

## ast-grep-essentials

**Essential security rules package** Because we value security, this package gets its own property in `.coderabbit.yaml` for easier installation without overwriting existing configurations.

```yaml
reviews:
  tools:
    ast-grep:
      essential_rules: true
      packages:
        - "my-awesome-org/my-awesome-package"
```

### Custom packages

To use a public repository containing `ast-grep` rules as a package, add it to the `packages` field in `.coderabbit.yaml`.

```yaml
reviews:
  tools:
    ast-grep:
      packages:
        - "my-awesome-org/my-awesome-package"
```

## Supported languages

ast-grep supports many languages via tree-sitter parsers.

## Examples

### JavaScript — disallow imports without file extension

```yaml
id: find-import-file
language: js
message: "Importing files without an extension is not allowed"
rule:
  regex: "/[^.]+[^/]$"
  kind: string_fragment
  any:
    - inside:
        stopBy: end
        kind: import_statement
    - inside:
        stopBy: end
        kind: call_expression
        has:
          field: function
          regex: "^import$"
```

### TypeScript — no `console.log` except `console.error` in catch blocks

```yaml
id: no-console-except-error
language: typescript
message: "No console.log allowed except console.error on the catch block"
rule:
  any:
    - pattern: console.error($$$)
      not:
        inside:
          kind: catch_clause
          stopBy: end
    - pattern: console.$METHOD($$$)
constraints:
  METHOD:
    regex: "log|debug|warn"
```

### C — prefer plain function calls over struct method-style calls

In C, simulating OOP via struct function pointers introduces memory and indirection overhead. This rule flags the pattern and suggests a plain function call with the struct pointer as the first argument.

```yaml
id: method_receiver
language: c
rule:
  pattern: $R.$METHOD($$$ARGS)
transform:
  MAYBE_COMMA:
    replace:
      source: $$$ARGS
      replace: "^.+"
      by: ", "
fix: $METHOD(&$R$MAYBE_COMMA$$$ARGS)
```
