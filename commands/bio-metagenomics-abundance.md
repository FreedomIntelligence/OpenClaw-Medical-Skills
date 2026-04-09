# bio-metagenomics-abundance

> Species abundance estimation using Bracken with Kraken2 output. Redistributes reads from higher taxonomic levels to species for more accurate estimates. Use when accurate species-level abundances are needed from Kraken2 classification output.

## Version Compatibility

Reference examples tested with: Bracken 2.9+, Kraken2 2.1+, MetaPhlAn 4.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Abundance Estimation with Bracken

**"Get species-level abundances from my Kraken2 results"** → Redistribute reads assigned to higher taxonomic levels down to species using Bracken's Bayesian re-estimation for more accurate abundance profiles.
- CLI: `bracken -d db -i kraken2.report -o bracken.output -r 150 -l S`

## Basic Abundance Estimation

```bash
# Run Bracken on Kraken2 report
bracken -d /path/to/kraken2_db \
    -i kraken_report.txt \
    -o bracken_output.txt \
    -r 150 \                       # Read length (100, 150, 200, 250, 300)
    -l S                           # Taxonomic level
```

## Full Workflow with Kraken2

```bash
# Step 1: Classify with Kraken2
kraken2 --db /path/to/kraken2_db \
    --threads 8 \
    --paired \
    --report sample_kraken_report.txt \
    reads_R1.fastq.gz reads_R2.fastq.gz

# Step 2: Estimate abundances with Bracken
bracken -d /path/to/kraken2_db \
    -i sample_kraken_report.txt \
    -o sample_bracken_species.txt \
    -w sample_bracken_report.txt \
    -r 150 \
    -l S
```

## Different Taxonomic Levels

```bash
# Species level (default)
bracken -d db -i report.txt -o species.txt -r 150 -l S

# Genus level
bracken -d db -i report.txt -o genus.txt -r 150 -l G

# Family level
bracken -d db -i report.txt -o family.txt -r 150 -l F

# Phylum level
bracken -d db -i report.txt -o phylum.txt -r 150 -l P
```

## Build Bracken Database

```bash
# Build Bracken database for specific read lengths
# Run AFTER building Kraken2 database
bracken-build -d /path/to/kraken2_db -t 8 -l 150

# Build for multiple read lengths
bracken-build -d /path/to/kraken2_db -t 8 -l 100
bracken-build -d /path/to/kraken2_db -t 8 -l 250
```

## Output Format

```
name                    taxonomy_id    taxonomy_lvl    kraken_assigned_reads    added_reads    new_est_reads    fraction_total_reads
Escherichia coli        562           S               5234                     1245           6479             0.52
Staphylococcus aureus   1280          S               2156                     456            2612             0.21
```

## Filter Low-Abundance Taxa

```bash
# Use threshold for minimum reads
bracken -d db \
    -i report.txt \
    -o bracken.txt \
    -r 150 \
    -l S \
    -t 10                          # Minimum reads threshold
```

## Combine Multiple Samples

```bash
# Run Bracken on each sample
for report in kraken_reports/*.txt; do
    sample=$(basename $report _kraken_report.txt)
    bracken -d db -i $report -o bracken/${sample}_species.txt -r 150 -l S
done

# Combine into abundance matrix
combine_bracken_outputs.py --files bracken/*_species.txt -o combined_abundance.txt
```

## Parse Bracken Output in Python

```python
import pandas as pd

bracken = pd.read_csv('bracken_output.txt', sep='\t')

bracken_sorted = bracken.sort_values('new_est_reads', ascending=False)
bracken_sorted[['name', 'fraction_total_reads']].head(20)

total_reads = bracken['new_est_reads'].sum()
bracken['relative_abundance'] = bracken['new_est_reads'] / total_reads * 100
```

## Convert to Relative Abundance

```python
import pandas as pd

df = pd.read_csv('bracken_output.txt', sep='\t')

total = df['new_est_reads'].sum()
df['relative_abundance'] = df['new_est_reads'] / total * 100

df.to_csv('bracken_relative_abundance.txt', sep='\t', index=False)
```

## Create Abundance Matrix

**Goal:** Merge per-sample Bracken outputs into a single species-by-sample abundance matrix for downstream statistical analysis.

**Approach:** Load each Bracken output, extract species names and read counts, iteratively outer-merge on species name, and fill missing values with zero.

```python
import pandas as pd
import os

files = [f for f in os.listdir('bracken') if f.endswith('_species.txt')]

dfs = []
for f in files:
    sample = f.replace('_species.txt', '')
    df = pd.read_csv(f'bracken/{f}', sep='\t')
    df = df[['name', 'new_est_reads']].rename(columns={'new_est_reads': sample})
    dfs.append(df)

merged = dfs[0]
for df in dfs[1:]:
    merged = merged.merge(df, on='name', how='outer')

merged = merged.fillna(0)
merged.to_csv('abundance_matrix.txt', sep='\t', index=False)
```

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| -d | Kraken2 database path |
| -i | Input Kraken2 report |
| -o | Output abundance file |
| -w | Output updated report (optional) |
| -r | Read length used |
| -l | Taxonomic level |
| -t | Minimum read threshold |

## Taxonomic Levels

| Level | Code | Description |
|-------|------|-------------|
| Kingdom | K | Bacteria, Archaea |
| Phylum | P | Major divisions |
| Class | C | Class level |
| Order | O | Order level |
| Family | F | Family level |
| Genus | G | Genus level |
| Species | S | Species level |

## Read Length Options

Pre-built databases typically include: 50, 75, 100, 150, 200, 250, 300 bp

Choose the length closest to your actual read length.

## Related Skills

- kraken-classification - Generate Kraken2 report
- metaphlan-profiling - Alternative profiling method
- metagenome-visualization - Visualize abundances
