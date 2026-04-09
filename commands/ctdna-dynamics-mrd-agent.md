# ctdna-dynamics-mrd-agent

> AI-powered circulating tumor DNA dynamics analysis for molecular residual disease detection, treatment response monitoring, and early relapse prediction using liquid biopsy.

**Available tools:** Read, Bash

# ctDNA Dynamics MRD Agent

The **ctDNA Dynamics MRD Agent** provides comprehensive analysis of circulating tumor DNA dynamics for molecular residual disease (MRD) detection, treatment response monitoring, and early relapse prediction. It integrates tumor-informed and tumor-naive approaches with temporal modeling for longitudinal ctDNA analysis.

## When to Use This Skill

* When monitoring minimal/molecular residual disease post-treatment.
* For tracking treatment response through ctDNA kinetics.
* To predict relapse before clinical/radiological detection.
* When assessing tumor burden dynamics during therapy.
* For early detection of acquired resistance mutations.

## Core Capabilities

1. **MRD Detection**: Ultra-sensitive detection of residual disease (LOD 0.001% VAF).

2. **Kinetic Modeling**: Model ctDNA clearance and doubling time.

3. **Response Prediction**: Predict treatment response from early ctDNA dynamics.

4. **Relapse Prediction**: Identify molecular relapse months before imaging.

5. **Resistance Monitoring**: Track emergence of resistance mutations.

6. **Multi-Timepoint Integration**: Analyze longitudinal ctDNA trajectories.

## Detection Approaches

| Approach | Method | LOD | Best Use Case |
|----------|--------|-----|---------------|
| Tumor-Informed | Track known mutations | 0.001% | Post-surgical MRD |
| Tumor-Naive | Panel-based detection | 0.1% | Screening, unknown primary |
| WGS-Based | Fragmentomics + mutations | 0.01% | Comprehensive profiling |
| Methylation | cfDNA methylation | 0.1% | Tissue of origin, early detection |

## Kinetic Parameters

| Parameter | Definition | Clinical Meaning |
|-----------|------------|------------------|
| ctDNA Half-Life | Time to 50% reduction | Treatment sensitivity |
| Doubling Time | Time to 2x increase | Tumor growth rate |
| Nadir | Lowest ctDNA level | Depth of response |
| Time to Nadir | Days to reach nadir | Response kinetics |
| Clearance Rate | Exponential decay constant | Treatment efficacy |
| Lead Time | MRD+ to clinical relapse | Early detection window |

## Workflow

1. **Input**: Serial ctDNA measurements (VAF or copies/mL), timepoints, treatment dates.

2. **QC**: Assess sequencing quality, coverage, tumor fraction.

3. **Mutation Tracking**: Quantify tracked variants across timepoints.

4. **Kinetic Modeling**: Fit exponential/sigmoidal models to dynamics.

5. **MRD Calling**: Determine MRD status with confidence intervals.

6. **Resistance Detection**: Identify emerging resistant clones.

7. **Output**: MRD status, kinetic parameters, predictions, visualizations.

## Example Usage

**User**: "Analyze this patient's serial ctDNA data to assess MRD status and predict relapse risk."

**Agent Action**:
```bash
python3 Skills/Oncology/ctDNA_Dynamics_MRD_Agent/ctdna_mrd_analysis.py \
    --ctdna_data serial_ctdna.tsv \
    --tracked_mutations tumor_mutations.vcf \
    --sample_times 0,14,42,90,180 \
    --treatment_start 0 \
    --surgery_date 7 \
    --cancer_type colorectal \
    --output mrd_analysis/
```

## Input Data Format

```tsv
Sample_ID  Timepoint_Days  Mutation  VAF  Copies_per_mL  Coverage
PT001_T0   0               TP53_R248Q  5.2  1500          15000
PT001_T1   14              TP53_R248Q  2.1  620           18000
PT001_T2   42              TP53_R248Q  0.05 15            20000
PT001_T3   90              TP53_R248Q  0.002 0.6          22000
```

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| MRD Status | Positive/Negative at each timepoint | .csv |
| Kinetic Parameters | Half-life, doubling time, nadir | .json |
| Response Classification | Major/Minor/No response | .csv |
| Relapse Risk | Probability and predicted time | .json |
| Dynamics Plot | ctDNA trajectory visualization | .png, .pdf |
| Resistance Variants | Emerging mutations | .vcf |
| Clonal Evolution | Clone frequency over time | .csv |

## Response Definitions

| Response Category | ctDNA Change | Clinical Correlation |
|-------------------|--------------|---------------------|
| Major Molecular Response | >2 log reduction | Excellent prognosis |
| Molecular Response | 1-2 log reduction | Good prognosis |
| Stable Molecular Disease | <1 log change | Intermediate |
| Molecular Progression | >0.5 log increase | Poor prognosis |

## Cancer-Specific Parameters

| Cancer Type | Typical Half-Life | MRD Lead Time | ctDNA Shedding |
|-------------|-------------------|---------------|----------------|
| Colorectal | 1-2 days | 6-12 months | High |
| Lung (NSCLC) | 1-3 days | 3-6 months | High |
| Breast | 2-5 days | 6-18 months | Moderate |
| Pancreatic | 1-2 days | 3-6 months | High |
| Melanoma | 2-4 days | 3-9 months | Variable |

## AI/ML Components

**Kinetic Modeling**:
- Non-linear mixed effects models
- Bayesian hierarchical models
- Gaussian process regression

**MRD Detection**:
- Error-suppressed variant calling
- Machine learning noise filtering
- Duplex UMI deduplication

**Relapse Prediction**:
- Time-series forecasting (LSTM, Transformers)
- Survival analysis (Cox, Random Survival Forests)
- Multi-mutation integration

## Clinical Trial Support

| Application | Endpoint | ctDNA Metric |
|-------------|----------|--------------|
| Neoadjuvant | pathCR surrogate | Pre-surgery clearance |
| Adjuvant | DFS surrogate | Post-surgery MRD |
| Metastatic | PFS/OS surrogate | ctDNA dynamics |
| Maintenance | Duration decision | MRD negativity |

## Prerequisites

* Python 3.10+
* Variant callers (Mutect2, Strelka)
* UMI-aware pipelines
* scipy, lifelines, survival analysis tools
* PyTorch for deep learning models

## Related Skills

* MRD_EDGE_Detection_Agent - Ultra-sensitive MRD detection
* Liquid_Biopsy_Analytics_Agent - Comprehensive liquid biopsy
* Tumor_Heterogeneity_Agent - Clonal evolution tracking
* HRD_Analysis_Agent - Genomic biomarkers

## Special Considerations

1. **Tumor Fraction**: Low tumor fraction limits sensitivity
2. **Pre-Analytical**: Plasma processing affects cfDNA quality
3. **Clonal Hematopoiesis**: CHIP variants can confound results
4. **Panel Design**: Ensure sufficient mutation coverage
5. **Timing**: Sample timing relative to treatment critical

## FDA-Cleared ctDNA Tests

| Test | Cancer Types | Application |
|------|--------------|-------------|
| Guardant360 CDx | Pan-cancer | Treatment selection |
| FoundationOne Liquid CDx | Pan-cancer | Treatment selection |
| Signatera | Solid tumors | MRD monitoring |
| Guardant Reveal | CRC | MRD detection |

## Author

AI Group - Biomedical AI Platform
