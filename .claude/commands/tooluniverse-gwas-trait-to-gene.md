# tooluniverse-gwas-trait-to-gene

> Discover genes associated with diseases and traits using GWAS data from the GWAS Catalog (500,000+ associations) and Open Targets Genetics (L2G predictions). Identifies genetic risk factors, prioritizes causal genes via locus-to-gene scoring, and assesses druggability. Use when asked to find genes associated with a disease or trait, discover genetic risk factors, translate GWAS signals to gene targets, or answer questions like "What genes are associated with type 2 diabetes?"

# GWAS Trait-to-Gene Discovery

**Discover genes associated with diseases and traits using genome-wide association studies (GWAS)**

## Overview

This skill enables systematic discovery of genes linked to diseases/traits by analyzing GWAS data from two major resources:
- **GWAS Catalog** (EBI/NHGRI): Curated catalog of published GWAS with >500,000 associations
- **Open Targets Genetics**: Fine-mapped GWAS signals with locus-to-gene (L2G) predictions

## Use Cases

**Clinical Research**
- "What genes are associated with type 2 diabetes?"
- "Find genetic risk factors for coronary artery disease"
- "Which genes contribute to Alzheimer's disease susceptibility?"

**Drug Target Discovery**
- Identify genes with strong genetic evidence for disease causation
- Prioritize targets based on L2G scores and replication across studies
- Find genes with genome-wide significant associations (p < 5e-8)

**Functional Genomics**
- Map disease-associated variants to candidate genes
- Analyze genetic architecture of complex traits
- Understand polygenic disease mechanisms

## Workflow

```
1. Trait Search → Search GWAS Catalog by disease/trait name
       ↓
2. SNP Aggregation → Collect genome-wide significant SNPs (p < 5e-8)
       ↓
3. Gene Mapping → Extract mapped genes from associations
       ↓
4. Evidence Ranking → Score by p-value, replication, fine-mapping
       ↓
5. Annotation (Optional) → Add L2G predictions from Open Targets
```

## Key Concepts

**Genome-wide Significance**
- Standard threshold: p < 5×10⁻⁸
- Accounts for multiple testing burden across ~1M common variants
- Higher confidence: p < 5×10⁻¹⁰ or replicated across studies

**Gene Mapping Methods**
- **Positional**: Nearest gene to lead SNP
- **Fine-mapping**: Statistical refinement to credible variants
- **Locus-to-Gene (L2G)**: Integrative score combining multiple evidence types

**Evidence Confidence Levels**
- **High**: L2G score > 0.5 OR multiple studies with p < 5e-10
- **Medium**: 2+ studies with p < 5e-8
- **Low**: Single study or marginal significance

## Required ToolUniverse Tools

### GWAS Catalog (11 tools)
- `gwas_get_associations_for_trait` - Get all associations for a trait (sorted by p-value)
- `gwas_search_snps` - Search SNPs by gene mapping
- `gwas_get_snp_by_id` - Get SNP details (MAF, consequence, location)
- `gwas_get_study_by_id` - Get study metadata
- `gwas_search_associations` - Search associations with filters
- `gwas_search_studies` - Search studies by trait/cohort
- `gwas_get_associations_for_snp` - Get all associations for a SNP
- `gwas_get_variants_for_trait` - Get variants for a trait
- `gwas_get_studies_for_trait` - Get studies for a trait
- `gwas_get_snps_for_gene` - Get SNPs mapped to a gene
- `gwas_get_associations_for_study` - Get associations from a study

### Open Targets Genetics (6 tools)
- `OpenTargets_search_gwas_studies_by_disease` - Search studies by disease ontology
- `OpenTargets_get_study_credible_sets` - Get fine-mapped loci for a study
- `OpenTargets_get_variant_credible_sets` - Get credible sets for a variant
- `OpenTargets_get_variant_info` - Get variant annotation (frequencies, consequences)
- `OpenTargets_get_gwas_study` - Get study metadata
- `OpenTargets_get_credible_set_detail` - Get detailed credible set information

## Parameters

**Required**
- `trait` - Disease/trait name (e.g., "type 2 diabetes", "coronary artery disease")

**Optional**
- `p_value_threshold` - Significance threshold (default: 5e-8)
- `min_evidence_count` - Minimum number of studies (default: 1)
- `max_results` - Maximum genes to return (default: 100)
- `use_fine_mapping` - Include L2G predictions (default: true)
- `disease_ontology_id` - Disease ontology ID for Open Targets (e.g., "MONDO_0005148")

## Output Schema

```python
{
  "genes": [
    {
      "symbol": str,              # Gene symbol (e.g., "TCF7L2")
      "min_p_value": float,       # Most significant p-value
      "evidence_count": int,      # Number of independent studies
      "snps": [str],              # Associated SNP rs IDs
      "studies": [str],           # GWAS study accessions
      "l2g_score": float | null,  # Locus-to-gene score (0-1)
      "credible_sets": int,       # Number of credible sets
      "confidence_level": str     # "High", "Medium", or "Low"
    }
  ],
  "summary": {
    "trait": str,
    "total_associations": int,
    "significant_genes": int,
    "data_sources": ["GWAS Catalog", "Open Targets"]
  }
}
```

## Example Results

**Type 2 Diabetes**
```
TCF7L2:  p=1.2e-98, 15 studies, L2G=0.82 → High confidence
KCNJ11:  p=3.4e-67, 12 studies, L2G=0.76 → High confidence
PPARG:   p=2.1e-45, 8 studies,  L2G=0.71 → High confidence
FTO:     p=5.6e-42, 10 studies, L2G=0.68 → High confidence
IRS1:    p=8.9e-38, 6 studies,  L2G=0.54 → High confidence
```

**Alzheimer's Disease**
```
APOE:    p=1.0e-450, 25 studies, L2G=0.95 → High confidence
BIN1:    p=2.3e-89,  18 studies, L2G=0.88 → High confidence
CLU:     p=4.5e-67,  16 studies, L2G=0.82 → High confidence
ABCA7:   p=6.7e-54,  14 studies, L2G=0.79 → High confidence
CR1:     p=8.9e-52,  13 studies, L2G=0.75 → High confidence
```

## Best Practices

**1. Use Disease Ontology IDs for Precision**
```
# Instead of:
discover_gwas_genes("diabetes")  # Ambiguous

# Use:
discover_gwas_genes(
    "type 2 diabetes",
    disease_ontology_id="MONDO_0005148"  # Specific
)
```

**2. Filter by Evidence Strength**
```
# For drug targets, require strong evidence:
discover_gwas_genes(
    "coronary artery disease",
    p_value_threshold=5e-10,    # Stricter than GWAS threshold
    min_evidence_count=3,       # Multiple independent studies
    use_fine_mapping=True       # Include L2G predictions
)
```

**3. Interpret Results Carefully**
- **Association ≠ Causation**: GWAS identifies correlated variants, not necessarily causal genes
- **Linkage Disequilibrium**: Lead SNP may tag the true causal variant in a nearby gene
- **Fine-mapping**: L2G scores provide better causal gene evidence than positional mapping
- **Functional Evidence**: Validate with orthogonal data (eQTLs, knockout models, etc.)

## Limitations

1. **Gene Mapping Uncertainty**
   - Positional mapping assigns SNPs to nearest gene (may be incorrect)
   - Fine-mapping available for only a subset of studies
   - Intergenic variants difficult to map

2. **Population Bias**
   - Most GWAS in European populations
   - Effect sizes may differ across ancestries
   - Rare variants often under-represented

3. **Sample Size Dependence**
   - Larger studies detect more associations
   - Older small studies may have false negatives
   - p-values alone don't indicate effect size

4. **Validation Bug**
   - Some ToolUniverse tools have oneOf validation issues
   - Use `validate=False` parameter if needed
   - This is automatically handled in the Python implementation

## Related Skills

- **Variant-to-Disease Association**: Look up specific SNPs (e.g., rs7903146 → T2D)
- **Gene-to-Disease Links**: Find diseases associated with known genes
- **Drug Target Prioritization**: Rank targets by genetic evidence
- **Population Genetics Analysis**: Compare allele frequencies across populations

## Data Sources

**GWAS Catalog**
- Curator: EBI and NHGRI
- URL: https://www.ebi.ac.uk/gwas/
- Coverage: 100,000+ publications, 500,000+ associations
- Update Frequency: Weekly

**Open Targets Genetics**
- Curator: Open Targets consortium
- URL: https://genetics.opentargets.org/
- Coverage: Fine-mapped GWAS, L2G predictions, QTL colocalization
- Update Frequency: Quarterly

## Citation

If you use this skill in research, please cite:

```
Buniello A, et al. (2019) The NHGRI-EBI GWAS Catalog of published genome-wide
association studies. Nucleic Acids Research, 47(D1):D1005-D1012.

Mountjoy E, et al. (2021) An open approach to systematically prioritize causal
variants and genes at all published human GWAS trait-associated loci.
Nature Genetics, 53:1527-1533.
```

## Support

For issues with:
- **Skill functionality**: Open issue at tooluniverse/skills
- **GWAS data**: Contact GWAS Catalog or Open Targets support
- **Tool errors**: Check ToolUniverse tool status
