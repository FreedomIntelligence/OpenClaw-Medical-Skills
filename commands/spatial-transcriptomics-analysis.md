# spatial-transcriptomics-analysis

> Automated analysis pipeline for Spatial Transcriptomics (Visium, Xenium) integrating histology and gene expression.

**Available tools:** Bash, Read, Write

# Spatial Transcriptomics Skill

**Version:** 1.0.0
**Author:** MD BABU MIA, PhD
**Date:** February 2026

## Overview
This skill provides automated analysis capabilities for Spatial Transcriptomics data, specifically designed for 10x Visium and Xenium platforms. It enables the integration of histological data with gene expression profiles to uncover spatial organization of cell types.

## Capabilities
1.  **Data Loading:** Supports Spaceranger output (h5, images).
2.  **QC & Preprocessing:** Spatial QC metrics, normalization.
3.  **Spatial Variable Features:** Identification of spatially variable genes (SVGs) using Moran's I and Geary's C.
4.  **Deconvolution:** Interface for cell type deconvolution (mapping scRNA-seq to spatial).
5.  **Visualization:** Interactive spatial plots overlaying gene expression on tissue images.

## Usage
```python
from Skills.Genomics.Spatial_Transcriptomics.spatial_analyzer import SpatialAnalyzer

# Initialize
sa = SpatialAnalyzer(data_path="./data/visium_sample1")

# Run Pipeline
sa.load_data()
sa.preprocess()
sa.find_spatial_features()
sa.plot_spatial("INS", save_path="./output/insulin_spatial.png")
```

## Requirements
*   scanpy
*   squidpy
*   anndata
*   matplotlib
