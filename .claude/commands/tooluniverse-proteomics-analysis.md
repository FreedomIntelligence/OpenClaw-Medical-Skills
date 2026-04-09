# tooluniverse-proteomics-analysis

> Analyze mass spectrometry proteomics data including protein quantification, differential expression, post-translational modifications (PTMs), and protein-protein interactions. Processes MaxQuant, Spectronaut, DIA-NN, and other MS platform outputs. Performs normalization, statistical analysis, pathway enrichment, and integration with transcriptomics. Use when analyzing proteomics data, comparing protein abundance between conditions, identifying PTM changes, studying protein complexes, integrating protein and RNA data, discovering protein biomarkers, or conducting quantitative proteomics experiments.

# Proteomics Analysis

Comprehensive analysis of mass spectrometry-based proteomics data from protein identification through quantification, differential expression, post-translational modifications, and systems-level interpretation.

## When to Use This Skill

**Triggers**:
- User has proteomics data (MS output files)
- Questions about protein abundance or expression
- Differential protein expression analysis requests
- PTM analysis (phosphorylation, acetylation, ubiquitination)
- Protein-RNA correlation analysis
- Multi-omics integration involving proteomics
- Protein complex or interaction analysis
- Proteomics biomarker discovery

**Example Questions This Skill Solves**:
1. "Analyze this MaxQuant output for differential protein expression"
2. "Which proteins are significantly upregulated in disease vs control?"
3. "Correlate protein abundance with mRNA expression"
4. "What post-translational modifications change between conditions?"
5. "Identify protein complexes in my co-IP MS data"
6. "Which pathways are enriched in differentially expressed proteins?"
7. "Find protein biomarkers for disease classification"
8. "Compare protein and RNA levels to identify translation-regulated genes"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Import** | MaxQuant, Spectronaut, DIA-NN, Proteome Discoverer, FragPipe outputs |
| **Quality Control** | Missing value analysis, intensity distributions, sample clustering |
| **Normalization** | Median, quantile, TMM, VSN normalization methods |
| **Imputation** | MinProb, KNN, QRILC for missing values |
| **Differential Expression** | Limma, DEP, MSstats for statistical testing |
| **PTM Analysis** | Phospho-site localization, PTM enrichment, kinase prediction |
| **Protein-RNA Integration** | Correlation analysis, translation efficiency |
| **Pathway Enrichment** | Over-representation and GSEA for protein sets |
| **PPI Analysis** | Protein complex detection, interaction networks via STRING/IntAct |
| **Reporting** | Comprehensive reports with volcano plots, heatmaps, pathway diagrams |

---

## Workflow Overview

```
Input: MS Proteomics Data
    |
    v
Phase 1: Data Import & QC
    |-- Load MaxQuant/Spectronaut/DIA-NN output
    |-- Parse protein groups, intensities, modifications
    |-- Quality control plots (missing values, intensity distributions)
    |-- Sample correlation and PCA
    |
    v
Phase 2: Preprocessing
    |-- Filter low-confidence proteins
    |-- Handle missing values (imputation or filtering)
    |-- Log-transform intensities
    |-- Normalize across samples
    |
    v
Phase 3: Differential Expression Analysis
    |-- Statistical testing (limma, t-test, ANOVA)
    |-- Multiple testing correction (BH, Bonferroni)
    |-- Fold change calculation
    |-- Significance thresholds (p < 0.05, |log2FC| > 1)
    |
    v
Phase 4: PTM Analysis (if applicable)
    |-- Identify modified peptides
    |-- Localization probability filtering
    |-- PTM site quantification
    |-- Kinase-substrate prediction
    |-- PTM enrichment analysis
    |
    v
Phase 5: Functional Enrichment
    |-- Gene Ontology enrichment
    |-- KEGG/Reactome pathway enrichment
    |-- Protein complex enrichment (CORUM)
    |-- Tissue-specific enrichment
    |
    v
Phase 6: Protein-Protein Interactions
    |-- Query STRING for interaction networks
    |-- Identify protein complexes
    |-- Network clustering and modules
    |-- Hub protein identification
    |
    v
Phase 7: Multi-Omics Integration (optional)
    |-- Correlate with RNA-seq data
    |-- Identify translation-regulated proteins
    |-- Compare with variant/CNV data
    |-- Integrate with metabolomics
    |
    v
Phase 8: Generate Report
    |-- Summary statistics
    |-- Volcano plots and heatmaps
    |-- Pathway diagrams
    |-- Protein network visualizations
    |-- Multi-omics integration plots
```

---

## Phase Details

### Phase 1: Data Import & Quality Control

**Objective**: Load proteomics data and assess data quality.

**Supported input formats**:

**MaxQuant (most common)**:
- `proteinGroups.txt` - Protein-level quantification
- `evidence.txt` - Peptide-level data
- `Phospho (STY)Sites.txt` - Phosphorylation sites
- `modificationSpecificPeptides.txt` - Other PTMs

**Spectronaut**:
- `*_Report.tsv` - Protein/peptide quantification
- DIA-based quantification

**DIA-NN**:
- `report.tsv` - Protein groups
- `report.pr_matrix.tsv` - Protein matrix

**Proteome Discoverer**:
- `*_Proteins.txt`
- `*_PSMs.txt`

**Data loading**:
```python
def load_maxquant_proteins(protein_groups_file):
    """
    Load MaxQuant proteinGroups.txt file.

    Returns:
    - DataFrame with proteins as rows, samples as columns
    - Metadata (protein names, gene names, sequence coverage)
    """
    import pandas as pd

    # Read file
    df = pd.read_csv(protein_groups_file, sep='\t')

    # Extract intensity columns (LFQ or raw)
    intensity_cols = [col for col in df.columns if 'LFQ intensity' in col or 'Intensity ' in col]

    # Create intensity matrix
    intensity_matrix = df[intensity_cols].copy()
    intensity_matrix.columns = [col.replace('LFQ intensity ', '').replace('Intensity ', '')
                                 for col in intensity_cols]

    # Add protein metadata
    metadata = df[['Protein IDs', 'Gene names', 'Fasta headers',
                   'Peptides', 'Sequence coverage [%]']].copy()

    return intensity_matrix, metadata
```

**Quality Control**:

1. **Missing value assessment**:
```python
def assess_missing_values(intensity_matrix):
    """
    Calculate percentage of missing values per protein and sample.
    """
    # Per protein
    missing_per_protein = (intensity_matrix == 0).sum(axis=1) / intensity_matrix.shape[1]

    # Per sample
    missing_per_sample = (intensity_matrix == 0).sum(axis=0) / intensity_matrix.shape[0]

    # Visualize
    plot_missing_value_heatmap(intensity_matrix)

    return missing_per_protein, missing_per_sample
```

2. **Intensity distribution**:
```python
def plot_intensity_distributions(intensity_matrix):
    """
    Plot log10 intensity distributions per sample.
    Check for consistent distributions across samples.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    log_intensities = np.log10(intensity_matrix.replace(0, np.nan))

    # Boxplot per sample
    log_intensities.plot(kind='box')
    plt.ylabel('log10 Intensity')
    plt.title('Intensity Distribution per Sample')

    # Should see similar median and spread across samples
```

3. **Sample correlation**:
```python
def plot_sample_correlation(intensity_matrix):
    """
    Calculate and visualize sample-sample correlation.
    Expect: High correlation within replicates, lower between conditions.
    """
    # Log-transform and remove zeros
    log_data = np.log2(intensity_matrix.replace(0, np.nan))

    # Correlation matrix
    corr_matrix = log_data.corr(method='pearson')

    # Heatmap
    import seaborn as sns
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', vmin=0.8, vmax=1.0)
```

4. **PCA**:
```python
def perform_pca(intensity_matrix, sample_groups):
    """
    Principal component analysis for sample clustering.
    """
    from sklearn.decomposition import PCA

    # Prepare data (log, impute, scale)
    log_data = np.log2(intensity_matrix.replace(0, np.nan))
    # Simple imputation with minimum value
    imputed = log_data.fillna(log_data.min().min())

    # PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(imputed.T)

    # Plot with group colors
    plt.scatter(pca_result[:, 0], pca_result[:, 1], c=sample_groups)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
```

### Phase 2: Preprocessing & Normalization

**Objective**: Clean data and normalize across samples for fair comparison.

**Filtering**:
```python
def filter_proteins(intensity_matrix, metadata, min_valid=3):
    """
    Filter out low-confidence proteins.

    Criteria:
    - At least 2 unique peptides (from metadata)
    - At least min_valid samples with detected intensity
    - Remove contaminants and reverse sequences
    """
    # Filter by peptide count
    valid_proteins = metadata['Peptides'] >= 2

    # Filter by detection in samples
    n_detected = (intensity_matrix > 0).sum(axis=1)
    valid_detection = n_detected >= min_valid

    # Remove contaminants (from MaxQuant)
    is_contaminant = metadata['Protein IDs'].str.contains('CON__', na=False)
    is_reverse = metadata['Protein IDs'].str.contains('REV__', na=False)

    # Combined filter
    keep = valid_proteins & valid_detection & ~is_contaminant & ~is_reverse

    return intensity_matrix[keep], metadata[keep]
```

**Missing value imputation**:
```python
def impute_missing_values(intensity_matrix, method='MinProb'):
    """
    Impute missing protein intensities.

    Methods:
    - MinProb: Random from minimum observed + normal noise (for MNAR)
    - KNN: K-nearest neighbors imputation
    - QRILC: Quantile regression-based imputation
    """
    if method == 'MinProb':
        # Assume missing = low abundance (MNAR assumption)
        min_val = intensity_matrix[intensity_matrix > 0].min().min()
        width = 0.3  # Standard deviation of noise
        shift = 1.8  # Downshift from minimum

        # Replace zeros with random low values
        imputed = intensity_matrix.copy()
        missing_mask = imputed == 0
        n_missing = missing_mask.sum().sum()

        random_vals = np.random.normal(
            loc=min_val - shift,
            scale=width,
            size=n_missing
        )
        imputed.values[missing_mask.values] = random_vals

        return imputed

    elif method == 'KNN':
        from sklearn.impute import KNNImputer
        imputer = KNNImputer(n_neighbors=5)
        imputed = pd.DataFrame(
            imputer.fit_transform(intensity_matrix.replace(0, np.nan)),
            index=intensity_matrix.index,
            columns=intensity_matrix.columns
        )
        return imputed
```

**Normalization**:
```python
def normalize_intensities(intensity_matrix, method='median'):
    """
    Normalize protein intensities across samples.

    Methods:
    - median: Divide by median intensity per sample
    - quantile: Quantile normalization (same distribution)
    - TMM: Trimmed mean of M-values (from edgeR)
    - VSN: Variance-stabilizing normalization
    """
    if method == 'median':
        # Median normalization
        medians = intensity_matrix.median(axis=0)
        global_median = medians.median()
        norm_factors = global_median / medians
        normalized = intensity_matrix * norm_factors
        return normalized

    elif method == 'quantile':
        # Quantile normalization
        from sklearn.preprocessing import quantile_transform
        normalized = pd.DataFrame(
            quantile_transform(intensity_matrix, axis=1),
            index=intensity_matrix.index,
            columns=intensity_matrix.columns
        )
        return normalized
```

### Phase 3: Differential Expression Analysis

**Objective**: Identify proteins with significant abundance changes between conditions.

**Statistical testing with limma**:
```python
def differential_expression_limma(log2_intensities, group1_samples, group2_samples):
    """
    Perform differential expression using limma-like approach.

    Returns:
    - log2 fold changes
    - p-values
    - adjusted p-values (BH)
    """
    from scipy import stats

    results = []

    for protein in log2_intensities.index:
        # Extract intensities for each group
        group1 = log2_intensities.loc[protein, group1_samples]
        group2 = log2_intensities.loc[protein, group2_samples]

        # Calculate statistics
        mean1 = group1.mean()
        mean2 = group2.mean()
        log2fc = mean2 - mean1

        # t-test
        t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)

        results.append({
            'protein': protein,
            'log2FC': log2fc,
            'mean_group1': mean1,
            'mean_group2': mean2,
            'p_value': p_value,
            't_statistic': t_stat
        })

    results_df = pd.DataFrame(results)

    # Multiple testing correction (Benjamini-Hochberg)
    from statsmodels.stats.multitest import multipletests
    results_df['adj_p_value'] = multipletests(results_df['p_value'], method='fdr_bh')[1]

    # Classify significance
    results_df['significant'] = (
        (results_df['adj_p_value'] < 0.05) &
        (np.abs(results_df['log2FC']) > 1.0)
    )

    return results_df
```

**Volcano plot**:
```python
def plot_volcano(de_results, title='Volcano Plot'):
    """
    Visualize differential expression results.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 6))

    # Non-significant
    non_sig = de_results[~de_results['significant']]
    plt.scatter(non_sig['log2FC'], -np.log10(non_sig['p_value']),
                c='gray', alpha=0.5, s=10)

    # Significant
    sig = de_results[de_results['significant']]
    plt.scatter(sig['log2FC'], -np.log10(sig['p_value']),
                c='red', alpha=0.7, s=20)

    # Thresholds
    plt.axhline(-np.log10(0.05), color='blue', linestyle='--', label='p=0.05')
    plt.axvline(-1, color='blue', linestyle='--')
    plt.axvline(1, color='blue', linestyle='--', label='|log2FC|=1')

    plt.xlabel('log2 Fold Change')
    plt.ylabel('-log10(p-value)')
    plt.title(title)
    plt.legend()
```

### Phase 4: PTM Analysis

**Objective**: Analyze post-translational modifications (phosphorylation, acetylation, etc.)

**Phosphoproteomics workflow**:
```python
def analyze_phosphosites(phospho_sites_file, intensity_matrix):
    """
    Analyze phosphorylation site changes.

    Input: MaxQuant Phospho (STY)Sites.txt
    Output: Differential phosphorylation per site
    """
    # Load phospho data
    phospho = pd.read_csv(phospho_sites_file, sep='\t')

    # Filter by localization probability
    phospho_confident = phospho[phospho['Localization prob'] > 0.75]

    # Extract site information
    phospho_confident['site'] = (
        phospho_confident['Gene names'] + '_' +
        phospho_confident['Amino acid'] +
        phospho_confident['Position'].astype(str)
    )

    # Quantification (similar to protein-level analysis)
    # ... perform differential analysis ...

    return phospho_results
```

**Kinase-substrate prediction**:
```python
def predict_kinases(phospho_sites):
    """
    Predict upstream kinases for phosphorylation sites.

    Uses ToolUniverse PhosphoSitePlus or KEA3 tools.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # For each significant phosphosite
    kinase_predictions = []
    for site in phospho_sites:
        # Query kinase-substrate databases
        # (would use actual ToolUniverse tool here)
        result = tu.run_one_function({
            "name": "phosphosite_plus_query",  # hypothetical
            "arguments": {"site": site}
        })
        kinase_predictions.append(result)

    return kinase_predictions
```

### Phase 5: Functional Enrichment

**Objective**: Interpret biological meaning of protein changes via pathway analysis.

**Gene Ontology enrichment**:
```python
def pathway_enrichment_proteins(de_proteins, organism='human'):
    """
    Perform pathway enrichment for differentially expressed proteins.

    Uses ToolUniverse gene-enrichment skill.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Extract gene names for significant proteins
    sig_proteins = de_proteins[de_proteins['significant']]
    gene_list = sig_proteins['gene_name'].tolist()

    # Run enrichment via ToolUniverse
    enrichment = tu.run_one_function({
        "name": "enrichr_enrich",
        "arguments": {
            "gene_list": ",".join(gene_list),
            "library": "KEGG_2021_Human"
        }
    })

    return enrichment
```

**Protein complex enrichment**:
```python
def protein_complex_enrichment(protein_list):
    """
    Test for enrichment of known protein complexes (CORUM database).
    """
    # Query CORUM or use ToolUniverse
    # Identify if proteins are part of known complexes
    pass
```

### Phase 6: Protein-Protein Interactions

**Objective**: Identify interaction networks and protein complexes.

**STRING network analysis**:
```python
def build_protein_network(protein_list, confidence=0.7):
    """
    Build PPI network using STRING database.

    Uses ToolUniverse STRING tools.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Get interactions
    interactions = tu.run_one_function({
        "name": "string_get_interactions",
        "arguments": {
            "proteins": ",".join(protein_list),
            "species": 9606,  # human
            "score_threshold": int(confidence * 1000)
        }
    })

    # Build network graph
    import networkx as nx
    G = nx.Graph()

    for interaction in interactions['data']:
        G.add_edge(
            interaction['protein1'],
            interaction['protein2'],
            score=interaction['score']
        )

    return G
```

**Module detection**:
```python
def detect_protein_modules(network_graph):
    """
    Identify tightly connected protein modules (complexes).
    """
    from networkx.algorithms import community

    # Detect communities
    communities = community.greedy_modularity_communities(network_graph)

    # Annotate modules with enriched functions
    modules = []
    for i, comm in enumerate(communities):
        module_proteins = list(comm)
        # Run enrichment for this module
        enrichment = pathway_enrichment_proteins(module_proteins)
        modules.append({
            'module_id': i,
            'proteins': module_proteins,
            'size': len(module_proteins),
            'top_function': enrichment['top_terms'][0]
        })

    return modules
```

### Phase 7: Multi-Omics Integration

**Objective**: Integrate proteomics with transcriptomics and other omics.

**Protein-RNA correlation**:
```python
def correlate_protein_rna(protein_data, rna_data, common_samples):
    """
    Correlate protein and mRNA levels for each gene.

    Expected: r ~ 0.4-0.6 (moderate correlation)
    Discordance indicates post-transcriptional regulation
    """
    from scipy.stats import spearmanr

    # Find common genes
    common_genes = set(protein_data.index) & set(rna_data.index)

    correlations = {}
    for gene in common_genes:
        protein = protein_data.loc[gene, common_samples]
        rna = rna_data.loc[gene, common_samples]

        r, p = spearmanr(protein, rna)
        correlations[gene] = {
            'r': r,
            'p': p,
            'regulation': classify_regulation(r, protein.mean(), rna.mean())
        }

    return correlations

def classify_regulation(r, protein_level, rna_level):
    """
    Classify regulatory mechanism based on correlation and levels.
    """
    if r > 0.6 and protein_level > 0 and rna_level > 0:
        return 'transcriptional_upregulation'
    elif r > 0.6 and protein_level < 0 and rna_level < 0:
        return 'transcriptional_downregulation'
    elif r < 0.2 and protein_level > 0 and rna_level < 0:
        return 'translational_upregulation'
    elif r < 0.2 and protein_level < 0 and rna_level > 0:
        return 'protein_degradation'
    else:
        return 'mixed_regulation'
```

**Integration with multi-omics skill**:
```python
def integrate_with_multiomics(protein_data, rna_data, methylation_data):
    """
    Pass proteomics data to multi-omics integration skill.

    Enables comprehensive analysis across all molecular layers.
    """
    # Prepare for multi-omics skill
    omics_data = {
        'proteomics': protein_data,
        'rnaseq': rna_data,
        'methylation': methylation_data
    }

    # Invoke multi-omics integration skill
    from tooluniverse import ToolUniverse
    # (Would use Skill tool to invoke tooluniverse-multi-omics-integration)

    return integrated_analysis
```

### Phase 8: Report Generation

**Generate comprehensive proteomics report**:

```markdown
# Proteomics Analysis Report

## Dataset Summary
- **Samples**: 20 (10 disease, 10 control)
- **Proteins Identified**: 5,432
- **Proteins Quantified**: 4,987 (at least 3 samples)
- **Platform**: Orbitrap Fusion Lumos, MaxQuant 2.0

## Quality Control
- **Missing Values**: 15% average per protein
- **Sample Correlation**: 0.92-0.98 within groups
- **PCA**: Clear separation between disease and control (PC1: 35% variance)

## Differential Expression
- **Significant Proteins**: 432 (adj. p < 0.05, |log2FC| > 1)
  - Upregulated: 245 proteins
  - Downregulated: 187 proteins
- **Top upregulated**: MYC (log2FC=3.2), EGFR (log2FC=2.8)
- **Top downregulated**: TP53 (log2FC=-2.5), BRCA1 (log2FC=-2.1)

## Phosphoproteomics
- **Phosphosites Quantified**: 8,543
- **Differentially Phosphorylated**: 234 sites (p < 0.05)
- **Top Predicted Kinases**: CDK1, MAPK1, AKT1

## Pathway Enrichment
### Top Pathways (Upregulated)
1. **Cell Cycle** (p=1e-15) - 45 proteins, including cyclins, CDKs
2. **DNA Replication** (p=1e-12) - 23 proteins
3. **Glycolysis** (p=1e-10) - 18 proteins

### Top Pathways (Downregulated)
1. **Apoptosis** (p=1e-14) - 32 proteins, including caspases
2. **DNA Repair** (p=1e-11) - 28 proteins
3. **Oxidative Phosphorylation** (p=1e-9) - 25 proteins

## Protein Network Analysis
- **Network**: 432 nodes, 1,245 edges (STRING confidence > 0.7)
- **Modules Detected**: 8 functional modules
  - Module 1: Cell cycle (85 proteins)
  - Module 2: Metabolism (62 proteins)
  - Module 3: Translation (48 proteins)

## Protein-RNA Correlation
- **Overall Correlation**: r = 0.54 (moderate, expected)
- **High Correlation**: 2,134 genes (r > 0.6) - transcriptional regulation
- **Low Correlation**: 456 genes (r < 0.2) - post-transcriptional regulation
- **Translation-Regulated**: 89 proteins (high protein, low RNA)

## Biological Interpretation
Disease state shows increased proliferation (MYC, cyclins) with concurrent
suppression of apoptosis and DNA repair (TP53, BRCA1). Metabolic shift toward
glycolysis evident at protein level. Post-transcriptional upregulation of
translation machinery suggests adaptation to proliferative demands.

## Potential Biomarkers
Top 10 proteins for disease classification (Random Forest AUC=0.95):
1. MYC (protein)
2. EGFR (protein)
3. CDK1 (phospho-T161)
4. TP53 (protein)
5. BRCA1 (protein)
```

---

## Integration with ToolUniverse

**Skills Coordinated**:
| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-gene-enrichment` | Pathway enrichment | Phase 5 |
| `tooluniverse-protein-interactions` | PPI networks | Phase 6 |
| `tooluniverse-rnaseq-deseq2` | RNA-seq for integration | Phase 7 |
| `tooluniverse-multi-omics-integration` | Cross-omics analysis | Phase 7 |
| `tooluniverse-target-research` | Protein annotation | Phase 8 |

---

## Example Use Cases

### Use Case 1: Cancer Proteomics

**Question**: "Analyze proteomics data from breast cancer vs normal tissue"

**Workflow**:
1. Load MaxQuant proteinGroups.txt
2. QC and filter (keep proteins with 2+ peptides, detected in 3+ samples)
3. Impute missing, normalize by median
4. Differential expression (limma): 432 significant proteins
5. Pathway enrichment: Cell cycle, metabolism upregulated
6. STRING network: Identify hub proteins (MYC, EGFR)
7. Integrate with TCGA RNA-seq: Find translation-regulated genes
8. Report: Comprehensive analysis with biomarkers

### Use Case 2: Phosphoproteomics Signaling

**Question**: "What kinase signaling is activated in response to drug treatment?"

**Workflow**:
1. Load Phospho (STY)Sites.txt from MaxQuant
2. Filter by localization probability > 0.75
3. Differential phosphorylation analysis
4. Kinase prediction for significant sites
5. Identify MAPK1, CDK1, AKT1 as top kinases
6. Pathway enrichment: MAPK, PI3K/AKT pathways
7. Report: Drug activates growth signaling

### Use Case 3: Protein-RNA Integration

**Question**: "Which proteins are regulated post-transcriptionally?"

**Workflow**:
1. Load proteomics (MaxQuant) and RNA-seq (DESeq2) data
2. Match samples, extract common genes
3. Correlate protein and RNA for each gene
4. Identify low-correlation genes (r < 0.2)
5. Classify: translation upregulation, protein degradation
6. Enrichment: Find pathways enriched in post-transcriptional regulation
7. Report: 89 translation-regulated proteins, RNA-binding proteins enriched

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Proteins quantified | At least 500 proteins |
| Replicates | At least 3 per condition |
| Filtering | 2+ unique peptides per protein |
| Statistical test | limma or t-test with multiple testing correction |
| Pathway enrichment | At least one method (GO, KEGG, or Reactome) |
| Report | Summary, QC, DE results, pathways, visualizations |

---

## Limitations

- **Platform-specific**: Optimized for MS-based proteomics (not Western blot quantification)
- **Missing values**: High missing rate (>50% per protein) limits statistical power
- **PTM analysis**: Requires enrichment protocols for comprehensive PTM profiling
- **Absolute quantification**: Relative abundance only (unless TMT/SILAC used)
- **Protein isoforms**: Typically collapsed to gene level
- **Dynamic range**: MS has limited dynamic range vs mRNA sequencing

---

## References

**Methods**:
- MaxQuant: https://doi.org/10.1038/nbt.1511
- Limma for proteomics: https://doi.org/10.1093/nar/gkv007
- DEP workflow: https://doi.org/10.1038/nprot.2018.107

**Databases**:
- STRING: https://string-db.org
- PhosphoSitePlus: https://www.phosphosite.org
- CORUM: https://mips.helmholtz-muenchen.de/corum
