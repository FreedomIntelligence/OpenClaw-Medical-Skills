# tooluniverse-precision-medicine-stratification

> Comprehensive patient stratification for precision medicine by integrating genomic, clinical, and therapeutic data. Given a disease/condition, genomic data (germline variants, somatic mutations, expression), and optional clinical parameters, performs multi-phase analysis across 9 phases covering disease disambiguation, genetic risk assessment, disease-specific molecular stratification, pharmacogenomic profiling, comorbidity/DDI risk, pathway analysis, clinical evidence and guideline mapping, clinical trial matching, and integrated outcome prediction. Generates a quantitative Precision Medicine Risk Score (0-100) with risk tier assignment (Low/Intermediate/High/Very High), treatment algorithm (1st/2nd/3rd line), pharmacogenomic guidance, clinical trial matches, and monitoring plan. Use when clinicians ask about patient risk stratification, treatment selection, prognosis prediction, or personalized therapeutic strategy across cancer, metabolic, cardiovascular, neurological, or rare diseases.

# Precision Medicine Patient Stratification

Transform patient genomic and clinical profiles into actionable risk stratification, treatment recommendations, and personalized therapeutic strategies. Integrates germline genetics, somatic alterations, pharmacogenomics, pathway biology, and clinical evidence to produce a quantitative risk score with tiered management recommendations.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Disease-specific logic** - Cancer vs metabolic vs rare disease pipelines diverge at Phase 2
3. **Multi-level integration** - Germline + somatic + expression + clinical data layers
4. **Evidence-graded** - Every finding has an evidence tier (T1-T4)
5. **Quantitative output** - Precision Medicine Risk Score (0-100) with transparent components
6. **Pharmacogenomic guidance** - Drug selection AND dosing recommendations
7. **Guideline-concordant** - Reference NCCN, ACC/AHA, ADA, and other guidelines
8. **Source-referenced** - Every statement cites the tool/database source
9. **Completeness checklist** - Mandatory section showing data availability and analysis coverage
10. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use

Apply when user asks:
- "Stratify this breast cancer patient: ER+/HER2-, BRCA1 mutation, stage II"
- "What is the risk profile for this diabetes patient with HbA1c 8.5 and CYP2C19 poor metabolizer?"
- "NSCLC patient with EGFR L858R, stage IV, TMB 25 - treatment strategy?"
- "Predict prognosis and recommend treatment for this cardiovascular patient"
- "Patient has Marfan syndrome with FBN1 mutation - risk stratification"
- "Alzheimer's risk assessment: APOE e4/e4, family history positive"
- "Personalized treatment plan for type 2 diabetes with genetic risk factors"
- "Which therapy is best for this patient's molecular profile?"

**NOT for** (use other skills instead):
- Single variant interpretation -> Use `tooluniverse-variant-interpretation` or `tooluniverse-cancer-variant-interpretation`
- Immunotherapy-specific prediction -> Use `tooluniverse-immunotherapy-response-prediction`
- Drug safety profiling only -> Use `tooluniverse-adverse-event-detection`
- Target validation -> Use `tooluniverse-drug-target-validation`
- Clinical trial search only -> Use `tooluniverse-clinical-trial-matching`
- Drug-drug interaction analysis only -> Use `tooluniverse-drug-drug-interaction`
- PRS calculation only -> Use `tooluniverse-polygenic-risk-score`

---

## Input Parsing

### Required Input
- **Disease/condition**: Free-text disease name (e.g., "breast cancer", "type 2 diabetes", "Marfan syndrome")
- **At least one of**: Germline variants, somatic mutations, gene list, or clinical biomarkers

### Strongly Recommended
- **Genomic data**: Specific variants (e.g., "BRCA1 c.68_69delAG", "EGFR L858R"), gene names, or expression changes
- **Clinical parameters**: Age, sex, disease stage, biomarkers (HbA1c, PSA, LDL-C)

### Optional (improves stratification)
- **Comorbidities**: Other conditions (e.g., "hypertension", "diabetes")
- **Prior treatments**: Previous therapies and responses
- **Family history**: Affected relatives, inheritance pattern
- **Ethnicity**: For population-specific risk calibration
- **Current medications**: For DDI and pharmacogenomic analysis
- **Stratification goal**: Risk assessment, treatment selection, prognosis, prevention

### Input Format Examples

| Format | Example | How to Parse |
|--------|---------|-------------|
| Cancer + mutations + stage | "Breast cancer, BRCA1 mut, ER+, HER2-, stage II" | disease=breast_cancer, mutations=[BRCA1], biomarkers={ER:+, HER2:-}, stage=II |
| Metabolic + biomarkers + PGx | "T2D, HbA1c 8.5, CYP2C19 *2/*2" | disease=T2D, biomarkers={HbA1c:8.5}, pgx={CYP2C19:poor_metabolizer} |
| CVD risk profile | "High LDL 190, SLCO1B1*5, family hx MI" | disease=CVD, biomarkers={LDL:190}, pgx={SLCO1B1:*5}, family_hx=positive |
| Rare disease + variant | "Marfan, FBN1 c.4082G>A" | disease=Marfan, mutations=[FBN1 c.4082G>A], disease_type=rare |
| Neuro risk | "Alzheimer risk, APOE e4/e4, age 55" | disease=AD, genotype={APOE:e4/e4}, clinical={age:55} |
| Cancer + comprehensive | "NSCLC, EGFR L858R, TMB 25, PD-L1 80%, stage IV" | disease=NSCLC, mutations=[EGFR L858R], biomarkers={TMB:25, PDL1:80}, stage=IV |

### Disease Type Classification

Classify the disease into one of these categories (determines Phase 2 routing):

| Category | Examples | Key Stratification Axes |
|----------|----------|------------------------|
| **CANCER** | Breast, lung, colorectal, melanoma, prostate | Stage, molecular subtype, TMB, driver mutations, hormone receptors |
| **METABOLIC** | Type 2 diabetes, obesity, metabolic syndrome, NAFLD | HbA1c, BMI, genetic risk, comorbidities, CYP genotypes |
| **CARDIOVASCULAR** | CAD, heart failure, atrial fibrillation, hypertension | ASCVD risk, LDL, genetic risk, statin PGx, anticoagulant PGx |
| **NEUROLOGICAL** | Alzheimer, Parkinson, epilepsy, multiple sclerosis | APOE status, genetic risk, age of onset, PGx for anticonvulsants |
| **RARE/MONOGENIC** | Marfan, CF, sickle cell, Huntington, PKU | Causal variant, penetrance, genotype-phenotype correlation |
| **AUTOIMMUNE** | RA, lupus, MS, Crohn's, ulcerative colitis | HLA associations, genetic risk, biologics PGx |

### Gene Symbol Normalization

| Common Alias | Official Symbol | Notes |
|-------------|----------------|-------|
| HER2 | ERBB2 | Breast cancer biomarker |
| PD-L1 | CD274 | Immunotherapy biomarker |
| EGFR | EGFR | Lung cancer driver |
| BRCA1/2 | BRCA1, BRCA2 | Hereditary cancer |
| CYP2D6 | CYP2D6 | Drug metabolism |
| CYP2C19 | CYP2C19 | Clopidogrel, PPIs |
| CYP3A4 | CYP3A4 | Major drug metabolism |
| VKORC1 | VKORC1 | Warfarin dosing |
| SLCO1B1 | SLCO1B1 | Statin myopathy |
| DPYD | DPYD | Fluoropyrimidine toxicity |
| UGT1A1 | UGT1A1 | Irinotecan toxicity |
| TPMT | TPMT | Thiopurine toxicity |

---

## Phase 0: Tool Parameter Reference (CRITICAL)

**BEFORE calling ANY tool**, verify parameters using this reference table.

### Verified Tool Parameters

| Tool | Parameters | Response Structure | Notes |
|------|-----------|-------------------|-------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` | `{data: {search: {hits: [{id, name, description}]}}}` | Disease to EFO ID |
| `OpenTargets_get_drug_id_description_by_name` | `drugName` | `{data: {search: {hits: [{id, name, description}]}}}` | Drug to ChEMBL ID |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | `efoId`, `size` | `{data: {disease: {knownDrugs: {count, rows}}}}` | Drugs for disease |
| `OpenTargets_get_associated_targets_by_disease_efoId` | `efoId`, `size` | `{data: {disease: {associatedTargets: {count, rows}}}}` | Genetic associations |
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId` | `{data: {drug: {mechanismsOfAction: {rows}}}}` | Drug MOA |
| `OpenTargets_get_approved_indications_by_drug_chemblId` | `chemblId` | Approved indications list | Check drug approvals |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | `chemblId` | `{data: {drug: {adverseEvents: {count, rows}}}}` | Drug safety |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId`, `size` | Drug-target associations | Drugs targeting gene |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | `ensemblId` | Safety profile data | Target safety |
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensemblId` | Tractability assessment | Druggability |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | `ensemblId` | Disease-phenotype associations | Gene-disease links |
| `OpenTargets_target_disease_evidence` | `ensemblId`, `efoId`, `size` | Evidence for target-disease pair | Specific gene-disease evidence |
| `OpenTargets_search_gwas_studies_by_disease` | `diseaseIds` (array), `size` | `{data: {studies: {count, rows}}}` | GWAS studies |
| `OpenTargets_drug_pharmacogenomics_data` | `chemblId` | Pharmacogenomic data | Drug PGx |
| `MyGene_query_genes` | `query` (NOT `q`) | `{hits: [{_id, symbol, name, ensembl: {gene}}]}` | Gene resolution |
| `ensembl_lookup_gene` | `gene_id`, `species='homo_sapiens'` | `{data: {id, display_name, description, biotype}}` | REQUIRES species |
| `EnsemblVEP_annotate_rsid` | `variant_id` (NOT `rsid`) | VEP annotation with SIFT/PolyPhen | Variant impact |
| `EnsemblVEP_annotate_hgvs` | `hgvs_notation`, `species` | VEP annotation | HGVS variant annotation |
| `ensembl_get_variation` | `variant_id`, `species` | Variant details | rsID lookup |
| `clinvar_search_variants` | `gene`, `significance`, `limit` | Variant list | Search ClinVar |
| `clinvar_get_variant_details` | `variant_id` | Variant details with clinical significance | ClinVar details |
| `clinvar_get_clinical_significance` | `variant_id` | Clinical significance only | Quick pathogenicity |
| `civic_search_evidence_items` | `therapy_name`, `disease_name` | `{data: {evidenceItems: {nodes}}}` | Clinical evidence |
| `civic_search_variants` | `name`, `gene_name` | `{data: {variants: {nodes}}}` | Variant clinical significance |
| `civic_search_assertions` | `therapy_name`, `disease_name` | `{data: {assertions: {nodes}}}` | Clinical assertions |
| `cBioPortal_get_mutations` | `study_id`, `gene_list` (STRING, not array) | `{status, data: [{...}]}` | Somatic mutation data |
| `gwas_get_associations_for_trait` | `trait` | GWAS associations | Trait-SNP associations |
| `gwas_search_associations` | `query` | GWAS associations | Broad GWAS search |
| `gwas_get_snps_for_gene` | `gene` | SNPs associated with gene | Gene GWAS hits |
| `GWAS_search_associations_by_gene` | `gene_name` | Gene GWAS associations | Gene-trait links |
| `PharmGKB_get_clinical_annotations` | `query` | Clinical annotations | Drug-gene-phenotype |
| `PharmGKB_get_dosing_guidelines` | `query` | Dosing guidelines | PGx dosing |
| `PharmGKB_search_variants` | `query` | Variant PGx data | PGx variant search |
| `PharmGKB_get_gene_details` | `query` | Gene PGx details | PGx gene info |
| `PharmGKB_get_drug_details` | `query` | Drug PGx details | Drug PGx info |
| `fda_pharmacogenomic_biomarkers` | `drug_name`, `biomarker`, `limit` | `{count, shown, results: [{Drug, Biomarker, ...}]}` | FDA PGx biomarkers |
| `FDA_get_pharmacogenomics_info_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | FDA PGx label info |
| `FDA_get_indications_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | FDA indications |
| `FDA_get_clinical_studies_info_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Clinical study data |
| `FDA_get_contraindications_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Contraindications |
| `FDA_get_warnings_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | Warnings |
| `FDA_get_boxed_warning_info_by_drug_name` | `drug_name`, `limit` | May return NOT_FOUND | Boxed warnings |
| `FDA_get_drug_interactions_by_drug_name` | `drug_name`, `limit` | `{meta, results}` | DDI info |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Drug basic info | ALL 4 REQUIRED |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Drug targets | ALL 4 REQUIRED |
| `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Pharmacology | ALL 4 REQUIRED |
| `drugbank_get_indications_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Indications | ALL 4 REQUIRED |
| `drugbank_get_drug_interactions_by_drug_name_or_id` | `query`, `case_sensitive`, `exact_match`, `limit` | DDI data | ALL 4 REQUIRED |
| `drugbank_get_safety_by_drug_name_or_drugbank_id` | `query`, `case_sensitive`, `exact_match`, `limit` | Safety data | ALL 4 REQUIRED |
| `enrichr_gene_enrichment_analysis` | `gene_list` (array), `libs` (array, REQUIRED) | Enrichment results | Key libs: `KEGG_2021_Human`, `Reactome_2022`, `GO_Biological_Process_2023` |
| `ReactomeAnalysis_pathway_enrichment` | `identifiers` (space-separated string) | `{data: {pathways: [{pathway_id, name, p_value, ...}]}}` | Pathway enrichment |
| `Reactome_map_uniprot_to_pathways` | `id` (UniProt accession) | List of pathways | Gene-to-pathway |
| `STRING_get_interaction_partners` | `protein_ids` (array), `species` (9606), `limit` | Interaction partners | PPI network |
| `STRING_functional_enrichment` | `protein_ids` (array), `species` (9606) | Functional enrichment | Network enrichment |
| `HPA_get_cancer_prognostics_by_gene` | `gene_name` | Cancer prognostic data | Prognostic markers |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` (ALL 3) | Expression data | Tissue expression |
| `gnomad_get_gene_constraints` | `gene_symbol` | Gene constraint metrics | LoF intolerance |
| `gnomad_get_variant` | `variant_id` | Variant frequency | Population frequency |
| `clinical_trials_search` | `action='search_studies'`, `condition`, `intervention`, `limit` | `{total_count, studies}` | Trial search |
| `search_clinical_trials` | `query_term` (REQUIRED), `condition`, `intervention`, `pageSize` | `{studies, total_count}` | Alternative trial search |
| `PubMed_search_articles` | `query`, `max_results` | Plain list of dicts | Literature |
| `PubMed_Guidelines_Search` | `query`, `limit` (REQUIRED) | List of guideline articles | Clinical guidelines (may require API key) |
| `UniProt_get_function_by_accession` | `accession` | List of strings | Protein function |
| `UniProt_get_disease_variants_by_accession` | `accession` | Disease variants | Known pathogenic variants |

### Response Format Notes

- **OpenTargets**: Always nested `{data: {entity: {field: ...}}}` structure
- **FDA label tools**: Return `{meta: {disclaimer, terms, license, ...}, results: [...]}`. Access via `result['results'][0]['field']`
- **DrugBank**: ALL tools require 4 params: `query`, `case_sensitive` (bool), `exact_match` (bool), `limit` (int)
- **PharmGKB**: Returns complex nested objects. Check for `data` wrapper
- **PubMed_search_articles**: Returns a **plain list** of dicts, NOT `{articles: [...]}`
- **ClinVar**: `clinvar_search_variants` returns list of variants with clinical significance
- **gnomAD**: May return "Service overloaded" - treat as transient, retry or skip
- **fda_pharmacogenomic_biomarkers**: Default limit=10, use `limit=1000` to get all
- **cBioPortal_get_mutations**: `gene_list` is a STRING, not array. cBioPortal tools may have URL bugs
- **ClinVar**: May return either a plain list or `{status, data: {esearchresult: {count, idlist}}}` - handle both
- **EnsemblVEP**: May return either a list `[{...}]` or `{data: {...}, metadata: {...}}` - handle both
- **PubMed_Guidelines_Search**: Requires `limit` parameter (NOT `max_results`), may require API key. Use `PubMed_search_articles` as fallback
- **gwas_get_associations_for_trait**: May return errors; use `gwas_search_associations` instead
- **MyGene CYP2D6**: First result may be LOC110740340; always filter by `symbol` match

---

## Workflow Overview

```
Input: Disease + Genomic data + Clinical parameters + Stratification goal

Phase 1: Disease Disambiguation & Profile Standardization
  - Resolve disease to EFO/MONDO IDs
  - Classify disease type (cancer/metabolic/CVD/neuro/rare/autoimmune)
  - Parse genomic data (variants, genes, expression)
  - Resolve gene IDs (Ensembl, Entrez, UniProt)

Phase 2: Genetic Risk Assessment
  - Germline variant pathogenicity (ClinVar, VEP)
  - Gene-disease association strength (OpenTargets)
  - GWAS-based polygenic risk estimation
  - Population frequency (gnomAD)
  - Gene constraint/intolerance (gnomAD)

Phase 3: Disease-Specific Molecular Stratification
  CANCER PATH:
    - Molecular subtyping (driver mutations, receptor status)
    - Prognostic markers (stage + grade + molecular)
    - TMB/MSI/HRD assessment
    - Somatic mutation landscape (cBioPortal)
  METABOLIC PATH:
    - Genetic risk + clinical risk integration
    - Complication risk (nephropathy, neuropathy, CVD)
    - Monogenic subtypes (MODY, lipodystrophy)
  CVD PATH:
    - ASCVD risk integration
    - Familial hypercholesterolemia genes
    - Statin/anticoagulant PGx
  RARE DISEASE PATH:
    - Causal variant identification
    - Genotype-phenotype correlation
    - Penetrance estimation

Phase 4: Pharmacogenomic Profiling
  - Drug-metabolizing enzyme genotypes (CYP2D6, CYP2C19, CYP3A4)
  - Drug transporter variants (SLCO1B1, ABCB1)
  - Drug target variants (VKORC1, DPYD, UGT1A1)
  - HLA alleles (drug hypersensitivity risk)
  - PharmGKB clinical annotations
  - FDA pharmacogenomic biomarkers

Phase 5: Comorbidity & Drug Interaction Risk
  - Disease-disease genetic overlap
  - Impact on treatment selection
  - Drug-drug interaction risk
  - Pharmacogenomic DDI amplification

Phase 6: Molecular Pathway Analysis
  - Dysregulated pathway identification (Reactome, KEGG)
  - Network disruption analysis (STRING)
  - Druggable pathway targets
  - Pathway-based therapeutic opportunities

Phase 7: Clinical Evidence & Guidelines
  - Guideline-based risk categories (NCCN, ACC/AHA, ADA)
  - FDA-approved therapies for patient profile
  - Literature evidence (PubMed)
  - Biomarker-guided treatment evidence

Phase 8: Clinical Trial Matching
  - Trials matching molecular profile
  - Biomarker-driven trials
  - Precision medicine basket/umbrella trials
  - Risk-adapted trials

Phase 9: Integrated Scoring & Recommendations
  - Calculate Precision Medicine Risk Score (0-100)
  - Risk tier assignment (Low/Int/High/Very High)
  - Treatment algorithm (1st/2nd/3rd line)
  - Monitoring plan
  - Outcome predictions
```

---

## Phase 1: Disease Disambiguation & Profile Standardization

### Step 1.1: Resolve Disease to EFO ID

```python
# Get disease EFO ID
result = tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName='breast cancer')
# -> {data: {search: {hits: [{id: 'EFO_0000305', name: 'breast carcinoma', description: '...'}]}}}
efo_id = result['data']['search']['hits'][0]['id']
```

**Common Disease EFO IDs** (for reference):

| Disease | EFO ID | Category |
|---------|--------|----------|
| Breast carcinoma | EFO_0000305 | CANCER |
| Non-small cell lung carcinoma | EFO_0003060 | CANCER |
| Colorectal cancer | EFO_0000365 | CANCER |
| Melanoma | EFO_0000756 | CANCER |
| Prostate carcinoma | EFO_0001663 | CANCER |
| Type 2 diabetes | EFO_0001360 | METABOLIC |
| Coronary artery disease | EFO_0001645 | CVD |
| Atrial fibrillation | EFO_0000275 | CVD |
| Alzheimer disease | MONDO_0004975 | NEUROLOGICAL |
| Parkinson disease | EFO_0002508 | NEUROLOGICAL |
| Rheumatoid arthritis | EFO_0000685 | AUTOIMMUNE |
| Marfan syndrome | Orphanet_558 | RARE |
| Cystic fibrosis | EFO_0000508 | RARE |

### Step 1.2: Classify Disease Type

Based on disease name and EFO ID, classify into: CANCER, METABOLIC, CVD, NEUROLOGICAL, RARE, AUTOIMMUNE. This determines the Phase 3 routing.

### Step 1.3: Parse Genomic Data

Parse each variant/gene into structured format:
```
"BRCA1 c.68_69delAG" -> {gene: "BRCA1", variant: "c.68_69delAG", type: "frameshift"}
"EGFR L858R" -> {gene: "EGFR", variant: "L858R", type: "missense"}
"CYP2C19 *2/*2" -> {gene: "CYP2C19", genotype: "*2/*2", metabolizer_status: "poor"}
"APOE e4/e4" -> {gene: "APOE", genotype: "e4/e4", risk_allele: "e4"}
```

### Step 1.4: Resolve Gene IDs

```python
# For each gene in profile
result = tu.tools.MyGene_query_genes(query='BRCA1')
# -> hits[0]: {_id: '672', symbol: 'BRCA1', ensembl: {gene: 'ENSG00000012048'}}
ensembl_id = result['hits'][0]['ensembl']['gene']
entrez_id = result['hits'][0]['_id']
```

**Critical Gene IDs** (pre-resolved):

| Gene | Ensembl ID | Entrez ID | Category |
|------|-----------|-----------|----------|
| BRCA1 | ENSG00000012048 | 672 | Cancer predisposition |
| BRCA2 | ENSG00000139618 | 675 | Cancer predisposition |
| TP53 | ENSG00000141510 | 7157 | Tumor suppressor |
| EGFR | ENSG00000146648 | 1956 | Cancer driver |
| BRAF | ENSG00000157764 | 673 | Cancer driver |
| KRAS | ENSG00000133703 | 3845 | Cancer driver |
| CYP2D6 | ENSG00000100197 | 1565 | Pharmacogenomics |
| CYP2C19 | ENSG00000165841 | 1557 | Pharmacogenomics |
| SLCO1B1 | ENSG00000134538 | 10599 | Pharmacogenomics |
| VKORC1 | ENSG00000167397 | 79001 | Pharmacogenomics |
| DPYD | ENSG00000188641 | 1806 | Pharmacogenomics |
| APOE | ENSG00000130203 | 348 | Neurological risk |
| LDLR | ENSG00000130164 | 3949 | CVD risk |
| PCSK9 | ENSG00000169174 | 255738 | CVD risk |
| FBN1 | ENSG00000166147 | 2200 | Marfan syndrome |
| CFTR | ENSG00000001626 | 1080 | Cystic fibrosis |

---

## Phase 2: Genetic Risk Assessment

### Step 2.1: Germline Variant Pathogenicity

For each germline variant provided:

```python
# Search ClinVar for variant pathogenicity
result = tu.tools.clinvar_search_variants(gene='BRCA1', significance='pathogenic', limit=50)
# Check if patient's specific variant is in ClinVar

# For rsID variants, get VEP annotation
result = tu.tools.EnsemblVEP_annotate_rsid(variant_id='rs80357906')
# Returns SIFT, PolyPhen predictions, consequence type

# For HGVS variants
result = tu.tools.EnsemblVEP_annotate_hgvs(hgvs_notation='ENST00000357654.9:c.5266dupC', species='homo_sapiens')
```

**Pathogenicity Classification** (ACMG-aligned):

| Classification | ClinVar Term | Risk Score Points |
|---------------|-------------|-------------------|
| Pathogenic | Pathogenic | 25 (molecular component) |
| Likely pathogenic | Likely pathogenic | 20 |
| VUS | Uncertain significance | 10 (conservative) |
| Likely benign | Likely benign | 2 |
| Benign | Benign | 0 |

### Step 2.2: Gene-Disease Association Strength

```python
# Get genetic evidence for gene-disease pair
result = tu.tools.OpenTargets_target_disease_evidence(
    ensemblId='ENSG00000012048',  # BRCA1
    efoId='EFO_0000305',         # breast cancer
    size=20
)
# Returns evidence items with scores
```

### Step 2.3: GWAS-Based Polygenic Risk

```python
# Search GWAS associations for disease
result = tu.tools.gwas_get_associations_for_trait(trait='breast cancer')
# Returns associated SNPs with effect sizes

# Search GWAS studies via OpenTargets
result = tu.tools.OpenTargets_search_gwas_studies_by_disease(
    diseaseIds=['EFO_0000305'], size=25
)

# For specific genes, check GWAS hits
result = tu.tools.GWAS_search_associations_by_gene(gene_name='BRCA1')
```

**PRS Estimation** (from available GWAS data):

| PRS Percentile | Risk Category | Score Points (0-35) |
|---------------|--------------|---------------------|
| >95th percentile | Very high genetic risk | 35 |
| 90-95th | High genetic risk | 30 |
| 75-90th | Elevated genetic risk | 25 |
| 50-75th | Average-high | 18 |
| 25-50th | Average-low | 12 |
| 10-25th | Below average | 8 |
| <10th | Low genetic risk | 5 |

**Note**: With user-provided variants only (not full genotype), estimate approximate PRS by counting known risk alleles and their effect sizes from GWAS catalog. Flag as "estimated - full genotyping recommended for precise PRS."

### Step 2.4: Population Frequency

```python
# Check variant frequency in gnomAD
result = tu.tools.gnomad_get_variant(variant_id='1-55505647-G-T')
# Returns allele frequency across populations
```

### Step 2.5: Gene Constraint

```python
# Gene intolerance to loss of function
result = tu.tools.gnomad_get_gene_constraints(gene_symbol='BRCA1')
# Returns pLI, LOEUF scores - high pLI/low LOEUF = haploinsufficiency
```

**Genetic Risk Score Component** (0-35 points):

Combine pathogenicity + gene-disease association + PRS:
- Pathogenic variant in disease gene: 25+ points
- Strong GWAS associations (multiple risk alleles): up to 35 points
- VUS in relevant gene: 10-15 points
- No known pathogenic variants but some risk alleles: 5-15 points

---

## Phase 3: Disease-Specific Molecular Stratification

### CANCER PATH (Phase 3C)

#### Step 3C.1: Molecular Subtyping

```python
# Get somatic mutation landscape from cBioPortal
result = tu.tools.cBioPortal_get_mutations(
    study_id='brca_tcga_pub',  # breast cancer TCGA
    gene_list='BRCA1 BRCA2 TP53 PIK3CA ESR1 ERBB2'  # STRING, not array
)
# Returns mutation frequencies, types

# Check cancer prognostic markers
result = tu.tools.HPA_get_cancer_prognostics_by_gene(gene_name='ESR1')
# Returns prognostic data for breast cancer
```

**Cancer-Specific Subtype Definitions**:

| Cancer | Subtype System | Key Markers | High-Risk Features |
|--------|---------------|-------------|-------------------|
| Breast | Luminal A/B, HER2+, TNBC | ER, PR, HER2, Ki67 | TNBC, high Ki67, TP53 mut |
| NSCLC | Adenocarcinoma, squamous | EGFR, ALK, ROS1, KRAS, PD-L1 | KRAS G12C, no driver = chemoIO |
| CRC | MSI-H vs MSS, CMS1-4 | KRAS, BRAF, MSI, CMS | BRAF V600E, MSS |
| Melanoma | BRAF-mut, NRAS-mut, wild-type | BRAF, NRAS, KIT, NF1 | NRAS, uveal |
| Prostate | Luminal vs basal, BRCA status | AR, BRCA1/2, SPOP, TMPRSS2:ERG | BRCA2, neuroendocrine |

#### Step 3C.2: TMB/MSI/HRD Assessment

If TMB provided:
```python
# Check FDA TMB-H approvals
result = tu.tools.fda_pharmacogenomic_biomarkers(drug_name='pembrolizumab', limit=100)
# Look for "Tumor Mutational Burden" in Biomarker field
```

| Biomarker | High-Risk Threshold | Clinical Significance |
|-----------|-------------------|----------------------|
| TMB | >= 10 mut/Mb (FDA cutoff) | Pembrolizumab eligible (tissue-agnostic) |
| MSI-H | MSI-high or dMMR | Pembrolizumab/nivolumab eligible |
| HRD | HRD-positive | PARP inhibitor eligible |

#### Step 3C.3: Prognostic Stratification

Combine stage + molecular features:

| Stage | Low-Risk Molecular | High-Risk Molecular | Score (0-30 clinical) |
|-------|-------------------|--------------------|-----------------------|
| I | Favorable subtype | Unfavorable subtype | 5-10 |
| II | Favorable subtype | Unfavorable subtype | 10-18 |
| III | Any | Any | 18-25 |
| IV | Any | Any | 25-30 |

### METABOLIC PATH (Phase 3M)

#### Step 3M.1: Clinical Risk Integration

```python
# Check genetic risk factors for T2D
result = tu.tools.GWAS_search_associations_by_gene(gene_name='TCF7L2')
# TCF7L2 is strongest T2D risk gene

# Check monogenic diabetes genes
result = tu.tools.OpenTargets_target_disease_evidence(
    ensemblId='ENSG00000148737',  # TCF7L2
    efoId='EFO_0001360',         # T2D
    size=20
)
```

**T2D Stratification**:

| Risk Factor | Low Risk | Moderate Risk | High Risk | Score Points |
|-------------|----------|---------------|-----------|-------------|
| HbA1c | <6.5% | 6.5-8.0% | >8.0% | 5-30 |
| Genetic risk | No risk alleles | 1-3 risk alleles | MODY gene/many risk alleles | 5-25 |
| Complications | None | Microalbuminuria | Retinopathy, neuropathy | 0-20 |
| Duration | <5 years | 5-15 years | >15 years | 0-10 |

### CVD PATH (Phase 3V)

```python
# Check PCSK9 and LDLR variants
result = tu.tools.clinvar_search_variants(gene='LDLR', significance='pathogenic', limit=20)
# Familial hypercholesterolemia check

# Check statin-relevant PGx
result = tu.tools.PharmGKB_get_clinical_annotations(query='SLCO1B1')
# SLCO1B1 *5 -> increased statin myopathy risk
```

**CVD Risk Integration**:

| Factor | Score Points |
|--------|-------------|
| LDL >190 mg/dL | 15 |
| FH gene mutation (LDLR/APOB/PCSK9) | 20 |
| ASCVD >20% 10-year risk | 30 |
| Family hx premature CVD | 10 |
| Lipoprotein(a) elevated | 8 |
| Multiple GWAS risk alleles | 5-15 |

### RARE DISEASE PATH (Phase 3R)

```python
# Check causal variant in disease gene
result = tu.tools.clinvar_search_variants(gene='FBN1', significance='pathogenic', limit=50)
# Marfan syndrome - FBN1 pathogenic variants

# Genotype-phenotype correlation
result = tu.tools.UniProt_get_disease_variants_by_accession(accession='P35555')  # FBN1 UniProt
# Known disease variants and their phenotypes
```

**Rare Disease Risk Assessment**:

| Finding | Risk Level | Score Points |
|---------|-----------|-------------|
| Pathogenic variant in causal gene | Definitive | 30 |
| Likely pathogenic in causal gene | Strong | 25 |
| VUS in causal gene | Moderate | 15 |
| Family history + partial phenotype | Suggestive | 10 |
| Single phenotype feature only | Low | 5 |

---

## Phase 4: Pharmacogenomic Profiling

### Step 4.1: Drug-Metabolizing Enzyme Genotypes

```python
# PharmGKB clinical annotations for CYP2C19
result = tu.tools.PharmGKB_get_clinical_annotations(query='CYP2C19')
# Returns drug-gene pairs with clinical annotation levels

# FDA pharmacogenomic biomarkers
result = tu.tools.fda_pharmacogenomic_biomarkers(drug_name='clopidogrel', limit=50)
# CYP2C19 poor metabolizer -> reduced clopidogrel efficacy

# PharmGKB dosing guidelines
result = tu.tools.PharmGKB_get_dosing_guidelines(query='CYP2C19')
# CPIC dosing guidelines
```

**Key Pharmacogenes and Clinical Impact**:

| Gene | Star Alleles | Metabolizer Status | Clinical Impact | Score Points |
|------|-------------|-------------------|----------------|-------------|
| CYP2D6 | *4/*4, *5/*5 | Poor metabolizer | Codeine, tamoxifen, many antidepressants | 8 |
| CYP2C19 | *2/*2, *2/*3 | Poor metabolizer | Clopidogrel, voriconazole, PPIs | 8 |
| CYP2C9 | *2/*3, *3/*3 | Poor metabolizer | Warfarin, NSAIDs, phenytoin | 5 |
| SLCO1B1 | *5/*5 | Decreased function | Statin myopathy (simvastatin) | 5 |
| DPYD | *2A | DPD deficient | 5-FU/capecitabine severe toxicity | 10 |
| VKORC1 | -1639G>A | Warfarin sensitive | Lower warfarin dose needed | 5 |
| UGT1A1 | *28/*28 | Poor glucuronidator | Irinotecan toxicity | 5 |
| TPMT | *2, *3A, *3C | Poor metabolizer | Thiopurine toxicity | 8 |
| HLA-B*5701 | Present | N/A | Abacavir hypersensitivity | 10 |
| HLA-B*1502 | Present | N/A | Carbamazepine SJS/TEN | 10 |

### Step 4.2: Treatment-Specific PGx

```python
# For the specific disease, identify relevant drugs and check PGx
# Example: breast cancer -> tamoxifen -> CYP2D6
result = tu.tools.PharmGKB_get_drug_details(query='tamoxifen')
# Returns PGx annotations for tamoxifen

# Get FDA PGx biomarkers for disease area
result = tu.tools.fda_pharmacogenomic_biomarkers(biomarker='CYP2D6', limit=100)
# All drugs with CYP2D6 PGx in FDA labels
```

### Step 4.3: Drug Target Variants

```python
# Check if patient has variants in drug targets
result = tu.tools.PharmGKB_search_variants(query='VKORC1')
# VKORC1 variants affecting warfarin response
```

**Pharmacogenomic Risk Score** (0-10 points):
- Poor metabolizer for treatment-relevant CYP: 8-10 points
- Intermediate metabolizer: 4-5 points
- High-risk HLA allele: 8-10 points
- Drug target variant: 3-5 points
- Normal metabolizer, no actionable PGx: 0 points

---

## Phase 5: Comorbidity & Drug Interaction Risk

### Step 5.1: Comorbidity Analysis

```python
# Check disease-disease overlap via shared genetic targets
result = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId='EFO_0001360',  # T2D
    size=50
)
# Compare top targets between primary disease and comorbidities

# Literature on comorbidity
result = tu.tools.PubMed_search_articles(
    query='type 2 diabetes cardiovascular comorbidity risk',
    max_results=5
)
```

### Step 5.2: Drug-Drug Interaction Risk

```python
# If current medications provided, check DDI
result = tu.tools.drugbank_get_drug_interactions_by_drug_name_or_id(
    query='metformin',
    case_sensitive=False,
    exact_match=False,
    limit=20
)

# FDA DDI data
result = tu.tools.FDA_get_drug_interactions_by_drug_name(drug_name='metformin', limit=5)
```

### Step 5.3: PGx-Amplified DDI Risk

If patient is a CYP2D6 poor metabolizer AND taking a CYP2D6 inhibitor -> compounded risk.

| Interaction Type | Risk Level | Management |
|-----------------|-----------|------------|
| PGx PM + CYP inhibitor | Very high | Alternative drug or dose reduction |
| PGx IM + CYP inhibitor | High | Monitor closely, possible dose reduction |
| PGx normal + CYP inhibitor | Moderate | Standard monitoring |
| No interacting drugs | Low | Standard care |

---

## Phase 6: Molecular Pathway Analysis

### Step 6.1: Dysregulated Pathways

```python
# Pathway enrichment for affected genes
gene_list = ['BRCA1', 'TP53', 'PIK3CA']  # from patient mutations
result = tu.tools.enrichr_gene_enrichment_analysis(
    gene_list=gene_list,
    libs=['KEGG_2021_Human', 'Reactome_2022']
)
# Returns enriched pathways with p-values

# Reactome pathway analysis
# First get UniProt IDs, then map to pathways
result = tu.tools.Reactome_map_uniprot_to_pathways(id='P38398')  # BRCA1 UniProt
# Returns list of pathways involving BRCA1
```

### Step 6.2: Network Analysis

```python
# Protein-protein interaction network
result = tu.tools.STRING_get_interaction_partners(
    protein_ids=['BRCA1', 'TP53'],
    species=9606,
    limit=20
)

# Functional enrichment of network
result = tu.tools.STRING_functional_enrichment(
    protein_ids=['BRCA1', 'TP53', 'PALB2', 'RAD51'],
    species=9606
)
```

### Step 6.3: Druggable Pathway Targets

```python
# Check tractability of pathway nodes
for gene in pathway_genes:
    result = tu.tools.OpenTargets_get_target_tractability_by_ensemblID(ensemblId=ensembl_id)
    # Returns small molecule, antibody, PROTAC tractability
```

**Key Druggable Pathways**:

| Pathway | Key Nodes | Drug Classes | Cancer Relevance |
|---------|-----------|-------------|-----------------|
| PI3K/AKT/mTOR | PIK3CA, AKT1, MTOR | PI3K inhibitors, mTOR inhibitors | Breast, endometrial |
| RAS/MAPK | KRAS, BRAF, MEK1/2 | KRAS G12C inhibitors, BRAF inhibitors | Lung, CRC, melanoma |
| DNA damage repair | BRCA1/2, ATM, PALB2 | PARP inhibitors | Breast, ovarian, prostate |
| Cell cycle | CDK4/6, RB1, CCND1 | CDK4/6 inhibitors | Breast |
| Immunocheckpoint | PD-1, PD-L1, CTLA-4 | ICIs | Pan-cancer |
| Wnt/beta-catenin | APC, CTNNB1, TCF | Wnt inhibitors (investigational) | CRC |

---

## Phase 7: Clinical Evidence & Guidelines

### Step 7.1: Guideline-Based Risk Categories

```python
# Search clinical guidelines in PubMed
result = tu.tools.PubMed_Guidelines_Search(
    query='NCCN breast cancer BRCA1 treatment guidelines',
    max_results=5
)

# Search general evidence
result = tu.tools.PubMed_search_articles(
    query='BRCA1 breast cancer treatment stratification',
    max_results=10
)
```

**Guideline References by Disease**:

| Disease Category | Guidelines | Key Stratification |
|-----------------|-----------|-------------------|
| Breast cancer | NCCN, ASCO, St. Gallen | Luminal A/B, HER2+, TNBC, BRCA status |
| NSCLC | NCCN, ESMO | Driver mutation status, PD-L1, TMB |
| CRC | NCCN | MSI, RAS/BRAF, sidedness |
| T2D | ADA Standards | HbA1c, CVD risk, CKD stage |
| CVD | ACC/AHA | ASCVD risk score, LDL goals, PGx |
| AF | ACC/AHA/HRS | CHA2DS2-VASc, anticoagulant selection |
| Rare disease | ACMG/AMP | Variant classification, genetic counseling |

### Step 7.2: FDA-Approved Therapies

```python
# Get approved drugs for disease
result = tu.tools.OpenTargets_get_associated_drugs_by_disease_efoId(
    efoId='EFO_0000305',  # breast cancer
    size=50
)
# Returns all known drugs with clinical status

# Check specific drug FDA info
result = tu.tools.FDA_get_indications_by_drug_name(drug_name='olaparib', limit=5)
# PARP inhibitor for BRCA-mutated breast cancer

# Get drug mechanism
result = tu.tools.FDA_get_mechanism_of_action_by_drug_name(drug_name='olaparib', limit=5)
```

### Step 7.3: Biomarker-Drug Evidence

```python
# CIViC evidence for biomarker-drug pair
result = tu.tools.civic_search_evidence_items(
    therapy_name='olaparib',
    disease_name='breast cancer'
)
# Returns clinical evidence items with evidence levels

# DrugBank for drug details
result = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(
    query='olaparib',
    case_sensitive=False,
    exact_match=False,
    limit=5
)
```

---

## Phase 8: Clinical Trial Matching

### Step 8.1: Biomarker-Driven Trials

```python
# Search trials matching molecular profile
result = tu.tools.clinical_trials_search(
    action='search_studies',
    condition='breast cancer',
    intervention='PARP inhibitor',
    limit=10
)
# Returns {total_count, studies: [{nctId, title, status, conditions}]}

# Alternative search
result = tu.tools.search_clinical_trials(
    query_term='BRCA1 breast cancer',
    condition='breast cancer',
    intervention='olaparib',
    pageSize=10
)
```

### Step 8.2: Precision Medicine Trials

```python
# Search basket/umbrella trials
result = tu.tools.search_clinical_trials(
    query_term='precision medicine biomarker-driven',
    condition='breast cancer',
    pageSize=10
)

# Search risk-adapted trials
result = tu.tools.search_clinical_trials(
    query_term='high risk BRCA1',
    condition='breast cancer',
    pageSize=10
)
```

### Step 8.3: Trial Details

```python
# Get details for promising trials
result = tu.tools.clinical_trials_get_details(
    action='get_study_details',
    nct_id='NCT03344965'
)
# Returns full study protocol
```

---

## Phase 9: Integrated Scoring & Recommendations

### Precision Medicine Risk Score (0-100)

#### Score Components

**Genetic Risk Component** (0-35 points):

| Scenario | Points |
|----------|--------|
| Pathogenic variant in high-penetrance disease gene (BRCA1, LDLR, FBN1) | 30-35 |
| Multiple moderate-risk variants (GWAS hits + moderate penetrance) | 20-28 |
| High PRS (>90th percentile) with no known pathogenic variants | 25-30 |
| Single moderate-risk variant | 12-18 |
| VUS in relevant gene | 8-12 |
| Average PRS, no pathogenic variants | 5-10 |
| Low genetic risk (low PRS, no risk alleles) | 0-5 |

**Clinical Risk Component** (0-30 points):

| Disease Type | Factor | Low (0-8) | Moderate (10-20) | High (22-30) |
|-------------|--------|-----------|------------------|-------------|
| Cancer | Stage | I | II-III | IV |
| T2D | HbA1c | <7% | 7-9% | >9% |
| CVD | ASCVD 10-yr | <10% | 10-20% | >20% |
| Neuro | Biomarker status | No biomarkers | Mild changes | Established |
| Rare | Phenotype match | Partial | Moderate | Full phenotype |

**Molecular Features Component** (0-25 points):

| Feature | Points |
|---------|--------|
| Cancer: High-risk driver mutations (TP53+PIK3CA, KRAS G12C) | 20-25 |
| Cancer: Actionable mutation (EGFR, BRAF V600E) | 15-20 |
| Cancer: High TMB or MSI-H (favorable for ICI) | 10-15 |
| Metabolic: Monogenic form (MODY, FH) | 20-25 |
| Metabolic: Multiple metabolic risk variants | 10-15 |
| CVD: FH gene mutation | 20-25 |
| Rare: Complete genotype-phenotype match | 20-25 |
| VUS requiring further workup | 5-10 |

**Pharmacogenomic Risk Component** (0-10 points):

| Finding | Points |
|---------|--------|
| Poor metabolizer for treatment-critical CYP + high-risk HLA | 10 |
| Poor metabolizer for treatment-critical CYP | 7-8 |
| Intermediate metabolizer for relevant CYP | 4-5 |
| Drug target variant (e.g., VKORC1 for warfarin) | 3-5 |
| No actionable PGx findings | 0-2 |

#### Risk Tier Assignment

| Total Score | Risk Tier | Management Intensity |
|------------|-----------|---------------------|
| 75-100 | **VERY HIGH** | Intensive treatment, subspecialty referral, clinical trial enrollment |
| 50-74 | **HIGH** | Aggressive treatment, close monitoring, molecular tumor board |
| 25-49 | **INTERMEDIATE** | Standard treatment, guideline-based care, PGx-guided dosing |
| 0-24 | **LOW** | Surveillance, prevention, risk factor modification |

### Treatment Algorithm

Based on disease type + risk tier + molecular profile + PGx:

#### Cancer Treatment Algorithm

```
IF actionable mutation present:
  1st line: Targeted therapy (e.g., EGFR TKI, BRAF inhibitor, PARP inhibitor)
  2nd line: Immunotherapy (if TMB-H or MSI-H) OR chemotherapy
  3rd line: Clinical trial OR alternative targeted therapy

IF no actionable mutation:
  IF TMB-H or MSI-H:
    1st line: Immunotherapy (pembrolizumab)
    2nd line: Chemotherapy
  ELSE:
    1st line: Standard chemotherapy (disease-specific)
    2nd line: Consider clinical trials

PGx adjustments:
  - DPYD deficient -> AVOID fluoropyrimidines or reduce dose 50%
  - UGT1A1 *28/*28 -> Reduce irinotecan dose
  - CYP2D6 PM + tamoxifen -> Switch to aromatase inhibitor
```

#### Metabolic/CVD Treatment Algorithm

```
IF monogenic form (MODY, FH):
  Disease-specific therapy (e.g., sulfonylureas for HNF1A-MODY, PCSK9i for FH)

IF polygenic risk:
  Standard guidelines (ADA, ACC/AHA)
  PGx-guided drug selection:
    - CYP2C19 PM -> Alternative to clopidogrel (ticagrelor, prasugrel)
    - SLCO1B1 *5 -> Lower statin dose or alternative statin
    - VKORC1 variant -> Warfarin dose adjustment or DOAC
```

### Monitoring Plan

| Component | Frequency | Method |
|-----------|-----------|--------|
| Molecular biomarkers | Per guideline | Liquid biopsy, tissue biopsy |
| Clinical markers | 3-6 months | Labs, imaging |
| PGx-guided drug levels | As needed | TDM |
| Disease progression | Per stage/risk | Imaging, biomarkers |
| Comorbidity screening | Annually | Labs, risk calculators |

---

## Output Report Structure

Generate a comprehensive markdown report saved to: `[PATIENT_ID]_precision_medicine_report.md`

### Required Sections

```markdown
# Precision Medicine Stratification Report

## Executive Summary
- **Patient Profile**: [Disease, key features]
- **Precision Medicine Risk Score**: [X]/100
- **Risk Tier**: [LOW / INTERMEDIATE / HIGH / VERY HIGH]
- **Key Finding**: [One-line summary of most actionable finding]
- **Primary Recommendation**: [One-line treatment recommendation]

## 1. Patient Profile
### Disease Classification
### Genomic Data Summary
### Clinical Parameters

## 2. Genetic Risk Assessment
### Germline Variant Analysis
### Gene-Disease Association Evidence
### Polygenic Risk Estimation
### Population Frequency Data

## 3. Disease-Specific Stratification
### [Cancer: Molecular Subtype / Metabolic: Risk Integration / etc.]
### Prognostic Markers
### Risk Group Assignment

## 4. Pharmacogenomic Profile
### Drug-Metabolizing Enzymes
### Drug Target Variants
### Treatment-Specific PGx Recommendations
### FDA PGx Biomarker Status

## 5. Comorbidity & Drug Interaction Risk
### Disease-Disease Overlap
### Drug-Drug Interactions
### PGx-Amplified DDI Risk

## 6. Dysregulated Pathways
### Key Pathways Affected
### Druggable Targets
### Network Analysis

## 7. Clinical Evidence & Guidelines
### Guideline-Based Classification
### FDA-Approved Therapies
### Biomarker-Drug Evidence

## 8. Clinical Trial Matches
### Biomarker-Driven Trials
### Precision Medicine Trials
### Risk-Adapted Trials

## 9. Integrated Risk Score
### Score Breakdown
| Component | Points | Max | Basis |
|-----------|--------|-----|-------|
| Genetic Risk | X | 35 | [Details] |
| Clinical Risk | X | 30 | [Details] |
| Molecular Features | X | 25 | [Details] |
| Pharmacogenomic Risk | X | 10 | [Details] |
| **TOTAL** | **X** | **100** | |

### Risk Tier: [TIER]
### Confidence Level: [HIGH/MODERATE/LOW]

## 10. Treatment Algorithm
### 1st Line Recommendation
### 2nd Line Options
### 3rd Line / Investigational
### PGx Dose Adjustments

## 11. Monitoring Plan
### Biomarker Surveillance
### Imaging Schedule
### Risk Reassessment Timeline

## 12. Outcome Predictions
### Disease-Specific Prognosis
### Treatment Response Prediction
### Projected Timeline

## Completeness Checklist
| Data Layer | Available | Analyzed | Key Finding |
|-----------|-----------|----------|-------------|
| Disease disambiguation | Y/N | Y/N | [EFO ID] |
| Germline variants | Y/N | Y/N | [Pathogenicity] |
| Somatic mutations | Y/N | Y/N | [Drivers] |
| Gene expression | Y/N | Y/N | [Subtype] |
| PGx genotypes | Y/N | Y/N | [Metabolizer status] |
| Clinical biomarkers | Y/N | Y/N | [Key values] |
| GWAS/PRS | Y/N | Y/N | [Risk percentile] |
| Pathway analysis | Y/N | Y/N | [Key pathways] |
| Clinical trials | Y/N | Y/N | [N matches] |
| Guidelines | Y/N | Y/N | [Guideline tier] |

## Evidence Sources
[List all databases and tools used with specific citations]
```

---

## Evidence Grading

All findings must be graded:

| Tier | Level | Sources | Weight |
|------|-------|---------|--------|
| **T1** | Clinical/regulatory evidence | FDA labels, NCCN guidelines, PharmGKB Level 1A/1B, ClinVar pathogenic | Highest |
| **T2** | Strong experimental evidence | CIViC Level A/B, OpenTargets high-score, GWAS p<5e-8, clinical trials | High |
| **T3** | Moderate evidence | PharmGKB Level 2, CIViC Level C, GWAS suggestive, preclinical data | Moderate |
| **T4** | Computational/predicted | VEP predictions, pathway inference, network analysis, PRS estimates | Supportive |

---

## Completeness Requirements

**Minimum deliverables** for a valid stratification report:
1. Disease resolved to EFO/ontology ID
2. At least one genetic risk assessment completed (germline OR somatic OR PRS)
3. Disease-specific stratification with risk group
4. At least one pharmacogenomic assessment (even if "no actionable findings")
5. Pathway analysis with at least one pathway identified
6. Treatment recommendation with evidence tier
7. At least one clinical trial match attempted
8. Precision Medicine Risk Score calculated with all available components
9. Risk tier assigned
10. Monitoring plan outlined

---

## Common Use Patterns

### Pattern 1: Cancer Patient with Actionable Mutation
**Input**: "Breast cancer, BRCA1 pathogenic variant, ER+/HER2-, stage IIA, age 45"
**Key phases**: Phase 1 (cancer classification) -> Phase 2 (BRCA1 pathogenicity) -> Phase 3C (molecular subtype = Luminal B, BRCA+) -> Phase 4 (check CYP2D6 for tamoxifen) -> Phase 7 (NCCN guidelines: PARP inhibitor eligible) -> Phase 8 (PARP inhibitor trials) -> Phase 9 (Risk Score ~55-65, HIGH tier)

### Pattern 2: Metabolic Disease with PGx Concern
**Input**: "Type 2 diabetes, HbA1c 8.5%, CYP2C19 *2/*2, on clopidogrel for CAD stent"
**Key phases**: Phase 1 (T2D + CAD) -> Phase 2 (T2D genetic risk) -> Phase 3M (HbA1c-based risk) -> Phase 4 (CYP2C19 PM: clopidogrel ineffective!) -> Phase 5 (T2D-CAD comorbidity) -> Phase 9 (Risk Score ~50-60, HIGH, clopidogrel switch urgent)

### Pattern 3: CVD Risk Stratification
**Input**: "LDL 190 mg/dL, SLCO1B1*5 heterozygous, family history of MI at age 48"
**Key phases**: Phase 1 (CVD/FH evaluation) -> Phase 2 (FH gene check: LDLR, APOB, PCSK9) -> Phase 3V (ASCVD risk) -> Phase 4 (SLCO1B1 *5: statin myopathy risk) -> Phase 7 (ACC/AHA guidelines) -> Phase 9 (Risk Score ~45-55, statin dose reduction or rosuvastatin)

### Pattern 4: Rare Disease Diagnosis
**Input**: "Marfan syndrome suspected, FBN1 c.4082G>A, tall stature, aortic root dilation"
**Key phases**: Phase 1 (Marfan/rare) -> Phase 2 (FBN1 variant pathogenicity) -> Phase 3R (genotype-phenotype match) -> Phase 7 (Ghent criteria) -> Phase 9 (Risk Score depends on aortic involvement)

### Pattern 5: Neurological Risk Assessment
**Input**: "Family history of Alzheimer's, APOE e4/e4, age 55"
**Key phases**: Phase 1 (AD/neuro) -> Phase 2 (APOE e4/e4 = highest genetic risk) -> Phase 3 (AD-specific risk) -> Phase 4 (PGx for potential treatments) -> Phase 7 (guidelines) -> Phase 9 (Risk Score ~60-75, HIGH)

### Pattern 6: Comprehensive Cancer with Full Molecular
**Input**: "NSCLC, EGFR L858R, TMB 25 mut/Mb, PD-L1 80%, stage IV, no EGFR T790M"
**Key phases**: All phases. Phase 3C critical: EGFR L858R = EGFR TKI eligible, high TMB + PD-L1 = ICI eligible. Treatment algorithm: 1st line osimertinib (EGFR TKI), 2nd line ICI (if progression). Risk Score ~70-80 (VERY HIGH due to stage IV).
