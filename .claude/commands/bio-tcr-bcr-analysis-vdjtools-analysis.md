# bio-tcr-bcr-analysis-vdjtools-analysis

> Calculate immune repertoire diversity metrics, compare samples, and track clonal dynamics using VDJtools. Use when analyzing repertoire diversity, finding shared clonotypes, or comparing immune profiles between conditions.

## Version Compatibility

Reference examples tested with: MiXCR 4.6+, VDJtools 1.2.1+, matplotlib 3.8+, pandas 2.2+, scanpy 1.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# VDJtools Analysis

**"Compute diversity and overlap for my TCR repertoires"** → Calculate repertoire diversity metrics, sample overlap, and perform statistical comparisons between immune repertoire samples.
- CLI: `vdjtools CalcDiversityStats`, `vdjtools OverlapPair`, `vdjtools PlotFancySpectratype`

## Basic Usage

**Goal:** Run VDJtools commands for immune repertoire analysis.

**Approach:** Invoke VDJtools via Java JAR or wrapper script with appropriate subcommand and options.

```bash
# VDJtools requires Java
java -jar vdjtools.jar <command> [options]

# Or with wrapper script
vdjtools <command> [options]
```

## Calculate Diversity Metrics

**Goal:** Compute repertoire diversity indices (Shannon, Simpson, Chao1, Gini) across samples.

**Approach:** Run CalcDiversityStats with a metadata file linking sample files to sample IDs and conditions.

```bash
# Basic diversity (Shannon, Simpson, Chao1, etc.)
vdjtools CalcDiversityStats \
    -m metadata.txt \
    output_dir/

# Metadata format (tab-separated):
# #file.name    sample.id    condition
# sample1.txt   S1           control
# sample2.txt   S2           treated
```

## Diversity Metrics Explained

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| Shannon | Entropy-based diversity | Higher = more diverse |
| Simpson | Probability two random clones differ | 0-1, higher = diverse |
| InverseSimpson | 1/Simpson | Effective number of clones |
| Chao1 | Richness estimator | Total estimated clonotypes |
| Gini | Inequality coefficient | 0=equal, 1=dominated by one |
| d50 | Clones comprising 50% of repertoire | Lower = more oligoclonal |

## Sample Comparison

**Goal:** Quantify clonotype sharing and repertoire overlap between samples or conditions.

**Approach:** Compute pairwise overlap metrics (Jaccard, Morisita-Horn, F2) on amino acid clonotype identities.

```bash
# Find overlapping clonotypes
vdjtools OverlapPair \
    -p sample1.txt sample2.txt \
    output_dir/

# Calculate overlap for all pairs
vdjtools CalcPairwiseDistances \
    -m metadata.txt \
    -i aa \
    output_dir/

# Overlap metrics: F2 (frequency-weighted Jaccard), Jaccard, MorisitaHorn
```

## Spectratype Analysis

**Goal:** Analyze CDR3 length distributions and V/J gene segment usage patterns across samples.

**Approach:** Generate spectratype (CDR3 length histogram) and segment usage tables via VDJtools commands.

```bash
# CDR3 length distribution (spectratype)
vdjtools CalcSpectratype \
    -m metadata.txt \
    output_dir/

# V/J gene usage
vdjtools CalcSegmentUsage \
    -m metadata.txt \
    output_dir/
```

## Clonal Tracking

**Goal:** Track individual clonotype frequencies across longitudinal timepoints and identify public clones shared across individuals.

**Approach:** Use TrackClonotypes for temporal tracking and JoinSamples to find public (cross-individual) clonotypes.

```bash
# Track clones across timepoints
vdjtools TrackClonotypes \
    -m metadata_timecourse.txt \
    -x time \
    output_dir/

# Identify public clones (shared across individuals)
vdjtools JoinSamples \
    -m metadata.txt \
    -p \
    output_dir/
```

## Input Format

VDJtools accepts MiXCR output or standard format:

```
# Required columns (tab-separated):
count   frequency   CDR3nt  CDR3aa  V   D   J

# Example:
1500    0.15    TGTGCCAGC...    CASSF...    TRBV5-1*01  TRBD2*01    TRBJ2-7*01
```

## Convert from MiXCR

**Goal:** Convert MiXCR clonotype output into VDJtools-compatible format.

**Approach:** Use VDJtools Convert command specifying MiXCR as the source software format.

```bash
# Convert MiXCR output to VDJtools format
vdjtools Convert \
    -S mixcr \
    mixcr_clones.txt \
    output.txt
```

## Parse VDJtools Output in Python

**Goal:** Load VDJtools diversity statistics and overlap matrices into Python for custom analysis and plotting.

**Approach:** Read tab-delimited VDJtools output files into pandas DataFrames and visualize diversity comparisons.

```python
import pandas as pd

def load_diversity_stats(filepath):
    '''Load VDJtools diversity statistics'''
    df = pd.read_csv(filepath, sep='\t')
    return df

def load_overlap_matrix(filepath):
    '''Load pairwise overlap matrix'''
    df = pd.read_csv(filepath, sep='\t', index_col=0)
    return df

# Plot diversity across samples
def plot_diversity(stats_df, metric='shannon_wiener_index_mean'):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.bar(stats_df['sample_id'], stats_df[metric])
    plt.xlabel('Sample')
    plt.ylabel(metric)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('diversity_plot.png')
```

## Related Skills

- mixcr-analysis - Generate input clonotype tables
- repertoire-visualization - Visualize VDJtools output
- immcantation-analysis - BCR-specific phylogenetics
