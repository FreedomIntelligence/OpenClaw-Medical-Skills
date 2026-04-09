# bio-spatial-transcriptomics-spatial-proteomics

> Analyzes spatial proteomics data from CODEX, IMC, and MIBI platforms including cell segmentation and protein colocalization. Use when working with multiplexed imaging data, analyzing protein spatial patterns, or integrating spatial proteomics with transcriptomics.

## Version Compatibility

Reference examples tested with: anndata 0.10+, scanpy 1.10+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Proteomics Analysis

**"Analyze my CODEX/IMC spatial proteomics data"** → Process multiplexed imaging data including cell segmentation, protein phenotyping, spatial neighborhood analysis, and protein colocalization scoring.
- Python: `scimap.tl.phenotype_cells()`, `squidpy.gr.nhood_enrichment()`

## Data Loading

**Goal:** Process multiplexed spatial proteomics data (CODEX/IMC/MIBI) through cell phenotyping, spatial neighborhood analysis, and protein colocalization scoring.

**Approach:** Load the cell-by-marker intensity matrix with spatial coordinates into AnnData, normalize and rescale marker intensities, phenotype cells by marker expression gating, then analyze spatial neighborhoods and cell-cell interactions using scimap and squidpy.

```python
import scimap as sm
import anndata as ad

# Load CODEX/IMC data (cell x marker matrix with spatial coordinates)
adata = ad.read_h5ad('spatial_proteomics.h5ad')

# Required: spatial coordinates in adata.obsm['spatial']
# Required: protein intensities in adata.X
```

## Preprocessing

```python
# Log transform intensities
sm.pp.log1p(adata)

# Rescale markers (0-1 per marker)
sm.pp.rescale(adata)

# Combat batch correction if multiple FOVs
sm.pp.combat(adata, batch_key='fov')
```

## Phenotyping Cells

```python
# Manual gating approach
phenotype_markers = {
    'T_cell': ['CD3', 'CD45'],
    'B_cell': ['CD20', 'CD45'],
    'Macrophage': ['CD68', 'CD163'],
    'Tumor': ['panCK', 'Ki67']
}

sm.tl.phenotype_cells(adata, phenotype=phenotype_markers,
                      gate=0.5, label='phenotype')

# Clustering-based phenotyping
sm.tl.cluster(adata, method='leiden', resolution=1.0)
```

## Spatial Analysis

```python
# Build spatial neighbors graph
sm.tl.spatial_distance(adata, x_coordinate='X', y_coordinate='Y')

# Neighborhood enrichment
sm.tl.spatial_interaction(adata, phenotype='phenotype',
                          method='knn', knn=10)

# Spatial clustering (communities of cells)
sm.tl.spatial_cluster(adata, phenotype='phenotype')
```

## Visualization

```python
# Spatial scatter plot
sm.pl.spatial_scatterPlot(adata, colorBy='phenotype',
                          x='X', y='Y', s=5)

# Heatmap of spatial interactions
sm.pl.spatial_interaction(adata)

# Marker expression overlay
sm.pl.image_viewer(adata, markers=['CD3', 'CD20', 'panCK'])
```

## Integration with Transcriptomics

```python
import squidpy as sq

# If matched spatial transcriptomics available
# Transfer labels or integrate modalities
sq.gr.spatial_neighbors(adata_protein)
sq.gr.spatial_neighbors(adata_rna)

# Compare spatial patterns across modalities
```

## Platform-Specific Notes

| Platform | Markers | Resolution | Notes |
|----------|---------|------------|-------|
| CODEX | 40-60 | Subcellular | Cyclic staining |
| IMC | 40+ | 1 um | Metal-tagged antibodies |
| MIBI | 40+ | 260 nm | Mass spectrometry |

## Related Skills

- spatial-transcriptomics/spatial-neighbors - Spatial graph construction
- spatial-transcriptomics/spatial-domains - Domain identification
- imaging-mass-cytometry/phenotyping - IMC-specific analysis
