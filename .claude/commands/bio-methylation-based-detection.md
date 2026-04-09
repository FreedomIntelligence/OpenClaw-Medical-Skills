# bio-methylation-based-detection

> Analyzes cfDNA methylation patterns for cancer detection using cfMeDIP-seq or bisulfite sequencing with MethylDackel. Identifies cancer-specific methylation signatures and performs tissue-of-origin deconvolution. Use when using methylation biomarkers for early cancer detection or minimal residual disease.

## Version Compatibility

Reference examples tested with: Bismark 0.24+, numpy 1.26+, pandas 2.2+, pysam 0.22+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Methylation-Based Detection

**"Detect cancer from cfDNA methylation patterns"** → Analyze cell-free DNA methylation for multi-cancer early detection and tissue-of-origin classification using bisulfite or enzymatic conversion.
- CLI: `MethylDackel extract` for methylation calling from cfDNA bisulfite data

Analyze cfDNA methylation for cancer detection and tissue-of-origin analysis.

## Methods Overview

| Method | Description | cfDNA Input |
|--------|-------------|-------------|
| cfMeDIP-seq | Enrichment-based, good for low input | >= 5 ng |
| Bisulfite-seq | Single-base resolution | >= 10 ng |
| EM-seq | Enzymatic, less degradation | >= 10 ng |

## MethylDackel Pipeline

MethylDackel is actively maintained and integrated with nf-core/methylseq.

```bash
# Extract methylation from bisulfite BAM
MethylDackel extract \
    reference.fa \
    sample_bismark.bam \
    --CHG \
    --CHH \
    -o sample_methylation

# Output: sample_methylation_CpG.bedGraph, etc.

# Merge C and G strand calls
MethylDackel mergeContext \
    reference.fa \
    sample_methylation
```

## Python Implementation

```python
import subprocess
import pandas as pd
import numpy as np


def extract_methylation(bam_file, reference, output_prefix, min_depth=5):
    '''
    Extract methylation from bisulfite-seq BAM using MethylDackel.
    '''
    subprocess.run([
        'MethylDackel', 'extract',
        reference,
        bam_file,
        '-o', output_prefix,
        '--minDepth', str(min_depth),
        '--mergeContext'
    ], check=True)

    # Parse output
    bedgraph = f'{output_prefix}_CpG.bedGraph'
    meth = pd.read_csv(bedgraph, sep='\t', header=None,
                       names=['chrom', 'start', 'end', 'meth_pct', 'meth', 'unmeth'])

    return meth


def calculate_methylation_beta(meth_df):
    '''Calculate beta values (0-1 scale).'''
    meth_df['beta'] = meth_df['meth'] / (meth_df['meth'] + meth_df['unmeth'])
    return meth_df
```

## DMR Detection

```python
def find_differentially_methylated_regions(cancer_samples, normal_samples, min_diff=0.2):
    '''
    Find differentially methylated regions between cancer and normal.

    Args:
        cancer_samples: List of methylation DataFrames
        normal_samples: List of methylation DataFrames
        min_diff: Minimum beta difference
    '''
    from scipy import stats

    # Merge samples
    cancer_betas = pd.concat([s['beta'] for s in cancer_samples], axis=1)
    normal_betas = pd.concat([s['beta'] for s in normal_samples], axis=1)

    results = []

    for idx in cancer_betas.index:
        c_vals = cancer_betas.loc[idx].dropna()
        n_vals = normal_betas.loc[idx].dropna()

        if len(c_vals) < 3 or len(n_vals) < 3:
            continue

        diff = c_vals.mean() - n_vals.mean()
        stat, pval = stats.mannwhitneyu(c_vals, n_vals, alternative='two-sided')

        if abs(diff) >= min_diff:
            results.append({
                'region': idx,
                'cancer_mean': c_vals.mean(),
                'normal_mean': n_vals.mean(),
                'diff': diff,
                'pvalue': pval
            })

    results_df = pd.DataFrame(results)

    # FDR correction
    from statsmodels.stats.multitest import multipletests
    if len(results_df) > 0:
        _, results_df['fdr'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')

    return results_df.sort_values('fdr')
```

## Tissue Deconvolution

**Goal:** Estimate the tissue-of-origin composition of cfDNA by decomposing its methylation profile against a reference atlas of tissue-specific methylomes.

**Approach:** Align sample beta values to reference atlas regions, then solve for non-negative tissue proportions using constrained least squares (NNLS) and normalize to sum to one.

```python
def tissue_deconvolution(sample_meth, reference_atlas):
    '''
    Deconvolve tissue composition from cfDNA methylation.

    Args:
        sample_meth: Sample methylation DataFrame
        reference_atlas: Reference methylomes per tissue type
    '''
    from scipy.optimize import nnls

    # Align samples to reference regions
    common_regions = sample_meth.index.intersection(reference_atlas.index)

    sample_vec = sample_meth.loc[common_regions, 'beta'].values
    ref_matrix = reference_atlas.loc[common_regions].values

    # Non-negative least squares for proportions
    proportions, residual = nnls(ref_matrix, sample_vec)

    # Normalize to sum to 1
    proportions = proportions / proportions.sum()

    return dict(zip(reference_atlas.columns, proportions))
```

## MCED Panel Analysis

```python
def analyze_mced_regions(meth_df, mced_regions):
    '''
    Analyze multi-cancer early detection (MCED) regions.
    Similar to Galleri-style analysis.
    '''
    results = {}

    for cancer_type, regions in mced_regions.items():
        region_betas = meth_df[meth_df['chrom'].isin(regions)]
        results[cancer_type] = {
            'mean_beta': region_betas['beta'].mean(),
            'hypermethylated_frac': (region_betas['beta'] > 0.8).mean(),
            'hypomethylated_frac': (region_betas['beta'] < 0.2).mean()
        }

    return results
```

## cfMeDIP-seq Analysis

```python
def analyze_cfmedip(bam_file, output_prefix, genome_bins):
    '''
    Analyze cfMeDIP-seq data for methylation enrichment.
    '''
    import pysam

    bam = pysam.AlignmentFile(bam_file, 'rb')

    bin_counts = {}
    for chrom, start, end in genome_bins:
        count = bam.count(chrom, start, end)
        bin_counts[(chrom, start, end)] = count

    bam.close()

    # Normalize by total reads and bin size
    total = sum(bin_counts.values())
    for key in bin_counts:
        bin_size = key[2] - key[1]
        bin_counts[key] = (bin_counts[key] / total) * 1e6 / (bin_size / 1000)  # RPM per kb

    return bin_counts
```

## Related Skills

- cfdna-preprocessing - Preprocess before methylation analysis
- fragment-analysis - Complement with fragmentomics
- methylation-analysis/bismark-alignment - General methylation processing
