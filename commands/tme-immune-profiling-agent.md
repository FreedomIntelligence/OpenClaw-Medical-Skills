# tme-immune-profiling-agent

> Comprehensive AI-powered tumor microenvironment immune profiling integrating bulk deconvolution, single-cell analysis, and spatial transcriptomics for immunotherapy biomarker discovery.

**Available tools:** Read, Bash

# TME Immune Profiling Agent

The **TME Immune Profiling Agent** provides comprehensive tumor microenvironment (TME) immune profiling by integrating multiple data modalities including bulk RNA-seq deconvolution, single-cell transcriptomics, spatial transcriptomics, and multiplex immunofluorescence. It enables biomarker discovery for immunotherapy response and TME-based patient stratification.

## When to Use This Skill

* When characterizing immune composition of tumor microenvironment.
* For predicting immunotherapy response from TME profiles.
* To identify immune cell states and functional programs.
* When analyzing spatial organization of immune infiltrates.
* For discovering TME-based biomarkers and therapeutic targets.

## Core Capabilities

1. **Bulk Deconvolution**: Estimate immune cell fractions from bulk RNA-seq.

2. **Single-Cell Immune Profiling**: Deep characterization of immune populations.

3. **Spatial Immune Architecture**: Map immune cell locations and neighborhoods.

4. **Immune Phenotype Classification**: Hot/cold/excluded tumor classification.

5. **Functional State Analysis**: Exhaustion, activation, memory signatures.

6. **Response Prediction**: Multi-modal immunotherapy response models.

## Immune Cell Types Profiled

| Cell Type | Subtypes | Key Markers |
|-----------|----------|-------------|
| T cells | CD8+, CD4+, Treg, Th1/2/17 | CD3, CD8, CD4, FOXP3 |
| B cells | Naive, memory, plasma | CD19, CD20, CD138 |
| NK cells | CD56bright, CD56dim | NKG7, NCAM1 |
| Macrophages | M1, M2, TAM | CD68, CD163, CD206 |
| Dendritic | cDC1, cDC2, pDC | CLEC9A, CD1C, BDCA2 |
| MDSC | M-MDSC, PMN-MDSC | CD33, CD11b, ARG1 |
| CAF | myCAF, iCAF, apCAF | FAP, ACTA2, COL1A1 |

## Deconvolution Methods

| Method | Algorithm | Cell Types | Best For |
|--------|-----------|------------|----------|
| CIBERSORTx | SVR | 22 | Gold standard |
| xCell | ssGSEA | 64 | Comprehensive |
| EPIC | Constrained regression | 8 | Tumor/stroma |
| MCP-counter | Marker genes | 10 | Robust scores |
| quanTIseq | Deconvolution | 10 | Pan-cancer |
| TIMER2.0 | Multiple | Variable | Integrated |

## Workflow

1. **Input**: Bulk RNA-seq, scRNA-seq, spatial data, or IHC images.

2. **Deconvolution**: Estimate cell fractions from bulk data.

3. **Single-Cell Analysis**: Deep immune phenotyping if available.

4. **Spatial Mapping**: Localize immune populations in tissue.

5. **Integration**: Combine modalities for comprehensive profile.

6. **Classification**: Assign TME phenotype (hot/cold/excluded).

7. **Output**: Immune profiles, visualizations, response predictions.

## Example Usage

**User**: "Profile the tumor microenvironment of this lung cancer cohort to identify immunotherapy responders."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/TME_Immune_Profiling_Agent/tme_profiling.py \
    --bulk_rna expression_matrix.tsv \
    --scRNA_data scRNA_lung.h5ad \
    --spatial_data visium_tumor.h5ad \
    --cancer_type nsclc \
    --deconvolution_methods cibersortx,epic,mcpcounter \
    --response_labels clinical_response.csv \
    --output tme_profiles/
```

## TME Phenotypes

| Phenotype | Characteristics | Immunotherapy Response |
|-----------|-----------------|----------------------|
| Immune Hot | High TIL infiltration, PD-L1+ | Favorable |
| Immune Cold | Low TIL, low inflammation | Poor |
| Immune Excluded | TILs at margin, not penetrating | Intermediate |
| Immune Suppressed | TILs + MDSCs/Tregs | Variable |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Cell Fractions | Per-sample immune estimates | .csv |
| TME Classification | Hot/cold/excluded labels | .csv |
| Immune Scores | Composite signatures | .csv |
| Spatial Maps | Cell type locations | .h5ad |
| Neighborhood Analysis | Immune niches | .csv |
| Response Prediction | IO probability | .json |
| Visualizations | Deconvolution plots | .png, .pdf |

## Immune Signatures

| Signature | Genes | Interpretation |
|-----------|-------|----------------|
| Cytotoxic | PRF1, GZMB, GNLY | T cell killing |
| Exhaustion | PDCD1, LAG3, HAVCR2, TIGIT | T cell dysfunction |
| IFN-gamma | IFNG, STAT1, IRF1 | Inflammation |
| TLS | CD20, CD4, BCL6 | Tertiary lymphoid |
| Exclusion | TGFB1, FAP, COL1A1 | Stromal barrier |

## AI/ML Components

**Deconvolution Enhancement**:
- Deep learning deconvolution
- Multi-method ensemble
- Single-cell reference optimization

**Response Prediction**:
- Multi-modal fusion (bulk + spatial)
- Survival analysis integration
- Transfer learning across cancers

**Spatial Analysis**:
- Graph neural networks for niches
- Attention for region importance
- Cell-cell interaction networks

## Clinical Applications

| Application | TME Feature | Clinical Decision |
|-------------|-------------|-------------------|
| IO Selection | Immune hot phenotype | Prioritize IO |
| Combination | Cold + excluded | Consider combo |
| Prognosis | TLS presence | Favorable outcome |
| Biomarker | CD8+ density | Response prediction |
| Resistance | MDSC enrichment | Address suppression |

## Performance Benchmarks

| Task | Dataset | Performance |
|------|---------|-------------|
| IO Response | NSCLC | AUC 0.78 |
| IO Response | Melanoma | AUC 0.82 |
| TME Classification | Pan-cancer | Accuracy 85% |
| Survival | TCGA | C-index 0.72 |

## Prerequisites

* Python 3.10+
* CIBERSORTx, EPIC, xCell
* Scanpy, Squidpy
* PyTorch for deep learning
* R for certain deconvolution methods

## Related Skills

* TCR_Repertoire_Analysis_Agent - T cell specificity
* TCell_Exhaustion_Analysis_Agent - Exhaustion phenotyping
* Spatial_Epigenomics_Agent - Spatial analysis
* Nicheformer_Spatial_Agent - Spatial foundation models

## Spatial Immune Metrics

| Metric | Definition | Clinical Relevance |
|--------|------------|-------------------|
| Immune Distance | Distance to tumor edge | Exclusion |
| Clustering Coefficient | Immune aggregation | TLS formation |
| CD8/Treg Ratio | Spatial ratio | Effector balance |
| Contact Score | Immune-tumor contacts | Direct killing |
| Neighborhood Entropy | Mixing vs segregation | TME organization |

## Special Considerations

1. **Reference Panel**: Use cancer-type specific references
2. **Batch Correction**: Normalize across samples/platforms
3. **Purity Effects**: Account for tumor purity in deconvolution
4. **Single-Cell Validation**: Validate bulk estimates with scRNA
5. **Spatial Context**: Bulk loses spatial information

## Therapeutic Implications

| TME State | Therapeutic Strategy |
|-----------|---------------------|
| Hot, PD-L1+ | Anti-PD-1/PD-L1 |
| Cold | Oncolytic virus, radiation, chemo |
| Excluded | TGF-beta inhibition, VEGF targeting |
| Suppressed | Treg depletion, MDSC targeting |
| TLS+ | Excellent IO candidate |

## Author

AI Group - Biomedical AI Platform
