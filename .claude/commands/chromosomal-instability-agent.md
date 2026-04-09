# chromosomal-instability-agent

> AI-powered analysis of chromosomal instability (CIN) signatures for cancer prognosis, immunotherapy response prediction, and therapeutic vulnerability identification.

**Available tools:** Read, Bash

# Chromosomal Instability Agent

The **Chromosomal Instability Agent** analyzes CIN signatures to predict cancer prognosis, immunotherapy response, and therapeutic vulnerabilities. It integrates copy number alterations, aneuploidy scores, and CIN-related gene expression for comprehensive genomic instability assessment.

## When to Use This Skill

* When assessing tumor aneuploidy and chromosomal instability levels.
* To predict prognosis based on CIN signatures.
* For identifying tumors vulnerable to CIN-targeted therapies (PARP, ATR, WEE1).
* When analyzing immune evasion mechanisms related to CIN.
* To stratify patients for immunotherapy based on CIN status.

## Core Capabilities

1. **CIN Scoring**: Calculate comprehensive CIN scores from copy number data.

2. **Aneuploidy Quantification**: Measure arm-level and focal copy number alterations.

3. **CIN Gene Expression**: Analyze CIN70 and other transcriptional signatures.

4. **Immune Correlation**: Assess CIN-immune microenvironment relationships.

5. **Therapeutic Vulnerability**: Identify CIN-targeted treatment options.

6. **Prognostic Modeling**: Predict outcomes based on CIN signatures.

## CIN Metrics

| Metric | Calculation | Interpretation |
|--------|-------------|----------------|
| Aneuploidy score | Arm-level alterations | Chromosome-level CIN |
| SCNA burden | Total CNV alterations | Overall instability |
| Weighted GII | Fraction altered genome | Focal vs broad changes |
| CIN70 | 70-gene signature | Transcriptional CIN |
| WGII | Weighted genome instability | Comprehensive score |

## CIN70 Signature Genes

Core genes reflecting CIN phenotype:
- Mitotic checkpoint: BUB1, BUBR1, MAD2L1
- Kinetochore: CENPA, CENPF, NDC80
- DNA replication: MCM2-7, ORC1
- Cell cycle: CCNB1, CCNB2, CDK1, PLK1
- Chromosome segregation: AURKB, KIF2C, KIF11

## Workflow

1. **Input**: Copy number data (segments), gene expression, mutation data.

2. **CNV Analysis**: Calculate arm-level and focal alterations.

3. **Signature Scoring**: Compute CIN70 and other transcriptional signatures.

4. **Integration**: Combine DNA and RNA-based CIN metrics.

5. **Immune Analysis**: Correlate CIN with TME composition.

6. **Vulnerability Assessment**: Identify targetable dependencies.

7. **Output**: CIN scores, prognosis, treatment recommendations.

## Example Usage

**User**: "Analyze chromosomal instability in this breast cancer sample and identify treatment vulnerabilities."

**Agent Action**:
```bash
python3 Skills/Oncology/Chromosomal_Instability_Agent/cin_analyzer.py \
    --cnv_segments tumor_cnv.tsv \
    --expression rnaseq_tpm.tsv \
    --mutations somatic.maf \
    --tumor_type breast_cancer \
    --signatures cin70,cin25 \
    --output cin_report/
```

## CIN and Immune Evasion

**High CIN Associates With**:
- Reduced immune infiltration
- Lower checkpoint inhibitor response
- Increased immune evasion
- cGAS-STING activation (paradoxical)

**Mechanisms**:
1. Loss of tumor suppressors on chromosome arms
2. Chronic inflammatory signaling
3. Aneuploidy-induced stress responses
4. Subclonal diversification

## Therapeutic Vulnerabilities

| Target | Agents | CIN Context |
|--------|--------|-------------|
| PARP | Olaparib, etc. | High CIN + HRD |
| ATR | Berzosertib | Replication stress |
| WEE1 | Adavosertib | G2/M dependency |
| CHK1 | Prexasertib | Cell cycle checkpoint |
| KIF11 | Ispinesib | Mitotic dependency |
| Aurora kinases | Alisertib | Mitotic errors |

## CIN-Based Patient Stratification

| CIN Level | Prognosis | ICI Response | Alternative Therapy |
|-----------|-----------|--------------|---------------------|
| Low | Better | Better | Standard care |
| Intermediate | Variable | Variable | Combination therapy |
| High | Poor | Poor | CIN-targeted agents |
| Extreme | Very poor | Immune desert | Chemotherapy |

## AI/ML Components

**CIN Score Prediction**:
- Random forest on CNV features
- Expression-based CIN inference
- Multi-modal integration

**Prognosis Modeling**:
- Cox regression with CIN features
- Cancer-type specific models
- Integration with clinical variables

**Therapeutic Matching**:
- GDSC/CCLE drug sensitivity
- CIN-drug response correlations
- Combination predictions

## Pan-Cancer CIN Patterns

| Cancer Type | Typical CIN Level | Driver Events |
|-------------|-------------------|---------------|
| Ovarian HGSOC | Very high | TP53, BRCA |
| Triple-neg breast | High | TP53, PI3K |
| Colorectal MSS | Moderate-high | APC, TP53 |
| Colorectal MSI | Low | MMR deficiency |
| Thyroid (PTC) | Low | BRAF, RAS |
| Melanoma | Moderate | BRAF, NRAS |

## Prerequisites

* Python 3.10+
* GISTIC2 or similar for CNV analysis
* Gene signature databases
* Survival analysis packages

## Related Skills

* HRD_Analysis_Agent - For HR-specific instability
* Pan_Cancer_MultiOmics_Agent - For pan-cancer context
* Tumor_Clonal_Evolution_Agent - For evolutionary dynamics

## Research Applications

1. **Biomarker Development**: CIN as predictive marker
2. **Drug Development**: CIN-targeted therapy trials
3. **Evolution Studies**: Track CIN changes over time
4. **Resistance Mechanisms**: CIN and drug resistance

## Author

AI Group - Biomedical AI Platform
