# cancer-metabolism-agent

> AI-powered analysis of cancer metabolic reprogramming including Warburg effect, glutamine addiction, lipid metabolism, and metabolic vulnerabilities for therapeutic targeting.

**Available tools:** Read, Bash

# Cancer Metabolism Agent

The **Cancer Metabolism Agent** analyzes tumor metabolic reprogramming to identify vulnerabilities for therapeutic targeting. It integrates metabolomics, transcriptomics, and flux analysis to characterize Warburg effect, glutamine addiction, lipid synthesis, and other cancer-specific metabolic alterations.

## When to Use This Skill

* When analyzing tumor metabolomic profiles to identify metabolic phenotypes.
* To identify metabolic vulnerabilities as therapeutic targets.
* For predicting response to metabolism-targeting drugs (metformin, 2-DG, CB-839).
* When integrating metabolomics with transcriptomics for pathway analysis.
* To analyze tumor-microenvironment metabolic competition.

## Core Capabilities

1. **Metabolic Phenotyping**: Classify tumors by dominant metabolic programs (glycolytic, oxidative, lipogenic).

2. **Warburg Effect Quantification**: Measure aerobic glycolysis and lactate production signatures.

3. **Glutamine Dependency Analysis**: Identify glutamine-addicted tumors vulnerable to GLS inhibitors.

4. **Lipid Metabolism Profiling**: Analyze de novo lipogenesis and fatty acid oxidation.

5. **Metabolic Flux Analysis**: Integrate 13C tracer data for pathway flux quantification.

6. **Drug Sensitivity Prediction**: Predict response to metabolism-targeting therapeutics.

## Key Metabolic Pathways in Cancer

| Pathway | Key Enzymes | Cancer Relevance | Therapeutic Targets |
|---------|-------------|------------------|---------------------|
| Glycolysis | HK2, PKM2, LDHA | Warburg effect | 2-DG, lonidamine |
| Glutaminolysis | GLS1, GDH | Nitrogen/carbon source | CB-839, BPTES |
| Fatty acid synthesis | FASN, ACC, ACLY | Membrane biogenesis | TVB-2640, ND-646 |
| Oxidative phosphorylation | Complex I-V | OXPHOS tumors | Metformin, IACS-010759 |
| One-carbon metabolism | SHMT, MTHFD | Nucleotide synthesis | Methotrexate |
| Serine synthesis | PHGDH, PSAT1 | Amino acid auxotrophy | NCT-503 |

## Workflow

1. **Input**: Metabolomics data (LC-MS, GC-MS), RNA-seq expression, clinical annotations.

2. **Normalization**: Process metabolomics data with appropriate normalization.

3. **Pathway Scoring**: Calculate metabolic pathway activity scores.

4. **Phenotype Classification**: Assign metabolic phenotype clusters.

5. **Vulnerability Identification**: Identify metabolic dependencies.

6. **Drug Matching**: Predict sensitivity to metabolism-targeting agents.

7. **Output**: Metabolic phenotype, pathway activities, therapeutic recommendations.

## Example Usage

**User**: "Analyze this tumor's metabolic profile and identify targetable metabolic vulnerabilities."

**Agent Action**:
```bash
python3 Skills/Oncology/Cancer_Metabolism_Agent/metabolism_analyzer.py \
    --metabolomics tumor_lcms.csv \
    --rnaseq tumor_expression.tsv \
    --tumor_type NSCLC \
    --normalize mtic \
    --pathway_analysis true \
    --drug_prediction true \
    --output metabolism_report/
```

## Metabolic Phenotype Classification

**Glycolytic (Warburg)**:
- High HK2, PKM2, LDHA expression
- Elevated lactate/pyruvate ratio
- Low mitochondrial gene expression
- Sensitive to glycolysis inhibitors

**Oxidative (OXPHOS-dependent)**:
- High ETC complex expression
- Active TCA cycle
- PGC1α driven
- Sensitive to metformin, IACS-010759

**Lipogenic**:
- High FASN, ACC, SREBP1/2
- Active de novo lipogenesis
- Common in prostate, breast cancer
- Sensitive to FASN inhibitors

**Glutamine-addicted**:
- High GLS1, MYC-driven
- Glutamine-dependent anaplerosis
- Common in KRAS-mutant cancers
- Sensitive to CB-839

## AI/ML Models

**Metabolic Phenotype Classifier**:
- Random forest on metabolite ratios
- 85% accuracy on validation cohorts
- Integrates with molecular subtypes

**Flux Balance Analysis**:
- Genome-scale metabolic models (Recon3D)
- Constraint-based optimization
- Predicts essential metabolic genes

**Drug Response Prediction**:
- GDSC/CCLE metabolic drug data
- Multi-omic feature integration
- AUC 0.75-0.85 for metabolic drugs

## Metabolomics Data Processing

| Step | Method | Purpose |
|------|--------|---------|
| Peak detection | XCMS, MZmine | Identify metabolites |
| Annotation | HMDB, KEGG | Assign identities |
| Normalization | MTIC, median | Remove batch effects |
| Imputation | KNN, RF | Handle missing values |
| Enrichment | MSEA, Mummichog | Pathway analysis |

## TME Metabolic Competition

The agent analyzes tumor-immune metabolic crosstalk:
- Glucose competition (T-cell activation)
- Lactate immunosuppression
- Arginine depletion by MDSCs
- Tryptophan-IDO axis
- Adenosine immunosuppression

## Prerequisites

* Python 3.10+
* COBRApy for flux balance
* MetaboAnalyst interface
* Pathway databases (KEGG, Reactome)

## Related Skills

* Metabolomics_Agent - For general metabolomics
* Multi_Omics_Integration - For omic integration
* Drug_Repurposing - For therapeutic matching

## Clinical Applications

1. **Treatment Selection**: Match metabolic phenotype to drugs
2. **Combination Therapy**: Identify synergistic metabolic targets
3. **Resistance Mechanisms**: Metabolic adaptation under therapy
4. **Diet Interventions**: Ketogenic diet in glycolytic tumors

## Author

AI Group - Biomedical AI Platform
