# cnv-caller-agent

> AI-enhanced copy number variation calling and analysis from sequencing data for cancer genomics, constitutional CNV detection, and chromosomal aberration characterization.

**Available tools:** Read, Bash

# CNV Caller Agent

The **CNV Caller Agent** provides comprehensive AI-enhanced copy number variation analysis from WGS, WES, and targeted sequencing for cancer genomics and constitutional CNV detection.

## When to Use This Skill

* When calling somatic CNVs from tumor-normal paired sequencing.
* To detect constitutional CNVs from germline sequencing.
* For allele-specific copy number analysis.
* When characterizing focal amplifications and deletions in cancer.
* To assess tumor purity and ploidy from CNV data.

## Core Capabilities

1. **Somatic CNV Calling**: Detect tumor-specific copy number alterations.

2. **Germline CNV Detection**: Identify constitutional CNVs for rare disease.

3. **Allele-Specific Analysis**: Determine allele-specific copy number and LOH.

4. **Purity/Ploidy Estimation**: Estimate tumor content and genome doubling.

5. **Focal Event Detection**: Identify amplifications and deletions of driver genes.

6. **Segmentation Optimization**: AI-enhanced breakpoint detection.

## Workflow

1. **Input**: BAM files (tumor/normal), or targeted panel data.

2. **Coverage Normalization**: GC correction, mappability adjustment.

3. **Segmentation**: Identify regions of consistent copy number.

4. **Allele-Specific**: Calculate B-allele frequency for heterozygosity.

5. **Purity/Ploidy**: Estimate sample parameters.

6. **Calling**: Assign integer copy number states.

7. **Output**: Segmented CNV calls, purity/ploidy, driver events.

## Example Usage

**User**: "Call somatic copy number alterations from this tumor-normal WES pair."

**Agent Action**:
```bash
python3 Skills/Genomics/CNV_Caller_Agent/cnv_caller.py \
    --tumor tumor.bam \
    --normal normal.bam \
    --reference GRCh38.fa \
    --method facets \
    --targets exome_targets.bed \
    --driver_genes cancer_genes.txt \
    --output cnv_results/
```

## CNV Calling Methods

| Tool | Application | Key Features |
|------|-------------|--------------|
| FACETS | Tumor WES | Purity/ploidy, allele-specific |
| ASCAT | Tumor WGS/arrays | Allele-specific, multi-clone |
| CNVkit | WES/targeted | Hybrid reference approach |
| GATK CNV | WES/WGS | GATK ecosystem integration |
| Purple | WGS | GRIDSS integration, comprehensive |
| CONICS | scRNA-seq | Single-cell CNV inference |

## Key Output Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| Purity | Tumor fraction | Sample quality |
| Ploidy | Average copy number | Genome doubling |
| LOH | Loss of heterozygosity | Regions of allele loss |
| SCNA burden | Total altered fraction | Genomic instability |
| Focal events | Amplifications/deletions | Driver candidates |

## Cancer Driver CNVs

| Gene | Alteration | Cancer Type |
|------|------------|-------------|
| ERBB2 (HER2) | Amplification | Breast, gastric |
| MYC | Amplification | Many cancers |
| EGFR | Amplification | Lung, GBM |
| CDK4/MDM2 | Amplification | Sarcoma, GBM |
| CDKN2A | Deletion | Many cancers |
| RB1 | Deletion | Many cancers |
| PTEN | Deletion | Prostate, GBM |

## AI/ML Enhancements

**Segmentation**:
- Deep learning for breakpoint detection
- Noise reduction in low-coverage data
- Improved sensitivity for focal events

**Quality Prediction**:
- Sample quality scoring
- Artifact detection
- Confidence estimation

**Driver Prioritization**:
- GISTIC-style analysis
- Functional impact scoring
- Pan-cancer frequency context

## Allele-Specific Copy Number

```
Total CN = Major allele + Minor allele

Examples:
- Normal: 1 + 1 = 2 (diploid)
- CN gain: 2 + 1 = 3 (trisomy)
- CN-LOH: 2 + 0 = 2 (normal total, LOH)
- Homozygous deletion: 0 + 0 = 0
- High amplification: 10 + 0 = 10 (focal amp)
```

## Prerequisites

* Python 3.10+
* CNV calling tools (FACETS, CNVkit, etc.)
* Reference genome and annotations
* Sufficient memory for WGS (16GB+)

## Related Skills

* Variant_Interpretation - For CNV annotation
* HRD_Analysis_Agent - For HRD scoring from CNV
* Pan_Cancer_MultiOmics_Agent - For pan-cancer CNV context

## Quality Considerations

1. **Coverage depth**: Higher = better resolution
2. **Tumor purity**: Low purity challenges calling
3. **Normal match**: Best with matched normal
4. **Target design**: Uniform coverage for panels
5. **GC bias**: Proper normalization critical

## Author

AI Group - Biomedical AI Platform
