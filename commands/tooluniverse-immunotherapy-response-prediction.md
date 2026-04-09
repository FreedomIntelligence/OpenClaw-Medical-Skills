# tooluniverse-immunotherapy-response-prediction

> Predict patient response to immune checkpoint inhibitors (ICIs) using multi-biomarker integration. Given a cancer type, somatic mutations, and optional biomarkers (TMB, PD-L1, MSI status), performs systematic analysis across 11 phases covering TMB classification, neoantigen burden estimation, MSI/MMR assessment, PD-L1 evaluation, immune microenvironment profiling, mutation-based resistance/sensitivity prediction, clinical evidence retrieval, and multi-biomarker score integration. Generates a quantitative ICI Response Score (0-100), response likelihood tier, specific ICI drug recommendations with evidence, resistance risk factors, and a monitoring plan. Use when oncologists ask about immunotherapy eligibility, checkpoint inhibitor selection, or biomarker-guided ICI treatment decisions.

# Immunotherapy Response Prediction

Predict patient response to immune checkpoint inhibitors (ICIs) using multi-biomarker integration. Transforms a patient tumor profile (cancer type + mutations + biomarkers) into a quantitative ICI Response Score with drug-specific recommendations, resistance risk assessment, and monitoring plan.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Evidence-graded** - Every finding has an evidence tier (T1-T4)
3. **Quantitative output** - ICI Response Score (0-100) with transparent component breakdown
4. **Cancer-specific** - All thresholds and predictions are cancer-type adjusted
5. **Multi-biomarker** - Integrate TMB + MSI + PD-L1 + neoantigen + mutations
6. **Resistance-aware** - Always check for known resistance mutations (STK11, PTEN, JAK1/2, B2M)
7. **Drug-specific** - Recommend specific ICI agents with evidence
8. **Source-referenced** - Every statement cites the tool/database source
9. **English-first queries** - Always use English terms in tool calls

---

## When to Use

Apply when user asks:
- "Will this patient respond to immunotherapy?"
- "Should I give pembrolizumab to this melanoma patient?"
- "Patient has NSCLC with TMB 25, PD-L1 80% - predict ICI response"
- "MSI-high colorectal cancer - which checkpoint inhibitor?"
- "Patient has BRAF V600E melanoma, TMB 15 - immunotherapy or targeted?"
- "Low TMB NSCLC with STK11 mutation - should I try immunotherapy?"
- "Compare pembrolizumab vs nivolumab for this patient profile"
- "What biomarkers predict checkpoint inhibitor response?"

---

## Input Parsing

**Required**: Cancer type + at least one of: mutation list OR TMB value
**Optional**: PD-L1 expression, MSI status, immune infiltration data, HLA type, prior treatments, intended ICI

### Accepted Input Formats

| Format | Example | How to Parse |
|--------|---------|-------------|
| Cancer + mutations | "Melanoma, BRAF V600E, TP53 R273H" | cancer=melanoma, mutations=[BRAF V600E, TP53 R273H] |
| Cancer + TMB | "NSCLC, TMB 25 mut/Mb" | cancer=NSCLC, tmb=25 |
| Cancer + full profile | "Melanoma, BRAF V600E, TMB 15, PD-L1 50%, MSS" | cancer=melanoma, mutations=[BRAF V600E], tmb=15, pdl1=50, msi=MSS |
| Cancer + MSI status | "Colorectal cancer, MSI-high" | cancer=CRC, msi=MSI-H |
| Resistance query | "NSCLC, TMB 2, STK11 loss, PD-L1 <1%" | cancer=NSCLC, tmb=2, mutations=[STK11 loss], pdl1=0 |
| ICI selection | "Which ICI for NSCLC PD-L1 90%?" | cancer=NSCLC, pdl1=90, query_type=drug_selection |

### Cancer Type Normalization

Common aliases to resolve:
- NSCLC -> non-small cell lung carcinoma
- SCLC -> small cell lung carcinoma
- CRC -> colorectal cancer
- RCC -> renal cell carcinoma
- HNSCC -> head and neck squamous cell carcinoma
- UC / bladder -> urothelial carcinoma
- HCC -> hepatocellular carcinoma
- TNBC -> triple-negative breast cancer
- GEJ -> gastroesophageal junction cancer

### Gene Symbol Normalization

- PD-L1 -> CD274
- PD-1 -> PDCD1
- CTLA-4 -> CTLA4
- HER2 -> ERBB2
- MSH2/MLH1/MSH6/PMS2 -> MMR genes

---

## Phase 0: Tool Parameter Reference (CRITICAL)

**BEFORE calling ANY tool**, verify parameters using this reference table.

### Verified Tool Parameters

| Tool | Parameters | Notes |
|------|-----------|-------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` | Returns `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_drug_id_description_by_name` | `drugName` | Returns `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | `efoId`, `size` | Returns `{data: {disease: {knownDrugs: {count, rows}}}}` |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` | Returns `{data: {drug: {mechanismsOfAction: {rows}}}}` |
| `OpenTargets_get_approved_indications_by_drug_chemblId` | `chemblId` | Approved indications list |
| `OpenTargets_get_drug_description_by_chemblId` | `chemblId` | Drug description text |
| `OpenTargets_get_associated_targets_by_drug_chemblId` | `chemblId` | Drug targets |
| `MyGene_query_genes` | `query` (NOT `q`) | Returns `{hits: [{_id, symbol, name, ensembl: {gene}}]}` |
| `ensembl_lookup_gene` | `gene_id`, `species='homo_sapiens'` | REQUIRES species. Returns `{data: {id, display_name}}` |
| `EnsemblVEP_annotate_rsid` | `variant_id` (NOT `rsid`) | VEP annotation with SIFT/PolyPhen |
| `civic_search_evidence_items` | `therapy_name`, `disease_name` | Returns `{data: {evidenceItems: {nodes}}}` - may not filter accurately |
| `civic_search_variants` | `name`, `gene_name` | Returns `{data: {variants: {nodes}}}` - returns many unrelated variants |
| `civic_get_variants_by_gene` | `gene_id` (CIViC numeric ID) | Requires CIViC gene ID, NOT Entrez |
| `civic_search_assertions` | `therapy_name`, `disease_name` | Returns `{data: {assertions: {nodes}}}` |
| `civic_search_therapies` | `name` | Search therapies by name |
| `cBioPortal_get_mutations` | `study_id`, `gene_list` (string) | `gene_list` is a STRING not array |
| `cBioPortal_get_cancer_studies` | (no params needed) | May fail with keyword param |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL 4 REQUIRED |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL 4 REQUIRED |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL 4 REQUIRED |
| `drugbank_get_indications_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL 4 REQUIRED |
| `FDA_get_indications_by_drug_name` | `drug_name`, `limit` | Returns `{meta, results}` |
| `FDA_get_clinical_studies_info_by_drug_name` | `drug_name`, `limit` | Returns `{meta, results}` |
| `FDA_get_adverse_reactions_by_drug_name` | `drug_name`, `limit` | Returns `{meta, results}` |
| `FDA_get_mechanism_of_action_by_drug_name` | `drug_name`, `limit` | Returns `{meta, results}` |
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name`, `limit` | May return NOT_FOUND |
| `FDA_get_warnings_by_drug_name` | `drug_name`, `limit` | Returns `{meta, results}` |
| `fda_pharmacogenomic_biomarkers` | `drug_name`, `biomarker`, `limit` | Returns `{count, shown, results: [{Drug, Biomarker, TherapeuticArea, LabelingSection}]}` |
| `clinical_trials_search` | `action='search_studies'`, `condition`, `intervention`, `limit` | Returns `{total_count, studies}` |
| `clinical_trials_get_details` | `action='get_study_details'`, `nct_id` | Full study object |
| `search_clinical_trials` | `query_term` (REQUIRED), `condition`, `intervention`, `pageSize` | Returns `{studies, total_count}` |
| `PubMed_search_articles` | `query`, `max_results` | Returns plain list of dicts |
| `UniProt_get_function_by_accession` | `accession` | Returns list of strings |
| `UniProt_get_disease_variants_by_accession` | `accession` | Disease-associated variants |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` | ALL 3 REQUIRED |
| `HPA_get_cancer_prognostics_by_gene` | `gene_name` | Cancer prognostic data |
| `iedb_search_epitopes` | `organism_name`, `source_antigen_name` | Returns `{status, data, count}` |
| `iedb_search_mhc` | various | MHC binding data |
| `enrichr_gene_enrichment_analysis` | `gene_list` (array), `libs` (array, REQUIRED) | Key libs: `KEGG_2021_Human`, `Reactome_2022` |
| `PharmGKB_get_clinical_annotations` | `query` | Clinical annotations |
| `gnomad_get_gene_constraints` | `gene_symbol` | Gene constraint metrics |

---

## Workflow Overview

```
Input: Cancer type + Mutations/TMB + Optional biomarkers (PD-L1, MSI, etc.)

Phase 1: Input Standardization & Cancer Context
  - Resolve cancer type to EFO ID
  - Parse mutation list
  - Resolve genes to Ensembl/Entrez IDs
  - Get cancer-specific ICI baseline

Phase 2: TMB Analysis
  - TMB classification (low/intermediate/high)
  - Cancer-specific TMB thresholds
  - FDA TMB-H biomarker status

Phase 3: Neoantigen Analysis
  - Estimate neoantigen burden from mutations
  - Mutation type classification (missense/frameshift/nonsense)
  - Neoantigen quality indicators

Phase 4: MSI/MMR Status Assessment
  - MSI status integration
  - MMR gene mutation check
  - FDA MSI-H approval status

Phase 5: PD-L1 Expression Analysis
  - PD-L1 level classification
  - Cancer-specific PD-L1 thresholds
  - FDA-approved PD-L1 cutoffs

Phase 6: Immune Microenvironment Profiling
  - Immune checkpoint gene expression
  - Tumor immune classification (hot/cold)
  - Immune escape signatures

Phase 7: Mutation-Based Predictors
  - Driver mutation analysis
  - Resistance mutations (STK11, PTEN, JAK1/2, B2M)
  - Sensitivity mutations (POLE)
  - DNA damage repair pathway

Phase 8: Clinical Evidence & ICI Options
  - FDA-approved ICIs for this cancer
  - Clinical trial response rates
  - Drug mechanism comparison
  - Combination therapy evidence

Phase 9: Resistance Risk Assessment
  - Known resistance factors
  - Tumor immune evasion mechanisms
  - Prior treatment context

Phase 10: Multi-Biomarker Score Integration
  - Calculate ICI Response Score (0-100)
  - Component breakdown
  - Confidence level

Phase 11: Clinical Recommendations
  - ICI drug recommendation
  - Monitoring plan
  - Alternative strategies
```

---

## Phase 1: Input Standardization & Cancer Context

### Step 1.1: Resolve Cancer Type

```python
# Get cancer EFO ID
result = tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName='melanoma')
# -> {data: {search: {hits: [{id: 'EFO_0000756', name: 'melanoma', description: '...'}]}}}
```

**Cancer-specific ICI context** (hardcoded knowledge base):

| Cancer Type | EFO ID | Baseline ICI ORR | Key Biomarkers | FDA-Approved ICIs |
|-------------|--------|-------------------|----------------|-------------------|
| Melanoma | EFO_0000756 | 30-45% | TMB, PD-L1 | pembro, nivo, ipi, nivo+ipi, nivo+rela |
| NSCLC | EFO_0003060 | 15-50% (PD-L1 dependent) | PD-L1, TMB, STK11 | pembro, nivo, atezo, durva, cemiplimab |
| Bladder/UC | EFO_0000292 | 15-25% | PD-L1, TMB | pembro, nivo, atezo, avelumab, durva |
| RCC | EFO_0000681 | 25-40% | PD-L1 | nivo, pembro, nivo+ipi, nivo+cabo, pembro+axitinib |
| HNSCC | EFO_0000181 | 15-20% | PD-L1 CPS | pembro, nivo |
| MSI-H (any) | N/A | 30-50% | MSI, dMMR | pembro (tissue-agnostic) |
| TMB-H (any) | N/A | 20-30% | TMB >=10 | pembro (tissue-agnostic) |
| CRC (MSI-H) | EFO_0000365 | 30-50% | MSI, dMMR | pembro, nivo, nivo+ipi |
| CRC (MSS) | EFO_0000365 | <5% | Generally poor | Generally not recommended |
| HCC | EFO_0000182 | 15-20% | PD-L1 | atezo+bev, durva+treme, nivo+ipi |
| TNBC | EFO_0005537 | 10-20% | PD-L1 CPS | pembro+chemo |
| Gastric/GEJ | EFO_0000178 | 10-20% | PD-L1 CPS, MSI | pembro, nivo |

### Step 1.2: Parse Mutations

Parse each mutation into structured format:
```
"BRAF V600E" -> {gene: "BRAF", variant: "V600E", type: "missense"}
"TP53 R273H" -> {gene: "TP53", variant: "R273H", type: "missense"}
"STK11 loss" -> {gene: "STK11", variant: "loss of function", type: "loss"}
```

### Step 1.3: Resolve Gene IDs

```python
# For each gene in mutation list
result = tu.tools.MyGene_query_genes(query='BRAF')
# -> hits[0]: {_id: '673', symbol: 'BRAF', ensembl: {gene: 'ENSG00000157764'}}
```

---

## Phase 2: TMB Analysis

### Step 2.1: TMB Classification

If TMB value provided directly, classify:

| TMB Range | Classification | ICI Score Component |
|-----------|---------------|---------------------|
| >= 20 mut/Mb | TMB-High | 30 points |
| 10-19.9 mut/Mb | TMB-Intermediate | 20 points |
| 5-9.9 mut/Mb | TMB-Low | 10 points |
| < 5 mut/Mb | TMB-Very-Low | 5 points |

If only mutations provided, estimate TMB:
- Count total mutations provided
- Note: User-provided lists are typically key mutations, not full exome
- Flag as "estimated from provided mutations - clinical TMB testing recommended"

### Step 2.2: TMB FDA Context

```python
# Check FDA TMB-H biomarker approval
result = tu.tools.fda_pharmacogenomic_biomarkers(drug_name='pembrolizumab', limit=100)
# Look for "Tumor Mutational Burden" in Biomarker field
# -> Pembrolizumab approved for TMB-H (>=10 mut/Mb) tissue-agnostic
```

### Step 2.3: Cancer-Specific TMB Thresholds

| Cancer Type | Typical TMB Range | High-TMB Threshold | Notes |
|-------------|-------------------|-------------------|-------|
| Melanoma | 5-50+ | >20 | High baseline TMB; UV-induced |
| NSCLC | 2-30 | >10 | Smoking-related; FDA cutoff 10 |
| Bladder | 5-25 | >10 | Moderate baseline |
| CRC (MSI-H) | 20-100+ | >10 | Very high in MSI-H |
| CRC (MSS) | 2-10 | >10 | Generally low |
| RCC | 1-8 | >10 | Low TMB but ICI-responsive |
| HNSCC | 2-15 | >10 | Moderate |

**IMPORTANT**: RCC responds to ICIs despite low TMB. TMB is less predictive in some cancers.

---

## Phase 3: Neoantigen Analysis

### Step 3.1: Neoantigen Burden Estimation

From mutation list:
- **Missense mutations** -> Each has ~20-50% chance of generating a neoantigen
- **Frameshift mutations** -> High neoantigen-generating potential (novel peptides)
- **Nonsense mutations** -> Moderate potential (truncated proteins)
- **Splice site mutations** -> Moderate potential (aberrant peptides)

Estimate: neoantigen_count ~= missense_count * 0.3 + frameshift_count * 1.5

### Step 3.2: Neoantigen Quality Assessment

```python
# Check mutation impact using UniProt
result = tu.tools.UniProt_get_function_by_accession(accession='P15056')  # BRAF UniProt
# Assess if mutation is in functional domain
```

**Quality indicators**:
- Mutations in protein kinase domains -> high immunogenicity potential
- Mutations in surface-exposed regions -> better MHC presentation
- POLE/POLD1 mutations -> ultra-high neoantigen load (ultramutated)

### Step 3.3: IEDB Epitope Data (if relevant)

```python
# Check known epitopes for mutated proteins
result = tu.tools.iedb_search_epitopes(organism_name='homo sapiens', source_antigen_name='BRAF')
# Returns known epitopes, MHC restrictions
```

### Neoantigen Score Component

| Estimated Neoantigen Load | Classification | Score |
|---------------------------|---------------|-------|
| >50 neoantigens | High | 15 points |
| 20-50 neoantigens | Moderate | 10 points |
| <20 neoantigens | Low | 5 points |

---

## Phase 4: MSI/MMR Status Assessment

### Step 4.1: MSI Status Integration

If MSI status provided directly:

| MSI Status | Classification | Score Component |
|-----------|----------------|----------------|
| MSI-H / dMMR | MSI-High | 25 points |
| MSS / pMMR | Microsatellite Stable | 5 points |
| Unknown | Not tested | 10 points (neutral) |

### Step 4.2: MMR Gene Mutation Check

Check if any provided mutations are in MMR genes:
- **MLH1** (ENSG00000076242) - mismatch repair
- **MSH2** (ENSG00000095002) - mismatch repair
- **MSH6** (ENSG00000116062) - mismatch repair
- **PMS2** (ENSG00000122512) - mismatch repair
- **EPCAM** (ENSG00000119888) - can silence MSH2

If MMR gene mutations found but MSI status not provided -> flag as "possible MSI-H, recommend testing"

### Step 4.3: FDA MSI-H Approvals

```python
# Check FDA approvals for MSI-H
result = tu.tools.fda_pharmacogenomic_biomarkers(biomarker='Microsatellite Instability', limit=100)
# Pembrolizumab: tissue-agnostic for MSI-H/dMMR
# Nivolumab: CRC (MSI-H)
# Dostarlimab: dMMR solid tumors
```

---

## Phase 5: PD-L1 Expression Analysis

### Step 5.1: PD-L1 Level Classification

| PD-L1 Level | Classification | Score Component |
|-------------|----------------|----------------|
| >= 50% (TPS) | PD-L1 High | 20 points |
| 1-49% (TPS) | PD-L1 Positive | 12 points |
| < 1% (TPS) | PD-L1 Negative | 5 points |
| Unknown | Not tested | 10 points (neutral) |

### Step 5.2: Cancer-Specific PD-L1 Thresholds

| Cancer | Scoring Method | Key Thresholds | ICI Monotherapy Recommended? |
|--------|---------------|----------------|------------------------------|
| NSCLC | TPS | >=50%: first-line mono; >=1%: after chemo | Yes at >=50%, combo at >=1% |
| Melanoma | Not routinely required | N/A | Yes regardless of PD-L1 |
| Bladder | CPS or IC | CPS>=10 preferred | Yes with PD-L1 positive |
| HNSCC | CPS | CPS>=1: pembro; CPS>=20: mono preferred | CPS>=20 for monotherapy |
| Gastric | CPS | CPS>=1 | Pembro+chemo |
| TNBC | CPS | CPS>=10 | Pembro+chemo |

### Step 5.3: PD-L1 Gene Expression (Baseline Reference)

```python
# PD-L1 (CD274) expression patterns
result = tu.tools.HPA_get_cancer_prognostics_by_gene(gene_name='CD274')
# Cancer-type specific prognostic data
```

---

## Phase 6: Immune Microenvironment Profiling

### Step 6.1: Key Immune Checkpoint Genes

Query expression data for immune microenvironment markers:

```python
# Key immune genes to check
immune_genes = ['CD274', 'PDCD1', 'CTLA4', 'LAG3', 'HAVCR2', 'TIGIT', 'CD8A', 'CD8B', 'GZMA', 'GZMB', 'PRF1', 'IFNG']

# For each gene, get cancer-specific expression
for gene in immune_genes:
    result = tu.tools.HPA_get_cancer_prognostics_by_gene(gene_name=gene)
```

### Step 6.2: Tumor Immune Classification

Based on available data, classify:

| Classification | Characteristics | ICI Likelihood |
|---------------|-----------------|----------------|
| Hot (T cell inflamed) | High CD8+ T cells, IFN-g, PD-L1+ | High response |
| Cold (immune desert) | Low immune infiltration | Low response |
| Immune excluded | Immune cells at margin, not infiltrating | Moderate response |
| Immune suppressed | High Tregs, MDSCs, immunosuppressive | Low-moderate |

### Step 6.3: Immune Pathway Enrichment

```python
# If mutation list includes immune-related genes, do pathway analysis
result = tu.tools.enrichr_gene_enrichment_analysis(
    gene_list=['CD274', 'PDCD1', 'CTLA4', 'IFNG', 'CD8A'],
    libs=['KEGG_2021_Human', 'Reactome_2022']
)
```

---

## Phase 7: Mutation-Based Predictors

### Step 7.1: ICI-Resistance Mutations (CRITICAL)

**Known resistance mutations** - apply PENALTIES:

| Gene | Mutation | Cancer Context | Mechanism | Penalty |
|------|----------|---------------|-----------|---------|
| STK11/LKB1 | Loss/inactivation | NSCLC (esp. KRAS+) | Immune exclusion, cold TME | -10 points |
| PTEN | Loss/deletion | Multiple | Reduced T cell infiltration | -5 points |
| JAK1 | Loss of function | Multiple | IFN-g signaling loss | -10 points |
| JAK2 | Loss of function | Multiple | IFN-g signaling loss | -10 points |
| B2M | Loss/mutation | Multiple | MHC-I loss, immune escape | -15 points |
| KEAP1 | Loss/mutation | NSCLC | Oxidative stress, cold TME | -5 points |
| MDM2 | Amplification | Multiple | Hyperprogression risk | -5 points |
| MDM4 | Amplification | Multiple | Hyperprogression risk | -5 points |
| EGFR | Activating mutation | NSCLC | Low TMB, cold TME | -5 points |

### Step 7.2: ICI-Sensitivity Mutations (BONUS)

| Gene | Mutation | Cancer Context | Mechanism | Bonus |
|------|----------|---------------|-----------|-------|
| POLE | Exonuclease domain | Any | Ultramutation, high neoantigens | +10 points |
| POLD1 | Proofreading domain | Any | Ultramutation | +5 points |
| BRCA1/2 | Loss of function | Multiple | Genomic instability | +3 points |
| ARID1A | Loss of function | Multiple | Chromatin remodeling, TME | +3 points |
| PBRM1 | Loss of function | RCC | ICI response in RCC | +5 points (RCC only) |

### Step 7.3: Driver Mutation Context

```python
# For each mutation, check CIViC evidence for ICI context
# Use OpenTargets for drug associations
result = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(efoId='EFO_0000756', size=50)
# Filter for ICI drugs (pembro, nivo, ipi, atezo, durva, avelumab, cemiplimab)
```

### Step 7.4: DNA Damage Repair (DDR) Pathway

Check if mutations are in DDR genes (associated with ICI response):
- **ATM, ATR, CHEK1, CHEK2** - DNA damage sensing
- **BRCA1, BRCA2, PALB2** - homologous recombination
- **RAD50, MRE11, NBN** - double-strand break repair
- **POLE, POLD1** - polymerase proofreading

DDR mutations -> likely higher TMB -> better ICI response

---

## Phase 8: Clinical Evidence & ICI Options

### Step 8.1: FDA-Approved ICIs

```python
# Get FDA indications for key ICIs
ici_drugs = ['pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab', 'ipilimumab', 'avelumab', 'cemiplimab']

for drug in ici_drugs:
    result = tu.tools.FDA_get_indications_by_drug_name(drug_name=drug, limit=3)
    # Extract cancer-specific indications
```

### Step 8.2: ICI Drug Profiles

| Drug | Target | Type | Key Indications |
|------|--------|------|-----------------|
| Pembrolizumab (Keytruda) | PD-1 | IgG4 mAb | Melanoma, NSCLC, HNSCC, Bladder, MSI-H, TMB-H, many others |
| Nivolumab (Opdivo) | PD-1 | IgG4 mAb | Melanoma, NSCLC, RCC, CRC (MSI-H), HCC, HNSCC |
| Atezolizumab (Tecentriq) | PD-L1 | IgG1 mAb | NSCLC, Bladder, HCC, Melanoma |
| Durvalumab (Imfinzi) | PD-L1 | IgG1 mAb | NSCLC (Stage III), Bladder, HCC, BTC |
| Ipilimumab (Yervoy) | CTLA-4 | IgG1 mAb | Melanoma, RCC (combo), CRC (MSI-H combo) |
| Avelumab (Bavencio) | PD-L1 | IgG1 mAb | Merkel cell, Bladder (maintenance) |
| Cemiplimab (Libtayo) | PD-1 | IgG4 mAb | CSCC, NSCLC, Basal cell |
| Dostarlimab (Jemperli) | PD-1 | IgG4 mAb | dMMR endometrial, dMMR solid tumors |
| Tremelimumab (Imjudo) | CTLA-4 | IgG2 mAb | HCC (combo with durva) |

### Step 8.3: Clinical Trial Evidence

```python
# Search for ICI trials in this cancer type
result = tu.tools.clinical_trials_search(
    action='search_studies',
    condition='melanoma',
    intervention='pembrolizumab',
    limit=10
)
# Returns: {total_count, studies: [{nctId, title, status, conditions}]}
```

### Step 8.4: Literature Evidence

```python
# Search PubMed for biomarker-specific ICI response data
result = tu.tools.PubMed_search_articles(
    query='pembrolizumab melanoma TMB response biomarker',
    max_results=10
)
# Returns list of {pmid, title, ...}
```

### Step 8.5: OpenTargets Drug-Target Evidence

```python
# Get drug mechanism details
result = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(chemblId='CHEMBL3137343')
# -> pembrolizumab: PD-1 inhibitor, targets PDCD1 (ENSG00000188389)
```

### Key ICI ChEMBL IDs

| Drug | ChEMBL ID |
|------|-----------|
| Pembrolizumab | CHEMBL3137343 |
| Nivolumab | CHEMBL2108738 |
| Atezolizumab | CHEMBL3707227 |
| Durvalumab | CHEMBL3301587 |
| Ipilimumab | CHEMBL1789844 |
| Avelumab | CHEMBL3833373 |
| Cemiplimab | CHEMBL4297723 |

---

## Phase 9: Resistance Risk Assessment

### Step 9.1: Known Resistance Factors Check

For each mutation in the patient profile, check against resistance database:

```python
# Check for resistance evidence in CIViC
# CIViC evidence types: PREDICTIVE, PROGNOSTIC, DIAGNOSTIC, PREDISPOSING, ONCOGENIC
result = tu.tools.civic_search_evidence_items(therapy_name='pembrolizumab')
# Filter for resistance-associated evidence
```

### Step 9.2: Pathway-Level Resistance

| Pathway | Resistance Mechanism | Genes |
|---------|---------------------|-------|
| IFN-g signaling | Loss of IFN-g response | JAK1, JAK2, STAT1, IRF1 |
| Antigen presentation | MHC-I downregulation | B2M, TAP1, TAP2, HLA-A/B/C |
| WNT/b-catenin | T cell exclusion | CTNNB1 activating mutations |
| MAPK pathway | Immune suppression | MEK, ERK hyperactivation |
| PI3K/AKT/mTOR | Immune suppression | PTEN loss, PIK3CA |

### Step 9.3: Resistance Risk Score

Summarize resistance risk as:
- **Low risk**: No resistance mutations, favorable TME
- **Moderate risk**: 1 resistance factor OR uncertain TME
- **High risk**: Multiple resistance mutations OR known resistant phenotype

---

## Phase 10: Multi-Biomarker Score Integration

### ICI Response Score Calculation (0-100)

```
TOTAL SCORE = TMB_score + MSI_score + PDL1_score + Neoantigen_score + Mutation_bonus + Resistance_penalty

Where:
  TMB_score:        5-30 points (based on TMB classification)
  MSI_score:        5-25 points (based on MSI status)
  PDL1_score:       5-20 points (based on PD-L1 level)
  Neoantigen_score: 5-15 points (based on estimated neoantigens)
  Mutation_bonus:   0-10 points (POLE, PBRM1, etc.)
  Resistance_penalty: -20 to 0 points (STK11, PTEN, JAK1/2, B2M)

Minimum score: 0 (floor)
Maximum score: 100 (cap)
```

### Response Likelihood Tiers

| Score Range | Tier | Expected ORR | Recommendation |
|-------------|------|-------------|----------------|
| 70-100 | HIGH | 50-80% | Strong ICI candidate; monotherapy or combo |
| 40-69 | MODERATE | 20-50% | Consider ICI; combo preferred; monitor closely |
| 0-39 | LOW | <20% | ICI alone unlikely effective; consider alternatives |

### Confidence Level

| Data Completeness | Confidence |
|-------------------|-----------|
| All biomarkers (TMB + MSI + PD-L1 + mutations) | HIGH |
| 3 of 4 biomarkers | MODERATE-HIGH |
| 2 of 4 biomarkers | MODERATE |
| 1 biomarker only | LOW |
| Cancer type only | VERY LOW |

---

## Phase 11: Clinical Recommendations

### Step 11.1: ICI Drug Selection Algorithm

```
IF MSI-H:
  -> Pembrolizumab (tissue-agnostic FDA approval)
  -> Nivolumab (CRC-specific)
  -> Consider nivo+ipi combination

IF TMB-H (>=10) and not MSI-H:
  -> Pembrolizumab (tissue-agnostic for TMB-H)

IF Cancer = Melanoma:
  IF PD-L1 >= 1%: pembrolizumab or nivolumab monotherapy
  ELSE: nivolumab + ipilimumab combination
  IF BRAF V600E: consider targeted therapy first if rapid response needed

IF Cancer = NSCLC:
  IF PD-L1 >= 50% and no STK11/EGFR: pembrolizumab monotherapy
  IF PD-L1 1-49%: pembrolizumab + chemotherapy
  IF PD-L1 < 1%: ICI + chemotherapy combination
  IF STK11 loss: ICI less likely effective
  IF EGFR/ALK positive: targeted therapy preferred over ICI

IF Cancer = RCC:
  -> Nivolumab + ipilimumab (IMDC intermediate/poor risk)
  -> Pembrolizumab + axitinib (all risk)

IF Cancer = Bladder:
  -> Pembrolizumab or atezolizumab (2L)
  -> Avelumab maintenance post-platinum
```

### Step 11.2: Monitoring Plan

**During ICI treatment, monitor**:
- Tumor response (CT/MRI every 8-12 weeks)
- Circulating tumor DNA (ctDNA) for early response
- Immune-related adverse events (irAEs)
- Thyroid function (TSH every 6 weeks)
- Liver function (every 2-4 weeks initially)
- Cortisol if symptoms

**Early response biomarkers**:
- ctDNA decrease at 4-6 weeks
- PET-CT metabolic response
- Circulating immune cell phenotyping

### Step 11.3: Alternative Strategies

If ICI response predicted to be LOW:
1. **Targeted therapy** (if actionable mutations: BRAF, EGFR, ALK, ROS1)
2. **Chemotherapy** (standard of care)
3. **ICI + chemotherapy combination** (may overcome low PD-L1)
4. **ICI + anti-angiogenic** (may convert cold to hot tumor)
5. **ICI + CTLA-4 combo** (nivolumab + ipilimumab)
6. **Clinical trial enrollment** (novel combinations)

---

## Output Report Format

Save report as `immunotherapy_response_prediction_{cancer_type}.md`

### Report Structure

```markdown
# Immunotherapy Response Prediction Report

## Executive Summary
[2-3 sentence summary: cancer type, ICI Response Score, recommendation]

## ICI Response Score: XX/100
**Response Likelihood: [HIGH/MODERATE/LOW]**
**Confidence: [HIGH/MODERATE/LOW]**
**Expected ORR: XX-XX%**

### Score Breakdown
| Component | Value | Score | Max |
|-----------|-------|-------|-----|
| TMB | XX mut/Mb | XX | 30 |
| MSI Status | MSI-H/MSS | XX | 25 |
| PD-L1 | XX% | XX | 20 |
| Neoantigen Load | XX est. | XX | 15 |
| Sensitivity Bonus | +XX | XX | 10 |
| Resistance Penalty | -XX | XX | -20 |
| **TOTAL** | | **XX** | **100** |

## Patient Profile
- **Cancer Type**: [cancer]
- **Mutations**: [list]
- **TMB**: XX mut/Mb [classification]
- **MSI Status**: [MSI-H/MSS/Unknown]
- **PD-L1**: XX% [scoring method]

## Biomarker Analysis

### TMB Analysis
[TMB classification, cancer-specific context, FDA TMB-H status]

### MSI/MMR Status
[MSI status, MMR gene mutations, FDA MSI-H approvals]

### PD-L1 Expression
[PD-L1 level, cancer-specific thresholds, scoring method]

### Neoantigen Burden
[Estimated neoantigen count, quality assessment, mutation types]

## Mutation Analysis

### Driver Mutations
[Analysis of each mutation - oncogenic role, ICI implications]

### Resistance Mutations
[Any STK11, PTEN, JAK1/2, B2M, KEAP1 etc. with penalties]

### Sensitivity Mutations
[Any POLE, PBRM1, DDR genes with bonuses]

## Immune Microenvironment
[Hot/cold classification, immune gene expression data]

## ICI Drug Recommendation

### Primary Recommendation
**[Drug name]** - [monotherapy/combination]
- Evidence: [FDA approval, trial data]
- Expected response: XX-XX%
- Key trial: [trial name/NCT#]

### Alternative Options
1. [Alternative 1] - [rationale]
2. [Alternative 2] - [rationale]

### Combination Strategies
[ICI+ICI, ICI+chemo, ICI+targeted recommendations]

## Clinical Evidence
[Key trials, response rates, PFS/OS data for this cancer + biomarker profile]

## Resistance Risk
- **Risk Level**: [LOW/MODERATE/HIGH]
- **Key Factors**: [list resistance mutations/mechanisms]
- **Mitigation**: [combination strategies]

## Monitoring Plan
- **Response assessment**: [schedule]
- **Biomarkers to track**: [ctDNA, imaging, labs]
- **irAE monitoring**: [schedule]
- **Resistance monitoring**: [when to suspect progression]

## Alternative Strategies (if ICI unlikely effective)
[Targeted therapy, chemotherapy, clinical trials]

## Evidence Grading
| Finding | Evidence Tier | Source |
|---------|-------------|--------|
| [finding 1] | T1 (FDA/Guidelines) | [source] |
| [finding 2] | T2 (Clinical trial) | [source] |

## Data Completeness
| Biomarker | Status | Impact |
|-----------|--------|--------|
| TMB | Provided/Estimated/Unknown | XX points |
| MSI | Provided/Unknown | XX points |
| PD-L1 | Provided/Unknown | XX points |
| Neoantigen | Estimated | XX points |
| Mutations | X provided | +/-XX points |

## Missing Data Recommendations
[What additional tests would improve prediction accuracy]

---
*Generated by ToolUniverse Immunotherapy Response Prediction Skill*
*Sources: OpenTargets, CIViC, FDA, DrugBank, PubMed, IEDB, HPA, cBioPortal*
```

---

## Evidence Tiers

| Tier | Description | Source Examples |
|------|-------------|----------------|
| T1 | FDA-approved biomarker/indication | FDA labels, NCCN guidelines |
| T2 | Phase 2-3 clinical trial evidence | Published trial data, PubMed |
| T3 | Preclinical/computational evidence | Pathway analysis, in vitro data |
| T4 | Expert opinion/case reports | Case series, reviews |

---

## Use Case Examples

### Use Case 1: NSCLC with High TMB
**Input**: "NSCLC, TMB 25, PD-L1 80%, no STK11 mutation"
**Expected**: ICI Score 70-85, HIGH response, pembrolizumab monotherapy recommended

### Use Case 2: Melanoma with BRAF
**Input**: "Melanoma, BRAF V600E, TMB 15, PD-L1 50%"
**Expected**: ICI Score 50-65, MODERATE response, discuss ICI vs BRAF-targeted

### Use Case 3: MSI-H Colorectal
**Input**: "Colorectal cancer, MSI-high, TMB 40"
**Expected**: ICI Score 80-95, HIGH response, pembrolizumab first-line

### Use Case 4: Low Biomarker NSCLC
**Input**: "NSCLC, TMB 2, PD-L1 <1%, STK11 mutation"
**Expected**: ICI Score 5-20, LOW response, chemotherapy preferred

### Use Case 5: Bladder Cancer
**Input**: "Bladder cancer, TMB 12, PD-L1 10%, no resistance mutations"
**Expected**: ICI Score 45-55, MODERATE response, ICI+chemo or maintenance

### Use Case 6: Checkpoint Inhibitor Selection
**Input**: "Which ICI for NSCLC with PD-L1 90%?"
**Expected**: Pembrolizumab monotherapy first-line, evidence from KEYNOTE-024

---

## Completeness Checklist

Before finalizing the report, verify:

- [ ] Cancer type resolved to EFO ID
- [ ] All mutations parsed and genes resolved
- [ ] TMB classified with cancer-specific context
- [ ] MSI/MMR status assessed
- [ ] PD-L1 integrated (or flagged as unknown)
- [ ] Neoantigen burden estimated
- [ ] Resistance mutations checked (STK11, PTEN, JAK1/2, B2M, KEAP1)
- [ ] Sensitivity mutations checked (POLE, PBRM1, DDR)
- [ ] FDA-approved ICIs identified for this cancer
- [ ] Clinical trial evidence retrieved
- [ ] ICI Response Score calculated with component breakdown
- [ ] Drug recommendation provided with evidence
- [ ] Monitoring plan included
- [ ] Alternative strategies for low responders
- [ ] Evidence grading applied to all findings
- [ ] Data completeness documented
- [ ] Missing data recommendations provided
- [ ] Report saved to file
