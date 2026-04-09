# hemoglobinopathy-analysis-agent

> AI-powered analysis of hemoglobin disorders including sickle cell disease, thalassemias, and variant hemoglobins using HPLC, electrophoresis, and molecular data.

**Available tools:** Read, Bash

# Hemoglobinopathy Analysis Agent

The **Hemoglobinopathy Analysis Agent** provides comprehensive AI-driven analysis of hemoglobin disorders. It integrates HPLC chromatograms, electrophoresis patterns, CBC parameters, and molecular genetics for diagnosis and management of sickle cell disease, thalassemias, and variant hemoglobins.

## When to Use This Skill

* When interpreting HPLC hemoglobin chromatograms for variant identification.
* To diagnose and classify thalassemia syndromes (α, β, δβ).
* For comprehensive sickle cell disease phenotype assessment.
* When correlating genotype with clinical phenotype severity.
* To guide hydroxyurea dosing and transfusion management.

## Core Capabilities

1. **HPLC Interpretation**: AI pattern recognition for hemoglobin variant identification from HPLC chromatograms.

2. **Thalassemia Classification**: Distinguish α-thalassemia (silent carrier to Hb Bart's) and β-thalassemia (minor to major).

3. **Sickle Cell Phenotyping**: Integrate HbS%, HbF%, α-globin status for phenotype prediction.

4. **Variant Identification**: Database matching for >1,500 known hemoglobin variants.

5. **Molecular Correlation**: Link genetic variants (HBB, HBA1/2) to protein phenotypes.

6. **Management Guidance**: Treatment recommendations based on disease severity.

## Hemoglobin Pattern Analysis

| Condition | HbA | HbA2 | HbF | Variants | RBC Indices |
|-----------|-----|------|-----|----------|-------------|
| Normal adult | 96-98% | 2-3% | <1% | - | Normal |
| β-thal trait | 92-95% | 3.5-7% | 1-3% | - | Microcytic |
| β-thal major | 0-10% | Variable | 90-95% | - | Severe anemia |
| α-thal trait | 97-98% | 2-3% | <1% | - | Microcytic |
| HbH disease | 70-90% | 1-2% | <1% | HbH 5-30% | Moderate anemia |
| Sickle trait | 55-60% | 2-3% | <1% | HbS 38-45% | Normal |
| Sickle cell | 0% | 2-3% | 2-20% | HbS 80-95% | Sickle cells |

## Workflow

1. **Input**: HPLC chromatogram, CBC with indices, peripheral smear findings, molecular data (if available).

2. **Pattern Recognition**: AI analysis of HPLC retention times and peak areas.

3. **Variant Matching**: Compare against hemoglobin variant database.

4. **RBC Correlation**: Integrate MCV, MCH, RDW, reticulocyte count.

5. **Phenotype Classification**: Assign clinical phenotype category.

6. **Management**: Generate treatment and monitoring recommendations.

7. **Output**: Diagnosis, variant identification, clinical classification, management plan.

## Example Usage

**User**: "Interpret this HPLC chromatogram showing an abnormal peak and correlate with the CBC findings."

**Agent Action**:
```bash
python3 Skills/Hematology/Hemoglobinopathy_Analysis_Agent/hb_analyzer.py \
    --hplc_data chromatogram.csv \
    --retention_times peak_times.json \
    --cbc cbc_results.json \
    --peripheral_smear smear_findings.txt \
    --molecular hbb_sequencing.vcf \
    --output hb_report.json
```

## Key Hemoglobin Variants

| Variant | Mutation | HPLC Window | Clinical Significance |
|---------|----------|-------------|----------------------|
| HbS | β6 Glu→Val | S window | Sickling disorders |
| HbC | β6 Glu→Lys | C window | HbC disease, HbSC |
| HbE | β26 Glu→Lys | A2/E window | Common in SE Asia |
| HbD-Punjab | β121 Glu→Gln | D window | HbSD-Punjab |
| Hb Lepore | δβ fusion | S window | Thalassemia |
| HbH | β4 tetramer | Fast band | α-thalassemia |
| Hb Bart's | γ4 tetramer | Very fast | Hydrops fetalis |

## AI/ML Components

**HPLC Pattern Recognition**:
- CNN trained on 50,000+ chromatograms
- Identifies peaks by retention time and shape
- Quantifies hemoglobin fractions
- Flags unusual patterns for review

**Phenotype Prediction**:
- Gradient boosting model
- Features: Hb%, HbF%, α-globin genotype, F-cell distribution
- Predicts clinical severity (mild/moderate/severe)
- VOC risk, stroke risk, TCD velocity correlation

**Genotype-Phenotype Correlation**:
- Database of published correlations
- Modifier genes (BCL11A, HBS1L-MYB, α-globin)
- Pharmacogenomics (HU response prediction)

## Clinical Decision Support

**Hydroxyurea Candidacy**:
- Severe phenotype
- ≥3 pain crises/year
- ACS history
- Stroke prevention

**Transfusion Protocols**:
- Simple vs exchange transfusion
- Target HbS% thresholds
- Iron chelation monitoring

**Monitoring Schedule**:
- LDH, reticulocytes, bilirubin
- Ferritin for transfused patients
- TCD for children with SCD

## Prerequisites

* Python 3.10+
* PyTorch for image/signal analysis
* Hemoglobin variant databases
* Clinical lab interface

## Related Skills

* Blood_Smear_Analysis - For morphology assessment
* Variant_Interpretation - For molecular findings
* Flow_Cytometry_AI - For F-cell quantification

## Newborn Screening Integration

- Interpret newborn screening HPLC patterns
- Distinguish FAS (sickle trait) from FS (sickle disease)
- Flag FAE (HbE), FAC (HbC), F-only (β-thal major)
- Generate confirmatory testing recommendations

## Author

AI Group - Biomedical AI Platform
