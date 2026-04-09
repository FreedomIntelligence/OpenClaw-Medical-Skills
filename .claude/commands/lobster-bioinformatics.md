# lobster-bioinformatics

> Run bioinformatics analyses using Lobster AI - single-cell RNA-seq, bulk RNA-seq, literature mining, dataset discovery, quality control, and visualization. Use when analyzing genomics data, searching for papers/datasets, or working with H5AD, CSV, GEO/SRA accessions, or biological data. Requires lobster-ai package installed.

# Lobster Bioinformatics Agent

Lobster AI is a bioinformatics platform that combines specialized AI agents with open-source tools to analyze multi-omics data through natural language.

## When to use this Skill

Use Lobster when the user asks to:
- Analyze single-cell RNA-seq data (QC, clustering, annotation, markers)
- Perform bulk RNA-seq analysis (differential expression, complex designs)
- Search scientific literature (PubMed, PMC, full-text retrieval)
- Discover datasets (GEO, SRA, ENA (free) and PRIDE, MASSive (cloud))
- Run quality control on biological data
- Generate bioinformatics visualizations (UMAP, volcano plots, heatmaps)
- Download and process biological datasets
- Work with H5AD, CSV, Excel, 10X formats
- Extract methods or metadata from papers

## Requirements

Lobster must be installed and configured:

```bash
# Check if Lobster is installed
which lobster

# If not installed:
uv pip install lobster-ai
lobster init --help #to see non-interactive
```

Lobster requires an LLM provider (Ollama, Anthropic, or AWS Bedrock).

## Pre-flight check (IMPORTANT)

**Before running any analysis, always verify Lobster is ready:**
```bash
lobster config-test --json
```

Returns structured JSON:
```json
{
  "valid": true,
  "env_file": "/path/to/.env",
  "checks": {
    "llm_provider": {"status": "pass", "provider": "bedrock", "message": "Connected"},
    "ncbi_api": {"status": "pass", "has_key": true, "message": "Connected"},
    "workspace": {"status": "pass", "path": "/path/to/workspace", "message": "Writable"}
  }
}
```

This command validates:
- **LLM provider** - Ollama server running + models installed, or Anthropic/Bedrock API keys valid
- **NCBI API** - PubMed/GEO access (optional but recommended)
- **Workspace** - Directory writable for output files

**Expected output for a working setup:**
```
✅ LLM Provider: bedrock (connected)
✅ NCBI API: Connected (with API key)
✅ Workspace: Writable
✅ Configuration Valid
```

**If config-test fails:**

| Error | Solution |
|-------|----------|
| No LLM provider configured | Run `lobster init` |
| Ollama server not accessible | Start Ollama: `ollama serve` |
| Ollama: No models installed | After asking user - Install a model: `ollama pull gpt-oss:20b` |
| Anthropic/Bedrock API error | Check API key validity in `.env` |
| NCBI API not configured | Add `NCBI_API_KEY` to `.env` (optional) |
| Workspace not writable | Check directory permissions |

**Quick status checks:**
```bash
# Show configuration values (masked)
lobster config-show

# Show subscription tier and available agents
lobster status
```

## Usage

### Basic syntax

```bash
# Single query (non-interactive)
lobster query "<natural language request>"

# With custom workspace
lobster query --workspace /path/to/workspace "<request>"

# With reasoning mode (for complex tasks)
lobster query --reasoning "<request>"
```

### Session continuity (multi-turn conversations)

Lobster supports conversation continuity via `--session-id`, enabling follow-up questions that reference previous context either by setting sessin-id to latest or a string of your choice:

```bash
# default session
lobster query "Search PubMed for CRISPR papers"
# Output: Session: session_20241208_150000 (use --session-id latest for follow-ups)
# then follow up with 
lobster query --session-id latest "Download the first dataset from that search"

#or use custom session id
lobster query --session-id "crispr_search_1" "Search PubMed for CRISPR papers"
#follow up with 
lobster query --session-id "crispr_search_1" "show me metadata from the first paper"
```

**Best practices:**
- Always use `--session-id latest` for follow-up queries
- Session files are saved in workspace as `session_*.json`
- Use same `--workspace` for related queries to maintain context
- Session contains conversation history, not tool execution state

**Workspace-based sessions:**
```bash
# Project 1: Cancer research
lobster query --workspace ~/cancer-project "Search for breast cancer datasets"
lobster query --workspace ~/cancer-project --session-id latest "Download the best one"

# Project 2: Immunology (separate session)
lobster query --workspace ~/immuno-project "Search for T cell datasets"
lobster query --workspace ~/immuno-project --session-id latest "Analyze that"
```

### Common patterns

**Single-cell analysis:**
```bash
lobster query "Download GSE109564 and perform quality control"
lobster query "Cluster the dataset and find marker genes"
lobster query "Create UMAP visualization colored by cell type"
```

**Literature mining:**
```bash
lobster query "Search PubMed for CRISPR screens in cancer"
lobster query "Find papers about CAR-T therapy and extract their GEO datasets"
lobster query "Get the full text and methods section for PMID:12345678"
```

**Dataset discovery:**
```bash
lobster query "Search GEO for single-cell pancreatic beta cell datasets"
lobster query "Validate GSE200997 metadata for required fields: cell_type, tissue"
lobster query "Download SRA dataset SRP123456"
```

**Data analysis:**
```bash
lobster query "Load counts.csv and run differential expression analysis"
lobster query "Perform batch correction on the loaded dataset"
lobster query "Generate volcano plot for DE results"
```

**Quality control:**
```bash
lobster query "Assess quality metrics for the loaded dataset"
lobster query "Filter cells with <200 genes or >8000 genes"
lobster query "Identify doublets using scrublet"
```

## Output handling

Lobster outputs are saved in the workspace directory (default: `.lobster_workspace/`):

**Key files to check:**
- `*.h5ad` - Processed datasets (AnnData format)
- `*.html` - Interactive visualizations
- `*.png` - Static plots for publications
- `*.csv` - Exported data tables
- `*.json` - Metadata and provenance

**To read results:**
```bash
# List workspace files
ls -lh .lobster_workspace/

# Read specific outputs
cat .lobster_workspace/analysis_summary.json
```

## Integration workflow

**Example 1: Analyze dataset and extract results**

```bash
# Step 1: Run analysis
lobster query --session-id "gse109564" "Download GSE109564, run QC, and cluster cells"

# Step 2: Check outputs
ls .lobster_workspace/*.h5ad
ls .lobster_workspace/*.html

# Step 3: Extract specific data
lobster query --session-id "gse109564" "Export cluster markers to CSV"

# Step 4: Use results in your code
# Results are now in .lobster_workspace/markers.csv
```

**Example 2: Literature mining workflow**

```bash
# Step 1: Find papers
lobster query "Search for papers about immune checkpoint inhibitors in melanoma"

# Step 2: Extract datasets
lobster query "Extract all GEO dataset IDs from the cached papers"

# Step 3: Validate datasets
lobster query "Check which datasets have cell_type and treatment metadata"

# Step 4: Download best match
lobster query "Download the dataset with most samples"
```

## Advanced features

**Export reproducible notebooks:**
```bash
lobster query "Export the analysis pipeline as a Jupyter notebook"
# Creates a Papermill-compatible notebook in workspace
```

**Workspace management:**
```bash
# Use custom workspace per project
lobster query --workspace ./project1-data "Analyze counts.csv"
lobster query --workspace ./project2-data "Analyze other-counts.csv"
```

**Provider switching (if multiple LLM providers configured):**
```bash
# Use specific provider
lobster query --provider ollama "Run expensive analysis"  # Free local
lobster query --provider anthropic "Quick task"  # Fast cloud
```

## Troubleshooting

**Command not found:**
- Verify installation: `which lobster`
- Install: `uv pip install lobster-ai`
- Configure: `lobster init`

**Rate limit errors:**
- Using Anthropic? Switch to Ollama (free) or AWS Bedrock (enterprise)
- Wait 60 seconds and retry
- Configure Ollama: `ollama pull llama3:8b-instruct && export LOBSTER_LLM_PROVIDER=ollama`

**Analysis errors:**
- Check workspace: `ls .lobster_workspace/`
- View session log: `cat ~/.lobster/.session.json`
- Try with reasoning: `lobster query --reasoning "<request>"`

**No output files:**
- Verify workspace location: `lobster query "show workspace info"`
- Check for errors in command output
- Ensure request was analysis (not just information retrieval)

## Tips for effective use

1. **Be specific:** Instead of "analyze data", say "perform single-cell clustering with resolution 0.5"
2. **Chain operations:** "Download GSE12345, run QC, cluster, and export markers to CSV"
3. **Check outputs:** Always verify generated files in `.lobster_workspace/`
4. **Use reasoning mode:** For complex multi-step tasks, add `--reasoning` flag
5. **Provide context:** Reference specific files, datasets, or previous results

## Limitations

- Lobster requires active LLM provider (Ollama/Anthropic/Bedrock)
- Large datasets (>100K cells) may be slow depending on system resources
- Some features require premium subscription (proteomics, metadata assistant)
- Full-text paper access limited by journal availability
- Rate limits apply when using cloud LLM providers

## Documentation

- Wiki: https://github.com/the-omics-os/lobster-local/wiki
- Examples: https://github.com/the-omics-os/lobster-local/wiki/27-examples-cookbook
- Installation: https://github.com/the-omics-os/lobster-local/wiki/02-installation
- Configuration: https://github.com/the-omics-os/lobster-local/wiki/03-configuration

## Version

This Skill is compatible with:
- Lobster AI v0.3.1.4+
- Claude Code v1.0+

For issues or questions: https://github.com/the-omics-os/lobster-local/issues
