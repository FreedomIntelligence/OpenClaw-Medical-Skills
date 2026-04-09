# tooluniverse-epigenomics

> Production-ready genomics and epigenomics data processing for BixBench questions. Handles methylation array analysis (CpG filtering, differential methylation, age-related CpG detection, chromosome-level density), ChIP-seq peak analysis (peak calling, motif enrichment, coverage stats), ATAC-seq chromatin accessibility, multi-omics integration (expression + methylation correlation), and genome-wide statistics. Pure Python computation (pandas, scipy, numpy, pysam, statsmodels) plus ToolUniverse annotation tools (Ensembl, ENCODE, SCREEN, JASPAR, ReMap, RegulomeDB, ChIPAtlas). Supports BED, BigWig, methylation beta-value matrices, Illumina manifest files, and multi-sample clinical data. Use when processing methylation data, ChIP-seq peaks, ATAC-seq signals, or answering questions about CpG sites, differential methylation, chromatin accessibility, histone marks, or epigenomic statistics.

# Genomics and Epigenomics Data Processing

Production-ready computational skill for processing and analyzing epigenomics data. Combines local Python computation (pandas, scipy, numpy, pysam, statsmodels) with ToolUniverse annotation tools for regulatory context. Designed to solve BixBench-style questions about methylation, ChIP-seq, ATAC-seq, and multi-omics integration.

## When to Use This Skill

**Triggers**:
- User provides methylation data (beta-value matrices, Illumina arrays) and asks about CpG sites
- Questions about differential methylation analysis
- Age-related CpG detection or epigenetic clock questions
- Chromosome-level methylation density or statistics
- ChIP-seq peak files (BED format) with analysis questions
- ATAC-seq chromatin accessibility questions
- Multi-omics integration (expression + methylation, expression + ChIP-seq)
- Genome-wide epigenomic statistics
- Questions mentioning "methylation", "CpG", "ChIP-seq", "ATAC-seq", "histone", "chromatin", "epigenetic"
- Questions about missing data across clinical/genomic/epigenomic modalities
- Regulatory element annotation for processed epigenomic data

**Example Questions This Skill Solves**:
1. "How many patients have no missing data for vital status, gene expression, and methylation data?"
2. "What is the ratio of filtered age-related CpG density between chromosomes?"
3. "What is the genome-wide average chromosomal density of unique age-related CpGs per base pair?"
4. "How many CpG sites show significant differential methylation (padj < 0.05)?"
5. "What is the Pearson correlation between methylation and expression for gene X?"
6. "How many ChIP-seq peaks overlap with promoter regions?"
7. "What fraction of ATAC-seq peaks are in enhancer regions?"
8. "Which chromosome has the highest density of hypermethylated CpGs?"
9. "Filter CpG sites by variance > threshold and map to nearest genes"
10. "What is the average beta value difference between tumor and normal for chromosome 17?"

**NOT for** (use other skills instead):
- Gene regulation lookup without data files -> Use existing epigenomics annotation pattern
- RNA-seq differential expression -> Use `tooluniverse-rnaseq-deseq2`
- Variant calling/annotation from VCF -> Use `tooluniverse-variant-analysis`
- Gene enrichment analysis -> Use `tooluniverse-gene-enrichment`
- Protein structure analysis -> Use `tooluniverse-protein-structure-retrieval`

---

## Required Python Packages

```python
# Core (MUST be available)
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.stats.multitest as mt

# Optional but useful
import pysam      # BAM/CRAM file access
import gseapy     # Enrichment of genes from methylation analysis

# ToolUniverse (for annotation)
from tooluniverse import ToolUniverse
```

---

## KEY PRINCIPLES

1. **Data-first approach** - Load and inspect data files BEFORE any analysis
2. **Question-driven** - Parse what the user is actually asking and extract the specific numeric answer
3. **File format detection** - Automatically detect methylation arrays, BED files, BigWig, clinical data
4. **Coordinate system awareness** - Track genome build (hg19, hg38, mm10), handle chr prefix differences
5. **Statistical rigor** - Proper multiple testing correction, effect size filtering, sample size awareness
6. **Missing data handling** - Explicitly report and handle NaN/missing values
7. **Chromosome normalization** - Always normalize chromosome names (chr1 vs 1, chrX vs X)
8. **CpG site identification** - Parse Illumina probe IDs (cg/ch probes), genomic coordinates
9. **Report-first** - Create output file first, populate progressively
10. **English-first queries** - Use English in all tool calls

---

## Complete Workflow

### Phase 0: Question Parsing and Data Discovery

**CRITICAL FIRST STEP**: Before writing ANY code, parse the question to identify what is being asked and what data files are available.

#### 0.1 Discover Available Data Files

```python
import os
import glob

data_dir = "."  # or specified path
all_files = glob.glob(os.path.join(data_dir, "**/*"), recursive=True)

# Categorize files
methylation_files = [f for f in all_files if any(x in f.lower() for x in
    ['methyl', 'beta', 'cpg', 'illumina', '450k', '850k', 'epic', 'mval'])]
chipseq_files = [f for f in all_files if any(x in f.lower() for x in
    ['chip', 'peak', 'narrowpeak', 'broadpeak', 'histone'])]
atacseq_files = [f for f in all_files if any(x in f.lower() for x in
    ['atac', 'accessibility', 'openChromatin', 'dnase'])]
bed_files = [f for f in all_files if f.endswith(('.bed', '.bed.gz', '.narrowPeak', '.broadPeak'))]
bigwig_files = [f for f in all_files if f.endswith(('.bw', '.bigwig', '.bigWig'))]
clinical_files = [f for f in all_files if any(x in f.lower() for x in
    ['clinical', 'patient', 'sample', 'metadata', 'phenotype', 'survival'])]
expression_files = [f for f in all_files if any(x in f.lower() for x in
    ['express', 'rnaseq', 'fpkm', 'tpm', 'counts', 'transcriptom'])]
manifest_files = [f for f in all_files if any(x in f.lower() for x in
    ['manifest', 'annotation', 'probe', 'platform'])]

# Print summary
for category, files in [
    ('Methylation', methylation_files),
    ('ChIP-seq', chipseq_files),
    ('ATAC-seq', atacseq_files),
    ('BED', bed_files),
    ('BigWig', bigwig_files),
    ('Clinical', clinical_files),
    ('Expression', expression_files),
    ('Manifest', manifest_files),
]:
    if files:
        print(f"{category}: {files}")
```

#### 0.2 Parse Question Parameters

Extract these from the question:

| Parameter | Default | Example Question Text |
|-----------|---------|----------------------|
| **Significance threshold** | 0.05 | "padj < 0.05", "FDR < 0.01" |
| **Beta difference threshold** | 0 | "|delta_beta| > 0.2", "mean difference > 0.1" |
| **Variance filter** | None | "variance > 0.01", "top 5000 most variable" |
| **Chromosome filter** | All | "chromosome 17", "autosomes only" |
| **Genome build** | hg38 | "hg19", "GRCh37", "mm10" |
| **CpG type filter** | All | "cg probes only", "exclude ch probes" |
| **Region filter** | None | "promoter", "gene body", "intergenic" |
| **Missing data handling** | Report | "complete cases", "no missing data" |
| **Specific comparison** | Infer | "tumor vs normal", "old vs young" |
| **Specific statistic** | Infer | "density", "ratio", "count", "average" |

#### 0.3 Decision Tree

```
Q: What type of epigenomics data?
  METHYLATION -> Phase 1 (Methylation Processing)
  CHIP-SEQ    -> Phase 2 (ChIP-seq Processing)
  ATAC-SEQ    -> Phase 3 (ATAC-seq Processing)
  MULTI-OMICS -> Phase 4 (Integration)
  CLINICAL    -> Phase 5 (Clinical Integration)
  ANNOTATION  -> Phase 6 (ToolUniverse Annotation)

Q: Is this a genome-wide statistics question?
  YES -> Focus on chromosome-level aggregation (Phase 7)
  NO  -> Focus on site/region-level analysis
```

---

### Phase 1: Methylation Data Processing

#### 1.1 Load Methylation Data

```python
import pandas as pd
import numpy as np

def load_methylation_data(file_path, **kwargs):
    """Load methylation beta-value or M-value matrix.

    Expected format:
    - Rows: CpG probes (cg00000029, cg00000108, ...)
    - Columns: Samples (TCGA-XX-XXXX, ...)
    - Values: Beta values (0-1) or M-values (log2 ratio)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.csv']:
        df = pd.read_csv(file_path, index_col=0, **kwargs)
    elif ext in ['.tsv', '.txt']:
        df = pd.read_csv(file_path, sep='\t', index_col=0, **kwargs)
    elif ext in ['.parquet']:
        df = pd.read_parquet(file_path, **kwargs)
    elif ext in ['.h5', '.hdf5']:
        df = pd.read_hdf(file_path, **kwargs)
    else:
        # Try tab first, then comma
        try:
            df = pd.read_csv(file_path, sep='\t', index_col=0, **kwargs)
        except Exception:
            df = pd.read_csv(file_path, index_col=0, **kwargs)

    return df


def detect_methylation_type(df):
    """Detect if data is beta values (0-1) or M-values (unbounded)."""
    sample_vals = df.iloc[:1000, :5].values.flatten()
    sample_vals = sample_vals[~np.isnan(sample_vals)]

    if sample_vals.min() >= 0 and sample_vals.max() <= 1:
        return 'beta'
    else:
        return 'mvalue'


def beta_to_mvalue(beta):
    """Convert beta values to M-values: M = log2(beta / (1 - beta))."""
    beta = np.clip(beta, 1e-6, 1 - 1e-6)
    return np.log2(beta / (1 - beta))


def mvalue_to_beta(mvalue):
    """Convert M-values to beta values: beta = 2^M / (2^M + 1)."""
    return 2**mvalue / (2**mvalue + 1)
```

#### 1.2 Load Methylation Manifest / Probe Annotation

```python
def load_probe_annotation(manifest_path):
    """Load Illumina methylation array manifest.

    Common columns: IlmnID, Name, CHR, MAPINFO (position), Strand,
    UCSC_RefGene_Name, UCSC_RefGene_Group, Relation_to_UCSC_CpG_Island
    """
    # Try reading manifest - may have header rows to skip
    for skiprows in [0, 7, 8]:
        try:
            manifest = pd.read_csv(manifest_path, skiprows=skiprows,
                                    low_memory=False)
            if 'CHR' in manifest.columns or 'chr' in manifest.columns:
                break
            if 'Name' in manifest.columns or 'IlmnID' in manifest.columns:
                break
        except Exception:
            continue

    # Normalize column names
    col_map = {}
    for col in manifest.columns:
        lower = col.lower()
        if lower in ['chr', 'chromosome']:
            col_map[col] = 'chr'
        elif lower in ['mapinfo', 'position', 'pos', 'start']:
            col_map[col] = 'position'
        elif lower in ['name', 'ilmnid', 'probe_id', 'cpg_id']:
            col_map[col] = 'probe_id'
        elif 'refgene_name' in lower or 'gene' in lower:
            col_map[col] = 'gene_name'
        elif 'refgene_group' in lower:
            col_map[col] = 'gene_group'
        elif 'cpg_island' in lower or 'relation' in lower:
            col_map[col] = 'cpg_island_relation'

    manifest = manifest.rename(columns=col_map)
    return manifest


def normalize_chromosome(chrom):
    """Normalize chromosome name: '1' -> 'chr1', 'chrX' -> 'chrX', etc."""
    if chrom is None or pd.isna(chrom):
        return None
    chrom = str(chrom).strip()
    if not chrom.startswith('chr'):
        chrom = 'chr' + chrom
    return chrom


def get_chromosome_lengths(genome='hg38'):
    """Return chromosome lengths for common genome builds."""
    # hg38 chromosome sizes (main chromosomes)
    hg38 = {
        'chr1': 248956422, 'chr2': 242193529, 'chr3': 198295559,
        'chr4': 190214555, 'chr5': 181538259, 'chr6': 170805979,
        'chr7': 159345973, 'chr8': 145138636, 'chr9': 138394717,
        'chr10': 133797422, 'chr11': 135086622, 'chr12': 133275309,
        'chr13': 114364328, 'chr14': 107043718, 'chr15': 101991189,
        'chr16': 90338345, 'chr17': 83257441, 'chr18': 80373285,
        'chr19': 58617616, 'chr20': 64444167, 'chr21': 46709983,
        'chr22': 50818468, 'chrX': 156040895, 'chrY': 57227415,
    }
    hg19 = {
        'chr1': 249250621, 'chr2': 243199373, 'chr3': 198022430,
        'chr4': 191154276, 'chr5': 180915260, 'chr6': 171115067,
        'chr7': 159138663, 'chr8': 146364022, 'chr9': 141213431,
        'chr10': 135534747, 'chr11': 135006516, 'chr12': 133851895,
        'chr13': 115169878, 'chr14': 107349540, 'chr15': 102531392,
        'chr16': 90354753, 'chr17': 81195210, 'chr18': 78077248,
        'chr19': 59128983, 'chr20': 63025520, 'chr21': 48129895,
        'chr22': 51304566, 'chrX': 155270560, 'chrY': 59373566,
    }
    mm10 = {
        'chr1': 195471971, 'chr2': 182113224, 'chr3': 160039680,
        'chr4': 156508116, 'chr5': 151834684, 'chr6': 149736546,
        'chr7': 145441459, 'chr8': 129401213, 'chr9': 124595110,
        'chr10': 130694993, 'chr11': 122082543, 'chr12': 120129022,
        'chr13': 120421639, 'chr14': 124902244, 'chr15': 104043685,
        'chr16': 98207768, 'chr17': 94987271, 'chr18': 90702639,
        'chr19': 61431566, 'chrX': 171031299, 'chrY': 91744698,
    }
    genomes = {'hg38': hg38, 'hg19': hg19, 'mm10': mm10}
    return genomes.get(genome, hg38)
```

#### 1.3 CpG Site Filtering

```python
def filter_cpg_probes(df, manifest=None, filters=None):
    """Filter CpG probes based on various criteria.

    Args:
        df: Methylation matrix (probes x samples)
        manifest: Probe annotation DataFrame
        filters: dict with keys:
            - 'variance_threshold': float, minimum variance across samples
            - 'mean_beta_range': tuple (min, max), filter probes with extreme mean beta
            - 'missing_threshold': float (0-1), max fraction of NaN allowed per probe
            - 'chromosomes': list, keep only these chromosomes
            - 'exclude_sex_chr': bool, remove chrX and chrY
            - 'probe_type': 'cg' or 'ch', keep only one type
            - 'cpg_island': str ('Island', 'Shore', 'Shelf', 'OpenSea')
            - 'gene_group': str ('TSS200', 'TSS1500', 'Body', '1stExon', etc.)
            - 'top_n_variable': int, keep top N most variable probes
    """
    if filters is None:
        filters = {}

    probe_mask = pd.Series(True, index=df.index)

    # Probe type filter (cg vs ch)
    if 'probe_type' in filters:
        ptype = filters['probe_type']
        probe_mask &= df.index.str.startswith(ptype)

    # Missing data filter
    if 'missing_threshold' in filters:
        threshold = filters['missing_threshold']
        missing_frac = df.isna().mean(axis=1)
        probe_mask &= missing_frac <= threshold

    # Variance filter
    if 'variance_threshold' in filters:
        var_threshold = filters['variance_threshold']
        probe_var = df.var(axis=1, skipna=True)
        probe_mask &= probe_var >= var_threshold

    # Mean beta range filter
    if 'mean_beta_range' in filters:
        min_beta, max_beta = filters['mean_beta_range']
        probe_mean = df.mean(axis=1, skipna=True)
        probe_mask &= (probe_mean >= min_beta) & (probe_mean <= max_beta)

    # Top N most variable
    if 'top_n_variable' in filters:
        n = filters['top_n_variable']
        probe_var = df.var(axis=1, skipna=True)
        top_probes = probe_var.nlargest(n).index
        probe_mask &= df.index.isin(top_probes)

    # Manifest-based filters
    if manifest is not None and len(manifest) > 0:
        probe_id_col = 'probe_id' if 'probe_id' in manifest.columns else manifest.columns[0]
        manifest_indexed = manifest.set_index(probe_id_col) if probe_id_col in manifest.columns else manifest

        # Chromosome filter
        if 'chromosomes' in filters and 'chr' in manifest_indexed.columns:
            valid_chr = [normalize_chromosome(c) for c in filters['chromosomes']]
            chr_probes = manifest_indexed[
                manifest_indexed['chr'].apply(normalize_chromosome).isin(valid_chr)
            ].index
            probe_mask &= df.index.isin(chr_probes)

        # Exclude sex chromosomes
        if filters.get('exclude_sex_chr', False) and 'chr' in manifest_indexed.columns:
            sex_chr = ['chrX', 'chrY', 'X', 'Y']
            nonsex_probes = manifest_indexed[
                ~manifest_indexed['chr'].apply(normalize_chromosome).isin(['chrX', 'chrY'])
            ].index
            probe_mask &= df.index.isin(nonsex_probes)

        # CpG island relation filter
        if 'cpg_island' in filters and 'cpg_island_relation' in manifest_indexed.columns:
            relation = filters['cpg_island']
            island_probes = manifest_indexed[
                manifest_indexed['cpg_island_relation'].str.contains(relation, na=False, case=False)
            ].index
            probe_mask &= df.index.isin(island_probes)

        # Gene group filter (TSS200, Body, etc.)
        if 'gene_group' in filters and 'gene_group' in manifest_indexed.columns:
            group = filters['gene_group']
            group_probes = manifest_indexed[
                manifest_indexed['gene_group'].str.contains(group, na=False, case=False)
            ].index
            probe_mask &= df.index.isin(group_probes)

    filtered_df = df[probe_mask]
    return filtered_df
```

#### 1.4 Differential Methylation Analysis

```python
from scipy import stats
import statsmodels.stats.multitest as mt

def differential_methylation(beta_df, group1_samples, group2_samples,
                              test='ttest', correction='fdr_bh', alpha=0.05):
    """Perform differential methylation analysis between two groups.

    Args:
        beta_df: Beta-value matrix (probes x samples)
        group1_samples: list of sample IDs for group 1
        group2_samples: list of sample IDs for group 2
        test: 'ttest', 'wilcoxon', or 'ks' (Kolmogorov-Smirnov)
        correction: multiple testing correction method
        alpha: significance threshold

    Returns:
        DataFrame with columns: mean_g1, mean_g2, delta_beta, pvalue, padj
    """
    g1 = beta_df[group1_samples]
    g2 = beta_df[group2_samples]

    results = []
    for probe in beta_df.index:
        vals1 = g1.loc[probe].dropna().values
        vals2 = g2.loc[probe].dropna().values

        if len(vals1) < 2 or len(vals2) < 2:
            results.append({
                'probe': probe, 'mean_g1': np.nan, 'mean_g2': np.nan,
                'delta_beta': np.nan, 'pvalue': np.nan
            })
            continue

        mean1 = np.nanmean(vals1)
        mean2 = np.nanmean(vals2)
        delta = mean2 - mean1

        if test == 'ttest':
            stat, pval = stats.ttest_ind(vals1, vals2, equal_var=False)
        elif test == 'wilcoxon':
            stat, pval = stats.mannwhitneyu(vals1, vals2, alternative='two-sided')
        elif test == 'ks':
            stat, pval = stats.ks_2samp(vals1, vals2)
        else:
            stat, pval = stats.ttest_ind(vals1, vals2, equal_var=False)

        results.append({
            'probe': probe, 'mean_g1': mean1, 'mean_g2': mean2,
            'delta_beta': delta, 'pvalue': pval
        })

    result_df = pd.DataFrame(results).set_index('probe')

    # Multiple testing correction
    valid_pvals = result_df['pvalue'].dropna()
    if len(valid_pvals) > 0:
        reject, padj, _, _ = mt.multipletests(valid_pvals.values, alpha=alpha, method=correction)
        result_df.loc[valid_pvals.index, 'padj'] = padj
    else:
        result_df['padj'] = np.nan

    return result_df


def identify_dmps(dm_results, alpha=0.05, delta_beta_threshold=0.0):
    """Identify differentially methylated positions (DMPs).

    Args:
        dm_results: Output from differential_methylation()
        alpha: adjusted p-value threshold
        delta_beta_threshold: minimum absolute beta-value difference

    Returns:
        DataFrame of significant DMPs
    """
    dmps = dm_results[
        (dm_results['padj'] < alpha) &
        (dm_results['delta_beta'].abs() >= delta_beta_threshold)
    ].copy()
    dmps['direction'] = np.where(dmps['delta_beta'] > 0, 'hyper', 'hypo')
    return dmps.sort_values('padj')
```

#### 1.5 Age-Related CpG Analysis

```python
def identify_age_related_cpgs(beta_df, ages, method='correlation',
                                correction='fdr_bh', alpha=0.05):
    """Identify CpG sites associated with age.

    Args:
        beta_df: Beta-value matrix (probes x samples)
        ages: Series or array of ages corresponding to samples
        method: 'correlation' (Pearson/Spearman) or 'regression'
        correction: multiple testing method
        alpha: significance threshold

    Returns:
        DataFrame with correlation, p-value, adjusted p-value
    """
    results = []
    for probe in beta_df.index:
        vals = beta_df.loc[probe].values
        mask = ~np.isnan(vals) & ~np.isnan(ages.values if hasattr(ages, 'values') else ages)
        if sum(mask) < 5:
            results.append({'probe': probe, 'correlation': np.nan,
                          'pvalue': np.nan})
            continue

        if method == 'correlation':
            corr, pval = stats.pearsonr(ages[mask] if hasattr(ages, '__getitem__') else
                                        np.array(ages)[mask], vals[mask])
        elif method == 'spearman':
            corr, pval = stats.spearmanr(ages[mask] if hasattr(ages, '__getitem__') else
                                          np.array(ages)[mask], vals[mask])
        else:
            corr, pval = stats.pearsonr(ages[mask] if hasattr(ages, '__getitem__') else
                                        np.array(ages)[mask], vals[mask])

        results.append({'probe': probe, 'correlation': corr, 'pvalue': pval})

    result_df = pd.DataFrame(results).set_index('probe')

    # Multiple testing correction
    valid_pvals = result_df['pvalue'].dropna()
    if len(valid_pvals) > 0:
        reject, padj, _, _ = mt.multipletests(valid_pvals.values, alpha=alpha, method=correction)
        result_df.loc[valid_pvals.index, 'padj'] = padj
    else:
        result_df['padj'] = np.nan

    return result_df
```

#### 1.6 Chromosome-Level Methylation Statistics

```python
def chromosome_cpg_density(cpg_probes, manifest, genome='hg38'):
    """Calculate CpG density per chromosome.

    Args:
        cpg_probes: list/Index of CpG probe IDs
        manifest: probe annotation with chr and position columns
        genome: genome build for chromosome lengths

    Returns:
        DataFrame with chr, n_cpgs, chr_length, density (CpGs per bp)
    """
    chr_lengths = get_chromosome_lengths(genome)

    # Map probes to chromosomes
    probe_id_col = 'probe_id' if 'probe_id' in manifest.columns else manifest.columns[0]
    if probe_id_col in manifest.columns:
        probe_chr = manifest.set_index(probe_id_col)
    else:
        probe_chr = manifest

    # Get chromosome for each probe
    if 'chr' in probe_chr.columns:
        chr_col = 'chr'
    elif 'CHR' in probe_chr.columns:
        chr_col = 'CHR'
    else:
        raise ValueError("No chromosome column found in manifest")

    # Count probes per chromosome
    probe_chrs = probe_chr.loc[probe_chr.index.isin(cpg_probes), chr_col]
    probe_chrs = probe_chrs.apply(normalize_chromosome)
    chr_counts = probe_chrs.value_counts()

    results = []
    for chrom, count in chr_counts.items():
        if chrom in chr_lengths:
            length = chr_lengths[chrom]
            density = count / length
            results.append({
                'chr': chrom,
                'n_cpgs': count,
                'chr_length': length,
                'density_per_bp': density,
                'density_per_mb': density * 1e6,
            })

    return pd.DataFrame(results).sort_values('chr',
        key=lambda x: x.str.replace('chr', '').replace({'X': '23', 'Y': '24'}).astype(int))


def genome_wide_average_density(density_df):
    """Calculate genome-wide average CpG density across all chromosomes.

    Args:
        density_df: Output from chromosome_cpg_density()

    Returns:
        float: genome-wide average density (CpGs per bp)
    """
    total_cpgs = density_df['n_cpgs'].sum()
    total_length = density_df['chr_length'].sum()
    return total_cpgs / total_length


def chromosome_density_ratio(density_df, chr1, chr2):
    """Calculate density ratio between two chromosomes.

    Args:
        density_df: Output from chromosome_cpg_density()
        chr1, chr2: chromosome names (e.g., 'chr1', 'chr2')

    Returns:
        float: density ratio (chr1 / chr2)
    """
    chr1 = normalize_chromosome(chr1)
    chr2 = normalize_chromosome(chr2)
    d1 = density_df[density_df['chr'] == chr1]['density_per_bp'].values[0]
    d2 = density_df[density_df['chr'] == chr2]['density_per_bp'].values[0]
    return d1 / d2
```

---

### Phase 2: ChIP-seq Peak Analysis

#### 2.1 Load BED/Peak Files

```python
def load_bed_file(file_path, format='bed'):
    """Load BED format file (standard BED, narrowPeak, broadPeak).

    Standard BED: chrom, start, end, name, score, strand
    narrowPeak: + signalValue, pValue, qValue, peak
    broadPeak: + signalValue, pValue, qValue
    """
    if format == 'narrowPeak' or file_path.endswith('.narrowPeak'):
        names = ['chrom', 'start', 'end', 'name', 'score', 'strand',
                 'signalValue', 'pValue', 'qValue', 'peak']
    elif format == 'broadPeak' or file_path.endswith('.broadPeak'):
        names = ['chrom', 'start', 'end', 'name', 'score', 'strand',
                 'signalValue', 'pValue', 'qValue']
    else:
        # Standard BED - detect number of columns
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            while first_line.startswith('#') or first_line.startswith('track') or first_line.startswith('browser'):
                first_line = f.readline().strip()
            n_cols = len(first_line.split('\t'))

        bed_col_names = ['chrom', 'start', 'end', 'name', 'score', 'strand',
                         'thickStart', 'thickEnd', 'itemRgb', 'blockCount',
                         'blockSizes', 'blockStarts']
        names = bed_col_names[:n_cols]

    df = pd.read_csv(file_path, sep='\t', header=None, names=names,
                      comment='#', low_memory=False)

    # Skip track/browser lines
    df = df[~df['chrom'].astype(str).str.startswith(('track', 'browser'))]

    # Normalize chromosomes
    df['chrom'] = df['chrom'].apply(normalize_chromosome)

    # Ensure numeric types
    df['start'] = pd.to_numeric(df['start'], errors='coerce')
    df['end'] = pd.to_numeric(df['end'], errors='coerce')

    return df


def peak_statistics(peaks_df):
    """Calculate basic peak statistics.

    Args:
        peaks_df: BED DataFrame from load_bed_file()

    Returns:
        dict with peak statistics
    """
    peaks_df = peaks_df.copy()
    peaks_df['length'] = peaks_df['end'] - peaks_df['start']

    stats_dict = {
        'total_peaks': len(peaks_df),
        'mean_peak_length': peaks_df['length'].mean(),
        'median_peak_length': peaks_df['length'].median(),
        'total_coverage_bp': peaks_df['length'].sum(),
        'peaks_per_chromosome': peaks_df['chrom'].value_counts().to_dict(),
    }

    if 'signalValue' in peaks_df.columns:
        stats_dict['mean_signal'] = peaks_df['signalValue'].mean()
        stats_dict['median_signal'] = peaks_df['signalValue'].median()

    if 'qValue' in peaks_df.columns:
        stats_dict['mean_qvalue'] = peaks_df['qValue'].mean()

    return stats_dict
```

#### 2.2 Peak Annotation

```python
def annotate_peaks_to_genes(peaks_df, gene_annotation=None,
                             tss_upstream=2000, tss_downstream=500):
    """Annotate peaks to nearest gene / genomic feature.

    Args:
        peaks_df: BED DataFrame
        gene_annotation: DataFrame with gene coordinates (chr, start, end, gene_name, strand)
        tss_upstream: bp upstream of TSS to define promoter
        tss_downstream: bp downstream of TSS to define promoter

    Returns:
        DataFrame with peak annotations
    """
    if gene_annotation is None:
        return peaks_df  # No annotation available

    annotated = peaks_df.copy()
    annotations = []

    for _, peak in peaks_df.iterrows():
        peak_chr = peak['chrom']
        peak_mid = (peak['start'] + peak['end']) // 2

        # Filter genes on same chromosome
        chr_genes = gene_annotation[gene_annotation['chr'] == peak_chr]

        if len(chr_genes) == 0:
            annotations.append({
                'nearest_gene': 'intergenic',
                'distance_to_tss': np.nan,
                'feature': 'intergenic'
            })
            continue

        # Calculate distance to TSS
        tss_positions = chr_genes.apply(
            lambda g: g['start'] if g.get('strand', '+') == '+' else g['end'],
            axis=1
        )
        distances = (peak_mid - tss_positions).abs()
        nearest_idx = distances.idxmin()
        nearest_gene = chr_genes.loc[nearest_idx]
        distance = distances.loc[nearest_idx]
        tss = tss_positions.loc[nearest_idx]

        # Classify feature type
        if abs(peak_mid - tss) <= tss_upstream:
            feature = 'promoter'
        elif peak['start'] >= nearest_gene['start'] and peak['end'] <= nearest_gene['end']:
            feature = 'gene_body'
        elif abs(peak_mid - tss) <= 10000:
            feature = 'proximal'
        else:
            feature = 'distal'

        annotations.append({
            'nearest_gene': nearest_gene.get('gene_name', nearest_gene.name),
            'distance_to_tss': int(distance),
            'feature': feature
        })

    ann_df = pd.DataFrame(annotations, index=peaks_df.index)
    return pd.concat([peaks_df, ann_df], axis=1)


def classify_peak_regions(annotated_peaks):
    """Classify peaks into genomic regions.

    Returns:
        dict with counts per region type
    """
    if 'feature' not in annotated_peaks.columns:
        return {'unknown': len(annotated_peaks)}

    return annotated_peaks['feature'].value_counts().to_dict()
```

#### 2.3 Peak Overlap Analysis

```python
def find_overlaps(peaks_a, peaks_b, min_overlap=1):
    """Find overlapping peaks between two BED DataFrames.

    Uses a simple interval overlap approach (pure Python, no pybedtools).

    Args:
        peaks_a: BED DataFrame (query)
        peaks_b: BED DataFrame (subject)
        min_overlap: minimum overlap in bp

    Returns:
        DataFrame of overlapping pairs
    """
    overlaps = []

    # Group by chromosome for efficiency
    for chrom in peaks_a['chrom'].unique():
        a_chr = peaks_a[peaks_a['chrom'] == chrom].sort_values('start')
        b_chr = peaks_b[peaks_b['chrom'] == chrom].sort_values('start')

        if len(b_chr) == 0:
            continue

        for _, a_peak in a_chr.iterrows():
            # Binary search for potential overlaps
            for _, b_peak in b_chr.iterrows():
                if b_peak['start'] >= a_peak['end']:
                    break
                if b_peak['end'] <= a_peak['start']:
                    continue

                # Calculate overlap
                overlap_start = max(a_peak['start'], b_peak['start'])
                overlap_end = min(a_peak['end'], b_peak['end'])
                overlap_bp = overlap_end - overlap_start

                if overlap_bp >= min_overlap:
                    overlaps.append({
                        'a_chrom': chrom,
                        'a_start': a_peak['start'],
                        'a_end': a_peak['end'],
                        'b_start': b_peak['start'],
                        'b_end': b_peak['end'],
                        'overlap_bp': overlap_bp,
                    })

    return pd.DataFrame(overlaps) if overlaps else pd.DataFrame()


def jaccard_similarity(peaks_a, peaks_b, genome='hg38'):
    """Calculate Jaccard similarity between two peak sets.

    Jaccard = intersection / union of genomic coverage.
    """
    chr_lengths = get_chromosome_lengths(genome)
    total_genome = sum(chr_lengths.values())

    # Simple approximation: total bp covered
    coverage_a = (peaks_a['end'] - peaks_a['start']).sum()
    coverage_b = (peaks_b['end'] - peaks_b['start']).sum()

    overlaps = find_overlaps(peaks_a, peaks_b)
    if len(overlaps) == 0:
        return 0.0

    intersection = overlaps['overlap_bp'].sum()
    union = coverage_a + coverage_b - intersection

    return intersection / union if union > 0 else 0.0
```

---

### Phase 3: ATAC-seq Analysis

#### 3.1 ATAC-seq Peak Processing

```python
def load_atac_peaks(file_path):
    """Load ATAC-seq peak file (typically narrowPeak format)."""
    return load_bed_file(file_path, format='narrowPeak')


def atac_peak_statistics(peaks_df):
    """ATAC-seq specific statistics.

    ATAC-seq peaks represent open chromatin regions.
    """
    basic_stats = peak_statistics(peaks_df)

    # ATAC-specific: nucleosome-free region (NFR) analysis
    # NFR peaks typically < 150bp
    peaks_df = peaks_df.copy()
    peaks_df['length'] = peaks_df['end'] - peaks_df['start']
    nfr_peaks = peaks_df[peaks_df['length'] < 150]
    nucleosome_peaks = peaks_df[peaks_df['length'] >= 150]

    basic_stats['nfr_peaks'] = len(nfr_peaks)
    basic_stats['nucleosome_peaks'] = len(nucleosome_peaks)
    basic_stats['nfr_fraction'] = len(nfr_peaks) / len(peaks_df) if len(peaks_df) > 0 else 0

    return basic_stats


def chromatin_accessibility_by_region(peaks_df, gene_annotation=None):
    """Calculate chromatin accessibility distribution across genomic regions."""
    annotated = annotate_peaks_to_genes(peaks_df, gene_annotation)
    regions = classify_peak_regions(annotated)

    total = sum(regions.values())
    region_fractions = {k: v / total for k, v in regions.items()}

    return {
        'counts': regions,
        'fractions': region_fractions,
        'total_peaks': total,
    }
```

---

### Phase 4: Multi-Omics Integration

#### 4.1 Expression-Methylation Correlation

```python
def correlate_methylation_expression(beta_df, expression_df, probe_gene_map,
                                       method='pearson', correction='fdr_bh'):
    """Correlate methylation levels with gene expression.

    Args:
        beta_df: Methylation matrix (probes x samples)
        expression_df: Expression matrix (genes x samples)
        probe_gene_map: dict or Series mapping probe IDs to gene symbols
        method: 'pearson' or 'spearman'
        correction: multiple testing correction

    Returns:
        DataFrame with correlation, p-value per probe-gene pair
    """
    # Align samples
    common_samples = list(set(beta_df.columns) & set(expression_df.columns))
    if len(common_samples) < 5:
        raise ValueError(f"Not enough common samples: {len(common_samples)}")

    beta_aligned = beta_df[common_samples]
    expr_aligned = expression_df[common_samples]

    results = []
    for probe, gene in probe_gene_map.items():
        if probe not in beta_aligned.index or gene not in expr_aligned.index:
            continue

        meth_vals = beta_aligned.loc[probe].values
        expr_vals = expr_aligned.loc[gene].values

        mask = ~np.isnan(meth_vals) & ~np.isnan(expr_vals)
        if sum(mask) < 5:
            continue

        if method == 'pearson':
            corr, pval = stats.pearsonr(meth_vals[mask], expr_vals[mask])
        else:
            corr, pval = stats.spearmanr(meth_vals[mask], expr_vals[mask])

        results.append({
            'probe': probe,
            'gene': gene,
            'correlation': corr,
            'pvalue': pval,
            'n_samples': sum(mask),
        })

    result_df = pd.DataFrame(results)

    if len(result_df) > 0:
        valid_pvals = result_df['pvalue'].dropna()
        if len(valid_pvals) > 0:
            reject, padj, _, _ = mt.multipletests(valid_pvals.values, method=correction)
            result_df.loc[valid_pvals.index, 'padj'] = padj

    return result_df
```

#### 4.2 ChIP-seq + Expression Integration

```python
def integrate_chipseq_expression(peaks_df, expression_df, gene_annotation,
                                   tss_window=5000):
    """Integrate ChIP-seq peaks with gene expression.

    Args:
        peaks_df: ChIP-seq peaks (BED)
        expression_df: Gene expression (genes x samples)
        gene_annotation: Gene coordinates
        tss_window: window around TSS for promoter peaks

    Returns:
        DataFrame with genes having promoter peaks and their expression
    """
    annotated = annotate_peaks_to_genes(peaks_df, gene_annotation,
                                         tss_upstream=tss_window)
    promoter_peaks = annotated[annotated['feature'] == 'promoter']

    # Get genes with promoter peaks
    peak_genes = promoter_peaks['nearest_gene'].unique()

    # Get expression for these genes
    common_genes = [g for g in peak_genes if g in expression_df.index]

    result = pd.DataFrame({
        'gene': common_genes,
        'has_promoter_peak': True,
        'mean_expression': [expression_df.loc[g].mean() for g in common_genes],
    })

    return result
```

---

### Phase 5: Clinical Data Integration

#### 5.1 Missing Data Analysis

```python
def missing_data_analysis(clinical_df=None, expression_df=None,
                           methylation_df=None, sample_id_col=None):
    """Analyze missing data across multiple omics modalities.

    For BixBench questions like:
    "How many patients have no missing data for vital status, gene expression, and methylation?"

    Args:
        clinical_df: Clinical data (patients x variables)
        expression_df: Expression matrix (genes x samples)
        methylation_df: Methylation matrix (probes x samples)
        sample_id_col: Column name for sample/patient IDs in clinical data

    Returns:
        dict with completeness statistics
    """
    results = {}

    # Get sample sets from each modality
    clinical_samples = set()
    if clinical_df is not None:
        if sample_id_col and sample_id_col in clinical_df.columns:
            clinical_samples = set(clinical_df[sample_id_col].dropna())
        else:
            clinical_samples = set(clinical_df.index)
        results['clinical_samples'] = len(clinical_samples)

    expression_samples = set()
    if expression_df is not None:
        expression_samples = set(expression_df.columns)
        results['expression_samples'] = len(expression_samples)

    methylation_samples = set()
    if methylation_df is not None:
        methylation_samples = set(methylation_df.columns)
        results['methylation_samples'] = len(methylation_samples)

    # Intersection: samples with ALL data types
    all_sets = []
    if clinical_samples:
        all_sets.append(clinical_samples)
    if expression_samples:
        all_sets.append(expression_samples)
    if methylation_samples:
        all_sets.append(methylation_samples)

    if len(all_sets) > 0:
        complete_samples = set.intersection(*all_sets)
        results['complete_samples'] = len(complete_samples)
        results['complete_sample_ids'] = sorted(complete_samples)
    else:
        results['complete_samples'] = 0

    # Additional: check for missing values within clinical data
    if clinical_df is not None:
        for col in clinical_df.columns:
            n_missing = clinical_df[col].isna().sum()
            n_total = len(clinical_df)
            results[f'clinical_{col}_missing'] = n_missing
            results[f'clinical_{col}_complete'] = n_total - n_missing

    return results


def find_complete_cases(data_frames, variables=None):
    """Find samples that are complete across specified data frames and variables.

    Args:
        data_frames: dict of {name: DataFrame} where columns are samples
        variables: dict of {df_name: [variable_names]} for clinical variables to check

    Returns:
        set of sample IDs with complete data
    """
    sample_sets = []
    for name, df in data_frames.items():
        if df is not None:
            if variables and name in variables:
                # Check specific variables for completeness
                for var in variables[name]:
                    if var in df.columns:
                        complete = set(df[df[var].notna()].index)
                        sample_sets.append(complete)
                    elif var in df.index:
                        complete = set(df.columns[df.loc[var].notna()])
                        sample_sets.append(complete)
            else:
                # Just check sample presence
                sample_sets.append(set(df.columns))

    if not sample_sets:
        return set()

    return set.intersection(*sample_sets)
```

---

### Phase 6: ToolUniverse Annotation Integration

Use ToolUniverse tools for biological annotation of epigenomic findings.

#### 6.1 Gene-Level Annotation

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Annotate differentially methylated genes
def annotate_genes_with_tooluniverse(gene_list, tu):
    """Annotate a list of genes using ToolUniverse tools.

    Uses:
    - Ensembl for gene coordinates and cross-references
    - SCREEN for regulatory elements near gene
    - ChIPAtlas for ChIP-seq experiments
    """
    annotations = {}
    for gene in gene_list[:20]:  # Limit for API rate
        annotation = {'gene': gene}

        # Ensembl lookup
        try:
            ens = tu.tools.ensembl_lookup_gene(id=gene, species='homo_sapiens')
            if isinstance(ens, dict):
                data = ens.get('data', ens)
                annotation['ensembl_id'] = data.get('id', 'N/A')
                annotation['chr'] = data.get('seq_region_name', 'N/A')
                annotation['start'] = data.get('start', 'N/A')
                annotation['end'] = data.get('end', 'N/A')
                annotation['biotype'] = data.get('biotype', 'N/A')
        except Exception:
            pass

        # SCREEN regulatory elements
        try:
            screen = tu.tools.SCREEN_get_regulatory_elements(
                gene_name=gene, element_type="enhancer", limit=5
            )
            if screen is not None:
                annotation['screen_enhancers'] = 'available'
        except Exception:
            pass

        annotations[gene] = annotation

    return pd.DataFrame.from_dict(annotations, orient='index')
```

#### 6.2 ChIPAtlas Integration

```python
def query_chipatlas_experiments(antigen, genome='hg38', cell_type=None, tu=None):
    """Query ChIPAtlas for available ChIP-seq experiments.

    Args:
        antigen: TF or histone mark name (e.g., 'H3K27ac', 'CTCF')
        genome: genome build
        cell_type: optional cell type filter

    Returns:
        ChIPAtlas experiment metadata
    """
    if tu is None:
        from tooluniverse import ToolUniverse
        tu = ToolUniverse()
        tu.load_tools()

    params = {
        'operation': 'get_experiment_list',
        'genome': genome,
        'antigen': antigen,
        'limit': 50,
    }
    if cell_type:
        params['cell_type'] = cell_type

    return tu.tools.ChIPAtlas_get_experiments(**params)
```

#### 6.3 Ensembl Regulatory Feature Annotation

```python
def annotate_regions_with_ensembl(regions, species='human', tu=None):
    """Annotate genomic regions with Ensembl regulatory features.

    Args:
        regions: list of (chr, start, end) tuples
        species: Ensembl species name

    Returns:
        dict of region -> regulatory features
    """
    if tu is None:
        from tooluniverse import ToolUniverse
        tu = ToolUniverse()
        tu.load_tools()

    annotations = {}
    for chrom, start, end in regions[:10]:  # Limit for API rate
        # Ensembl uses chromosome without 'chr' prefix
        ens_chrom = chrom.replace('chr', '') if chrom.startswith('chr') else chrom
        region_str = f"{ens_chrom}:{start}-{end}"

        try:
            result = tu.tools.ensembl_get_regulatory_features(
                region=region_str, feature="regulatory", species=species
            )
            annotations[(chrom, start, end)] = result
        except Exception as e:
            annotations[(chrom, start, end)] = {'error': str(e)}

    return annotations
```

---

### Phase 7: Genome-Wide Statistics

#### 7.1 Comprehensive Genome Statistics

```python
def genome_wide_methylation_stats(beta_df, manifest=None, genome='hg38'):
    """Calculate comprehensive genome-wide methylation statistics.

    Args:
        beta_df: Methylation matrix (probes x samples)
        manifest: Probe annotation
        genome: genome build

    Returns:
        dict with genome-wide statistics
    """
    stats_result = {
        'total_probes': len(beta_df),
        'total_samples': beta_df.shape[1],
        'global_mean_beta': float(beta_df.mean().mean()),
        'global_median_beta': float(beta_df.median().median()),
        'global_std_beta': float(beta_df.values[~np.isnan(beta_df.values)].std()),
        'missing_fraction': float(beta_df.isna().mean().mean()),
    }

    # Per-sample statistics
    stats_result['sample_means'] = beta_df.mean(axis=0).describe().to_dict()

    # Per-probe statistics
    probe_var = beta_df.var(axis=1, skipna=True)
    stats_result['probe_variance'] = {
        'mean': float(probe_var.mean()),
        'median': float(probe_var.median()),
        'max': float(probe_var.max()),
    }
    stats_result['high_variance_probes'] = int((probe_var > 0.01).sum())

    # Chromosome-level stats (if manifest available)
    if manifest is not None:
        density_df = chromosome_cpg_density(beta_df.index.tolist(), manifest, genome)
        stats_result['chromosome_density'] = density_df.to_dict('records')
        stats_result['genome_wide_density'] = genome_wide_average_density(density_df)

    return stats_result


def summarize_differential_methylation(dm_results, alpha=0.05):
    """Summarize differential methylation results.

    Args:
        dm_results: Output from differential_methylation()

    Returns:
        dict with summary statistics
    """
    sig = dm_results[dm_results['padj'] < alpha]
    hyper = sig[sig['delta_beta'] > 0]
    hypo = sig[sig['delta_beta'] < 0]

    return {
        'total_tested': len(dm_results),
        'total_significant': len(sig),
        'hypermethylated': len(hyper),
        'hypomethylated': len(hypo),
        'fraction_significant': len(sig) / len(dm_results) if len(dm_results) > 0 else 0,
        'mean_delta_beta_sig': float(sig['delta_beta'].mean()) if len(sig) > 0 else 0,
        'max_abs_delta_beta': float(sig['delta_beta'].abs().max()) if len(sig) > 0 else 0,
    }
```

---

## ToolUniverse Tool Parameter Reference

### Regulatory Annotation Tools

| Tool | Parameters | Returns |
|------|-----------|---------|
| `ensembl_lookup_gene` | `id: str`, `species: str` (REQUIRED) | `{status, data: {id, display_name, seq_region_name, start, end, strand, biotype}, url}` |
| `ensembl_get_regulatory_features` | `region: str` (no "chr"), `feature: str`, `species: str` | `{status, data: [...features...]}` |
| `ensembl_get_overlap_features` | `region: str`, `feature: str`, `species: str` | Gene/transcript overlap data |
| `SCREEN_get_regulatory_elements` | `gene_name: str`, `element_type: str`, `limit: int` | cCREs (enhancers, promoters, insulators) |
| `ReMap_get_transcription_factor_binding` | `gene_name: str`, `cell_type: str`, `limit: int` | TF binding sites |
| `RegulomeDB_query_variant` | `rsid: str` | `{status, data, url}` regulatory score |
| `jaspar_search_matrices` | `search: str`, `collection: str`, `species: str` | `{count, results: [...matrices...]}` |
| `ENCODE_search_experiments` | `assay_title: str`, `target: str`, `organism: str`, `limit: int` | Experiment metadata |
| `ChIPAtlas_get_experiments` | `operation: str` (REQUIRED: "get_experiment_list"), `genome: str`, `antigen: str`, `cell_type: str`, `limit: int` | Experiment list |
| `ChIPAtlas_search_datasets` | `operation` REQUIRED, `antigenList/celltypeList` | Dataset search results |
| `ChIPAtlas_enrichment_analysis` | Various input types (BED regions, motifs, genes) | Enrichment results |
| `ChIPAtlas_get_peak_data` | `operation` REQUIRED | Peak data download URLs |
| `FourDN_search_data` | `operation: str` (REQUIRED: "search_data"), `assay_title: str`, `limit: int` | Chromatin conformation data |

### Gene Annotation Tools

| Tool | Parameters | Returns |
|------|-----------|---------|
| `MyGene_query_genes` | `query: str` | `{hits: [{_id, symbol, ensembl, ...}]}` |
| `MyGene_batch_query` | `gene_ids: list[str]`, `fields: str` | `{results: [{query, symbol, ...}]}` |
| `HGNC_get_gene_info` | `symbol: str` | Gene symbol, aliases, IDs |
| `GO_get_annotations_for_gene` | `gene_id: str` | GO annotations |

### CRITICAL Tool Notes

- **ensembl_lookup_gene**: REQUIRES `species='homo_sapiens'` parameter
- **ensembl_get_regulatory_features**: Region format is "17:start-end" (NO "chr" prefix)
- **ChIPAtlas tools**: ALL require `operation` parameter (SOAP-style)
- **FourDN tools**: ALL require `operation` parameter (SOAP-style)
- **SCREEN**: Returns JSON-LD format with `@context, @graph` keys

---

## Response Format Notes

- **Methylation data**: Typically stored as probes (rows) x samples (columns), beta values 0-1
- **BED files**: Tab-separated, 0-based half-open coordinates
- **narrowPeak**: 10-column BED extension with signalValue, pValue, qValue, peak
- **Illumina manifests**: Contains probe ID, chromosome, position, gene annotation
- **Clinical data**: Patient/sample-centric with clinical variables as columns

---

## Fallback Strategies

| Scenario | Primary | Fallback |
|----------|---------|----------|
| No manifest file | Load from data dir | Build minimal from Ensembl lookup |
| No pybedtools | Pure Python overlap | pandas-based interval intersection |
| No pyBigWig | Skip BigWig analysis | Use pre-computed summary tables |
| Missing clinical data | Report missing | Use available samples only |
| Low sample count | Parametric test | Use non-parametric (Wilcoxon) |
| Large dataset (>500K probes) | Full analysis | Sample or chunk-based processing |

---

## Common Use Patterns

### Pattern 1: Methylation Array Analysis
```
Input: Beta-value matrix + manifest + clinical data
Question: "How many CpGs are differentially methylated?"

Flow:
1. Load beta matrix, manifest, clinical data
2. Filter CpG probes (cg only, remove sex chr, variance filter)
3. Define groups from clinical data
4. Run differential_methylation()
5. Apply thresholds (padj < 0.05, |delta_beta| > 0.2)
6. Report count and direction (hyper/hypo)
```

### Pattern 2: Age-Related CpG Density
```
Input: Beta-value matrix + manifest + ages
Question: "What is the density ratio of age-related CpGs between chr1 and chr2?"

Flow:
1. Load beta matrix and ages from clinical data
2. Run identify_age_related_cpgs()
3. Filter significant age-related CpGs
4. Map to chromosomes using manifest
5. Calculate chromosome_cpg_density()
6. Compute ratio between specified chromosomes
```

### Pattern 3: Multi-Omics Missing Data
```
Input: Clinical + expression + methylation data files
Question: "How many patients have complete data for all modalities?"

Flow:
1. Load all data files
2. Extract sample IDs from each
3. Find intersection (common samples)
4. Check for NaN/missing within clinical variables
5. Report complete cases count
```

### Pattern 4: ChIP-seq Peak Annotation
```
Input: BED/narrowPeak file
Question: "What fraction of peaks are in promoter regions?"

Flow:
1. Load BED file with load_bed_file()
2. Load or fetch gene annotation (Ensembl)
3. Run annotate_peaks_to_genes()
4. Classify regions with classify_peak_regions()
5. Calculate fraction in promoters
```

### Pattern 5: Methylation-Expression Integration
```
Input: Beta matrix + expression matrix + probe-gene mapping
Question: "What is the correlation between methylation and expression?"

Flow:
1. Load both matrices
2. Build probe-gene map from manifest
3. Align samples across datasets
4. Run correlate_methylation_expression()
5. Report significant anti-correlations
```

---

## Edge Cases

### Missing Probe Annotation
When no manifest/annotation file is available:
- Extract chromosome from probe ID naming patterns if possible
- Use ToolUniverse Ensembl tools to build minimal annotation
- Report limitation: "chromosome mapping unavailable for X probes"

### Mixed Genome Builds
When data uses different builds:
- Detect build from context (data README, file names, known coordinates)
- Use appropriate chromosome lengths for density calculations
- Do NOT mix hg19 and hg38 coordinates

### Very Large Datasets
For datasets with >500K CpG sites:
- Use chunked processing for differential methylation
- Pre-filter by variance before statistical testing
- Use vectorized operations (avoid row-by-row loops where possible)

### Sample ID Mismatches
Clinical and molecular data may use different ID formats:
- TCGA: barcode (TCGA-XX-XXXX-01A) vs patient ID (TCGA-XX-XXXX)
- Try truncating or matching partial IDs
- Report number of matched/unmatched samples

---

## Limitations

- **No native pybedtools**: Uses pure Python interval operations (slower for very large BED files)
- **No native pyBigWig**: Cannot read BigWig files directly without package
- **No R bridge**: Does not use methylKit, ChIPseeker, or DiffBind
- **Illumina-centric**: Methylation functions designed for 450K/EPIC arrays
- **Statistical simplicity**: Uses t-test/Wilcoxon for differential methylation (not limma/bumphunter)
- **No peak calling**: Assumes peaks are pre-called; does not run MACS2 or similar
- **API rate limits**: ToolUniverse annotation limited to ~20 genes per batch

---

## Summary

**Genomics & Epigenomics Data Processing Skill** provides:

1. **Methylation analysis** - Beta-value processing, CpG filtering, differential methylation, age-related CpGs, chromosome density
2. **ChIP-seq analysis** - Peak loading (BED/narrowPeak), peak annotation, overlap analysis, statistics
3. **ATAC-seq analysis** - Chromatin accessibility peaks, NFR detection, region classification
4. **Multi-omics integration** - Methylation-expression correlation, ChIP-seq + expression
5. **Clinical integration** - Missing data analysis across modalities, complete case identification
6. **Genome-wide statistics** - Chromosome-level density, genome-wide averages, density ratios
7. **ToolUniverse annotation** - Ensembl, SCREEN, ChIPAtlas, JASPAR, ENCODE for biological context

**Core packages**: pandas, numpy, scipy, statsmodels, pysam, gseapy
**ToolUniverse tools**: 25+ tools across Ensembl, SCREEN, ENCODE, ChIPAtlas, JASPAR, ReMap, RegulomeDB, 4DN
**Best for**: BixBench-style quantitative questions about methylation data, ChIP-seq peaks, chromatin accessibility, and multi-omics integration
