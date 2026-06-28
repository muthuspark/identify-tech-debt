# identify-tech-debt

A Codex skill for auditing software projects for hidden technical debt: architecture drift, duplicated business rules, ignored abstractions, stale configuration, weak tests, operational gaps, security shortcuts, and other long-term maintainability risks.

## Install

Clone this repository into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone git@github.com:muthuspark/identify-tech-debt.git "${CODEX_HOME:-$HOME/.codex}/skills/identify-tech-debt"
```

Restart Codex so it can discover the new skill.

## Use

Invoke the skill by name:

```text
Use $identify-tech-debt to audit this project for hidden technical debt.
```

For a narrower review:

```text
Use $identify-tech-debt to inspect the backend service layer for duplicated business rules and architecture drift.
```

## Update

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/identify-tech-debt"
git pull
```

Restart Codex after updating.

## Optional Scanner

The skill includes a heuristic scanner for cheap leads. Run it from any checkout:

```bash
python3 scripts/scan_debt_signals.py /path/to/project
```

For JSON output:

```bash
python3 scripts/scan_debt_signals.py /path/to/project --format json --output debt-signals.json
```

Scanner output is only a lead list. Verify source context before treating any signal as confirmed technical debt.
