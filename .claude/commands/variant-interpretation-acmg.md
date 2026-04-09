# variant-interpretation-acmg

> Classifies genetic variants according to ACMG (American College of Medical Genetics) guidelines.

**Available tools:** Read, Bash

# Variant Interpretation (ACMG)

The **Variant Interpretation Skill** automates the classification of genetic variants (Pathogenic, Benign, VUS) using a rules-based engine derived from ACMG guidelines.

## When to Use This Skill

*   When analyzing a VCF file for clinical reporting.
*   To determine the clinical significance of a specific mutation (e.g., BRCA1 c.123A>G).
*   To aggregate evidence (population freq, computational predictions) into a final verdict.

## Core Capabilities

1.  **Rule Scoring**: Applies codes like PVS1 (Null variant), PM2 (Rare), PP3 (In silico).
2.  **Classification**: Combines scores to reach a verdict (Pathogenic, Likely Pathogenic, VUS, etc.).
3.  **Explanation**: Provides the logic/evidence used for the classification.

## Workflow

1.  **Input**: Variant details (Gene, HGVS, Consequence) or Evidence codes directly.
2.  **Process**: Sums weights of applied ACMG criteria.
3.  **Output**: Final classification and score breakdown.

## Example Usage

**User**: "Classify a variant with evidence PVS1 and PM2."

**Agent Action**:
```bash
python3 Skills/Genomics/Variant_Interpretation/acmg_classifier.py \
    --evidence "PVS1,PM2"
```
