# hrd-analysis-agent

> AI-powered homologous recombination deficiency (HRD) analysis for PARP inhibitor response prediction using genomic scarring signatures and BRCA pathway assessment.

**Available tools:** Read, Bash

# HRD Analysis Agent

The **HRD Analysis Agent** provides comprehensive analysis of homologous recombination deficiency for predicting response to PARP inhibitors and platinum chemotherapy. It integrates genomic scarring signatures (LOH, TAI, LST), BRCA1/2 status, and HRD gene pathway analysis.

## When to Use This Skill

* When determining HRD status for PARP inhibitor eligibility.
* To calculate genomic instability scores (GIS) from tumor sequencing.
* For analyzing BRCA1/2 and HRD gene mutations.
* When predicting response to PARP inhibitors or platinum chemotherapy.
* To identify "BRCAness" phenotype in BRCA wild-type tumors.

## Core Capabilities

1. **Genomic Scar Scoring**: Calculate LOH, TAI, and LST scores from copy number data.

2. **BRCA Pathway Analysis**: Assess mutations in BRCA1, BRCA2, and 13 other HRD genes.

3. **HRD Classification**: Determine HRD-positive vs. HRD-negative status.

4. **PARP Inhibitor Prediction**: Predict response to olaparib, niraparib, rucaparib, talazoparib.

5. **Platinum Sensitivity**: Predict platinum chemotherapy sensitivity.

6. **Reversion Detection**: Identify BRCA reversion mutations restoring HR function.

## HRD Scoring Components

| Score | Definition | Biological Basis |
|-------|------------|------------------|
| LOH | Loss of heterozygosity regions >15 Mb | Genomic scarring |
| TAI | Telomeric allelic imbalance | End-to-end fusions |
| LST | Large-scale state transitions | Break-induced repair |
| GIS | Combined LOH + TAI + LST | Overall HRD score |

**HRD-Positive Threshold**: GIS ≥ 42 (Myriad myChoice) or equivalent

## HRD Gene Panel

| Gene | Function | HRD Contribution |
|------|----------|------------------|
| BRCA1 | HR core component | Major |
| BRCA2 | RAD51 loading | Major |
| PALB2 | BRCA2 partner | Moderate-Major |
| RAD51C/D | HR mediators | Moderate |
| ATM | DNA damage sensing | Moderate |
| CHEK2 | Cell cycle checkpoint | Moderate |
| BARD1 | BRCA1 partner | Moderate |
| BRIP1 | Fanconi pathway | Moderate |
| CDK12 | Transcription | Variable |
| RAD51B | HR mediator | Low-Moderate |

## Workflow

1. **Input**: Copy number segments, somatic mutations, germline variants.

2. **Scar Calculation**: Compute LOH, TAI, LST from segmented CNV data.

3. **Gene Analysis**: Assess pathogenic variants in HRD genes.

4. **Score Integration**: Calculate composite GIS score.

5. **Classification**: Determine HRD status.

6. **Reversion Check**: Screen for reversion mutations.

7. **Output**: HRD score, classification, gene mutations, treatment recommendations.

## Example Usage

**User**: "Analyze HRD status for this ovarian cancer patient to guide PARP inhibitor selection."

**Agent Action**:
```bash
python3 Skills/Oncology/HRD_Analysis_Agent/hrd_analyzer.py \
    --cnv_segments tumor_segments.tsv \
    --mutations somatic_variants.maf \
    --germline germline_variants.vcf \
    --tumor_type ovarian \
    --purity 0.65 \
    --ploidy 2.1 \
    --output hrd_report.json
```

## Commercial HRD Tests

| Test | Components | Threshold | FDA Status |
|------|------------|-----------|------------|
| myChoice CDx | GIS + BRCA | ≥42 or BRCA+ | FDA approved |
| FoundationOne | LOH | ≥16% | FDA approved |
| SOPHiA DDM HRD | GIS + BRCA | ≥42 or BRCA+ | CE-IVD |

## Clinical Indications

**FDA-Approved PARP Inhibitor Indications**:
- **Ovarian**: HRD+ or BRCA+ (maintenance, later-line)
- **Breast**: gBRCA+ (HER2-, metastatic)
- **Pancreatic**: gBRCA+ (maintenance)
- **Prostate**: HRR gene mutated (mCRPC)

## Response Prediction

| Status | PARP Response | Platinum Response |
|--------|---------------|-------------------|
| BRCA mutated | Very high | High |
| HRD+ / BRCA WT | High | Moderate-High |
| HRD- / BRCA WT | Limited | Standard |
| Reversion+ | Poor | Poor |

## AI/ML Components

**GIS Calculation**:
- ASCAT/FACETS for allele-specific CNV
- HRDetect algorithm integration
- ML refinement of thresholds

**Reversion Detection**:
- Frameshift restoration analysis
- Splice site reversion
- Secondary deletion removing stop

**Response Prediction**:
- Multi-feature model (GIS + genes + expression)
- HRDetect signature scoring
- Clinical outcome integration

## Resistance Mechanisms

| Mechanism | Detection | Implication |
|-----------|-----------|-------------|
| BRCA reversion | Sequencing | Acquired resistance |
| 53BP1 loss | Expression/mutation | Rescued HR |
| ABCB1 upregulation | Expression | Drug efflux |
| PARP1 loss | Expression | Target loss |

## Prerequisites

* Python 3.10+
* ASCAT/FACETS for CNV
* HRDetect implementation
* Germline/somatic variant callers

## Related Skills

* Variant_Interpretation - For BRCA classification
* Liquid_Biopsy_Analytics_Agent - For ctDNA HRD monitoring
* Pan_Cancer_MultiOmics_Agent - For multi-omic context

## Special Considerations

1. **Tumor Purity**: Low purity affects scar detection
2. **Prior Therapy**: Platinum may select resistant clones
3. **Germline Testing**: Important for family counseling
4. **Reversion Monitoring**: Serial testing recommended

## Author

AI Group - Biomedical AI Platform
