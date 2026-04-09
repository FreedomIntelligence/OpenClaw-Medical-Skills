# universal-single-cell-annotator

> Annotate scRNA-seq

**Available tools:** Read, Bash

# Universal Single-Cell Annotator

This skill wraps multiple cell type annotation strategies into a single Python class. It allows agents to flexibly choose between rule-based (markers), data-driven (CellTypist), or reasoning-based (LLM) approaches depending on the context.

## When to Use This Skill

*   **Initial Analysis**: When processing raw AnnData objects.
*   **Validation**: When cross-referencing automated labels with known markers.
*   **Discovery**: When identifying rare cell types using LLM reasoning on marker lists.

## Core Capabilities

1.  **Marker-Based Scoring**: Scores cells based on provided gene lists (e.g., "T-cell": ["CD3D", "CD3E"]).
2.  **Deep Learning Reference**: Wraps `celltypist` to transfer labels from massive atlases.
3.  **LLM Reasoning**: Extracts top markers per cluster and constructs prompts for LLM interpretation.

## Workflow

1.  **Load Data**: Ensure data is in `AnnData` format (standard for Scanpy).
2.  **Choose Strategy**:
    *   Use **Markers** if you have a known gene panel.
    *   Use **CellTypist** for broad immune/tissue profiling.
    *   Use **LLM** for novel clusters.
3.  **Annotate**: Run the corresponding method.
4.  **Inspect**: Check `adata.obs` for the new annotation columns.

## Example Usage

**User**: "Annotate this dataset looking for T-cells and B-cells."

**Agent Action**:
```python
from universal_annotator import UniversalAnnotator
import scanpy as sc

adata = sc.read_h5ad('data.h5ad')
annotator = UniversalAnnotator(adata)

markers = {
    'T-cell': ['CD3D', 'CD3E', 'CD8A'],
    'B-cell': ['CD79A', 'MS4A1']
}

annotator.annotate_marker_based(markers)
# Results in adata.obs['predicted_cell_type']
```
