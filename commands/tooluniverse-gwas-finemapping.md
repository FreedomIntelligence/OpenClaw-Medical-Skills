# tooluniverse-gwas-finemapping

> Identify and prioritize causal variants at GWAS loci using statistical fine-mapping and locus-to-gene predictions. Computes posterior probabilities for causal variants, links variants to genes via L2G predictions, annotates functional consequences, and suggests validation strategies. Use when asked to fine-map GWAS loci, prioritize causal variants, identify credible sets, or link GWAS signals to causal genes.

# GWAS Fine-Mapping & Causal Variant Prioritization

Identify and prioritize causal variants at GWAS loci using statistical fine-mapping and locus-to-gene predictions.

## Overview

Genome-wide association studies (GWAS) identify genomic regions associated with traits, but linkage disequilibrium (LD) makes it difficult to pinpoint the causal variant. **Fine-mapping** uses Bayesian statistical methods to compute the posterior probability that each variant is causal, given the GWAS summary statistics.

This skill provides tools to:
- **Prioritize causal variants** using fine-mapping posterior probabilities
- **Link variants to genes** using locus-to-gene (L2G) predictions
- **Annotate variants** with functional consequences
- **Suggest validation strategies** based on fine-mapping results

## Key Concepts

### Credible Sets
A **credible set** is a minimal set of variants that contains the causal variant with high confidence (typically 95% or 99%). Each variant in the set has a **posterior probability** of being causal, computed using methods like:
- **SuSiE** (Sum of Single Effects)
- **FINEMAP** (Bayesian fine-mapping)
- **PAINTOR** (Probabilistic Annotation INtegraTOR)

### Posterior Probability
The probability that a specific variant is causal, given the GWAS data and LD structure. Higher posterior probability = more likely to be causal.

### Locus-to-Gene (L2G) Predictions
L2G scores integrate multiple data types to predict which gene is affected by a variant:
- Distance to gene (closer = higher score)
- eQTL evidence (expression changes)
- Chromatin interactions (Hi-C, promoter capture)
- Functional annotations (coding variants, regulatory regions)

L2G scores range from 0 to 1, with higher scores indicating stronger gene-variant links.

## Use Cases

### 1. Prioritize Variants at a Known Locus
**Question**: "Which variant at the TCF7L2 locus is likely causal for type 2 diabetes?"

```python
from python_implementation import prioritize_causal_variants

# Prioritize variants in TCF7L2 for diabetes
result = prioritize_causal_variants("TCF7L2", "type 2 diabetes")
print(result.get_summary())

# Output shows:
# - Credible sets containing TCF7L2 variants
# - Posterior probabilities (via fine-mapping methods)
# - Top L2G genes (which genes are likely affected)
# - Associated traits
```

### 2. Fine-Map a Specific Variant
**Question**: "What do we know about rs429358 (APOE4) from fine-mapping?"

```python
# Fine-map a specific variant
result = prioritize_causal_variants("rs429358")

# Check which credible sets contain this variant
for cs in result.credible_sets:
    print(f"Trait: {cs.trait}")
    print(f"Fine-mapping method: {cs.finemapping_method}")
    print(f"Top gene: {cs.l2g_genes[0] if cs.l2g_genes else 'N/A'}")
    print(f"Confidence: {cs.confidence}")
```

### 3. Explore All Loci from a GWAS Study
**Question**: "What are all the causal loci from the recent T2D meta-analysis?"

```python
from python_implementation import get_credible_sets_for_study

# Get all fine-mapped loci from a study
credible_sets = get_credible_sets_for_study("GCST90029024")  # T2D GWAS

print(f"Found {len(credible_sets)} independent loci")

# Examine each locus
for cs in credible_sets:
    print(f"\nRegion: {cs.region}")
    print(f"Lead variant: {cs.lead_variant.rs_ids[0] if cs.lead_variant else 'N/A'}")

    if cs.l2g_genes:
        top_gene = cs.l2g_genes[0]
        print(f"Most likely causal gene: {top_gene.gene_symbol} (L2G: {top_gene.l2g_score:.3f})")
```

### 4. Find GWAS Studies for a Disease
**Question**: "What GWAS studies exist for Alzheimer's disease?"

```python
from python_implementation import search_gwas_studies_for_disease

# Search by disease name
studies = search_gwas_studies_for_disease("Alzheimer's disease")

for study in studies[:5]:
    print(f"{study['id']}: {study.get('nSamples', 'N/A')} samples")
    print(f"   Author: {study.get('publicationFirstAuthor', 'N/A')}")
    print(f"   Has summary stats: {study.get('hasSumstats', False)}")

# Or use precise disease ontology IDs
studies = search_gwas_studies_for_disease(
    "Alzheimer's disease",
    disease_id="EFO_0000249"  # EFO ID for Alzheimer's
)
```

### 5. Get Validation Suggestions
**Question**: "How should we validate the top causal variant?"

```python
result = prioritize_causal_variants("APOE", "alzheimer")

# Get experimental validation suggestions
suggestions = result.get_validation_suggestions()
for suggestion in suggestions:
    print(suggestion)

# Output includes:
# - CRISPR knock-in experiments
# - Reporter assays
# - eQTL analysis
# - Colocalization studies
```

## Workflow Example: Complete Fine-Mapping Analysis

```python
from python_implementation import (
    prioritize_causal_variants,
    search_gwas_studies_for_disease,
    get_credible_sets_for_study
)

# Step 1: Find relevant GWAS studies
print("Step 1: Finding T2D GWAS studies...")
studies = search_gwas_studies_for_disease("type 2 diabetes", "MONDO_0005148")
largest_study = max(studies, key=lambda s: s.get('nSamples', 0) or 0)
print(f"Largest study: {largest_study['id']} ({largest_study.get('nSamples', 'N/A')} samples)")

# Step 2: Get all fine-mapped loci from the study
print("\nStep 2: Getting fine-mapped loci...")
credible_sets = get_credible_sets_for_study(largest_study['id'], max_sets=100)
print(f"Found {len(credible_sets)} credible sets")

# Step 3: Find loci near genes of interest
print("\nStep 3: Finding TCF7L2 loci...")
tcf7l2_loci = [
    cs for cs in credible_sets
    if any(gene.gene_symbol == "TCF7L2" for gene in cs.l2g_genes)
]

print(f"TCF7L2 appears in {len(tcf7l2_loci)} loci")

# Step 4: Prioritize variants at TCF7L2
print("\nStep 4: Prioritizing TCF7L2 variants...")
result = prioritize_causal_variants("TCF7L2", "type 2 diabetes")

# Step 5: Print summary and validation plan
print("\n" + "="*60)
print("FINE-MAPPING SUMMARY")
print("="*60)
print(result.get_summary())

print("\n" + "="*60)
print("VALIDATION STRATEGY")
print("="*60)
suggestions = result.get_validation_suggestions()
for suggestion in suggestions:
    print(suggestion)
```

## Data Classes

### `FineMappingResult`
Main result object containing:
- `query_variant`: Variant annotation
- `query_gene`: Gene symbol (if queried by gene)
- `credible_sets`: List of fine-mapped loci
- `associated_traits`: All associated traits
- `top_causal_genes`: L2G genes ranked by score

Methods:
- `get_summary()`: Human-readable summary
- `get_validation_suggestions()`: Experimental validation strategies

### `CredibleSet`
Represents a fine-mapped locus:
- `study_locus_id`: Unique identifier
- `region`: Genomic region (e.g., "10:112861809-113404438")
- `lead_variant`: Top variant by posterior probability
- `finemapping_method`: Statistical method used (SuSiE, FINEMAP, etc.)
- `l2g_genes`: Locus-to-gene predictions
- `confidence`: Credible set confidence (95%, 99%)

### `L2GGene`
Locus-to-gene prediction:
- `gene_symbol`: Gene name (e.g., "TCF7L2")
- `gene_id`: Ensembl gene ID
- `l2g_score`: Probability score (0-1)

### `VariantAnnotation`
Functional annotation for a variant:
- `variant_id`: Open Targets format (chr_pos_ref_alt)
- `rs_ids`: dbSNP identifiers
- `chromosome`, `position`: Genomic coordinates
- `most_severe_consequence`: Functional impact
- `allele_frequencies`: Population-specific MAFs

## Tools Used

### Open Targets Genetics (GraphQL)
- `OpenTargets_get_variant_info`: Variant details and allele frequencies
- `OpenTargets_get_variant_credible_sets`: Credible sets containing a variant
- `OpenTargets_get_credible_set_detail`: Detailed credible set information
- `OpenTargets_get_study_credible_sets`: All loci from a GWAS study
- `OpenTargets_search_gwas_studies_by_disease`: Find studies by disease

### GWAS Catalog (REST API)
- `gwas_search_snps`: Find SNPs by gene or rsID
- `gwas_get_snp_by_id`: Detailed SNP information
- `gwas_get_associations_for_snp`: All trait associations for a variant
- `gwas_search_studies`: Find studies by disease/trait

## Understanding Fine-Mapping Output

### Interpreting Posterior Probabilities
- **> 0.5**: Very likely causal (strong candidate)
- **0.1 - 0.5**: Plausible causal variant
- **0.01 - 0.1**: Possible but uncertain
- **< 0.01**: Unlikely to be causal

### Interpreting L2G Scores
- **> 0.7**: High confidence gene-variant link
- **0.5 - 0.7**: Moderate confidence
- **0.3 - 0.5**: Weak but possible link
- **< 0.3**: Low confidence

### Fine-Mapping Methods Compared

| Method | Approach | Strengths | Use Case |
|--------|----------|-----------|----------|
| **SuSiE** | Sum of Single Effects | Handles multiple causal variants | Multi-signal loci |
| **FINEMAP** | Bayesian shotgun stochastic search | Fast, scalable | Large studies |
| **PAINTOR** | Functional annotations | Integrates epigenomics | Regulatory variants |
| **CAVIAR** | Colocalization | Finds shared causal variants | eQTL overlap |

## Common Questions

**Q: Why don't all variants have credible sets?**
A: Fine-mapping requires:
1. GWAS summary statistics (not just top hits)
2. LD reference panel
3. Sufficient signal strength (p < 5e-8)
4. Computational resources

**Q: Can a variant be in multiple credible sets?**
A: Yes! A variant can be causal for multiple traits (pleiotropy) or appear in different studies for the same trait.

**Q: What if the top L2G gene is far from the variant?**
A: This suggests regulatory effects (enhancers, promoters). Check:
- eQTL evidence in relevant tissues
- Chromatin interaction data (Hi-C)
- Regulatory element annotations (Roadmap, ENCODE)

**Q: How do I choose between variants in a credible set?**
A: Prioritize by:
1. Posterior probability (higher = better)
2. Functional consequence (coding > regulatory > intergenic)
3. eQTL evidence
4. Evolutionary conservation
5. Experimental feasibility

## Limitations

1. **LD-dependent**: Fine-mapping accuracy depends on LD structure matching the study population
2. **Requires summary stats**: Not all studies provide full summary statistics
3. **Computational intensive**: Fine-mapping large studies takes significant resources
4. **Prior assumptions**: Bayesian methods depend on priors (number of causal variants, effect sizes)
5. **Missing data**: Not all GWAS loci have been fine-mapped in Open Targets

## Best Practices

1. **Start with study-level queries** when exploring a new disease
2. **Check multiple studies** for replication of signals
3. **Combine with functional data** (eQTLs, chromatin, CRISPR screens)
4. **Consider ancestry** - LD differs across populations
5. **Validate experimentally** - fine-mapping provides candidates, not proof

## References

1. Wang et al. (2020) "A simple new approach to variable selection in regression, with application to genetic fine mapping." *JRSS-B* (SuSiE)
2. Benner et al. (2016) "FINEMAP: efficient variable selection using summary data from genome-wide association studies." *Bioinformatics*
3. Ghoussaini et al. (2021) "Open Targets Genetics: systematic identification of trait-associated genes using large-scale genetics and functional genomics." *NAR*
4. Mountjoy et al. (2021) "An open approach to systematically prioritize causal variants and genes at all published human GWAS trait-associated loci." *Nat Genet*

## Related Skills

- **tooluniverse-gwas-explorer**: Broader GWAS analysis
- **tooluniverse-eqtl-colocalization**: Link variants to gene expression
- **tooluniverse-gene-prioritization**: Systematic gene ranking
