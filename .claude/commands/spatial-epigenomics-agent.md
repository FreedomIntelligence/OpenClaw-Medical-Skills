# spatial-epigenomics-agent

> AI-powered spatial epigenomics analysis combining chromatin accessibility, histone modifications, and DNA methylation with spatial coordinates for tissue architecture mapping.

**Available tools:** Read, Bash

# Spatial Epigenomics Agent

The **Spatial Epigenomics Agent** analyzes spatial epigenomic data combining chromatin accessibility (ATAC-seq), histone modifications (CUT&Tag), and DNA methylation with spatial coordinates. It maps regulatory landscapes across tissue architecture to understand cell-state regulation in spatial context.

## When to Use This Skill

* When analyzing spatial ATAC-seq data (Slide-seq + ATAC, DBiT-seq).
* To map chromatin accessibility across tissue microenvironments.
* For spatial profiling of histone modifications (H3K27ac, H3K4me3, H3K27me3).
* When integrating spatial epigenomics with spatial transcriptomics.
* To identify spatially-variable regulatory elements and enhancers.

## Core Capabilities

1. **Spatial ATAC Analysis**: Process spatial chromatin accessibility data to identify open chromatin regions with spatial coordinates.

2. **Spatial CUT&Tag**: Analyze spatially-resolved histone modification profiles (H3K27ac for enhancers, H3K4me3 for promoters).

3. **Spatial Methylation**: Map DNA methylation patterns across tissue sections using spatial bisulfite methods.

4. **Multi-Modal Integration**: Combine spatial epigenomics with spatial transcriptomics for regulatory network inference.

5. **Regulatory Element Mapping**: Identify spatially-variable enhancers, promoters, and silencers.

6. **3D Chromatin Organization**: Integrate with MERFISH/seqFISH+ for spatial chromatin organization.

## Technologies Supported

| Technology | Epigenetic Mark | Resolution | Method |
|------------|-----------------|------------|--------|
| Spatial-ATAC-seq | Open chromatin | ~10-50μm | Microfluidic barcoding |
| DBiT-seq | ATAC + expression | ~10μm | Deterministic barcoding |
| Spatial-CUT&Tag | Histone marks | ~50μm | Cleavage under targets |
| Spatial-MethylSeq | DNA methylation | Variable | Bisulfite conversion |
| MERFISH + epigenetics | 3D organization | Single-cell | Imaging-based |

## Workflow

1. **Input**: Spatial epigenomics data (BAM files + spatial coordinates) or processed peak matrices.

2. **Preprocessing**: Alignment, deduplication, peak calling with spatial awareness.

3. **Spatial Clustering**: Identify spatial domains with similar epigenetic profiles.

4. **Peak Annotation**: Map peaks to genomic features (promoters, enhancers, gene bodies).

5. **Motif Analysis**: Identify transcription factor binding motifs in spatially-variable peaks.

6. **Integration**: Combine with expression data for regulatory inference.

7. **Output**: Spatial peak maps, regulatory networks, domain annotations.

## Example Usage

**User**: "Analyze this spatial ATAC-seq dataset to identify spatially-variable regulatory elements in the tumor microenvironment."

**Agent Action**:
```bash
python3 Skills/Genomics/Spatial_Epigenomics_Agent/spatial_epigenomics.py \
    --input spatial_atac_fragments.tsv.gz \
    --coordinates spot_coordinates.csv \
    --peaks macs2_peaks.bed \
    --spatial_variable true \
    --motif_db jaspar_2024 \
    --integrate_with spatial_rna.h5ad \
    --output spatial_epi_results/
```

## Analysis Modules

**1. Spatial Peak Calling**
- Adapted MACS2/Genrich for spatial data
- Spatial autocorrelation of accessibility
- Pseudo-bulk and single-spot approaches

**2. Spatial Domain Detection**
- Graph-based clustering (Leiden, Louvain)
- Hidden Markov Random Fields
- Deep learning segmentation

**3. Transcription Factor Analysis**
- ChromVAR for TF activity scores
- SCENIC+ for spatial regulon inference
- Motif enrichment in spatial domains

**4. Enhancer-Gene Linking**
- Activity-by-contact (ABC) model adaptation
- Spatial correlation of enhancer accessibility with gene expression
- Chromatin loop integration

## Integration with Spatial Transcriptomics

```
Spatial ATAC-seq          Spatial RNA-seq
      |                        |
      v                        v
  Peak Matrix            Expression Matrix
      |                        |
      +--------> Integration <-+
                     |
                     v
         Regulatory Network
         (Enhancer -> TF -> Gene)
```

## Key Metrics

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| TSS Enrichment | Signal at transcription start sites | >4 good quality |
| FRiP | Fraction reads in peaks | >30% |
| Spatial autocorrelation | Moran's I for epigenetic features | 0.2-0.8 |
| Spots per gene | Detection sensitivity | 100-500 |

## Prerequisites

* Python 3.10+
* SnapATAC2, ArchR for ATAC analysis
* Squidpy, Scanpy for spatial analysis
* MACS2/Genrich for peak calling

## Related Skills

* Spatial_Transcriptomics - For gene expression spatial mapping
* Epigenomics_MethylGPT_Agent - For methylation analysis
* Single_Cell - For non-spatial epigenomics

## Applications

1. **Tumor Microenvironment**: Map regulatory programs across tumor-stroma boundary
2. **Development**: Track enhancer activation during tissue morphogenesis
3. **Neuroanatomy**: Brain region-specific regulatory landscapes
4. **Disease Mechanisms**: Spatial dysregulation in pathology

## Author

AI Group - Biomedical AI Platform
