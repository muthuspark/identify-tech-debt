# Identify Tech Debt

A Codex skill that audits software projects for hidden technical debt while separating confirmed findings from investigation leads.

It targets architecture drift, duplicated business rules, ignored abstractions, stale configuration, weak tests, operational gaps, security shortcuts, performance risks, and other long-term maintainability issues that normal linters and tests often miss.

## Install in Codex

Clone this skill into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/muthuspark/identify-tech-debt.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/identify-tech-debt"
```

Start a new Codex thread after installing so Codex picks up the new skill.

## Local development install

Use this path only if you want to edit the skill locally.

```bash
git clone https://github.com/muthuspark/identify-tech-debt.git
cd identify-tech-debt
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)" "${CODEX_HOME:-$HOME/.codex}/skills/identify-tech-debt"
```

After changing the skill, start a new Codex thread before testing.

## Update

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/identify-tech-debt"
git pull
```

Start a new Codex thread after updating.

## Use

In Codex CLI, mention the skill with `$identify-tech-debt`:

```text
$identify-tech-debt Audit this project for hidden technical debt.
```

You can also browse/select it with `/skills`, or let Codex invoke it implicitly when your request matches the skill description.

Ask Codex naturally:

```text
Audit this project for architecture drift, duplicated business rules, and operational debt.
```

For a narrower review:

```text
Use $identify-tech-debt to inspect the backend service layer for duplicated business rules and architecture drift.
```

## Optional scanner

The skill includes a heuristic scanner for cheap leads:

```bash
python3 scripts/scan_debt_signals.py /path/to/project
```

For JSON output:

```bash
python3 scripts/scan_debt_signals.py /path/to/project \
  --format json \
  --output debt-signals.json
```

Scanner output is only a lead list. Verify source context before treating any signal as confirmed technical debt.

## Layout

```text
SKILL.md                         # Skill instructions and audit workflow
agents/openai.yaml               # Codex skill UI metadata
references/debt-taxonomy.md      # Debt categories, signals, and evidence standard
scripts/scan_debt_signals.py     # Optional heuristic scanner
```

## License

Add a license file before distributing this skill broadly.
