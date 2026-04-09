# bio-spatial-transcriptomics-spatial-neighbors

> Build spatial neighbor graphs for spatial transcriptomics data using Squidpy. Compute k-nearest neighbors, Delaunay triangulation, and radius-based connectivity for downstream spatial analyses. Use when building spatial neighborhood graphs.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, scikit-learn 1.4+, scipy 1.12+, squidpy 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Neighbor Graphs

**"Build a spatial neighborhood graph"** → Construct spatial connectivity graphs using k-nearest neighbors, Delaunay triangulation, or radius-based methods for downstream spatial statistics.
- Python: `squidpy.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)`

Build spatial neighbor graphs for connectivity-based analyses.

## Required Imports

```python
import squidpy as sq
import scanpy as sc
import numpy as np
```

## Build K-Nearest Neighbors Graph

**Goal:** Construct a spatial KNN graph connecting each spot to its nearest spatial neighbors.

**Approach:** Use Squidpy's `spatial_neighbors` with k-nearest neighbors on coordinate distances.

```python
# Build spatial KNN graph
sq.gr.spatial_neighbors(adata, n_neighs=6, coord_type='generic')

# Check the graph
print(f"Connectivities shape: {adata.obsp['spatial_connectivities'].shape}")
print(f"Distances shape: {adata.obsp['spatial_distances'].shape}")
```

## Build Delaunay Triangulation Graph

```python
# Delaunay triangulation (natural neighbors)
sq.gr.spatial_neighbors(adata, delaunay=True, coord_type='generic')
```

## Radius-Based Neighbors

```python
# Connect all spots within a radius
sq.gr.spatial_neighbors(adata, radius=100, coord_type='generic')
```

## For Visium Data (Grid Structure)

```python
# For Visium hexagonal grid, use n_rings
sq.gr.spatial_neighbors(adata, n_rings=1, coord_type='grid')  # 6 immediate neighbors
sq.gr.spatial_neighbors(adata, n_rings=2, coord_type='grid')  # Extended neighborhood
```

## Access Neighbor Information

```python
# Get connectivities as sparse matrix
conn = adata.obsp['spatial_connectivities']
print(f'Edges in graph: {conn.nnz}')
print(f'Mean neighbors per spot: {conn.nnz / adata.n_obs:.1f}')

# Get distances
dist = adata.obsp['spatial_distances']
nonzero_dist = dist.data[dist.data > 0]
print(f'Mean neighbor distance: {nonzero_dist.mean():.1f}')
```

## Get Neighbors for a Specific Spot

```python
from scipy.sparse import csr_matrix

spot_idx = 0
conn = adata.obsp['spatial_connectivities']

# Get neighbor indices
neighbor_indices = conn[spot_idx].nonzero()[1]
print(f'Spot {spot_idx} has {len(neighbor_indices)} neighbors: {neighbor_indices}')

# Get distances to neighbors
dist = adata.obsp['spatial_distances']
neighbor_distances = dist[spot_idx, neighbor_indices].toarray().flatten()
print(f'Distances: {neighbor_distances}')
```

## Build Expression-Based Neighbors

```python
# Standard expression-based neighbors (for comparison)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Now adata has both:
# - adata.obsp['spatial_connectivities'] (spatial)
# - adata.obsp['connectivities'] (expression)
```

## Combine Spatial and Expression Neighbors

**Goal:** Create a unified neighbor graph that balances spatial proximity with expression similarity.

**Approach:** Build separate spatial and expression neighbor graphs, normalize each, then combine with a tunable weight parameter.

```python
# Build both graphs
sq.gr.spatial_neighbors(adata, n_neighs=6, coord_type='generic')
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Weighted combination (manual)
alpha = 0.5  # Weight for spatial vs expression
spatial_conn = adata.obsp['spatial_connectivities']
expr_conn = adata.obsp['connectivities']

# Normalize and combine
from sklearn.preprocessing import normalize
spatial_norm = normalize(spatial_conn, norm='l1', axis=1)
expr_norm = normalize(expr_conn, norm='l1', axis=1)
combined = alpha * spatial_norm + (1 - alpha) * expr_norm

adata.obsp['combined_connectivities'] = combined
```

## Visualize Neighbor Graph

**Goal:** Display the spatial neighbor graph overlaid on tissue coordinates for visual inspection.

**Approach:** Draw edges between connected spots and scatter plot the spot positions.

```python
import matplotlib.pyplot as plt

# Get coordinates
coords = adata.obsm['spatial']
conn = adata.obsp['spatial_connectivities']

fig, ax = plt.subplots(figsize=(10, 10))

# Draw edges
rows, cols = conn.nonzero()
for i, j in zip(rows, cols):
    if i < j:  # Avoid drawing twice
        ax.plot([coords[i, 0], coords[j, 0]], [coords[i, 1], coords[j, 1]], 'k-', alpha=0.1, linewidth=0.5)

# Draw nodes
ax.scatter(coords[:, 0], coords[:, 1], s=10, c='blue', alpha=0.5)
ax.set_aspect('equal')
plt.title('Spatial neighbor graph')
```

## Compute Graph Statistics

**Goal:** Calculate summary statistics of the spatial neighbor graph (nodes, edges, connectivity).

**Approach:** Convert the sparse connectivity matrix to a NetworkX graph and compute standard graph metrics.

```python
import networkx as nx
from scipy.sparse import csr_matrix

conn = adata.obsp['spatial_connectivities']
G = nx.from_scipy_sparse_array(conn)

print(f'Nodes: {G.number_of_nodes()}')
print(f'Edges: {G.number_of_edges()}')
print(f'Average degree: {2 * G.number_of_edges() / G.number_of_nodes():.2f}')
print(f'Connected components: {nx.number_connected_components(G)}')
```

## Store Multiple Neighbor Graphs

```python
# Store different neighborhood sizes
for n_neighs in [4, 6, 10]:
    sq.gr.spatial_neighbors(adata, n_neighs=n_neighs, coord_type='generic')
    adata.obsp[f'spatial_conn_{n_neighs}'] = adata.obsp['spatial_connectivities'].copy()
    adata.obsp[f'spatial_dist_{n_neighs}'] = adata.obsp['spatial_distances'].copy()
```

## Related Skills

- spatial-statistics - Use neighbor graph for spatial statistics
- spatial-domains - Identify domains using spatial graph
- single-cell/clustering - Non-spatial neighbor graphs
