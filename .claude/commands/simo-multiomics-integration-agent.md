# simo-multiomics-integration-agent

> AI-powered spatial integration of multi-omics datasets using probabilistic alignment for comprehensive tissue atlas construction and cellular state mapping.

**Available tools:** Read, Bash

# SIMO Multiomics Integration Agent

The **SIMO Multiomics Integration Agent** performs spatial integration of multi-omics datasets through probabilistic alignment. Unlike previous tools limited to transcriptomics, SIMO integrates spatial transcriptomics with single-cell RNA-seq and expands to chromatin accessibility, DNA methylation, and proteomics data.

## When to Use This Skill

* When integrating spatial transcriptomics with single-cell multi-omics data.
* For constructing comprehensive tissue atlases with spatial context.
* To map epigenomic states (ATAC-seq, methylation) onto spatial coordinates.
* When analyzing multi-modal cellular phenotypes in tissue architecture.
* For spatial deconvolution combining multiple modalities.

## Core Capabilities

1. **Spatial-scRNA Integration**: Probabilistically align single-cell RNA-seq to spatial coordinates.

2. **Chromatin Accessibility Mapping**: Project scATAC-seq profiles onto spatial tissue locations.

3. **DNA Methylation Spatial Mapping**: Integrate single-cell methylation data with spatial context.

4. **Multi-Modal Fusion**: Combine transcriptomic, epigenomic, and proteomic layers.

5. **Probabilistic Cell-Type Assignment**: Assign cell types to spatial spots with uncertainty quantification.

6. **Spatial Niche Identification**: Discover cellular niches defined by multi-omic signatures.

## Supported Modalities

| Modality | Input Format | Spatial Reference |
|----------|--------------|-------------------|
| scRNA-seq | AnnData, Seurat | Visium, MERFISH, Xenium |
| scATAC-seq | SnapATAC2, ArchR | Visium, Slide-seq |
| scMethyl | Bismark, allcools | Any spatial modality |
| CITE-seq (protein) | AnnData | Spatial proteomics |
| Multi-ome (RNA+ATAC) | Muon, SnapATAC2 | All platforms |

## Integration Algorithm

| Step | Method | Purpose |
|------|--------|---------|
| Feature Selection | HVG + marker genes | Reduce dimensionality |
| Embedding | Variational autoencoder | Shared latent space |
| Alignment | Optimal transport | Probabilistic matching |
| Spatial Mapping | Gaussian processes | Smooth spatial predictions |
| Uncertainty | Posterior sampling | Confidence intervals |

## Workflow

1. **Input**: Spatial transcriptomics (Visium/MERFISH/Xenium), reference single-cell multi-omics.

2. **Preprocessing**: Normalize, select features, QC both datasets.

3. **Embedding**: Learn joint latent representation across modalities.

4. **Probabilistic Alignment**: Compute cell-to-spot assignment probabilities.

5. **Spatial Imputation**: Transfer modalities to spatial coordinates.

6. **Niche Analysis**: Identify spatial domains by multi-omic signatures.

7. **Output**: Integrated spatial multi-omics object, niche assignments, visualizations.

## Example Usage

**User**: "Integrate our scRNA-seq and scATAC-seq data with the spatial transcriptomics to understand chromatin states in different tissue regions."

**Agent Action**:
```bash
python3 Skills/Genomics/SIMO_Multiomics_Integration_Agent/simo_integration.py \
    --spatial_data visium_data.h5ad \
    --scrna_ref scrna_atlas.h5ad \
    --scatac_ref scatac_atlas.h5ad \
    --modalities rna,atac \
    --n_spots_per_cell 5 \
    --uncertainty_quantification true \
    --output integrated_spatial_multiome.h5ad
```

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Integrated Object | Multi-modal spatial data | AnnData/Muon |
| Cell Type Map | Spatial cell type assignments | GeoTIFF, CSV |
| Chromatin Accessibility Map | Spatial ATAC patterns | BigWig, CSV |
| Niche Assignments | Spatial domain labels | CSV, Zarr |
| Uncertainty Maps | Per-spot confidence | GeoTIFF |
| Gene Activity Scores | ATAC-derived gene activity | AnnData layer |

## Spatial Platforms Supported

| Platform | Resolution | Spots/Cells | Genes |
|----------|------------|-------------|-------|
| 10x Visium | 55 μm | ~5,000 | Whole transcriptome |
| 10x Visium HD | 8 μm | ~300,000 | Whole transcriptome |
| 10x Xenium | Subcellular | >100,000 | 300-5,000 panel |
| MERFISH | Subcellular | >1M | 100-10,000 panel |
| Slide-seq | 10 μm | ~60,000 | Whole transcriptome |
| CosMx | Subcellular | >1M | 1,000-6,000 panel |

## AI/ML Components

**Variational Integration**:
- Multi-modal VAE for joint embeddings
- Contrastive learning for modality alignment
- Batch correction across datasets

**Probabilistic Mapping**:
- Optimal transport with entropic regularization
- Gaussian process spatial smoothing
- Bayesian uncertainty estimation

**Niche Discovery**:
- Multi-view clustering
- Spatial autocorrelation (Moran's I)
- Graph neural networks for niche boundaries

## Prerequisites

* Python 3.10+
* Scanpy, Squidpy, Muon
* scvi-tools, SnapATAC2
* POT (Python Optimal Transport)
* PyTorch, GPyTorch

## Related Skills

* scGPT_Agent - For foundation model embeddings
* Spatial_Epigenomics_Agent - For spatial epigenomics analysis
* Cell_Cell_Communication - For ligand-receptor analysis
* Nicheformer_Spatial_Agent - For spatial niche modeling

## Special Considerations

1. **Batch Effects**: Pre-align datasets from different protocols
2. **Spot Deconvolution**: Lower resolution platforms need deconvolution
3. **Sparsity**: scATAC data requires aggregation strategies
4. **Compute**: Multi-modal integration is memory-intensive
5. **Validation**: Verify spatial patterns with known marker distributions

## Applications

| Application | Use Case |
|-------------|----------|
| Tumor Microenvironment | Map chromatin states of immune infiltrates |
| Development | Track lineage chromatin dynamics spatially |
| Neurodegeneration | Spatial mapping of epigenetic changes |
| Fibrosis | Understand spatial activation programs |

## Author

AI Group - Biomedical AI Platform
