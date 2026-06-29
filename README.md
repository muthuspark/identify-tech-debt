# Identify Tech Debt

A Codex and Claude Code plugin that audits software projects for hidden technical debt while separating confirmed findings from investigation leads.

It adds the `identify-tech-debt` skill and targets architecture drift, duplicated business rules, ignored abstractions, stale configuration, weak tests, operational gaps, security shortcuts, performance risks, and other long-term maintainability issues that normal linters and tests often miss.

## Install in Codex

Add the GitHub repo as a Codex marketplace:

```bash
codex plugin marketplace add muthuspark/identify-tech-debt
```

Install the plugin:

```bash
codex plugin add identify-tech-debt@identify-tech-debt
```

Start a new Codex thread after installing so Codex picks up the new skill.

## Install in Claude Code

Add the GitHub repo as a Claude Code marketplace:

```bash
claude plugin marketplace add muthuspark/identify-tech-debt
```

Install the plugin:

```bash
claude plugin install identify-tech-debt@identify-tech-debt
```

Start a new Claude Code session after installing so Claude picks up the new skill.

## Local development install

Use this path only if you want to edit the plugin locally.

For Codex:

```bash
git clone https://github.com/muthuspark/identify-tech-debt.git
cd identify-tech-debt
codex plugin marketplace add "$(pwd)"
codex plugin add identify-tech-debt@identify-tech-debt
```

For Claude Code:

```bash
git clone https://github.com/muthuspark/identify-tech-debt.git
cd identify-tech-debt
claude plugin marketplace add "$(pwd)"
claude plugin install identify-tech-debt@identify-tech-debt
```

After changing the plugin, refresh the marketplace or restart the target agent before testing in a new thread or session.

## Sparse install

If you want Codex to fetch only the marketplace and plugin package from the repo:

```bash
codex plugin marketplace add muthuspark/identify-tech-debt \
  --sparse .agents/plugins \
  --sparse plugins/identify-tech-debt
codex plugin add identify-tech-debt@identify-tech-debt
```

## Use

In Codex CLI, mention the bundled skill with `$identify-tech-debt`:

```text
$identify-tech-debt Audit this project for hidden technical debt.
```

You can also browse/select it with `/skills`, or let Codex invoke it implicitly when your request matches the skill description.

In Claude Code, ask naturally and name the skill:

```text
Use the identify-tech-debt skill to audit this project for hidden technical debt.
```

Ask naturally:

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
python3 plugins/identify-tech-debt/skills/identify-tech-debt/scripts/scan_debt_signals.py /path/to/project
```

For JSON output:

```bash
python3 plugins/identify-tech-debt/skills/identify-tech-debt/scripts/scan_debt_signals.py /path/to/project \
  --format json \
  --output debt-signals.json
```

Scanner output is only a lead list. Verify source context before treating any signal as confirmed technical debt.

## Layout

```text
.claude-plugin/marketplace.json                         # Claude Code marketplace
.agents/plugins/marketplace.json                         # Local Codex marketplace
plugins/identify-tech-debt/                              # Marketplace plugin package
plugins/identify-tech-debt/.claude-plugin/plugin.json    # Claude Code plugin manifest
plugins/identify-tech-debt/.codex-plugin/plugin.json     # Codex plugin manifest
plugins/identify-tech-debt/skills/identify-tech-debt/     # Bundled skill source
```

## License

MIT.
