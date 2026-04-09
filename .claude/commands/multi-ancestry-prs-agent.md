# multi-ancestry-prs-agent

> AI-powered multi-ancestry polygenic risk score calculation and optimization for equitable disease risk prediction across diverse global populations.

**Available tools:** Read, Bash

# Multi-Ancestry PRS Agent

The **Multi-Ancestry PRS Agent** provides AI-optimized polygenic risk score calculation designed to work across diverse ancestral populations. It addresses the critical limitation of European-biased GWAS by integrating trans-ancestry methods, improving risk prediction for underrepresented populations and enabling equitable precision medicine.

## When to Use This Skill

* When calculating PRS for non-European ancestry individuals.
* For developing trans-ancestry risk prediction models.
* To reduce PRS bias across ancestral populations.
* When integrating multi-ancestry GWAS summary statistics.
* For research on PRS portability and equity.

## Core Capabilities

1. **Multi-Ancestry PRS**: Calculate ancestry-aware polygenic scores.

2. **Trans-Ancestry Optimization**: Optimize weights across populations.

3. **Local Ancestry Integration**: Account for admixed genomes.

4. **Ensemble Methods**: Combine multiple PRS approaches.

5. **Ancestry Calibration**: Population-specific score calibration.

6. **Equity Assessment**: Evaluate prediction fairness across groups.

## Supported Ancestries

| Ancestry | Training Data Availability | PRS Performance |
|----------|---------------------------|-----------------|
| European (EUR) | Excellent | High |
| East Asian (EAS) | Good | Good |
| South Asian (SAS) | Moderate | Moderate |
| African (AFR) | Limited | Lower |
| Hispanic/Latino (AMR) | Limited | Variable |
| Middle Eastern (MID) | Very Limited | Lower |

## Multi-Ancestry Methods

| Method | Approach | Best For |
|--------|----------|----------|
| PRS-CSx | Cross-population shrinkage | Multi-ancestry |
| PRS-Multi | Multi-population training | Large cohorts |
| Ensemble | Combined methods | Best overall |
| Local Ancestry | Ancestry-specific weights | Admixed populations |
| GPSMult | Integrated multi-trait | Correlated traits |

## Workflow

1. **Input**: Individual genotypes, target ancestry, disease/trait.

2. **Ancestry Inference**: Determine genetic ancestry.

3. **Method Selection**: Choose optimal PRS approach.

4. **Score Calculation**: Compute ancestry-aware PRS.

5. **Calibration**: Apply population-specific calibration.

6. **Risk Stratification**: Categorize into risk groups.

7. **Output**: PRS, percentile, clinical interpretation.

## Example Usage

**User**: "Calculate multi-ancestry coronary artery disease PRS for this admixed individual with African and European ancestry."

**Agent Action**:
```bash
python3 Skills/Precision_Medicine/Multi_Ancestry_PRS_Agent/calc_prs.py \
    --genotypes patient_genotypes.vcf.gz \
    --ancestry admixed_AFR_EUR \
    --local_ancestry lai_segments.bed \
    --trait coronary_artery_disease \
    --method prs_csx \
    --gwas_summary_stats eur_gwas.txt,afr_gwas.txt \
    --calibration_cohort 1kg_admixed \
    --output prs_results/
```

## Input Requirements

| Input | Format | Purpose |
|-------|--------|---------|
| Genotypes | VCF/PLINK | Individual variants |
| Ancestry | Estimated or self-reported | Method selection |
| GWAS Summary Stats | Multiple ancestries | Score weights |
| Local Ancestry | LAI segments | Admixture handling |
| Reference Panel | Multi-ancestry | LD calculation |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| PRS Score | Raw polygenic score | .csv |
| Percentile | Population-specific ranking | .csv |
| Risk Category | High/Intermediate/Low | .csv |
| Ancestry Breakdown | Component scores | .json |
| Confidence Interval | Score uncertainty | .json |
| Clinical Interpretation | Risk explanation | .md |

## Disease-Specific Performance

| Disease | Multi-Ancestry AUC | EUR Only AUC | Improvement |
|---------|-------------------|--------------|-------------|
| CAD | 0.75-0.80 | 0.70-0.85 | 5-10% in non-EUR |
| Type 2 Diabetes | 0.70-0.75 | 0.65-0.72 | 8-12% in AFR |
| Breast Cancer | 0.65-0.72 | 0.60-0.70 | 5-8% globally |
| Alzheimer's | 0.70-0.78 | 0.65-0.75 | 5-10% in diverse |

## AI/ML Components

**PRS Optimization**:
- Bayesian shrinkage (PRS-CS)
- Cross-population learning
- Neural network weight optimization

**Ancestry Inference**:
- Supervised classification
- Unsupervised clustering (PCA, ADMIXTURE)
- Local ancestry inference (RFMix)

**Ensemble Learning**:
- Stacking multiple PRS methods
- Ancestry-stratified weighting
- Uncertainty quantification

## Clinical Integration

| Application | PRS Role | Clinical Action |
|-------------|----------|-----------------|
| Primary Prevention | Risk stratification | Screening intensity |
| Risk Communication | Personalized risk | Lifestyle modification |
| Treatment Selection | Predicted response | Drug choice |
| Family Screening | Cascade testing | Genetic counseling |

## Prerequisites

* Python 3.10+
* PLINK 2.0
* PRSice-2, LDpred2, PRS-CSx
* Multi-ancestry reference panels
* GWAS summary statistics

## Related Skills

* PRS_Net_Deep_Learning_Agent - Deep learning PRS
* Pharmacogenomics_Agent - Drug-gene interactions
* PopEVE_Variant_Predictor_Agent - Variant interpretation
* DiagAI_Agent - Clinical integration

## Bias and Fairness

| Bias Type | Cause | Mitigation |
|-----------|-------|------------|
| Discovery Bias | EUR-dominated GWAS | Multi-ancestry GWAS |
| LD Variation | Population-specific LD | Local ancestry adjustment |
| Allele Frequency | Differing frequencies | Population-specific weights |
| Effect Size | Heterogeneous effects | Trans-ancestry meta-analysis |

## Large-Scale Initiatives

| Initiative | Focus | Contribution |
|------------|-------|--------------|
| All of Us | US diversity | 1M diverse participants |
| PAGE | Multi-ethnic GWAS | Discovery in diverse |
| H3Africa | African genomics | Continental diversity |
| Mexican Biobank | Latin American | Admixed populations |
| GBMI | Global Biobank | Multi-ancestry meta-analysis |

## Special Considerations

1. **Self-Reported Ancestry**: May not match genetic ancestry
2. **Admixture**: Require local ancestry methods
3. **Population Stratification**: Careful covariate adjustment
4. **Clinical Validity**: Validate in target population
5. **Health Equity**: Consider access disparities

## ESC Guidelines Integration (2025)

| Recommendation | PRS Role | Evidence Level |
|----------------|----------|----------------|
| CV Risk Assessment | Risk modifier | IIa, B |
| Statin Decisions | Borderline risk reclassification | IIa, B |
| Family History Enhancement | Quantify genetic burden | IIa, C |

## Limitations

| Limitation | Impact | Research Needed |
|------------|--------|-----------------|
| AFR Performance | Lower accuracy | More GWAS |
| Rare Variants | Not captured | WGS integration |
| Gene-Environment | Not modeled | Interaction studies |
| Clinical Utility | Limited evidence | Randomized trials |

## Author

AI Group - Biomedical AI Platform
