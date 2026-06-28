---
name: identify-tech-debt
description: Audit software projects for hidden technical debt, especially debt introduced by AI-assisted changes. Use when asked to identify, review, inventory, or prioritize tech debt; assess codebase health; inspect architecture drift, duplication, ignored abstractions, coupling, dead code, stale configuration, weak tests, operational gaps, security shortcuts, performance risks, or inconsistent APIs; or produce a technical-debt report without immediately fixing code.
---

# Identify Tech Debt

## Purpose

Identify technical debt that normal tests and linters miss: architectural drift, duplicate concepts, inconsistent business rules, forgotten temporary fixes, operational gaps, and maintainability risks. Produce evidence-backed findings, not vague cleanup advice.

## Operating Rules

- Do not modify project code unless the user explicitly asks for remediation.
- Prefer project-specific standards over generic rules. Read local agent instructions, architecture docs, contribution docs, dependency manifests, test setup, and recent diffs when relevant.
- Separate confirmed debt from leads. Report only findings with concrete evidence and explain uncertainty when confidence is not high.
- Prioritize debt by expected future cost, blast radius, and likelihood of recurring bugs, not by style preference.
- Avoid treating unfamiliar code as debt solely because it is complex. First infer the design intent and existing patterns.

## Workflow

1. Establish scope.
   - Determine whether the audit covers the whole repository, a change set, a feature area, or a specific concern.
   - If scope is broad, sample high-leverage areas first: entry points, shared services, domain logic, API boundaries, config, migrations, tests, and modules touched recently.
   - If the user mentions AI-generated code, compare new or changed code against existing abstractions and conventions.

2. Build a quick project map.
   - Identify languages, frameworks, package managers, test runners, data stores, API surfaces, deployment/CI files, and key module boundaries.
   - Read local docs that define architecture, layering, naming, ownership, ADRs, API conventions, or test strategy.
   - Use semantic/code search tools when available to find similar concepts before relying on literal search.

3. Run the heuristic scanner when a local filesystem is available.
   - Execute:

```bash
python3 <skill-dir>/scripts/scan_debt_signals.py <repo-root>
```

   - Use `--format json --output debt-signals.json` when you need machine-readable output.
   - Treat scanner output as leads. Verify each lead by reading surrounding code and checking whether it is actually a project risk.

4. Perform manual audit passes.
   - Duplication: look for repeated business rules, validators, API clients, query logic, components, test setup, and helpers with overlapping responsibilities.
   - Architecture: inspect dependency direction, layer boundaries, feature-specific patterns becoming global patterns, shared abstractions ignored by new code, and modules that now know too much about each other.
   - Knowledge: inspect TODO/FIXME/HACK comments, stale comments, missing rationale for new abstractions, naming drift, README/API docs drift, and decisions encoded only in code.
   - Operational: inspect timeouts, retries, cleanup on failure, logging around critical operations, monitoring, alerting, feature flags, environment-specific hacks, and CI/deploy scripts.
   - Maintenance: inspect dead code, unused exports, unused dependencies, stale migrations, orphaned config, old flags, dumping-ground utilities, and large files/functions.
   - Quality: inspect weak tests, missing edge cases, fragile snapshots, security shortcuts, missing authorization/input validation, performance risks, N+1 queries, duplicate API calls, and blocking work inside async paths.

5. Cross-check for coherence.
   - Search for at least two existing implementations before calling something duplicated or inconsistent.
   - Compare names for the same concept across files, APIs, config keys, database fields, events, and tests.
   - Check whether new abstractions have multiple real use cases. Flag one-off abstractions when they increase cognitive load or bypass established patterns.
   - Check whether the same business rule lives in multiple layers or services.

6. Produce a ranked report.
   - Lead with the highest-risk findings.
   - Include file and line references for each finding.
   - Include category, confidence, impact, why it is debt, and a concrete next step.
   - Group low-confidence observations separately as "leads to investigate" instead of findings.

## Reference

Read `references/debt-taxonomy.md` for the detailed signal catalog when performing a broad audit, classifying findings, or deciding whether a concern is duplication, architecture, knowledge, operational, maintenance, or quality debt.

## Report Format

Use this format unless the user requests a different one:

```markdown
## Findings

1. [Severity] Title
   - Category: Duplication | Architecture | Knowledge | Operational | Maintenance | Quality
   - Confidence: High | Medium | Low
   - Evidence: path/to/file.ext:line and brief code/context reference
   - Why it is debt: explain the long-term cost or failure mode
   - Suggested next step: smallest practical remediation or investigation

## Leads To Investigate

- path/to/file.ext:line - why this may be debt, and what would confirm it

## Notable Non-Issues

- Briefly mention suspicious patterns that were checked and found acceptable when useful.
```

## Severity Guidance

- Critical: likely security exposure, data loss, repeated production failure, or architecture violation blocking safe change.
- High: duplicated business rules, boundary violations, missing authorization, hidden coupling, or operational gaps likely to cause recurring defects.
- Medium: maintainability or consistency problems that slow future work or increase review burden.
- Low: localized cleanup with limited blast radius.

## Scanner Notes

The scanner finds common textual signals: TODO/FIXME/HACK comments, broad or swallowed exceptions, suspicious fallbacks, hardcoded secrets, missing timeouts, debug statements, duplicate config keys, large files/functions, utility dumping grounds, looped database calls, and blocking operations in async code. It cannot detect design intent, ignored abstractions, or true business-rule duplication without manual review.
