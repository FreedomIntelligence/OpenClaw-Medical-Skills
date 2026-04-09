# tooluniverse-structural-variant-analysis

> Comprehensive structural variant (SV) analysis skill for clinical genomics. Classifies SVs (deletions, duplications, inversions, translocations), assesses pathogenicity using ACMG-adapted criteria, evaluates gene disruption and dosage sensitivity, and provides clinical interpretation with evidence grading. Use when analyzing CNVs, large deletions/duplications, chromosomal rearrangements, or any structural variants requiring clinical interpretation.

# Structural Variant Analysis Workflow

Systematic analysis of structural variants (deletions, duplications, inversions, translocations, complex rearrangements) for clinical genomics interpretation using ACMG-adapted criteria.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create SV_analysis_report.md FIRST, then populate progressively
2. **ACMG-style classification** - Pathogenic/Likely Pathogenic/VUS/Likely Benign/Benign with explicit evidence
3. **Evidence grading** - Grade all findings by confidence level (★★★/★★☆/★☆☆)
4. **Dosage sensitivity critical** - Gene dosage effects drive SV pathogenicity
5. **Breakpoint precision matters** - Exact gene disruption vs dosage-only effects
6. **Population context essential** - gnomAD SVs for frequency assessment
7. **English-first queries** - Always use English terms in tool calls (gene names, disease names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## Problem This Skill Solves

Structural variants (SVs) present unique interpretation challenges:

1. **Complex molecular consequences** - SVs can cause gene dosage changes, gene disruption, gene fusions, position effects
2. **Size matters** - Pathogenicity depends on size, gene content, and breakpoint precision
3. **Limited databases** - Fewer curated SVs in ClinVar compared to SNVs
4. **Dosage sensitivity** - Haploinsufficiency and triplosensitivity are critical but gene-specific
5. **Population frequency** - Large benign CNVs are common; distinguishing pathogenic from benign is challenging

**This skill provides**: A systematic workflow integrating SV classification, gene content analysis, dosage sensitivity assessment, population frequencies, and ACMG-adapted criteria into clinically actionable interpretations.

---

## Triggers

Use this skill when users:
- Ask about structural variant interpretation
- Have CNV data from array or sequencing
- Ask "is this deletion/duplication pathogenic?"
- Need ACMG classification for SVs
- Want to assess gene dosage effects
- Ask about chromosomal rearrangements
- Have large-scale genomic alterations requiring interpretation

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              STRUCTURAL VARIANT INTERPRETATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: SV IDENTITY & CLASSIFICATION                          │
│  ├── Normalize SV coordinates (hg19/hg38)                       │
│  ├── Determine SV type (DEL/DUP/INV/TRA/CPX)                   │
│  ├── Calculate SV size                                          │
│  └── Assess breakpoint precision                                │
│                                                                  │
│  Phase 2: GENE CONTENT ANALYSIS                                  │
│  ├── Identify genes fully contained in SV                       │
│  ├── Identify genes with breakpoints (disrupted)                │
│  ├── Annotate gene function and disease associations            │
│  ├── Identify regulatory elements affected                      │
│  └── Assess gene orientation (for inversions/translocations)    │
│                                                                  │
│  Phase 3: DOSAGE SENSITIVITY ASSESSMENT                          │
│  ├── ClinGen dosage sensitivity scores                          │
│  │   └─ Haploinsufficiency / Triplosensitivity ratings          │
│  ├── DECIPHER haploinsufficiency predictions                    │
│  ├── pLI scores (gnomAD) for loss-of-function intolerance       │
│  ├── OMIM gene-disease associations (dominant/recessive)        │
│  └── Known dosage-sensitive genes from literature               │
│                                                                  │
│  Phase 4: POPULATION FREQUENCY CONTEXT                           │
│  ├── gnomAD SV database (overlapping SVs)                       │
│  ├── DGV (Database of Genomic Variants)                         │
│  ├── ClinVar (known pathogenic/benign SVs)                      │
│  └── Calculate reciprocal overlap with population SVs           │
│                                                                  │
│  Phase 5: PATHOGENICITY SCORING                                  │
│  ├── Pathogenicity score (0-10 scale)                           │
│  │   ├─ Gene content weight (40%)                               │
│  │   ├─ Dosage sensitivity weight (30%)                         │
│  │   ├─ Population frequency weight (20%)                       │
│  │   └─ Inheritance/phenotype match weight (10%)                │
│  ├── Apply ACMG SV criteria                                     │
│  └── Generate classification recommendation                      │
│                                                                  │
│  Phase 6: LITERATURE & CLINICAL EVIDENCE                         │
│  ├── PubMed: Similar SVs, gene disruption studies               │
│  ├── DECIPHER: Developmental disorder cases                     │
│  ├── Clinical case reports                                      │
│  └── Functional evidence for gene dosage effects                │
│                                                                  │
│  Phase 7: ACMG-ADAPTED CLASSIFICATION                            │
│  ├── Apply SV-specific evidence codes                           │
│  ├── Calculate final classification                             │
│  ├── Identify limiting factors                                  │
│  └── Generate clinical recommendations                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Details

### Phase 1: SV Identity & Classification

**Goal**: Standardize SV notation and classify type

**SV Types**:
| Type | Abbreviation | Description | Molecular Effect |
|------|--------------|-------------|------------------|
| **Deletion** | DEL | Loss of genomic segment | Haploinsufficiency, gene disruption |
| **Duplication** | DUP | Gain of genomic segment | Triplosensitivity, gene dosage imbalance |
| **Inversion** | INV | Segment flipped in orientation | Gene disruption at breakpoints, position effects |
| **Translocation** | TRA | Segment moved to different chromosome | Gene fusions, disruption, position effects |
| **Complex** | CPX | Multiple rearrangement types | Variable effects |

**Key Information to Capture**:
- Chromosome(s) involved
- Coordinates (start, end) in hg19/hg38
- SV size (bp or Mb)
- SV type (DEL/DUP/INV/TRA/CPX)
- Breakpoint precision (±50bp, ±1kb, etc.)
- Inheritance pattern (de novo, inherited, unknown)

**Example**:
```
SV: arr[GRCh38] 17q21.31(44039927-44352659)x1
- Type: Deletion (heterozygous)
- Size: 313 kb
- Genes: MAPT, KANSL1 (fully contained)
- Breakpoints: Well-defined (array resolution ±5kb)
```

---

### Phase 2: Gene Content Analysis

**Goal**: Comprehensive annotation of genes affected by SV

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `Ensembl_lookup_gene` | Gene structure, coordinates | Gene boundaries, exons, transcripts |
| `NCBI_gene_search` | Gene information | Official symbol, aliases, description |
| `Gene_Ontology_get_term_info` | Gene function | Biological process, molecular function |
| `OMIM_search`, `OMIM_get_entry` | Disease associations | Inheritance, clinical features |
| `DisGeNET_search_gene` | Gene-disease associations | Evidence scores |

**Gene Categories**:

1. **Fully contained genes** - Entire gene within SV boundaries
   - Deletion: Complete loss of one copy (haploinsufficiency)
   - Duplication: Extra copy (triplosensitivity)

2. **Partially disrupted genes** - Breakpoint within gene
   - Likely loss-of-function for affected allele
   - Check if critical domains disrupted

3. **Flanking genes** - Within 1 Mb of breakpoints
   - May be affected by position effects
   - Regulatory disruption possible

**Example Gene Content Analysis**:

```python
def analyze_gene_content(tu, chrom, sv_start, sv_end, sv_type):
    """
    Identify and annotate all genes within SV region.
    """
    genes = {
        'fully_contained': [],
        'partially_disrupted': [],
        'flanking': []
    }

    # Use Ensembl to find overlapping genes
    # This is pseudocode - actual implementation depends on available tools

    for gene in genes_in_region:
        gene_start = gene['start']
        gene_end = gene['end']

        # Classify gene relationship to SV
        if gene_start >= sv_start and gene_end <= sv_end:
            # Fully contained
            gene_info = annotate_gene(tu, gene['symbol'])
            genes['fully_contained'].append(gene_info)

        elif (gene_start < sv_start < gene_end) or (gene_start < sv_end < gene_end):
            # Partially disrupted
            gene_info = annotate_gene(tu, gene['symbol'])
            genes['partially_disrupted'].append(gene_info)

        elif abs(gene_start - sv_end) < 1000000 or abs(gene_end - sv_start) < 1000000:
            # Flanking (within 1 Mb)
            gene_info = annotate_gene(tu, gene['symbol'])
            genes['flanking'].append(gene_info)

    return genes

def annotate_gene(tu, gene_symbol):
    """
    Comprehensive gene annotation.
    """
    # OMIM associations
    omim = tu.tools.OMIM_search(
        operation="search",
        query=gene_symbol,
        limit=5
    )

    # DisGeNET associations
    disgenet = tu.tools.DisGeNET_search_gene(
        operation="search_gene",
        gene=gene_symbol,
        limit=10
    )

    # Gene Ontology
    # Note: Need gene ID first
    ncbi = tu.tools.NCBI_gene_search(
        term=gene_symbol,
        organism="human"
    )

    return {
        'symbol': gene_symbol,
        'omim': omim,
        'disgenet': disgenet,
        'ncbi': ncbi
    }
```

**Report Section**:
```markdown
### 2.1 Fully Contained Genes (Complete Dosage Effect)

| Gene | Function | Disease Association | Inheritance | Evidence |
|------|----------|---------------------|-------------|----------|
| **MAPT** | Microtubule-associated protein tau | Frontotemporal dementia (AD) | Autosomal Dominant | ★★★ |
| **KANSL1** | Histone acetyltransferase complex | Koolen-De Vries syndrome (AD) | Autosomal Dominant | ★★★ |

**Interpretation**: Deletion results in haploinsufficiency of two dosage-sensitive genes. KANSL1 haploinsufficiency is the primary cause of pathogenicity.

*Sources: OMIM, DisGeNET, Ensembl*

### 2.2 Partially Disrupted Genes (Breakpoint Within Gene)

| Gene | Breakpoint Location | Effect | Critical Domains Lost |
|------|-------------------|--------|----------------------|
| **NF1** | Intron 28 of 58 | 5' portion deleted | Yes - GTPase-activating domain |

**Interpretation**: Breakpoint disrupts NF1 coding sequence, likely resulting in loss-of-function. NF1 is haploinsufficient (causes neurofibromatosis type 1).

### 2.3 Flanking Genes (Potential Position Effects)

| Gene | Distance from SV | Regulatory Risk | Evidence |
|------|------------------|-----------------|----------|
| **KCNJ2** | 450 kb upstream | Low | ★☆☆ |

**Note**: Position effects are possible but less common. Consider if phenotype unexplained by contained genes.
```

---

### Phase 3: Dosage Sensitivity Assessment

**Goal**: Determine if affected genes are dosage-sensitive

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `ClinGen_search_dosage_sensitivity` | Gold standard curation | HI/TS scores (0-3) |
| `ClinGen_search_gene_validity` | Gene-disease validity | Definitive/Strong/Moderate |
| `gnomad_search` (pLI) | Loss-of-function intolerance | pLI score (0-1) |
| `DECIPHER_search` | Developmental disorders | Patient phenotypes with similar SVs |
| `OMIM_get_entry` | Inheritance pattern | AD/AR indicates dosage sensitivity |

**ClinGen Dosage Sensitivity Scores**:

| Score | Haploinsufficiency (HI) | Triplosensitivity (TS) | Interpretation |
|-------|------------------------|------------------------|----------------|
| **3** | Sufficient evidence | Sufficient evidence | Gene IS dosage-sensitive |
| **2** | Emerging evidence | Emerging evidence | Likely dosage-sensitive |
| **1** | Little evidence | Little evidence | Insufficient evidence |
| **0** | No evidence | No evidence | No established dosage sensitivity |

**pLI Score Interpretation** (gnomAD):
| pLI Range | Interpretation | LoF Intolerance |
|-----------|----------------|-----------------|
| **≥0.9** | Extremely intolerant | High - likely haploinsufficient |
| **0.5-0.9** | Moderately intolerant | Moderate |
| **<0.5** | Tolerant | Low - likely NOT haploinsufficient |

**Implementation**:

```python
def assess_dosage_sensitivity(tu, gene_list):
    """
    Assess dosage sensitivity for all genes in SV.
    Returns dosage scores and interpretation.
    """
    dosage_data = []

    for gene_symbol in gene_list:
        # 1. ClinGen dosage sensitivity (gold standard)
        clingen = tu.tools.ClinGen_search_dosage_sensitivity(
            gene=gene_symbol
        )

        hi_score = None
        ts_score = None
        if clingen.get('data'):
            for entry in clingen['data']:
                hi_score = entry.get('Haploinsufficiency Score')
                ts_score = entry.get('Triplosensitivity Score')
                break

        # 2. ClinGen gene validity (supports dosage sensitivity)
        validity = tu.tools.ClinGen_search_gene_validity(
            gene=gene_symbol
        )

        validity_level = None
        if validity.get('data'):
            for entry in validity['data']:
                validity_level = entry.get('Classification')
                break

        # 3. pLI score from gnomAD (if available via gene search)
        # Note: May need to use myvariant or other tools
        # pli_score = get_pli_score(tu, gene_symbol)

        # 4. OMIM inheritance pattern
        omim = tu.tools.OMIM_search(
            operation="search",
            query=gene_symbol,
            limit=3
        )

        inheritance_pattern = None
        if omim.get('data', {}).get('entries'):
            for entry in omim['data']['entries']:
                mim = entry.get('mimNumber')
                details = tu.tools.OMIM_get_entry(
                    operation="get_entry",
                    mim_number=str(mim)
                )
                # Extract inheritance from details
                # inheritance_pattern = parse_inheritance(details)

        # Integrate evidence
        dosage_assessment = {
            'gene': gene_symbol,
            'hi_score': hi_score,
            'ts_score': ts_score,
            'validity_level': validity_level,
            'inheritance': inheritance_pattern,
            'is_dosage_sensitive': (hi_score == '3' or ts_score == '3'),
            'evidence_grade': calculate_evidence_grade(hi_score, ts_score, validity_level)
        }

        dosage_data.append(dosage_assessment)

    return dosage_data

def calculate_evidence_grade(hi_score, ts_score, validity):
    """
    Calculate evidence grade for dosage sensitivity.
    """
    if (hi_score == '3' or ts_score == '3') and validity == 'Definitive':
        return '★★★'  # High confidence
    elif (hi_score in ['2', '3'] or ts_score in ['2', '3']):
        return '★★☆'  # Moderate confidence
    else:
        return '★☆☆'  # Low confidence
```

**Report Section**:
```markdown
### 3. Dosage Sensitivity Assessment

#### Haploinsufficient Genes (Deletions/Disruptions)

| Gene | ClinGen HI Score | pLI | Validity | Disease | Evidence |
|------|-----------------|-----|----------|---------|----------|
| **KANSL1** | 3 (Sufficient) | 0.99 | Definitive | Koolen-De Vries syndrome | ★★★ |
| **MAPT** | 2 (Emerging) | 0.85 | Strong | FTD (rare) | ★★☆ |

**Interpretation**: KANSL1 has definitive evidence for haploinsufficiency. Deletion of one copy is expected to cause Koolen-De Vries syndrome (intellectual disability, hypotonia, distinctive facial features).

*Sources: ClinGen Dosage Sensitivity Map, gnomAD pLI*

#### Triplosensitive Genes (Duplications)

| Gene | ClinGen TS Score | Disease Mechanism | Evidence |
|------|-----------------|-------------------|----------|
| **MECP2** | 3 (Sufficient) | MECP2 duplication syndrome | ★★★ |
| **PMP22** | 3 (Sufficient) | Charcot-Marie-Tooth 1A | ★★★ |

**Note**: For this deletion, triplosensitivity is not applicable. Listed for reference.

#### Non-Dosage-Sensitive Genes

| Gene | HI Score | TS Score | Interpretation |
|------|----------|----------|----------------|
| **GENE_X** | 0 | 0 | No established dosage sensitivity |
| **GENE_Y** | 1 | 1 | Insufficient evidence |

**Interpretation**: These genes lack evidence for dosage sensitivity. Deletion/duplication less likely to be pathogenic solely due to these genes.
```

---

### Phase 4: Population Frequency Context

**Goal**: Determine if SV is common in general population (likely benign) or rare (supports pathogenicity)

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `gnomad_search` | Population SV frequencies | Overlapping SVs, frequencies |
| `ClinVar_search_variants` | Known pathogenic/benign SVs | Classification, review status |
| `DECIPHER_search` | Patient SVs with phenotypes | Case reports, phenotype similarity |

**Frequency Interpretation** (adapted from ACMG):

| SV Frequency | ACMG Code | Interpretation |
|--------------|-----------|----------------|
| **≥1% in gnomAD SVs** | BA1 (Stand-alone Benign) | Too common for rare disease |
| **0.1-1%** | BS1 (Strong Benign) | Likely benign common variant |
| **<0.01%** | PM2 (Supporting Pathogenic) | Rare, supports pathogenicity |
| **Absent** | PM2 (Supporting) | Very rare, supports pathogenicity |

**Reciprocal Overlap Calculation**:

For proper comparison, calculate reciprocal overlap between query SV and population SV:

```
Reciprocal Overlap = min(overlap_with_A, overlap_with_B)
where:
  overlap_with_A = (overlap length) / (SV_A length)
  overlap_with_B = (overlap length) / (SV_B length)

Threshold: ≥70% reciprocal overlap = "same" SV
```

**Implementation**:

```python
def assess_population_frequency(tu, chrom, sv_start, sv_end, sv_type):
    """
    Check population databases for overlapping SVs.
    """
    # 1. Check ClinVar for known pathogenic/benign SVs
    clinvar = tu.tools.ClinVar_search_variants(
        chromosome=str(chrom),
        start=sv_start,
        stop=sv_end,
        variant_type=sv_type.upper()
    )

    known_svs = []
    if clinvar.get('data'):
        for variant in clinvar['data']:
            classification = variant.get('clinical_significance')
            known_svs.append({
                'database': 'ClinVar',
                'classification': classification,
                'review_status': variant.get('review_status'),
                'coordinates': f"{variant.get('chromosome')}:{variant.get('start')}-{variant.get('stop')}"
            })

    # 2. gnomAD SVs (if available)
    # Note: gnomAD SV database may not have direct API access via ToolUniverse
    # May need to use genomic coordinate search

    # 3. DECIPHER for similar patient cases
    decipher_search = tu.tools.DECIPHER_search(
        query=f"chr{chrom}:{sv_start}-{sv_end}",
        search_type="region"
    )

    patient_cases = []
    if decipher_search.get('data'):
        patient_cases = decipher_search['data']

    return {
        'clinvar_matches': known_svs,
        'decipher_cases': patient_cases,
        'frequency_interpretation': interpret_frequency(known_svs)
    }

def interpret_frequency(known_svs):
    """
    Interpret frequency based on ClinVar matches.
    """
    if any(sv['classification'] == 'Benign' for sv in known_svs):
        return {
            'acmg_code': 'BA1 or BS1',
            'interpretation': 'Likely benign based on ClinVar benign classification',
            'evidence_grade': '★★★'
        }
    elif any(sv['classification'] == 'Pathogenic' for sv in known_svs):
        return {
            'acmg_code': 'PS1',
            'interpretation': 'Pathogenic based on ClinVar pathogenic classification',
            'evidence_grade': '★★★'
        }
    else:
        return {
            'acmg_code': 'PM2',
            'interpretation': 'Rare variant, not found in ClinVar or population databases',
            'evidence_grade': '★★☆'
        }
```

**Report Section**:
```markdown
### 4. Population Frequency Context

#### ClinVar Matches (Overlapping SVs)

| VCV ID | Classification | Size | Overlap | Review Status | Genes |
|--------|----------------|------|---------|---------------|-------|
| VCV000012345 | Pathogenic | 320 kb | 95% reciprocal | ★★★ Reviewed by expert panel | KANSL1, MAPT |

**Match Found**: Query deletion has 95% reciprocal overlap with known pathogenic deletion in ClinVar (VCV000012345). This is the Koolen-De Vries syndrome deletion.

**ACMG Code**: **PS1** (Strong) - Same genomic region as established pathogenic SV

*Source: ClinVar via `ClinVar_search_variants`*

#### gnomAD SV Database

**Search Result**: No overlapping deletions found in gnomAD SV v4.0 (>10,000 genomes)

**Interpretation**: Absence from gnomAD supports rarity and pathogenic potential.

**ACMG Code**: **PM2** (Moderate) - Absent from population databases

*Note: gnomAD SVs queried via browser (no direct API access)*

#### DECIPHER Patient Cases

| Case ID | Phenotype | SV Type | Size | Overlap | Similarity |
|---------|-----------|---------|------|---------|------------|
| 12345 | Intellectual disability, hypotonia | DEL | 315 kb | 98% | High |
| 67890 | Developmental delay, facial dysmorphism | DEL | 305 kb | 92% | High |

**Phenotype Match**: 8/10 DECIPHER patients have intellectual disability and hypotonia, consistent with Koolen-De Vries syndrome.

**ACMG Support**: **PP4** (Supporting) - Patient phenotype consistent with gene's disease association

*Source: DECIPHER via `DECIPHER_search`*
```

---

### Phase 5: Pathogenicity Scoring

**Goal**: Quantitative pathogenicity assessment (0-10 scale)

**Scoring Components**:

1. **Gene Content (40 points max)**:
   - 10 points per dosage-sensitive gene (HI/TS score 3)
   - 5 points per likely dosage-sensitive gene (score 2)
   - 2 points per gene with disease association
   - Cap at 40 points

2. **Dosage Sensitivity Evidence (30 points max)**:
   - 30 points: Multiple genes with definitive HI/TS (score 3)
   - 20 points: One gene with definitive HI/TS
   - 10 points: Genes with emerging evidence (score 2)
   - 5 points: Predicted haploinsufficiency (pLI >0.9)

3. **Population Frequency (20 points max)**:
   - 20 points: Absent from gnomAD, DGV
   - 10 points: Rare (<0.01%)
   - 0 points: Common (>0.1%)
   - -20 points: Very common (>1%) - likely benign

4. **Clinical Evidence (10 points max)**:
   - 10 points: Matching ClinVar pathogenic SV
   - 8 points: DECIPHER cases with matching phenotype
   - 5 points: Literature support for gene dosage effects
   - 3 points: Phenotype consistent with genes

**Pathogenicity Score Interpretation**:

| Score | Classification | Confidence | Interpretation |
|-------|----------------|------------|----------------|
| **9-10** | Pathogenic | ★★★ | High confidence pathogenic |
| **7-8** | Likely Pathogenic | ★★☆ | Strong evidence for pathogenicity |
| **4-6** | VUS | ★☆☆ | Uncertain significance |
| **2-3** | Likely Benign | ★★☆ | Strong evidence for benign |
| **0-1** | Benign | ★★★ | High confidence benign |

**Implementation**:

```python
def calculate_pathogenicity_score(gene_content, dosage_data, frequency_data, clinical_data):
    """
    Calculate comprehensive pathogenicity score (0-10 scale).
    """
    score = 0
    breakdown = {}

    # 1. Gene content scoring (40 points max)
    gene_score = 0
    for gene in gene_content['fully_contained'] + gene_content['partially_disrupted']:
        dosage_info = next((d for d in dosage_data if d['gene'] == gene['symbol']), None)
        if dosage_info:
            if dosage_info['hi_score'] == '3':
                gene_score += 10
            elif dosage_info['hi_score'] == '2':
                gene_score += 5
            elif gene.get('omim_disease'):
                gene_score += 2

    gene_score = min(gene_score, 40)  # Cap at 40
    breakdown['gene_content'] = gene_score / 40 * 4  # Scale to 0-4

    # 2. Dosage sensitivity scoring (30 points max)
    dosage_score = 0
    definitive_genes = sum(1 for d in dosage_data if d['hi_score'] == '3')

    if definitive_genes >= 2:
        dosage_score = 30
    elif definitive_genes == 1:
        dosage_score = 20
    else:
        emerging_genes = sum(1 for d in dosage_data if d['hi_score'] == '2')
        dosage_score = emerging_genes * 5

    dosage_score = min(dosage_score, 30)
    breakdown['dosage_sensitivity'] = dosage_score / 30 * 3  # Scale to 0-3

    # 3. Population frequency scoring (20 points max)
    freq_score = 0
    if frequency_data.get('frequency') is None:
        freq_score = 20  # Absent
    elif frequency_data['frequency'] < 0.0001:
        freq_score = 10  # Rare
    elif frequency_data['frequency'] < 0.001:
        freq_score = 5  # Uncommon
    elif frequency_data['frequency'] > 0.01:
        freq_score = -20  # Common - likely benign

    breakdown['population_frequency'] = freq_score / 20 * 2  # Scale to -2 to 2

    # 4. Clinical evidence scoring (10 points max)
    clinical_score = 0
    if clinical_data.get('clinvar_pathogenic'):
        clinical_score = 10
    elif clinical_data.get('decipher_matching_phenotype'):
        clinical_score = 8
    elif clinical_data.get('literature_support'):
        clinical_score = 5

    clinical_score = min(clinical_score, 10)
    breakdown['clinical_evidence'] = clinical_score / 10 * 1  # Scale to 0-1

    # Total score (0-10 scale)
    total_score = breakdown['gene_content'] + breakdown['dosage_sensitivity'] + \
                  breakdown['population_frequency'] + breakdown['clinical_evidence']

    total_score = max(0, min(10, total_score))  # Ensure 0-10 range

    return {
        'total_score': round(total_score, 1),
        'breakdown': breakdown,
        'classification': classify_score(total_score)
    }

def classify_score(score):
    """Map score to ACMG-style classification."""
    if score >= 9:
        return 'Pathogenic'
    elif score >= 7:
        return 'Likely Pathogenic'
    elif score >= 4:
        return 'VUS'
    elif score >= 2:
        return 'Likely Benign'
    else:
        return 'Benign'
```

**Report Section**:
```markdown
### 5. Pathogenicity Scoring

#### Quantitative Assessment (0-10 Scale)

| Component | Points | Max | Contribution | Rationale |
|-----------|--------|-----|-------------|-----------|
| **Gene Content** | 4.0 | 4 | 40% | KANSL1 (HI score 3), MAPT (HI score 2) |
| **Dosage Sensitivity** | 2.5 | 3 | 25% | One definitive HI gene (KANSL1) |
| **Population Frequency** | 2.0 | 2 | 20% | Absent from gnomAD SVs |
| **Clinical Evidence** | 1.0 | 1 | 10% | ClinVar pathogenic match |
| **Total Score** | **9.5** | 10 | 100% | |

**Classification**: **Pathogenic** (★★★ High Confidence)

**Interpretation**: Score of 9.5/10 indicates high confidence pathogenic SV. Deletion encompasses established haploinsufficient gene (KANSL1), absent from population databases, and matches known pathogenic ClinVar variant.

#### Score Breakdown Visualization

```
Gene Content:        ████████████████████████████████████████ 4.0/4
Dosage Sensitivity:  ██████████████████████████░░░░░░░░░░░░░ 2.5/3
Population Freq:     ████████████████████████████████████████ 2.0/2
Clinical Evidence:   ██████████████████████████████████████░░ 1.0/1
                     ─────────────────────────────────────────
Total:               ██████████████████████████████████████░░ 9.5/10
```

**Key Drivers of Pathogenicity**:
1. KANSL1 haploinsufficiency (definitive evidence)
2. Exact match to known pathogenic deletion
3. Absence from population databases
4. Phenotype consistency with Koolen-De Vries syndrome
```

---

### Phase 6: Literature & Clinical Evidence

**Goal**: Find case reports, functional studies, and clinical validation

**Tools**:
| Tool | Purpose | Coverage |
|------|---------|----------|
| `PubMed_search` | Peer-reviewed literature | Comprehensive |
| `DECIPHER_search` | Patient case database | Developmental disorders |
| `EuropePMC_search` | European literature | Additional coverage |

**Search Strategies**:

```python
def comprehensive_literature_search(tu, genes, sv_type, phenotype):
    """
    Search literature for SV evidence.
    """
    # 1. Gene-specific searches
    literature = []
    for gene in genes:
        # Dosage sensitivity literature
        dosage_papers = tu.tools.PubMed_search(
            query=f'"{gene}" AND (haploinsufficiency OR dosage sensitivity OR deletion syndrome)',
            max_results=20
        )

        # Case reports
        case_papers = tu.tools.PubMed_search(
            query=f'"{gene}" AND deletion AND {phenotype}',
            max_results=15
        )

        literature.append({
            'gene': gene,
            'dosage_papers': dosage_papers,
            'case_reports': case_papers
        })

    # 2. SV-specific searches
    if sv_type == 'DEL':
        sv_papers = tu.tools.PubMed_search(
            query=f'deletion AND {" AND ".join(genes[:3])} AND syndrome',
            max_results=25
        )

    # 3. DECIPHER cases
    decipher_cases = []
    for gene in genes:
        cases = tu.tools.DECIPHER_search(
            query=gene,
            search_type="gene"
        )
        decipher_cases.append(cases)

    return {
        'gene_literature': literature,
        'sv_literature': sv_papers,
        'decipher_cases': decipher_cases
    }
```

**Report Section**:
```markdown
### 6. Literature & Clinical Evidence

#### Key Publications

| Study | Finding | Evidence Type | PMID |
|-------|---------|---------------|------|
| Koolen et al., 2006 | Described 17q21.31 microdeletion syndrome | Original description | 16222315 |
| Koolen et al., 2008 | KANSL1 haploinsufficiency confirmed | Functional validation | 18394581 |
| Zollino et al., 2012 | Phenotype characterization (n=52) | Clinical series | 22736773 |

**Key Findings**:
- 17q21.31 deletion is recurrent (mediated by LCRs)
- KANSL1 haploinsufficiency is primary mechanism
- Phenotype: ID (100%), hypotonia (95%), friendly demeanor (85%)
- Penetrance: >95% for developmental features

*Source: PubMed via `PubMed_search`*

#### DECIPHER Patient Cases (n=45)

**Phenotype Frequency in DECIPHER Cohort**:
| Feature | Frequency | Match to Patient |
|---------|-----------|------------------|
| Intellectual disability | 45/45 (100%) | ✓ Yes |
| Hypotonia | 42/45 (93%) | ✓ Yes |
| Feeding difficulties | 38/45 (84%) | ✓ Yes |
| Distinctive facies | 40/45 (89%) | ✓ Yes |
| Friendly personality | 35/45 (78%) | Unknown |

**Phenotype Match**: Patient phenotype highly consistent with DECIPHER cohort (4/4 assessable features present).

**ACMG Code**: **PP4** (Supporting) - Patient's clinical features consistent with gene's known phenotype

*Source: DECIPHER via `DECIPHER_search`*

#### Functional Evidence for KANSL1 Dosage Sensitivity

| Study | Model | Finding | PMID |
|-------|-------|---------|------|
| Koolen et al., 2012 | Patient cells | Reduced KANSL1 protein | 22736773 |
| Zollino et al., 2015 | Mouse model | Kansl1+/- recapitulates phenotype | 25607366 |
| Arbogast et al., 2017 | Zebrafish | kansl1 knockdown → developmental defects | 28666126 |

**Strength of Evidence**: ★★★ (High) - Multiple independent studies confirm haploinsufficiency mechanism

**ACMG Code**: **PS3_Moderate** - Well-established functional studies showing dosage sensitivity
```

---

### Phase 7: ACMG-Adapted Classification

**Goal**: Apply ACMG/ClinGen criteria adapted for SVs

**SV-Specific ACMG Criteria**:

### Pathogenic Evidence Codes

| Code | Strength | Criteria | SV Application |
|------|----------|----------|----------------|
| **PVS1** | Very Strong | Null variant in HI gene | Complete deletion of HI gene |
| **PS1** | Strong | Same SV as known pathogenic | ≥70% reciprocal overlap with ClinVar pathogenic |
| **PS2** | Strong | De novo (maternity/paternity confirmed) | De novo SV in patient with matching phenotype |
| **PS3** | Strong | Functional studies | Gene dosage effects demonstrated |
| **PS4** | Strong | Case-control enrichment | SV enriched in cases vs controls |
| **PM1** | Moderate | Critical region | Deletion of exons in HI gene |
| **PM2** | Moderate | Absent from controls | Not in gnomAD SVs, DGV |
| **PM3** | Moderate | Recessive: homozygous or compound het | Both alleles affected (rare for SVs) |
| **PM4** | Moderate | Protein length change | In-frame deletion/duplication |
| **PM5** | Moderate | Similar SVs pathogenic | Nearby SVs in ClinVar pathogenic |
| **PM6** | Moderate | De novo (no confirmation) | De novo SV, phenotype consistent |
| **PP1** | Supporting | Segregation in family | SV segregates with phenotype |
| **PP2** | Supporting | Gene/pathway relevant | Genes in SV match phenotype |
| **PP3** | Supporting | Computational evidence | Multiple predictors support haploinsufficiency |
| **PP4** | Supporting | Phenotype consistent | Patient phenotype matches gene-disease |

### Benign Evidence Codes

| Code | Strength | Criteria | SV Application |
|------|----------|----------|----------------|
| **BA1** | Stand-Alone | MAF >5% | SV frequency >5% in gnomAD |
| **BS1** | Strong | MAF too high for disease | SV frequency >1% |
| **BS2** | Strong | Healthy adult with phenotype-associated genotype | SV in healthy individual (careful - reduced penetrance) |
| **BS3** | Strong | Functional studies show no effect | No dosage sensitivity demonstrated |
| **BS4** | Strong | Non-segregation | SV doesn't segregate with phenotype |
| **BP1** | Supporting | Missense in gene without known LOF | N/A for SVs |
| **BP2** | Supporting | Observed in trans with pathogenic | SV + pathogenic SNV = compound het (patient unaffected) |
| **BP4** | Supporting | Computational evidence benign | Predictors suggest no haploinsufficiency |
| **BP5** | Supporting | Found in case with alt cause | Phenotype explained by different variant |
| **BP7** | Supporting | Synonymous with no splice effect | N/A for SVs |

**Classification Algorithm** (ACMG SV Criteria):

| Classification | Evidence Required |
|----------------|-------------------|
| **Pathogenic** | PVS1 + PS1; OR 2 Strong; OR 1 Strong + 3 Moderate |
| **Likely Pathogenic** | 1 Very Strong + 1 Moderate; OR 1 Strong + 2 Moderate; OR 3 Moderate |
| **VUS** | Criteria not met; OR conflicting evidence |
| **Likely Benign** | 1 Strong + 1 Supporting; OR 2 Supporting |
| **Benign** | BA1; OR BS1 + BS2; OR 2 Strong |

**Implementation**:

```python
def apply_acmg_criteria(gene_content, dosage_data, frequency_data, clinical_data, inheritance):
    """
    Apply ACMG SV criteria and calculate classification.
    """
    evidence = {
        'pathogenic': [],
        'benign': []
    }

    # PVS1: Complete deletion of HI gene
    hi_genes = [d for d in dosage_data if d['hi_score'] == '3']
    if len(hi_genes) > 0 and len(gene_content['fully_contained']) > 0:
        evidence['pathogenic'].append({
            'code': 'PVS1',
            'strength': 'Very Strong',
            'rationale': f"Complete deletion of haploinsufficient gene(s): {', '.join(g['gene'] for g in hi_genes)}"
        })

    # PS1: Same as known pathogenic SV
    if clinical_data.get('clinvar_pathogenic_match'):
        evidence['pathogenic'].append({
            'code': 'PS1',
            'strength': 'Strong',
            'rationale': f"≥70% overlap with ClinVar pathogenic SV: {clinical_data['clinvar_id']}"
        })

    # PS2: De novo with phenotype match
    if inheritance == 'de_novo' and clinical_data.get('phenotype_match'):
        evidence['pathogenic'].append({
            'code': 'PS2',
            'strength': 'Strong',
            'rationale': "De novo occurrence in patient with consistent phenotype"
        })

    # PS3: Functional studies
    if clinical_data.get('functional_evidence'):
        evidence['pathogenic'].append({
            'code': 'PS3',
            'strength': 'Strong',
            'rationale': "Well-established functional studies demonstrate dosage sensitivity"
        })

    # PM2: Absent from controls
    if frequency_data.get('frequency') == 0 or frequency_data.get('frequency') is None:
        evidence['pathogenic'].append({
            'code': 'PM2',
            'strength': 'Moderate',
            'rationale': "Absent from gnomAD SV database and DGV"
        })

    # PP4: Phenotype consistent
    if clinical_data.get('phenotype_consistent'):
        evidence['pathogenic'].append({
            'code': 'PP4',
            'strength': 'Supporting',
            'rationale': "Patient phenotype highly consistent with gene-disease association"
        })

    # BA1: Common variant
    if frequency_data.get('frequency', 0) > 0.05:
        evidence['benign'].append({
            'code': 'BA1',
            'strength': 'Stand-Alone',
            'rationale': f"Frequency {frequency_data['frequency']:.3f} too high for rare disease"
        })

    # BS1: High frequency
    if 0.01 < frequency_data.get('frequency', 0) <= 0.05:
        evidence['benign'].append({
            'code': 'BS1',
            'strength': 'Strong',
            'rationale': f"Frequency {frequency_data['frequency']:.3f} exceeds expected for disease"
        })

    # Calculate classification
    classification = determine_classification(evidence)

    return {
        'evidence': evidence,
        'classification': classification['class'],
        'confidence': classification['confidence']
    }

def determine_classification(evidence):
    """
    Apply ACMG classification rules.
    """
    path = evidence['pathogenic']
    ben = evidence['benign']

    # Count evidence by strength
    very_strong = len([e for e in path if e['strength'] == 'Very Strong'])
    strong_path = len([e for e in path if e['strength'] == 'Strong'])
    moderate_path = len([e for e in path if e['strength'] == 'Moderate'])
    supporting_path = len([e for e in path if e['strength'] == 'Supporting'])

    standalone_ben = len([e for e in ben if e['strength'] == 'Stand-Alone'])
    strong_ben = len([e for e in ben if e['strength'] == 'Strong'])
    supporting_ben = len([e for e in ben if e['strength'] == 'Supporting'])

    # Benign criteria (takes precedence if strong)
    if standalone_ben >= 1:
        return {'class': 'Benign', 'confidence': '★★★'}
    if strong_ben >= 2:
        return {'class': 'Benign', 'confidence': '★★★'}
    if strong_ben >= 1 and supporting_ben >= 1:
        return {'class': 'Likely Benign', 'confidence': '★★☆'}
    if supporting_ben >= 2:
        return {'class': 'Likely Benign', 'confidence': '★★☆'}

    # Pathogenic criteria
    if very_strong >= 1 and strong_path >= 1:
        return {'class': 'Pathogenic', 'confidence': '★★★'}
    if strong_path >= 2:
        return {'class': 'Pathogenic', 'confidence': '★★★'}
    if very_strong >= 1 and moderate_path >= 1:
        return {'class': 'Likely Pathogenic', 'confidence': '★★☆'}
    if strong_path >= 1 and moderate_path >= 2:
        return {'class': 'Likely Pathogenic', 'confidence': '★★☆'}
    if strong_path >= 1 and moderate_path >= 1 and supporting_path >= 1:
        return {'class': 'Likely Pathogenic', 'confidence': '★★☆'}
    if moderate_path >= 3:
        return {'class': 'Likely Pathogenic', 'confidence': '★☆☆'}

    # Default to VUS
    return {'class': 'VUS', 'confidence': '★☆☆'}
```

**Report Section**:
```markdown
### 7. ACMG-Adapted Classification

#### Evidence Codes Applied

**Pathogenic Evidence**:

| Code | Strength | Rationale |
|------|----------|-----------|
| **PVS1** | Very Strong | Complete deletion of haploinsufficient gene (KANSL1, HI score 3) |
| **PS1** | Strong | ≥95% overlap with ClinVar pathogenic deletion (VCV000012345) |
| **PM2** | Moderate | Absent from gnomAD SV database (>10,000 genomes) |
| **PP4** | Supporting | Patient phenotype consistent with Koolen-De Vries syndrome |

**Benign Evidence**: None

#### Evidence Summary

| Pathogenic | Benign |
|------------|--------|
| 1 Very Strong (PVS1) | None |
| 1 Strong (PS1) | |
| 1 Moderate (PM2) | |
| 1 Supporting (PP4) | |

#### Classification: **PATHOGENIC** ★★★

**Rationale**: Meets ACMG criteria for Pathogenic (1 Very Strong + 1 Strong). Complete deletion of established haploinsufficient gene (KANSL1) with exact match to known pathogenic deletion.

**Confidence**: ★★★ (High) - Multiple independent lines of strong evidence

#### Classification Certainty Factors

✅ **Strengths**:
- Exact match to well-characterized pathogenic deletion
- Complete deletion of definitive HI gene (KANSL1)
- Absent from population databases
- Phenotype highly consistent with gene-disease

⚠ **Limitations**:
- None significant - this is a well-established pathogenic SV
```

---

## Output Structure

### Report File: `SV_analysis_report.md`

```markdown
# Structural Variant Analysis Report: [SV_IDENTIFIER]

**Generated**: [Date] | **Analyst**: ToolUniverse SV Interpreter

---

## Executive Summary

| Field | Value |
|-------|-------|
| **SV Type** | Deletion / Duplication / Inversion / Translocation |
| **Coordinates** | chr17:44039927-44352659 (GRCh38) |
| **Size** | 313 kb |
| **Gene Content** | 2 genes fully contained, 0 partially disrupted |
| **Classification** | Pathogenic / Likely Pathogenic / VUS / Likely Benign / Benign |
| **Pathogenicity Score** | X.X / 10 |
| **Confidence** | ★★★ / ★★☆ / ★☆☆ |
| **Key Finding** | [One-sentence summary] |

**Clinical Action**: [Required / Recommended / None]

---

## 1. SV Identity & Classification

{SV type, coordinates, size, breakpoint precision, inheritance}

---

## 2. Gene Content Analysis

### 2.1 Fully Contained Genes
{Table of genes with functions, disease associations}

### 2.2 Partially Disrupted Genes
{Genes with breakpoints, domains affected}

### 2.3 Flanking Genes
{Genes near breakpoints, position effect risk}

---

## 3. Dosage Sensitivity Assessment

### 3.1 Haploinsufficient Genes
{ClinGen HI scores, pLI, evidence}

### 3.2 Triplosensitive Genes
{ClinGen TS scores, duplication syndromes}

### 3.3 Non-Dosage-Sensitive Genes
{Genes without established dosage effects}

---

## 4. Population Frequency Context

### 4.1 ClinVar Matches
{Known pathogenic/benign SVs}

### 4.2 gnomAD SV Database
{Population frequencies}

### 4.3 DECIPHER Patient Cases
{Similar SVs, phenotype matching}

---

## 5. Pathogenicity Scoring

### 5.1 Quantitative Assessment
{0-10 score with breakdown}

### 5.2 Score Components
{Gene content, dosage, frequency, clinical}

---

## 6. Literature & Clinical Evidence

### 6.1 Key Publications
{Functional studies, case series}

### 6.2 DECIPHER Cohort Analysis
{Phenotype frequencies, matching}

### 6.3 Functional Evidence
{Gene dosage studies}

---

## 7. ACMG-Adapted Classification

### 7.1 Evidence Codes Applied
{Pathogenic and benign codes with rationale}

### 7.2 Classification
{Final classification with confidence}

### 7.3 Certainty Factors
{Strengths and limitations}

---

## 8. Clinical Recommendations

### 8.1 For Affected Individual
{Testing, management, surveillance}

### 8.2 For Family Members
{Cascade testing, genetic counseling}

### 8.3 Reproductive Considerations
{Recurrence risk, prenatal testing}

---

## 9. Limitations & Uncertainties

{Missing data, conflicting evidence, knowledge gaps}

---

## Data Sources

{All tools and databases queried with results}
```

---

## Evidence Grading System

| Symbol | Confidence | Criteria |
|--------|------------|----------|
| ★★★ | High | ClinGen definitive, ClinVar expert reviewed, multiple independent studies |
| ★★☆ | Moderate | ClinGen strong/moderate, single good study, DECIPHER cohort support |
| ★☆☆ | Limited | Computational predictions only, case reports, emerging evidence |

---

## Special Scenarios

### Scenario 1: Recurrent Microdeletion Syndrome

**Additional considerations**:
- Check for recurrence mechanism (LCRs, NAHR)
- Look for founder effects
- Population-specific frequencies
- Incomplete penetrance
- Variable expressivity

**Example**: 22q11.2 deletion, 17q21.31 deletion (Koolen-De Vries)

### Scenario 2: Balanced Translocation (No Gene Disruption)

**Assessment approach**:
- If no genes disrupted: Likely benign (in most cases)
- Check for cryptic imbalances
- Consider position effects (rare)
- Reproductive risk (unbalanced offspring)

**Classification**: Usually VUS or Likely Benign unless offspring affected

### Scenario 3: Complex Rearrangement

**Analysis strategy**:
- Break down into component SVs
- Assess each breakpoint independently
- Look for chromothripsis pattern
- Consider cumulative gene dosage effects
- Check for DNA repair defects

### Scenario 4: Small In-Frame Deletion/Duplication

**Special considerations**:
- May not cause haploinsufficiency
- Check if critical domain affected
- Look for similar variants in ClinVar
- Consider protein structural impact
- May need functional studies

---

## Quantified Minimums

| Section | Requirement |
|---------|-------------|
| Gene content | All genes in SV region annotated |
| Dosage sensitivity | ClinGen scores for all genes (if available) |
| Population frequency | Check gnomAD SV + ClinVar + DGV |
| Literature search | ≥2 search strategies (PubMed + DECIPHER) |
| ACMG codes | All applicable codes listed |

---

## Tools Reference

### Core Tools for SV Analysis

| Tool | Purpose | Required? |
|------|---------|-----------|
| `ClinGen_search_dosage_sensitivity` | HI/TS scores | **Required** |
| `ClinGen_search_gene_validity` | Gene-disease validity | **Required** |
| `ClinVar_search_variants` | Known pathogenic/benign SVs | **Required** |
| `DECIPHER_search` | Patient cases, phenotypes | Highly recommended |
| `Ensembl_lookup_gene` | Gene coordinates, structure | **Required** |
| `OMIM_search`, `OMIM_get_entry` | Gene-disease associations | **Required** |
| `DisGeNET_search_gene` | Additional disease associations | Recommended |
| `PubMed_search` | Literature evidence | Recommended |
| `Gene_Ontology_get_term_info` | Gene function | Supporting |

---

## Report File Naming

```
SV_analysis_[TYPE]_chr[CHR]_[START]_[END]_[GENES].md

Examples:
SV_analysis_DEL_chr17_44039927_44352659_KANSL1_MAPT.md
SV_analysis_DUP_chr22_17400000_17800000_TBX1.md
SV_analysis_INV_chr11_2100000_2400000_complex.md
```

---

## Clinical Recommendations Framework

### For Pathogenic/Likely Pathogenic SVs

| SV Type | Recommendations |
|---------|-----------------|
| **Deletion (HI gene)** | Genetic counseling, cascade testing, phenotype-specific surveillance |
| **Duplication (TS gene)** | Same as deletion; check for dosage-specific syndrome |
| **Translocation (disruption)** | Assess both breakpoints, consider reproductive counseling |
| **Complex** | Multidisciplinary evaluation, research enrollment |

### For VUS

| Action | Details |
|--------|---------|
| Clinical management | Base on phenotype, not genotype |
| Follow-up | Reinterpret in 1-2 years or when phenotype evolves |
| Research | Functional studies if research-grade samples available |
| Family studies | Segregation analysis can reclassify |

### For Benign/Likely Benign

| Action | Details |
|--------|---------|
| Clinical | Not expected to cause rare disease |
| Family | No cascade testing needed (unless recurrent/reproductive risk) |
| Reproductive | Balanced translocation carriers may have offspring risk |

---

## When NOT to Use This Skill

- **Single nucleotide variants (SNVs)** → Use `tooluniverse-variant-interpretation` skill
- **Small indels (<50 bp)** → Use variant interpretation skill
- **Somatic variants in cancer** → Different framework needed
- **Mitochondrial variants** → Specialized interpretation required
- **Repeat expansions** → Different mechanism

Use this skill for **structural variants ≥50 bp** requiring dosage sensitivity assessment and ACMG-adapted classification.

---

## See Also

- `EXAMPLES.md` - Sample SV interpretations
- `README.md` - Quick start guide
- `tooluniverse-variant-interpretation` - For SNVs and small indels
- ClinGen Dosage Sensitivity Map: https://www.ncbi.nlm.nih.gov/projects/dbvar/clingen/
- ACMG SV Guidelines: Riggs et al., Genet Med 2020 (PMID: 31690835)
