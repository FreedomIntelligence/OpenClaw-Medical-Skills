# tooluniverse-metabolomics-analysis

> Analyze metabolomics data including metabolite identification, quantification, pathway analysis, and metabolic flux. Processes LC-MS, GC-MS, NMR data from targeted and untargeted experiments. Performs normalization, statistical analysis, pathway enrichment, metabolite-enzyme integration, and biomarker discovery. Use when analyzing metabolomics datasets, identifying differential metabolites, studying metabolic pathways, integrating with transcriptomics/proteomics, discovering metabolic biomarkers, performing flux balance analysis, or characterizing metabolic phenotypes in disease, drug response, or physiological conditions.

# Metabolomics Analysis

Comprehensive analysis of metabolomics data from metabolite identification through quantification, statistical analysis, pathway interpretation, and integration with other omics layers.

## When to Use This Skill

**Triggers**:
- User has metabolomics data (LC-MS, GC-MS, NMR)
- Questions about metabolite abundance or concentrations
- Differential metabolite analysis requests
- Metabolic pathway analysis
- Multi-omics integration with metabolomics
- Metabolic biomarker discovery
- Flux balance analysis or metabolic modeling
- Metabolite-enzyme correlation

**Example Questions This Skill Solves**:
1. "Analyze this LC-MS metabolomics data for differential metabolites"
2. "Which metabolic pathways are dysregulated between conditions?"
3. "Identify metabolite biomarkers for disease classification"
4. "Correlate metabolite levels with enzyme expression"
5. "Perform pathway enrichment for differential metabolites"
6. "Integrate metabolomics with transcriptomics data"
7. "Characterize the metabolic phenotype of this cell line"
8. "Identify metabolites associated with drug response"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Import** | LC-MS, GC-MS, NMR, targeted/untargeted platforms |
| **Metabolite Identification** | Match to HMDB, KEGG, PubChem, spectral libraries |
| **Quality Control** | Peak quality, blank subtraction, internal standard normalization |
| **Normalization** | Probabilistic quotient, total ion current, internal standards |
| **Statistical Analysis** | Univariate and multivariate (PCA, PLS-DA, OPLS-DA) |
| **Differential Analysis** | Identify significant metabolite changes |
| **Pathway Enrichment** | KEGG, Reactome, BioCyc metabolic pathway analysis |
| **Metabolite-Enzyme Integration** | Correlate with expression data |
| **Flux Analysis** | Metabolic flux balance analysis (FBA) |
| **Biomarker Discovery** | Multi-metabolite signatures |

---

## Workflow Overview

```
Input: Metabolomics Data (Peak Table or Spectra)
    |
    v
Phase 1: Data Import & Metabolite Identification
    |-- Load peak table or process raw spectra
    |-- Match features to metabolite databases (HMDB, KEGG)
    |-- Annotate with chemical IDs, formulas, pathways
    |-- Confidence scoring for IDs
    |
    v
Phase 2: Quality Control & Filtering
    |-- Assess peak quality (CV, blank ratios)
    |-- Remove background peaks
    |-- Filter low-quality metabolites
    |-- Internal standard check
    |
    v
Phase 3: Normalization
    |-- Sample-wise normalization (TIC, PQN, internal standards)
    |-- Batch effect correction
    |-- Log-transform or scaling
    |
    v
Phase 4: Exploratory Analysis
    |-- PCA for sample clustering
    |-- Quality assessment plots
    |-- Outlier detection
    |-- Sample correlation
    |
    v
Phase 5: Differential Analysis
    |-- Statistical testing (t-test, ANOVA, Wilcoxon)
    |-- Fold change calculation
    |-- Multiple testing correction
    |-- Volcano plots, heatmaps
    |
    v
Phase 6: Pathway Analysis
    |-- Metabolite set enrichment (MSEA)
    |-- Pathway topology analysis
    |-- KEGG/Reactome pathway mapping
    |-- Identify dysregulated pathways
    |
    v
Phase 7: Multi-Omics Integration
    |-- Correlate with enzyme expression (RNA/protein)
    |-- Metabolite-gene associations
    |-- Pathway-level integration
    |-- Metabolic flux inference
    |
    v
Phase 8: Generate Report
    |-- Summary statistics
    |-- Differential metabolites
    |-- Pathway diagrams
    |-- Multi-omics integration plots
    |-- Biomarker panel
```

---

## Phase Details

### Phase 1: Data Import & Metabolite Identification

**Objective**: Load data and identify metabolites from features.

**Supported data types**:
- **Peak tables**: Pre-processed metabolite abundance
- **Raw spectra**: LC-MS (.mzML, .mzXML), GC-MS
- **NMR spectra**: 1D/2D NMR data

**Peak table format** (typical):
```
Sample_ID | Glucose | Lactate | Glutamine | ... | Cholesterol
----------|---------|---------|-----------|-----|------------
Control_1 | 125000  | 45000   | 78000     | ... | 23000
Control_2 | 130000  | 43000   | 82000     | ... | 25000
Disease_1 | 85000   | 92000   | 45000     | ... | 45000
```

**Data loading**:
```python
def load_metabolomics_data(file_path, file_type='peak_table'):
    """
    Load metabolomics data.

    file_type options:
    - 'peak_table': CSV/TSV with metabolites as columns
    - 'mzml': Raw LC-MS data (requires processing)
    - 'nmr': NMR spectra
    """
    import pandas as pd

    if file_type == 'peak_table':
        # Load peak table
        data = pd.read_csv(file_path, index_col=0)
        # Rows = samples, Columns = metabolites
        return data

    elif file_type == 'mzml':
        # Process raw MS data (requires pymzml or similar)
        # Peak detection, alignment, quantification
        pass
```

**Metabolite identification**:
```python
def identify_metabolites(feature_data, mass_list, rt_list=None):
    """
    Match features to metabolite databases.

    Uses accurate mass and retention time (if available).
    Queries: HMDB, KEGG Compound, PubChem
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    identified_metabolites = []

    for i, mass in enumerate(mass_list):
        # Query HMDB by mass (±5 ppm tolerance)
        hmdb_result = tu.run_one_function({
            "name": "hmdb_search_by_mass",
            "arguments": {
                "mass": mass,
                "mass_tolerance": 0.005  # 5 ppm
            }
        })

        if hmdb_result and 'data' in hmdb_result:
            matches = hmdb_result['data']
            # Rank by confidence
            # (exact mass match, pathway context, etc.)
            identified_metabolites.append({
                'feature_id': i,
                'metabolite_name': matches[0]['name'],
                'hmdb_id': matches[0]['accession'],
                'formula': matches[0]['chemical_formula'],
                'confidence': calculate_confidence(matches[0])
            })

    return identified_metabolites
```

**Confidence scoring**:
```
Level 1: Confirmed with authentic standard (MS + RT match)
Level 2: Probable structure (accurate mass + MS/MS)
Level 3: Tentative match (accurate mass only)
Level 4: Unknown metabolite
```

### Phase 2: Quality Control & Filtering

**Objective**: Remove low-quality features and background noise.

**Quality control metrics**:
```python
def metabolomics_qc(data, sample_metadata):
    """
    Quality control for metabolomics data.

    QC metrics:
    - Coefficient of variation (CV) in QC samples
    - Blank ratios (signal in samples vs blanks)
    - Missing values per metabolite
    - Total ion current per sample
    """
    # 1. CV in QC samples (should be < 30%)
    qc_samples = sample_metadata['sample_type'] == 'QC'
    qc_data = data[qc_samples]

    cv_per_metabolite = qc_data.std() / qc_data.mean()
    high_cv = cv_per_metabolite > 0.3

    print(f"Metabolites with CV > 30%: {high_cv.sum()}")

    # 2. Blank subtraction
    blank_samples = sample_metadata['sample_type'] == 'Blank'
    blank_data = data[blank_samples]

    # Calculate blank ratios
    blank_means = blank_data.mean()
    sample_means = data[~blank_samples & ~qc_samples].mean()
    blank_ratio = sample_means / blank_means

    # Filter: keep metabolites with sample/blank > 3
    keep_metabolites = blank_ratio > 3

    # 3. Missing values (remove if >50% missing)
    missing_per_metabolite = (data == 0).sum() / data.shape[0]
    keep_metabolites &= (missing_per_metabolite < 0.5)

    # Filter data
    filtered_data = data.loc[:, keep_metabolites]

    return filtered_data
```

### Phase 3: Normalization

**Objective**: Account for technical variation and enable fair comparison.

**Normalization methods**:

**1. Total Ion Current (TIC)**:
```python
def normalize_tic(data):
    """
    Normalize by total ion current.
    Assumes total metabolite abundance is similar across samples.
    """
    tic = data.sum(axis=1)
    median_tic = tic.median()
    norm_factors = median_tic / tic
    normalized = data.multiply(norm_factors, axis=0)
    return normalized
```

**2. Probabilistic Quotient Normalization (PQN)**:
```python
def normalize_pqn(data, reference_sample=None):
    """
    Probabilistic quotient normalization.
    More robust than TIC to large metabolite changes.
    """
    import numpy as np

    # Use median sample as reference
    if reference_sample is None:
        reference = data.median(axis=0)
    else:
        reference = data.loc[reference_sample]

    # Calculate quotients
    quotients = data.div(reference, axis=1)

    # Median quotient per sample
    norm_factors = quotients.median(axis=1)

    # Normalize
    normalized = data.div(norm_factors, axis=0)

    return normalized
```

**3. Internal Standard Normalization**:
```python
def normalize_internal_standard(data, is_metabolite):
    """
    Normalize by spiked-in internal standard.
    Most accurate if added before sample processing.
    """
    is_abundance = data[is_metabolite]
    norm_factors = is_abundance.median() / is_abundance
    normalized = data.multiply(norm_factors, axis=0)

    # Remove internal standard from data
    normalized = normalized.drop(columns=[is_metabolite])

    return normalized
```

**Transformation**:
```python
def transform_data(data, method='log'):
    """
    Transform metabolite abundances.

    Methods:
    - 'log': log2 transform (stabilize variance)
    - 'pareto': Pareto scaling (mean-center, divide by sqrt(std))
    - 'auto': Auto-scaling (mean-center, divide by std)
    """
    import numpy as np

    if method == 'log':
        # Add small constant to avoid log(0)
        transformed = np.log2(data + 1)

    elif method == 'pareto':
        # Pareto scaling (common in metabolomics)
        mean = data.mean(axis=0)
        std = data.std(axis=0)
        transformed = (data - mean) / np.sqrt(std)

    elif method == 'auto':
        # Auto-scaling (z-score)
        mean = data.mean(axis=0)
        std = data.std(axis=0)
        transformed = (data - mean) / std

    return transformed
```

### Phase 4: Exploratory Analysis

**Objective**: Visualize data structure and detect outliers.

**PCA**:
```python
def perform_pca_metabolomics(data, sample_groups):
    """
    Principal component analysis for sample clustering.
    """
    from sklearn.decomposition import PCA
    import matplotlib.pyplot as plt

    # PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(data)

    # Plot
    plt.figure(figsize=(8, 6))
    for group in sample_groups.unique():
        mask = sample_groups == group
        plt.scatter(pca_result[mask, 0], pca_result[mask, 1], label=group)

    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    plt.legend()
    plt.title('PCA - Metabolomics Data')
```

**PLS-DA** (Partial Least Squares Discriminant Analysis):
```python
def plsda_analysis(X, y, n_components=2):
    """
    PLS-DA for supervised dimensionality reduction.
    Better separation than PCA for classification tasks.
    """
    from sklearn.cross_decomposition import PLSRegression
    from sklearn.preprocessing import LabelEncoder

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # PLS
    pls = PLSRegression(n_components=n_components)
    X_pls = pls.fit_transform(X, y_encoded)[0]

    # Plot
    plt.scatter(X_pls[:, 0], X_pls[:, 1], c=y_encoded)
    plt.xlabel('PLS Component 1')
    plt.ylabel('PLS Component 2')
    plt.title('PLS-DA')

    return X_pls
```

### Phase 5: Differential Metabolite Analysis

**Objective**: Identify metabolites with significant abundance changes.

**Statistical testing**:
```python
def differential_metabolites(data, group1_samples, group2_samples):
    """
    Identify differential metabolites between two groups.
    """
    from scipy import stats
    import numpy as np

    results = []

    for metabolite in data.columns:
        # Extract abundances
        group1 = data.loc[group1_samples, metabolite]
        group2 = data.loc[group2_samples, metabolite]

        # Statistics
        mean1 = group1.mean()
        mean2 = group2.mean()
        fold_change = mean2 / mean1
        log2fc = np.log2(fold_change)

        # t-test
        t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)

        results.append({
            'metabolite': metabolite,
            'fold_change': fold_change,
            'log2FC': log2fc,
            'mean_group1': mean1,
            'mean_group2': mean2,
            'p_value': p_value,
            't_statistic': t_stat
        })

    results_df = pd.DataFrame(results)

    # Multiple testing correction
    from statsmodels.stats.multitest import multipletests
    results_df['adj_p_value'] = multipletests(results_df['p_value'], method='fdr_bh')[1]

    # Significance
    results_df['significant'] = (
        (results_df['adj_p_value'] < 0.05) &
        (np.abs(results_df['log2FC']) > 1.0)
    )

    return results_df
```

**Volcano plot**:
```python
def plot_metabolite_volcano(de_results):
    """Visualize differential metabolite results."""
    plt.figure(figsize=(8, 6))

    # Non-significant
    non_sig = de_results[~de_results['significant']]
    plt.scatter(non_sig['log2FC'], -np.log10(non_sig['p_value']),
                c='gray', alpha=0.5, s=20)

    # Significant
    sig = de_results[de_results['significant']]
    plt.scatter(sig['log2FC'], -np.log10(sig['p_value']),
                c='red', alpha=0.7, s=30)

    plt.axhline(-np.log10(0.05), color='blue', linestyle='--')
    plt.axvline(-1, color='blue', linestyle='--')
    plt.axvline(1, color='blue', linestyle='--')

    plt.xlabel('log2 Fold Change')
    plt.ylabel('-log10(p-value)')
    plt.title('Differential Metabolites')
```

### Phase 6: Metabolic Pathway Analysis

**Objective**: Interpret metabolite changes at pathway level.

**Metabolite Set Enrichment Analysis (MSEA)**:
```python
def pathway_enrichment_metabolites(metabolite_list, organism='human'):
    """
    Perform pathway enrichment for differential metabolites.

    Uses KEGG metabolic pathways.
    """
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()

    # Get KEGG compound IDs for metabolites
    kegg_ids = []
    for metabolite in metabolite_list:
        # Convert HMDB ID to KEGG Compound ID
        result = tu.run_one_function({
            "name": "kegg_find_compound",
            "arguments": {"query": metabolite}
        })
        if result and 'data' in result:
            kegg_ids.append(result['data'][0]['entry_id'])

    # Pathway enrichment
    enrichment = tu.run_one_function({
        "name": "kegg_enrich_pathway",
        "arguments": {
            "compound_list": ",".join(kegg_ids),
            "organism": organism
        }
    })

    return enrichment
```

**Pathway topology analysis**:
```python
def pathway_topology_analysis(metabolites, pathway_id):
    """
    Analyze pathway dysregulation considering topology.

    Metabolites at key pathway positions (hubs, bottlenecks)
    have more impact than peripheral metabolites.
    """
    # Load pathway structure from KEGG
    # Calculate impact score based on:
    # - Betweenness centrality (bottleneck metabolites)
    # - Degree centrality (hub metabolites)
    # - Pathway position (early vs late)

    pass
```

### Phase 7: Multi-Omics Integration

**Objective**: Integrate metabolomics with transcriptomics/proteomics.

**Metabolite-enzyme correlation**:
```python
def correlate_metabolite_enzyme(metabolite_data, enzyme_expression):
    """
    Correlate metabolite levels with enzyme expression.

    Expected correlations:
    - Substrate + enzyme → negative correlation (consumption)
    - Product + enzyme → positive correlation (production)
    """
    from scipy.stats import spearmanr

    # For each metabolite-enzyme pair
    correlations = {}

    for metabolite in metabolite_data.columns:
        # Find enzymes that produce/consume this metabolite
        enzymes = find_metabolite_enzymes(metabolite)

        for enzyme in enzymes:
            if enzyme in enzyme_expression.index:
                met_levels = metabolite_data[metabolite]
                enz_expr = enzyme_expression.loc[enzyme]

                r, p = spearmanr(met_levels, enz_expr)

                correlations[f'{metabolite}_{enzyme}'] = {
                    'r': r,
                    'p': p,
                    'relationship': 'product' if r > 0 else 'substrate'
                }

    return correlations
```

**Pathway-level integration**:
```python
def integrate_omics_pathway(metabolite_fc, gene_fc, pathway_id):
    """
    Integrate metabolite and gene fold changes at pathway level.

    For each reaction:
    - Check if metabolites are changed
    - Check if enzymes are changed
    - Score pathway dysregulation (combined evidence)
    """
    # Load pathway reactions
    # For each reaction:
    #   - Metabolite substrate/product changes
    #   - Enzyme expression changes
    #   - Concordance score

    pathway_score = calculate_pathway_dysregulation(
        metabolite_fc, gene_fc, pathway_id
    )

    return pathway_score
```

### Phase 8: Report Generation

**Generate comprehensive metabolomics report**:

```markdown
# Metabolomics Analysis Report

## Dataset Summary
- **Platform**: LC-MS/MS (Orbitrap)
- **Method**: Untargeted metabolomics
- **Samples**: 40 (20 disease, 20 control)
- **Metabolites Identified**: 324 (Level 1/2 confidence)
- **Metabolites Quantified**: 298 (after QC)

## Quality Control
- **CV in QC samples**: 18% median (acceptable: <30%)
- **Blank ratios**: All metabolites > 3x blank signal
- **Missing values**: 8% average per metabolite
- **Internal standard**: Recovery 95-105% across samples

## Normalization
- **Method**: Probabilistic Quotient Normalization (PQN)
- **Transformation**: log2
- **Batch correction**: Not required (single batch)

## Exploratory Analysis
- **PCA**: Clear separation between groups (PC1: 28%, PC2: 18%)
- **PLS-DA**: Excellent discrimination (R2=0.89, Q2=0.75)
- **Outliers**: 1 sample removed (technical failure)

## Differential Metabolites
- **Significant metabolites**: 87 (adj. p < 0.05, |log2FC| > 1)
  - Increased: 52 metabolites
  - Decreased: 35 metabolites

### Top Increased Metabolites
1. **Lactate** (log2FC=3.2, p=1e-12) - Glycolysis
2. **Glutamine** (log2FC=2.8, p=1e-10) - Amino acid metabolism
3. **Palmitate** (log2FC=2.5, p=1e-9) - Fatty acid synthesis

### Top Decreased Metabolites
1. **Citrate** (log2FC=-2.9, p=1e-11) - TCA cycle
2. **ATP** (log2FC=-2.3, p=1e-9) - Energy metabolism
3. **NAD+** (log2FC=-2.1, p=1e-8) - Redox balance

## Pathway Enrichment
### Top Dysregulated Pathways
1. **Glycolysis/Gluconeogenesis** (p=1e-15)
   - 12 metabolites: glucose, pyruvate, lactate, etc.
   - Direction: Increased flux to lactate (Warburg effect)
2. **TCA Cycle** (p=1e-12)
   - 8 metabolites: citrate, succinate, malate, etc.
   - Direction: Decreased activity
3. **Glutaminolysis** (p=1e-10)
   - 6 metabolites: glutamine, glutamate, α-KG, etc.
   - Direction: Increased glutamine consumption

## Multi-Omics Integration
### Metabolite-Enzyme Correlations
- **LDHA (lactate dehydrogenase)**
  - Expression: 3.5-fold increased (RNA + protein)
  - Lactate: 3.2-fold increased
  - Correlation: r=0.85 (p<0.001) - Concordant upregulation
- **IDH1 (isocitrate dehydrogenase)**
  - Expression: 2.1-fold decreased
  - Citrate: 2.9-fold decreased
  - Correlation: r=0.78 (p<0.001) - TCA cycle suppression

### Metabolic Phenotype
Integration with RNA-seq and proteomics reveals:
- **Warburg effect**: Shift from oxidative to glycolytic metabolism
- **Glutamine addiction**: Increased glutaminolysis for anaplerosis
- **Redox imbalance**: Decreased NAD+/NADH ratio, oxidative stress

## Biomarker Discovery
### Top 10 Metabolites for Classification
Random Forest model (10-fold CV):
- **AUC**: 0.96 ± 0.03
- **Accuracy**: 92%

**Biomarker Panel**:
1. Lactate
2. Glutamine
3. Citrate
4. ATP
5. Palmitate
6. Pyruvate
7. Succinate
8. NAD+
9. α-ketoglutarate
10. Glucose-6-phosphate

## Biological Interpretation
Metabolomics reveals fundamental metabolic reprogramming in disease state:

1. **Glycolytic switch**: Increased glycolysis with lactate accumulation despite oxygen availability (Warburg effect), driven by LDHA upregulation.

2. **TCA cycle suppression**: Decreased citrate and TCA intermediates, consistent with IDH1 downregulation. Shunts carbon to biosynthesis.

3. **Glutamine dependence**: Elevated glutamine consumption and glutaminolysis provides alternative carbon source for anaplerosis and NADPH for biosynthesis.

4. **Biosynthetic activation**: Increased palmitate indicates active fatty acid synthesis, supporting membrane production for proliferation.

5. **Energy stress**: Despite active glycolysis, ATP levels are decreased, suggesting high energy demand outpacing production.

This metabolic signature is characteristic of proliferative, biosynthetically active cells typical of cancer or activated immune cells.

## Clinical Relevance
- **Therapeutic targets**: LDHA inhibitors, glutaminase inhibitors to disrupt metabolic dependencies
- **Biomarkers**: Lactate/citrate ratio as metabolic activity marker
- **Drug response**: Metabolic phenotype may predict sensitivity to metabolic inhibitors
```

---

## Integration with ToolUniverse

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-gene-enrichment` | Pathway enrichment | Phase 6 |
| `tooluniverse-rnaseq-deseq2` | Enzyme expression for integration | Phase 7 |
| `tooluniverse-proteomics-analysis` | Protein levels for integration | Phase 7 |
| `tooluniverse-multi-omics-integration` | Comprehensive integration | Phase 7 |

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Metabolites | At least 50 identified metabolites |
| Replicates | At least 3 per condition |
| QC | CV < 30% in QC samples, blank subtraction |
| Statistical test | t-test or Wilcoxon with FDR correction |
| Pathway analysis | MSEA with KEGG or Reactome |
| Report | QC, differential metabolites, pathways, visualizations |

---

## Limitations

- **Identification**: Many features remain unidentified (Level 4)
- **Coverage**: Cannot detect all metabolites (depends on method)
- **Quantification**: Relative abundance (not absolute concentration without standards)
- **Isomers**: Difficult to distinguish structural isomers
- **Ion suppression**: Matrix effects can affect quantification
- **Dynamic range**: Limited compared to targeted methods

---

## References

**Methods**:
- MetaboAnalyst: https://doi.org/10.1093/nar/gkab382
- XCMS: https://doi.org/10.1021/ac051437y
- MSEA: https://doi.org/10.1186/1471-2105-11-395

**Databases**:
- HMDB: https://hmdb.ca
- KEGG Compound: https://www.genome.jp/kegg/compound/
- Reactome: https://reactome.org
