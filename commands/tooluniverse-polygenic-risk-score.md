# tooluniverse-polygenic-risk-score

> Build and interpret polygenic risk scores (PRS) for complex diseases using GWAS summary statistics. Calculates genetic risk profiles, interprets PRS percentiles, and assesses disease predisposition across conditions including type 2 diabetes, coronary artery disease, and Alzheimer's disease. Use when asked to calculate polygenic risk scores, interpret genetic risk for complex diseases, build custom PRS from GWAS data, or answer questions like "What is my genetic predisposition to breast cancer?"

# Polygenic Risk Score (PRS) Builder

Build and interpret polygenic risk scores for complex diseases using genome-wide association study (GWAS) data.

## Overview

**Use Cases:**
- "Calculate my genetic risk for type 2 diabetes"
- "Build a polygenic risk score for coronary artery disease"
- "What's my genetic predisposition to Alzheimer's disease?"
- "Interpret my PRS percentile for breast cancer risk"

**What This Skill Does:**
- Extracts genome-wide significant variants (p < 5e-8) from GWAS Catalog
- Builds weighted PRS models using effect sizes (beta coefficients)
- Calculates individual risk scores from genotype data
- Interprets PRS as population percentiles and risk categories

**What This Skill Does NOT Do:**
- Diagnose disease (PRS is probabilistic, not deterministic)
- Replace clinical assessment or genetic counseling
- Account for non-genetic factors (lifestyle, environment)
- Provide treatment recommendations

## Methodology

### PRS Calculation Formula

A polygenic risk score is calculated as a weighted sum across genetic variants:

```
PRS = Σ (dosage_i × effect_size_i)
```

Where:
- **dosage_i**: Number of effect alleles at SNP i (0, 1, or 2)
- **effect_size_i**: Beta coefficient or log(odds ratio) from GWAS

### Standardization

Raw PRS is standardized to z-scores for interpretation:

```
z-score = (PRS - population_mean) / population_std
```

This allows comparison to population distribution and percentile calculation.

### Significance Thresholds

- **Genome-wide significance**: p < 5×10⁻⁸ (default threshold)
- This corrects for ~1 million independent tests across the genome
- Relaxed thresholds (e.g., p < 1×10⁻⁵) can include more SNPs but may add noise

### Effect Size Handling

- **Continuous traits** (e.g., height, BMI): Beta coefficient (units of trait per allele)
- **Binary traits** (e.g., disease): Odds ratio converted to log-odds (beta = ln(OR))
- Missing effect sizes or non-significant SNPs are excluded

## Data Sources

This skill uses ToolUniverse GWAS tools to query:

1. **GWAS Catalog** (EMBL-EBI)
   - Curated GWAS associations
   - 5000+ studies, millions of variants
   - Tools: `gwas_get_associations_for_trait`, `gwas_get_snp_by_id`

2. **Open Targets Genetics**
   - Integrated genetics platform
   - Fine-mapped credible sets
   - Tools: `OpenTargets_search_gwas_studies_by_disease`, `OpenTargets_get_variant_info`

## Key Concepts

### Polygenic Risk Scores (PRS)

Polygenic risk scores aggregate the effects of many genetic variants to estimate an individual's genetic predisposition to a trait or disease. Unlike Mendelian diseases caused by single mutations, complex diseases involve hundreds to thousands of variants, each with small effects.

**Key Properties:**
- **Continuous distribution**: PRS forms a bell curve in populations
- **Relative risk**: Compares individual to population average
- **Probabilistic**: High PRS doesn't guarantee disease, low PRS doesn't guarantee protection
- **Ancestry-specific**: PRS accuracy depends on matching GWAS and target ancestry

### GWAS (Genome-Wide Association Studies)

GWAS compare allele frequencies between cases and controls (or correlate with trait values) across millions of SNPs to identify disease-associated variants.

**Study Design:**
- **Discovery cohort**: Initial identification of associations
- **Replication cohort**: Validation in independent samples
- **Sample size**: Larger studies detect smaller effects (power ∝ √N)
- **Multiple testing correction**: Bonferroni-type correction for ~1M tests

### Effect Sizes and Odds Ratios

- **Beta (β)**: Change in trait per copy of effect allele
  - Example: β = 0.5 kg/m² means each allele increases BMI by 0.5 units
- **Odds Ratio (OR)**: Multiplicative change in disease odds
  - OR = 1.5 means 50% increased odds per allele
  - Convert to beta: β = ln(OR)

### Linkage Disequilibrium (LD) and Clumping

Nearby variants are often inherited together (LD). To avoid double-counting:
- **LD clumping**: Select independent variants (r² < 0.1 within 1 Mb windows)
- **Fine-mapping**: Statistical methods to identify causal variants
- This skill uses raw associations; production PRS should include LD pruning

### Population Stratification

GWAS and PRS are most accurate when ancestries match:
- **Population structure**: Different ancestries have different allele frequencies
- **Transferability**: European-trained PRS perform worse in non-European populations
- **Solution**: Train PRS on diverse cohorts or use ancestry-matched references

## Applications

### Clinical Risk Assessment

PRS can stratify individuals for:
- **Screening programs**: Target high-risk individuals (e.g., mammography, colonoscopy)
- **Prevention strategies**: Lifestyle interventions for high genetic risk
- **Drug response**: Pharmacogenomics based on metabolism genes

**Example**: Khera et al. (2018) showed PRS identifies 3× more individuals at >3-fold coronary artery disease risk than monogenic mutations.

### Research Applications

- **Gene discovery**: PRS-based phenome-wide association studies (PheWAS)
- **Genetic correlation**: Compare PRS across traits
- **Causal inference**: Mendelian randomization using PRS as instruments
- **Simulation studies**: Model polygenic architecture

### Personal Genomics

Consumer genetic testing (23andMe, Ancestry DNA) provides raw genotypes. Users can:
- Calculate PRS for traits not reported
- Compare to published PRS models
- Understand genetic contribution vs. lifestyle factors

**Caution**: Personal PRS should not replace medical advice. Results may cause anxiety if not properly contextualized.

## Limitations and Considerations

### Scientific Limitations

1. **Heritability Gap**: PRS explains a fraction of genetic heritability
   - Type 2 diabetes: ~50% heritable, PRS explains ~10-20%
   - Rare variants, epistasis, and gene-environment interactions not captured

2. **Ancestry Bias**: Most GWAS are European ancestry
   - PRS accuracy drops in non-European populations
   - Need for diverse cohort recruitment

3. **Winner's Curse**: Discovery effect sizes often overestimated
   - Replication studies show smaller effects
   - Meta-analyses provide better estimates

4. **Missing Heritability**: Unexplained genetic contribution from:
   - Rare variants not captured by SNP arrays
   - Structural variants (CNVs, inversions)
   - Epigenetic factors

### Clinical Limitations

1. **Not Diagnostic**: PRS is probabilistic, not deterministic
   - High PRS doesn't mean you will get disease
   - Low PRS doesn't mean you won't get disease

2. **Environmental Factors**: Many complex diseases are 50%+ environmental
   - Smoking, diet, exercise, stress, pollution
   - PRS doesn't account for these

3. **Pleiotropy**: Same variants affect multiple traits
   - Genetic correlation between diseases
   - Risk for one may protect against another

4. **Actionability**: Not all high-risk predictions have interventions
   - Alzheimer's PRS has limited actionability currently
   - Ethical considerations for testing

### Ethical Considerations

1. **Privacy**: Genetic data is identifiable and permanent
   - Can't be changed like passwords
   - Familial implications (relatives share genetics)

2. **Discrimination**: Potential for genetic discrimination
   - GINA protects against health/employment discrimination (US)
   - Life insurance and long-term care not protected

3. **Psychological Impact**: Knowledge of high risk can cause anxiety
   - Need for genetic counseling
   - Risk communication training

4. **Equity**: Ancestry bias means unequal benefits
   - Europeans benefit most from current PRS
   - Exacerbates health disparities

## References

### Key Publications

1. **Lambert et al. (2021)**: "The Polygenic Score Catalog as an open database for reproducibility and systematic evaluation"
   - PGS Catalog: https://www.pgscatalog.org/
   - Repository of published PRS models

2. **Khera et al. (2018)**: "Genome-wide polygenic scores for common diseases identify individuals with risk equivalent to monogenic mutations"
   - Nature Genetics, 50:1219–1224
   - Demonstrated clinical utility of PRS

3. **Torkamani et al. (2018)**: "The personal and clinical utility of polygenic risk scores"
   - Nature Reviews Genetics, 19:581–590
   - Comprehensive review of PRS applications

4. **Martin et al. (2019)**: "Clinical use of current polygenic risk scores may exacerbate health disparities"
   - Nature Genetics, 51:584–591
   - Addresses ancestry bias and equity concerns

5. **Choi et al. (2020)**: "Tutorial: a guide to performing polygenic risk score analyses"
   - Nature Protocols, 15:2759–2772
   - Practical guide to PRS calculation and evaluation

### Resources

- **PGS Catalog**: https://www.pgscatalog.org/ - Published PRS models
- **LD Hub**: http://ldsc.broadinstitute.org/ - Genetic correlations
- **PRSice**: https://www.prsice.info/ - PRS calculation software
- **GWAS Catalog**: https://www.ebi.ac.uk/gwas/ - Association database

## Workflow

### 1. Trait Selection

Identify the disease or trait of interest:
- Use standard terminology (e.g., "type 2 diabetes" not "T2D")
- Check GWAS Catalog for availability
- Verify sufficient GWAS studies exist (n > 10,000 samples ideal)

### 2. Association Collection

Query GWAS databases for genome-wide significant associations:
```python
prs = build_polygenic_risk_score(
    trait="coronary artery disease",
    p_threshold=5e-8,  # Genome-wide significance
    max_snps=1000
)
```

**Considerations:**
- P-value threshold: 5e-8 is conservative, 1e-5 includes more variants
- LD clumping: Production systems should prune correlated SNPs
- Study quality: Prefer large meta-analyses over small studies

### 3. Effect Size Extraction

Extract beta coefficients or odds ratios:
- Beta for continuous traits (direct use)
- OR for binary traits (convert to log-odds)
- Handle missing values (exclude or impute from meta-analysis)

### 4. SNP Filtering

Quality control filters:
- **MAF filter**: Exclude rare variants (MAF < 0.01) for robustness
- **Genotype QC**: Remove SNPs with high missingness (> 10%)
- **Hardy-Weinberg**: Exclude SNPs violating HWE (p < 1e-6)
- **Ambiguous SNPs**: Remove A/T and G/C SNPs (strand ambiguity)

### 5. Score Calculation

Calculate weighted sum of genotype dosages:
```python
result = calculate_personal_prs(
    prs_weights=prs,
    genotypes=my_genotypes,
    population_mean=0.0,
    population_std=1.0
)
```

**Genotype Sources:**
- 23andMe raw data export
- Ancestry DNA raw data
- Whole genome sequencing (VCF files)
- SNP array data (Illumina, Affymetrix)

### 6. Risk Interpretation

Convert to percentiles and risk categories:
```python
result = interpret_prs_percentile(result)
print(f"Percentile: {result.percentile:.1f}%")
print(f"Risk: {result.risk_category}")
```

**Risk Categories:**
- **Low risk**: < 20th percentile (genetic protection)
- **Average risk**: 20-80th percentile (typical genetic predisposition)
- **Elevated risk**: 80-95th percentile (moderately increased risk)
- **High risk**: > 95th percentile (substantially increased risk)

**Clinical Interpretation:**
- Percentiles assume normal distribution
- Relative risk vs. average (not absolute risk)
- Combine with family history, clinical risk factors
- PRS is NOT diagnostic - many high-risk individuals never develop disease

## Best Practices

### PRS Construction

1. **Use validated PRS from PGS Catalog** when available
   - Published models have been externally validated
   - Include LD clumping and ancestry-specific weights

2. **Match ancestries** between GWAS and target population
   - European GWAS for European individuals
   - Use multi-ancestry GWAS when available

3. **Include as many SNPs as practical**
   - More SNPs = better prediction (up to a point)
   - Balance between coverage and genotyping cost

4. **Consider trait architecture**
   - Highly polygenic traits (height, education): benefit from relaxed thresholds
   - Oligogenic traits (IBD, T1D): few large-effect variants, strict thresholds

### Clinical Use

1. **Combine with clinical risk scores**
   - Add PRS to Framingham Risk Score, QRISK, etc.
   - Integrated models improve prediction

2. **Stratify screening and prevention**
   - Intensify surveillance for high PRS (e.g., earlier mammography)
   - Lifestyle interventions for modifiable risk

3. **Provide genetic counseling**
   - Explain probabilistic nature of PRS
   - Discuss limitations and uncertainty
   - Address psychological impact

4. **Consider actionability**
   - Is there an intervention for high risk?
   - Benefits vs. harms of knowing genetic risk

### Research Use

1. **Report methods transparently**
   - Document SNP selection criteria
   - Report LD clumping parameters
   - Specify ancestry of GWAS and target

2. **Validate in held-out cohorts**
   - Split data: training vs. testing
   - Report out-of-sample prediction accuracy (R², AUC)

3. **Compare to existing PRS**
   - Benchmark against PGS Catalog models
   - Report incremental improvement

4. **Test across ancestries**
   - Evaluate transferability to non-European populations
   - Report performance stratified by ancestry

## Disclaimer

**This skill is for educational and research purposes only.**

- **Not for clinical diagnosis or treatment decisions**
- **Not validated for clinical use** - use PGS Catalog models for clinical-grade PRS
- **Requires genetic counseling** - interpretation requires expertise
- **Does not account for family history, environment, or lifestyle factors**
- **Ancestry-specific** - accuracy depends on matching GWAS ancestry

**For clinical genetic testing, consult:**
- Genetic counselors (certified by ABGC/ABMGG)
- Medical geneticists
- Healthcare providers with genomics training

PRS is a rapidly evolving field. Guidelines and best practices will continue to change as research progresses.

**Regulatory Status:**
- FDA does not currently regulate PRS (as of 2024)
- Some countries restrict direct-to-consumer genetic risk reporting
- Check local regulations before clinical implementation
