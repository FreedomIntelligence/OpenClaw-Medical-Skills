# galaxy-bridge

> Galaxy tool discovery, intelligent recommendation, and execution — 8,000+ bioinformatics tools from usegalaxy.org with multi-signal scoring and workflow suggestions

# Galaxy Bridge

**ClawBio's gateway to the Galaxy ecosystem — 1,770+ production bioinformatics tools, discoverable and executable through natural language.**

## Why This Exists

Galaxy (usegalaxy.org) hosts the world's largest collection of curated bioinformatics tools — 1,770+ on the main server alone, covering everything from FASTQ QC to metagenomics to protein structure prediction. But discovering the right tool requires knowing exact tool IDs, navigating nested ToolShed categories, and understanding parameter schemas.

Galaxy Bridge makes these tools **agent-accessible**: search by natural language, execute via CLI, and chain Galaxy tools with ClawBio's local skills for cross-platform workflows that neither system can do alone.

## Core Capabilities

1. **Intelligent tool recommendation** — describe a task in plain English; multi-signal scoring across 7 dimensions returns the best Galaxy tool with explanations
2. **Workflow suggestions** — 8 pre-defined pipeline templates (RNA-seq DE, metagenomics, variant calling, WES germline, ChIP-seq, nanopore, genome assembly, variant annotation)
3. **Input format awareness** — provide your file extension (.fastq, .bam, .vcf) for format-aware recommendations
4. **Version deduplication** — 8,182 catalog entries collapse to ~2,300 unique tools; latest version preferred, version count as maturity signal
5. **EDAM ontology resolution** — 108 EDAM topic/operation IDs resolved to human-readable labels for richer matching
6. **Natural language search** — keyword-based search across 8,000+ Galaxy tools by name, description, section, and EDAM terms
7. **Remote execution** — run Galaxy tools on usegalaxy.org via BioBlend API
8. **Category browsing** — explore 86 ToolShed categories with tool counts
9. **Tool detail inspection** — view inputs, outputs, and parameter schemas
10. **Offline demo mode** — FastQC demo with pre-cached results (no API key needed)
11. **Cross-platform chaining** — Galaxy VEP → ClawBio PharmGx, Galaxy Kraken2 → ClawBio metagenomics

## Input Formats

| Format | Extension | Required Fields | Example |
|--------|-----------|----------------|---------|
| FASTQ | `.fq`, `.fastq`, `.fq.gz` | Sequence reads | Illumina paired-end reads |
| VCF | `.vcf`, `.vcf.gz` | Variant calls | Annotated VCF for VEP |
| BAM | `.bam` | Aligned reads | BWA-MEM2 output |
| FASTA | `.fa`, `.fasta` | Sequences | Reference genome |
| Tabular | `.tsv`, `.csv` | Varies by tool | Gene expression matrix |

## Workflow

1. **Search** — User describes what they need → bridge searches local catalog + Galaxy API
2. **Select** — Ranked results with descriptions, versions, and categories
3. **Configure** — Show tool inputs/outputs schema; user provides files and parameters
4. **Execute** — Upload input to Galaxy, run tool, poll for completion
5. **Retrieve** — Download outputs to local directory
6. **Bundle** — Generate reproducibility package (commands.sh, environment.yml, checksums)

## CLI Reference

```bash
# Intelligent tool recommendation (new in v0.2.0)
python galaxy_bridge.py --recommend "quality control on my sequencing reads"
python galaxy_bridge.py --recommend "classify microbial species" --format .fastq
python galaxy_bridge.py --recommend "call variants" --format .bam
python galaxy_bridge.py --recommend "annotate variants from WES" --format .vcf

# Workflow / pipeline suggestions (new in v0.2.0)
python galaxy_bridge.py --workflow "RNA-seq differential expression"
python galaxy_bridge.py --workflow "metagenomics"
python galaxy_bridge.py --workflow "whole exome sequencing"

# Search for tools by keyword
python galaxy_bridge.py --search "metagenomics profiling"
python galaxy_bridge.py --search "variant annotation"
python galaxy_bridge.py --search "RNA-seq differential expression"

# Browse Galaxy ToolShed categories
python galaxy_bridge.py --list-categories

# View tool details (inputs, outputs, parameters)
python galaxy_bridge.py --tool-details toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.74+galaxy1

# Run a tool on Galaxy (requires GALAXY_API_KEY)
python galaxy_bridge.py --run fastqc --input reads.fq.gz --output /tmp/qc_results

# Demo mode (works offline, no API key needed)
python galaxy_bridge.py --demo
```

## Recommendation Engine

The `--recommend` flag uses **multi-signal scoring** across 7 dimensions to rank tools:

| Signal | Max Points | Description |
|--------|-----------|-------------|
| Section match | 30 | Tool's Galaxy category matches the detected task |
| Preferred tool | 20 | Tool is a known best-in-class for the task |
| Exact name match | 15 | Tool name appears in the query |
| Keyword match | 15 | Query words found in tool name/description |
| EDAM ontology | 10 | EDAM topic/operation IDs match the task |
| Format compatibility | 10 | Tool accepts the specified input format |
| Version maturity | 5 | Tools with more versions score higher (log scale) |

**15 task categories** are recognised: Quality Control, Read Mapping, Variant Calling, Variant Annotation, WES/WGS, RNA-seq, Metagenomics, Genome Assembly, Genome Annotation, Phylogenetics, ChIP-seq, Single-cell, Proteomics, Nanopore, BAM Processing.

**8 workflow templates**: WES Germline, WES Annotation, RNA-seq DE, Metagenomics Profiling, Variant Calling, ChIP-seq, Nanopore Assembly, Genome Assembly.

## Demo

Running `--demo` executes a simulated FastQC analysis using pre-cached results:

```
$ python galaxy_bridge.py --demo

Galaxy Bridge — Demo Mode (offline)
====================================
Tool: FastQC v0.74+galaxy1
Input: demo/demo_reads.fq (bundled synthetic FASTQ, 1000 reads)
Output: demo/fastqc_demo_output.html

Result: PASS — Per base sequence quality ✓
        PASS — Per sequence quality scores ✓
        WARN — Per base sequence content (normal for Illumina)
        PASS — Sequence length distribution ✓

Reproducibility bundle written to demo/reproducibility/
```

## Galaxy Tool Categories

The bridge indexes tools across all 56 Galaxy ToolShed categories, including:

- **Sequence Analysis** (~30 tools): FastQC, Trimmomatic, Cutadapt, fastp
- **Metagenomics** (~25 tools): Kraken2, MetaPhlAn, HUMAnN, QIIME2
- **Variant Analysis** (~25 tools): VEP, SnpSift, BCFtools, FreeBayes
- **RNA** (~20 tools): HISAT2, StringTie, featureCounts, DESeq2
- **Proteomics** (~15 tools): MaxQuant, SearchGUI, PeptideShaker
- **Phylogenetics** (~15 tools): IQ-TREE, RAxML, MAFFT, MUSCLE
- **Genome Annotation** (~15 tools): Prokka, Augustus, MAKER
- **Assembly** (~15 tools): SPAdes, Flye, Unicycler, MEGAHIT
- **Single Cell** (~10 tools): Scanpy, CellRanger, Seurat
- **ChIP-seq/Epigenetics** (~10 tools): MACS2, deepTools, DiffBind
- **GWAS** (~10 tools): PLINK, REGENIE, BOLT-LMM
- **Nanopore** (~10 tools): NanoPlot, Medaka, minimap2

## Output Structure

```
output_dir/
├── report.md              # Analysis summary with methods and results
├── result.json            # Machine-readable: tool ID, version, parameters, output paths
├── galaxy_outputs/        # Raw outputs downloaded from Galaxy
│   ├── fastqc_report.html
│   └── ...
└── reproducibility/
    ├── commands.sh        # Galaxy API calls to reproduce
    ├── environment.yml    # Tool versions and Galaxy server info
    └── checksums.sha256   # SHA-256 of all inputs and outputs
```

## Dependencies

**Required:**
- Python 3.9+
- bioblend (Galaxy Python SDK)

**Optional (for execution):**
- `GALAXY_URL` environment variable (default: `https://usegalaxy.org`)
- `GALAXY_API_KEY` environment variable (register at usegalaxy.org)

## Safety

- **Local-first search**: Tool discovery uses the bundled `galaxy_catalog.json` — no API calls needed
- **API key optional**: Demo mode and search work without credentials
- **No data retention**: Uploaded files are deleted from Galaxy after output retrieval
- **Reproducibility**: Every execution generates a full provenance bundle
- **Disclaimer**: ClawBio is a research and educational tool. It is not a medical device and does not provide clinical diagnoses. Consult a healthcare professional before making any medical decisions.

## Integration with Bio Orchestrator

**Triggers when**: User mentions "galaxy", "usegalaxy", "tool shed", "run on galaxy", "NGS pipeline", or references a Galaxy tool ID.

**Chaining partners**:
- `pharmgx-reporter` — Galaxy VEP annotates variants → PharmGx generates dosage report
- `claw-metagenomics` — Galaxy Kraken2 → ClawBio metagenomics profiling
- `equity-scorer` — Galaxy VCF processing → HEIM equity scoring
- `vcf-annotator` — Galaxy VEP/SnpSift ↔ ClawBio annotation

## Citations

- [Galaxy Project](https://galaxyproject.org/) — Afgan et al. (2018) Nucleic Acids Research
- [BioBlend](https://bioblend.readthedocs.io/) — Sloggett et al. (2013) Bioinformatics
- [usegalaxy.org](https://usegalaxy.org/) — Main Galaxy public server
- [Galaxy ToolShed](https://toolshed.g2.bx.psu.edu/) — Community tool repository
