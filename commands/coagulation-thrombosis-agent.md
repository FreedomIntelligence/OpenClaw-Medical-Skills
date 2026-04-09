# coagulation-thrombosis-agent

> AI-powered analysis of coagulation disorders, thrombosis risk prediction, anticoagulation management, and platelet function assessment using machine learning.

**Available tools:** Read, Bash

# Coagulation and Thrombosis Agent

The **Coagulation and Thrombosis Agent** provides AI-driven analysis of hemostatic disorders, thrombosis risk assessment, and anticoagulation management. It integrates coagulation cascade modeling, platelet function analysis, and machine learning for personalized thrombosis prevention.

## When to Use This Skill

* When assessing venous thromboembolism (VTE) risk in hospitalized patients.
* For anticoagulation dose optimization (warfarin, DOACs).
* To analyze coagulation panel results and identify bleeding/clotting disorders.
* For platelet morphology and function assessment.
* When managing thrombosis in myeloproliferative neoplasms (MPNs).

## Core Capabilities

1. **VTE Risk Prediction**: Machine learning models predict deep vein thrombosis (DVT) and pulmonary embolism (PE) risk using clinical and laboratory features.

2. **Anticoagulation Optimization**: AI-guided dosing for warfarin (incorporating pharmacogenomics) and monitoring for DOACs.

3. **Coagulation Cascade Analysis**: Interprets PT, aPTT, fibrinogen, D-dimer, and specialized assays to diagnose coagulopathies.

4. **Platelet Analysis**: CNN-based morphology analysis predicting bleeding and thrombosis risk from peripheral smear images.

5. **DIC Scoring**: Automated disseminated intravascular coagulation (DIC) scoring and monitoring.

6. **MPN Thrombosis Risk**: Specialized models for thrombosis prediction in polycythemia vera, essential thrombocythemia.

## Workflow

1. **Input**: Coagulation lab results, patient demographics, clinical risk factors, platelet images (optional).

2. **Risk Assessment**: Apply ML models for VTE, bleeding, or DIC risk scores.

3. **Dosing Optimization**: Generate anticoagulation recommendations.

4. **Monitoring**: Track INR/anti-Xa trends and alert on deviations.

5. **Diagnosis**: Pattern recognition for coagulation disorders.

6. **Output**: Risk scores, dosing recommendations, diagnostic suggestions, monitoring alerts.

## Example Usage

**User**: "Calculate VTE risk for this hospitalized patient and optimize LMWH prophylaxis."

**Agent Action**:
```bash
python3 Skills/Hematology/Coagulation_Thrombosis_Agent/thrombosis_analyzer.py \
    --patient_data patient_demographics.json \
    --labs coagulation_panel.csv \
    --risk_model improved_padua \
    --anticoagulant lmwh \
    --renal_function egfr_45 \
    --output vte_assessment.json
```

## Risk Models Implemented

| Model | Application | Key Features |
|-------|-------------|--------------|
| Padua (Enhanced) | Medical VTE risk | 11 clinical factors + ML enhancement |
| Caprini (AI) | Surgical VTE risk | 40+ factors with ML weighting |
| CHADS2-VASc | Atrial fibrillation stroke risk | Standard guideline scoring |
| HAS-BLED | Anticoagulation bleeding risk | Major bleeding prediction |
| IPSET-thrombosis | MPN thrombosis | JAK2, age, prior thrombosis |

## Coagulation Panel Interpretation

| Test | Normal Range | Elevations Suggest | Decreases Suggest |
|------|--------------|-------------------|-------------------|
| PT/INR | 11-13.5s / 0.9-1.1 | Warfarin, VII def, liver disease | - |
| aPTT | 25-35s | Heparin, VIII/IX/XI def, lupus AC | - |
| Fibrinogen | 200-400 mg/dL | Acute phase, inflammation | DIC, liver disease |
| D-dimer | <500 ng/mL | VTE, DIC, inflammation | - |
| Platelet | 150-400K | Reactive, MPN | ITP, marrow failure |

## AI/ML Components

**Deep Learning for Platelet Morphology**:
- CNN analysis of peripheral smear images
- Identifies giant platelets, platelet clumps, hypogranular forms
- Predicts bleeding/thrombosis risk from morphology

**VTE Prediction Models**:
- Gradient boosting (XGBoost) on structured EHR data
- Incorporates labs, vitals, medications, procedures
- AUC > 0.85 for hospital-acquired VTE

**Anticoagulation Dosing**:
- Reinforcement learning for INR control
- Pharmacogenomic integration (CYP2C9, VKORC1)
- Real-time dose adjustment recommendations

## Prerequisites

* Python 3.10+
* scikit-learn, XGBoost, PyTorch
* HL7 FHIR client (for EHR integration)
* Image analysis libraries (for platelet morphology)

## Related Skills

* Flow_Cytometry_AI - For platelet function assays
* Pharmacogenomics_Agent - For anticoagulant pharmacogenomics
* Blood_Smear_Analysis - For morphology assessment

## Clinical Applications

1. **Hospital VTE Prevention**: Real-time risk scoring in EMR
2. **Anticoagulation Clinic**: AI-assisted warfarin dosing
3. **DIC Management**: Automated scoring and transfusion guidance
4. **Inherited Disorders**: Pattern recognition for factor deficiencies

## Author

AI Group - Biomedical AI Platform
