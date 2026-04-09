# mpn-progression-monitor-agent

> AI-powered myeloproliferative neoplasm monitoring for disease progression prediction, treatment response tracking, and transformation risk assessment in PV, ET, and myelofibrosis.

**Available tools:** Read, Bash

# MPN Progression Monitor Agent

The **MPN Progression Monitor Agent** provides comprehensive monitoring of myeloproliferative neoplasms (PV, ET, MF) for disease progression, treatment response, and transformation risk. It integrates molecular profiling, clinical parameters, and AI-based risk models to guide management of chronic phase disease and predict blast transformation.

## When to Use This Skill

* When monitoring JAK2/CALR/MPL mutation burden over time.
* For predicting fibrosis progression in PV/ET.
* To assess risk of blast transformation.
* When tracking treatment response to JAK inhibitors.
* For calculating dynamic risk scores (DIPSS, MIPSS70).

## Core Capabilities

1. **Mutation Monitoring**: Track driver and high-risk mutation VAF.

2. **Progression Prediction**: Model fibrosis and transformation risk.

3. **Risk Scoring**: Calculate DIPSS, MIPSS70+, MTSS dynamically.

4. **Treatment Response**: Assess molecular and clinical response.

5. **Clone Evolution**: Track clonal dynamics and new mutations.

6. **Transplant Timing**: Optimize allo-HSCT timing decisions.

## MPN Classification

| MPN Type | Driver Mutations | Progression Risk |
|----------|------------------|------------------|
| PV | JAK2 V617F (95%), JAK2 exon 12 | Fibrosis 10-15%, AML 2-5% |
| ET | JAK2 (55%), CALR (25%), MPL (5%) | Fibrosis 5-10%, AML 1-2% |
| Pre-PMF | Same as PMF | Variable |
| PMF | JAK2 (60%), CALR (25%), MPL (5%) | AML 10-20% |

## High-Risk Mutations

| Mutation | Impact | MF Association |
|----------|--------|----------------|
| ASXL1 | Adverse | Strong |
| SRSF2 | Adverse | Strong (PMF) |
| EZH2 | Adverse | Moderate |
| IDH1/2 | Adverse | Transformation |
| RUNX1 | Very Adverse | Transformation |
| TP53 | Very Adverse | Transformation |
| U2AF1 | Adverse | Moderate |

## Risk Scores

| Score | Components | Application |
|-------|------------|-------------|
| IPSS | Age, Hb, WBC, blasts, symptoms | PMF at diagnosis |
| DIPSS | Same, dynamic | PMF follow-up |
| DIPSS+ | + karyotype, transfusion, platelets | PMF refined |
| MIPSS70 | Molecular markers | Transplant-age PMF |
| MIPSS70+ v2.0 | + U2AF1, karyotype | Most comprehensive |
| MTSS | Transplant-specific | Allo-HSCT outcomes |

## Workflow

1. **Input**: Serial molecular testing, CBC, clinical parameters.

2. **Baseline Assessment**: Calculate initial risk score.

3. **Mutation Tracking**: Monitor VAF trends over time.

4. **Risk Recalculation**: Update scores at each timepoint.

5. **Progression Detection**: Identify molecular/clinical progression.

6. **Treatment Assessment**: Evaluate response to therapy.

7. **Output**: Dynamic risk assessment, progression alerts, recommendations.

## Example Usage

**User**: "Monitor this myelofibrosis patient's disease trajectory and update risk scores with new molecular data."

**Agent Action**:
```bash
python3 Skills/Hematology/MPN_Progression_Monitor_Agent/mpn_monitor.py \
    --patient_id MF_001 \
    --molecular_data serial_mutations.csv \
    --cbc_data serial_cbc.csv \
    --clinical_data symptoms.json \
    --mpn_type pmf \
    --baseline_date 2024-01-15 \
    --calculate_scores dipss,mipss70 \
    --output mpn_monitoring/
```

## Input Requirements

| Data Type | Parameters | Frequency |
|-----------|------------|-----------|
| Molecular | JAK2/CALR/MPL VAF, NGS panel | q3-6 months |
| CBC | Hb, WBC, platelets, blasts | Monthly |
| Clinical | Symptoms, spleen size | q3 months |
| Bone Marrow | Fibrosis grade, cytogenetics | q6-12 months |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Risk Scores | DIPSS, MIPSS70 over time | .csv |
| VAF Trends | Mutation burden plots | .png |
| Progression Alert | Warning if criteria met | .json |
| Response Assessment | IWG-MRT criteria | .json |
| Transplant Timing | Recommendation if indicated | .json |
| Clone Evolution | New mutations, clonal shifts | .csv |

## Progression Criteria

| Progression Type | Criteria | Action |
|------------------|----------|--------|
| Clinical | New symptoms, splenomegaly | Intensify therapy |
| Hematologic | Cytopenias, increased blasts | BMB, cytogenetics |
| Molecular | New high-risk mutations | Risk restaging |
| Fibrotic | Increased fibrosis grade | Consider transplant |
| Blast Phase | ≥20% blasts | Urgent intervention |

## Response Criteria (IWG-MRT)

| Response | Definition | Implications |
|----------|------------|--------------|
| Complete Remission | No disease manifestations | Excellent outcome |
| Partial Remission | >50% improvement | Good response |
| Clinical Improvement | Symptom/spleen improvement | Benefit |
| Stable Disease | No change | Observe |
| Progressive Disease | Progression criteria | Change therapy |

## AI/ML Components

**Progression Prediction**:
- Survival analysis with molecular features
- Random survival forests
- Deep learning time-to-event

**Clone Tracking**:
- VAF trajectory modeling
- New clone detection
- Evolutionary tree inference

**Transplant Decision**:
- Survival benefit modeling
- NRM prediction
- Optimal timing algorithms

## Treatment Response Monitoring

| Therapy | Response Markers | Timeline |
|---------|------------------|----------|
| Ruxolitinib | Spleen, symptoms, JAK2 VAF | 12-24 weeks |
| Fedratinib | Similar to ruxolitinib | 24 weeks |
| Momelotinib | + anemia improvement | 24 weeks |
| Interferon | Molecular response, JAK2 VAF | 12+ months |

## Prerequisites

* Python 3.10+
* lifelines, scikit-survival
* Variant annotation tools
* Risk score calculators
* Visualization libraries

## Related Skills

* CHIP_Clonal_Hematopoiesis_Agent - Pre-MPN states
* MDS_Classification_Agent - Overlap syndromes
* Bone_Marrow_AI_Agent - Morphology analysis
* Coagulation_Thrombosis_Agent - Thrombosis risk

## Thrombosis Risk in MPN

| Factor | Risk Increase | Management |
|--------|---------------|------------|
| Age >60 | 2-3x | Cytoreduction |
| Prior thrombosis | 3-5x | Anticoagulation |
| JAK2 V617F | 2x | Higher for homozygous |
| High WBC | 1.5-2x | Control counts |
| CV risk factors | Additive | Aggressive management |

## Special Considerations

1. **Triple-Negative MPN**: Different prognosis, consider other diagnoses
2. **Cytogenetic Evolution**: High-risk signal, BMB follow-up
3. **New Mutations**: May indicate disease evolution
4. **Treatment Resistance**: Consider second-line or transplant
5. **Quality of Life**: Balance treatment intensity

## Transplant Indications

| Indication | Criteria | Timing |
|------------|----------|--------|
| High-Risk PMF | MIPSS70+ high/very high | Consider early |
| Blast Phase | ≥20% blasts | Urgent if fit |
| Refractory Disease | Failed JAKi | Evaluate |
| Transfusion Dependence | RBC/platelet dependent | Factor in decision |

## Author

AI Group - Biomedical AI Platform
