# tooluniverse-immune-repertoire-analysis

> Comprehensive immune repertoire analysis for T-cell and B-cell receptor sequencing data. Analyze TCR/BCR repertoires to assess clonality, diversity, V(D)J gene usage, CDR3 characteristics, convergence, and predict epitope specificity. Integrate with single-cell data for clonotype-phenotype associations. Use for adaptive immune response profiling, cancer immunotherapy research, vaccine response assessment, autoimmune disease studies, or repertoire diversity analysis in immunology research.

# ToolUniverse Immune Repertoire Analysis

Comprehensive skill for analyzing T-cell receptor (TCR) and B-cell receptor (BCR) repertoire sequencing data to characterize adaptive immune responses, clonal expansion, and antigen specificity.

## Overview

Adaptive immune receptor repertoire sequencing (AIRR-seq) enables comprehensive profiling of T-cell and B-cell populations through high-throughput sequencing of TCR and BCR variable regions. This skill provides an 8-phase workflow for:
- Clonotype identification and tracking
- Diversity and clonality assessment
- V(D)J gene usage analysis
- CDR3 sequence characterization
- Clonal expansion and convergence detection
- Epitope specificity prediction
- Integration with single-cell phenotyping
- Longitudinal repertoire tracking

## Core Workflow

### Phase 1: Data Import & Clonotype Definition

**Load AIRR-seq Data**

```python
import pandas as pd
import numpy as np
from collections import Counter

def load_airr_data(file_path, format='mixcr'):
    """
    Load immune repertoire data from common formats.

    Supported formats:
    - 'mixcr': MiXCR output
    - 'immunoseq': Adaptive Biotechnologies ImmunoSEQ
    - 'airr': AIRR Community Standard
    - '10x': 10x Genomics VDJ output
    """
    if format == 'mixcr':
        # MiXCR clonotypes.txt format
        df = pd.read_csv(file_path, sep='\t')
        
        # Standardize column names
        clonotype_df = pd.DataFrame({
            'cloneId': df.get('cloneId', range(len(df))),
            'count': df.get('cloneCount', df.get('count', 0)),
            'frequency': df.get('cloneFraction', df.get('frequency', 0)),
            'cdr3aa': df.get('aaSeqCDR3', df.get('cdr3', '')),
            'cdr3nt': df.get('nSeqCDR3', ''),
            'v_gene': df.get('allVHitsWithScore', df.get('v_call', '')),
            'j_gene': df.get('allJHitsWithScore', df.get('j_call', '')),
            'chain': df.get('chain', 'TRB')  # Default to TRB
        })

    elif format == '10x':
        # 10x Genomics filtered_contig_annotations.csv
        df = pd.read_csv(file_path)
        
        # Group by barcode to get clonotypes
        clonotype_df = df.groupby('barcode').agg({
            'cdr3': lambda x: ','.join(x.dropna()),
            'cdr3_nt': lambda x: ','.join(x.dropna()),
            'v_gene': lambda x: ','.join(x.dropna()),
            'j_gene': lambda x: ','.join(x.dropna()),
            'chain': lambda x: ','.join(x.dropna()),
            'umis': 'sum'
        }).reset_index()
        
        clonotype_df = clonotype_df.rename(columns={
            'barcode': 'cloneId',
            'cdr3': 'cdr3aa',
            'cdr3_nt': 'cdr3nt',
            'umis': 'count'
        })
        
        clonotype_df['frequency'] = clonotype_df['count'] / clonotype_df['count'].sum()

    elif format == 'airr':
        # AIRR Community Standard
        df = pd.read_csv(file_path, sep='\t')
        
        clonotype_df = pd.DataFrame({
            'cloneId': df.get('clone_id', range(len(df))),
            'count': df.get('duplicate_count', 1),
            'frequency': df.get('clone_frequency', df.get('duplicate_count', 1) / df.get('duplicate_count', 1).sum()),
            'cdr3aa': df.get('junction_aa', ''),
            'cdr3nt': df.get('junction', ''),
            'v_gene': df.get('v_call', ''),
            'j_gene': df.get('j_call', ''),
            'chain': df.get('locus', 'TRB')
        })

    # Calculate additional metrics
    clonotype_df['cdr3_length'] = clonotype_df['cdr3aa'].str.len()
    
    return clonotype_df

# Load TCR repertoire
tcr_data = load_airr_data("clonotypes.txt", format='mixcr')
print(f"Loaded {len(tcr_data)} unique clonotypes")
print(f"Total reads: {tcr_data['count'].sum()}")
```

**Define Clonotypes**

```python
def define_clonotypes(df, method='cdr3aa'):
    """
    Define clonotypes based on various criteria.

    Methods:
    - 'cdr3aa': Amino acid CDR3 sequence only
    - 'cdr3nt': Nucleotide CDR3 sequence
    - 'vj_cdr3': V gene + J gene + CDR3aa (most common)
    """
    if method == 'cdr3aa':
        df['clonotype'] = df['cdr3aa']
    
    elif method == 'cdr3nt':
        df['clonotype'] = df['cdr3nt']
    
    elif method == 'vj_cdr3':
        # Extract V and J gene families (e.g., TRBV12-3 -> TRBV12)
        df['v_family'] = df['v_gene'].str.extract(r'(TRB[VDJ]\d+)', expand=False)
        df['j_family'] = df['j_gene'].str.extract(r'(TRB[VDJ]\d+)', expand=False)
        
        # Combine V + J + CDR3
        df['clonotype'] = df['v_family'] + '_' + df['j_family'] + '_' + df['cdr3aa']
    
    # Aggregate by clonotype
    clonotype_summary = df.groupby('clonotype').agg({
        'count': 'sum',
        'frequency': 'sum'
    }).reset_index()
    
    clonotype_summary = clonotype_summary.sort_values('count', ascending=False)
    clonotype_summary['rank'] = range(1, len(clonotype_summary) + 1)
    
    return clonotype_summary

# Define clonotypes
clonotypes = define_clonotypes(tcr_data, method='vj_cdr3')
print(f"Identified {len(clonotypes)} unique clonotypes")
```

### Phase 2: Diversity & Clonality Analysis

**Calculate Diversity Metrics**

```python
def calculate_diversity(clonotype_counts):
    """
    Calculate diversity metrics for immune repertoire.

    Metrics:
    - Shannon entropy: Overall diversity
    - Simpson index: Probability two random clones are same
    - Inverse Simpson: Effective number of clonotypes
    - Gini coefficient: Inequality in clonotype distribution
    """
    from scipy.stats import entropy
    
    # Normalize to frequencies
    if isinstance(clonotype_counts, pd.Series):
        counts = clonotype_counts.values
    else:
        counts = clonotype_counts
    
    freqs = counts / counts.sum()
    
    # Shannon entropy
    shannon = entropy(freqs, base=2)
    
    # Simpson index (D)
    simpson = np.sum(freqs ** 2)
    
    # Inverse Simpson (1/D) - effective number of clonotypes
    inv_simpson = 1 / simpson if simpson > 0 else 0
    
    # Gini coefficient
    sorted_freqs = np.sort(freqs)
    n = len(freqs)
    cumsum = np.cumsum(sorted_freqs)
    gini = (2 * np.sum((np.arange(1, n+1)) * sorted_freqs)) / (n * cumsum[-1]) - (n + 1) / n
    
    # Richness (number of unique clonotypes)
    richness = len(counts)
    
    # Clonality (1 - Pielou's evenness)
    max_entropy = np.log2(richness)
    evenness = shannon / max_entropy if max_entropy > 0 else 0
    clonality = 1 - evenness
    
    return {
        'richness': richness,
        'shannon_entropy': shannon,
        'simpson_index': simpson,
        'inverse_simpson': inv_simpson,
        'gini_coefficient': gini,
        'evenness': evenness,
        'clonality': clonality
    }

# Calculate diversity
diversity = calculate_diversity(clonotypes['count'])
print("Diversity Metrics:")
for metric, value in diversity.items():
    print(f"  {metric}: {value:.4f}")
```

**Rarefaction Analysis**

```python
def rarefaction_curve(df, n_samples=100, n_boots=10):
    """
    Generate rarefaction curve to assess sampling depth.
    
    Shows how clonotype richness increases with sequencing depth.
    """
    total_reads = df['count'].sum()
    sample_sizes = np.linspace(1000, total_reads, n_samples)
    
    richness_curves = []
    
    for _ in range(n_boots):
        richness_at_depth = []
        
        for sample_size in sample_sizes:
            # Sample reads according to clonotype frequencies
            sampled = np.random.choice(
                df.index,
                size=int(sample_size),
                p=df['frequency'].values,
                replace=True
            )
            
            # Count unique clonotypes
            unique_clonotypes = len(set(sampled))
            richness_at_depth.append(unique_clonotypes)
        
        richness_curves.append(richness_at_depth)
    
    # Calculate mean and std
    mean_richness = np.mean(richness_curves, axis=0)
    std_richness = np.std(richness_curves, axis=0)
    
    return sample_sizes, mean_richness, std_richness

# Generate rarefaction curve
sample_sizes, mean_rich, std_rich = rarefaction_curve(clonotypes)

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 5))
plt.plot(sample_sizes, mean_rich, 'b-', label='Mean richness')
plt.fill_between(sample_sizes, mean_rich - std_rich, mean_rich + std_rich, alpha=0.3)
plt.xlabel('Sequencing Depth (reads)')
plt.ylabel('Clonotype Richness')
plt.title('Rarefaction Curve')
plt.legend()
plt.savefig('rarefaction_curve.png', dpi=300)
```

### Phase 3: V(D)J Gene Usage Analysis

**Analyze V and J Gene Usage**

```python
def analyze_vdj_usage(df):
    """
    Analyze V(D)J gene usage patterns.
    """
    # Extract gene families
    df['v_family'] = df['v_gene'].str.extract(r'(TRB[VDJ]\d+)', expand=False)
    df['j_family'] = df['j_gene'].str.extract(r'(TRB[VDJ]\d+)', expand=False)
    
    # V gene usage (weighted by count)
    v_usage = df.groupby('v_family')['count'].sum().sort_values(ascending=False)
    v_usage_freq = v_usage / v_usage.sum()
    
    # J gene usage
    j_usage = df.groupby('j_family')['count'].sum().sort_values(ascending=False)
    j_usage_freq = j_usage / j_usage.sum()
    
    # V-J pairing
    vj_pairs = df.groupby(['v_family', 'j_family'])['count'].sum().reset_index()
    vj_pairs['frequency'] = vj_pairs['count'] / vj_pairs['count'].sum()
    vj_pairs = vj_pairs.sort_values('count', ascending=False)
    
    return {
        'v_usage': v_usage_freq,
        'j_usage': j_usage_freq,
        'vj_pairs': vj_pairs
    }

# Analyze V(D)J usage
vdj_usage = analyze_vdj_usage(tcr_data)

print("Top 10 V genes:")
print(vdj_usage['v_usage'].head(10))

print("\nTop 10 J genes:")
print(vdj_usage['j_usage'].head(10))

print("\nTop 10 V-J pairs:")
print(vdj_usage['vj_pairs'].head(10))
```

**Statistical Testing for Biased Usage**

```python
def test_vdj_bias(observed_usage, expected_frequencies=None):
    """
    Test whether V(D)J gene usage deviates from expected (uniform or reference).
    
    Uses chi-square test.
    """
    from scipy.stats import chisquare
    
    observed = observed_usage.values
    
    if expected_frequencies is None:
        # Assume uniform distribution
        expected = np.ones(len(observed)) / len(observed) * observed.sum()
    else:
        # Use provided reference frequencies
        expected = expected_frequencies * observed.sum()
    
    # Chi-square test
    chi2, pvalue = chisquare(observed, f_exp=expected)
    
    return {
        'chi2_statistic': chi2,
        'p_value': pvalue,
        'significant': pvalue < 0.05
    }

# Test for V gene bias
v_bias_test = test_vdj_bias(vdj_usage['v_usage'] * tcr_data['count'].sum())
print(f"V gene usage bias test: chi2={v_bias_test['chi2_statistic']:.2f}, p={v_bias_test['p_value']:.2e}")
```

### Phase 4: CDR3 Sequence Analysis

**CDR3 Length Distribution**

```python
def analyze_cdr3_length(df):
    """
    Analyze CDR3 length distribution.
    
    Typical TCR CDR3 length: 12-18 amino acids
    Typical BCR CDR3 length: 10-20 amino acids
    """
    # Length distribution (weighted by count)
    length_dist = df.groupby('cdr3_length')['count'].sum().sort_index()
    length_freq = length_dist / length_dist.sum()
    
    # Statistics
    mean_length = (df['cdr3_length'] * df['count']).sum() / df['count'].sum()
    median_length = df['cdr3_length'].median()
    
    return {
        'length_distribution': length_freq,
        'mean_length': mean_length,
        'median_length': median_length
    }

# Analyze CDR3 length
cdr3_analysis = analyze_cdr3_length(tcr_data)
print(f"Mean CDR3 length: {cdr3_analysis['mean_length']:.1f} aa")
print(f"Median CDR3 length: {cdr3_analysis['median_length']:.0f} aa")

# Plot distribution
plt.figure(figsize=(8, 5))
plt.bar(cdr3_analysis['length_distribution'].index, cdr3_analysis['length_distribution'].values)
plt.xlabel('CDR3 Length (amino acids)')
plt.ylabel('Frequency')
plt.title('CDR3 Length Distribution')
plt.savefig('cdr3_length_distribution.png', dpi=300)
```

**Amino Acid Composition**

```python
def analyze_cdr3_composition(cdr3_sequences, weights=None):
    """
    Analyze amino acid composition in CDR3 regions.
    """
    from collections import Counter
    
    if weights is None:
        weights = np.ones(len(cdr3_sequences))
    
    # Count amino acids (weighted by clonotype frequency)
    aa_counts = Counter()
    total_aa = 0
    
    for seq, weight in zip(cdr3_sequences, weights):
        for aa in seq:
            aa_counts[aa] += weight
            total_aa += weight
    
    # Convert to frequencies
    aa_freq = {aa: count / total_aa for aa, count in aa_counts.items()}
    aa_freq_df = pd.DataFrame.from_dict(aa_freq, orient='index', columns=['frequency'])
    aa_freq_df = aa_freq_df.sort_values('frequency', ascending=False)
    
    return aa_freq_df

# Analyze amino acid composition
aa_comp = analyze_cdr3_composition(tcr_data['cdr3aa'], weights=tcr_data['count'])
print("Top 10 amino acids in CDR3:")
print(aa_comp.head(10))
```

### Phase 5: Clonal Expansion Detection

**Identify Expanded Clonotypes**

```python
def detect_expanded_clones(clonotypes, threshold_percentile=95):
    """
    Identify clonally expanded T/B cell populations.
    
    Expanded clonotypes = clones above frequency threshold.
    """
    # Calculate threshold (e.g., 95th percentile)
    threshold = np.percentile(clonotypes['frequency'], threshold_percentile)
    
    # Identify expanded clones
    expanded = clonotypes[clonotypes['frequency'] >= threshold].copy()
    expanded = expanded.sort_values('frequency', ascending=False)
    
    # Calculate expansion metrics
    total_expanded_freq = expanded['frequency'].sum()
    n_expanded = len(expanded)
    
    return {
        'expanded_clonotypes': expanded,
        'n_expanded': n_expanded,
        'expanded_frequency': total_expanded_freq,
        'threshold': threshold
    }

# Detect expanded clones
expansion_result = detect_expanded_clones(clonotypes, threshold_percentile=95)

print(f"Detected {expansion_result['n_expanded']} expanded clonotypes")
print(f"Expanded clones represent {expansion_result['expanded_frequency']*100:.1f}% of repertoire")
print("\nTop 10 expanded clonotypes:")
print(expansion_result['expanded_clonotypes'].head(10))
```

**Longitudinal Clonotype Tracking**

```python
def track_clonotypes_longitudinal(timepoint_dataframes, clonotype_col='clonotype'):
    """
    Track clonotype dynamics across multiple timepoints.
    
    Input: List of DataFrames, each representing one timepoint
    """
    all_timepoints = []
    
    for i, df in enumerate(timepoint_dataframes):
        df_copy = df.copy()
        df_copy['timepoint'] = i
        all_timepoints.append(df_copy[[clonotype_col, 'frequency', 'timepoint']])
    
    # Merge all timepoints
    merged = pd.concat(all_timepoints, ignore_index=True)
    
    # Pivot to wide format
    tracking = merged.pivot(index=clonotype_col, columns='timepoint', values='frequency')
    tracking = tracking.fillna(0)  # Absent clonotypes = 0 frequency
    
    # Calculate persistence
    tracking['persistence'] = (tracking > 0).sum(axis=1)
    tracking['mean_frequency'] = tracking.iloc[:, :-1].mean(axis=1)
    tracking['max_frequency'] = tracking.iloc[:, :-1].max(axis=1)
    
    # Sort by persistence and frequency
    tracking = tracking.sort_values(['persistence', 'max_frequency'], ascending=False)
    
    return tracking

# Example: Track clonotypes across 3 timepoints
# timepoints = [tcr_t0, tcr_t1, tcr_t2]
# tracking = track_clonotypes_longitudinal(timepoints)
```

### Phase 6: Convergence & Public Clonotypes

**Detect Convergent Recombination**

```python
def detect_convergent_recombination(df):
    """
    Identify cases where different nucleotide sequences encode same CDR3 amino acid.
    
    Convergent recombination = same CDR3aa from different CDR3nt sequences.
    """
    # Group by CDR3 amino acid sequence
    convergence = df.groupby('cdr3aa').agg({
        'cdr3nt': lambda x: len(set(x)),  # Number of unique nucleotide sequences
        'count': 'sum',
        'frequency': 'sum'
    }).reset_index()
    
    # Filter for convergent (>1 nucleotide sequence)
    convergent = convergence[convergence['cdr3nt'] > 1].copy()
    convergent = convergent.rename(columns={'cdr3nt': 'n_nucleotide_variants'})
    convergent = convergent.sort_values('n_nucleotide_variants', ascending=False)
    
    return convergent

# Detect convergence
convergent_clones = detect_convergent_recombination(tcr_data)
print(f"Found {len(convergent_clones)} convergent CDR3 sequences")
print("\nTop 10 convergent sequences:")
print(convergent_clones.head(10))
```

**Identify Public (Shared) Clonotypes**

```python
def identify_public_clonotypes(sample_dataframes, min_samples=2):
    """
    Identify public (shared) clonotypes present in multiple samples.
    
    Input: List of DataFrames, each representing one sample
    """
    all_samples = []
    
    for i, df in enumerate(sample_dataframes):
        df_copy = df[['clonotype', 'frequency']].copy()
        df_copy['sample_id'] = f'Sample_{i+1}'
        all_samples.append(df_copy)
    
    # Merge all samples
    merged = pd.concat(all_samples, ignore_index=True)
    
    # Count how many samples each clonotype appears in
    public_counts = merged.groupby('clonotype').agg({
        'sample_id': lambda x: len(set(x)),
        'frequency': 'mean'
    }).reset_index()
    
    public_counts = public_counts.rename(columns={'sample_id': 'n_samples'})
    
    # Filter for public clonotypes
    public = public_counts[public_counts['n_samples'] >= min_samples].copy()
    public = public.sort_values(['n_samples', 'frequency'], ascending=False)
    
    return public

# Example: Identify public clonotypes across 5 samples
# samples = [sample1_tcr, sample2_tcr, sample3_tcr, sample4_tcr, sample5_tcr]
# public_clonotypes = identify_public_clonotypes(samples, min_samples=3)
```

### Phase 7: Epitope Prediction & Specificity

**Query IEDB for Known Epitopes**

```python
def query_epitope_database(cdr3_sequences, organism='human', top_n=10):
    """
    Query IEDB for known T-cell epitopes matching CDR3 sequences.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()
    
    epitope_matches = {}
    
    for cdr3 in cdr3_sequences[:top_n]:  # Limit to top clonotypes
        # Search IEDB for CDR3 sequence
        result = tu.run_one_function({
            "name": "IEDB_search_tcells",
            "arguments": {
                "receptor": cdr3,
                "organism": organism
            }
        })
        
        if 'data' in result and 'epitopes' in result['data']:
            epitopes = result['data']['epitopes']
            if len(epitopes) > 0:
                epitope_matches[cdr3] = epitopes
    
    return epitope_matches

# Query IEDB for top expanded clonotypes
# top_clones = expansion_result['expanded_clonotypes']['clonotype'].head(10)
# epitope_matches = query_epitope_database(top_clones)
```

**Predict Epitope Specificity with VDJdb**

```python
def predict_specificity_vdjdb(cdr3_sequences, chain='TRB'):
    """
    Predict antigen specificity using VDJdb (TCR database).
    
    VDJdb contains TCR sequences with known epitope specificity.
    """
    # Note: ToolUniverse doesn't have VDJdb tool yet
    # This is a placeholder for manual VDJdb query
    
    print("Manual VDJdb query required:")
    print("1. Go to https://vdjdb.cdr3.net/search")
    print("2. Search for CDR3 sequences:")
    for cdr3 in cdr3_sequences[:10]:
        print(f"   - {cdr3}")
    print("3. Check for matches with known epitopes (virus, tumor antigens)")
    
    # Alternative: Use literature search
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()
    
    specificity_results = {}
    
    for cdr3 in cdr3_sequences[:5]:  # Top 5 only
        result = tu.run_one_function({
            "name": "PubMed_search",
            "arguments": {
                "query": f'"{cdr3}" AND (epitope OR antigen OR specificity)',
                "max_results": 10
            }
        })
        
        if 'data' in result and 'papers' in result['data']:
            papers = result['data']['papers']
            if len(papers) > 0:
                specificity_results[cdr3] = papers
    
    return specificity_results

# Predict specificity
# top_cdr3 = expansion_result['expanded_clonotypes']['clonotype'].head(10)
# specificity = predict_specificity_vdjdb(top_cdr3)
```

### Phase 8: Integration with Single-Cell Data

**Link Clonotypes to Cell Phenotypes**

```python
def integrate_with_single_cell(vdj_df, gex_adata, barcode_col='barcode'):
    """
    Integrate TCR/BCR clonotypes with single-cell gene expression.
    
    Requires:
    - vdj_df: DataFrame with clonotype info (from 10x VDJ)
    - gex_adata: AnnData object with gene expression (from 10x GEX)
    """
    import scanpy as sc
    
    # Create clonotype mapping
    clonotype_map = dict(zip(vdj_df[barcode_col], vdj_df['clonotype']))
    
    # Add clonotype info to AnnData
    gex_adata.obs['clonotype'] = gex_adata.obs.index.map(clonotype_map)
    gex_adata.obs['has_clonotype'] = ~gex_adata.obs['clonotype'].isna()
    
    # Identify expanded clonotypes
    clonotype_counts = gex_adata.obs['clonotype'].value_counts()
    expanded_clonotypes = clonotype_counts[clonotype_counts > 5].index.tolist()
    
    gex_adata.obs['is_expanded'] = gex_adata.obs['clonotype'].isin(expanded_clonotypes)
    
    # Visualize on UMAP
    sc.pl.umap(gex_adata, color=['clonotype', 'is_expanded'], 
               title=['Clonotype', 'Expanded Clones'])
    
    return gex_adata

# Example integration
# integrated_data = integrate_with_single_cell(tcr_10x, gex_adata)
```

**Clonotype-Phenotype Association**

```python
def analyze_clonotype_phenotype(adata, clonotype_col='clonotype', cluster_col='leiden'):
    """
    Analyze association between clonotypes and cell phenotypes/clusters.
    """
    import scanpy as sc
    
    # Get cells with clonotypes
    cells_with_tcr = adata[~adata.obs[clonotype_col].isna()].copy()
    
    # Count clonotypes per cluster
    clonotype_cluster = pd.crosstab(
        cells_with_tcr.obs[clonotype_col],
        cells_with_tcr.obs[cluster_col],
        normalize='index'
    )
    
    # Find cluster-specific clonotypes (>80% cells in one cluster)
    cluster_specific = clonotype_cluster[clonotype_cluster.max(axis=1) > 0.8]
    
    # Get top expanded clonotypes per cluster
    top_per_cluster = {}
    for cluster in clonotype_cluster.columns:
        top_clonotypes = clonotype_cluster[cluster].sort_values(ascending=False).head(5)
        top_per_cluster[cluster] = top_clonotypes.index.tolist()
    
    return {
        'clonotype_cluster_matrix': clonotype_cluster,
        'cluster_specific_clonotypes': cluster_specific,
        'top_clonotypes_per_cluster': top_per_cluster
    }

# Analyze clonotype-phenotype associations
# associations = analyze_clonotype_phenotype(integrated_data)
```

## Advanced Use Cases

### Use Case 1: Cancer Immunotherapy Response Analysis

```python
# Compare TCR repertoires before and after immunotherapy

# Load baseline and post-treatment samples
tcr_baseline = load_airr_data("patient_baseline.txt", format='mixcr')
tcr_post = load_airr_data("patient_post_treatment.txt", format='mixcr')

# Define clonotypes
clones_baseline = define_clonotypes(tcr_baseline, method='vj_cdr3')
clones_post = define_clonotypes(tcr_post, method='vj_cdr3')

# Calculate diversity changes
div_baseline = calculate_diversity(clones_baseline['count'])
div_post = calculate_diversity(clones_post['count'])

print(f"Baseline diversity: {div_baseline['shannon_entropy']:.2f}")
print(f"Post-treatment diversity: {div_post['shannon_entropy']:.2f}")
print(f"Change: {div_post['shannon_entropy'] - div_baseline['shannon_entropy']:.2f}")

# Track clonal expansion
expanded_baseline = detect_expanded_clones(clones_baseline)
expanded_post = detect_expanded_clones(clones_post)

# Identify newly expanded clonotypes
new_clones = set(expanded_post['expanded_clonotypes']['clonotype']) - \
             set(expanded_baseline['expanded_clonotypes']['clonotype'])

print(f"Newly expanded clonotypes: {len(new_clones)}")

# Query epitope specificity for newly expanded clones
epitope_matches = query_epitope_database(list(new_clones)[:10])
```

### Use Case 2: Vaccine Response Tracking

```python
# Track TCR repertoire changes after vaccination

timepoints = [
    load_airr_data("pre_vaccine.txt", format='mixcr'),
    load_airr_data("week1_post.txt", format='mixcr'),
    load_airr_data("week4_post.txt", format='mixcr'),
    load_airr_data("week12_post.txt", format='mixcr')
]

# Process each timepoint
clonotype_dfs = [define_clonotypes(df, method='vj_cdr3') for df in timepoints]

# Track longitudinal dynamics
tracking = track_clonotypes_longitudinal(clonotype_dfs)

# Identify persistent vaccine-responding clones
persistent_clones = tracking[tracking['persistence'] == 4]  # Present at all timepoints
print(f"Persistent clonotypes: {len(persistent_clones)}")

# Identify clonotypes that expanded after vaccination
tracking['fold_change'] = tracking.iloc[:, 3] / (tracking.iloc[:, 0] + 1e-6)
vaccine_responders = tracking[tracking['fold_change'] > 10]
print(f"Vaccine-responding clonotypes (>10-fold expansion): {len(vaccine_responders)}")
```

### Use Case 3: Autoimmune Disease Repertoire Analysis

```python
# Compare TCR repertoires between autoimmune patients and healthy controls

# Load data
patient_tcr = load_airr_data("autoimmune_patient.txt", format='mixcr')
control_tcr = load_airr_data("healthy_control.txt", format='mixcr')

# Define clonotypes
patient_clones = define_clonotypes(patient_tcr, method='vj_cdr3')
control_clones = define_clonotypes(control_tcr, method='vj_cdr3')

# Compare diversity
div_patient = calculate_diversity(patient_clones['count'])
div_control = calculate_diversity(control_clones['count'])

print(f"Patient clonality: {div_patient['clonality']:.3f}")
print(f"Control clonality: {div_control['clonality']:.3f}")

# Identify disease-specific clonotypes
patient_specific = set(patient_clones['clonotype']) - set(control_clones['clonotype'])
print(f"Patient-specific clonotypes: {len(patient_specific)}")

# Analyze V(D)J usage bias
vdj_patient = analyze_vdj_usage(patient_tcr)
vdj_control = analyze_vdj_usage(control_tcr)

# Compare V gene usage
v_comparison = pd.DataFrame({
    'patient': vdj_patient['v_usage'],
    'control': vdj_control['v_usage']
}).fillna(0)

v_comparison['fold_change'] = (v_comparison['patient'] + 1e-6) / (v_comparison['control'] + 1e-6)
biased_v_genes = v_comparison[v_comparison['fold_change'] > 2]
print(f"V genes overrepresented in patient: {len(biased_v_genes)}")
```

### Use Case 4: Single-Cell TCR-seq + RNA-seq Integration

```python
# Integrate TCR clonotypes with T-cell phenotypes

import scanpy as sc

# Load 10x data
tcr_10x = load_airr_data("filtered_contig_annotations.csv", format='10x')
gex_adata = sc.read_10x_h5("filtered_feature_bc_matrix.h5")

# Standard single-cell processing
sc.pp.filter_cells(gex_adata, min_genes=200)
sc.pp.normalize_total(gex_adata, target_sum=1e4)
sc.pp.log1p(gex_adata)
sc.pp.highly_variable_genes(gex_adata, n_top_genes=2000)
sc.pp.pca(gex_adata)
sc.pp.neighbors(gex_adata)
sc.tl.umap(gex_adata)
sc.tl.leiden(gex_adata)

# Integrate TCR data
integrated = integrate_with_single_cell(tcr_10x, gex_adata)

# Analyze clonotype-phenotype associations
associations = analyze_clonotype_phenotype(integrated)

# Identify phenotype of expanded clones
expanded_cells = integrated[integrated.obs['is_expanded']].copy()
sc.pl.umap(expanded_cells, color='leiden', title='Phenotype of Expanded Clones')

# Find marker genes for expanded vs non-expanded
sc.tl.rank_genes_groups(integrated, 'is_expanded', method='wilcoxon')
sc.pl.rank_genes_groups(integrated, n_genes=20)
```

## ToolUniverse Tool Integration

**Key Tools Used**:
- `IEDB_search_tcells` - Known T-cell epitopes
- `IEDB_search_bcells` - Known B-cell epitopes
- `PubMed_search` - Literature on TCR/BCR specificity
- `UniProt_get_protein` - Antigen protein information

**Integration with Other Skills**:
- `tooluniverse-single-cell` - Single-cell transcriptomics
- `tooluniverse-rnaseq-deseq2` - Bulk RNA-seq analysis
- `tooluniverse-variant-analysis` - Somatic hypermutation analysis (BCR)

## Best Practices

1. **Sequencing Depth**: Aim for 10,000+ unique UMIs per sample for bulk TCR-seq; 500+ for single-cell

2. **Technical Replicates**: Use biological replicates (n≥3) for statistical comparisons

3. **Clonotype Definition**: Use V+J+CDR3aa for most analyses (balances specificity and sensitivity)

4. **Diversity Metrics**: Report multiple metrics (Shannon, Simpson, clonality) for comprehensive assessment

5. **Rare Clonotypes**: Filter clonotypes with very low frequency (<0.001%) to remove sequencing errors

6. **Public Clonotypes**: Check VDJdb, McPAS-TCR databases for known antigen specificities

7. **CDR3 Length**: Flag unusual length distributions (may indicate PCR bias or sequencing issues)

8. **V(D)J Annotation**: Use high-quality reference databases (IMGT, TRAPeS)

9. **Batch Effects**: Correct for batch effects when comparing samples from different runs

10. **Functional Validation**: Validate predicted specificities with tetramer staining or functional assays

## Troubleshooting

**Problem**: Very low diversity (few dominant clonotypes)
- **Solution**: May indicate clonal expansion (biological) or PCR bias (technical); check sequencing QC

**Problem**: Unusual CDR3 length distribution
- **Solution**: Check for PCR amplification bias; verify primer design

**Problem**: Many non-productive sequences
- **Solution**: May indicate B-cell repertoire or contamination; filter for productive sequences only

**Problem**: No matches in epitope databases
- **Solution**: Most TCR/BCR specificities are unknown; use convergence and public clonotype analysis

**Problem**: Low integration rate with single-cell GEX
- **Solution**: Check cell barcodes match; ensure VDJ and GEX libraries from same cells

## References

- Dash P, et al. (2017) Quantifiable predictive features define epitope-specific T cell receptor repertoires. Nature
- Glanville J, et al. (2017) Identifying specificity groups in the T cell receptor repertoire. Nature
- Stubbington MJT, et al. (2016) T cell fate and clonality inference from single-cell transcriptomes. Nature Methods
- Vander Heiden JA, et al. (2014) pRESTO: a toolkit for processing high-throughput sequencing raw reads of lymphocyte receptor repertoires. Bioinformatics

## Quick Start

```python
# Minimal workflow
from tooluniverse import ToolUniverse

# 1. Load data
tcr_data = load_airr_data("clonotypes.txt", format='mixcr')

# 2. Define clonotypes
clonotypes = define_clonotypes(tcr_data, method='vj_cdr3')

# 3. Calculate diversity
diversity = calculate_diversity(clonotypes['count'])
print(f"Shannon entropy: {diversity['shannon_entropy']:.2f}")

# 4. Detect expanded clones
expansion = detect_expanded_clones(clonotypes)
print(f"Expanded clonotypes: {expansion['n_expanded']}")

# 5. Analyze V(D)J usage
vdj_usage = analyze_vdj_usage(tcr_data)

# 6. Query epitope databases
top_clones = expansion['expanded_clonotypes']['clonotype'].head(10)
epitopes = query_epitope_database(top_clones)
```
