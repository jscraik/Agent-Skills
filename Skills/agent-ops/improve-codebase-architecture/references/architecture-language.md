# Architecture Language

Use these terms consistently when reviewing architecture.

## Terms

**Module**:
A unit with an interface and an implementation, ranging from a function to a package.
_Avoid_: helper pile, layer, bucket

**Interface**:
The surface other code depends on to use a module.
_Avoid_: public bits, API-ish wrapper

**Implementation**:
The internal decisions and machinery hidden behind an interface.
_Avoid_: internals when the contrast with interface matters

**Deep module**:
A module whose small interface hides substantial implementation complexity.
_Avoid_: big module, god object

**Shallow module**:
A module whose interface reveals almost as much complexity as its implementation hides.
_Avoid_: abstraction when it does not abstract much

**Seam**:
A boundary where code can vary independently because there are real alternate implementations or dependency categories.
_Avoid_: seam for a hypothetical future adapter

**Adapter**:
An implementation that translates between the core module interface and a concrete external or replaceable dependency.
_Avoid_: adapter for ordinary in-process helper calls

**Locality**:
The degree to which a change can be understood and made in one place.
_Avoid_: cohesion when the review is specifically about change radius

**Leverage**:
The amount of useful behavior gained from a small, stable interface.
_Avoid_: abstraction benefit

## Heuristics

- A module should earn its name by hiding complexity.
- If deleting a wrapper makes the caller clearer, the wrapper is probably shallow.
- One adapter usually means a hypothetical seam; two adapters usually means a real seam.
- Tests should target the interface where users observe behavior.
- A deep module is allowed to contain messy implementation detail when the interface makes that mess local.
