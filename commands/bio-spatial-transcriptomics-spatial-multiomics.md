# bio-spatial-transcriptomics-spatial-multiomics

> Analyze high-resolution spatial platforms like Slide-seq, Stereo-seq, and Visium HD. Use when working with subcellular resolution or high-density spatial data.

## Version Compatibility

Reference examples tested with: Cellpose 3.0+, matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, scipy 1.12+, spatialdata 0.1+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Multi-omics Analysis

**"Analyze my high-resolution spatial data"** → Process subcellular-resolution spatial platforms (Xenium, MERFISH, Slide-seq, Stereo-seq) including cell segmentation, binning strategies, and multi-modal integration.
- Python: `spatialdata` + `squidpy` for unified multi-platform analysis

## Platform Comparison

| Platform | Resolution | Spots/Beads | Coverage |
|----------|------------|-------------|----------|
| Visium | 55 µm | ~5,000 | Tissue-wide |
| Visium HD | 2 µm | ~11M | Subcellular |
| Slide-seq | 10 µm | ~100,000 | High-density |
| Stereo-seq | 0.5 µm | >200M | Subcellular |
| MERFISH | Single-molecule | N/A | Targeted genes |

## Squidpy for High-Resolution Data

**Goal:** Run standard spatial analyses (autocorrelation, neighborhood enrichment, ligand-receptor) on high-resolution spatial data.

**Approach:** Adjust neighbor graph density for high-resolution platforms, then apply standard Squidpy workflows.

```python
import squidpy as sq
import scanpy as sc

# Load spatial data
adata = sc.read_h5ad('spatial_multiomics.h5ad')

# Spatial neighbors (for high-resolution, adjust n_neighs based on density)
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=10, spatial_key='spatial')

# Spatial autocorrelation (Moran's I)
sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:100])

# Neighborhood enrichment analysis
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')
sq.pl.nhood_enrichment(adata, cluster_key='cell_type')

# Ligand-receptor analysis
sq.gr.ligrec(adata, n_perms=100, cluster_key='cell_type')
```

## SpatialData Framework

**Goal:** Load and query multi-modal spatial data using the SpatialData unified representation.

**Approach:** Use spatialdata-io readers per platform, then access images, points, shapes, and tables through a single object with spatial queries.

```python
import spatialdata as sd
from spatialdata_io import read_visium, read_xenium

# Read Visium data
sdata = read_visium('visium_output/')

# Read Xenium data (10x Genomics subcellular)
sdata = read_xenium('xenium_output/')

# Read from Zarr
sdata = sd.read_zarr('experiment.zarr')

# Access different elements
images = sdata.images['morphology']
points = sdata.points['transcripts']
shapes = sdata.shapes['cell_boundaries']
table = sdata.tables['adata']

# Query by region
from spatialdata import bounding_box_query
roi = bounding_box_query(sdata, min_coordinate=[0, 0], max_coordinate=[1000, 1000], axes=['x', 'y'])
```

## Slide-seq/Stereo-seq Processing

```python
# For high-density data, bin spots into hexagonal grids
import numpy as np

# Create hexagonal bins
def hexbin_data(adata, gridsize=50):
    coords = adata.obsm['spatial']
    from matplotlib.pyplot import hexbin
    hb = hexbin(coords[:, 0], coords[:, 1], C=None, gridsize=gridsize, reduce_C_function=np.sum)
    return hb

# Squidpy visualization with hex binning
sq.pl.spatial_scatter(adata, shape='hex', size=50, color='cluster')

# Grid-based spatial neighbors for regular patterns
sq.gr.spatial_neighbors(adata, coord_type='grid', n_rings=1)
```

## Subcellular Analysis (MERFISH/Xenium)

**Goal:** Perform transcript-level and subcellular compartment analysis for single-molecule platforms.

**Approach:** Segment cells with Cellpose, then assign individual transcripts to cells based on mask coordinates.

```python
# Transcript-level analysis
# Assign transcripts to compartments
sq.gr.co_occurrence(adata, cluster_key='compartment', spatial_key='spatial')

# Cell segmentation integration
from cellpose import models
model = models.Cellpose(model_type='cyto2')
masks, flows, styles, diams = model.eval(image, diameter=30, channels=[0, 0])

# Map transcripts to cells
def assign_transcripts_to_cells(transcripts_df, masks):
    x, y = transcripts_df['x'].values.astype(int), transcripts_df['y'].values.astype(int)
    transcripts_df['cell_id'] = masks[y, x]
    return transcripts_df[transcripts_df['cell_id'] > 0]
```

## Multi-Modal Integration

**Goal:** Combine spatial gene expression with histological image features for integrated analysis.

**Approach:** Process and segment tissue images, extract image features, then correlate with gene expression.

```python
# Combine spatial transcriptomics with histology
sq.im.process(adata, layer='image', method='smooth', sigma=2)
sq.im.segment(adata, layer='image', method='watershed', thresh=0.1)

# Extract image features
sq.im.calculate_image_features(
    adata, layer='image', features=['texture', 'summary'],
    key_added='img_features', n_jobs=4
)

# Correlate image features with gene expression
from scipy.stats import pearsonr
for gene in ['marker1', 'marker2']:
    r, p = pearsonr(adata.obs['img_feature'], adata[:, gene].X.flatten())
    print(f'{gene}: r={r:.3f}, p={p:.3e}')
```

## Visium HD Specific

```python
# Visium HD produces bin files at multiple resolutions
# Load 8µm binned data (recommended starting point)
adata = sc.read_h5ad('visium_hd_8um.h5ad')

# Downsample to 16µm if needed for initial analysis
# Original 2µm data available for detailed analysis
```

## Quality Metrics

| Metric | Visium | High-Resolution |
|--------|--------|-----------------|
| Genes/spot | >2000 | >500 |
| UMI/spot | >5000 | >1000 |
| Spatial coverage | >80% | >50% |

## Related Skills

- spatial-transcriptomics/spatial-preprocessing - Standard spatial analysis
- single-cell/preprocessing - scRNA-seq concepts
- spatial-transcriptomics/image-analysis - Morphology processing
- single-cell/cell-annotation - Cell type assignment
