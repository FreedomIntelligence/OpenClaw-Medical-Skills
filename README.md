# Claude Code Medical Skills

> **868 medical & bioinformatics skills** adapted as Claude Code slash commands.
> Ported from [OpenClaw Medical Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills).

## Quick Start

Clone this repo into your project's `.claude/` directory, or copy the `commands/` folder:

```bash
# Option 1: clone as .claude folder in your project
git clone https://github.com/vasya-boop/Claude-Medical-Skills.git /your-project/.claude

# Option 2: copy just the commands
cp -r .claude/commands/ /your-project/.claude/commands/
```

Then in Claude Code, invoke any skill:

```
/alphafold
/bio-blast-searches
/autonomous-oncology-agent
/arxiv-search
```

## Categories

| Category | Example Skills |
|----------|---------------|
| **Gene Therapy** | `aav-vector-design-agent`, `armored-cart-design-agent`, `crispr-*` |
| **Structure Prediction** | `alphafold`, `alphafold-database`, `bindcraft`, `binder-design` |
| **Genomics** | `bio-atac-seq-*`, `bio-chipseq-*`, `bio-rna-seq-*`, `bio-wgs-*` |
| **Drug Discovery** | `agentd-drug-discovery`, `bio-admet-prediction`, `bindingdb-database` |
| **Clinical** | `autonomous-oncology-agent`, `bio-clinical-databases-*`, `adhd-daily-planner` |
| **Bioinformatics** | `bio-alignment-*`, `bio-blast-searches`, `bio-codon-usage` |
| **Literature** | `arxiv-search`, `bgpt-paper-search` |
| **Lab Integration** | `adaptyv`, `benchling-integration` |
| **AI/ML** | `bayesian-optimizer`, `ai-analyzer`, `alphafold` |

## All 868 Skills

See `.claude/commands/` for the full list. Each file is a standalone Claude Code command.

## Format

Each skill is a markdown file with:
- **Description** — what the skill does and when to use it
- **When to Use** — trigger conditions
- **Core Capabilities** — what it can do
- **Workflow** — step-by-step process
- **Code Examples** — Python, Bash, or other relevant examples
- **Available Tools** — Read, Write, Bash, WebSearch, etc.

## Differences from OpenClaw

| OpenClaw | Claude Code |
|----------|------------|
| `read_file` | `Read` |
| `write_file` | `Write` |
| `run_shell_command` | `Bash` |
| `search_files` | `Grep` |
| `web_search` | `WebSearch` |
| Platform-specific frontmatter | Clean markdown |

## License

MIT — original skills copyright their respective authors.
Source: [FreedomIntelligence/OpenClaw-Medical-Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills)
