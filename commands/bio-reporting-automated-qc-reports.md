# bio-reporting-automated-qc-reports

> Generates standardized quality control reports by aggregating metrics from FastQC, alignment, and other tools using MultiQC. Use when summarizing QC metrics across samples, creating shareable quality reports, or building automated QC pipelines.

**Available tools:** Read, Bash

# Automated QC Reports with MultiQC

## Basic Usage

```bash
# Aggregate all QC outputs in directory
multiqc results/ -o qc_report/

# Specify output name
multiqc results/ -n my_project_qc

# Include specific tools only
multiqc results/ --module fastqc --module star
```

## Supported Tools

MultiQC recognizes outputs from 100+ bioinformatics tools:

| Category | Tools |
|----------|-------|
| Read QC | FastQC, fastp, Cutadapt |
| Alignment | STAR, HISAT2, BWA, Bowtie2 |
| Quantification | featureCounts, Salmon, kallisto |
| Variant Calling | bcftools, GATK |
| Single-cell | CellRanger, STARsolo |

## Configuration

Create `multiqc_config.yaml`:

```yaml
title: "RNA-seq QC Report"
subtitle: "Project XYZ"
intro_text: "QC metrics for all samples"

# Custom sample name cleaning
extra_fn_clean_exts:
  - '.sorted'
  - '.dedup'

# Report sections to include
module_order:
  - fastqc
  - star
  - featurecounts

# Highlight samples
table_cond_formatting_rules:
  pct_mapped:
    fail: [{lt: 50}]
    warn: [{lt: 70}]
```

## Custom Data

```bash
# Add custom data file
# File format: sample\tmetric1\tmetric2
multiqc results/ --data-format tsv --custom-data-file custom_metrics.tsv
```

## Python API

```python
from multiqc import run as multiqc_run

# Run programmatically
multiqc_run(analysis_dir='results/', outdir='qc_report/')
```

## Related Skills

- read-qc/quality-reports - Generate input FastQC reports
- read-qc/fastp-workflow - Preprocessing QC
- workflows/rnaseq-to-de - Full workflow with QC
