# tooluniverse-spatial-transcriptomics

> Analyze spatial transcriptomics data to map gene expression in tissue architecture. Supports 10x Visium, MERFISH, seqFISH, Slide-seq, and imaging-based platforms. Performs spatial clustering, domain identification, cell-cell proximity analysis, spatial gene expression patterns, tissue architecture mapping, and integration with single-cell data. Use when analyzing spatial transcriptomics datasets, studying tissue organization, identifying spatial expression patterns, mapping cell-cell interactions in tissue context, characterizing tumor microenvironment spatial structure, or integrating spatial and single-cell RNA-seq data for comprehensive tissue analysis.

# Spatial Transcriptomics Analysis

Comprehensive analysis of spatially-resolved transcriptomics data to understand gene expression patterns in tissue architecture context. Combines expression profiling with spatial coordinates to reveal tissue organization, cell-cell interactions, and spatially variable genes.

## When to Use This Skill

**Triggers**:
- User has spatial transcriptomics data (Visium, MERFISH, seqFISH, etc.)
- Questions about tissue architecture or spatial organization
- Spatial gene expression pattern analysis
- Cell-cell proximity or neighborhood analysis requests
- Tumor microenvironment spatial structure questions
- Integration of spatial with single-cell data
- Spatial domain identification
- Tissue morphology correlation with expression

**Example Questions This Skill Solves**:
1. "Analyze this 10x Visium dataset to identify spatial domains"
2. "Which genes show spatially variable expression in this tissue?"
3. "Map the tumor microenvironment spatial organization"
4. "Find genes enriched at tissue boundaries"
5. "Identify cell-cell interactions based on spatial proximity"
6. "Integrate spatial transcriptomics with scRNA-seq annotations"
7. "Characterize spatial gradients in gene expression"
8. "Map ligand-receptor pairs in tissue context"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Data Import** | 10x Visium, MERFISH, seqFISH, Slide-seq, STARmap, Xenium formats |
| **Quality Control** | Spot/cell QC, spatial alignment verification, tissue coverage |
| **Normalization** | Spatial-aware normalization accounting for tissue heterogeneity |
| **Spatial Clustering** | Identify spatial domains with similar expression profiles |
| **Spatial Variable Genes** | Find genes with non-random spatial patterns |
| **Neighborhood Analysis** | Cell-cell proximity, spatial neighborhoods, niche identification |
| **Spatial Patterns** | Gradients, boundaries, hotspots, expression waves |
| **Integration** | Merge with scRNA-seq for cell type mapping |
| **Ligand-Receptor Spatial** | Map cell communication in tissue context |
| **Visualization** | Spatial plots, heatmaps on tissue, 3D reconstruction |

---

## Workflow Overview

```
Input: Spatial Transcriptomics Data + Tissue Image
    |
    v
Phase 1: Data Import & QC
    |-- Load spatial coordinates + expression matrix
    |-- Load tissue histology image
    |-- Quality control per spot/cell
    |-- Filter low-quality spots
    |-- Align spatial coordinates to tissue
    |
    v
Phase 2: Preprocessing
    |-- Normalization (spatial-aware methods)
    |-- Highly variable gene selection
    |-- Dimensionality reduction (PCA)
    |-- Spatial lag smoothing (optional)
    |
    v
Phase 3: Spatial Clustering
    |-- Identify spatial domains/regions
    |-- Graph-based clustering with spatial constraints
    |-- Annotate domains with marker genes
    |-- Visualize domains on tissue
    |
    v
Phase 4: Spatial Variable Genes
    |-- Test for spatial autocorrelation (Moran's I, Geary's C)
    |-- Identify genes with spatial patterns
    |-- Classify pattern types (gradient, hotspot, boundary)
    |-- Rank by spatial significance
    |
    v
Phase 5: Neighborhood Analysis
    |-- Define spatial neighborhoods (k-NN, radius)
    |-- Calculate neighborhood composition
    |-- Identify interaction zones
    |-- Niche characterization
    |
    v
Phase 6: Integration with scRNA-seq
    |-- Cell type deconvolution per spot
    |-- Map cell types to spatial locations
    |-- Predict cell type spatial distributions
    |-- Validate with marker genes
    |
    v
Phase 7: Spatial Cell Communication
    |-- Identify proximal cell type pairs
    |-- Query ligand-receptor database (OmniPath)
    |-- Score spatial interactions
    |-- Map communication hotspots
    |
    v
Phase 8: Generate Spatial Report
    |-- Tissue overview with domains
    |-- Spatially variable genes
    |-- Cell type spatial maps
    |-- Interaction networks in tissue context
    |-- 3D visualization (if applicable)
```

---

## Phase Details

### Phase 1: Data Import & Quality Control

**Objective**: Load spatial data and assess quality.

**Supported platforms**:

**10x Visium** (most common):
- Spots: 55μm diameter, ~50 cells per spot
- Resolution: ~5,000-10,000 spots per capture area
- Data: Expression matrix + spatial coordinates + H&E image

**MERFISH/seqFISH** (imaging-based):
- Single-cell resolution
- Targeted gene panels (100-10,000 genes)
- Absolute coordinates per cell

**Slide-seq/Slide-seqV2**:
- 10μm bead resolution
- Genome-wide profiling

**Xenium** (10x single-cell spatial):
- Single-cell resolution
- Large gene panels (300+ genes)
- Subcellular resolution

**Data loading (Visium)**:
```python
def load_visium_data(data_dir):
    """
    Load 10x Visium spatial transcriptomics data.

    Expected structure:
    data_dir/
      ├── filtered_feature_bc_matrix/
      │   ├── barcodes.tsv.gz
      │   ├── features.tsv.gz
      │   └── matrix.mtx.gz
      ├── spatial/
      │   ├── tissue_positions_list.csv
      │   ├── scalefactors_json.json
      │   └── tissue_hires_image.png

    Returns: AnnData object with spatial coordinates
    """
    import scanpy as sc
    import pandas as pd

    # Load expression data
    adata = sc.read_visium(data_dir)

    # Spatial coordinates are in adata.obsm['spatial']
    # Tissue image in adata.uns['spatial']

    return adata
```

**Quality Control**:

1. **Spot-level QC**:
```python
def spatial_qc(adata):
    """
    Quality control for spatial transcriptomics data.
    """
    import scanpy as sc

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(adata, inplace=True)

    # Visualize QC metrics spatially
    sc.pl.spatial(adata, color='n_genes_by_counts', title='Genes per Spot')
    sc.pl.spatial(adata, color='total_counts', title='UMI Counts per Spot')

    # Filter criteria
    # - Min 200 genes per spot
    # - Min 500 UMI counts per spot
    # - Max mitochondrial content < 20%

    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_cells(adata, min_counts=500)

    # Mitochondrial filtering
    adata.var['mt'] = adata.var_names.str.startswith('MT-')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
    adata = adata[adata.obs['pct_counts_mt'] < 20].copy()

    return adata
```

2. **Spatial alignment verification**:
```python
def verify_spatial_alignment(adata):
    """
    Verify spatial coordinates align with tissue image.
    """
    import matplotlib.pyplot as plt

    # Plot spots on tissue image
    fig, ax = plt.subplots(figsize=(10, 10))

    # Tissue image
    img = adata.uns['spatial']['tissue_hires_image']
    ax.imshow(img)

    # Overlay spot coordinates
    coords = adata.obsm['spatial']
    ax.scatter(coords[:, 0], coords[:, 1], c='red', s=1, alpha=0.5)

    ax.set_title('Spatial Alignment Verification')
    plt.axis('off')
```

### Phase 2: Preprocessing & Normalization

**Objective**: Normalize data accounting for spatial heterogeneity.

**Normalization**:
```python
def normalize_spatial(adata):
    """
    Normalize spatial transcriptomics data.
    """
    import scanpy as sc

    # Filter genes (min 3 spots)
    sc.pp.filter_genes(adata, min_cells=3)

    # Normalize to median total counts
    sc.pp.normalize_total(adata, target_sum=1e4)

    # Log-transform
    sc.pp.log1p(adata)

    # Store raw counts
    adata.raw = adata

    return adata
```

**Highly variable genes**:
```python
def select_hvg_spatial(adata):
    """
    Select highly variable genes for spatial analysis.
    """
    import scanpy as sc

    # Standard HVG selection
    sc.pp.highly_variable_genes(adata, n_top_genes=2000)

    # Optionally: weight by spatial autocorrelation
    # Genes with spatial patterns are more informative

    return adata
```

**Spatial smoothing** (optional):
```python
def spatial_smooth(adata, radius=2):
    """
    Smooth expression by averaging over spatial neighbors.

    Useful for noisy data, but can blur boundaries.
    """
    from sklearn.neighbors import NearestNeighbors

    # Find spatial neighbors
    coords = adata.obsm['spatial']
    nn = NearestNeighbors(n_neighbors=radius, metric='euclidean')
    nn.fit(coords)
    distances, indices = nn.kneighbors(coords)

    # Smooth expression matrix
    X_smooth = adata.X.copy()
    for i in range(adata.n_obs):
        neighbors = indices[i]
        X_smooth[i] = adata.X[neighbors].mean(axis=0)

    adata.layers['smoothed'] = X_smooth

    return adata
```

### Phase 3: Spatial Clustering

**Objective**: Identify spatial domains (regions with distinct expression).

**Graph-based clustering with spatial constraints**:
```python
def spatial_clustering(adata, n_neighbors=6):
    """
    Cluster spots into spatial domains.

    Uses both expression similarity AND spatial proximity.
    """
    import scanpy as sc
    import squidpy as sq

    # PCA for dimensionality reduction
    sc.pp.pca(adata, n_comps=50)

    # Build spatial neighbor graph
    sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=n_neighbors)

    # Clustering with spatial constraints
    # Uses both PCA space and spatial graph
    sc.tl.leiden(adata, resolution=1.0, key_added='spatial_domain')

    # Visualize domains on tissue
    sc.pl.spatial(adata, color='spatial_domain', title='Spatial Domains')

    return adata
```

**Domain marker genes**:
```python
def find_domain_markers(adata):
    """
    Identify marker genes for each spatial domain.
    """
    import scanpy as sc

    # Differential expression per domain
    sc.tl.rank_genes_groups(adata, groupby='spatial_domain', method='wilcoxon')

    # Get top markers per domain
    markers = sc.get.rank_genes_groups_df(adata, group=None)

    return markers
```

### Phase 4: Spatially Variable Genes

**Objective**: Find genes with non-random spatial patterns.

**Moran's I (spatial autocorrelation)**:
```python
def identify_spatial_genes(adata):
    """
    Test for spatial autocorrelation using Moran's I.

    Moran's I > 0: Positive spatial autocorrelation (clustering)
    Moran's I ~ 0: Random spatial distribution
    Moran's I < 0: Negative autocorrelation (checkerboard)
    """
    import squidpy as sq

    # Calculate Moran's I for all genes
    sq.gr.spatial_autocorr(
        adata,
        mode='moran',
        n_perms=100,
        n_jobs=-1
    )

    # Results in adata.uns['moranI']
    spatial_genes = adata.uns['moranI'].sort_values('I', ascending=False)

    # Filter significant spatial genes (FDR < 0.05)
    sig_spatial = spatial_genes[spatial_genes['pval_norm_fdr_bh'] < 0.05]

    return sig_spatial
```

**Spatial pattern classification**:
```python
def classify_spatial_patterns(adata, spatial_genes):
    """
    Classify types of spatial patterns.

    Pattern types:
    - Gradient: Smooth directional change
    - Hotspot: Localized high expression
    - Boundary: Expression at domain edges
    - Periodic: Regular spacing
    """
    patterns = {}

    for gene in spatial_genes.index[:100]:  # Top 100 spatial genes
        # Get expression and coordinates
        expr = adata[:, gene].X.toarray().flatten()
        coords = adata.obsm['spatial']

        # Detect pattern type
        pattern_type = detect_pattern_type(expr, coords)
        patterns[gene] = pattern_type

    return patterns
```

### Phase 5: Neighborhood Analysis

**Objective**: Analyze cell-cell proximity and spatial niches.

**Define spatial neighborhoods**:
```python
def analyze_neighborhoods(adata, radius=150):
    """
    Analyze spatial neighborhood composition.

    For each spot, characterize its microenvironment.
    """
    import squidpy as sq

    # Calculate neighborhood enrichment
    # Tests if cell types are enriched in proximity
    sq.gr.nhood_enrichment(adata, cluster_key='spatial_domain')

    # Visualize neighborhood enrichment
    sq.pl.nhood_enrichment(adata, cluster_key='spatial_domain')

    # Results: which domains are spatially proximal?

    return adata
```

**Interaction zones**:
```python
def identify_interaction_zones(adata, domain_a, domain_b):
    """
    Find boundary regions between two spatial domains.

    These are hotspots for cell-cell interactions.
    """
    # Get spots from each domain
    spots_a = adata.obs['spatial_domain'] == domain_a
    spots_b = adata.obs['spatial_domain'] == domain_b

    # Find spots that neighbor the other domain
    # (spots from A that have neighbors in B)
    coords = adata.obsm['spatial']
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=6)
    nn.fit(coords)
    distances, indices = nn.kneighbors(coords)

    interaction_spots = []
    for i, spot_in_a in enumerate(spots_a):
        if spot_in_a:
            neighbors = indices[i]
            if any(spots_b[neighbors]):
                interaction_spots.append(i)

    # Mark interaction zone
    adata.obs['interaction_zone'] = False
    adata.obs.loc[interaction_spots, 'interaction_zone'] = True

    return adata
```

### Phase 6: Integration with Single-Cell RNA-seq

**Objective**: Map cell types from scRNA-seq to spatial locations.

**Cell type deconvolution**:
```python
def deconvolve_cell_types(adata_spatial, adata_sc):
    """
    Predict cell type composition per spatial spot.

    Uses scRNA-seq reference to deconvolve Visium spots.
    Methods: Cell2location, Tangram, SPOTlight
    """
    import cell2location

    # Prepare single-cell reference
    # Extract signature genes per cell type
    cell_type_signatures = extract_signatures(adata_sc)

    # Run cell2location
    # Estimates cell type abundances per spot
    mod = cell2location.models.Cell2location(
        adata_spatial,
        cell_state_df=cell_type_signatures
    )

    mod.train(max_epochs=30000)

    # Add cell type proportions to adata_spatial
    adata_spatial.obsm['cell_type_fractions'] = mod.get_cell_type_fractions()

    return adata_spatial
```

**Spatial cell type mapping**:
```python
def map_cell_types_spatial(adata):
    """
    Visualize cell type spatial distributions.
    """
    import scanpy as sc

    # For each cell type, plot abundance on tissue
    cell_types = adata.obsm['cell_type_fractions'].columns

    for ct in cell_types:
        sc.pl.spatial(
            adata,
            color=adata.obsm['cell_type_fractions'][ct],
            title=f'{ct} Spatial Distribution'
        )
```

### Phase 7: Spatial Cell Communication

**Objective**: Map ligand-receptor interactions in tissue context.

**Spatial proximity-based communication**:
```python
def spatial_cell_communication(adata):
    """
    Identify cell-cell communication based on spatial proximity.

    Requires:
    - Cell type annotations (from deconvolution)
    - Ligand-receptor database (OmniPath)
    """
    import squidpy as sq
    from tooluniverse import ToolUniverse

    tu = ToolUniverse()

    # Get ligand-receptor pairs from OmniPath
    lr_pairs = tu.run_one_function({
        "name": "OmniPath_get_ligand_receptor_interactions",
        "arguments": {"partners": ""}  # Get all pairs
    })

    # For each cell type pair that are spatially proximal
    # Calculate interaction scores
    sq.gr.ligrec(
        adata,
        n_perms=100,
        cluster_key='cell_type',
        interactions=lr_pairs,
        copy=False
    )

    # Visualize significant interactions
    sq.pl.ligrec(adata, cluster_key='cell_type')

    return adata
```

**Communication hotspot mapping**:
```python
def map_communication_hotspots(adata, ligand, receptor):
    """
    Map spatial locations of specific L-R interactions.
    """
    import matplotlib.pyplot as plt

    # Get ligand expression
    ligand_expr = adata[:, ligand].X.toarray().flatten()

    # Get receptor expression
    receptor_expr = adata[:, receptor].X.toarray().flatten()

    # Interaction score = ligand × receptor
    interaction_score = ligand_expr * receptor_expr

    # Add to adata
    adata.obs[f'{ligand}_{receptor}_score'] = interaction_score

    # Visualize on tissue
    sc.pl.spatial(adata, color=f'{ligand}_{receptor}_score',
                  title=f'{ligand}-{receptor} Interaction Hotspots')
```

### Phase 8: Spatial Report Generation

**Generate comprehensive spatial report**:

```markdown
# Spatial Transcriptomics Analysis Report

## Dataset Summary
- **Platform**: 10x Visium
- **Tissue**: Breast cancer tumor section
- **Spots**: 3,562 (after QC filtering)
- **Genes**: 18,432 detected
- **Resolution**: 55μm spot diameter (~50 cells/spot)

## Quality Control
- **Mean genes per spot**: 3,245
- **Mean UMI counts**: 12,543
- **Mitochondrial content**: 8.2% average
- **Tissue coverage**: 85% of capture area

## Spatial Domains Identified
- **7 distinct spatial domains** detected via graph-based clustering
  - Domain 1: Tumor core (32% of tissue)
  - Domain 2: Invasive margin (18%)
  - Domain 3: Stromal region (25%)
  - Domain 4: Immune infiltrate (12%)
  - Domain 5: Necrotic region (8%)
  - Domain 6: Normal epithelium (3%)
  - Domain 7: Adipose tissue (2%)

## Top Marker Genes per Domain

### Domain 1 (Tumor Core)
- EPCAM, KRT19, MKI67, CCNB1, TOP2A (proliferative tumor)

### Domain 2 (Invasive Margin)
- VIM, FN1, MMP2, SNAI2 (EMT signature)

### Domain 4 (Immune Infiltrate)
- CD3D, CD8A, CD4, PTPRC (T cell enriched)
- CD68, CD14 (macrophage enriched)

## Spatially Variable Genes
- **456 genes with significant spatial patterns** (Moran's I, FDR < 0.05)

### Top 10 Spatial Genes
1. **MKI67** (I=0.82) - Hotspot pattern in tumor core
2. **CD8A** (I=0.78) - Gradient from margin to stroma
3. **VIM** (I=0.75) - Boundary enrichment at invasive margin
4. **COL1A1** (I=0.71) - Stromal-specific expression
5. **EPCAM** (I=0.69) - Tumor region pattern

## Cell Type Deconvolution
Integration with scRNA-seq reference (Bassez et al. 2021)

### Cell Type Spatial Distributions
- **Tumor cells**: Concentrated in core, sparse at margin
- **T cells**: Enriched at invasive margin and infiltrate zones
- **CAFs**: Stromal region and invasive margin
- **Macrophages**: Scattered, enriched near necrosis
- **B cells**: Lymphoid aggregates (2% of tissue)

### Tumor Microenvironment Composition
- Tumor core: 85% tumor cells, 10% CAFs, 5% immune
- Invasive margin: 45% tumor, 30% CAFs, 25% immune (T cell rich)
- Immune infiltrate: 70% T cells, 20% macrophages, 10% B cells

## Spatial Cell Communication

### Top L-R Interactions (Spatially Proximal)
1. **Tumor → T cell**: CD274 (PD-L1) → PDCD1 (PD-1)
   - Hotspot: Invasive margin
   - Interpretation: Immune checkpoint evasion
2. **CAF → Tumor**: TGFB1 → TGFBR2
   - Hotspot: Stromal-tumor interface
   - Interpretation: TGF-β-driven EMT
3. **Macrophage → Tumor**: TNF → TNFRSF1A
   - Scattered across tumor
   - Interpretation: Inflammatory signaling

### Interaction Zones
- **Tumor-Immune Interface**: 245 spots (7% of tissue)
  - High expression: CXCL10, CXCL9 (chemokines)
  - T cell recruitment and activation
- **Stromal-Tumor Interface**: 387 spots (11% of tissue)
  - High expression: MMP2, MMP9 (matrix remodeling)
  - Invasion-promoting niche

## Spatial Gradients
- **Hypoxia gradient**: HIF1A, VEGFA increase toward tumor core
- **Proliferation gradient**: MKI67, TOP2A decrease from core to margin
- **Immune gradient**: CD8A, GZMB peak at invasive margin

## Biological Interpretation
Spatial analysis reveals distinct tumor microenvironment organization:

1. **Tumor core**: Highly proliferative, hypoxic, immune-excluded
2. **Invasive margin**: Active EMT, high immune infiltration, checkpoint expression
3. **Stromal barrier**: CAF-rich, matrix remodeling, immunosuppressive signals

The invasive margin shows hallmarks of immune-tumor interaction with
PD-L1/PD-1 checkpoint engagement, suggesting potential for checkpoint
blockade therapy. CAF-mediated TGF-β signaling may drive EMT and therapy
resistance at tumor-stroma interface.

## Clinical Relevance
- **Checkpoint inhibitor response**: High immune infiltration at margin suggests potential
- **Resistance mechanisms**: CAF barrier and TGF-β signaling
- **Biomarkers**: Spatial arrangement of immune cells more predictive than bulk tumor metrics
```

---

## Integration with ToolUniverse Skills

| Skill | Used For | Phase |
|-------|----------|-------|
| `tooluniverse-single-cell` | scRNA-seq reference for deconvolution | Phase 6 |
| `tooluniverse-single-cell` (Phase 10) | L-R database for communication | Phase 7 |
| `tooluniverse-gene-enrichment` | Pathway enrichment for spatial domains | Phase 3 |
| `tooluniverse-multi-omics-integration` | Integrate with other omics | Phase 8 |

---

## Example Use Cases

### Use Case 1: Tumor Microenvironment Mapping

**Question**: "Map the spatial organization of tumor, immune, and stromal cells"

**Workflow**:
1. Load Visium data, QC and normalize
2. Spatial clustering → 7 domains identified
3. Cell type deconvolution using scRNA-seq reference
4. Map cell type distributions spatially
5. Identify interaction zones (tumor-immune, tumor-stroma)
6. Analyze L-R interactions in each zone
7. Report: Comprehensive TME spatial architecture

### Use Case 2: Developmental Gradient Analysis

**Question**: "Identify spatial gene expression gradients in developing tissue"

**Workflow**:
1. Load spatial data (e.g., mouse embryo)
2. Identify spatially variable genes
3. Classify gradient patterns (anterior-posterior, dorsal-ventral)
4. Map morphogen expression (WNT, BMP, FGF)
5. Correlate with cell fate markers
6. Report: Developmental spatial patterns

### Use Case 3: Brain Region Identification

**Question**: "Automatically segment brain tissue into anatomical regions"

**Workflow**:
1. Load Visium mouse brain data
2. Spatial clustering with high resolution
3. Match domains to known brain regions (cortex, hippocampus, etc.)
4. Identify region-specific marker genes
5. Validate with Allen Brain Atlas
6. Report: Automated brain region annotation

---

## Quantified Minimums

| Component | Requirement |
|-----------|-------------|
| Spots/cells | At least 500 spatial locations |
| QC | Filter low-quality spots, verify alignment |
| Spatial clustering | At least one method (graph-based or spatial) |
| Spatial genes | Moran's I or similar spatial test |
| Visualization | Spatial plots on tissue images |
| Report | Domains, spatial genes, visualizations |

---

## Limitations

- **Resolution**: Visium spots contain multiple cells (not single-cell)
- **Gene coverage**: Imaging methods have limited gene panels
- **3D structure**: Most platforms are 2D sections
- **Tissue quality**: Requires well-preserved tissue for imaging
- **Computational**: Large datasets require significant memory
- **Reference dependency**: Deconvolution quality depends on scRNA-seq reference

---

## References

**Methods**:
- Squidpy: https://doi.org/10.1038/s41592-021-01358-2
- Cell2location: https://doi.org/10.1038/s41587-021-01139-4
- SpatialDE: https://doi.org/10.1038/nmeth.4636

**Platforms**:
- 10x Visium: https://www.10xgenomics.com/products/spatial-gene-expression
- MERFISH: https://doi.org/10.1126/science.aaa6090
- Slide-seq: https://doi.org/10.1126/science.aaw1219
