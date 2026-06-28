# Technical Debt Taxonomy

Use this reference to classify findings by why the debt exists, then map the finding to concrete project evidence. A finding can have more than one area, but choose one primary category so the report stays clear.

## Categories By Cause

### Duplication Debt

Debt caused by solving the same problem more than once.

Signals:
- Copy-pasted implementation with small local variations.
- Duplicate business rules, validators, policies, serializers, mappers, or query builders.
- Similar APIs for the same operation.
- Multiple implementations of the same algorithm.
- Shared UI patterns or components implemented differently.
- State duplicated across stores, caches, or services.

Evidence to collect:
- At least two file references showing the repeated concept.
- Whether the implementations can diverge and produce inconsistent behavior.
- Existing abstraction that could have been reused.

### Architecture Debt

Debt caused by weaker boundaries, wrong dependency direction, or abstractions that do not match the system.

Signals:
- Business logic leaking across API, UI, persistence, job, or service layers.
- Feature-specific pattern becoming a global pattern without design rationale.
- Increased coupling between modules or service boundaries becoming unclear.
- Hidden circular dependencies.
- Excessive inheritance where composition is the local norm.
- New abstraction introduced for one use case.
- Existing framework or local pattern ignored.

Evidence to collect:
- Current intended boundary from docs, folder structure, imports, or existing examples.
- Exact dependency or call path that violates the boundary.
- Consequence: harder testing, harder reuse, circular initialization, or unclear ownership.

### Knowledge Debt

Debt caused by missing, stale, or fragmented design knowledge.

Signals:
- Comments describing old behavior.
- Missing ADR or rationale for architectural decisions.
- API documentation drift.
- README or setup docs not updated after behavior/config changes.
- Multiple naming conventions for the same idea.
- TODO/FIXME/HACK comments without tracking.
- Temporary prompts, scripts, or migration notes translated into permanent code.

Evidence to collect:
- The stale or missing doc location, plus the code that proves drift.
- Names used for the same concept across files.
- Whether a future maintainer would have to rediscover the rationale.

### Operational Debt

Debt caused by weak runtime behavior, observability, deployment, or configuration practices.

Signals:
- Swallowed exceptions, silent fallback behavior, or missing cleanup on failures.
- Missing timeout handling or inconsistent retry logic.
- Missing logs for critical operations.
- Debug logs committed into production paths.
- Sensitive information logged.
- Inconsistent log formats.
- Feature flags never removed.
- Duplicate configuration keys, environment-specific hacks, or magic constants.
- CI pipelines, deployment scripts, metrics, or alerts growing without cleanup.
- Missing observability around new features.

Evidence to collect:
- Runtime path affected and likely failure mode.
- Whether callers can distinguish failure from empty/default results.
- Config/log/monitoring artifact that proves inconsistency or drift.

### Maintenance Debt

Debt caused by code or dependencies that remain after their purpose changes.

Signals:
- Dead code after refactoring.
- Unused configuration flags.
- Utility/helper classes becoming dumping grounds.
- Large methods or files that barely pass review.
- Unused dependencies or transitive dependency bloat.
- Outdated packages where upgrade risk is accumulating.
- Stale migrations, duplicate schema fields, schema drift, or orphaned tables.

Evidence to collect:
- Reachability or usage evidence, not just suspicion.
- Dependency manifests, import/export references, migrations, or schema files.
- How the debt increases future change cost.

### Quality Debt

Debt caused by shortcuts in correctness, safety, performance, or test coverage.

Signals:
- Tests that only verify happy paths.
- Duplicate test logic or tests tightly coupled to implementation.
- Missing integration coverage for cross-module behavior.
- Fragile snapshot tests.
- Missing authorization checks.
- Hardcoded secrets, unsafe defaults, excessive permissions, or missing input validation.
- N+1 database queries, duplicate API calls, missing caching, inefficient loops, loading entire datasets unnecessarily, or blocking operations inside async code.

Evidence to collect:
- Code path and realistic trigger.
- Missing edge case or failure case.
- Performance/security impact or likely incident mode.

## Area Checklist

Use these as prompts during a broad audit:

- Architecture: duplicated abstractions, dependency direction, layer leaks, globalized feature patterns, coupling.
- Code: copy-paste, overlapping helpers, dead code, unused flags, dumping-ground utilities, large methods, hidden cycles, inheritance misuse, standard-library reinvention.
- APIs: inconsistent naming, optional parameters hiding interface design issues, multiple ways to do the same task.
- Error handling: swallowed exceptions, retries, timeouts, cleanup, silent fallbacks.
- Logging: missing critical logs, production debug logs, sensitive logs, inconsistent formats.
- Security: authorization, secrets, defaults, input validation, permissions.
- Performance: N+1 queries, duplicate calls, caching gaps, inefficient loops, whole-dataset loading, blocking async work.
- Database: indexes, duplicate fields, schema drift, migration strategy, orphaned tables.
- Testing: happy-path-only tests, duplicate test logic, integration gaps, fragile snapshots, implementation-coupled assertions.
- Documentation: stale comments, missing ADRs, API docs drift, README drift.
- Configuration: stale flags, duplicate keys, environment hacks, magic constants.
- Dependencies: overlapping libraries, outdated packages, unused packages, transitive bloat.
- Frontend: duplicate components, inconsistent UI patterns, duplicated state, CSS specificity conflicts.
- Backend: duplicate endpoints, duplicated business rules, unclear service boundaries.
- DevOps and monitoring: CI/deploy duplication, permanent temporary workarounds, unused metrics, noisy alerts, missing observability.
- AI-specific: hallucinated APIs wrapped in compatibility layers, new abstractions instead of local framework patterns, inconsistent style between runs, partial refactors that stop after the requested file.

## Evidence Standard

Do not report a finding unless it names:

- What is duplicated, drifting, unsafe, or harder to maintain.
- Where the evidence lives, with file and line references.
- Why the project will pay for it later.
- What would reduce the debt with the smallest reasonable change.

Use "leads to investigate" for suspicious patterns that need deeper validation.
