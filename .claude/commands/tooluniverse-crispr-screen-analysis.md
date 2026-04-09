# tooluniverse-crispr-screen-analysis

> Comprehensive CRISPR screen analysis for functional genomics. Analyze pooled or arrayed CRISPR screens (knockout, activation, interference) to identify essential genes, synthetic lethal interactions, and drug targets. Perform sgRNA count processing, gene-level scoring (MAGeCK, BAGEL), quality control, pathway enrichment, and drug target prioritization. Use for CRISPR screen analysis, gene essentiality studies, synthetic lethality detection, functional genomics, drug target validation, or identifying genetic vulnerabilities.

# ToolUniverse CRISPR Screen Analysis

Comprehensive skill for analyzing CRISPR-Cas9 genetic screens to identify essential genes, synthetic lethal interactions, and therapeutic targets through robust statistical analysis and pathway enrichment.

## Overview

CRISPR screens enable genome-wide functional genomics by systematically perturbing genes and measuring fitness effects. This skill provides an 8-phase workflow for:
- Processing sgRNA count matrices
- Quality control and normalization
- Gene-level essentiality scoring (MAGeCK-like and BAGEL-like approaches)
- Synthetic lethality detection
- Pathway enrichment analysis
- Drug target prioritization with DepMap integration
- Integration with expression and mutation data

## Core Workflow

### Phase 1: Data Import & sgRNA Count Processing

**Load sgRNA Count Matrix**

```python
import pandas as pd
import numpy as np

def load_sgrna_counts(counts_file):
    """
    Load sgRNA count matrix from MAGeCK format or generic TSV.

    Expected format:
    sgRNA | Gene | Sample1 | Sample2 | Sample3 | ...
    sgRNA_1 | BRCA1 | 1500 | 1200 | 1100 | ...
    sgRNA_2 | BRCA1 | 1800 | 1500 | 1400 | ...
    """
    counts = pd.read_csv(counts_file, sep='\t')

    # Validate required columns
    required_cols = ['sgRNA', 'Gene']
    if not all(col in counts.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {required_cols}")

    # Extract sample columns
    sample_cols = [col for col in counts.columns if col not in ['sgRNA', 'Gene']]

    # Create count matrix
    count_matrix = counts[sample_cols].copy()
    count_matrix.index = counts['sgRNA']

    # Gene mapping
    sgrna_to_gene = dict(zip(counts['sgRNA'], counts['Gene']))

    metadata = {
        'n_sgrnas': len(counts),
        'n_genes': counts['Gene'].nunique(),
        'n_samples': len(sample_cols),
        'sample_names': sample_cols,
        'sgrna_to_gene': sgrna_to_gene
    }

    return count_matrix, metadata

# Load counts
counts, meta = load_sgrna_counts("sgrna_counts.txt")
print(f"Loaded {meta['n_sgrnas']} sgRNAs targeting {meta['n_genes']} genes across {meta['n_samples']} samples")
```

**Create Experimental Design Table**

```python
def create_design_matrix(sample_names, conditions, timepoints=None):
    """
    Create experimental design linking samples to conditions.

    Example:
    Sample | Condition | Timepoint | Replicate
    T0_rep1 | baseline | 0 | 1
    T14_rep1 | treatment | 14 | 1
    """
    design = pd.DataFrame({
        'Sample': sample_names,
        'Condition': conditions
    })

    if timepoints is not None:
        design['Timepoint'] = timepoints

    # Auto-detect replicates
    design['Replicate'] = design.groupby('Condition').cumcount() + 1

    return design

# Example usage
sample_names = ['T0_rep1', 'T0_rep2', 'T14_rep1', 'T14_rep2', 'T14_rep3']
conditions = ['baseline', 'baseline', 'treatment', 'treatment', 'treatment']
design = create_design_matrix(sample_names, conditions)
```

### Phase 2: Quality Control & Filtering

**Assess sgRNA Distribution**

```python
def qc_sgrna_distribution(count_matrix, min_reads=30, min_samples=2):
    """
    Quality control for sgRNA distribution.
    - Remove sgRNAs with low read counts
    - Check for outlier samples
    - Assess library representation
    """
    results = {}

    # 1. Library size per sample
    library_sizes = count_matrix.sum(axis=0)
    results['library_sizes'] = library_sizes
    results['median_library_size'] = library_sizes.median()

    # 2. Zero-count sgRNAs
    zero_counts = (count_matrix == 0).sum(axis=1)
    results['zero_counts'] = zero_counts
    results['sgrnas_with_zeros'] = (zero_counts > 0).sum()

    # 3. Low-count sgRNAs (< min_reads in > min_samples)
    low_count_mask = (count_matrix < min_reads).sum(axis=1) > (len(count_matrix.columns) - min_samples)
    results['low_count_sgrnas'] = low_count_mask.sum()

    # 4. Gini coefficient (library skewness)
    def gini_coefficient(counts):
        sorted_counts = np.sort(counts)
        n = len(counts)
        cumsum = np.cumsum(sorted_counts)
        return (2 * np.sum((np.arange(1, n+1)) * sorted_counts)) / (n * cumsum[-1]) - (n + 1) / n

    results['gini_per_sample'] = {col: gini_coefficient(count_matrix[col].values)
                                   for col in count_matrix.columns}

    # 5. Recommend filtering
    results['filter_recommendation'] = {
        'min_reads': min_reads,
        'min_samples_above_threshold': min_samples,
        'sgrnas_to_remove': low_count_mask.sum()
    }

    return results

# Run QC
qc_results = qc_sgrna_distribution(counts, min_reads=30, min_samples=2)
print(f"Library sizes: {qc_results['library_sizes']}")
print(f"Low-count sgRNAs to remove: {qc_results['filter_recommendation']['sgrnas_to_remove']}")
```

**Filter Low-Count sgRNAs**

```python
def filter_low_count_sgrnas(count_matrix, sgrna_to_gene, min_reads=30, min_samples=2):
    """
    Remove sgRNAs with insufficient read counts.
    """
    # Keep sgRNAs with >= min_reads in >= min_samples
    keep_mask = (count_matrix >= min_reads).sum(axis=1) >= min_samples

    filtered_counts = count_matrix[keep_mask].copy()
    filtered_mapping = {k: v for k, v in sgrna_to_gene.items() if k in filtered_counts.index}

    print(f"Filtered: {(~keep_mask).sum()} sgRNAs removed, {keep_mask.sum()} retained")

    return filtered_counts, filtered_mapping

# Apply filtering
filtered_counts, filtered_mapping = filter_low_count_sgrnas(counts, meta['sgrna_to_gene'])
```

### Phase 3: Normalization

**Library Size Normalization**

```python
def normalize_counts(count_matrix, method='median'):
    """
    Normalize sgRNA counts to account for library size differences.

    Methods:
    - 'median': Median ratio normalization (like DESeq2)
    - 'total': Total count normalization (CPM-like)
    """
    if method == 'median':
        # Calculate geometric mean for each sgRNA across samples
        pseudo_ref = np.exp(np.log(count_matrix + 1).mean(axis=1)) - 1

        # Calculate size factors for each sample
        size_factors = {}
        for col in count_matrix.columns:
            ratios = count_matrix[col] / pseudo_ref
            ratios = ratios[ratios > 0]  # Remove zeros
            size_factors[col] = ratios.median()

        # Normalize
        normalized = count_matrix.div(pd.Series(size_factors), axis=1)

    elif method == 'total':
        # CPM-like normalization
        size_factors = count_matrix.sum(axis=0) / 1e6
        normalized = count_matrix.div(size_factors, axis=1)

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    return normalized, size_factors

# Normalize
norm_counts, size_factors = normalize_counts(filtered_counts, method='median')
```

**Log-Fold Change Calculation**

```python
def calculate_lfc(norm_counts, design, control_condition='baseline', treatment_condition='treatment'):
    """
    Calculate log2 fold changes between treatment and control.
    """
    # Get sample names for each condition
    control_samples = design[design['Condition'] == control_condition]['Sample'].tolist()
    treatment_samples = design[design['Condition'] == treatment_condition]['Sample'].tolist()

    # Calculate mean counts
    control_mean = norm_counts[control_samples].mean(axis=1)
    treatment_mean = norm_counts[treatment_samples].mean(axis=1)

    # Log2 fold change (add pseudocount to avoid log(0))
    lfc = np.log2((treatment_mean + 1) / (control_mean + 1))

    return lfc, control_mean, treatment_mean

# Calculate LFC
lfc, control_mean, treatment_mean = calculate_lfc(norm_counts, design)
```

### Phase 4: Gene-Level Scoring (MAGeCK-like)

**Aggregate sgRNA Scores to Gene Level**

```python
def mageck_gene_scoring(lfc, sgrna_to_gene, method='rra'):
    """
    Gene-level essentiality scoring using MAGeCK-like approach.

    Methods:
    - 'rra': Robust Rank Aggregation (identify genes with consistently low-ranking sgRNAs)
    - 'mean': Simple mean LFC across sgRNAs
    """
    # Create gene-level aggregation
    gene_lfc = {}

    for sgrna, gene in sgrna_to_gene.items():
        if sgrna in lfc.index:
            if gene not in gene_lfc:
                gene_lfc[gene] = []
            gene_lfc[gene].append(lfc[sgrna])

    if method == 'rra':
        # Simplified RRA: rank sgRNAs, calculate p-value for each gene
        # based on whether its sgRNAs are enriched at the top (negative selection)
        # or bottom (positive selection)

        # Rank all sgRNAs by LFC
        ranked_sgrnas = lfc.sort_values()
        ranks = {sgrna: rank for rank, sgrna in enumerate(ranked_sgrnas.index, 1)}

        gene_scores = {}
        for gene, sgrna_list in gene_lfc.items():
            # Get ranks for this gene's sgRNAs
            gene_ranks = [ranks[sgrna] for sgrna in sgrna_list if sgrna in ranks]

            if len(gene_ranks) > 0:
                # Use mean rank as score (lower = more essential)
                gene_scores[gene] = {
                    'score': np.mean(gene_ranks),
                    'n_sgrnas': len(gene_ranks),
                    'mean_lfc': np.mean([lfc[sg] for sg in sgrna_list if sg in lfc.index])
                }

        # Convert to DataFrame
        gene_df = pd.DataFrame(gene_scores).T
        gene_df['rank'] = gene_df['score'].rank()

    elif method == 'mean':
        # Simple mean LFC
        gene_df = pd.DataFrame({
            gene: {
                'mean_lfc': np.mean(sgrna_lfcs),
                'n_sgrnas': len(sgrna_lfcs),
                'score': np.mean(sgrna_lfcs)
            }
            for gene, sgrna_lfcs in gene_lfc.items()
        }).T

    # Sort by essentiality (negative LFC = essential)
    gene_df = gene_df.sort_values('mean_lfc')

    return gene_df

# Gene-level scoring
gene_scores = mageck_gene_scoring(lfc, filtered_mapping, method='rra')
print(f"Top 10 essential genes:\n{gene_scores.head(10)[['mean_lfc', 'n_sgrnas']]}")
```

**Bayes Factor Scoring (BAGEL-like)**

```python
def bagel_bayes_factor(lfc, sgrna_to_gene, essential_genes=None, nonessential_genes=None):
    """
    BAGEL-like Bayes Factor calculation for gene essentiality.

    Uses reference sets of known essential and non-essential genes to
    calculate likelihood ratios.
    """
    # Default reference gene sets (core essential genes)
    if essential_genes is None:
        essential_genes = ['RPL5', 'RPS6', 'POLR2A', 'PSMC2', 'PSMD14']  # Example

    if nonessential_genes is None:
        nonessential_genes = ['AAVS1', 'ROSA26', 'HPRT1']  # Example

    # Get LFC distributions for reference sets
    essential_lfc = [lfc[sg] for sg, g in sgrna_to_gene.items()
                     if g in essential_genes and sg in lfc.index]
    nonessential_lfc = [lfc[sg] for sg, g in sgrna_to_gene.items()
                        if g in nonessential_genes and sg in lfc.index]

    if len(essential_lfc) < 3 or len(nonessential_lfc) < 3:
        print("Warning: Insufficient reference genes for BAGEL scoring")
        return None

    # Estimate distributions (simplified)
    essential_mean, essential_std = np.mean(essential_lfc), np.std(essential_lfc)
    nonessential_mean, nonessential_std = np.mean(nonessential_lfc), np.std(nonessential_lfc)

    # Calculate Bayes Factor for each gene
    gene_bf = {}
    gene_lfc_map = {}
    for sgrna, gene in sgrna_to_gene.items():
        if sgrna in lfc.index:
            if gene not in gene_lfc_map:
                gene_lfc_map[gene] = []
            gene_lfc_map[gene].append(lfc[sgrna])

    for gene, sgrna_lfcs in gene_lfc_map.items():
        mean_lfc = np.mean(sgrna_lfcs)

        # Likelihood under essential distribution
        from scipy.stats import norm
        l_essential = norm.pdf(mean_lfc, essential_mean, essential_std)

        # Likelihood under non-essential distribution
        l_nonessential = norm.pdf(mean_lfc, nonessential_mean, nonessential_std)

        # Bayes Factor (avoid division by zero)
        bf = l_essential / (l_nonessential + 1e-10)

        gene_bf[gene] = {
            'bayes_factor': bf,
            'mean_lfc': mean_lfc,
            'n_sgrnas': len(sgrna_lfcs)
        }

    # Convert to DataFrame and sort
    bf_df = pd.DataFrame(gene_bf).T
    bf_df = bf_df.sort_values('bayes_factor', ascending=False)

    return bf_df

# BAGEL scoring
bf_scores = bagel_bayes_factor(lfc, filtered_mapping)
if bf_scores is not None:
    print(f"Top 10 by Bayes Factor:\n{bf_scores.head(10)}")
```

### Phase 5: Synthetic Lethality Detection

**Identify Context-Specific Essential Genes**

```python
def detect_synthetic_lethality(gene_scores_wildtype, gene_scores_mutant,
                                lfc_threshold=-1.0, rank_diff_threshold=100):
    """
    Identify genes that are selectively essential in mutant context
    (synthetic lethal interactions).

    Compare essentiality scores between wildtype and mutant cell lines.
    """
    # Merge scores
    comparison = pd.merge(
        gene_scores_wildtype[['mean_lfc', 'rank']],
        gene_scores_mutant[['mean_lfc', 'rank']],
        left_index=True,
        right_index=True,
        suffixes=('_wt', '_mut')
    )

    # Calculate differential essentiality
    comparison['delta_lfc'] = comparison['mean_lfc_mut'] - comparison['mean_lfc_wt']
    comparison['delta_rank'] = comparison['rank_wt'] - comparison['rank_mut']

    # Identify synthetic lethal candidates
    # (more essential in mutant, not essential in wildtype)
    sl_candidates = comparison[
        (comparison['mean_lfc_mut'] < lfc_threshold) &  # Essential in mutant
        (comparison['mean_lfc_wt'] > -0.5) &  # Not essential in wildtype
        (comparison['delta_rank'] > rank_diff_threshold)  # Large rank change
    ].copy()

    sl_candidates = sl_candidates.sort_values('delta_lfc')

    return sl_candidates

# Example: Detect genes synthetic lethal with KRAS mutation
# (Requires running screens in both KRAS-mutant and wildtype cells)
# sl_hits = detect_synthetic_lethality(gene_scores_wt, gene_scores_kras_mut)
```

**Query DepMap for Known Dependencies**

```python
def query_depmap_dependencies(gene_symbol):
    """
    Query DepMap database for known gene dependencies.

    ToolUniverse doesn't have direct DepMap tools, but we can use
    STRING or literature tools to find dependency information.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Search literature for essentiality/dependency information
    result = tu.run_one_function({
        "name": "PubMed_search",
        "arguments": {
            "query": f'("{gene_symbol}"[Gene]) AND ("CRISPR screen" OR "gene essentiality" OR "DepMap")',
            "max_results": 20
        }
    })

    if 'data' in result and 'papers' in result['data']:
        papers = result['data']['papers']
        print(f"Found {len(papers)} papers on {gene_symbol} essentiality")
        return papers

    return []

# Example usage
# depmap_papers = query_depmap_dependencies("PRMT5")
```

### Phase 6: Pathway Enrichment Analysis

**Enrichment of Essential Genes**

```python
def enrich_essential_genes(gene_scores, top_n=100, databases=['KEGG_2021_Human', 'GO_Biological_Process_2021']):
    """
    Perform pathway enrichment on top essential genes.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Get top essential genes (most negative LFC)
    top_genes = gene_scores.head(top_n).index.tolist()

    print(f"Enriching {len(top_genes)} top essential genes...")

    # Run Enrichr
    result = tu.run_one_function({
        "name": "Enrichr_submit_genelist",
        "arguments": {
            "gene_list": top_genes,
            "description": "CRISPR_screen_essential_genes"
        }
    })

    if 'data' not in result or 'userListId' not in result['data']:
        print("Failed to submit gene list to Enrichr")
        return None

    user_list_id = result['data']['userListId']

    # Get enrichment results for each database
    all_results = {}
    for db in databases:
        enrich_result = tu.run_one_function({
            "name": "Enrichr_get_results",
            "arguments": {
                "userListId": user_list_id,
                "backgroundType": db
            }
        })

        if 'data' in enrich_result and db in enrich_result['data']:
            all_results[db] = pd.DataFrame(enrich_result['data'][db])
            print(f"{db}: {len(all_results[db])} enriched terms")

    return all_results

# Run enrichment
# enrichment_results = enrich_essential_genes(gene_scores, top_n=100)
```

### Phase 7: Drug Target Prioritization

**Integrate with Expression & Mutation Data**

```python
def prioritize_drug_targets(gene_scores, expression_data=None, mutation_data=None):
    """
    Prioritize CRISPR hits as drug targets based on:
    1. Essentiality score (from CRISPR screen)
    2. Expression level in disease vs normal (if provided)
    3. Mutation frequency in tumors (if provided)
    4. Druggability (query DGIdb)
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Start with top essential genes
    candidates = gene_scores.head(50).copy()

    # Add expression data if provided
    if expression_data is not None:
        candidates = candidates.merge(expression_data, left_index=True, right_index=True, how='left')

    # Add mutation data if provided
    if mutation_data is not None:
        candidates = candidates.merge(mutation_data, left_index=True, right_index=True, how='left')

    # Query druggability for each gene
    druggability_scores = {}
    for gene in candidates.index[:20]:  # Limit to top 20 to avoid rate limits
        result = tu.run_one_function({
            "name": "DGIdb_query_gene",
            "arguments": {"gene_symbol": gene}
        })

        if 'data' in result and 'matchedTerms' in result['data']:
            matches = result['data']['matchedTerms']
            if len(matches) > 0:
                # Count number of drug interactions
                n_drugs = len(matches[0].get('interactions', []))
                druggability_scores[gene] = n_drugs
            else:
                druggability_scores[gene] = 0
        else:
            druggability_scores[gene] = 0

    candidates['n_drugs'] = pd.Series(druggability_scores)

    # Calculate composite priority score
    # (Normalize each component to 0-1 scale)
    candidates['essentiality_norm'] = (candidates['mean_lfc'].min() - candidates['mean_lfc']) / \
                                       (candidates['mean_lfc'].min() - candidates['mean_lfc'].max())

    if 'log2fc' in candidates.columns:
        candidates['expression_norm'] = (candidates['log2fc'] - candidates['log2fc'].min()) / \
                                        (candidates['log2fc'].max() - candidates['log2fc'].min())
    else:
        candidates['expression_norm'] = 0

    candidates['druggability_norm'] = candidates['n_drugs'] / (candidates['n_drugs'].max() + 1)

    # Weighted composite score
    candidates['priority_score'] = (
        0.5 * candidates['essentiality_norm'] +
        0.3 * candidates['expression_norm'] +
        0.2 * candidates['druggability_norm']
    )

    # Sort by priority
    candidates = candidates.sort_values('priority_score', ascending=False)

    return candidates

# Prioritize targets
# drug_targets = prioritize_drug_targets(gene_scores, expression_data=rna_seq_results)
```

**Query Existing Drugs for Top Targets**

```python
def find_drugs_for_targets(target_genes, max_per_gene=5):
    """
    Find existing drugs targeting top candidate genes.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    drug_results = {}

    for gene in target_genes[:10]:  # Top 10 targets
        print(f"Searching drugs for {gene}...")

        # Query DGIdb
        result = tu.run_one_function({
            "name": "DGIdb_query_gene",
            "arguments": {"gene_symbol": gene}
        })

        if 'data' in result and 'matchedTerms' in result['data']:
            matches = result['data']['matchedTerms']
            if len(matches) > 0:
                interactions = matches[0].get('interactions', [])

                drugs = []
                for interaction in interactions[:max_per_gene]:
                    drugs.append({
                        'drug_name': interaction.get('drugName', 'Unknown'),
                        'interaction_type': interaction.get('interactionTypes', ['Unknown'])[0],
                        'source': interaction.get('source', 'Unknown')
                    })

                drug_results[gene] = drugs

    return drug_results

# Find drugs
# drug_candidates = find_drugs_for_targets(drug_targets.index.tolist())
```

### Phase 8: Report Generation

**Comprehensive CRISPR Screen Report**

```python
def generate_crispr_report(gene_scores, enrichment_results, drug_targets,
                           output_file="crispr_screen_report.md"):
    """
    Generate comprehensive CRISPR screen analysis report.
    """
    with open(output_file, 'w') as f:
        f.write("# CRISPR Screen Analysis Report\n\n")

        # Summary statistics
        f.write("## Summary\n\n")
        f.write(f"- **Total genes analyzed**: {len(gene_scores)}\n")
        f.write(f"- **Essential genes** (LFC < -1): {(gene_scores['mean_lfc'] < -1).sum()}\n")
        f.write(f"- **Non-essential genes** (LFC > -0.5): {(gene_scores['mean_lfc'] > -0.5).sum()}\n\n")

        # Top 20 essential genes
        f.write("## Top 20 Essential Genes\n\n")
        f.write("| Rank | Gene | Mean LFC | sgRNAs | Score |\n")
        f.write("|------|------|----------|--------|-------|\n")
        for idx, (gene, row) in enumerate(gene_scores.head(20).iterrows(), 1):
            f.write(f"| {idx} | {gene} | {row['mean_lfc']:.3f} | {int(row['n_sgrnas'])} | {row['score']:.2f} |\n")

        f.write("\n")

        # Pathway enrichment
        if enrichment_results:
            f.write("## Pathway Enrichment\n\n")
            for db, results in enrichment_results.items():
                f.write(f"### {db}\n\n")
                f.write("| Term | P-value | Adjusted P-value | Genes |\n")
                f.write("|------|---------|------------------|-------|\n")
                for _, row in results.head(10).iterrows():
                    term = row.get('Term', 'Unknown')
                    pval = row.get('P-value', 1.0)
                    adj_pval = row.get('Adjusted P-value', 1.0)
                    genes = row.get('Genes', '')
                    f.write(f"| {term} | {pval:.2e} | {adj_pval:.2e} | {genes[:50]}... |\n")
                f.write("\n")

        # Drug target prioritization
        if drug_targets is not None:
            f.write("## Top Drug Target Candidates\n\n")
            f.write("| Rank | Gene | Essentiality | Expression FC | Druggable | Priority Score |\n")
            f.write("|------|------|--------------|---------------|-----------|----------------|\n")
            for idx, (gene, row) in enumerate(drug_targets.head(10).iterrows(), 1):
                ess = row['mean_lfc']
                expr = row.get('log2fc', 0)
                drugs = int(row.get('n_drugs', 0))
                priority = row['priority_score']
                f.write(f"| {idx} | {gene} | {ess:.3f} | {expr:.2f} | {drugs} | {priority:.3f} |\n")
            f.write("\n")

        # Methods
        f.write("## Methods\n\n")
        f.write("**sgRNA Processing**: MAGeCK-like robust rank aggregation\n\n")
        f.write("**Normalization**: Median ratio normalization\n\n")
        f.write("**Scoring**: Gene-level LFC aggregation with rank-based scoring\n\n")
        f.write("**Enrichment**: Enrichr (KEGG, GO)\n\n")
        f.write("**Druggability**: DGIdb v4.0\n\n")

    print(f"Report saved to {output_file}")
    return output_file

# Generate report
# report_file = generate_crispr_report(gene_scores, enrichment_results, drug_targets)
```

## Advanced Use Cases

### Use Case 1: Genome-Wide Essentiality Screen

```python
# Load counts and design
counts, meta = load_sgrna_counts("genome_wide_screen.txt")
design = create_design_matrix(
    sample_names=['T0_1', 'T0_2', 'T14_1', 'T14_2', 'T14_3'],
    conditions=['baseline', 'baseline', 'treatment', 'treatment', 'treatment']
)

# QC and filter
qc_results = qc_sgrna_distribution(counts)
filtered_counts, filtered_mapping = filter_low_count_sgrnas(counts, meta['sgrna_to_gene'])

# Normalize
norm_counts, size_factors = normalize_counts(filtered_counts, method='median')

# Calculate LFC
lfc, control_mean, treatment_mean = calculate_lfc(norm_counts, design)

# Gene-level scoring
gene_scores = mageck_gene_scoring(lfc, filtered_mapping, method='rra')

# Enrichment
enrichment = enrich_essential_genes(gene_scores, top_n=100)

# Report
report = generate_crispr_report(gene_scores, enrichment, None)
```

### Use Case 2: Synthetic Lethality Screen (KRAS)

```python
# Run screens in both KRAS-wildtype and KRAS-mutant cells
# Load both datasets
counts_wt, meta_wt = load_sgrna_counts("kras_wildtype_screen.txt")
counts_mut, meta_mut = load_sgrna_counts("kras_mutant_screen.txt")

# Process both (same steps as Use Case 1)
# ... filtering, normalization, LFC calculation ...

gene_scores_wt = mageck_gene_scoring(lfc_wt, filtered_mapping_wt)
gene_scores_mut = mageck_gene_scoring(lfc_mut, filtered_mapping_mut)

# Identify synthetic lethal hits
sl_hits = detect_synthetic_lethality(gene_scores_wt, gene_scores_mut)

print(f"Identified {len(sl_hits)} synthetic lethal candidates with KRAS mutation")
print(sl_hits.head(10))

# Prioritize for drug development
drug_targets = prioritize_drug_targets(sl_hits)
```

### Use Case 3: Drug Target Discovery Pipeline

```python
# Complete pipeline: Screen → Essential genes → Druggability → Drug candidates

# 1. Identify essential genes from screen
gene_scores = mageck_gene_scoring(lfc, filtered_mapping)

# 2. Filter for highly essential (stringent threshold)
highly_essential = gene_scores[gene_scores['mean_lfc'] < -1.5]

# 3. Prioritize with expression data (if available)
drug_targets = prioritize_drug_targets(highly_essential, expression_data=tumor_expression)

# 4. Find existing drugs
drug_candidates = find_drugs_for_targets(drug_targets.index.tolist())

# 5. Generate comprehensive report
report = generate_crispr_report(gene_scores, None, drug_targets)

print(f"Identified {len(drug_candidates)} druggable targets with {sum(len(v) for v in drug_candidates.values())} total drug candidates")
```

### Use Case 4: Integration with Expression Data

```python
# Combine CRISPR essentiality with RNA-seq differential expression

# Load RNA-seq results (from tooluniverse-rnaseq-deseq2 skill)
rna_results = pd.read_csv("deseq2_results.csv", index_col=0)

# Merge with CRISPR scores
integrated = gene_scores.merge(
    rna_results[['log2FoldChange', 'padj']],
    left_index=True,
    right_index=True,
    how='inner'
)

# Identify genes that are:
# 1. Essential in screen (LFC < -1)
# 2. Overexpressed in disease (log2FC > 1, padj < 0.05)
targets = integrated[
    (integrated['mean_lfc'] < -1) &
    (integrated['log2FoldChange'] > 1) &
    (integrated['padj'] < 0.05)
]

print(f"Identified {len(targets)} genes essential and overexpressed in disease")
```

## ToolUniverse Tool Integration

**Key Tools Used**:
- `PubMed_search` - Literature search for gene essentiality
- `Enrichr_submit_genelist` - Pathway enrichment submission
- `Enrichr_get_results` - Retrieve enrichment results
- `DGIdb_query_gene` - Drug-gene interactions and druggability
- `STRING_get_network` - Protein interaction networks
- `KEGG_get_pathway` - Pathway visualization

**Expression Integration**:
- `GEO_get_dataset` - Download expression data
- `ArrayExpress_get_experiment` - Alternative expression source

**Variant Integration**:
- `ClinVar_query_gene` - Known pathogenic variants
- `gnomAD_get_gene` - Population allele frequencies

## Best Practices

1. **sgRNA Design Quality**: Ensure library uses validated sgRNA designs (e.g., Brunello, Avana libraries)

2. **Replicates**: Minimum 2 biological replicates per condition; 3+ preferred

3. **Sequencing Depth**: Aim for 500-1000 reads per sgRNA at T0; 200+ at final timepoint

4. **Reference Genes**: Include positive (essential) and negative (non-essential) control genes

5. **Timepoint Selection**: Balance cell doublings (14-21 days) vs. sgRNA dropout

6. **Normalization**: Use median ratio normalization for count data (more robust than CPM)

7. **Multiple Testing**: Apply FDR correction when calling essential genes (padj < 0.05)

8. **Validation**: Validate top hits with orthogonal methods (siRNA, small molecule inhibitors)

9. **Context Matters**: Gene essentiality is context-dependent (cell line, tissue, genetic background)

10. **Druggability**: Essential genes are not always druggable; check DGIdb early in prioritization

## Troubleshooting

**Problem**: Low library representation (many zero-count sgRNAs)
- **Solution**: Increase sequencing depth; check for PCR biases in library prep

**Problem**: High Gini coefficient (skewed distribution)
- **Solution**: Optimize PCR cycles; consider using unique molecular identifiers (UMIs)

**Problem**: No strong essential genes detected
- **Solution**: Check timepoint (may be too early); verify cell viability; confirm sgRNA cutting efficiency

**Problem**: Too many essential genes (>500)
- **Solution**: Timepoint may be too late; adjust LFC threshold; check for batch effects

**Problem**: Discordant sgRNAs for same gene
- **Solution**: Check for off-target effects; verify sgRNA sequences; consider removing outlier sgRNAs

## References

- Li W, et al. (2014) MAGeCK enables robust identification of essential genes from genome-scale CRISPR/Cas9 knockout screens. Genome Biology
- Hart T, et al. (2015) High-Resolution CRISPR Screens Reveal Fitness Genes and Genotype-Specific Cancer Liabilities. Cell
- Meyers RM, et al. (2017) Computational correction of copy number effect improves specificity of CRISPR-Cas9 essentiality screens. Nature Genetics
- Tsherniak A, et al. (2017) Defining a Cancer Dependency Map. Cell (DepMap)

## Quick Start

```python
# Complete minimal workflow
import pandas as pd
from tooluniverse import ToolUniverse

# 1. Load data
counts, meta = load_sgrna_counts("sgrna_counts.txt")
design = create_design_matrix(['T0_1', 'T0_2', 'T14_1', 'T14_2'],
                               ['baseline', 'baseline', 'treatment', 'treatment'])

# 2. Process
filtered_counts, filtered_mapping = filter_low_count_sgrnas(counts, meta['sgrna_to_gene'])
norm_counts, _ = normalize_counts(filtered_counts)
lfc, _, _ = calculate_lfc(norm_counts, design)

# 3. Score genes
gene_scores = mageck_gene_scoring(lfc, filtered_mapping)

# 4. Enrich pathways
enrichment = enrich_essential_genes(gene_scores, top_n=100)

# 5. Find drug targets
drug_targets = prioritize_drug_targets(gene_scores)

# 6. Generate report
report = generate_crispr_report(gene_scores, enrichment, drug_targets)
```
