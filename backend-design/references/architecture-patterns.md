# Architecture Patterns

## Clean Architecture
- Layers: Entities, Use Cases, Interface Adapters, Frameworks/Drivers
- Dependencies point inward
- Core business logic is framework-agnostic

## Hexagonal Architecture (Ports and Adapters)
- Domain core with ports (interfaces)
- Adapters implement ports for DB, HTTP, queues
- Swap implementations easily for tests

## Domain-Driven Design (DDD)
- Strategic: bounded contexts, ubiquitous language
- Tactical: entities, value objects, aggregates, repositories, domain events

## Selection Guidance
- Clean: maintainability and testability across frameworks
- Hexagonal: many external systems or multiple adapters
- DDD: complex domain logic and invariants
