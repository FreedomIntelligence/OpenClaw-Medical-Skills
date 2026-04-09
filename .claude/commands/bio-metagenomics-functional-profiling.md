# bio-metagenomics-functional-profiling

> Profile functional potential of metagenomes using HUMAnN3 and similar tools. Use when obtaining pathway abundances, gene family counts, or functional annotations from metagenomic data.

## Version Compatibility

Reference examples tested with: HUMAnN 3.8+, MetaPhlAn 4.1+, matplotlib 3.8+, pandas 2.2+, scanpy 1.10+, scipy 1.12+, seaborn 0.13+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Functional Profiling

**"What metabolic pathways are present in my metagenome?"** → Profile functional potential of metagenomic samples to obtain pathway abundances and gene family counts using translated search against UniRef and MetaCyc.
- CLI: `humann --input reads.fastq --output results/` (HUMAnN3)

Profile the functional potential of metagenomic samples using HUMAnN3 to get pathway and gene family abundances.

## HUMAnN3 Workflow

### Installation

```bash
# Install via conda (recommended)
conda create -n humann -c bioconda humann
conda activate humann

# Download databases
humann_databases --download chocophlan full /path/to/databases
humann_databases --download uniref uniref90_diamond /path/to/databases

# Update config with database paths
humann_config --update database_folders nucleotide /path/to/databases/chocophlan
humann_config --update database_folders protein /path/to/databases/uniref
```

### Basic Usage

```bash
# Run HUMAnN3 on a single sample
humann --input sample.fastq.gz --output sample_humann

# With MetaPhlAn taxonomic profile (faster)
humann --input sample.fastq.gz \
       --taxonomic-profile sample_metaphlan.txt \
       --output sample_humann

# Paired-end reads (concatenate first)
cat sample_R1.fq.gz sample_R2.fq.gz > sample_concat.fq.gz
humann --input sample_concat.fq.gz --output sample_humann
```

### Output Files

```
sample_humann/
├── sample_genefamilies.tsv     # Gene family abundances (UniRef90)
├── sample_pathabundance.tsv    # MetaCyc pathway abundances
├── sample_pathcoverage.tsv     # Pathway coverage (0-1)
└── sample_humann_temp/         # Intermediate files
```

## Output Format

### Gene Families

```
# Gene Family   sample_Abundance-RPKs
UniRef90_A0A000|g__Bacteroides.s__Bacteroides_vulgatus   123.45
UniRef90_A0A001|unclassified                              67.89
UNMAPPED                                                  1000.0
```

### Pathway Abundance

```
# Pathway                                    sample_Abundance
PWY-5100: pyruvate fermentation              456.78
PWY-5100|g__Bacteroides.s__Bacteroides_vulgatus  234.56
PWY-5100|unclassified                        222.22
```

## Batch Processing

```bash
# Process multiple samples
for fq in *.fastq.gz; do
    sample=$(basename $fq .fastq.gz)
    humann --input $fq --output ${sample}_humann --threads 8
done

# Join tables across samples
humann_join_tables -i . -o merged_genefamilies.tsv --file_name genefamilies
humann_join_tables -i . -o merged_pathabundance.tsv --file_name pathabundance
```

## Normalization

```bash
# Normalize to relative abundance
humann_renorm_table -i merged_genefamilies.tsv \
                    -o genefamilies_relab.tsv \
                    -u relab

# Normalize to copies per million (CPM)
humann_renorm_table -i merged_pathabundance.tsv \
                    -o pathabundance_cpm.tsv \
                    -u cpm
```

## Regroup Gene Families

```bash
# Regroup to different functional categories
# EC numbers
humann_regroup_table -i genefamilies.tsv \
                     -g uniref90_level4ec \
                     -o genefamilies_ec.tsv

# KEGG Orthologs
humann_regroup_table -i genefamilies.tsv \
                     -g uniref90_ko \
                     -o genefamilies_ko.tsv

# GO terms
humann_regroup_table -i genefamilies.tsv \
                     -g uniref90_go \
                     -o genefamilies_go.tsv

# Pfam domains
humann_regroup_table -i genefamilies.tsv \
                     -g uniref90_pfam \
                     -o genefamilies_pfam.tsv
```

## Stratification

### Split by Organism

```bash
# Unstratify (remove organism info, sum across species)
humann_split_stratified_table -i merged_pathabundance.tsv \
                               -o .

# Creates: merged_pathabundance_unstratified.tsv
#          merged_pathabundance_stratified.tsv
```

### Species Contributions

```python
import pandas as pd

df = pd.read_csv('merged_pathabundance.tsv', sep='\t', index_col=0)

unstratified = df[~df.index.str.contains('\\|')]
stratified = df[df.index.str.contains('\\|')]

def get_species_contrib(pathway, df):
    '''Get species contributions to a pathway'''
    mask = df.index.str.startswith(pathway + '|')
    return df[mask]

contrib = get_species_contrib('PWY-5100', stratified)
```

## Quality Control

```bash
# Check unmapped and unintegrated
humann_barplot -i merged_pathabundance.tsv \
               -o pathabundance_barplot.png \
               --focal-feature UNMAPPED
```

### Key QC Metrics

| Metric | Good | Concerning |
|--------|------|------------|
| UNMAPPED (gene families) | <30% | >50% |
| UNINTEGRATED (pathways) | <40% | >60% |
| Pathway coverage | >0.5 | <0.3 |

## Differential Analysis

### LEfSe Format

```bash
# Format for LEfSe
humann_join_tables -i . -o merged.tsv --file_name pathabundance
humann_renorm_table -i merged.tsv -o merged_relab.tsv -u relab
```

### Python Analysis

**Goal:** Identify differentially abundant metabolic pathways between conditions from HUMAnN3 output.

**Approach:** Load unstratified pathway abundances, split samples by condition using metadata, run Mann-Whitney U tests per pathway, and apply FDR correction.

```python
import pandas as pd
from scipy import stats

df = pd.read_csv('pathabundance_cpm.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('metadata.tsv', sep='\t', index_col=0)

group1 = metadata[metadata['condition'] == 'healthy'].index
group2 = metadata[metadata['condition'] == 'disease'].index

results = []
for pathway in df.index:
    if '|' not in pathway and pathway != 'UNMAPPED':
        vals1 = df.loc[pathway, group1]
        vals2 = df.loc[pathway, group2]
        stat, pval = stats.mannwhitneyu(vals1, vals2)
        fc = vals2.mean() / (vals1.mean() + 1e-10)
        results.append({'pathway': pathway, 'pvalue': pval, 'fold_change': fc})

results_df = pd.DataFrame(results)
results_df['padj'] = stats.false_discovery_control(results_df['pvalue'])
```

## Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('pathabundance_relab.tsv', sep='\t', index_col=0)
df = df[~df.index.str.contains('\\|')]
df = df.drop(['UNMAPPED', 'UNINTEGRATED'], errors='ignore')
top = df.mean(axis=1).nlargest(20).index

plt.figure(figsize=(12, 8))
sns.heatmap(df.loc[top].T, cmap='viridis', xticklabels=True)
plt.tight_layout()
plt.savefig('pathway_heatmap.png')
```

## Related Skills

- metagenomics/metaphlan-profiling - Taxonomic profiling (input for HUMAnN)
- metagenomics/kraken-classification - Alternative taxonomy
- metagenomics/metagenome-visualization - Visualization methods
- pathway-analysis/kegg-pathways - KEGG pathway interpretation
