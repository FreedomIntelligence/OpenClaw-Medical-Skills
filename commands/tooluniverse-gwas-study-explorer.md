# tooluniverse-gwas-study-explorer

> Compare GWAS studies, perform meta-analyses, and assess replication across cohorts. Integrates NHGRI-EBI GWAS Catalog and Open Targets Genetics to compare study designs, effect sizes, ancestry diversity, and heterogeneity statistics. Use when comparing GWAS studies for a trait, performing meta-analysis of genetic loci, assessing replication across cohorts, or exploring the genetic architecture of complex diseases.

# GWAS Study Deep Dive & Meta-Analysis

**Compare GWAS studies, perform meta-analyses, and assess replication across cohorts**

---

## Overview

The GWAS Study Deep Dive & Meta-Analysis skill enables comprehensive comparison of genome-wide association studies (GWAS) for the same trait, meta-analysis of genetic loci across studies, and systematic assessment of replication and study quality. It integrates data from the NHGRI-EBI GWAS Catalog and Open Targets Genetics to provide a complete picture of the genetic architecture of complex traits.

### Key Capabilities

1. **Study Comparison**: Compare all GWAS studies for a trait, assessing sample sizes, ancestries, and platforms
2. **Meta-Analysis**: Aggregate effect sizes across studies and calculate heterogeneity statistics
3. **Replication Assessment**: Identify replicated vs novel findings across discovery and replication cohorts
4. **Quality Evaluation**: Assess statistical power, ancestry diversity, and data availability

---

## Use Cases

### 1. Comprehensive Trait Analysis
**Scenario**: "I want to understand all available GWAS data for type 2 diabetes"

**Workflow**:
- Search for all T2D studies in GWAS Catalog
- Filter by sample size and ancestry
- Extract top associations from each study
- Identify consistently replicated loci
- Assess ancestry-specific effects

**Outcome**: Complete landscape of T2D genetics with replicated findings and population-specific signals

### 2. Locus-Specific Meta-Analysis
**Scenario**: "Is the TCF7L2 association with T2D consistent across all studies?"

**Workflow**:
- Retrieve all TCF7L2 (rs7903146) associations for T2D
- Calculate combined effect size and p-value
- Assess heterogeneity (I² statistic)
- Generate forest plot data
- Interpret heterogeneity level

**Outcome**: Quantitative assessment of effect size consistency with heterogeneity interpretation

### 3. Replication Analysis
**Scenario**: "Which findings from the discovery cohort replicated in the independent sample?"

**Workflow**:
- Get top hits from discovery study
- Check for presence and significance in replication study
- Assess direction consistency
- Calculate replication rate
- Identify novel vs failed replication

**Outcome**: Systematic replication report with success rates and failed findings

### 4. Multi-Ancestry Comparison
**Scenario**: "Are T2D loci consistent across European and East Asian populations?"

**Workflow**:
- Filter studies by ancestry
- Compare top associations between populations
- Identify shared vs population-specific loci
- Assess allele frequency differences
- Evaluate transferability of genetic risk scores

**Outcome**: Ancestry-specific genetic architecture with transferability assessment

---

## Statistical Methods

### Meta-Analysis Approach

This skill implements standard GWAS meta-analysis methods:

**Fixed-Effects Model**:
- Used when heterogeneity is low (I² < 25%)
- Weights studies by inverse variance
- Assumes true effect size is the same across studies

**Random-Effects Model** (recommended when I² > 50%):
- Accounts for between-study variation
- More conservative than fixed-effects
- Better for diverse ancestries or methodologies

**Heterogeneity Assessment**:

The **I² statistic** measures the percentage of variance due to between-study heterogeneity:

```
I² = [(Q - df) / Q] × 100%

where Q = Cochran's Q statistic
      df = degrees of freedom (n_studies - 1)
```

**Interpretation Guidelines**:
- **I² < 25%**: Low heterogeneity → fixed-effects appropriate
- **I² = 25-50%**: Moderate heterogeneity → investigate sources
- **I² = 50-75%**: Substantial heterogeneity → random-effects preferred
- **I² > 75%**: Considerable heterogeneity → meta-analysis may not be appropriate

### Sources of Heterogeneity

Common reasons for high I²:

1. **Ancestry differences**: Different allele frequencies and LD structure
2. **Phenotype heterogeneity**: Trait definition varies across studies
3. **Platform differences**: Imputation quality and coverage
4. **Winner's curse**: Discovery studies overestimate effect sizes
5. **Cohort characteristics**: Age, sex, environmental factors

**Recommendations**:
- Perform subgroup analysis by ancestry
- Use meta-regression to investigate sources
- Consider excluding outlier studies
- Apply genomic control correction

---

## Study Quality Assessment

### Quality Metrics

The skill evaluates studies based on:

**1. Sample Size**:
- Power to detect associations (80% power requires n > 10,000 for OR=1.2)
- Precision of effect size estimates
- Ability to detect modest effects

**2. Ancestry Diversity**:
- Single-ancestry vs multi-ancestry
- Population stratification control
- Transferability of findings

**3. Data Availability**:
- Summary statistics available for meta-analysis
- Individual-level data vs summary-level
- Imputation quality scores

**4. Genotyping Quality**:
- Platform density and coverage
- Imputation reference panel
- Quality control measures

**5. Statistical Rigor**:
- Genome-wide significance threshold (p < 5×10⁻⁸)
- Multiple testing correction
- Replication in independent cohort

### Quality Tiers

**Tier 1 (High Quality)**:
- n ≥ 50,000
- Summary statistics available
- Multi-ancestry or large single-ancestry
- Imputed to high-quality reference
- Independent replication

**Tier 2 (Moderate Quality)**:
- n ≥ 10,000
- Standard GWAS platform
- Adequate power for common variants
- Some data availability

**Tier 3 (Limited)**:
- n < 10,000
- Limited power
- May miss modest effects
- Use with caution

---

## Best Practices

### Before Meta-Analysis

1. **Check phenotype consistency**: Ensure studies measure the same trait
2. **Verify ancestry overlap**: High heterogeneity expected if ancestries differ
3. **Harmonize alleles**: Align effect alleles across studies
4. **Quality control**: Exclude low-quality studies or associations

### Interpreting Results

1. **Genome-wide significance**: p < 5×10⁻⁸ (Bonferroni for ~1M independent tests)
2. **Replication threshold**: p < 0.05 in independent cohort
3. **Direction consistency**: Effect should be same direction across studies
4. **Heterogeneity**: I² > 50% suggests caution in interpretation

### Common Pitfalls

❌ **Don't**:
- Meta-analyze without checking heterogeneity
- Ignore ancestry differences
- Over-interpret nominal p-values
- Assume replication failure means false positive

✅ **Do**:
- Always report I² statistic
- Perform sensitivity analyses
- Consider ancestry-stratified analysis
- Account for winner's curse in discovery studies

---

## Limitations & Caveats

### Data Limitations

1. **Incomplete Overlap**: Studies may analyze different SNPs
2. **Cohort Overlap**: Some cohorts participate in multiple studies (inflates significance)
3. **Publication Bias**: Significant findings more likely to be published
4. **Winner's Curse**: Discovery studies overestimate effect sizes
5. **Imputation Quality**: Varies across studies and populations

### Statistical Limitations

1. **Heterogeneity**: High I² may preclude meaningful meta-analysis
2. **Sample Size Differences**: Large studies dominate fixed-effects models
3. **Allele Frequency Differences**: Same variant has different effects across ancestries
4. **Linkage Disequilibrium**: Fine-mapping needed to identify causal variants
5. **Gene-Environment Interactions**: Not captured in standard meta-analysis

### Interpretation Guidelines

**When I² > 75%**:
- Meta-analysis results should be interpreted with extreme caution
- Investigate sources of heterogeneity systematically
- Consider ancestry-specific or subgroup analyses
- Descriptive comparison may be more appropriate than meta-analysis

**When Studies Conflict**:
- Check for methodological differences
- Verify phenotype definitions match
- Investigate population stratification
- Consider conditional analysis

---

## Scientific References

### Key Publications

1. **GWAS Best Practices**:
   - Visscher et al. (2017). "10 Years of GWAS Discovery" *American Journal of Human Genetics* 101(1): 5-22
   - PMID: 28686856
   - DOI: 10.1016/j.ajhg.2017.06.005

2. **Meta-Analysis Methods**:
   - Evangelou & Ioannidis (2013). "Meta-analysis methods for genome-wide association studies and beyond" *Nature Reviews Genetics* 14: 379-389
   - PMID: 23657481

3. **Heterogeneity Interpretation**:
   - Higgins et al. (2003). "Measuring inconsistency in meta-analyses" *BMJ* 327: 557-560
   - PMID: 12958120

4. **Multi-Ancestry GWAS**:
   - Peterson et al. (2019). "Genome-wide Association Studies in Ancestrally Diverse Populations" *Nature Reviews Genetics* 20: 409-422
   - PMID: 30926972

5. **Replication Standards**:
   - Chanock et al. (2007). "Replicating genotype-phenotype associations" *Nature* 447: 655-660
   - PMID: 17554299

---

## Tools Used

### GWAS Catalog API
- `gwas_search_studies`: Find studies by trait
- `gwas_get_study_by_id`: Get detailed study metadata
- `gwas_get_associations_for_study`: Retrieve study associations
- `gwas_get_associations_for_snp`: Get SNP associations across studies
- `gwas_search_associations`: Search associations by trait

### Open Targets Genetics GraphQL API
- `OpenTargets_search_gwas_studies_by_disease`: Disease-based study search
- `OpenTargets_get_gwas_study`: Detailed study information with LD populations
- `OpenTargets_get_variant_credible_sets`: Fine-mapped loci for variant
- `OpenTargets_get_study_credible_sets`: All credible sets for study
- `OpenTargets_get_variant_info`: Variant annotation and allele frequencies

---

## Glossary

**Association**: Statistical relationship between a genetic variant and a trait

**Credible Set**: Set of variants likely to contain the causal variant (from fine-mapping)

**Effect Size**: Magnitude of genetic association (beta coefficient or odds ratio)

**Fine-Mapping**: Statistical method to identify causal variants within a locus

**Genome-Wide Significance**: p < 5×10⁻⁸, accounting for ~1M independent tests

**Heterogeneity (I²)**: Percentage of variance due to between-study differences

**L2G (Locus-to-Gene)**: Score predicting which gene is affected by a GWAS locus

**LD (Linkage Disequilibrium)**: Non-random association of alleles at different loci

**Meta-Analysis**: Statistical combination of results from multiple studies

**Replication**: Independent confirmation of an association in a new cohort

**Summary Statistics**: Per-SNP statistics (p-value, beta, SE) from GWAS

**Winner's Curse**: Overestimation of effect size in discovery studies

---

## Next Steps

After running this skill, consider:

1. **Fine-Mapping**: Use credible sets from Open Targets to identify causal variants
2. **Functional Follow-Up**: Investigate biological mechanisms of replicated loci
3. **Genetic Risk Scores**: Calculate polygenic risk scores using validated loci
4. **Drug Target Identification**: Use L2G scores to prioritize therapeutic targets
5. **Cross-Trait Analysis**: Look for pleiotropy with related traits

---

## Version History

- **v1.0** (2026-02-13): Initial release with study comparison, meta-analysis, and replication assessment

---

**Created by**: ToolUniverse GWAS Analysis Team
**Last Updated**: 2026-02-13
**License**: Open source (MIT)
