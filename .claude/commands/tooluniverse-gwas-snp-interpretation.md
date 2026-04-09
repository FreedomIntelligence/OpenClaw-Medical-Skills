# tooluniverse-gwas-snp-interpretation

> Interpret genetic variants (SNPs) from GWAS studies by aggregating evidence from multiple databases (GWAS Catalog, Open Targets Genetics, ClinVar). Retrieves variant annotations, GWAS trait associations, fine-mapping evidence, locus-to-gene predictions, and clinical significance. Use when asked to interpret a SNP by rsID, find disease associations for a variant, assess clinical significance, or answer questions like "What diseases is rs429358 associated with?" or "Interpret rs7903146".

# GWAS SNP Interpretation Skill

## Overview

Interpret genetic variants (SNPs) from GWAS studies by aggregating evidence from multiple sources to provide comprehensive clinical and biological context.

**Use Cases:**
- "Interpret rs7903146" (TCF7L2 diabetes variant)
- "What diseases is rs429358 associated with?" (APOE Alzheimer's variant)
- "Clinical significance of rs1801133" (MTHFR variant)
- "Is rs12913832 in any fine-mapped loci?" (Eye color variant)

## What It Does

The skill provides a comprehensive interpretation of SNPs by:

1. **SNP Annotation**: Retrieves basic variant information including genomic coordinates, alleles, functional consequence, and mapped genes
2. **Association Discovery**: Finds all GWAS trait/disease associations with statistical significance
3. **Fine-Mapping Evidence**: Identifies credible sets the variant belongs to (fine-mapped causal loci)
4. **Gene Mapping**: Uses Locus-to-Gene (L2G) predictions to identify likely causal genes
5. **Clinical Summary**: Aggregates evidence into actionable clinical significance

## Workflow

```
User Input: rs7903146
    ↓
[1] SNP Lookup
    → Get location, consequence, MAF
    → gwas_get_snp_by_id
    ↓
[2] Association Search
    → Find all trait/disease associations
    → gwas_get_associations_for_snp
    ↓
[3] Fine-Mapping (Optional)
    → Get credible set membership
    → OpenTargets_get_variant_credible_sets
    ↓
[4] Gene Predictions
    → Extract L2G scores for causal genes
    → (embedded in credible sets)
    ↓
[5] Clinical Summary
    → Aggregate evidence
    → Identify key traits and genes
    ↓
Output: Comprehensive Interpretation Report
```

## Data Sources

### GWAS Catalog (EMBL-EBI)
- **SNP annotations**: Functional consequences, mapped genes, population frequencies
- **Associations**: P-values, effect sizes, study metadata
- **Coverage**: 350,000+ publications, 670,000+ associations

### Open Targets Genetics
- **Fine-mapping**: Statistical credible sets from SuSiE, FINEMAP methods
- **L2G predictions**: Machine learning-based gene prioritization
- **Colocalization**: QTL evidence for causal genes
- **Coverage**: UK Biobank, FinnGen, and other large cohorts

## Input Parameters

### Required
- `rs_id` (str): dbSNP rs identifier
  - Format: "rs" + number (e.g., "rs7903146")
  - Must be valid rsID in GWAS Catalog

### Optional
- `include_credible_sets` (bool, default=True): Query fine-mapping data
  - True: Complete interpretation (slower, ~10-30s)
  - False: Fast associations only (~2-5s)
- `p_threshold` (float, default=5e-8): Genome-wide significance threshold
- `max_associations` (int, default=100): Maximum associations to retrieve

## Output Format

Returns `SNPInterpretationReport` containing:

### 1. SNP Basic Info
```python
{
    'rs_id': 'rs7903146',
    'chromosome': '10',
    'position': 112998590,
    'ref_allele': 'C',
    'alt_allele': 'T',
    'consequence': 'intron_variant',
    'mapped_genes': ['TCF7L2'],
    'maf': 0.293
}
```

### 2. Trait Associations
```python
[
    {
        'trait': 'Type 2 diabetes',
        'p_value': 1.2e-128,
        'beta': '0.28 unit increase',
        'study_id': 'GCST010555',
        'pubmed_id': '33536258',
        'effect_allele': 'T'
    },
    ...
]
```

### 3. Credible Sets (Fine-Mapping)
```python
[
    {
        'study_id': 'GCST90476118',
        'trait': 'Renal failure',
        'finemapping_method': 'SuSiE-inf',
        'p_value': 3.5e-42,
        'predicted_genes': [
            {'gene': 'TCF7L2', 'score': 0.863}
        ],
        'region': '10:112950000-113050000'
    },
    ...
]
```

### 4. Clinical Significance
```
Genome-wide significant associations with 100 traits/diseases:
  - Type 2 diabetes
  - Diabetic retinopathy
  - HbA1c levels
  ...

Identified in 20 fine-mapped loci.
Predicted causal genes: TCF7L2
```

## Example Usage

See `QUICK_START.md` for platform-specific examples.

## Tools Used

### GWAS Catalog Tools
1. `gwas_get_snp_by_id`: Get SNP annotation
2. `gwas_get_associations_for_snp`: Get all trait associations

### Open Targets Tools
3. `OpenTargets_get_variant_info`: Get variant details with population frequencies
4. `OpenTargets_get_variant_credible_sets`: Get fine-mapping credible sets with L2G

## Interpretation Guide

### P-value Significance Levels
- **p < 5e-8**: Genome-wide significant (strong evidence)
- **p < 5e-6**: Suggestive (moderate evidence)
- **p < 0.05**: Nominal (weak evidence)

### L2G Score Interpretation
- **> 0.5**: High confidence causal gene
- **0.1-0.5**: Moderate confidence
- **< 0.1**: Low confidence

### Clinical Actionability
1. **High**: Multiple genome-wide significant associations + in credible sets + high L2G scores
2. **Moderate**: Genome-wide significant associations but limited fine-mapping
3. **Low**: Suggestive associations or limited replication

## Limitations

1. **Variant ID Conversion**: OpenTargets requires chr_pos_ref_alt format, which may need allele lookup
2. **Population Specificity**: Associations may vary by ancestry
3. **Effect Sizes**: Beta values are study-dependent (different phenotype scales)
4. **Causality**: Associations don't prove causation; fine-mapping improves confidence
5. **Currency**: Data reflects published GWAS; latest studies may not be included

## Best Practices

1. **Use Full Interpretation**: Enable `include_credible_sets=True` for clinical decisions
2. **Check Multiple Variants**: Look at other variants in the same locus
3. **Validate Populations**: Consider ancestry-specific effect sizes
4. **Review Publications**: Check original studies for context
5. **Integrate Evidence**: Combine with functional data, eQTLs, pQTLs

## Technical Notes

### Performance
- **Fast mode** (no credible sets): 2-5 seconds
- **Full mode** (with credible sets): 10-30 seconds
- **Bottleneck**: OpenTargets GraphQL API rate limits

### Error Handling
- Invalid rs_id: Returns error message
- No associations: Returns empty list with note
- API failures: Graceful degradation (returns partial results)

## Related Skills

- **Gene Function Analysis**: Interpret predicted causal genes
- **Disease Ontology Lookup**: Understand trait classifications
- **PubMed Literature Search**: Find original GWAS publications
- **Variant Effect Prediction**: Functional consequence analysis

## References

1. GWAS Catalog: https://www.ebi.ac.uk/gwas/
2. Open Targets Genetics: https://genetics.opentargets.org/
3. GWAS Significance Thresholds: Fadista et al. 2016
4. L2G Method: Mountjoy et al. 2021 (Nature Genetics)

## Version

- **Version**: 1.0.0
- **Last Updated**: 2026-02-13
- **ToolUniverse Version**: >= 1.0.0
- **Tools Required**: gwas_get_snp_by_id, gwas_get_associations_for_snp, OpenTargets_get_variant_credible_sets
