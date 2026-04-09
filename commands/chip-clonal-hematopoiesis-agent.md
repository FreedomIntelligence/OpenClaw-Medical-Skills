# chip-clonal-hematopoiesis-agent

> AI-powered clonal hematopoiesis of indeterminate potential (CHIP) detection, risk stratification, and cardiovascular/malignancy risk prediction using genomic and clinical data.

**Available tools:** Read, Bash

# CHIP Clonal Hematopoiesis Agent

The **CHIP Clonal Hematopoiesis Agent** provides comprehensive detection and risk stratification of clonal hematopoiesis of indeterminate potential (CHIP). It identifies clonal mutations in blood cells, assesses risk of progression to myeloid malignancy, and predicts cardiovascular disease risk, integrating with the CHIC machine learning framework for CBC-based screening.

## When to Use This Skill

* When detecting CHIP mutations from blood sequencing data.
* For stratifying risk of progression to MDS/AML.
* To assess CHIP-associated cardiovascular disease risk.
* When filtering CHIP variants from tumor liquid biopsy.
* For population-level CHIP screening and research.

## Core Capabilities

1. **CHIP Detection**: Identify clonal mutations with VAF >2%.

2. **Risk Stratification**: Predict myeloid malignancy progression risk.

3. **CVD Risk Assessment**: Estimate cardiovascular disease risk.

4. **CCUS Classification**: Distinguish CHIP from CCUS/MDS.

5. **Clone Size Tracking**: Monitor clonal evolution over time.

6. **ctDNA Filtering**: Remove CHIP from tumor ctDNA analysis.

## CHIP-Associated Genes

| Gene | Frequency | Malignancy Risk | CVD Risk |
|------|-----------|-----------------|----------|
| DNMT3A | 50% | Moderate | Elevated |
| TET2 | 20% | Moderate | Elevated (inflammatory) |
| ASXL1 | 10% | High | Moderate |
| JAK2 | 5% | High (MPN) | Elevated (thrombosis) |
| TP53 | 5% | Very High | Low |
| SF3B1 | 3% | Moderate-High | Low |
| SRSF2 | 3% | High | Low |
| PPM1D | 2% | Moderate | Therapy-related |
| CBL | 2% | High | Moderate |
| IDH1/2 | 2% | Moderate-High | Low |

## Risk Categories

| Category | Criteria | Annual AML Risk |
|----------|----------|-----------------|
| Low-Risk CHIP | DNMT3A/TET2, VAF <10% | <0.5% |
| Intermediate CHIP | DNMT3A/TET2, VAF >10% | 0.5-1% |
| High-Risk CHIP | ASXL1, TP53, splicing | 1-3% |
| CCUS | CHIP + cytopenia | 3-10% |
| Pre-MDS | High-risk mutations + dysplasia | >10% |

## Workflow

1. **Input**: Blood sequencing (WES/panel), CBC data, clinical history.

2. **Variant Detection**: Call somatic variants with VAF filtering.

3. **CHIP Classification**: Identify CHIP-defining mutations.

4. **Risk Scoring**: Calculate malignancy and CVD risk scores.

5. **Longitudinal Analysis**: Track clone dynamics if serial samples.

6. **Clinical Integration**: Generate management recommendations.

7. **Output**: CHIP status, risk scores, monitoring plan.

## Example Usage

**User**: "Analyze this patient's blood sequencing for CHIP and calculate their risk of progression and cardiovascular events."

**Agent Action**:
```bash
python3 Skills/Hematology/CHIP_Clonal_Hematopoiesis_Agent/chip_analysis.py \
    --variants blood_variants.vcf \
    --cbc_data patient_cbc.csv \
    --clinical_data patient_demographics.json \
    --vaf_threshold 0.02 \
    --age 65 \
    --calculate_cvd_risk true \
    --output chip_analysis/
```

## CHRS Risk Score (Clonal Hematopoiesis Risk Score)

| Factor | Points | Notes |
|--------|--------|-------|
| High-risk mutation | +2 | SRSF2, SF3B1, ZRSR2, IDH1/2, FLT3, RUNX1, JAK2 |
| Single DNMT3A mutation | -1 | Lower risk |
| ≥2 mutations | +1 | Increased burden |
| VAF ≥20% | +1 | Large clone |
| CCUS (vs CHIP) | +2 | Cytopenia present |
| RDW ≥15% | +1 | Blood count abnormality |
| MCV ≥100 fL | +1 | Macrocytosis |
| Age ≥65 | +1 | Age-related risk |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| CHIP Status | Present/Absent, genes involved | .json |
| Mutation Details | VAF, gene, protein change | .csv |
| Malignancy Risk | 5-year AML/MDS probability | .json |
| CVD Risk | Cardiovascular risk score | .json |
| CHRS Score | Clonal hematopoiesis risk score | .json |
| Recommendations | Clinical management | .md |
| Monitoring Plan | Follow-up schedule | .json |

## AI/ML Components

**CHIC Framework**:
- Machine learning from CBC indices
- Identifies high-risk CHIP without sequencing
- Reduces "number needed to sequence"

**Risk Prediction**:
- Cox proportional hazards for progression
- Random survival forests
- Deep learning survival models

**CVD Risk Integration**:
- Framingham score adjustment
- CHIP-specific hazard ratios
- Inflammatory biomarker integration

## Cardiovascular Risk

| CHIP Gene | CVD Hazard Ratio | Mechanism |
|-----------|------------------|-----------|
| TET2 | 1.9 | IL-6, inflammasome |
| DNMT3A | 1.7 | Inflammation |
| JAK2 | 2.6 | Thrombosis, platelet activation |
| ASXL1 | 2.0 | Inflammation |
| Overall CHIP | 1.5-2.0 | Multiple pathways |

## Clinical Management Guidelines

| CHIP Category | Monitoring | Intervention |
|---------------|------------|--------------|
| Low-risk | Annual CBC | None |
| Intermediate | CBC q6 months | CVD optimization |
| High-risk | CBC q3-6 months, consider BMB | Hematology referral |
| CCUS | BMB, q3 month CBC | Active surveillance |

## Prerequisites

* Python 3.10+
* Variant callers (Mutect2, VarScan)
* ANNOVAR/VEP for annotation
* lifelines, scikit-survival
* CHIC model weights

## Related Skills

* MPN_Progression_Monitor_Agent - MPN monitoring
* CHIC_ML_Framework_Agent - CBC-based screening
* MDS_Classification_Agent - MDS diagnosis
* Bone_Marrow_AI_Agent - Morphology analysis

## CHIP vs ctDNA Filtering

| Feature | CHIP | Tumor ctDNA |
|---------|------|-------------|
| VAF Stability | Stable over time | Changes with disease |
| Genes | DNMT3A, TET2, ASXL1 | Tumor drivers |
| Age Association | Increases with age | Independent |
| Multiple Samples | Consistent | Variable |

## Special Considerations

1. **VAF Threshold**: Use 2% for CHIP definition
2. **Germline Filtering**: Exclude germline variants
3. **Age Context**: Prevalence increases with age
4. **Therapy History**: Consider treatment-related clones
5. **Serial Monitoring**: Track clone dynamics

## Population Prevalence

| Age Group | CHIP Prevalence | High-Risk CHIP |
|-----------|-----------------|----------------|
| 40-49 | ~2% | <0.5% |
| 50-59 | ~5% | ~1% |
| 60-69 | ~10% | ~2% |
| 70-79 | ~15% | ~4% |
| 80+ | ~20% | ~5% |

## Therapeutic Implications

| Scenario | CHIP Impact | Consideration |
|----------|-------------|---------------|
| CAR-T Therapy | May affect outcomes | Monitor clones |
| Stem Cell Transplant | Donor CHIP matters | Screen donors |
| Chemotherapy | May expand clones | Monitor post-treatment |
| Cardiovascular | Increased risk | Aggressive prevention |

## Author

AI Group - Biomedical AI Platform
