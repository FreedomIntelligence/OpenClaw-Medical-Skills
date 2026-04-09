# organoid-drug-response-agent

> AI-powered analysis of patient-derived organoid (PDO) drug screening for personalized oncology treatment selection and biomarker discovery.

**Available tools:** Read, Bash

# Organoid Drug Response Agent

The **Organoid Drug Response Agent** provides AI-driven analysis of patient-derived organoid (PDO) drug screening data for personalized treatment selection. It correlates organoid drug responses with patient outcomes and molecular profiles to guide precision oncology decisions.

## When to Use This Skill

* When interpreting organoid drug screening results for treatment selection.
* To correlate PDO drug sensitivity with molecular features.
* For identifying combination therapies using organoid co-culture systems.
* When predicting patient response from organoid-derived data.
* To discover biomarkers from large-scale organoid screens.

## Core Capabilities

1. **Drug Response Analysis**: Process organoid viability data to calculate IC50, AUC, and response metrics.

2. **Patient-Organoid Concordance**: Assess molecular fidelity between PDO and donor tumor.

3. **Biomarker Discovery**: Identify molecular features predicting drug sensitivity.

4. **Combination Screening**: Analyze drug synergy from combination matrices.

5. **Clinical Translation**: Project organoid findings to patient treatment recommendations.

6. **Microenvironment Modeling**: Analyze immune co-culture and CAF interactions.

## Organoid Advantages

| Feature | Organoids | Cell Lines | PDX |
|---------|-----------|------------|-----|
| Patient fidelity | High | Low | High |
| Establishment rate | 60-90% | Variable | 30-50% |
| Turnaround | 4-8 weeks | Fast | 3-6 months |
| Throughput | Medium-high | Very high | Low |
| Microenvironment | Partial | None | Mouse |
| Cost | Medium | Low | High |

## Workflow

1. **Input**: Organoid drug screening data, organoid molecular profiles, patient tumor data.

2. **QC**: Assess organoid viability and growth metrics.

3. **Response Calculation**: Compute drug sensitivity metrics.

4. **Concordance**: Compare organoid to donor tumor molecular profiles.

5. **Biomarker Analysis**: Correlate sensitivity with molecular features.

6. **Translation**: Generate patient treatment recommendations.

7. **Output**: Drug rankings, biomarkers, recommended treatments.

## Example Usage

**User**: "Analyze organoid drug screening results for this colorectal cancer patient and recommend treatments."

**Agent Action**:
```bash
python3 Skills/Oncology/Organoid_Drug_Response_Agent/organoid_analyzer.py \
    --screening_data drug_screen_384well.csv \
    --organoid_rnaseq organoid_expression.tsv \
    --organoid_mutations organoid_variants.maf \
    --patient_tumor patient_expression.tsv \
    --tumor_type colorectal \
    --combination_matrix combo_screen.csv \
    --output organoid_report/
```

## Drug Response Metrics

| Metric | Calculation | Interpretation |
|--------|-------------|----------------|
| IC50 | 50% inhibition concentration | Potency |
| AUC | Area under dose-response | Overall sensitivity |
| GR50 | Growth rate-adjusted IC50 | Normalized potency |
| DSS | Drug sensitivity score | Selective activity |
| Emax | Maximum effect | Efficacy plateau |

## Organoid-Patient Concordance Studies

| Study | Tumor Type | Accuracy | Reference |
|-------|------------|----------|-----------|
| Vlachogiannis 2018 | GI cancers | 88% | Science |
| Ooft 2019 | Colorectal | 80% | Science Transl Med |
| Tiriac 2018 | Pancreatic | 83% | Cancer Discovery |
| Ganesh 2019 | Rectal | 84% | Nature Medicine |

## Combination Synergy Analysis

**Methods**:
- Bliss independence
- Loewe additivity
- ZIP (Zero Interaction Potency)
- HSA (Highest Single Agent)

**Output**:
- Synergy scores
- Combination indices
- Dose-effect surfaces
- Optimal ratio identification

## AI/ML Models

**Response Prediction**:
- Multi-omic features (expression, mutation, CNV)
- Drug structural features
- Graph neural networks for drug-response

**Biomarker Discovery**:
- LASSO regression for feature selection
- Random forest for interaction detection
- SHAP values for interpretability

**Translation Modeling**:
- Transfer learning (organoid → patient)
- Concordance-weighted predictions
- Uncertainty quantification

## Organoid Co-Culture Systems

**Immune Co-Culture**:
- T-cell killing assays
- Checkpoint inhibitor testing
- CAR-T efficacy evaluation

**Stromal Co-Culture**:
- CAF interactions
- Drug resistance mechanisms
- ECM-mediated effects

## Prerequisites

* Python 3.10+
* Drug response analysis packages
* Machine learning frameworks
* Organoid molecular databases

## Related Skills

* PDX_Model_Analysis_Agent - For complementary models
* Drug_Repurposing - For additional drug candidates
* Multi_Omics_Integration - For molecular characterization

## Quality Control Metrics

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Z' factor | >0.5 | Assay quality |
| CV | <20% | Reproducibility |
| Passage number | <10 | Genetic stability |
| Growth rate | >1.5x/week | Viability |

## Clinical Implementation

1. **Turnaround Time**: 4-8 weeks from biopsy
2. **Panel Size**: 50-100+ drugs typically tested
3. **Decision Support**: Ranked drug recommendations
4. **Monitoring**: Re-screen on progression

## Author

AI Group - Biomedical AI Platform
