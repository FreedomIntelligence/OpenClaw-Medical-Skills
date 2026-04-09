# tooluniverse-cancer-variant-interpretation

> Provide comprehensive clinical interpretation of somatic mutations in cancer. Given a gene symbol + variant (e.g., EGFR L858R, BRAF V600E) and optional cancer type, performs multi-database analysis covering clinical evidence (CIViC), mutation prevalence (cBioPortal), therapeutic associations (OpenTargets, ChEMBL, FDA), resistance mechanisms, clinical trials, prognostic impact, and pathway context. Generates an evidence-graded markdown report with actionable recommendations for precision oncology. Use when oncologists, molecular tumor boards, or researchers ask about treatment options for specific cancer mutations, resistance mechanisms, or clinical trial matching.

# Cancer Variant Interpretation for Precision Oncology

Comprehensive clinical interpretation of somatic mutations in cancer. Transforms a gene + variant input into an actionable precision oncology report covering clinical evidence, therapeutic options, resistance mechanisms, clinical trials, and prognostic implications.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Evidence-graded** - Every recommendation has an evidence tier (T1-T4)
3. **Actionable output** - Prioritized treatment options, not data dumps
4. **Clinical focus** - Answer "what should we treat with?" not "what databases exist?"
5. **Resistance-aware** - Always check for known resistance mechanisms
6. **Cancer-type specific** - Tailor all recommendations to the patient's cancer type when provided
7. **Source-referenced** - Every statement must cite the tool/database source
8. **English-first queries** - Always use English terms in tool calls (gene names, drug names, cancer types), even if the user writes in another language. Respond in the user's language

---

## When to Use

Apply when user asks:
- "What treatments exist for EGFR L858R in lung cancer?"
- "Patient has BRAF V600E melanoma - what are the options?"
- "Is KRAS G12C targetable?"
- "Patient progressed on osimertinib - what's next?"
- "What clinical trials are available for PIK3CA E545K?"
- "Interpret this somatic mutation: TP53 R273H"
- "Molecular tumor board: EGFR exon 19 deletion, NSCLC"

---

## Input Parsing

**Required**: Gene symbol + variant notation
**Optional**: Cancer type (improves specificity)

### Accepted Input Formats

| Format | Example | How to Parse |
|--------|---------|-------------|
| Gene + amino acid change | EGFR L858R | gene=EGFR, variant=L858R |
| Gene + HGVS protein | BRAF p.V600E | gene=BRAF, variant=V600E |
| Gene + exon notation | EGFR exon 19 deletion | gene=EGFR, variant=exon 19 deletion |
| Gene + fusion | EML4-ALK fusion | gene=ALK, variant=EML4-ALK |
| Gene + amplification | HER2 amplification | gene=ERBB2, variant=amplification |
| Full query with cancer | "EGFR L858R in lung adenocarcinoma" | gene=EGFR, variant=L858R, cancer=lung adenocarcinoma |

### Gene Symbol Normalization

Common aliases to resolve:
- HER2 -> ERBB2
- ALK -> ALK (but EML4-ALK is a fusion)
- PD-L1 -> CD274
- VEGF -> VEGFA

---

## Phase 0: Tool Parameter Verification (CRITICAL)

**BEFORE calling ANY tool for the first time**, verify its parameters.

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblID` | `ensemblId` (camelCase) |
| `OpenTargets_get_drug_chembId_by_generic_name` | `genericName` | `drugName` |
| `OpenTargets_target_disease_evidence` | `ensemblID` | `ensemblId` + `efoId` |
| `MyGene_query_genes` | `q` | `query` |
| `search_clinical_trials` | `disease`, `biomarker` | `condition`, `query_term` (required) |
| `civic_get_variants_by_gene` | `gene_symbol` | `gene_id` (CIViC numeric ID) |
| `drugbank_*` | any 3 params | ALL 4 required: `query`, `case_sensitive`, `exact_match`, `limit` |
| `ChEMBL_get_drug_mechanisms` | `chembl_id` | `drug_chembl_id__exact` |
| `ensembl_lookup_gene` | no species | `species='homo_sapiens'` is REQUIRED for Ensembl IDs |

---

## Workflow Overview

```
Input: Gene symbol + Variant notation + Optional cancer type

Phase 1: Gene Disambiguation & ID Resolution
  - Resolve gene to Ensembl ID, UniProt accession, Entrez ID
  - Get gene function, pathways, protein domains
  - Identify cancer type EFO ID (if cancer type provided)

Phase 2: Clinical Variant Evidence (CIViC)
  - Find gene in CIViC (via Entrez ID matching)
  - Get all variants for the gene
  - Match specific variant
  - Retrieve evidence items (predictive, prognostic, diagnostic)
  - Get CIViC assertions

Phase 3: Mutation Prevalence (cBioPortal)
  - Frequency across cancer studies
  - Co-occurring mutations
  - Cancer type distribution

Phase 4: Therapeutic Associations (OpenTargets + ChEMBL + FDA + DrugBank)
  - FDA-approved targeted therapies
  - Clinical trial drugs (phase 2-3)
  - Drug mechanisms of action
  - Drug label information
  - Combination therapies

Phase 5: Resistance Mechanisms
  - Known resistance variants (CIViC, literature)
  - Bypass pathway analysis (Reactome)
  - Secondary mutations

Phase 6: Clinical Trials
  - Active trials recruiting for this mutation
  - Trial phase and status
  - Eligibility criteria

Phase 7: Prognostic Impact & Pathway Context
  - Survival associations (literature)
  - Pathway context (Reactome)
  - Expression data (GTEx)
  - Literature evidence (PubMed)

Phase 8: Report Synthesis
  - Executive summary
  - Clinical actionability score
  - Treatment recommendations (prioritized)
  - Completeness checklist
```

---

## Phase 1: Gene Disambiguation & ID Resolution

**Goal**: Resolve gene symbol to all cross-database identifiers needed for downstream queries.

### 1.1 MyGene ID Resolution (PRIMARY)

```python
def resolve_gene_ids(tu, gene_symbol):
    """Resolve gene symbol to Ensembl, Entrez, UniProt IDs."""
    result = tu.tools.MyGene_query_genes(query=gene_symbol, species='human')

    hits = result.get('hits', [])
    # Take the top hit where symbol matches exactly
    gene_hit = None
    for hit in hits:
        if hit.get('symbol', '').upper() == gene_symbol.upper():
            gene_hit = hit
            break
    if not gene_hit and hits:
        gene_hit = hits[0]

    ids = {
        'symbol': gene_hit.get('symbol'),
        'entrez_id': gene_hit.get('entrezgene'),
        'ensembl_id': gene_hit.get('ensembl', {}).get('gene'),
        'name': gene_hit.get('name'),
    }
    return ids
```

**Response structure**: `{took, total, max_score, hits: [{_id, _score, ensembl: {gene}, entrezgene, name, symbol}]}`

### 1.2 UniProt Accession

```python
def get_uniprot_id(tu, gene_symbol):
    """Get UniProt accession for gene."""
    result = tu.tools.UniProt_search(query=f'gene:{gene_symbol}', organism='human', limit=3)
    # Response: {total_results, returned, results: [{accession, id, protein_name, gene_names, organism, length}]}
    results = result.get('results', [])
    if results:
        return results[0].get('accession')
    return None
```

### 1.3 OpenTargets Target Resolution

```python
def get_opentargets_info(tu, gene_symbol):
    """Resolve gene to OpenTargets ensemblId and description."""
    result = tu.tools.OpenTargets_get_target_id_description_by_name(targetName=gene_symbol)
    # Response: {data: {search: {hits: [{id (ensemblId), name, description}]}}}
    hits = result.get('data', {}).get('search', {}).get('hits', [])
    # Match exact gene symbol
    for hit in hits:
        if hit.get('name', '').upper() == gene_symbol.upper():
            return hit
    return hits[0] if hits else None
```

### 1.4 Cancer Type EFO Resolution (if cancer type provided)

```python
def resolve_cancer_type(tu, cancer_type):
    """Resolve cancer type to EFO ID for OpenTargets queries."""
    result = tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName=cancer_type)
    # Response: {data: {search: {hits: [{id (efoId), name, description}]}}}
    hits = result.get('data', {}).get('search', {}).get('hits', [])
    return hits[0] if hits else None
```

### 1.5 Gene Function Context

```python
def get_gene_function(tu, uniprot_accession):
    """Get protein function from UniProt.
    NOTE: Returns a list of function description strings, NOT a dict.
    """
    result = tu.tools.UniProt_get_function_by_accession(accession=uniprot_accession)
    # Response type: list of strings
    # Example: ["Receptor tyrosine kinase binding ligands of the EGF family...", ...]
    return result
```

### 1.6 CIViC Gene ID Resolution

**IMPORTANT**: The `civic_search_genes` tool does NOT support name filtering in its GraphQL query. To find a gene in CIViC, either:
1. Paginate through results (inefficient, genes sorted alphabetically)
2. Use the Entrez ID from MyGene to construct a CIViC gene lookup

**Workaround**: Use `civic_search_genes` with `limit=100` and search the results client-side. For genes beyond alphabetical position ~100 (like EGFR, KRAS, TP53), you may need to use the CIViC gene ID if known from prior queries or documentation.

**Known CIViC Gene IDs** (for common cancer genes):
| Gene | CIViC Gene ID | Entrez ID |
|------|--------------|-----------|
| BRAF | 5 | 673 |
| ABL1 | 4 | 25 |
| ALK | 1 | 238 |

For other genes, the skill should attempt to find the gene through pagination or use alternative evidence sources (OpenTargets, cBioPortal) if CIViC lookup fails.

---

## Phase 2: Clinical Variant Evidence (CIViC)

**Goal**: Get clinical interpretations for the specific variant.

### 2.1 Get Gene Variants from CIViC

```python
def get_civic_variants(tu, civic_gene_id):
    """Get all variants for a gene in CIViC."""
    result = tu.tools.civic_get_variants_by_gene(gene_id=civic_gene_id, limit=200)
    # Response: {data: {gene: {variants: {nodes: [{id, name}]}}}}
    variants = result.get('data', {}).get('gene', {}).get('variants', {}).get('nodes', [])
    return variants
```

### 2.2 Match Specific Variant

```python
def find_variant_in_civic(variants, variant_name):
    """Find the specific variant in CIViC results."""
    # Normalize variant name (remove 'p.' prefix if present)
    normalized = variant_name.replace('p.', '').strip()

    for v in variants:
        if v.get('name', '').upper() == normalized.upper():
            return v

    # Partial match (e.g., "L858" matches "L858R")
    for v in variants:
        if normalized.upper() in v.get('name', '').upper():
            return v

    return None
```

### 2.3 Get Variant Details

```python
def get_variant_details(tu, variant_id):
    """Get detailed variant information from CIViC."""
    result = tu.tools.civic_get_variant(variant_id=variant_id)
    # Response: {data: {variant: {id, name}}}
    return result.get('data', {}).get('variant', {})
```

### 2.4 Get Molecular Profile Evidence

```python
def get_molecular_profile(tu, molecular_profile_id):
    """Get molecular profile details (for evidence items)."""
    result = tu.tools.civic_get_molecular_profile(molecular_profile_id=molecular_profile_id)
    # Response: {data: {molecularProfile: {id, name}}}
    return result.get('data', {}).get('molecularProfile', {})
```

### 2.5 CIViC Evidence Limitations and Fallback

The current CIViC tools return limited field sets from GraphQL. If CIViC data is sparse:

**Fallback to literature**: Use PubMed to search for "{gene} {variant} clinical significance cancer"
**Fallback to OpenTargets**: Use `OpenTargets_target_disease_evidence` for target-disease evidence

### Evidence Level Mapping

| CIViC Level | Tier | Meaning | Clinical Action |
|-------------|------|---------|-----------------|
| A | T1 (highest) | FDA-approved, guideline | Standard of care |
| B | T2 | Clinical evidence | Strong recommendation |
| C | T2 | Case study | Consider with caution |
| D | T3 | Preclinical | Research context only |
| E | T4 | Inferential | Computational evidence |

---

## Phase 3: Mutation Prevalence (cBioPortal)

**Goal**: Determine how common this mutation is across cancer types and studies.

### 3.1 Find Relevant Studies

```python
def find_cancer_studies(tu, cancer_keyword=None):
    """Find relevant cBioPortal studies."""
    result = tu.tools.cBioPortal_get_cancer_studies(limit=50)
    # Response: array of [{studyId, name, description, cancerTypeId, ...}]
    studies = result if isinstance(result, list) else result.get('data', [])

    if cancer_keyword:
        # Filter by cancer type keyword
        filtered = [s for s in studies
                    if cancer_keyword.lower() in str(s.get('name', '')).lower()
                    or cancer_keyword.lower() in str(s.get('cancerTypeId', '')).lower()]
        return filtered
    return studies
```

### 3.2 Get Mutation Data

```python
def get_mutation_prevalence(tu, gene_symbol, study_id):
    """Get mutation data for a gene in a specific study."""
    result = tu.tools.cBioPortal_get_mutations(study_id=study_id, gene_list=gene_symbol)
    # Response: {status: 'success', data: [{proteinChange, mutationType, sampleId, ...}]}
    # OR sometimes a plain list. Handle both formats:
    if isinstance(result, list):
        mutations = result
    elif isinstance(result, dict):
        mutations = result.get('data', []) if result.get('status') == 'success' else []
    else:
        mutations = []
    return mutations
```

### 3.3 Analyze Mutation Distribution

```python
def analyze_mutation_distribution(mutations, target_variant):
    """Count how many samples have the target variant vs. others."""
    from collections import Counter

    protein_changes = [m.get('proteinChange', '') for m in mutations]
    counts = Counter(protein_changes)

    total_mutated = len(mutations)
    target_count = sum(1 for m in mutations
                       if target_variant.upper() in str(m.get('proteinChange', '')).upper())

    return {
        'total_mutated_samples': total_mutated,
        'target_variant_count': target_count,
        'target_variant_frequency': target_count / total_mutated if total_mutated > 0 else 0,
        'top_variants': counts.most_common(10),
    }
```

### 3.4 Key cBioPortal Studies for Common Cancer Types

| Cancer Type | Study ID | Description |
|-------------|----------|-------------|
| Lung adenocarcinoma | luad_tcga | TCGA Lung Adenocarcinoma |
| Breast cancer | brca_tcga | TCGA Breast Cancer |
| Colorectal cancer | coadread_tcga | TCGA Colorectal |
| Melanoma | skcm_tcga | TCGA Melanoma |
| Pancreatic cancer | paad_tcga | TCGA Pancreatic |
| Glioblastoma | gbm_tcga | TCGA Glioblastoma |
| Prostate cancer | prad_tcga | TCGA Prostate |
| Ovarian cancer | ov_tcga | TCGA Ovarian |

---

## Phase 4: Therapeutic Associations

**Goal**: Identify all available therapies -- approved, in trials, and experimental.

### 4.1 OpenTargets Drug-Target Associations (PRIMARY)

```python
def get_target_drugs(tu, ensembl_id, size=50):
    """Get all drugs associated with a target from OpenTargets."""
    result = tu.tools.OpenTargets_get_associated_drugs_by_target_ensemblID(
        ensemblId=ensembl_id, size=size
    )
    # Response: {data: {target: {id, approvedSymbol, knownDrugs: {count, rows: [
    #   {drug: {id, name, tradeNames, maximumClinicalTrialPhase, isApproved, hasBeenWithdrawn},
    #    phase, mechanismOfAction, disease: {id, name}}
    # ]}}}}

    drugs = result.get('data', {}).get('target', {}).get('knownDrugs', {})
    rows = drugs.get('rows', [])

    # Categorize
    approved = [r for r in rows if r.get('drug', {}).get('isApproved')]
    phase3 = [r for r in rows if r.get('phase') == 3 and not r.get('drug', {}).get('isApproved')]
    phase2 = [r for r in rows if r.get('phase') == 2]

    return {
        'total': drugs.get('count', 0),
        'approved': approved,
        'phase3': phase3,
        'phase2': phase2,
        'all_rows': rows
    }
```

### 4.2 OpenTargets Drug Mechanisms

```python
def get_drug_mechanism(tu, chembl_id):
    """Get mechanism of action for a drug."""
    result = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId=chembl_id)
    return result
```

### 4.3 FDA Label Information

```python
def get_fda_label(tu, drug_name):
    """Get FDA-approved indications and label info."""
    indications = tu.tools.FDA_get_indications_by_drug_name(drug_name=drug_name, limit=3)
    # Response: {meta: {skip, limit, total}, results: [{openfda.brand_name, openfda.generic_name, indications_and_usage}]}

    warnings = tu.tools.FDA_get_boxed_warning_info_by_drug_name(drug_name=drug_name, limit=3)

    moa = tu.tools.FDA_get_mechanism_of_action_by_drug_name(drug_name=drug_name, limit=3)

    return {
        'indications': indications,
        'warnings': warnings,
        'mechanism': moa
    }
```

### 4.4 DrugBank Drug Information

```python
def get_drugbank_info(tu, drug_name):
    """Get drug information from DrugBank."""
    result = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(
        query=drug_name, case_sensitive=False, exact_match=False, limit=3
    )
    # Response: {query, total_matches, total_returned_results, results: [{drug_name, drugbank_id, description, ...}]}
    return result
```

### 4.5 ChEMBL Drug Mechanism

```python
def get_chembl_mechanism(tu, chembl_drug_id):
    """Get drug mechanism from ChEMBL."""
    result = tu.tools.ChEMBL_get_drug_mechanisms(drug_chembl_id__exact=chembl_drug_id, limit=10)
    return result
```

### 4.6 Disease-Specific Drug Filtering

When cancer type is provided, filter drugs by disease association:

```python
def get_disease_specific_drugs(tu, efo_id, size=30):
    """Get drugs associated with a specific disease/cancer type."""
    result = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId=efo_id, size=size)
    return result
```

### 4.7 Treatment Prioritization

| Priority | Criteria | Tier |
|----------|----------|------|
| **1st Line** | FDA-approved for exact indication + biomarker | T1 |
| **2nd Line** | FDA-approved for different indication, same biomarker | T1-T2 |
| **3rd Line** | Phase 3 clinical trial data | T2 |
| **4th Line** | Phase 1-2 data, off-label with evidence | T3 |
| **5th Line** | Preclinical or computational only | T4 |

---

## Phase 5: Resistance Mechanisms

**Goal**: Identify known resistance patterns and strategies to overcome them.

### 5.1 CIViC Resistance Evidence

Search CIViC for variants with resistance significance for the target gene. Get all variants and look for those with "Resistance" in the name or description.

### 5.2 Literature-Based Resistance Search

```python
def search_resistance_literature(tu, gene_symbol, drug_name):
    """Search PubMed for resistance mechanisms.
    NOTE: PubMed returns a plain list of article dicts, NOT {articles: [...]}.
    """
    result = tu.tools.PubMed_search_articles(
        query=f'"{gene_symbol}" AND "{drug_name}" AND resistance AND mechanism',
        limit=15,
        include_abstract=True
    )
    # Response: list of [{pmid, title, authors, journal, pub_date, doi, abstract, ...}]
    articles = result if isinstance(result, list) else result.get('articles', []) if isinstance(result, dict) else []
    return articles
```

### 5.3 Pathway-Based Bypass Resistance

```python
def get_bypass_pathways(tu, uniprot_id):
    """Get pathways that could mediate bypass resistance."""
    result = tu.tools.Reactome_map_uniprot_to_pathways(id=uniprot_id)
    return result
```

### 5.4 Known Resistance Patterns (Reference)

| Primary Target | Primary Drug | Resistance Mutation | Mechanism | Strategy |
|---------------|-------------|-------------------|-----------|----------|
| EGFR L858R | Erlotinib/Gefitinib | T790M | Steric hindrance | Osimertinib (3rd-gen TKI) |
| EGFR T790M | Osimertinib | C797S | Covalent bond loss | 4th-gen TKI trials |
| BRAF V600E | Vemurafenib | Splice variants | Paradoxical activation | BRAF+MEK combination |
| ALK fusion | Crizotinib | L1196M, G1269A | Kinase domain mutations | Alectinib, Lorlatinib |
| KRAS G12C | Sotorasib | Y96D, R68S | Drug binding loss | KRAS G12C combo trials |

---

## Phase 6: Clinical Trials

**Goal**: Find actively recruiting clinical trials relevant to this mutation.

### 6.1 Search Strategy

```python
def find_clinical_trials(tu, gene_symbol, variant_name, cancer_type=None):
    """Find clinical trials for this mutation."""
    # Search 1: Gene + variant specific
    query1 = f'{gene_symbol} {variant_name}'
    result1 = tu.tools.search_clinical_trials(
        query_term=query1,
        condition=cancer_type or 'cancer',
        pageSize=20
    )

    # Search 2: Gene + targeted therapy
    result2 = tu.tools.search_clinical_trials(
        query_term=f'{gene_symbol} mutation',
        condition=cancer_type or 'cancer',
        pageSize=20
    )

    return {
        'variant_specific': result1,
        'gene_level': result2
    }
```

**Response structure**: `{studies: [{NCT ID, brief_title, brief_summary, overall_status, condition, phase}], nextPageToken, total_count}`

### 6.2 Trial Filtering

Prioritize trials that:
1. Are **RECRUITING** or **NOT_YET_RECRUITING** status
2. Match the specific variant (not just gene)
3. Are Phase 2 or 3 (closer to approval)
4. Have the right cancer type

### 6.3 Trial Output Format

```markdown
| NCT ID | Phase | Agent(s) | Status | Cancer Type | Biomarker |
|--------|-------|----------|--------|-------------|-----------|
```

---

## Phase 7: Prognostic Impact & Pathway Context

**Goal**: Assess the variant's impact on prognosis and biological context.

### 7.1 Literature Evidence

```python
def get_prognostic_literature(tu, gene_symbol, variant_name, cancer_type=None):
    """Search for prognostic associations."""
    query = f'"{gene_symbol}" "{variant_name}" prognosis survival'
    if cancer_type:
        query += f' "{cancer_type}"'

    result = tu.tools.PubMed_search_articles(query=query, limit=10, include_abstract=True)
    return result
```

### 7.2 Pathway Context (Reactome)

```python
def get_pathway_context(tu, uniprot_id):
    """Get pathway context from Reactome."""
    result = tu.tools.Reactome_map_uniprot_to_pathways(id=uniprot_id)
    return result
```

### 7.3 Gene Expression (GTEx)

```python
def get_expression_context(tu, ensembl_id):
    """Get tissue expression data from GTEx."""
    # GTEx needs versioned ID. IMPORTANT: ensembl_lookup_gene requires species parameter.
    gene_info = tu.tools.ensembl_lookup_gene(gene_id=ensembl_id, species='homo_sapiens')
    # Response: {status: 'success', data: {id, version, display_name, ...}}
    data = gene_info.get('data', gene_info) if isinstance(gene_info, dict) else {}
    version = data.get('version', 1)
    versioned_id = f"{ensembl_id}.{version}"

    result = tu.tools.GTEx_get_median_gene_expression(
        gencode_id=versioned_id, operation='median'
    )
    return result
```

### 7.4 UniProt Disease Variants

```python
def get_known_disease_variants(tu, uniprot_accession):
    """Get known disease-associated variants from UniProt."""
    result = tu.tools.UniProt_get_disease_variants_by_accession(accession=uniprot_accession)
    return result
```

---

## Phase 8: Report Synthesis

### 8.1 Report File Naming

```
{GENE}_{VARIANT}_cancer_variant_report.md

Examples:
EGFR_L858R_cancer_variant_report.md
BRAF_V600E_cancer_variant_report.md
KRAS_G12C_cancer_variant_report.md
```

### 8.2 Report Template

```markdown
# Cancer Variant Interpretation Report: {GENE} {VARIANT}

**Date**: {date}
**Cancer Type**: {cancer_type or "Not specified"}

---

## Executive Summary

{1-2 sentences summarizing the key finding and top recommendation}

**Clinical Actionability**: {Score: HIGH / MODERATE / LOW / UNKNOWN}

---

## 1. Gene & Variant Overview

| Field | Value |
|-------|-------|
| Gene Symbol | {symbol} |
| Full Name | {name} |
| Ensembl ID | {ensembl_id} |
| UniProt | {uniprot_accession} |
| Entrez ID | {entrez_id} |
| Variant | {variant_notation} |
| Protein Function | {function_summary} |

## 2. Clinical Variant Evidence

### 2.1 CIViC Clinical Interpretations

| Evidence Type | Description | Level | Clinical Significance |
|---------------|-------------|-------|----------------------|
| ... | ... | ... | ... |

### 2.2 Evidence Summary

{Summary of clinical evidence from CIViC and other sources}

*Source: CIViC via civic_get_variants_by_gene, civic_get_variant*

## 3. Mutation Prevalence

### 3.1 Frequency Across Cancer Types (cBioPortal)

| Study | Cancer Type | Total Mutated | This Variant | Frequency |
|-------|-------------|---------------|--------------|-----------|
| ... | ... | ... | ... | ... |

### 3.2 Co-occurring Mutations

{Top co-occurring mutations from cBioPortal data}

*Source: cBioPortal via cBioPortal_get_mutations*

## 4. Therapeutic Options

### 4.1 FDA-Approved Therapies (T1 Evidence)

| Drug | Trade Name | Indication | Mechanism | Phase |
|------|-----------|------------|-----------|-------|
| ... | ... | ... | ... | ... |

### 4.2 Clinical Trial Drugs (T2-T3 Evidence)

| Drug | ChEMBL ID | Phase | Mechanism | Disease |
|------|-----------|-------|-----------|---------|
| ... | ... | ... | ... | ... |

### 4.3 Drug Details

{For each recommended drug: mechanism of action, FDA label info, dosing, warnings}

*Sources: OpenTargets, FDA, DrugBank, ChEMBL*

## 5. Resistance Mechanisms

### 5.1 Known Resistance Patterns

| Resistance Mutation | Drug Affected | Mechanism | Strategy to Overcome |
|--------------------|---------------|-----------|---------------------|
| ... | ... | ... | ... |

### 5.2 Bypass Pathways

{Pathway analysis showing potential bypass resistance routes}

*Sources: CIViC, PubMed, Reactome*

## 6. Clinical Trials

### 6.1 Actively Recruiting Trials

| NCT ID | Phase | Agent(s) | Status | Biomarker Required |
|--------|-------|----------|--------|-------------------|
| ... | ... | ... | ... | ... |

### 6.2 Trial Recommendations

{Specific trial recommendations based on patient's mutation and cancer type}

*Source: ClinicalTrials.gov via search_clinical_trials*

## 7. Prognostic Impact

### 7.1 Survival Associations

{Literature-based prognostic data}

### 7.2 Pathway Context

{Pathway analysis and biological context}

### 7.3 Expression Profile

{Tissue expression data for the gene}

*Sources: PubMed, Reactome, GTEx*

## 8. Evidence Grading Summary

| Finding | Evidence Tier | Source | Confidence |
|---------|--------------|--------|------------|
| ... | T1/T2/T3/T4 | ... | High/Moderate/Low |

---

## Data Sources Queried

| Source | Tool(s) Used | Data Retrieved |
|--------|-------------|----------------|
| MyGene | MyGene_query_genes | Gene IDs |
| UniProt | UniProt_search, UniProt_get_function_by_accession | Protein function |
| OpenTargets | OpenTargets_get_associated_drugs_by_target_ensemblID | Drug associations |
| CIViC | civic_search_genes, civic_get_variants_by_gene | Clinical evidence |
| cBioPortal | cBioPortal_get_mutations | Mutation prevalence |
| FDA | FDA_get_indications_by_drug_name | Drug labels |
| DrugBank | drugbank_get_drug_basic_info_by_drug_name_or_id | Drug info |
| ChEMBL | ChEMBL_get_drug_mechanisms | Drug mechanisms |
| ClinicalTrials.gov | search_clinical_trials | Active trials |
| PubMed | PubMed_search_articles | Literature evidence |
| Reactome | Reactome_map_uniprot_to_pathways | Pathway context |
| GTEx | GTEx_get_median_gene_expression | Expression data |

---

## Completeness Checklist

- [ ] Gene resolved to Ensembl, UniProt, and Entrez IDs
- [ ] Clinical variant evidence queried (CIViC or alternative)
- [ ] Mutation prevalence assessed (cBioPortal, at least 1 study)
- [ ] At least 1 therapeutic option identified with evidence tier, OR documented as "no targeted therapy available"
- [ ] FDA label information retrieved for recommended drugs
- [ ] Resistance mechanisms assessed (known patterns + literature search)
- [ ] At least 3 clinical trials listed, OR "no matching trials found"
- [ ] Prognostic literature searched
- [ ] Pathway context provided (Reactome)
- [ ] Executive summary is actionable (says what to DO)
- [ ] All recommendations have source citations
- [ ] Evidence tiers assigned to all findings
```

---

## Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|---------|
| **T1** | [T1] | FDA-approved therapy, Level A CIViC evidence, phase 3 trial | Osimertinib for EGFR T790M |
| **T2** | [T2] | Phase 2/3 clinical data, Level B CIViC evidence | Combination trial data |
| **T3** | [T3] | Preclinical data, Level D CIViC, case reports | Novel mechanisms, in vitro |
| **T4** | [T4] | Computational prediction, pathway inference | Docking, pathway analysis |

---

## Clinical Actionability Scoring

| Score | Criteria |
|-------|----------|
| **HIGH** | FDA-approved targeted therapy exists for this exact mutation + cancer type |
| **MODERATE** | Approved therapy exists for different cancer type with same mutation, OR phase 2-3 trial data |
| **LOW** | Only preclinical evidence or pathway-based rationale |
| **UNKNOWN** | Insufficient data to assess actionability |

---

## Fallback Chains

| Primary Tool | Fallback | Use When |
|-------------|----------|----------|
| CIViC variant lookup | PubMed literature search | Gene not found in CIViC (search doesn't filter) |
| OpenTargets drugs | ChEMBL drug search | No OpenTargets drug hits |
| FDA indications | DrugBank drug info | Drug not in FDA database |
| cBioPortal TCGA study | cBioPortal pan-cancer | Specific cancer study not available |
| GTEx expression | Ensembl gene lookup | GTEx returns empty |
| Reactome pathways | UniProt function | Pathway mapping fails |

---

## Tool Reference (Verified Parameters)

### Gene Resolution

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `MyGene_query_genes` | `query` (required), `species` | `hits[].symbol`, `hits[].ensembl.gene`, `hits[].entrezgene` |
| `UniProt_search` | `query` (required), `organism`, `limit` | `results[].accession`, `results[].gene_names` |
| `OpenTargets_get_target_id_description_by_name` | `targetName` (required) | `data.search.hits[].id` (ensemblId) |
| `ensembl_lookup_gene` | `gene_id` (required), `species` (REQUIRED: 'homo_sapiens') | `data.id`, `data.display_name`, `data.version` |

### Clinical Evidence

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `civic_search_genes` | `query`, `limit` | `data.genes.nodes[].id`, `.name`, `.entrezId` |
| `civic_get_variants_by_gene` | `gene_id` (required, CIViC numeric), `limit` | `data.gene.variants.nodes[].id`, `.name` |
| `civic_get_variant` | `variant_id` (required) | `data.variant.id`, `.name` |
| `civic_get_molecular_profile` | `molecular_profile_id` (required) | `data.molecularProfile.id`, `.name` |

### Mutation Prevalence

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `cBioPortal_get_mutations` | `study_id`, `gene_list` | `data[].proteinChange`, `.mutationType`, `.sampleId` (wrapped in `{status, data}`) |
| `cBioPortal_get_cancer_studies` | `limit` | `[].studyId`, `.name`, `.cancerTypeId` |
| `cBioPortal_get_molecular_profiles` | `study_id` (required) | `[].molecularProfileId`, `.molecularAlterationType` |

### Drug Information

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId` (required), `size` | `data.target.knownDrugs.rows[].drug.name`, `.isApproved`, `.mechanismOfAction` |
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName` (required) | `data.search.hits[].id` (ChEMBL ID), `.name` |
| `FDA_get_indications_by_drug_name` | `drug_name`, `limit` | `results[].indications_and_usage`, `.openfda.brand_name` |
| `FDA_get_mechanism_of_action_by_drug_name` | `drug_name`, `limit` | `results[].mechanism_of_action` |
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name`, `limit` | `results[].boxed_warning` |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL required) | `results[].drug_name`, `.drugbank_id`, `.description` |
| `ChEMBL_get_drug_mechanisms` | `drug_chembl_id__exact` (required), `limit` | `data.mechanisms[]` |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` (ALL required) | `results[].pharmacology` |

### Clinical Trials

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `search_clinical_trials` | `query_term` (required), `condition`, `intervention`, `pageSize` | `studies[].NCT ID`, `.brief_title`, `.overall_status`, `.phase` |

### Literature & Pathways

| Tool | Parameters | Response Key Fields |
|------|-----------|-------------------|
| `PubMed_search_articles` | `query` (required), `limit`, `include_abstract` | Returns **list** of `[{pmid, title, authors, journal, pub_date, doi, abstract}]` (NOT wrapped in dict) |
| `Reactome_map_uniprot_to_pathways` | `id` (required, UniProt accession) | Pathway mappings |
| `GTEx_get_median_gene_expression` | `gencode_id` (required), `operation="median"` | Expression by tissue |
| `UniProt_get_function_by_accession` | `accession` (required) | Protein function |
| `UniProt_get_disease_variants_by_accession` | `accession` (required) | Disease variants |

---

## Common Use Cases

### Use Case 1: Oncologist Evaluating Treatment Options

**Input**: "EGFR L858R in lung adenocarcinoma"

**Expected Output**: Report showing osimertinib as 1st-line [T1], with FDA label details, resistance pattern (T790M), clinical trials for combination therapies, and prognostic context.

### Use Case 2: Molecular Tumor Board Preparation

**Input**: "BRAF V600E, colorectal cancer"

**Expected Output**: Report noting that BRAF V600E is actionable in melanoma but requires combination therapy in CRC (encorafenib + cetuximab), with different resistance patterns than melanoma.

### Use Case 3: Clinical Trial Matching

**Input**: "KRAS G12C, any cancer type"

**Expected Output**: Report with sotorasib/adagrasib as approved options [T1], comprehensive trial listing for KRAS G12C inhibitors, resistance patterns (Y96D, etc.), and mutation prevalence across cancer types.

### Use Case 4: Resistance Mechanism Investigation

**Input**: "EGFR T790M after osimertinib failure"

**Expected Output**: Report focused on C797S resistance mutation, available 4th-generation TKI trials, amivantamab/lazertinib combinations, and bypass pathway mechanisms (MET amplification, HER2 activation).

### Use Case 5: VUS Interpretation

**Input**: "PIK3CA E545K"

**Expected Output**: Report showing this is a known hotspot oncogenic mutation (not a VUS), with alpelisib as FDA-approved therapy for HR+/HER2- breast cancer, and prevalence data across cancer types.

---

## Quantified Minimums

| Section | Requirement |
|---------|-------------|
| Gene IDs | At least Ensembl + UniProt resolved |
| Clinical evidence | CIViC queried + PubMed literature search |
| Mutation prevalence | At least 1 cBioPortal study |
| Therapeutic options | All approved drugs listed (OpenTargets) + FDA label for top drugs |
| Resistance | Literature search performed + known patterns documented |
| Clinical trials | At least 1 search query executed |
| Prognostic impact | PubMed literature search performed |
| Pathway context | Reactome pathway mapping attempted |

---

## See Also

- `QUICK_START.md` - Example usage and quick reference
- `TOOLS_REFERENCE.md` - Detailed tool parameter reference
- `EXAMPLES.md` - Complete example reports
