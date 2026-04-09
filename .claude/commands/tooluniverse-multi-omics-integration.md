# tooluniverse-multi-omics-integration

> Integrate and analyze multiple omics datasets (transcriptomics, proteomics, epigenomics, genomics, metabolomics) for systems biology and precision medicine. Performs cross-omics correlation, multi-omics clustering (MOFA+, NMF), pathway-level integration, and sample matching. Coordinates ToolUniverse skills for expression data (RNA-seq), epigenomics (methylation, ChIP-seq), variants (SNVs, CNVs), protein interactions, and pathway enrichment. Use when analyzing multi-omics datasets, performing integrative analysis, discovering multi-omics biomarkers, studying disease mechanisms across molecular layers, or conducting systems biology research that requires coordinated analysis of transcriptome, genome, epigenome, proteome, and metabolome data.

# Multi-Omics Integration

Coordinate and integrate multiple omics datasets for comprehensive systems biology analysis. This skill orchestrates specialized ToolUniverse skills to perform cross-omics correlation, multi-omics clustering, pathway-level integration, and unified interpretation across molecular layers.

## When to Use This Skill

**Triggers**:
- User has multiple omics datasets (RNA-seq + proteomics, methylation + expression, etc.)
- Requests for integrative multi-omics analysis
- Cross-omics correlation queries (e.g., "How does methylation affect expression?")
- Multi-omics biomarker discovery
- Systems biology questions requiring multiple molecular layers
- Precision medicine applications with multi-omics patient data
- Questions about molecular mechanisms across omics types

**Example Questions This Skill Solves**:
1. "Integrate RNA-seq and proteomics data to find genes with concordant changes"
2. "How does promoter methylation correlate with gene expression?"
3. "Perform multi-omics clustering to identify patient subtypes"
4. "Which pathways are dysregulated across transcriptome, proteome, and metabolome?"
5. "Find multi-omics biomarkers for disease classification"
6. "Correlate CNV with gene expression to identify dosage effects"
7. "Integrate GWAS variants, eQTLs, and expression data"
8. "Perform MOFA+ analysis on multi-omics cancer data"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Integration** | Match samples across omics, handle missing data, normalize scales |
| **Cross-Omics Correlation** | Correlate features across molecular layers (gene expression vs protein, methylation vs expression) |
| **Multi-Omics Clustering** | MOFA+, NMF, joint clustering to identify omics-driven subtypes |
| **Pathway Integration** | Combine omics evidence at pathway level for unified biological interpretation |
| **Biomarker Discovery** | Identify multi-omics signatures with improved predictive power |
| **Skill Coordination** | Orchestrate RNA-seq, epigenomics, variant-analysis, protein-interactions, gene-enrichment skills |
| **Visualization** | Circos plots, integrated heatmaps, network visualizations |
| **Reporting** | Unified multi-omics reports with cross-layer insights |

---

## Workflow Overview

```
Input: Multiple Omics Datasets
    |
    v
Phase 1: Data Loading & QC
    |-- Load RNA-seq (expression matrix)
    |-- Load proteomics (protein abundance)
    |-- Load methylation (beta values or M-values)
    |-- Load variants (CNV, SNV from VCF)
    |-- Load metabolomics (metabolite abundance)
    |-- Quality control per omics type
    |
    v
Phase 2: Sample Matching
    |-- Match samples across omics by ID
    |-- Identify common samples
    |-- Handle batch effects
    |-- Normalize sample identifiers
    |
    v
Phase 3: Feature Mapping
    |-- Map features to common identifier space (genes, proteins, metabolites)
    |-- Link CpG sites to genes (promoter, gene body)
    |-- Map variants to genes
    |-- Create unified feature matrix
    |
    v
Phase 4: Cross-Omics Correlation
    |-- Gene expression vs protein abundance (translation efficiency)
    |-- Promoter methylation vs expression (epigenetic regulation)
    |-- CNV vs expression (dosage effect)
    |-- eQTL variants vs expression (genetic regulation)
    |-- Metabolite vs enzyme expression (metabolic flux)
    |
    v
Phase 5: Multi-Omics Clustering
    |-- MOFA+ (Multi-Omics Factor Analysis) for latent factors
    |-- NMF (Non-negative Matrix Factorization) for patient subtypes
    |-- Joint clustering across omics
    |-- Identify omics-specific vs shared variation
    |
    v
Phase 6: Pathway-Level Integration
    |-- Aggregate omics to pathway level
    |-- Score pathway dysregulation (combined evidence)
    |-- Use ToolUniverse enrichment tools (Reactome, KEGG, GO)
    |-- Identify driver pathways across omics
    |
    v
Phase 7: Biomarker Discovery
    |-- Feature selection across omics
    |-- Multi-omics signatures for classification
    |-- Cross-validation and performance
    |-- Interpretation and biological validation
    |
    v
Phase 8: Generate Integrated Report
    |-- Summary statistics per omics
    |-- Cross-omics correlation results
    |-- Multi-omics clusters and subtypes
    |-- Top dysregulated pathways
    |-- Multi-omics biomarkers
    |-- Biological interpretation
```

---

## Phase Details

### Phase 1: Data Loading & Quality Control

**Objective**: Load multiple omics datasets and perform quality control.

**Supported omics types**:
- **Transcriptomics**: RNA-seq count matrices, microarray
- **Proteomics**: Protein abundance (MS-based)
- **Epigenomics**: Methylation (450K, EPIC arrays, WGBS), ChIP-seq peaks
- **Genomics**: CNV, SNV, structural variants
- **Metabolomics**: Metabolite abundance (targeted, untargeted)

**Data formats**:
- Expression: CSV/TSV matrices, HDF5, AnnData (.h5ad)
- Proteomics: MaxQuant output, Spectronaut, DIA-NN
- Methylation: IDAT files, beta value matrices
- Variants: VCF, SEG files (CNV)
- Metabolomics: Peak tables, identified metabolites

**Quality control per omics**:
```python
# RNA-seq QC
- Filter low-count genes (mean counts < threshold)
- Normalize (TPM, FPKM, or DESeq2)
- Log-transform for correlation

# Proteomics QC
- Filter proteins with high missing values
- Impute missing values (minimum, KNN)
- Normalize (median, quantile)

# Methylation QC
- Remove failed probes
- Correct for batch effects (ComBat)
- Filter cross-reactive probes

# Variants QC
- Use variant-analysis skill for VCF QC
- CNV segmentation validation
```

### Phase 2: Sample Matching

**Objective**: Identify common samples across omics datasets.

**Sample ID harmonization**:
```python
def match_samples_across_omics(omics_data_dict):
    """
    Match samples across multiple omics datasets.

    Parameters:
    omics_data_dict: {
        'rnaseq': DataFrame (genes x samples),
        'proteomics': DataFrame (proteins x samples),
        'methylation': DataFrame (CpGs x samples),
        'cnv': DataFrame (genes x samples)
    }

    Returns:
    - common_samples: List of sample IDs present in all omics
    - matched_data: Dict of DataFrames with common samples only
    """
    # Extract sample IDs from each omics
    sample_ids = {
        omics_type: set(df.columns)
        for omics_type, df in omics_data_dict.items()
    }

    # Find common samples (intersection)
    common_samples = set.intersection(*sample_ids.values())

    # Subset each omics to common samples
    matched_data = {
        omics_type: df[sorted(common_samples)]
        for omics_type, df in omics_data_dict.items()
    }

    return sorted(common_samples), matched_data
```

**Handling missing omics**:
- Pairwise integration if not all samples have all omics
- Document sample availability matrix

### Phase 3: Feature Mapping

**Objective**: Map features from different omics to common gene-level identifiers.

**Gene-centric integration**:
```python
# Map all features to genes
feature_mapping = {
    'rnaseq': 'gene_symbol',  # Already gene-level
    'proteomics': 'gene_symbol',  # Map protein to gene
    'methylation': 'gene_symbol',  # Map CpG to gene (promoter)
    'cnv': 'gene_symbol',  # CNV regions to overlapping genes
    'metabolomics': 'enzyme_gene'  # Metabolite to enzyme gene
}
```

**CpG to gene mapping**:
- **Promoter methylation**: CpGs within TSS ± 2kb
- **Gene body methylation**: CpGs within gene boundaries
- Average methylation per gene (weighted by probe coverage)

**CNV to gene mapping**:
- Use variant-analysis skill to identify genes in CNV regions
- Calculate copy number per gene (log2 ratio)

### Phase 4: Cross-Omics Correlation

**Objective**: Correlate features across molecular layers to understand regulation.

**Example analyses**:

#### 4.1: Expression vs Protein (Translation Efficiency)

```python
def correlate_rna_protein(rnaseq_data, proteomics_data):
    """
    Correlate mRNA and protein levels for each gene.

    Expected: Positive correlation (r ~ 0.4-0.6 typical)
    Discordance indicates post-transcriptional regulation
    """
    # Find common genes
    common_genes = set(rnaseq_data.index) & set(proteomics_data.index)

    correlations = {}
    for gene in common_genes:
        rna = rnaseq_data.loc[gene]
        protein = proteomics_data.loc[gene]

        # Spearman correlation (robust to outliers)
        r, p = spearmanr(rna, protein)
        correlations[gene] = {'r': r, 'p': p}

    # Identify discordant genes (low RNA-protein correlation)
    discordant = {g: v for g, v in correlations.items() if abs(v['r']) < 0.2}

    return correlations, discordant
```

#### 4.2: Methylation vs Expression (Epigenetic Regulation)

```python
def correlate_methylation_expression(methylation_data, rnaseq_data):
    """
    Correlate promoter methylation with gene expression.

    Expected: Negative correlation (increased methylation → decreased expression)
    """
    # For each gene with promoter methylation
    results = {}
    for gene in methylation_data.index:
        if gene in rnaseq_data.index:
            meth = methylation_data.loc[gene]  # Average promoter beta
            expr = rnaseq_data.loc[gene]

            r, p = spearmanr(meth, expr)
            results[gene] = {'r': r, 'p': p, 'direction': 'repressive' if r < 0 else 'activating'}

    # Identify genes with strong methylation-expression anticorrelation
    regulated = {g: v for g, v in results.items() if v['r'] < -0.5 and v['p'] < 0.01}

    return results, regulated
```

#### 4.3: CNV vs Expression (Dosage Effect)

```python
def correlate_cnv_expression(cnv_data, rnaseq_data):
    """
    Correlate copy number with gene expression.

    Expected: Positive correlation (gene dosage effect)
    """
    results = {}
    for gene in cnv_data.index:
        if gene in rnaseq_data.index:
            cnv = cnv_data.loc[gene]  # log2 ratio
            expr = rnaseq_data.loc[gene]

            r, p = pearsonr(cnv, expr)
            results[gene] = {'r': r, 'p': p}

    # Genes with dosage effect (CNV drives expression)
    dosage_genes = {g: v for g, v in results.items() if v['r'] > 0.5 and v['p'] < 0.01}

    return results, dosage_genes
```

### Phase 5: Multi-Omics Clustering

**Objective**: Identify patient subtypes using integrated omics data.

**Method 1: MOFA+ (Multi-Omics Factor Analysis)**

MOFA+ identifies latent factors that explain variation across omics.

```python
# Conceptual workflow (uses R's MOFA2 package or Python implementation)
# 1. Prepare multi-omics data as list of matrices
# 2. Run MOFA+ to identify factors
# 3. Inspect factor variance explained per omics
# 4. Cluster samples based on factor scores

# Example interpretation:
# Factor 1: Explains 40% variance in RNA-seq, 30% in proteomics → Cell proliferation
# Factor 2: Explains 50% variance in methylation → Epigenetic subtype
# Factor 3: Explains 20% variance in CNV → Genomic instability
```

**Method 2: Joint NMF (Non-negative Matrix Factorization)**

Decompose multi-omics matrices into shared latent components.

```python
def joint_nmf_clustering(omics_data_dict, n_clusters=3):
    """
    Perform joint NMF across omics for clustering.

    Returns patient cluster assignments based on shared factors.
    """
    # Concatenate omics matrices (after normalization)
    combined_matrix = np.vstack([
        omics_data_dict['rnaseq'].values,
        omics_data_dict['proteomics'].values,
        omics_data_dict['methylation'].values
    ])

    # Run NMF
    from sklearn.decomposition import NMF
    model = NMF(n_components=n_clusters, init='nndsvd', random_state=42)
    W = model.fit_transform(combined_matrix)  # Feature loadings
    H = model.components_  # Sample coefficients

    # Cluster samples based on H (components)
    from sklearn.cluster import KMeans
    clusters = KMeans(n_clusters=n_clusters).fit_predict(H.T)

    return clusters, W, H
```

**Method 3: Similarity Network Fusion (SNF)**

Integrate omics through patient similarity networks.

### Phase 6: Pathway-Level Integration

**Objective**: Aggregate multi-omics evidence at the pathway level.

**Approach**: Score pathway dysregulation using combined evidence from multiple omics.

```python
def integrate_pathway_evidence(omics_results, pathway_genes):
    """
    Score pathway dysregulation across omics.

    omics_results: {
        'rnaseq': {'gene': fold_change},
        'proteomics': {'gene': fold_change},
        'methylation': {'gene': methylation_diff},
        'cnv': {'gene': copy_number}
    }

    pathway_genes: List of genes in pathway
    """
    # For each gene in pathway
    pathway_scores = []
    for gene in pathway_genes:
        gene_score = 0
        evidence_count = 0

        # RNA-seq evidence
        if gene in omics_results['rnaseq']:
            gene_score += abs(omics_results['rnaseq'][gene])
            evidence_count += 1

        # Proteomics evidence
        if gene in omics_results['proteomics']:
            gene_score += abs(omics_results['proteomics'][gene])
            evidence_count += 1

        # Methylation evidence (negative correlation)
        if gene in omics_results['methylation']:
            gene_score += abs(omics_results['methylation'][gene])
            evidence_count += 1

        # CNV evidence
        if gene in omics_results['cnv']:
            gene_score += abs(omics_results['cnv'][gene])
            evidence_count += 1

        if evidence_count > 0:
            pathway_scores.append(gene_score / evidence_count)

    # Aggregate pathway score (mean of gene scores)
    pathway_score = np.mean(pathway_scores) if pathway_scores else 0

    return {
        'pathway_score': pathway_score,
        'n_genes_with_evidence': len(pathway_scores),
        'n_omics_types': evidence_count
    }
```

**Use ToolUniverse enrichment tools**:
```python
# Get pathways for gene set
from tooluniverse import ToolUniverse
tu = ToolUniverse()

# Enrichment for genes dysregulated in ANY omics
all_dysregulated_genes = set()
all_dysregulated_genes.update(rnaseq_degs)
all_dysregulated_genes.update(diff_proteins)
all_dysregulated_genes.update(methylation_dmgs)

# Run enrichment
enrichment = tu.run_one_function({
    "name": "enrichr_enrich",
    "arguments": {
        "gene_list": ",".join(all_dysregulated_genes),
        "library": "KEGG_2021_Human"
    }
})

# Score each pathway with multi-omics evidence
for pathway in enrichment['data']['results']:
    pathway_genes = pathway['genes']
    pathway['multi_omics_score'] = integrate_pathway_evidence(
        omics_results, pathway_genes
    )
```

### Phase 7: Biomarker Discovery

**Objective**: Identify multi-omics signatures for disease classification.

**Feature selection across omics**:
```python
def select_multiomics_features(X_dict, y, n_features=50):
    """
    Select top features across omics for classification.

    X_dict: {
        'rnaseq': DataFrame (samples x genes),
        'proteomics': DataFrame (samples x proteins),
        'methylation': DataFrame (samples x CpGs)
    }
    y: Target labels (disease vs control)

    Returns: Selected features per omics
    """
    from sklearn.feature_selection import SelectKBest, f_classif

    selected_features = {}
    for omics_type, X in X_dict.items():
        selector = SelectKBest(f_classif, k=min(n_features, X.shape[1]))
        selector.fit(X, y)

        # Get selected feature names
        selected_idx = selector.get_support()
        selected_features[omics_type] = X.columns[selected_idx].tolist()

    return selected_features
```

**Multi-omics classification**:
```python
def multiomics_classification(X_dict, y, selected_features):
    """
    Train classifier using multi-omics features.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score

    # Concatenate selected features from each omics
    X_combined = []
    for omics_type, features in selected_features.items():
        X_combined.append(X_dict[omics_type][features])

    X_combined = pd.concat(X_combined, axis=1)

    # Train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(clf, X_combined, y, cv=5, scoring='roc_auc')

    return {
        'mean_auc': scores.mean(),
        'std_auc': scores.std(),
        'n_features': X_combined.shape[1],
        'features_per_omics': {k: len(v) for k, v in selected_features.items()}
    }
```

### Phase 8: Integrated Reporting

**Generate comprehensive multi-omics report**:

```markdown
# Multi-Omics Integration Report

## Dataset Summary
- **Omics Types**: RNA-seq, Proteomics, Methylation, CNV
- **Common Samples**: 45 patients (30 disease, 15 control)
- **Features**: 15,000 genes, 5,000 proteins, 450K CpGs, 20K CNV regions

## Cross-Omics Correlation

### RNA-Protein Correlation
- **Overall correlation**: r = 0.52 (expected: 0.4-0.6)
- **Highly correlated**: 3,245 genes (45%)
- **Discordant genes**: 890 genes (post-transcriptional regulation)

### Methylation-Expression
- **Promoter methylation**: Anticorrelation r = -0.41
- **Epigenetically regulated genes**: 1,256 genes (p < 0.01)
- **Example**: BRCA1 promoter hypermethylation → 3-fold reduced expression

### CNV-Expression Dosage Effect
- **Genes with dosage effect**: 445 genes (r > 0.5, p < 0.01)
- **Example**: MYC amplification (3 copies) → 2.8-fold increased expression

## Multi-Omics Clustering

### MOFA+ Analysis
- **Factor 1** (25% variance): Cell cycle genes (RNA + protein)
- **Factor 2** (18% variance): Immune signature (RNA + methylation)
- **Factor 3** (15% variance): Metabolic reprogramming (RNA + metabolites)

### Patient Subtypes
- **Subtype 1** (n=18): High proliferation, MYC amplification
- **Subtype 2** (n=15): Immune-enriched, hypomethylation
- **Subtype 3** (n=12): Metabolic dysregulation, mitochondrial dysfunction

## Pathway Integration

### Top Dysregulated Pathways (Multi-Omics Score)
1. **Cell Cycle** (score: 8.5) - RNA (↑), Protein (↑), CNV (amplification)
2. **Immune Response** (score: 7.2) - RNA (↑), Methylation (hypo)
3. **Glycolysis** (score: 6.8) - RNA (↑), Metabolites (↑)

## Multi-Omics Biomarkers

### Classification Performance
- **AUC**: 0.92 ± 0.04 (5-fold CV)
- **Features**: 50 total (20 RNA, 15 protein, 10 methylation, 5 CNV)
- **Top biomarkers**:
  - MYC expression (RNA)
  - CDK1 protein abundance
  - BRCA1 promoter methylation
  - TP53 CNV status

## Biological Interpretation

The multi-omics analysis reveals three distinct disease subtypes driven by different molecular mechanisms:

1. **Proliferative subtype**: Characterized by MYC amplification driving coordinated upregulation of cell cycle genes at both RNA and protein levels.

2. **Immune subtype**: Hypomethylation of immune genes leading to increased expression and T-cell infiltration.

3. **Metabolic subtype**: Shift from oxidative phosphorylation to glycolysis, with concordant changes in enzyme expression and metabolite levels.

These subtypes may respond differently to targeted therapies.
```

---

## ToolUniverse Skills Coordination

This skill orchestrates multiple specialized skills:

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-rnaseq-deseq2` | Load and analyze RNA-seq data | Phase 1, 4 |
| `tooluniverse-epigenomics` | Methylation analysis, ChIP-seq peaks | Phase 1, 4 |
| `tooluniverse-variant-analysis` | CNV and SNV processing | Phase 1, 3, 4 |
| `tooluniverse-protein-interactions` | Protein network context | Phase 6 |
| `tooluniverse-gene-enrichment` | Pathway enrichment | Phase 6 |
| `tooluniverse-expression-data-retrieval` | Public omics data retrieval | Phase 1 |
| `tooluniverse-target-research` | Gene/protein annotation | Phase 3, 8 |

---

## Example Use Cases

### Use Case 1: Cancer Multi-Omics

**Question**: "Integrate TCGA breast cancer RNA-seq, proteomics, methylation, and CNV data"

**Workflow**:
1. Load 4 omics types for 500 patients
2. Match samples (450 common across all omics)
3. Correlate RNA-protein (identify translation-regulated genes)
4. Correlate methylation-expression (find epigenetically silenced genes)
5. Correlate CNV-expression (identify dosage-sensitive genes)
6. Run MOFA+ to find latent factors
7. Identify 4 subtypes with distinct multi-omics profiles
8. Perform pathway enrichment per subtype
9. Select multi-omics biomarkers (AUC=0.94)

### Use Case 2: eQTL + Expression

**Question**: "How do GWAS variants affect gene expression through methylation?"

**Workflow**:
1. Load genotype data (SNPs from GWAS)
2. Load expression data (RNA-seq)
3. Load methylation data (450K array)
4. For each GWAS SNP:
   - Test association with nearby gene expression (eQTL)
   - Test association with nearby CpG methylation (meQTL)
   - Test CpG-gene correlation
5. Identify SNP → methylation → expression regulatory chains
6. Annotate with ToolUniverse (GWAS traits, gene function)

### Use Case 3: Drug Response Multi-Omics

**Question**: "Predict drug response using multi-omics profiles"

**Workflow**:
1. Load baseline multi-omics (pre-treatment)
2. Load drug response data (IC50 or clinical response)
3. Correlate each omics with response
4. Select multi-omics features predictive of response
5. Train multi-omics classifier
6. Identify pathways associated with resistance/sensitivity
7. Use ToolUniverse drug-repurposing skill for alternative options

---

## Advanced Analysis Patterns

### Pattern 1: Omics-Driven Patient Stratification

For precision medicine applications where patient stratification is goal.

### Pattern 2: Multi-Omics Network Analysis

Build integrated networks combining PPI, co-expression, regulatory interactions.

### Pattern 3: Temporal Multi-Omics

Longitudinal multi-omics data (time-series or treatment response).

### Pattern 4: Spatial Multi-Omics

Spatial transcriptomics + proteomics for tissue architecture.

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Omics types | At least 2 omics datasets |
| Common samples | At least 10 samples across omics |
| Cross-correlation | Pearson/Spearman correlation computed |
| Clustering | At least one method (MOFA+, NMF, or SNF) |
| Pathway integration | Enrichment with multi-omics evidence scores |
| Report | Summary, correlations, clusters, pathways, biomarkers |

---

## Limitations

- **Sample size**: Multi-omics integration requires sufficient samples (n≥20 recommended)
- **Missing data**: Some patients may not have all omics types
- **Batch effects**: Different omics platforms/batches require careful normalization
- **Computational**: Large multi-omics datasets may require significant memory/compute
- **Interpretation**: Multi-omics results require domain expertise for biological validation

---

## References

**Methods**:
- MOFA+: https://doi.org/10.1186/s13059-020-02015-1
- Similarity Network Fusion: https://doi.org/10.1038/nmeth.2810
- Multi-omics review: https://doi.org/10.1038/s41576-019-0093-7

**ToolUniverse Skills**:
- See individual skill documentation for omics-specific methods
