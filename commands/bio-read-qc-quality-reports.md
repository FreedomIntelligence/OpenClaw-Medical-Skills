# bio-read-qc-quality-reports

> Generate and interpret quality reports from FASTQ files using FastQC and MultiQC. Assess per-base quality, adapter content, GC bias, duplication levels, and overrepresented sequences. Use when performing initial QC on raw sequencing data or validating preprocessing results.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Quality Reports

Generate quality reports for FASTQ files using FastQC and aggregate multiple reports with MultiQC.

**"Run quality control on FASTQ files"** → Generate per-base quality, adapter content, and duplication plots, then aggregate across samples.
- CLI: `fastqc *.fastq.gz` then `multiqc .`

## FastQC - Single Sample Reports

### Basic Usage

```bash
# Single file
fastqc sample.fastq.gz

# Multiple files
fastqc *.fastq.gz

# Specify output directory
fastqc -o qc_reports/ sample_R1.fastq.gz sample_R2.fastq.gz

# Set threads
fastqc -t 4 *.fastq.gz
```

### Output Files

FastQC produces two files per input:
- `sample_fastqc.html` - Interactive HTML report
- `sample_fastqc.zip` - Data files and images

### Key Modules

| Module | What It Shows | Warning Signs |
|--------|---------------|---------------|
| Per base sequence quality | Quality scores across read | Drop below Q20 at 3' end |
| Per sequence quality | Quality score distribution | Bimodal distribution |
| Per base sequence content | Nucleotide composition | Imbalance at start (normal) |
| Per sequence GC content | GC distribution | Secondary peak (contamination) |
| Per base N content | Unknown bases | High N content |
| Sequence length distribution | Read lengths | Unexpected variation |
| Sequence duplication | Duplicate reads | High duplication (PCR) |
| Overrepresented sequences | Common sequences | Adapter contamination |
| Adapter content | Adapter sequences | Visible adapter curves |

### Extract Data from ZIP

```bash
# Unzip to access raw data
unzip sample_fastqc.zip

# View summary
cat sample_fastqc/summary.txt

# Get per-base quality
cat sample_fastqc/fastqc_data.txt | grep -A 50 ">>Per base sequence quality"
```

## MultiQC - Aggregate Reports

### Basic Usage

```bash
# Aggregate all FastQC reports in current directory
multiqc .

# Specify input and output
multiqc qc_reports/ -o multiqc_output/

# Custom report name
multiqc . -n my_project_qc

# Force overwrite
multiqc . -f
```

### Common Options

```bash
# Flat directory (no sample subdirs)
multiqc --flat .

# Export data as TSV
multiqc . --export

# Only specific modules
multiqc . -m fastqc

# Exclude patterns
multiqc . --ignore '*_trimmed*'

# Include patterns
multiqc . --ignore-samples '*negative*'
```

### Output Files

- `multiqc_report.html` - Interactive HTML report
- `multiqc_data/` - Directory with data tables
  - `multiqc_fastqc.txt` - FastQC metrics
  - `multiqc_general_stats.txt` - Summary statistics
  - `multiqc_sources.txt` - Source files used

### Extract Data Programmatically

```python
import pandas as pd

general_stats = pd.read_csv('multiqc_data/multiqc_general_stats.txt', sep='\t')
print(general_stats.columns)

fastqc_data = pd.read_csv('multiqc_data/multiqc_fastqc.txt', sep='\t')
```

## Batch Processing

### Process Multiple Samples

```bash
# All FASTQ files in parallel
fastqc -t 8 -o qc_reports/ raw_data/*.fastq.gz

# Then aggregate
multiqc qc_reports/ -o multiqc_output/
```

### Before and After Trimming

```bash
# Create separate directories
mkdir -p qc_reports/raw qc_reports/trimmed

# QC raw reads
fastqc -o qc_reports/raw/ raw_data/*.fastq.gz

# After trimming (using fastp, cutadapt, etc.)
fastqc -o qc_reports/trimmed/ trimmed_data/*.fastq.gz

# Compare with MultiQC
multiqc qc_reports/ -o qc_comparison/
```

## Interpretation Guide

### Quality Scores

| Phred Score | Error Rate | Interpretation |
|-------------|------------|----------------|
| Q40 | 0.0001 | Excellent |
| Q30 | 0.001 | Good (Illumina target) |
| Q20 | 0.01 | Acceptable |
| Q10 | 0.1 | Poor |

### Common Issues

| Issue | Likely Cause | Action |
|-------|--------------|--------|
| Low quality at 3' end | Normal degradation | Trim 3' end |
| Adapter contamination | Short inserts | Trim adapters |
| GC bias | Library prep | Consider correction |
| High duplication | Low complexity, PCR | Mark/remove duplicates |
| Overrepresented seqs | Adapters, primers | Check sequences |

## Configuration

### Custom Adapters

Create `~/.fastqc/Configuration/adapter_list.txt`:
```
Custom_Adapter_Name    ACGTACGTACGT
```

### Custom Limits

Create `~/.fastqc/Configuration/limits.txt` to customize thresholds:
```
# Warn if mean quality below 25
quality_sequence    warn    25
quality_sequence    error   20
```

## Related Skills

- adapter-trimming - Remove adapters detected by FastQC
- fastp-workflow - All-in-one QC and trimming
- sequence-io/read-sequences - FASTQ file reading/writing
