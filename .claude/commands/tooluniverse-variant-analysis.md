# tooluniverse-variant-analysis

> Production-ready VCF processing, variant annotation, mutation analysis, and structural variant (SV/CNV) interpretation for bioinformatics questions. Parses VCF files (streaming, large files), classifies mutation types (missense, nonsense, synonymous, frameshift, splice, intronic, intergenic) and structural variants (deletions, duplications, inversions, translocations), applies VAF/depth/quality/consequence filters, annotates with ClinVar/dbSNP/gnomAD/CADD via ToolUniverse, interprets SV/CNV clinical significance using ClinGen dosage sensitivity scores, computes variant statistics, and generates reports. Solves questions like "What fraction of variants with VAF < 0.3 are missense?", "How many non-reference variants remain after filtering intronic/intergenic?", "What is the pathogenicity of this deletion affecting BRCA1?", or "Which dosage-sensitive genes overlap this CNV?". Use when processing VCF files, annotating variants, filtering by VAF/depth/consequence, classifying mutations, interpreting structural variants, assessing CNV pathogenicity, comparing cohorts, or answering variant analysis questions.

# Variant Analysis and Annotation

Production-ready VCF processing and variant annotation skill combining local bioinformatics computation with ToolUniverse database integration. Designed to answer bioinformatics analysis questions about VCF data, mutation classification, variant filtering, and clinical annotation.

## When to Use This Skill

**Triggers**:
- User provides a VCF file (SNV/indel or SV) and asks questions about its contents
- Questions about variant allele frequency (VAF) filtering
- Mutation type classification queries (missense, nonsense, synonymous, etc.)
- Structural variant interpretation requests (deletions, duplications, CNVs)
- Variant annotation requests (ClinVar, gnomAD, CADD, dbSNP)
- CNV pathogenicity assessment using ClinGen dosage sensitivity
- Cohort comparison questions
- Population frequency filtering (SNVs or SVs)
- Intronic/intergenic variant filtering
- Gene dosage sensitivity queries

**Example Questions**:
- "What fraction of variants with VAF < 0.3 are annotated as missense mutations?"
- "After filtering intronic/intergenic variants, how many non-reference variants remain?"
- "What is the clinical significance of this deletion affecting BRCA1?"
- "Which dosage-sensitive genes overlap this 500kb duplication on chr17?"
- "How many variants have clinical significance annotations?"
- "Compare variant counts between samples"

---

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| **VCF Parsing** | Pure Python + cyvcf2 parsers. VCF 4.x, gzipped, multi-sample, SNV/indel/SV |
| **Mutation Classification** | Maps SO terms, SnpEff ANN, VEP CSQ, GATK Funcotator to standard types |
| **VAF Extraction** | Handles AF, AD, AO/RO, NR/NV, INFO AF formats |
| **Filtering** | VAF, depth, quality, PASS, variant type, mutation type, consequence, chromosome, SV size |
| **Statistics** | Ti/Tv ratio, per-sample VAF/depth stats, mutation type distribution, SV size distribution |
| **Annotation** | MyVariant.info (aggregates ClinVar, dbSNP, gnomAD, CADD, SIFT, PolyPhen) |
| **SV/CNV Analysis** | gnomAD SV population frequencies, DGVa/dbVar known SVs, ClinGen dosage sensitivity |
| **Clinical Interpretation** | ACMG/ClinGen CNV pathogenicity classification using haploinsufficiency/triplosensitivity scores |
| **DataFrame** | Convert to pandas for advanced analytics |
| **Reporting** | Markdown reports with tables and statistics, SV clinical reports |

---

## Workflow Overview

```
Input VCF File (SNVs/indels or SVs)
    |
    v
Phase 1: Parse VCF
    |-- Pure Python parser (any VCF 4.x)
    |-- cyvcf2 parser (faster, C-based)
    |-- Extract: CHROM, POS, REF, ALT, QUAL, FILTER, INFO, FORMAT, samples
    |-- Extract per-sample: GT, VAF, depth
    |-- Extract annotations from INFO (ANN, CSQ, FUNCOTATION)
    |-- Detect variant class: SNV/indel vs SV/CNV
    |
    v
Phase 2: Classify Variants
    |-- Variant type: SNV, INS, DEL, MNV, COMPLEX, SV
    |-- Mutation type: missense, nonsense, synonymous, frameshift, splice, etc.
    |-- Impact: HIGH, MODERATE, LOW, MODIFIER
    |-- SV type: DEL, DUP, INV, BND, CNV (if structural variant)
    |
    v
Phase 3: Apply Filters
    |-- VAF range (min/max)
    |-- Read depth minimum
    |-- Quality threshold
    |-- PASS only
    |-- Variant/mutation type inclusion/exclusion
    |-- Consequence exclusion (intronic, intergenic)
    |-- Population frequency range
    |-- Chromosome selection
    |-- SV size range (for structural variants)
    |
    v
Phase 4: Compute Statistics
    |-- Variant type distribution
    |-- Mutation type distribution
    |-- Impact distribution
    |-- Chromosome distribution
    |-- Ti/Tv ratio (for SNVs)
    |-- Per-sample VAF/depth stats
    |-- Gene mutation counts
    |-- SV size distribution (for structural variants)
    |
    v
Phase 5: Annotate with ToolUniverse (optional)
    |-- MyVariant.info: ClinVar, dbSNP, gnomAD, CADD, SIFT, PolyPhen
    |-- dbSNP: Population frequencies, gene associations
    |-- gnomAD: Population allele frequencies
    |-- Ensembl VEP: Consequence prediction
    |
    v
Phase 6: Generate Report / Answer Question
    |-- Markdown report with tables
    |-- Direct answer to specific question
    |-- DataFrame for downstream analysis
    |
    v
Phase 7: Structural Variant & CNV Analysis (if SV/CNV detected)
    |-- Annotate with gnomAD SV population frequencies
    |-- Query DGVa/dbVar for known SVs (Ensembl)
    |-- Identify affected genes
    |-- Query ClinGen dosage sensitivity (HI/TS scores)
    |-- Classify pathogenicity (Pathogenic/Likely Pathogenic/VUS/Benign)
    |-- Generate SV clinical report with ACMG/ClinGen guidelines
```

---

## Phase Summaries

### Phase 1: VCF Parsing

**Use pandas for**:
- Reading VCF as structured data
- Quick exploratory analysis
- When you need to manipulate columns and rows

**Use python_implementation tools for**:
- Production parsing with annotation extraction
- Multi-sample VCF handling
- VAF extraction from FORMAT fields
- Large file streaming

**Key functions**:
```python
vcf_data = parse_vcf("input.vcf")           # Pure Python (always works)
vcf_data = parse_vcf_cyvcf2("input.vcf")    # Fast C-based (if installed)
df = variants_to_dataframe(vcf_data.variants, sample="TUMOR")  # For pandas
```

### Phase 2: Variant Classification

**Automatic classification from annotations**:
- SnpEff ANN field
- VEP CSQ field
- GATK Funcotator FUNCOTATION field
- Standard INFO keys: EFFECT, EFF, TYPE

**Mutation types supported**: missense, nonsense, synonymous, frameshift, splice_site, splice_region, inframe_insertion, inframe_deletion, intronic, intergenic, UTR_5, UTR_3, upstream, downstream, stop_lost, start_lost

**See references/mutation_classification_guide.md for full details**

### Phase 3: Filtering

**Common filtering patterns**:
```python
# Somatic-like variants
criteria = FilterCriteria(
    min_vaf=0.05, max_vaf=0.95,
    min_depth=20, pass_only=True,
    exclude_consequences=["intronic", "intergenic", "upstream", "downstream"]
)

# High-confidence germline
criteria = FilterCriteria(
    min_vaf=0.25, min_depth=30, pass_only=True,
    chromosomes=["1", "2", ..., "22", "X", "Y"]
)

# Rare pathogenic candidates
criteria = FilterCriteria(
    min_depth=20, pass_only=True,
    mutation_types=["missense", "nonsense", "frameshift"]
)
```

**See references/vcf_filtering.md for all filter options**

### Phase 4: Statistics

**Use pandas for**:
- Complex aggregations (groupby, pivot tables)
- Custom statistical tests
- Data exploration

**Use python_implementation for**:
- Standard variant statistics (Ti/Tv, type distribution)
- Per-sample VAF/depth summary
- Quick mutation type counts

### Phase 5: ToolUniverse Annotation

**When to use ToolUniverse annotation tools**:
1. **ClinVar clinical significance**: Use MyVariant.info or dbSNP tools
2. **Population frequencies**: Use MyVariant.info (aggregates gnomAD, ExAC, 1000G)
3. **Pathogenicity scores**: Use MyVariant.info (aggregates CADD, SIFT, PolyPhen)
4. **Consequence prediction**: Use Ensembl VEP tools

**Best practices**:
- Annotate variants with rsIDs first (most reliable)
- Use MyVariant.info for batch annotation (aggregates multiple sources)
- Limit to top variants (max_annotate=50-100) to respect rate limits
- Query dbSNP/gnomAD directly for specific use cases

**Key tools**:
- `MyVariant_query_variants`: Batch annotation (ClinVar, dbSNP, gnomAD, CADD)
- `dbsnp_get_variant_by_rsid`: Population frequencies
- `gnomad_get_variant`: Basic variant metadata
- `EnsemblVEP_annotate_rsid`: Consequence prediction

**See references/annotation_guide.md for detailed examples**

### Phase 6: Report Generation

**Report includes**:
1. Summary Statistics (total variants, type counts, Ti/Tv)
2. Mutation Type Distribution (table with counts and percentages)
3. Impact Distribution
4. Chromosome Distribution
5. VAF Distribution (per-sample)
6. Clinical Significance
7. Top Mutated Genes
8. Variant Annotations (ClinVar-annotated variants)

### Phase 7: Structural Variant & CNV Analysis

**When VCF contains SV calls** (SVTYPE=DEL/DUP/INV/BND):

1. **Identify affected genes** (from VCF annotation or coordinate overlap)
2. **Query ClinGen dosage sensitivity**:
   ```python
   clingen = ClinGen_dosage_by_gene(gene_symbol="BRCA1")
   # Returns: haploinsufficiency_score, triplosensitivity_score
   ```
3. **Check population frequency**:
   ```python
   gnomad_sv = gnomad_get_sv_by_gene(gene_symbol="BRCA1")
   # Returns: SVs with AF, AC, AN
   ```
4. **Classify pathogenicity**:
   - Pathogenic: Deletion + HI score = 3, AF < 0.0001
   - Likely Pathogenic: Deletion + HI score = 2, AF < 0.001
   - VUS: HI/TS score = 0-1, AF 0.001-0.01
   - Benign: AF > 0.01

**ClinGen dosage score interpretation**:
- **3**: Sufficient evidence for dosage pathogenicity (HIGH impact)
- **2**: Some evidence (MODERATE impact)
- **1**: Little evidence (LOW impact)
- **0**: No evidence (MINIMAL impact)
- **40**: Dosage sensitivity unlikely

**See references/sv_cnv_analysis.md for full SV workflow**

---

## Answering BixBench Questions

### Pattern 1: VAF + Mutation Type Fraction

**Question**: "What fraction of variants with VAF < X are annotated as Y mutations?"

```python
result = answer_vaf_mutation_fraction(
    vcf_path="input.vcf",
    max_vaf=0.3,
    mutation_type="missense",
    sample="TUMOR"
)
# Returns: fraction, total_below_vaf, matching_mutation_type
```

### Pattern 2: Cohort Comparison

**Question**: "What is the difference in mutation frequency between cohorts?"

```python
result = answer_cohort_comparison(
    vcf_paths=["cohort1.vcf", "cohort2.vcf"],
    mutation_type="missense",
    cohort_names=["Treatment", "Control"]
)
# Returns: cohorts, frequency_difference
```

### Pattern 3: Filter and Count

**Question**: "After filtering X, how many Y remain?"

```python
result = answer_non_reference_after_filter(
    vcf_path="input.vcf",
    exclude_intronic_intergenic=True
)
# Returns: total_input, non_reference, remaining
```

---

## ToolUniverse Tools Reference

### SNV/Indel Annotation

| Tool | When to Use | Parameters | Response |
|------|------------|------------|----------|
| `MyVariant_query_variants` | Batch annotation | `query` (rsID/HGVS) | ClinVar, dbSNP, gnomAD, CADD |
| `dbsnp_get_variant_by_rsid` | Population frequencies | `rsid` | Frequencies, clinical significance |
| `gnomad_get_variant` | gnomAD metadata | `variant_id` (CHR-POS-REF-ALT) | Basic variant info |
| `EnsemblVEP_annotate_rsid` | Consequence prediction | `variant_id` (rsID) | Transcript impact |

### Structural Variant Annotation

| Tool | When to Use | Parameters | Response |
|------|------------|------------|----------|
| `gnomad_get_sv_by_gene` | SV population frequency | `gene_symbol` | SVs with AF, AC, AN |
| `gnomad_get_sv_by_region` | Regional SV search | `chrom`, `start`, `end` | SVs in region |
| `ClinGen_dosage_by_gene` | Dosage sensitivity | `gene_symbol` | HI/TS scores, disease |
| `ClinGen_dosage_region_search` | Dosage-sensitive genes in region | `chromosome`, `start`, `end` | All genes with HI/TS scores |
| `ensembl_get_structural_variants` | Known SVs from DGVa/dbVar | `chrom`, `start`, `end`, `species` | Clinical significance |

**See references/annotation_guide.md for detailed tool usage examples**

---

## Common Use Patterns

### Pattern 1: Quick VCF Summary
Parse VCF, compute statistics, generate report.

```python
report = variant_analysis_pipeline("input.vcf", output_file="report.md")
```

### Pattern 2: Filtered Analysis
Parse VCF, apply multi-criteria filter, compute statistics on filtered set.

```python
report = variant_analysis_pipeline(
    vcf_path="input.vcf",
    filters=FilterCriteria(min_vaf=0.1, min_depth=20, pass_only=True),
    output_file="filtered_report.md"
)
```

### Pattern 3: Annotated Report
Parse VCF, annotate top variants with ClinVar/gnomAD/CADD, generate clinical report.

```python
report = variant_analysis_pipeline(
    vcf_path="input.vcf",
    annotate=True,
    max_annotate=50,
    output_file="annotated_report.md"
)
```

### Pattern 4: BixBench Question Answering
Parse VCF, apply specific filters, compute targeted statistics to answer precise questions.

```python
result = answer_vaf_mutation_fraction(
    vcf_path="input.vcf",
    max_vaf=0.3,
    mutation_type="missense"
)
```

### Pattern 5: Cohort Comparison
Parse multiple VCFs, compare mutation frequencies across cohorts.

```python
result = answer_cohort_comparison(
    vcf_paths=["cohort1.vcf", "cohort2.vcf"],
    mutation_type="missense"
)
```

---

## When to Use pandas vs python_implementation

**Use pandas when**:
- You need to read VCF as a flat table
- You want to do custom aggregations (groupby, pivot)
- You need to join with other data
- You're doing exploratory data analysis
- You want to export to CSV/Excel

**Use python_implementation when**:
- You need production-grade VCF parsing
- You need to extract INFO annotations (ANN, CSQ)
- You need per-sample VAF/depth extraction
- You need to classify mutation types
- You need standard variant statistics (Ti/Tv)
- You need to integrate with ToolUniverse annotation

**Best approach**: Use python_implementation for parsing/classification, then convert to DataFrame for custom analysis:

```python
# Parse and classify
vcf_data = parse_vcf("input.vcf")
passing, failing = filter_variants(vcf_data.variants, criteria)

# Convert to DataFrame for custom analysis
df = variants_to_dataframe(passing, sample="TUMOR")

# Now use pandas
missense_high_vaf = df[(df['mutation_type'] == 'missense') & (df['vaf'] >= 0.3)]
```

---

## Limitations

- **VCF annotation required for mutation classification**: If VCF has no ANN/CSQ/FUNCOTATION in INFO, mutation types will be "unknown" until ToolUniverse annotation is applied
- **Multi-allelic variants**: Parser takes first ALT allele for type classification
- **ToolUniverse annotation rate**: API-based, limited to ~100 variants per batch by default to respect rate limits
- **gnomAD tool**: Returns basic metadata only (not full allele frequencies); use MyVariant.info for gnomAD AF
- **Large VCFs**: Pure Python parser streams line-by-line; cyvcf2 is recommended for files with >100K variants

---

## Reference Documentation

- **references/vcf_filtering.md**: Complete filter options and examples
- **references/mutation_classification_guide.md**: Detailed mutation type classification rules
- **references/annotation_guide.md**: ToolUniverse annotation workflows with examples
- **references/sv_cnv_analysis.md**: Complete SV/CNV interpretation workflow

---

## Utility Scripts

- **scripts/parse_vcf.py**: Standalone VCF parsing script
- **scripts/filter_variants.py**: Command-line variant filtering
- **scripts/annotate_variants.py**: Batch variant annotation

---

## Quick Start

See QUICK_START.md for:
- Python SDK examples (pipeline, question functions, individual tools)
- MCP conversational examples
- Common recipes (somatic analysis, clinical screening, population frequency)
- Expected output formats
- Troubleshooting guide
