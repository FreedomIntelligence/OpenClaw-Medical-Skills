# tooluniverse-variant-interpretation

> Systematic clinical variant interpretation from raw variant calls to ACMG-classified recommendations with structural impact analysis. Aggregates evidence from ClinVar, gnomAD, CIViC, UniProt, and PDB across ACMG criteria. Produces pathogenicity scores (0-100), clinical recommendations, and treatment implications. Use when interpreting genetic variants, classifying variants of uncertain significance (VUS), performing ACMG variant classification, or translating variant calls to clinical actionability.

---
name: tooluniverse-variant-interpretation
description: Systematic clinical variant interpretation from raw variant calls to ACMG-classified recommendations with structural impact analysis. Aggregates evidence from ClinVar, gnomAD, CIViC, UniProt, and PDB across ACMG criteria. Produces pathogenicity scores (0-100), clinical recommendations, and treatment implications. Use when interpreting genetic variants, classifying variants of uncertain significance (VUS), performing ACMG variant classification, or translating variant calls to clinical actionability.
---

# Clinical Variant Interpreter

Systematic variant interpretation skill using ToolUniverse - from raw variant calls to ACMG-classified clinical recommendations with structural impact analysis.

---

## Problem This Skill Solves

Clinical labs and researchers face critical challenges in variant interpretation:

1. **Variant classification uncertainty** - VUS (Variants of Uncertain Significance) comprise 40-60% of clinical variants
2. **Evidence aggregation burden** - Must integrate data from 10+ databases per variant
3. **Structural context missing** - Traditional annotation ignores 3D protein impact
4. **Clinical actionability unclear** - How does classification translate to patient care?

**This skill provides**: A systematic workflow that combines population databases, functional predictions, structural analysis (via AlphaFold2), and literature evidence into ACMG-compliant interpretations with clear clinical recommendations.

---

## Key Principles

1. **ACMG-Guided Classification** - Follow ACMG/AMP 2015 guidelines with explicit evidence codes
2. **Structural Evidence Integration** - Use AlphaFold2 for novel structural impact analysis
3. **Population Context** - gnomAD frequencies with ancestry-specific data
4. **Gene-Disease Validity** - ClinGen curation status for clinical relevance
5. **Actionable Output** - Clear recommendations, not just classifications
6. **English-first queries** - Always use English terms in tool calls (gene names, variant descriptions, disease names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## Triggers

Use this skill when users:
- Ask about variant interpretation or classification
- Have VCF data needing clinical annotation
- Ask "what does this variant mean clinically?"
- Need ACMG classification for variants
- Want structural impact analysis for missense variants
- Ask about pathogenicity of specific variants

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    VARIANT INTERPRETATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: VARIANT IDENTITY                                       │
│  ├── Normalize variant notation (HGVS)                          │
│  ├── Map to gene, transcript, protein                           │
│  └── Get consequence type (missense, nonsense, etc.)            │
│                                                                  │
│  Phase 2: CLINICAL DATABASES                                     │
│  ├── ClinVar: Existing classifications                          │
│  ├── gnomAD: Population frequencies (all + ancestry)            │
│  ├── OMIM: Gene-disease associations                            │
│  ├── ClinGen: Gene validity + dosage sensitivity (ENHANCED)     │
│  │   └─ ClinGen_search_gene_validity, ClinGen_search_dosage     │
│  └── SpliceAI: Splice variant prediction (NEW)                  │
│                                                                  │
│  Phase 2.5: REGULATORY CONTEXT (NEW - for non-coding variants)  │
│  ├── ChIPAtlas: TF binding at position                          │
│  ├── ENCODE: Regulatory elements (enhancers, promoters)         │
│  ├── Conservation in regulatory regions                         │
│  └── Functional annotation of regulatory impact                 │
│                                                                  │
│  Phase 3: COMPUTATIONAL PREDICTIONS                              │
│  ├── SIFT/PolyPhen: Damaging predictions                        │
│  ├── CADD: Deleteriousness score                                │
│  ├── SpliceAI: Splice impact (if applicable)                    │
│  └── Conservation: Cross-species alignment                      │
│                                                                  │
│  Phase 4: STRUCTURAL ANALYSIS (for VUS/novel missense)          │
│  ├── Get protein structure (PDB or AlphaFold2)                  │
│  ├── Map variant to structure                                   │
│  ├── Assess domain/functional site impact                       │
│  └── Predict structural destabilization                         │
│                                                                  │
│  Phase 4.5: EXPRESSION CONTEXT (NEW)                            │
│  ├── CELLxGENE: Cell-type specific expression                   │
│  ├── Tissue relevance to phenotype                              │
│  └── Expression validation                                       │
│                                                                  │
│  Phase 5: LITERATURE EVIDENCE                                    │
│  ├── PubMed: Functional studies                                 │
│  ├── BioRxiv/MedRxiv: Recent preprints (NEW)                   │
│  ├── Case reports: Phenotype correlations                       │
│  └── Segregation data (if in literature)                        │
│                                                                  │
│  Phase 6: ACMG CLASSIFICATION                                    │
│  ├── Apply evidence codes (PVS1, PM2, PP3, etc.)               │
│  ├── Calculate classification                                   │
│  ├── Identify limiting factors                                  │
│  └── Generate clinical recommendations                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Details

### Phase 1: Variant Identity & Normalization

**Goal**: Standardize variant notation and determine molecular consequence

**Tools**:
| Tool | Purpose |
|------|---------|
| `myvariant_query` | Get variant annotations from MyVariant.info |
| `Ensembl_get_variant_info` | Variant effect predictor data |
| `NCBI_gene_search` | Gene information |

**Key Information to Capture**:
- HGVS notation (c. and p.)
- Gene symbol and Ensembl ID
- Transcript (canonical/MANE Select)
- Consequence type
- Amino acid change (for missense)
- Exon/intron location

### Phase 2: Clinical Database Queries

**Goal**: Aggregate existing clinical knowledge

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `clinvar_search` | Existing classifications | Classification, review status, submissions |
| `gnomad_search` | Population frequency | AF, ancestry-specific AFs, homozygotes |
| `OMIM_search`, `OMIM_get_entry` | Gene-disease | Inheritance, phenotypes |
| `ClinGen_gene_validity` | Curation status | Gene-disease validity level |
| `COSMIC_search_mutations` | **Somatic mutations (NEW)** | Cancer frequency, histology |
| `DisGeNET_search_gene` | **Gene-disease associations (NEW)** | Evidence scores, sources |

### 2.1 COSMIC for Somatic Context (NEW)

For cancer variants, check COSMIC for somatic mutation frequency:

```python
def get_somatic_context(tu, gene_symbol, variant_aa):
    """Get somatic mutation context from COSMIC."""
    
    # Search for specific mutation
    cosmic = tu.tools.COSMIC_search_mutations(
        operation="search",
        terms=f"{gene_symbol} {variant_aa}",
        max_results=20,
        genome_build=38
    )
    
    # Get all gene mutations for context
    gene_mutations = tu.tools.COSMIC_get_mutations_by_gene(
        operation="get_by_gene",
        gene=gene_symbol,
        max_results=100
    )
    
    # Determine if it's a hotspot
    mutation_counts = Counter(m['MutationAA'] for m in gene_mutations.get('results', []))
    is_hotspot = variant_aa in [m[0] for m in mutation_counts.most_common(10)]
    
    return {
        'cosmic_hits': cosmic.get('results', []),
        'is_somatic_hotspot': is_hotspot,
        'cancer_types': [m['PrimarySite'] for m in cosmic.get('results', [])],
        'total_cosmic_count': cosmic.get('total_count', 0)
    }
```

### 2.2 OMIM Gene-Disease Context (NEW)

```python
def get_omim_context(tu, gene_symbol):
    """Get OMIM gene-disease associations."""
    
    # Search OMIM for gene
    search = tu.tools.OMIM_search(
        operation="search",
        query=gene_symbol,
        limit=5
    )
    
    omim_data = []
    for entry in search.get('data', {}).get('entries', []):
        mim = entry.get('mimNumber')
        
        # Get detailed entry
        details = tu.tools.OMIM_get_entry(
            operation="get_entry",
            mim_number=str(mim)
        )
        
        # Get clinical synopsis
        synopsis = tu.tools.OMIM_get_clinical_synopsis(
            operation="get_clinical_synopsis",
            mim_number=str(mim)
        )
        
        omim_data.append({
            'mim_number': mim,
            'title': details.get('data', {}).get('titles', {}),
            'inheritance': synopsis.get('data', {}).get('inheritance'),
            'clinical_features': synopsis.get('data', {})
        })
    
    return omim_data
```

### 2.3 DisGeNET Gene-Disease Evidence (NEW)

```python
def get_disgenet_context(tu, gene_symbol, variant_rsid=None):
    """Get gene-disease associations from DisGeNET."""
    
    # Gene-disease associations
    gda = tu.tools.DisGeNET_search_gene(
        operation="search_gene",
        gene=gene_symbol,
        limit=20
    )
    
    # Variant-disease associations (if rsID available)
    vda = None
    if variant_rsid:
        vda = tu.tools.DisGeNET_get_vda(
            operation="get_vda",
            variant=variant_rsid,
            limit=20
        )
    
    return {
        'gene_associations': gda.get('data', {}).get('associations', []),
        'variant_associations': vda.get('data', {}).get('associations', []) if vda else []
    }
```

### 2.4 ClinGen Gene Validity & Dosage Sensitivity (NEW)

ClinGen provides authoritative curation of gene-disease relationships:

```python
def get_clingen_evidence(tu, gene_symbol):
    """
    Get ClinGen gene validity and dosage sensitivity data.
    CRITICAL for ACMG classification - establishes gene-disease validity.
    """
    
    # 1. Gene-disease validity (Definitive/Strong/Moderate/Limited)
    validity = tu.tools.ClinGen_search_gene_validity(gene=gene_symbol)
    
    validity_data = []
    if validity.get('data'):
        for entry in validity.get('data', []):
            validity_data.append({
                'disease': entry.get('Disease Label'),
                'classification': entry.get('Classification'),  # Definitive, Strong, etc.
                'inheritance': entry.get('Inheritance'),
                'mondo_id': entry.get('Disease ID (MONDO)')
            })
    
    # 2. Dosage sensitivity (haploinsufficiency, triplosensitivity)
    dosage = tu.tools.ClinGen_search_dosage_sensitivity(gene=gene_symbol)
    
    dosage_data = {}
    if dosage.get('data'):
        for entry in dosage.get('data', []):
            dosage_data = {
                'haploinsufficiency_score': entry.get('Haploinsufficiency Score'),
                'triplosensitivity_score': entry.get('Triplosensitivity Score'),
                'disease': entry.get('Disease')
            }
            break  # Usually one entry per gene
    
    # 3. Clinical actionability (for incidental findings context)
    actionability = tu.tools.ClinGen_search_actionability(gene=gene_symbol)
    
    return {
        'gene_validity': validity_data,
        'dosage_sensitivity': dosage_data,
        'actionability': actionability.get('data', {}),
        'has_definitive_validity': any(v['classification'] == 'Definitive' for v in validity_data),
        'is_haploinsufficient': dosage_data.get('haploinsufficiency_score') == '3'
    }
```

**ClinGen Validity Levels** (for ACMG PM1/PP4):
| Classification | Meaning | ACMG Impact |
|----------------|---------|-------------|
| **Definitive** | Multiple concordant studies | Strong gene-disease support |
| **Strong** | Extensive evidence | Moderate-strong support |
| **Moderate** | Some evidence | Moderate support |
| **Limited** | Minimal evidence | Weak support, use caution |
| **Disputed** | Conflicting evidence | Do not use for classification |
| **Refuted** | Evidence against | Gene NOT associated |

**Dosage Sensitivity Scores** (for CNV interpretation):
| Score | Meaning | Interpretation |
|-------|---------|----------------|
| **3** | Sufficient evidence | Haploinsufficiency/triplosensitivity established |
| **2** | Emerging evidence | Some support, not definitive |
| **1** | Little evidence | Minimal support |
| **0** | No evidence | Unknown |

### 2.5 SpliceAI Splice Variant Prediction (NEW)

~15% of pathogenic variants affect splicing. SpliceAI is the gold standard for splice prediction:

```python
def get_spliceai_prediction(tu, chrom, pos, ref, alt, genome="38"):
    """
    Get SpliceAI splice effect predictions.
    
    Delta scores:
    - DS_AG: Acceptor gain
    - DS_AL: Acceptor loss  
    - DS_DG: Donor gain
    - DS_DL: Donor loss
    
    Thresholds:
    - ≥0.8: High pathogenicity (strong PP3)
    - 0.5-0.8: Moderate (supporting PP3)
    - 0.2-0.5: Low (weak evidence)
    - <0.2: Likely benign
    """
    
    # Format variant for SpliceAI
    variant = f"chr{chrom}-{pos}-{ref}-{alt}"
    
    # Get full splice predictions
    result = tu.tools.SpliceAI_predict_splice(
        variant=variant,
        genome=genome
    )
    
    if result.get('data'):
        max_score = result['data'].get('max_delta_score', 0)
        interpretation = result['data'].get('interpretation', '')
        
        # Determine ACMG support
        if max_score >= 0.8:
            acmg = 'PP3 (strong) - high splice impact'
        elif max_score >= 0.5:
            acmg = 'PP3 (supporting) - moderate splice impact'
        elif max_score >= 0.2:
            acmg = 'PP3 (weak) - possible splice impact'
        else:
            acmg = 'BP7 (if synonymous) - splice benign'
        
        return {
            'max_delta_score': max_score,
            'interpretation': interpretation,
            'acmg_support': acmg,
            'scores': result['data'].get('scores', [])
        }
    return None

def quick_splice_check(tu, variant, genome="38"):
    """Quick triage using max delta score only."""
    
    result = tu.tools.SpliceAI_get_max_delta(
        variant=variant,
        genome=genome
    )
    
    return result.get('data', {})
```

**When to Use SpliceAI**:
- **Intronic variants** near splice sites (±50bp)
- **Synonymous variants** (may still affect splicing)
- **Exonic variants** near splice junctions
- **Variants creating cryptic splice sites**

**Report Section for Splice Variants**:
```markdown
### Splice Impact Analysis (SpliceAI)

| Score Type | Value | Position | Interpretation |
|------------|-------|----------|----------------|
| DS_AG | 0.02 | +15 | Acceptor gain unlikely |
| DS_AL | 0.85 | -2 | **High acceptor loss** |
| DS_DG | 0.01 | +8 | Donor gain unlikely |
| DS_DL | 0.03 | +1 | Donor loss unlikely |

**Max Delta Score**: 0.85 (DS_AL)
**Interpretation**: High impact - likely disrupts acceptor site
**ACMG Support**: PP3 (strong) for splice-altering effect

*Source: SpliceAI via `SpliceAI_predict_splice`*
```

**ClinVar Classification Map**:
| ClinVar | Interpretation |
|---------|----------------|
| Pathogenic | Disease-causing |
| Likely pathogenic | 90%+ confidence pathogenic |
| VUS | Uncertain significance |
| Likely benign | 90%+ confidence benign |
| Benign | Not disease-causing |
| Conflicting | Multiple interpretations |

**gnomAD Thresholds (for rare disease)**:
| Frequency | ACMG Code | Interpretation |
|-----------|-----------|----------------|
| Absent | PM2_Supporting | Absent from controls |
| <0.00001 | PM2_Supporting | Extremely rare |
| <0.0001 | - | Rare (use with caution) |
| >0.01 | BS1/BA1 | Too common for rare disease |

**COSMIC Somatic Evidence (NEW)**:
| COSMIC Finding | Interpretation | ACMG Support |
|----------------|----------------|--------------|
| Recurrent hotspot (>100 samples) | Known oncogenic driver | PS3 (functional) |
| Moderate frequency (10-100) | Likely oncogenic | PM1 (hotspot) |
| Rare somatic (<10) | Unknown significance | No support |

**DisGeNET Score Interpretation (NEW)**:
| GDA Score | Evidence Level | ACMG Support |
|-----------|----------------|--------------|
| >0.7 | Strong | PP4 (phenotype) |
| 0.4-0.7 | Moderate | Supporting |
| <0.4 | Weak | Insufficient |

### Phase 2.5: Regulatory Context (NEW - for Non-Coding Variants)

**Goal**: Assess regulatory impact for non-coding, intronic, and promoter variants

**When to Apply**:
- Intronic variants (not splice site)
- Promoter variants
- 5'UTR / 3'UTR variants
- Intergenic variants near disease genes

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `ChIPAtlas_enrichment_analysis` | TF binding at position | Bound TFs, cell types |
| `ChIPAtlas_get_peak_data` | ChIP-seq peaks | Peak coordinates, scores |
| `ENCODE_search_experiments` | Regulatory elements | Enhancers, promoters, DHS |
| `ENCODE_get_experiment` | Experiment details | Assay type, targets |

**Regulatory Impact Assessment**:

```python
def assess_regulatory_impact(tu, variant_position, gene_symbol):
    """Assess regulatory impact of non-coding variant."""
    
    # Check TF binding at position
    tf_binding = tu.tools.ChIPAtlas_enrichment_analysis(
        gene=gene_symbol,
        cell_type="all"
    )
    
    # Get ChIP-seq peaks overlapping variant
    peaks = tu.tools.ChIPAtlas_get_peak_data(
        gene=gene_symbol,
        experiment_type="TF"
    )
    
    # Search ENCODE for regulatory annotations
    encode_data = tu.tools.ENCODE_search_experiments(
        assay_title="ATAC-seq",
        biosample="all"
    )
    
    # Assess if variant disrupts TF binding
    binding_disrupted = check_motif_disruption(variant_position, peaks)
    
    return {
        'tf_binding': tf_binding,
        'regulatory_peaks': peaks,
        'encode_annotations': encode_data,
        'likely_regulatory': binding_disrupted
    }
```

**Regulatory Impact Categories**:
| Category | Criteria | ACMG Support |
|----------|----------|--------------|
| **High impact** | Disrupts known TF binding motif | PP3 (supporting) |
| **Moderate impact** | In active regulatory region | Consider context |
| **Low impact** | No regulatory annotation | No support |

**Output for Report**:
```markdown
### 2.5 Regulatory Context (for Non-Coding Variants)

| Feature | Finding | Significance |
|---------|---------|--------------|
| Variant location | Intron 5, 120bp from exon 6 | Not canonical splice |
| TF binding site | CTCF binding peak (ChIPAtlas) | May affect insulation |
| ENCODE annotation | Active enhancer (H3K27ac) | Regulatory function |
| Conservation | PhyloP = 2.8 | Moderate conservation |

**Regulatory Interpretation**: Variant overlaps CTCF binding site in active enhancer region. Potential impact on gene regulation.

*Source: ChIPAtlas, ENCODE*
```

### Phase 3: Computational Predictions (ENHANCED)

**Goal**: Assess in silico pathogenicity predictions using state-of-the-art models

**Tools**:
| Tool | Purpose | Score Range |
|------|---------|-------------|
| `CADD_get_variant_score` | **Deleteriousness score (NEW API)** | PHRED 0-99 |
| `AlphaMissense_get_variant_score` | **DeepMind pathogenicity (NEW)** | 0-1 |
| `EVE_get_variant_score` | **Evolutionary pathogenicity (NEW)** | 0-1 |
| `myvariant_query` | Aggregated predictions | SIFT, PolyPhen |
| `Ensembl_get_variant_info` | VEP predictions | SIFT, PolyPhen |

### 3.1 CADD Deleteriousness Scoring (NEW)

```python
def get_cadd_score(tu, chrom, pos, ref, alt):
    """Get CADD deleteriousness score for a variant."""
    
    result = tu.tools.CADD_get_variant_score(
        chrom=str(chrom),
        pos=pos,
        ref=ref,
        alt=alt,
        version="GRCh38-v1.7"
    )
    
    if result.get('status') == 'success':
        phred = result['data'].get('phred_score')
        return {
            'score': phred,
            'interpretation': result['data'].get('interpretation'),
            'acmg_support': 'PP3' if phred >= 20 else ('BP4' if phred < 15 else 'neutral')
        }
    return None
```

### 3.2 AlphaMissense Pathogenicity (NEW)

DeepMind's AlphaMissense provides state-of-the-art missense pathogenicity prediction:

```python
def get_alphamissense_score(tu, uniprot_id, variant):
    """
    Get AlphaMissense pathogenicity score.
    variant format: 'R123H' or 'p.R123H'
    
    Thresholds:
    - Pathogenic: score > 0.564
    - Ambiguous: 0.34-0.564
    - Benign: score < 0.34
    """
    
    result = tu.tools.AlphaMissense_get_variant_score(
        uniprot_id=uniprot_id,
        variant=variant
    )
    
    if result.get('status') == 'success' and result.get('data'):
        score = result['data'].get('pathogenicity_score')
        classification = result['data'].get('classification')
        
        # Map to ACMG
        if classification == 'pathogenic':
            acmg = 'PP3 (strong)'  # AlphaMissense has high accuracy
        elif classification == 'benign':
            acmg = 'BP4 (strong)'
        else:
            acmg = 'neutral'
        
        return {
            'score': score,
            'classification': classification,
            'acmg_support': acmg
        }
    return None
```

### 3.3 EVE Evolutionary Prediction (NEW)

EVE uses unsupervised learning on evolutionary data:

```python
def get_eve_score(tu, chrom, pos, ref, alt):
    """
    Get EVE evolutionary pathogenicity score.
    
    Threshold: >0.5 indicates likely pathogenic
    """
    
    result = tu.tools.EVE_get_variant_score(
        chrom=str(chrom),
        pos=pos,
        ref=ref,
        alt=alt
    )
    
    if result.get('status') == 'success':
        eve_scores = result['data'].get('eve_scores', [])
        if eve_scores:
            best_score = eve_scores[0]
            return {
                'score': best_score.get('eve_score'),
                'classification': best_score.get('classification'),
                'gene': best_score.get('gene_symbol'),
                'acmg_support': 'PP3' if best_score.get('eve_score', 0) > 0.5 else 'BP4'
            }
    return None
```

### 3.4 Integrated Prediction Strategy

**For VUS (Variants of Uncertain Significance)**, combine multiple predictors:

```python
def comprehensive_pathogenicity_assessment(tu, variant_info):
    """
    Combine all prediction tools for robust classification.
    """
    chrom = variant_info['chrom']
    pos = variant_info['pos']
    ref = variant_info['ref']
    alt = variant_info['alt']
    uniprot_id = variant_info.get('uniprot_id')
    aa_change = variant_info.get('aa_change')  # e.g., 'R123H'
    
    predictions = {}
    
    # 1. CADD (works for all variant types)
    cadd = get_cadd_score(tu, chrom, pos, ref, alt)
    if cadd:
        predictions['cadd'] = cadd
    
    # 2. AlphaMissense (missense only, requires UniProt ID)
    if uniprot_id and aa_change:
        am = get_alphamissense_score(tu, uniprot_id, aa_change)
        if am:
            predictions['alphamissense'] = am
    
    # 3. EVE (missense only)
    eve = get_eve_score(tu, chrom, pos, ref, alt)
    if eve:
        predictions['eve'] = eve
    
    # Consensus assessment
    damaging_count = sum(1 for p in predictions.values() 
                         if 'PP3' in p.get('acmg_support', ''))
    benign_count = sum(1 for p in predictions.values() 
                       if 'BP4' in p.get('acmg_support', ''))
    
    if damaging_count >= 2 and benign_count == 0:
        consensus = 'likely_damaging'
        acmg = 'PP3 (multiple predictors concordant)'
    elif benign_count >= 2 and damaging_count == 0:
        consensus = 'likely_benign'
        acmg = 'BP4 (multiple predictors concordant)'
    else:
        consensus = 'uncertain'
        acmg = 'neutral (discordant predictions)'
    
    return {
        'predictions': predictions,
        'consensus': consensus,
        'acmg_recommendation': acmg
    }
```

**Prediction Interpretation** (Updated):
| Predictor | Damaging | Benign |
|-----------|----------|--------|
| **AlphaMissense** | >0.564 | <0.34 |
| **CADD PHRED** | ≥20 (top 1%) | <15 |
| **EVE** | >0.5 | ≤0.5 |
| SIFT | <0.05 | ≥0.05 |
| PolyPhen2 | >0.85 (probably) | <0.15 (benign) |

**ACMG Application** (Enhanced):
- **PP3**: Multiple concordant damaging predictions (AlphaMissense + CADD + EVE agreement = strong PP3)
- **BP4**: Multiple concordant benign predictions
- **Note**: AlphaMissense alone achieves ~90% accuracy on ClinVar pathogenic variants

### Phase 4: Structural Analysis

**Goal**: Assess protein structural impact (especially for VUS)

**Tools**:
| Tool | Purpose |
|------|---------|
| `PDB_search_by_uniprot` | Find experimental structures |
| `NvidiaNIM_alphafold2` | Predict structure if no PDB |
| `alphafold_get_prediction` | Get AlphaFold DB structure |
| `InterPro_get_protein_domains` | Domain annotations |
| `UniProt_get_protein_function` | Functional sites |

**Structural Impact Categories**:

| Impact Level | Description | ACMG Support |
|--------------|-------------|--------------|
| **Critical** | Active site, catalytic residue | PM1 (strong) |
| **High** | Buried residue, disulfide, structural core | PM1 (moderate) |
| **Moderate** | Domain interface, binding site | PM1 (supporting) |
| **Low** | Surface, flexible region | No support |

**Using AlphaFold2 for VUS**:
```
1. Get wildtype structure (PDB or AlphaFold)
2. Identify residue location:
   - pLDDT at position (confidence)
   - Solvent accessibility
   - Secondary structure
3. Assess structural context:
   - Distance to functional sites
   - Interaction partners
   - Conservation in structure
4. Predict impact:
   - Side chain burial
   - Hydrogen bond disruption
   - Charge changes in buried positions
```

### Phase 4.5: Expression Context (NEW)

**Goal**: Validate gene expression in disease-relevant tissues/cells

**Tools**:
| Tool | Purpose | Key Data |
|------|---------|----------|
| `CELLxGENE_get_expression_data` | Cell-type specific expression | TPM per cell type |
| `CELLxGENE_get_cell_metadata` | Cell type annotations | Tissue, disease state |
| `GTEx_get_median_gene_expression` | Tissue expression | TPM per tissue |

**Expression Validation**:

```python
def validate_expression_context(tu, gene_symbol, phenotype_tissues):
    """Validate gene is expressed in phenotype-relevant tissues."""
    
    # Single-cell expression
    sc_expression = tu.tools.CELLxGENE_get_expression_data(
        gene=gene_symbol,
        tissue=phenotype_tissues[0] if phenotype_tissues else "all"
    )
    
    # Bulk tissue expression (GTEx)
    gtex = tu.tools.GTEx_get_median_gene_expression(
        gene=gene_symbol
    )
    
    # Check expression in relevant tissues
    relevant_expression = {
        tissue: gtex.get(tissue, 0)
        for tissue in phenotype_tissues
    }
    
    return {
        'single_cell': sc_expression,
        'gtex': relevant_expression,
        'expressed_in_phenotype_tissue': any(v > 1 for v in relevant_expression.values())
    }
```

**Why it matters**:
- Confirms gene is expressed where disease manifests
- Supports PP4 (phenotype-specific) if highly restricted expression
- Can challenge classification if not expressed in affected tissue

**Output for Report**:
```markdown
### 4.5 Expression Context

| Tissue | Expression (TPM) | Relevance |
|--------|------------------|-----------|
| Heart | 45.2 | ✓ Primary disease tissue |
| Skeletal muscle | 38.7 | ✓ Secondary involvement |
| Liver | 2.1 | Low expression |
| Brain | 0.5 | Not expressed |

**Single-Cell Analysis (CELLxGENE)**:
- **Cardiomyocytes**: High expression (TPM=85)
- **Cardiac fibroblasts**: Low expression (TPM=5)

**Interpretation**: Gene highly expressed in cardiomyocytes, supporting cardiac phenotype association.

*Source: GTEx, CELLxGENE Census*
```

### Phase 5: Literature Evidence (ENHANCED)

**Goal**: Find functional studies, case reports, and cutting-edge preprints

**Tools**:
| Tool | Purpose | Coverage |
|------|---------|----------|
| `PubMed_search` | Peer-reviewed studies | Comprehensive |
| `EuropePMC_search` | Additional literature | Europe PMC |
| `BioRxiv_search_preprints` | Biology preprints | Recent findings |
| `MedRxiv_search_preprints` | Clinical preprints | Clinical studies |
| `openalex_search_works` | Citation analysis | Impact metrics |
| `SemanticScholar_search_papers` | AI-ranked search | Relevance |

**Search Strategies**:
```python
def comprehensive_literature_search(tu, gene, variant, phenotype):
    """Search across all literature sources."""
    
    # 1. PubMed: Peer-reviewed
    pubmed = tu.tools.PubMed_search(
        query=f'"{gene}" AND ("{variant}" OR functional)',
        max_results=30
    )
    
    # 2. BioRxiv: Recent preprints
    biorxiv = tu.tools.BioRxiv_search_preprints(
        query=f"{gene} {phenotype}",
        limit=10
    )
    
    # 3. MedRxiv: Clinical preprints
    medrxiv = tu.tools.MedRxiv_search_preprints(
        query=f"{gene} variant {phenotype}",
        limit=10
    )
    
    # 4. Citation analysis
    key_papers = pubmed[:5]  # Top papers
    for paper in key_papers:
        citations = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        paper['citation_count'] = citations[0].get('cited_by_count', 0) if citations else 0
    
    return {
        'pubmed': pubmed,
        'preprints': biorxiv + medrxiv,
        'key_papers_with_citations': key_papers
    }
```

**Search Queries**:
```
# Gene + variant specific
"{GENE} AND ({HGVS_p} OR {AA_change})"

# Functional studies
"{GENE} AND (functional OR functional study OR mutagenesis)"

# Clinical reports
"{GENE} AND (case report OR patient) AND {phenotype}"

# Preprint-specific
"{GENE} genetics 2024" (for recent preprints)
```

**⚠️ Preprint Warning**: Always flag preprints as NOT peer-reviewed in reports.

**Evidence Types**:
| Evidence | ACMG Code | Weight |
|----------|-----------|--------|
| Functional study (null) | PS3 | Strong |
| Functional study (reduced) | PS3_Moderate | Moderate |
| Case reports with segregation | PP1 | Supporting to Moderate |
| Co-occurrence with pathogenic | BP2 | Supporting against |

### Phase 6: ACMG Classification

**Goal**: Systematic classification with explicit evidence

**ACMG Evidence Codes**:

**Pathogenic**:
| Code | Strength | Description |
|------|----------|-------------|
| PVS1 | Very Strong | Null variant in gene where LOF is mechanism |
| PS1 | Strong | Same amino acid change as known pathogenic |
| PS3 | Strong | Well-established functional studies |
| PM1 | Moderate | Mutational hot spot / functional domain |
| PM2 | Moderate | Absent from controls |
| PM5 | Moderate | Different missense at same residue as pathogenic |
| PP3 | Supporting | Multiple computational predictions |
| PP5 | Supporting | Reputable source reports pathogenic |

**Benign**:
| Code | Strength | Description |
|------|----------|-------------|
| BA1 | Stand-alone | MAF >5% |
| BS1 | Strong | MAF greater than expected |
| BS3 | Strong | Functional studies show no effect |
| BP4 | Supporting | Multiple computational predictions benign |
| BP7 | Supporting | Synonymous with no splice impact |

**Classification Algorithm**:
| Classification | Evidence Required |
|----------------|-------------------|
| Pathogenic | 1 Very Strong + 1 Strong; OR 2 Strong; OR 1 Strong + 3 Moderate |
| Likely Pathogenic | 1 Very Strong + 1 Moderate; OR 1 Strong + 2 Moderate; OR 1 Strong + 2 Supporting |
| Likely Benign | 1 Strong + 1 Supporting; OR 2 Supporting |
| Benign | 1 Stand-alone; OR 2 Strong |
| VUS | Criteria not met |

---

## Output Structure

### Report Sections

```markdown
# Variant Interpretation Report: {GENE} {VARIANT}

## Executive Summary
- **Variant**: {HGVS notation}
- **Gene**: {gene symbol}
- **Classification**: {Pathogenic/Likely Pathogenic/VUS/Likely Benign/Benign}
- **Evidence Strength**: {strong/moderate/limited}
- **Key Finding**: {one-sentence summary}

## 1. Variant Identity
{gene, transcript, protein change, consequence}

## 2. Population Data
{gnomAD frequencies, ancestry breakdown}

## 3. Clinical Database Evidence
{ClinVar, ClinGen, OMIM}

## 4. Computational Predictions
{SIFT, PolyPhen, CADD scores}

## 5. Structural Analysis
{Domain location, functional site proximity, AlphaFold confidence}

## 6. Literature Evidence
{Functional studies, case reports}

## 7. ACMG Classification
{Evidence codes applied, classification rationale}

## 8. Clinical Recommendations
{Testing, management, family screening}

## 9. Limitations & Uncertainties
{Missing data, conflicting evidence}

## Data Sources
{All tools and databases queried}
```

---

## Evidence Grading

### Classification Confidence

| Symbol | Classification | Evidence Level |
|--------|----------------|----------------|
| ★★★ | High confidence | Multiple independent lines |
| ★★☆ | Moderate confidence | Some supporting evidence |
| ★☆☆ | Limited confidence | Minimal evidence |
| VUS | Uncertain | Insufficient data |

### Structural Impact Confidence

| pLDDT Range | Interpretation |
|-------------|----------------|
| >90 | Very high confidence in position |
| 70-90 | High confidence |
| 50-70 | Moderate (often loops) |
| <50 | Low confidence (disorder) |

---

## Special Scenarios

### Scenario 1: Novel Missense VUS

**Additional workflow**:
1. Check if other pathogenic variants at same residue
2. Get AlphaFold2 structure
3. Analyze:
   - Is residue buried or surface?
   - What secondary structure?
   - Proximity to active/binding sites?
   - Conservation across species?
4. Apply PM1 if in functional domain
5. Apply PP3 if predictions concordant

### Scenario 2: Truncating Variant

**Additional workflow**:
1. Check if LOF is mechanism for gene
2. Determine if escapes NMD (last exon)
3. Check for alternative isoforms
4. Review ClinGen LOF curation

**PVS1 Application**:
| Scenario | PVS1 Strength |
|----------|---------------|
| Canonical LOF gene, NMD predicted | Very Strong |
| LOF gene, last exon | Moderate |
| Non-LOF gene | Not applicable |

### Scenario 3: Splice Variant

**Additional workflow**:
1. Check SpliceAI scores (if available)
2. Determine canonical splice site distance
3. Review for in-frame skipping potential
4. Check for cryptic splice activation

---

## Quantified Minimums

| Section | Requirement |
|---------|-------------|
| Population frequency | gnomAD overall + ≥3 ancestry groups |
| Predictions | ≥3 computational predictors |
| Literature search | ≥2 search strategies |
| ACMG codes | All applicable codes listed |

---

## NVIDIA NIM Integration

### When to Use AlphaFold2 for Variants

**Use Case**: VUS missense variants where structural context aids interpretation

**Workflow**:
```python
# 1. Get protein sequence
protein_seq = tu.tools.UniProt_get_protein_sequence(accession=uniprot_id)

# 2. Get/predict structure
try:
    pdb_hits = tu.tools.PDB_search_by_uniprot(uniprot_id=uniprot_id)
    structure = tu.tools.PDB_get_structure(pdb_id=pdb_hits[0]['pdb_id'])
except:
    # Predict with AlphaFold2
    structure = tu.tools.NvidiaNIM_alphafold2(
        sequence=protein_seq['sequence'],
        algorithm="mmseqs2"
    )

# 3. Analyze variant position
# - Extract pLDDT at residue position
# - Calculate solvent accessibility
# - Check for nearby functional sites
```

**Structural Features to Report**:
- pLDDT at variant position
- Secondary structure (helix/sheet/coil)
- Solvent accessibility (buried/exposed)
- Distance to active site (if applicable)
- Interactions disrupted (H-bonds, salt bridges)

---

## Report File Naming

```
{GENE}_{VARIANT}_interpretation_report.md

Examples:
BRCA1_c.5266dupC_interpretation_report.md
TP53_p.R273H_interpretation_report.md
```

---

## Clinical Recommendations Framework

### For Pathogenic/Likely Pathogenic

| Disease Context | Recommendations |
|-----------------|-----------------|
| Cancer predisposition | Enhanced screening, risk-reducing options |
| Pharmacogenomics | Drug dosing adjustment |
| Carrier status | Reproductive counseling |
| Predictive testing | Family cascade screening |

### For VUS

| Action | Details |
|--------|---------|
| Clinical management | Do not use for medical decisions |
| Follow-up | Reinterpret in 1-2 years |
| Research | Functional studies if available |
| Family | Segregation data valuable |

### For Benign/Likely Benign

| Action | Details |
|--------|---------|
| Clinical | Not expected to cause disease |
| Family | No cascade testing needed |
| Documentation | Include in report for completeness |

---

## See Also

- `CHECKLIST.md` - Pre-delivery verification
- `EXAMPLES.md` - Sample interpretations
- `TOOLS_REFERENCE.md` - Tool parameters and fallbacks
