# tooluniverse-rare-disease-diagnosis

> Provide differential diagnosis for patients with suspected rare diseases based on phenotype and genetic data. Matches symptoms to HPO terms, identifies candidate diseases from Orphanet/OMIM, prioritizes genes for testing, interprets variants of uncertain significance. Use when clinician asks about rare disease diagnosis, unexplained phenotypes, or genetic testing interpretation.

# Rare Disease Diagnosis Advisor

Systematic diagnosis support for rare diseases using phenotype matching, gene panel prioritization, and variant interpretation across Orphanet, OMIM, HPO, ClinVar, and structure-based analysis.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, update progressively
2. **Phenotype-driven** - Convert symptoms to HPO terms before searching
3. **Multi-database triangulation** - Cross-reference Orphanet, OMIM, OpenTargets
4. **Evidence grading** - Grade diagnoses by supporting evidence strength
5. **Actionable output** - Prioritized differential diagnosis with next steps
6. **Genetic counseling aware** - Consider inheritance patterns and family history
7. **English-first queries** - Always use English terms in tool calls (phenotype descriptions, gene names, disease names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "Patient has [symptoms], what rare disease could this be?"
- "Unexplained developmental delay with [features]"
- "WES found VUS in [gene], is this pathogenic?"
- "What genes should we test for [phenotype]?"
- "Differential diagnosis for [rare symptom combination]"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[PATIENT_ID]_rare_disease_report.md`
   - Initialize with all section headers
   - Add placeholder text: `[Researching...]`

2. **Progressively update** as you gather data

3. **Output separate data files**:
   - `[PATIENT_ID]_gene_panel.csv` - Prioritized genes for testing
   - `[PATIENT_ID]_variant_interpretation.csv` - If variants provided

### 2. Citation Requirements (MANDATORY)

Every finding MUST include source:

```markdown
### Candidate Disease: Marfan Syndrome
- **ORPHA**: ORPHA:558
- **OMIM**: 154700
- **Phenotype match**: 85% (17/20 HPO terms)
- **Inheritance**: AD
- **Gene**: FBN1

*Source: Orphanet via `Orphanet_558`, OMIM via `OMIM_get_entry`*
```

---

## Phase 0: Tool Verification

**CRITICAL**: Verify tool parameters before calling.

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `OpenTargets_get_associated_diseases_by_target_ensemblId` | `ensemblID` | `ensemblId` |
| `ClinVar_get_variant_by_id` | `variant_id` | `id` |
| `MyGene_query_genes` | `gene` | `q` |
| `gnomAD_get_variant_frequencies` | `variant` | `variant_id` |

---

## Workflow Overview

```
Phase 1: Phenotype Standardization
├── Convert symptoms to HPO terms
├── Identify core vs. variable features
└── Note age of onset, inheritance hints
    ↓
Phase 2: Disease Matching
├── Orphanet phenotype search
├── OMIM clinical synopsis match
├── OpenTargets disease associations
└── OUTPUT: Ranked differential diagnosis
    ↓
Phase 3: Gene Panel Identification
├── Extract genes from top diseases
├── Cross-reference expression (GTEx)
├── Prioritize by evidence strength
└── OUTPUT: Recommended gene panel
    ↓
Phase 3.5: Expression & Tissue Context (NEW)
├── CELLxGENE: Cell-type specific expression
├── ChIPAtlas: Regulatory context (TF binding)
├── Tissue-specific gene networks
└── OUTPUT: Expression validation
    ↓
Phase 3.6: Pathway Analysis (NEW)
├── KEGG: Metabolic/signaling pathways
├── Reactome: Biological processes
├── IntAct: Protein-protein interactions
└── OUTPUT: Biological context
    ↓
Phase 4: Variant Interpretation (if provided)
├── ClinVar pathogenicity lookup
├── gnomAD population frequency
├── Protein domain/function impact
├── ENCODE/ChIPAtlas: Regulatory variant impact
└── OUTPUT: Variant classification
    ↓
Phase 5: Structure Analysis (for VUS)
├── NvidiaNIM_alphafold2 → Predict structure
├── Map variant to structure
├── Assess functional domain impact
└── OUTPUT: Structural evidence
    ↓
Phase 6: Literature Evidence (NEW)
├── PubMed: Published studies
├── BioRxiv/MedRxiv: Preprints
├── OpenAlex: Citation analysis
└── OUTPUT: Literature support
    ↓
Phase 7: Report Synthesis
├── Prioritized differential diagnosis
├── Recommended genetic testing
├── Next steps for clinician
└── OUTPUT: Final report
```

---

## Phase 1: Phenotype Standardization

### 1.1 Convert Symptoms to HPO Terms

```python
def standardize_phenotype(tu, symptoms_list):
    """Convert clinical descriptions to HPO terms."""
    hpo_terms = []
    
    for symptom in symptoms_list:
        # Search HPO for matching terms
        results = tu.tools.HPO_search_terms(query=symptom)
        if results:
            hpo_terms.append({
                'original': symptom,
                'hpo_id': results[0]['id'],
                'hpo_name': results[0]['name'],
                'confidence': 'exact' if symptom.lower() in results[0]['name'].lower() else 'partial'
            })
    
    return hpo_terms
```

### 1.2 Phenotype Categories

| Category | Examples | Weight |
|----------|----------|--------|
| **Core features** | Always present in disease | High |
| **Variable features** | Present in >50% | Medium |
| **Occasional features** | Present in <50% | Low |
| **Age-specific** | Onset-dependent | Context |

### 1.3 Output for Report

```markdown
## 1. Phenotype Analysis

### 1.1 Standardized HPO Terms

| Clinical Feature | HPO Term | HPO ID | Category |
|------------------|----------|--------|----------|
| Tall stature | Tall stature | HP:0000098 | Core |
| Long fingers | Arachnodactyly | HP:0001166 | Core |
| Heart murmur | Cardiac murmur | HP:0030148 | Variable |
| Joint hypermobility | Joint hypermobility | HP:0001382 | Core |

**Total HPO Terms**: 8
**Onset**: Childhood
**Family History**: Father with similar features (AD suspected)

*Source: HPO via `HPO_search_terms`*
```

---

## Phase 2: Disease Matching

### 2.1 Orphanet Disease Search (NEW TOOLS)

```python
def match_diseases_orphanet(tu, symptom_keywords):
    """Find rare diseases matching symptoms using Orphanet."""
    candidate_diseases = []
    
    # Search Orphanet by disease keywords
    for keyword in symptom_keywords:
        results = tu.tools.Orphanet_search_diseases(
            operation="search_diseases",
            query=keyword
        )
        if results.get('status') == 'success':
            candidate_diseases.extend(results['data']['results'])
    
    # Get genes for each disease
    for disease in candidate_diseases:
        orpha_code = disease.get('ORPHAcode')
        genes = tu.tools.Orphanet_get_genes(
            operation="get_genes",
            orpha_code=orpha_code
        )
        disease['genes'] = genes.get('data', {}).get('genes', [])
    
    return deduplicate_and_rank(candidate_diseases)
```

### 2.2 OMIM Cross-Reference (NEW TOOLS)

```python
def cross_reference_omim(tu, orphanet_diseases, gene_symbols):
    """Get OMIM details for diseases and genes."""
    omim_data = {}
    
    # Search OMIM for each disease/gene
    for gene in gene_symbols:
        search_result = tu.tools.OMIM_search(
            operation="search",
            query=gene,
            limit=5
        )
        if search_result.get('status') == 'success':
            for entry in search_result['data'].get('entries', []):
                mim_number = entry.get('mimNumber')
                
                # Get detailed entry
                details = tu.tools.OMIM_get_entry(
                    operation="get_entry",
                    mim_number=str(mim_number)
                )
                
                # Get clinical synopsis (phenotype features)
                synopsis = tu.tools.OMIM_get_clinical_synopsis(
                    operation="get_clinical_synopsis",
                    mim_number=str(mim_number)
                )
                
                omim_data[gene] = {
                    'mim_number': mim_number,
                    'details': details.get('data', {}),
                    'clinical_synopsis': synopsis.get('data', {})
                }
    
    return omim_data
```

### 2.3 DisGeNET Gene-Disease Associations (NEW TOOLS)

```python
def get_gene_disease_associations(tu, gene_symbols):
    """Get gene-disease associations from DisGeNET."""
    associations = {}
    
    for gene in gene_symbols:
        # Get diseases associated with gene
        result = tu.tools.DisGeNET_search_gene(
            operation="search_gene",
            gene=gene,
            limit=20
        )
        
        if result.get('status') == 'success':
            associations[gene] = result['data'].get('associations', [])
    
    return associations

def get_disease_genes_disgenet(tu, disease_name):
    """Get all genes associated with a disease."""
    result = tu.tools.DisGeNET_search_disease(
        operation="search_disease",
        disease=disease_name,
        limit=30
    )
    return result.get('data', {}).get('associations', [])
```

### 2.4 Phenotype Overlap Scoring

| Match Level | Score | Criteria |
|-------------|-------|----------|
| **Excellent** | >80% | Most core + variable features match |
| **Good** | 60-80% | Core features match, some variable |
| **Possible** | 40-60% | Some overlap, needs consideration |
| **Unlikely** | <40% | Poor phenotype fit |

### 2.5 Output for Report

```markdown
## 2. Differential Diagnosis

### Top Candidate Diseases (Ranked by Phenotype Match)

| Rank | Disease | ORPHA | OMIM | Match | Inheritance | Key Gene(s) |
|------|---------|-------|------|-------|-------------|-------------|
| 1 | Marfan syndrome | 558 | 154700 | 85% | AD | FBN1 |
| 2 | Loeys-Dietz syndrome | 60030 | 609192 | 72% | AD | TGFBR1, TGFBR2 |
| 3 | Ehlers-Danlos, vascular | 286 | 130050 | 65% | AD | COL3A1 |
| 4 | Homocystinuria | 394 | 236200 | 58% | AR | CBS |

### DisGeNET Gene-Disease Evidence

| Gene | Associated Diseases | GDA Score | Evidence |
|------|---------------------|-----------|----------|
| FBN1 | Marfan syndrome, MASS phenotype | 0.95 | ★★★ Curated |
| TGFBR1 | Loeys-Dietz syndrome | 0.89 | ★★★ Curated |
| COL3A1 | vascular EDS | 0.91 | ★★★ Curated |

*Source: DisGeNET via `DisGeNET_search_gene`*

### Disease Details

#### 1. Marfan Syndrome (★★★)

**ORPHA**: 558 | **OMIM**: 154700 | **Prevalence**: 1-5/10,000

**Phenotype Match Analysis**:
| Patient Feature | Disease Feature | Match |
|-----------------|-----------------|-------|
| Tall stature | Present in 95% | ✓ |
| Arachnodactyly | Present in 90% | ✓ |
| Joint hypermobility | Present in 85% | ✓ |
| Cardiac murmur | Aortic root dilation (70%) | Partial |

**OMIM Clinical Synopsis** (via `OMIM_get_clinical_synopsis`):
- **Cardiovascular**: Aortic root dilation, mitral valve prolapse
- **Skeletal**: Scoliosis, pectus excavatum, tall stature
- **Ocular**: Ectopia lentis, myopia

**Diagnostic Criteria**: Ghent nosology (2010)
- Aortic root dilation/dissection + FBN1 mutation = Diagnosis
- Without genetic testing: systemic score ≥7 + ectopia lentis

**Inheritance**: Autosomal dominant (25% de novo)

*Source: Orphanet via `Orphanet_get_disease`, OMIM via `OMIM_get_entry`, DisGeNET*
```

---

## Phase 3: Gene Panel Identification

### 3.1 Extract Disease Genes

```python
def build_gene_panel(tu, candidate_diseases):
    """Build prioritized gene panel from candidate diseases."""
    genes = {}
    
    for disease in candidate_diseases:
        for gene in disease['genes']:
            if gene not in genes:
                genes[gene] = {
                    'symbol': gene,
                    'diseases': [],
                    'evidence_level': 'unknown'
                }
            genes[gene]['diseases'].append(disease['name'])
    
    return genes
```

### 3.1.1 ClinGen Gene-Disease Validity Check (NEW)

**Critical**: Always verify gene-disease validity through ClinGen before including in panel.

```python
def get_clingen_gene_evidence(tu, gene_symbol):
    """
    Get ClinGen gene-disease validity and dosage sensitivity.
    ESSENTIAL for rare disease gene panel prioritization.
    """
    
    # 1. Gene-disease validity classification
    validity = tu.tools.ClinGen_search_gene_validity(gene=gene_symbol)
    
    validity_levels = []
    diseases_with_validity = []
    if validity.get('data'):
        for entry in validity.get('data', []):
            validity_levels.append(entry.get('Classification'))
            diseases_with_validity.append({
                'disease': entry.get('Disease Label'),
                'mondo_id': entry.get('Disease ID (MONDO)'),
                'classification': entry.get('Classification'),
                'inheritance': entry.get('Inheritance')
            })
    
    # 2. Dosage sensitivity (critical for CNV interpretation)
    dosage = tu.tools.ClinGen_search_dosage_sensitivity(gene=gene_symbol)
    
    hi_score = None
    ts_score = None
    if dosage.get('data'):
        for entry in dosage.get('data', []):
            hi_score = entry.get('Haploinsufficiency Score')
            ts_score = entry.get('Triplosensitivity Score')
            break
    
    # 3. Clinical actionability (return of findings context)
    actionability = tu.tools.ClinGen_search_actionability(gene=gene_symbol)
    is_actionable = (actionability.get('adult_count', 0) > 0 or 
                     actionability.get('pediatric_count', 0) > 0)
    
    # Determine best evidence level
    level_priority = ['Definitive', 'Strong', 'Moderate', 'Limited', 'Disputed', 'Refuted']
    best_level = 'Not curated'
    for level in level_priority:
        if level in validity_levels:
            best_level = level
            break
    
    return {
        'gene': gene_symbol,
        'evidence_level': best_level,
        'diseases_curated': diseases_with_validity,
        'haploinsufficiency_score': hi_score,
        'triplosensitivity_score': ts_score,
        'is_actionable': is_actionable,
        'include_in_panel': best_level in ['Definitive', 'Strong', 'Moderate']
    }

def prioritize_genes_with_clingen(tu, gene_list):
    """Prioritize genes using ClinGen evidence levels."""
    
    prioritized = []
    for gene in gene_list:
        evidence = get_clingen_gene_evidence(tu, gene)
        
        # Score based on ClinGen classification
        score = 0
        if evidence['evidence_level'] == 'Definitive':
            score = 5
        elif evidence['evidence_level'] == 'Strong':
            score = 4
        elif evidence['evidence_level'] == 'Moderate':
            score = 3
        elif evidence['evidence_level'] == 'Limited':
            score = 1
        # Disputed/Refuted get 0
        
        # Bonus for haploinsufficiency score 3
        if evidence['haploinsufficiency_score'] == '3':
            score += 1
        
        # Bonus for actionability
        if evidence['is_actionable']:
            score += 1
        
        prioritized.append({
            **evidence,
            'priority_score': score
        })
    
    # Sort by priority score
    return sorted(prioritized, key=lambda x: x['priority_score'], reverse=True)
```

**ClinGen Classification Impact on Panel**:
| Classification | Include in Panel? | Priority |
|----------------|-------------------|----------|
| **Definitive** | YES - mandatory | Highest |
| **Strong** | YES - highly recommended | High |
| **Moderate** | YES | Medium |
| **Limited** | Include but flag | Low |
| **Disputed** | Exclude or separate | Avoid |
| **Refuted** | EXCLUDE | Do not test |
| **Not curated** | Use other evidence | Variable |

### 3.2 Gene Prioritization Criteria

| Priority | Criteria | Points |
|----------|----------|--------|
| **Tier 1** | Gene causes #1 ranked disease | +5 |
| **Tier 2** | Gene causes multiple candidates | +3 |
| **Tier 3** | ClinGen "Definitive" evidence | +3 |
| **Tier 4** | Expressed in affected tissue | +2 |
| **Tier 5** | Constraint score pLI >0.9 | +1 |

### 3.3 Expression Validation

```python
def validate_expression(tu, gene_symbol, affected_tissue):
    """Check if gene is expressed in relevant tissue."""
    # Get Ensembl ID
    gene_info = tu.tools.MyGene_query_genes(q=gene_symbol, species="human")
    ensembl_id = gene_info.get('ensembl', {}).get('gene')
    
    # Check GTEx expression
    expression = tu.tools.GTEx_get_median_gene_expression(
        gencode_id=f"{ensembl_id}.latest"
    )
    
    return expression.get(affected_tissue, 0) > 1  # TPM > 1
```

### 3.4 Output for Report

```markdown
## 3. Recommended Gene Panel

### 3.1 Prioritized Genes for Testing

| Priority | Gene | Diseases | Evidence | Constraint (pLI) | Expression |
|----------|------|----------|----------|------------------|------------|
| ★★★ | FBN1 | Marfan syndrome | Definitive | 1.00 | Heart, aorta |
| ★★★ | TGFBR1 | Loeys-Dietz 1 | Definitive | 0.98 | Ubiquitous |
| ★★★ | TGFBR2 | Loeys-Dietz 2 | Definitive | 0.99 | Ubiquitous |
| ★★☆ | COL3A1 | EDS vascular | Definitive | 1.00 | Connective tissue |
| ★☆☆ | CBS | Homocystinuria | Definitive | 0.00 | Liver |

### 3.2 Panel Design Recommendation

**Minimum Panel** (high yield): FBN1, TGFBR1, TGFBR2, COL3A1
**Extended Panel** (+differential): Add CBS, SMAD3, ACTA2

**Testing Strategy**:
1. Start with FBN1 sequencing (highest pre-test probability)
2. If negative, proceed to full connective tissue panel
3. Consider WES if panel negative

*Source: ClinGen via gene-disease validity, GTEx expression*
```

---

## Phase 3.5: Expression & Tissue Context (ENHANCED)

### 3.5.1 Cell-Type Specific Expression (CELLxGENE)

```python
def get_cell_type_expression(tu, gene_symbol, affected_tissues):
    """Get single-cell expression to validate tissue relevance."""
    
    # Get expression across cell types
    expression = tu.tools.CELLxGENE_get_expression_data(
        gene=gene_symbol,
        tissue=affected_tissues[0] if affected_tissues else "all"
    )
    
    # Get cell type metadata
    cell_metadata = tu.tools.CELLxGENE_get_cell_metadata(
        gene=gene_symbol
    )
    
    # Identify high-expression cell types
    high_expression = [
        ct for ct in expression 
        if ct.get('mean_expression', 0) > 1.0  # TPM > 1
    ]
    
    return {
        'expression_data': expression,
        'high_expression_cells': high_expression,
        'total_cell_types': len(cell_metadata)
    }
```

**Why it matters**: Confirms candidate genes are expressed in disease-relevant tissues/cells.

### 3.5.2 Regulatory Context (ChIPAtlas)

```python
def get_regulatory_context(tu, gene_symbol):
    """Get transcription factor binding for candidate genes."""
    
    # Search for TF binding near gene
    tf_binding = tu.tools.ChIPAtlas_enrichment_analysis(
        gene=gene_symbol,
        cell_type="all"
    )
    
    # Get specific binding peaks
    peaks = tu.tools.ChIPAtlas_get_peak_data(
        gene=gene_symbol,
        experiment_type="TF"
    )
    
    return {
        'transcription_factors': tf_binding,
        'regulatory_peaks': peaks
    }
```

**Why it matters**: Identifies regulatory mechanisms that may be disrupted in disease.

### 3.5.3 Output for Report

```markdown
## 3.5 Expression & Regulatory Context

### Cell-Type Specific Expression (CELLxGENE)

| Gene | Top Expressing Cell Types | Expression Level | Tissue Relevance |
|------|---------------------------|------------------|------------------|
| FBN1 | Fibroblasts, Smooth muscle | High (TPM=45) | ✓ Connective tissue |
| TGFBR1 | Endothelial, Fibroblasts | Medium (TPM=12) | ✓ Vascular |
| COL3A1 | Fibroblasts, Myofibroblasts | Very High (TPM=120) | ✓ Connective tissue |

**Interpretation**: All top candidate genes show high expression in disease-relevant cell types (connective tissue, vascular cells), supporting their candidacy.

### Regulatory Context (ChIPAtlas)

| Gene | Key TF Regulators | Regulatory Significance |
|------|-------------------|------------------------|
| FBN1 | TGFβ pathway (SMAD2/3), AP-1 | TGFβ-responsive |
| TGFBR1 | STAT3, NF-κB | Inflammation-responsive |

*Source: CELLxGENE Census, ChIPAtlas*
```

---

## Phase 3.6: Pathway Analysis (NEW)

### 3.6.1 KEGG Pathway Context

```python
def get_pathway_context(tu, gene_symbols):
    """Get pathway context for candidate genes."""
    
    pathways = {}
    for gene in gene_symbols:
        # Search KEGG for gene
        kegg_genes = tu.tools.kegg_find_genes(query=f"hsa:{gene}")
        
        if kegg_genes:
            # Get pathway membership
            gene_info = tu.tools.kegg_get_gene_info(gene_id=kegg_genes[0]['id'])
            pathways[gene] = gene_info.get('pathways', [])
    
    return pathways
```

### 3.6.2 Protein-Protein Interactions (IntAct)

```python
def get_protein_interactions(tu, gene_symbol):
    """Get interaction partners for candidate genes."""
    
    # Search IntAct for interactions
    interactions = tu.tools.intact_search_interactions(
        query=gene_symbol,
        species="human"
    )
    
    # Get interaction network
    network = tu.tools.intact_get_interaction_network(
        gene=gene_symbol,
        depth=1  # Direct interactors only
    )
    
    return {
        'interactions': interactions,
        'network': network,
        'interactor_count': len(interactions)
    }
```

### 3.6.3 Output for Report

```markdown
## 3.6 Pathway & Network Context

### KEGG Pathways

| Gene | Key Pathways | Biological Process |
|------|--------------|-------------------|
| FBN1 | ECM-receptor interaction (hsa04512) | Extracellular matrix |
| TGFBR1/2 | TGF-beta signaling (hsa04350) | Cell signaling |
| COL3A1 | Focal adhesion (hsa04510) | Cell-matrix adhesion |

### Shared Pathway Analysis

**Convergent pathways** (≥2 candidate genes):
- TGF-beta signaling pathway: FBN1, TGFBR1, TGFBR2, SMAD3
- ECM organization: FBN1, COL3A1

**Interpretation**: Candidate genes converge on TGF-beta signaling and extracellular matrix pathways, consistent with connective tissue disorder etiology.

### Protein-Protein Interactions (IntAct)

| Gene | Direct Interactors | Notable Partners |
|------|-------------------|------------------|
| FBN1 | 42 | LTBP1, TGFB1, ADAMTS10 |
| TGFBR1 | 68 | TGFBR2, SMAD2, SMAD3 |

*Source: KEGG, IntAct, Reactome*
```

---

## Phase 4: Variant Interpretation (If Provided)

### 4.1 ClinVar Lookup

```python
def interpret_variant(tu, variant_hgvs):
    """Get ClinVar interpretation for variant."""
    result = tu.tools.ClinVar_search_variants(query=variant_hgvs)
    
    return {
        'clinvar_id': result.get('id'),
        'classification': result.get('clinical_significance'),
        'review_status': result.get('review_status'),
        'conditions': result.get('conditions'),
        'last_evaluated': result.get('last_evaluated')
    }
```

### 4.2 Population Frequency

```python
def check_population_frequency(tu, variant_id):
    """Get gnomAD allele frequency."""
    freq = tu.tools.gnomAD_get_variant_frequencies(variant_id=variant_id)
    
    # Interpret rarity
    if freq['allele_frequency'] < 0.00001:
        rarity = "Ultra-rare"
    elif freq['allele_frequency'] < 0.0001:
        rarity = "Rare"
    elif freq['allele_frequency'] < 0.01:
        rarity = "Low frequency"
    else:
        rarity = "Common (likely benign)"
    
    return freq, rarity
```

### 4.3 Computational Pathogenicity Prediction (ENHANCED)

Use state-of-the-art prediction tools for VUS interpretation:

```python
def comprehensive_vus_prediction(tu, variant_info):
    """
    Combine multiple prediction tools for VUS classification.
    Critical for rare disease variants not in ClinVar.
    """
    predictions = {}
    
    # 1. CADD - Deleteriousness (NEW API)
    cadd = tu.tools.CADD_get_variant_score(
        chrom=variant_info['chrom'],
        pos=variant_info['pos'],
        ref=variant_info['ref'],
        alt=variant_info['alt'],
        version="GRCh38-v1.7"
    )
    if cadd.get('status') == 'success':
        predictions['cadd'] = {
            'score': cadd['data'].get('phred_score'),
            'interpretation': cadd['data'].get('interpretation'),
            'acmg': 'PP3' if cadd['data'].get('phred_score', 0) >= 20 else 'neutral'
        }
    
    # 2. AlphaMissense - DeepMind pathogenicity (NEW)
    if variant_info.get('uniprot_id') and variant_info.get('aa_change'):
        am = tu.tools.AlphaMissense_get_variant_score(
            uniprot_id=variant_info['uniprot_id'],
            variant=variant_info['aa_change']  # e.g., "E1541K"
        )
        if am.get('status') == 'success' and am.get('data'):
            classification = am['data'].get('classification')
            predictions['alphamissense'] = {
                'score': am['data'].get('pathogenicity_score'),
                'classification': classification,
                'acmg': 'PP3 (strong)' if classification == 'pathogenic' else (
                    'BP4 (strong)' if classification == 'benign' else 'neutral'
                )
            }
    
    # 3. EVE - Evolutionary prediction (NEW)
    eve = tu.tools.EVE_get_variant_score(
        chrom=variant_info['chrom'],
        pos=variant_info['pos'],
        ref=variant_info['ref'],
        alt=variant_info['alt']
    )
    if eve.get('status') == 'success':
        eve_scores = eve['data'].get('eve_scores', [])
        if eve_scores:
            predictions['eve'] = {
                'score': eve_scores[0].get('eve_score'),
                'classification': eve_scores[0].get('classification'),
                'acmg': 'PP3' if eve_scores[0].get('eve_score', 0) > 0.5 else 'BP4'
            }
    
    # 4. SpliceAI - Splice variant prediction (NEW)
    # Use for intronic, synonymous, or exonic variants near splice sites
    variant_str = f"chr{variant_info['chrom']}-{variant_info['pos']}-{variant_info['ref']}-{variant_info['alt']}"
    splice = tu.tools.SpliceAI_predict_splice(
        variant=variant_str,
        genome="38"
    )
    if splice.get('data'):
        max_score = splice['data'].get('max_delta_score', 0)
        interpretation = splice['data'].get('interpretation', '')
        
        if max_score >= 0.8:
            splice_acmg = 'PP3 (strong) - high splice impact'
        elif max_score >= 0.5:
            splice_acmg = 'PP3 (moderate) - splice impact'
        elif max_score >= 0.2:
            splice_acmg = 'PP3 (supporting) - possible splice effect'
        else:
            splice_acmg = 'BP7 (if synonymous) - no splice impact'
        
        predictions['spliceai'] = {
            'max_delta_score': max_score,
            'interpretation': interpretation,
            'scores': splice['data'].get('scores', []),
            'acmg': splice_acmg
        }
    
    # Consensus for PP3/BP4
    damaging = sum(1 for p in predictions.values() if 'PP3' in p.get('acmg', ''))
    benign = sum(1 for p in predictions.values() if 'BP4' in p.get('acmg', ''))
    
    return {
        'predictions': predictions,
        'consensus': {
            'damaging_count': damaging,
            'benign_count': benign,
            'pp3_applicable': damaging >= 2 and benign == 0,
            'bp4_applicable': benign >= 2 and damaging == 0
        }
    }
```

### 4.4 ACMG Classification Criteria

| Evidence Type | Criteria | Weight |
|---------------|----------|--------|
| **PVS1** | Null variant in gene where LOF is mechanism | Very Strong |
| **PS1** | Same amino acid change as established pathogenic | Strong |
| **PM2** | Absent from population databases | Moderate |
| **PP3** | Computational evidence supports deleterious (AlphaMissense, CADD, EVE, SpliceAI) | Supporting |
| **BA1** | Allele frequency >5% | Benign standalone |

**Enhanced PP3 Evidence** (NEW):
- **AlphaMissense pathogenic** (>0.564) = Strong PP3 support (~90% accuracy)
- **CADD ≥20** + **EVE >0.5** = Multiple concordant predictions
- Agreement from 2+ predictors strengthens PP3 evidence

### 4.5 Output for Report

```markdown
## 4. Variant Interpretation

### 4.1 Variant: FBN1 c.4621G>A (p.Glu1541Lys)

| Property | Value | Interpretation |
|----------|-------|----------------|
| Gene | FBN1 | Marfan syndrome gene |
| Consequence | Missense | Amino acid change |
| ClinVar | VUS | Uncertain significance |
| gnomAD AF | 0.000004 | Ultra-rare (PM2) |

### 4.2 Computational Predictions (NEW)

| Predictor | Score | Classification | ACMG Support |
|-----------|-------|----------------|--------------|
| **AlphaMissense** | 0.78 | Pathogenic | PP3 (strong) |
| **CADD PHRED** | 28.5 | Top 0.1% deleterious | PP3 |
| **EVE** | 0.72 | Likely pathogenic | PP3 |

**Consensus**: 3/3 predictors concordant damaging → **Strong PP3 support**

*Source: AlphaMissense, CADD API, EVE via Ensembl VEP*

### 4.3 ACMG Evidence Summary

| Criterion | Evidence | Strength |
|-----------|----------|----------|
| PM2 | Absent from gnomAD (AF < 0.00001) | Moderate |
| PP3 | AlphaMissense + CADD + EVE concordant | Supporting (strong) |
| PP4 | Phenotype highly specific for Marfan | Supporting |
| PS4 | Multiple affected family members | Strong |

**Preliminary Classification**: Likely Pathogenic (1 Strong + 1 Moderate + 2 Supporting)

*Source: ClinVar, gnomAD, AlphaMissense, CADD, EVE*
```

---

## Phase 5: Structure Analysis for VUS

### 5.1 When to Perform Structure Analysis

Perform when:
- Variant is VUS or conflicting interpretations
- Missense variant in critical domain
- Novel variant not in databases
- Additional evidence needed for classification

### 5.2 Structure Prediction (NVIDIA NIM)

```python
def analyze_variant_structure(tu, protein_sequence, variant_position):
    """Predict structure and analyze variant impact."""
    
    # Predict structure with AlphaFold2
    structure = tu.tools.NvidiaNIM_alphafold2(
        sequence=protein_sequence,
        algorithm="mmseqs2",
        relax_prediction=False
    )
    
    # Extract pLDDT at variant position
    variant_plddt = get_residue_plddt(structure, variant_position)
    
    # Check if in structured region
    confidence = "High" if variant_plddt > 70 else "Low"
    
    return {
        'structure': structure,
        'variant_plddt': variant_plddt,
        'confidence': confidence
    }
```

### 5.3 Domain Impact Assessment

```python
def assess_domain_impact(tu, uniprot_id, variant_position):
    """Check if variant affects functional domain."""
    
    # Get domain annotations
    domains = tu.tools.InterPro_get_protein_domains(accession=uniprot_id)
    
    for domain in domains:
        if domain['start'] <= variant_position <= domain['end']:
            return {
                'in_domain': True,
                'domain_name': domain['name'],
                'domain_function': domain['description']
            }
    
    return {'in_domain': False}
```

### 5.4 Output for Report

```markdown
## 5. Structural Analysis

### 5.1 Structure Prediction

**Method**: AlphaFold2 via NVIDIA NIM
**Protein**: Fibrillin-1 (FBN1)
**Sequence Length**: 2,871 amino acids

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Mean pLDDT | 85.3 | High confidence overall |
| Variant position pLDDT | 92.1 | Very high confidence |
| Nearby domain | cbEGF-like domain 23 | Calcium-binding |

### 5.2 Variant Location Analysis

**Variant**: p.Glu1541Lys

| Feature | Finding | Impact |
|---------|---------|--------|
| Domain | cbEGF-like domain 23 | Critical for calcium binding |
| Conservation | 100% conserved across vertebrates | High constraint |
| Structural role | Calcium coordination residue | Likely destabilizing |
| Nearby pathogenic | p.Glu1540Lys (Pathogenic) | Adjacent residue |

### 5.3 Structural Interpretation

The variant p.Glu1541Lys:
1. **Located in cbEGF domain** - These domains are critical for fibrillin-1 function
2. **Glutamate → Lysine** - Charge reversal (negative to positive)
3. **Calcium binding** - Glutamate at this position coordinates Ca2+
4. **Adjacent pathogenic variant** - p.Glu1540Lys is classified Pathogenic

**Structural Evidence**: Strong support for pathogenicity (PM1 - critical domain)

*Source: NVIDIA NIM via `NvidiaNIM_alphafold2`, InterPro*
```

---

## Phase 6: Literature Evidence (NEW)

### 6.1 Published Literature (PubMed)

```python
def search_disease_literature(tu, disease_name, genes):
    """Search for relevant published literature."""
    
    # Disease-specific search
    disease_papers = tu.tools.PubMed_search_articles(
        query=f'"{disease_name}" AND (genetics OR mutation OR variant)',
        limit=20
    )
    
    # Gene-specific searches
    gene_papers = []
    for gene in genes[:5]:  # Top 5 genes
        papers = tu.tools.PubMed_search_articles(
            query=f'"{gene}" AND rare disease AND pathogenic',
            limit=10
        )
        gene_papers.extend(papers)
    
    return {
        'disease_literature': disease_papers,
        'gene_literature': gene_papers
    }
```

### 6.2 Preprint Literature (BioRxiv/MedRxiv)

```python
def search_preprints(tu, disease_name, genes):
    """Search preprints for cutting-edge findings."""
    
    # BioRxiv search
    biorxiv = tu.tools.BioRxiv_search_preprints(
        query=f"{disease_name} genetics",
        limit=10
    )
    
    # ArXiv for computational methods
    arxiv = tu.tools.ArXiv_search_papers(
        query=f"rare disease diagnosis {' OR '.join(genes[:3])}",
        category="q-bio",
        limit=5
    )
    
    return {
        'biorxiv': biorxiv,
        'arxiv': arxiv
    }
```

### 6.3 Citation Analysis (OpenAlex)

```python
def analyze_citations(tu, key_papers):
    """Analyze citation network for key papers."""
    
    citation_analysis = []
    for paper in key_papers[:5]:
        # Get citation data
        work = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        if work:
            citation_analysis.append({
                'title': paper['title'],
                'citations': work[0].get('cited_by_count', 0),
                'year': work[0].get('publication_year')
            })
    
    return citation_analysis
```

### 6.4 Output for Report

```markdown
## 6. Literature Evidence

### 6.1 Key Published Studies

| PMID | Title | Year | Citations | Relevance |
|------|-------|------|-----------|-----------|
| 32123456 | FBN1 variants in Marfan syndrome... | 2023 | 45 | Direct |
| 31987654 | TGF-beta signaling in connective... | 2022 | 89 | Pathway |
| 30876543 | Novel diagnostic criteria for... | 2021 | 156 | Diagnostic |

### 6.2 Recent Preprints (Not Yet Peer-Reviewed)

| Source | Title | Posted | Relevance |
|--------|-------|--------|-----------|
| BioRxiv | Novel FBN1 splice variant causes... | 2024-01 | Case report |
| MedRxiv | Machine learning for Marfan... | 2024-02 | Diagnostic |

**⚠️ Note**: Preprints have not undergone peer review. Use with caution.

### 6.3 Evidence Summary

| Evidence Type | Count | Strength |
|---------------|-------|----------|
| Case reports | 12 | Supporting |
| Functional studies | 5 | Strong |
| Clinical trials | 2 | Strong |
| Reviews | 8 | Context |

*Source: PubMed, BioRxiv, OpenAlex*
```

---

## Report Template

**File**: `[PATIENT_ID]_rare_disease_report.md`

```markdown
# Rare Disease Diagnostic Report

**Patient ID**: [ID] | **Date**: [Date] | **Status**: In Progress

---

## Executive Summary
[Researching...]

---

## 1. Phenotype Analysis
### 1.1 Standardized HPO Terms
[Researching...]
### 1.2 Key Clinical Features
[Researching...]

---

## 2. Differential Diagnosis
### 2.1 Ranked Candidate Diseases
[Researching...]
### 2.2 Disease Details
[Researching...]

---

## 3. Recommended Gene Panel
### 3.1 Prioritized Genes
[Researching...]
### 3.2 Testing Strategy
[Researching...]

---

## 4. Variant Interpretation (if applicable)
### 4.1 Variant Details
[Researching...]
### 4.2 ACMG Classification
[Researching...]

---

## 5. Structural Analysis (if applicable)
### 5.1 Structure Prediction
[Researching...]
### 5.2 Variant Impact
[Researching...]

---

## 6. Clinical Recommendations
### 6.1 Diagnostic Next Steps
[Researching...]
### 6.2 Specialist Referrals
[Researching...]
### 6.3 Family Screening
[Researching...]

---

## 7. Data Gaps & Limitations
[Researching...]

---

## 8. Data Sources
[Will be populated as research progresses...]
```

---

## Evidence Grading

| Tier | Symbol | Criteria | Example |
|------|--------|----------|---------|
| **T1** | ★★★ | Phenotype match >80% + gene match | Marfan with FBN1 mutation |
| **T2** | ★★☆ | Phenotype match 60-80% OR likely pathogenic variant | Good phenotype fit |
| **T3** | ★☆☆ | Phenotype match 40-60% OR VUS in candidate gene | Possible diagnosis |
| **T4** | ☆☆☆ | Phenotype <40% OR uncertain gene | Low probability |

---

## Completeness Checklist

### Phase 1: Phenotype
- [ ] All symptoms converted to HPO terms
- [ ] Core vs. variable features distinguished
- [ ] Age of onset documented
- [ ] Family history noted

### Phase 2: Disease Matching
- [ ] ≥5 candidate diseases identified (or all matching)
- [ ] Phenotype overlap % calculated
- [ ] Inheritance patterns noted
- [ ] ORPHA and OMIM IDs provided

### Phase 3: Gene Panel
- [ ] ≥5 genes prioritized (or all from top diseases)
- [ ] Evidence level for each gene (ClinGen)
- [ ] Expression validation performed
- [ ] Testing strategy recommended

### Phase 4: Variant Interpretation (if applicable)
- [ ] ClinVar classification retrieved
- [ ] gnomAD frequency checked
- [ ] ACMG criteria applied
- [ ] Classification justified

### Phase 5: Structure Analysis (if applicable)
- [ ] Structure predicted (if VUS)
- [ ] pLDDT confidence reported
- [ ] Domain impact assessed
- [ ] Structural evidence summarized

### Phase 6: Recommendations
- [ ] ≥3 next steps listed
- [ ] Specialist referrals suggested
- [ ] Family screening addressed

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `Orphanet_search_by_hpo` | `OMIM_search` | PubMed phenotype search |
| `ClinVar_get_variant` | `gnomAD_get_variant` | VEP annotation |
| `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | UniProt features |
| `GTEx_expression` | `HPA_expression` | Tissue-specific literature |
| `gnomAD_get_variant` | `ExAC_frequencies` | 1000 Genomes |

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
