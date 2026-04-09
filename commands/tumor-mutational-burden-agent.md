# tumor-mutational-burden-agent

> Calculates and harmonizes Tumor Mutational Burden (TMB) across platforms to predict immunotherapy response.

**Available tools:** Read, Bash

# Tumor Mutational Burden Agent

The **Tumor Mutational Burden Agent** provides comprehensive TMB analysis for immunotherapy response prediction. It harmonizes TMB calculation across different assays, integrates with other biomarkers (PD-L1, MSI), and provides evidence-based therapy recommendations.

## When to Use This Skill

* When calculating TMB from panel sequencing, WES, or WGS data.
* To harmonize TMB values across different assay platforms.
* For predicting immunotherapy response using TMB and integrated biomarkers.
* When determining TMB-High status for pembrolizumab eligibility.
* To analyze TMB in context of tumor type-specific distributions.

## Core Capabilities

1. **TMB Calculation**: Compute TMB from different sequencing platforms with appropriate normalization.

2. **Platform Harmonization**: Standardize TMB across FoundationOne, MSK-IMPACT, WES, and other assays.

3. **TMB-High Classification**: Apply FDA-approved and tumor-specific thresholds.

4. **Biomarker Integration**: Combine TMB with PD-L1, MSI, and gene signatures.

5. **Response Prediction**: ML models predicting ICI response from TMB-inclusive features.

6. **Tumor-Specific Context**: Interpret TMB relative to cancer type distributions.

## TMB Calculation Methods

| Platform | Coverage | TMB Formula | Normalization |
|----------|----------|-------------|---------------|
| WES | 30-50 Mb | Nonsynonymous/coding Mb | Per exome size |
| FoundationOne | 1.1 Mb | Syn + nonsyn/panel Mb | FDA validated |
| MSK-IMPACT | 1.0-1.2 Mb | Nonsyn + splice/panel Mb | Panel-specific |
| TSO500 | 1.94 Mb | Coding mutations/Mb | Illumina validated |
| WGS | 3 Gb | Various metrics | Genome-wide |

## TMB Thresholds

| Context | Threshold | Evidence |
|---------|-----------|----------|
| FDA (pan-tumor) | ≥10 mut/Mb | KEYNOTE-158 |
| Melanoma | ≥10 mut/Mb | Practice standard |
| NSCLC | ≥10 mut/Mb | Multiple trials |
| SCLC | ≥10 mut/Mb | Variable benefit |
| Colorectal (MSS) | Limited utility | MSI more predictive |
| Urothelial | ≥10 mut/Mb | IMvigor trials |

## Workflow

1. **Input**: VCF/MAF file with somatic mutations, assay details, tumor type.

2. **Filtering**: Remove germline, artifacts, known drivers (optional).

3. **Calculation**: Count mutations and normalize to coverage.

4. **Harmonization**: Convert to WES-equivalent TMB if needed.

5. **Classification**: Assign TMB-High/Low based on thresholds.

6. **Integration**: Combine with PD-L1, MSI for composite score.

7. **Output**: TMB value, classification, response prediction, recommendations.

## Example Usage

**User**: "Calculate TMB from this panel sequencing data and predict immunotherapy response."

**Agent Action**:
```bash
python3 Skills/Oncology/Tumor_Mutational_Burden_Agent/tmb_analyzer.py \
    --mutations tumor_somatic.maf \
    --panel foundation_one \
    --tumor_type nsclc \
    --pdl1_tps 50 \
    --msi_status stable \
    --harmonize_to wes \
    --output tmb_report.json
```

## Platform Harmonization

Different panels yield different TMB values for the same tumor:

```
TMB_WES = a * TMB_panel + b

Conversion factors (example):
- FoundationOne CDx: TMB_WES ≈ 1.0 × TMB_F1
- MSK-IMPACT: TMB_WES ≈ 1.1 × TMB_IMPACT
- TSO500: TMB_WES ≈ 0.9 × TMB_TSO
```

**Harmonization Considerations**:
- Panel size affects precision
- Gene content affects which mutations counted
- Algorithmic differences in filtering

## Integrated Biomarker Analysis

**TMB + PD-L1 + MSI Integration**:

| TMB | PD-L1 | MSI | ICI Benefit |
|-----|-------|-----|-------------|
| High | High | MSI-H | Very high |
| High | Low | MSS | Moderate-high |
| Low | High | MSS | Moderate |
| Low | Low | MSS | Limited |
| Any | Any | MSI-H | High (pembrolizumab) |

## Cancer Type TMB Distributions

| Cancer Type | Median TMB | TMB-High % |
|-------------|------------|------------|
| Melanoma | 13.5 | 45% |
| NSCLC | 7.2 | 25% |
| SCLC | 9.8 | 35% |
| Bladder | 6.5 | 20% |
| Colorectal | 4.0 | 5% (MSS) |
| Breast | 2.5 | 5% |
| Prostate | 2.0 | 3% |

## AI/ML Enhancement

**Response Prediction Model**:
- Features: TMB, PD-L1, MSI, gene expression signatures
- Additional: Clonal vs subclonal TMB, driver mutations
- Performance: AUC 0.70-0.80 across tumor types

**TMB Components Analysis**:
- Clonal TMB: Mutations in all cells
- Subclonal TMB: Mutations in subpopulations
- Clonal TMB more predictive of response

## Prerequisites

* Python 3.10+
* Variant annotation tools
* Panel BED files for coverage
* Reference mutation databases

## Related Skills

* Variant_Annotation - For mutation calling
* Liquid_Biopsy_Analytics_Agent - For blood-based TMB
* Immune_Checkpoint_Combination_Agent - For ICI selection

## Clinical Decision Support

1. **TMB-H Pembrolizumab**: FDA-approved pan-tumor indication
2. **TMB + PD-L1**: Combined scoring for NSCLC
3. **TMB Monitoring**: Track under immunotherapy
4. **TMB Heterogeneity**: Consider multiple samples

## Author

AI Group - Biomedical AI Platform
