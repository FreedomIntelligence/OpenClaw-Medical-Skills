# tooluniverse-drug-target-validation

> Comprehensive computational validation of drug targets for early-stage drug discovery. Evaluates targets across 10 dimensions (disambiguation, disease association, druggability, chemical matter, clinical precedent, safety, pathway context, validation evidence, structural insights, validation roadmap) using 60+ ToolUniverse tools. Produces a quantitative Target Validation Score (0-100) with GO/NO-GO recommendation. Use when users ask about target validation, druggability assessment, target prioritization, or "is X a good drug target for Y?"

# Drug Target Validation Pipeline

Validate drug target hypotheses using multi-dimensional computational evidence before committing to wet-lab work. Produces a quantitative Target Validation Score (0-100) with priority tier classification and GO/NO-GO recommendation.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Target disambiguation FIRST** - Resolve all identifiers before analysis
3. **Evidence grading** - Grade all evidence as T1 (experimental) to T4 (computational)
4. **Disease-specific** - Tailor analysis to disease context when provided
5. **Modality-aware** - Consider small molecule vs biologics tractability
6. **Safety-first** - Prominently flag safety concerns early
7. **Quantitative scoring** - Every dimension scored numerically (0-100 composite)
8. **Negative results documented** - "No data" is data; empty sections are failures
9. **Source references** - Every statement must cite tool/database
10. **Completeness checklist** - Mandatory section showing analysis coverage
11. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use This Skill

Apply when users:
- Ask "Is [target] a good drug target for [disease]?"
- Need target validation or druggability assessment
- Want to compare targets for drug discovery prioritization
- Ask about safety risks of modulating a target
- Need chemical starting points for target validation
- Ask about pathway context for a target
- Need a GO/NO-GO recommendation for a target
- Want a comprehensive target dossier for investment decisions

**NOT for** (use other skills instead):
- General target biology overview -> Use `tooluniverse-target-research`
- Drug compound profiling -> Use `tooluniverse-drug-research`
- Variant interpretation -> Use `tooluniverse-variant-interpretation`
- Disease research -> Use `tooluniverse-disease-research`

---

## Input Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| **target** | Yes | Gene symbol, protein name, or UniProt ID | `EGFR`, `P00533`, `Epidermal growth factor receptor` |
| **disease** | No | Disease/indication for context | `Non-small cell lung cancer`, `Pancreatic cancer` |
| **modality** | No | Preferred therapeutic modality | `small molecule`, `antibody`, `protein therapeutic`, `PROTAC` |

---

## Target Validation Scoring System

### Score Components (Total: 0-100)

**Disease Association** (0-30 points):
- Genetic evidence: 0-10 (GWAS, rare variants, somatic mutations)
- Literature evidence: 0-10 (publications, clinical studies)
- Pathway evidence: 0-10 (disease pathway involvement)

**Druggability** (0-25 points):
- Structural tractability: 0-10 (structure quality, binding pockets)
- Chemical matter: 0-10 (known compounds, bioactivity data)
- Target class: 0-5 (validated target family bonus)

**Safety Profile** (0-20 points):
- Tissue expression selectivity: 0-5 (expression in critical tissues)
- Genetic validation: 0-10 (knockout phenotypes, human genetics)
- Known adverse events: 0-5 (safety signals from modulators)

**Clinical Precedent** (0-15 points):
- Approved drugs: 15 (strong precedent, validated target)
- Clinical trials: 10 (moderate precedent)
- Preclinical compounds: 5 (weak precedent)
- None: 0 (novel target)

**Validation Evidence** (0-10 points):
- Functional studies: 0-5 (CRISPR, siRNA, biochemical)
- Disease models: 0-5 (animal models, patient data)

### Priority Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| **80-100** | Tier 1 | Highly validated - proceed with confidence |
| **60-79** | Tier 2 | Good target - needs focused validation |
| **40-59** | Tier 3 | Moderate risk - significant validation needed |
| **0-39** | Tier 4 | High risk - consider alternatives |

### Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Direct mechanistic, human clinical proof | FDA-approved drug, crystal structure with mechanism, patient mutation |
| **T2** | [T2] | Functional studies, model organism | siRNA phenotype, mouse KO, biochemical assay, CRISPR screen |
| **T3** | [T3] | Association, screen hits, computational | GWAS hit, DepMap essentiality, expression correlation |
| **T4** | [T4] | Mention, review, text-mined, predicted | Review article, database annotation, AlphaFold prediction |

---

## Phase 0: Target Disambiguation & ID Resolution (ALWAYS FIRST)

**Objective**: Resolve target to ALL needed identifiers before any analysis.

### Resolution Strategy

```python
# Step 1: Determine input type and get initial identifiers
# If gene symbol (e.g., "EGFR"):
mygene = tu.tools.MyGene_query_genes(query="EGFR", species="human", fields="symbol,name,ensembl.gene,uniprot.Swiss-Prot,entrezgene")
# Extract: ensembl_id, uniprot_id, entrez_id, symbol, name

# If UniProt ID (e.g., "P00533"):
uniprot = tu.tools.UniProt_get_entry_by_accession(accession="P00533")
# Extract: gene names, Ensembl xrefs, function

# Step 2: Resolve Ensembl ID and get versioned ID for GTEx
ensembl = tu.tools.ensembl_lookup_gene(gene_id=ensembl_id, species="homo_sapiens")
# CRITICAL: species parameter is REQUIRED
# CRITICAL: Response is wrapped in {status, data, url, content_type} - access via ensembl['data']
ensembl_data = ensembl.get('data', ensembl) if isinstance(ensembl, dict) else ensembl
# Extract: version for versioned_id (e.g., "ENSG00000146648.18")

# Step 3: Get Ensembl cross-references
xrefs = tu.tools.ensembl_get_xrefs(id=ensembl_id)
# Extract: HGNC, UniProt, EntrezGene mappings

# Step 4: Get OpenTargets target info
ot_target = tu.tools.OpenTargets_get_target_id_description_by_name(targetName="EGFR")
# Verify ensemblId matches

# Step 5: Get ChEMBL target ID
chembl_targets = tu.tools.ChEMBL_search_targets(pref_name__contains="EGFR", organism="Homo sapiens", limit=5)
# Extract: target_chembl_id for later use

# Step 6: Get UniProt function summary
function_info = tu.tools.UniProt_get_function_by_accession(accession=uniprot_id)
# Returns list of strings (NOT dict)

# Step 7: Get alternative names for collision detection
alt_names = tu.tools.UniProt_get_alternative_names_by_accession(accession=uniprot_id)
```

### Identifier Resolution Output

```markdown
## 1. Target Identity

| Database | Identifier | Verified |
|----------|-----------|----------|
| Gene Symbol | EGFR | Yes |
| Full Name | Epidermal growth factor receptor | Yes |
| Ensembl | ENSG00000146648 | Yes |
| Ensembl (versioned) | ENSG00000146648.18 | Yes |
| UniProt | P00533 | Yes |
| Entrez Gene | 1956 | Yes |
| ChEMBL | CHEMBL203 | Yes |
| HGNC | HGNC:3236 | Yes |

**Protein Function**: [from UniProt_get_function_by_accession]
**Subcellular Location**: [from UniProt_get_subcellular_location_by_accession]
**Target Class**: [from OpenTargets_get_target_classes_by_ensemblID]
```

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `ensembl_lookup_gene` | `id` | `gene_id` (+ `species="homo_sapiens"` REQUIRED) |
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `GTEx_get_median_gene_expression` | `gencode_id` only | `gencode_id` + `operation="median"` |
| `OpenTargets_*` | `ensemblID` (uppercase) | `ensemblId` (camelCase) |
| `OpenTargets_get_publications_*` | `ensemblId` | `entityId` |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId` only | `ensemblId` + `size` (REQUIRED) |
| `MyGene_query_genes` | `q` | `query` |
| `PubMed_search_articles` | returns `{articles: [...]}` | returns **plain list** of dicts |
| `UniProt_get_function_by_accession` | returns dict | returns **list of strings** |
| `HPA_get_rna_expression_by_source` | `ensembl_id` | `gene_name` + `source_type` + `source_name` (ALL required) |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` |
| `drugbank_get_safety_*` | simple params | `query`, `case_sensitive`, `exact_match`, `limit` (ALL required) |

---

## Phase 1: Disease Association Evidence (0-30 points)

**Objective**: Quantify the strength of target-disease association from genetic, literature, and pathway evidence.

### 1A. OpenTargets Disease Associations (Primary)

```python
# Get ALL disease associations for target
diseases = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(ensemblId=ensembl_id)

# If specific disease provided, get detailed evidence
if disease_name:
    disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName=disease_name)
    efo_id = disease_info.get('id')  # e.g., "EFO_0003060"

    evidence = tu.tools.OpenTargets_target_disease_evidence(
        efoId=efo_id, ensemblId=ensembl_id
    )

    # Get evidence by data source for detailed breakdown
    datasource_evidence = tu.tools.OpenTargets_get_evidence_by_datasource(
        efoId=efo_id, ensemblId=ensembl_id,
        datasourceIds=["ot_genetics_portal", "eva", "gene2phenotype", "genomics_england", "uniprot_literature"],
        size=100
    )
```

### 1B. GWAS Genetic Evidence

```python
# GWAS associations for target gene
gwas_snps = tu.tools.gwas_get_snps_for_gene(mapped_gene=gene_symbol, size=50)

# If specific disease, search for trait-specific associations
if disease_name:
    gwas_studies = tu.tools.gwas_search_studies(query=disease_name, size=20)
```

### 1C. Constraint Scores (gnomAD)

```python
# Genetic constraint - intolerance to loss of function
constraints = tu.tools.gnomad_get_gene_constraints(gene_symbol=gene_symbol)
# Extract: pLI, LOEUF, missense_z, pRec
# High pLI (>0.9) = highly intolerant to LoF = likely essential
```

### 1D. Literature Evidence

```python
# PubMed for target-disease association
articles = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND "{disease_name}" AND (target OR therapeutic OR inhibitor)',
    limit=50
)
# PubMed_search_articles returns a plain list of dicts

# OpenTargets publications
pubs = tu.tools.OpenTargets_get_publications_by_target_ensemblID(entityId=ensembl_id)
```

### Scoring Logic - Disease Association

```
Genetic Evidence (0-10):
  - GWAS hits for specific disease: +3 per significant locus (max 6)
  - Rare variant evidence (ClinVar pathogenic): +2
  - Somatic mutations in disease: +2
  - pLI > 0.9 (essential gene): +2

Literature Evidence (0-10):
  - >100 publications on target+disease: 10
  - 50-100 publications: 7
  - 10-50 publications: 5
  - 1-10 publications: 3
  - 0 publications: 0

Pathway Evidence (0-10):
  - OpenTargets overall score > 0.8: 10
  - Score 0.5-0.8: 7
  - Score 0.2-0.5: 4
  - Score < 0.2: 1
```

---

## Phase 2: Druggability Assessment (0-25 points)

**Objective**: Assess whether the target is amenable to therapeutic intervention.

### 2A. OpenTargets Tractability

```python
# Tractability assessment across modalities
tractability = tu.tools.OpenTargets_get_target_tractability_by_ensemblID(ensemblId=ensembl_id)
# Returns: label, modality (SM, AB, PR, OC), value (boolean/score)
# Modalities: Small Molecule, Antibody, PROTAC, Other Clinical
```

### 2B. Target Class & Family

```python
# Target classification (kinase, GPCR, ion channel, etc.)
target_classes = tu.tools.OpenTargets_get_target_classes_by_ensemblID(ensemblId=ensembl_id)

# Pharos target development level
pharos = tu.tools.Pharos_get_target(gene=gene_symbol)
# TDL: Tclin (approved drug) > Tchem (compounds) > Tbio (biology) > Tdark (unknown)

# DGIdb druggability categories
druggability = tu.tools.DGIdb_get_gene_druggability(genes=[gene_symbol])
```

### 2C. Structural Tractability

```python
# PDB structures available
if uniprot_id:
    uniprot_entry = tu.tools.UniProt_get_entry_by_accession(accession=uniprot_id)
    # Extract PDB cross-references from entry

# AlphaFold prediction
alphafold = tu.tools.alphafold_get_prediction(qualifier=uniprot_id)
alphafold_summary = tu.tools.alphafold_get_summary(qualifier=uniprot_id)

# For top PDB structures, analyze binding pockets
# ProteinsPlus DoGSiteScorer for pocket detection
for pdb_id in top_pdb_ids[:3]:
    pockets = tu.tools.ProteinsPlus_predict_binding_sites(pdb_id=pdb_id)
    # Returns predicted druggable pockets with scores
```

### 2D. Chemical Probes & Enabling Packages

```python
# Chemical probes (validated tool compounds)
probes = tu.tools.OpenTargets_get_chemical_probes_by_target_ensemblID(ensemblId=ensembl_id)

# Target Enabling Packages (TEPs)
teps = tu.tools.OpenTargets_get_target_enabling_packages_by_ensemblID(ensemblId=ensembl_id)
```

### Scoring Logic - Druggability

```
Structural Tractability (0-10):
  - High-res co-crystal structure with ligand: 10
  - PDB structure available, pockets detected: 7
  - AlphaFold only, confident pocket prediction: 5
  - AlphaFold low confidence / no structure: 2
  - No structural data: 0

Chemical Matter (0-10):
  - Known drug-like compounds (IC50 < 100nM): 10
  - Tool compounds (IC50 < 1uM): 7
  - HTS hits only (IC50 > 1uM): 4
  - No known ligands: 0

Target Class Bonus (0-5):
  - Validated druggable family (kinase, GPCR, nuclear receptor): 5
  - Enzyme, ion channel: 4
  - Protein-protein interaction, transporter: 2
  - Novel/unknown class: 0
```

---

## Phase 3: Known Modulators & Chemical Matter (Feeds into Phase 2 scoring)

**Objective**: Identify existing chemical starting points for target validation.

### 3A. ChEMBL Bioactivity

```python
# Search for ChEMBL target
chembl_targets = tu.tools.ChEMBL_search_targets(
    pref_name__contains=gene_symbol, organism="Homo sapiens", limit=10
)

# Get activities for best matching target
target_chembl_id = chembl_targets[0]['target_chembl_id']
activities = tu.tools.ChEMBL_get_target_activities(
    target_chembl_id__exact=target_chembl_id, limit=100
)
# Parse: compound IDs, pChEMBL values, activity types (IC50, Ki, Kd)
# Filter: potent compounds (pChEMBL >= 6.0 = IC50 <= 1uM)
```

### 3B. BindingDB Ligands

```python
# Experimental binding data
ligands = tu.tools.BindingDB_get_ligands_by_uniprot(
    uniprot=uniprot_id, affinity_cutoff=10000  # nM
)
# Returns: SMILES, affinity_type (Ki/IC50/Kd), affinity value, PMID
```

### 3C. PubChem Bioassays

```python
# HTS screening data
assays = tu.tools.PubChem_search_assays_by_target_gene(gene_symbol=gene_symbol)
# Get details for top assays
for aid in assay_ids[:5]:
    summary = tu.tools.PubChem_get_assay_summary(aid=str(aid))
    targets = tu.tools.PubChem_get_assay_targets(aid=str(aid))
    actives = tu.tools.PubChem_get_assay_active_compounds(aid=str(aid))
```

### 3D. Known Drugs Targeting This Protein

```python
# OpenTargets known drugs
drugs = tu.tools.OpenTargets_get_associated_drugs_by_target_ensemblID(
    ensemblId=ensembl_id, size=25
)

# ChEMBL drug mechanisms
drug_mechanisms = tu.tools.ChEMBL_search_mechanisms(
    target_chembl_id=target_chembl_id, limit=50
)

# Drug interaction databases
dgidb = tu.tools.DGIdb_get_gene_info(genes=[gene_symbol])
```

### Report Format - Chemical Matter

```markdown
### 4. Known Modulators & Chemical Matter

#### 4.1 Approved Drugs
| Drug | ChEMBL ID | Mechanism | Phase | Indication | Source |
|------|-----------|-----------|-------|------------|--------|
| Erlotinib | CHEMBL553 | Inhibitor | 4 | NSCLC | [T1] OpenTargets |
| Gefitinib | CHEMBL939 | Inhibitor | 4 | NSCLC | [T1] OpenTargets |

#### 4.2 ChEMBL Bioactivity Summary
**Total Activities**: 12,456 datapoints across 2,341 assays
**Most Potent Compound**: CHEMBL413456 (IC50 = 0.3 nM) [T1]
**Chemical Series**: 8 distinct scaffolds with pChEMBL >= 7.0
**Selectivity Data**: Available for 45 compounds (kinase panel)

#### 4.3 BindingDB Ligands
**Total Ligands**: 856 with measured affinity
**Best Affinity**: 0.1 nM (Ki)
**Affinity Distribution**: <1nM: 23, 1-10nM: 89, 10-100nM: 234, 100nM-1uM: 510

#### 4.4 Chemical Probes
| Probe | Source | Potency | Selectivity | Use |
|-------|--------|---------|-------------|-----|
| SGC-1234 | SGC | IC50=5nM | >100x | In vitro |
```

---

## Phase 4: Clinical Precedent (0-15 points)

**Objective**: Assess clinical validation from approved drugs and clinical trials.

### 4A. FDA-Approved Drugs

```python
# FDA label information
fda_moa = tu.tools.FDA_get_mechanism_of_action_by_drug_name(drug_name=gene_symbol)
fda_indications = tu.tools.FDA_get_indications_by_drug_name(drug_name=known_drug_name)

# DrugBank pharmacology
drugbank_targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    query=known_drug_name, case_sensitive=False, exact_match=False, limit=10
)

# DrugBank safety info
drugbank_safety = tu.tools.drugbank_get_safety_by_drug_name_or_drugbank_id(
    query=known_drug_name, case_sensitive=False, exact_match=False, limit=10
)
```

### 4B. Clinical Trials

```python
# Active clinical trials targeting this protein
trials = tu.tools.search_clinical_trials(
    query_term=gene_symbol,
    intervention=gene_symbol,
    pageSize=50
)

# If specific disease context
if disease_name:
    disease_trials = tu.tools.search_clinical_trials(
        query_term=gene_symbol,
        condition=disease_name,
        pageSize=50
    )
```

### 4C. Failed Programs (Learn from Failures)

```python
# Drug warnings and withdrawals
for drug_chembl_id in known_drug_ids:
    warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(chemblId=drug_chembl_id)
    adverse = tu.tools.OpenTargets_get_drug_adverse_events_by_chemblId(chemblId=drug_chembl_id)
```

### Scoring Logic - Clinical Precedent

```
Clinical Precedent (0-15):
  - FDA-approved drug for SAME disease: 15
  - FDA-approved drug for DIFFERENT disease: 12
  - Phase 3 clinical trial: 10
  - Phase 2 clinical trial: 7
  - Phase 1 clinical trial: 5
  - Preclinical compounds only: 3
  - No clinical development: 0

Adjustment factors:
  - Failed clinical program for safety: -3
  - Drug withdrawal: -5
  - Multiple approved drugs (validated class): +2
```

---

## Phase 5: Safety & Toxicity Considerations (0-20 points)

**Objective**: Identify safety risks from expression, genetics, and known adverse events.

### 5A. OpenTargets Safety Profile

```python
safety = tu.tools.OpenTargets_get_target_safety_profile_by_ensemblID(ensemblId=ensembl_id)
# Returns: safety liabilities, adverse effects, experimental toxicity
```

### 5B. Expression in Critical Tissues

```python
# GTEx tissue expression (identifies essential organ expression)
gtex = tu.tools.GTEx_get_median_gene_expression(
    operation="median", gencode_id=ensembl_versioned_id
)
# If empty, try unversioned ID

# HPA expression
# NOTE: HPA_get_rna_expression_by_source requires gene_name, source_type, source_name
hpa = tu.tools.HPA_search_genes_by_query(search_query=gene_symbol)
hpa_details = tu.tools.HPA_get_comprehensive_gene_details_by_ensembl_id(ensembl_id=ensembl_id)

# Check expression in safety-critical tissues
# Heart, liver, kidney, brain, bone marrow = high risk if target is expressed
```

### 5C. Knockout Phenotypes

```python
# Mouse model phenotypes
mouse_models = tu.tools.OpenTargets_get_biological_mouse_models_by_ensemblID(ensemblId=ensembl_id)

# Genetic constraint (proxy for essentiality)
constraints = tu.tools.gnomad_get_gene_constraints(gene_symbol=gene_symbol)
# High pLI = essential gene = potential safety concern
```

### 5D. Known Adverse Events from Target Modulation

```python
# For known drugs targeting this protein
for drug_name in known_drug_names:
    fda_adr = tu.tools.FDA_get_adverse_reactions_by_drug_name(drug_name=drug_name)
    fda_warnings = tu.tools.FDA_get_warnings_and_cautions_by_drug_name(drug_name=drug_name)
    fda_boxed = tu.tools.FDA_get_boxed_warning_info_by_drug_name(drug_name=drug_name)
    fda_contraindications = tu.tools.FDA_get_contraindications_by_drug_name(drug_name=drug_name)
```

### 5E. Homologs & Off-Target Risks

```python
# Paralogs (close family members that might be hit)
homologs = tu.tools.OpenTargets_get_target_homologues_by_ensemblID(ensemblId=ensembl_id)
# Paralogs with high sequence identity = selectivity challenge
```

### Scoring Logic - Safety

```
Tissue Expression Selectivity (0-5):
  - Target restricted to disease tissue: 5
  - Low expression in heart/liver/kidney/brain: 4
  - Moderate expression in 1-2 critical tissues: 2
  - High expression in multiple critical tissues: 0

Genetic Validation (0-10):
  - Mouse KO viable, no severe phenotype: 10
  - Mouse KO viable with mild phenotype: 7
  - Mouse KO has concerning phenotype: 3
  - Mouse KO lethal: 0
  - No KO data, low pLI (<0.5): 5
  - No KO data, high pLI (>0.9): 2

Known Adverse Events (0-5):
  - No known safety signals: 5
  - Mild, manageable ADRs: 3
  - Serious ADRs reported: 1
  - Black box warning or drug withdrawal: 0
```

---

## Phase 6: Pathway Context & Network Analysis

**Objective**: Understand the target's role in biological networks and disease pathways.

### 6A. Reactome Pathways

```python
# Map target to pathways
pathways = tu.tools.Reactome_map_uniprot_to_pathways(id=uniprot_id)

# Get pathway details for top pathways
for pathway in top_pathways[:5]:
    detail = tu.tools.Reactome_get_pathway(id=pathway['stId'])
    reactions = tu.tools.Reactome_get_pathway_reactions(id=pathway['stId'])
```

### 6B. Protein-Protein Interactions

```python
# STRING network
string_ppi = tu.tools.STRING_get_protein_interactions(
    protein_ids=[gene_symbol], species=9606, confidence_score=0.7
)
# Higher confidence = more reliable

# IntAct interactions (experimental)
intact_ppi = tu.tools.intact_get_interactions(identifier=uniprot_id)

# OpenTargets interactions
ot_ppi = tu.tools.OpenTargets_get_target_interactions_by_ensemblID(ensemblId=ensembl_id)
```

### 6C. Functional Enrichment

```python
# GO annotations
go_terms = tu.tools.OpenTargets_get_target_gene_ontology_by_ensemblID(ensemblId=ensembl_id)

# Direct GO query
go_annotations = tu.tools.GO_get_annotations_for_gene(gene_id=gene_symbol)

# STRING functional enrichment of interaction partners
enrichment = tu.tools.STRING_functional_enrichment(
    protein_ids=[gene_symbol], species=9606
)
```

### Report Format - Pathway Context

```markdown
### 7. Pathway Context & Network Analysis

#### 7.1 Key Pathways
| Pathway | Reactome ID | Relevance to Disease | Evidence |
|---------|-------------|---------------------|----------|
| EGFR signaling | R-HSA-177929 | Driver pathway in NSCLC | [T1] |
| RAS-RAF-MEK-ERK | R-HSA-5673001 | Downstream effector | [T1] |
| PI3K-AKT signaling | R-HSA-2219528 | Resistance mechanism | [T2] |

#### 7.2 Protein-Protein Interactions
**Total Interactors**: 45 (STRING confidence > 0.7)
**Key Interactors**: GRB2, SHC1, PLCG1, PIK3CA, STAT3

#### 7.3 Pathway Redundancy Assessment
**Compensation Risk**: MODERATE
- Parallel pathways: HER2, HER3 can compensate
- Feedback loops: RAS activation bypasses EGFR
- Downstream convergence: MEK/ERK shared with other RTKs
```

---

## Phase 7: Validation Evidence (0-10 points)

**Objective**: Assess existing functional validation data.

### 7A. DepMap Essentiality (CRISPR/RNAi)

```python
# Gene essentiality in cancer cell lines
deps = tu.tools.DepMap_get_gene_dependencies(gene_symbol=gene_symbol)
# Negative scores = essential (cells die upon KO)
# Score < -0.5: moderately essential
# Score < -1.0: strongly essential
```

### 7B. Literature Validation Evidence

```python
# Search for functional studies
validation_papers = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND (CRISPR OR siRNA OR knockdown OR knockout OR "loss of function") AND "{disease_name}"',
    limit=30
)

# Search for biomarker studies
biomarker_papers = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND (biomarker OR "target engagement" OR "pharmacodynamic")',
    limit=20
)
```

### 7C. Animal Model Evidence

```python
# Mouse phenotypes from OpenTargets (already retrieved in Phase 5)
# Reuse mouse_models data

# CTD gene-disease associations (complementary)
ctd_diseases = tu.tools.CTD_get_gene_diseases(input_terms=gene_symbol)
```

### Scoring Logic - Validation Evidence

```
Functional Studies (0-5):
  - CRISPR KO shows disease-relevant phenotype: 5
  - siRNA knockdown shows phenotype: 4
  - Biochemical assay validates mechanism: 3
  - Overexpression study only: 2
  - No functional data: 0

Disease Models (0-5):
  - Patient-derived xenograft (PDX) response: 5
  - Genetically engineered mouse model: 4
  - Cell line model: 3
  - In silico model only: 1
  - No model data: 0
```

---

## Phase 8: Structural Insights

**Objective**: Leverage structural biology for druggability and mechanism understanding.

### 8A. PDB Structures

```python
# Get PDB entries from UniProt cross-references
uniprot_entry = tu.tools.UniProt_get_entry_by_accession(accession=uniprot_id)
# Parse: uniProtKBCrossReferences where database == "PDB"

# Get details for each PDB
for pdb_id in pdb_ids[:10]:
    metadata = tu.tools.get_protein_metadata_by_pdb_id(pdb_id=pdb_id)
    quality = tu.tools.pdbe_get_entry_quality(pdb_id=pdb_id)
    summary = tu.tools.pdbe_get_entry_summary(pdb_id=pdb_id)
    experiment = tu.tools.pdbe_get_entry_experiment(pdb_id=pdb_id)
    molecules = tu.tools.pdbe_get_entry_molecules(pdb_id=pdb_id)
```

### 8B. AlphaFold Prediction

```python
alphafold = tu.tools.alphafold_get_prediction(qualifier=uniprot_id)
alphafold_info = tu.tools.alphafold_get_summary(qualifier=uniprot_id)
# Check pLDDT scores for confidence
```

### 8C. Binding Pocket Analysis

```python
# ProteinsPlus DoGSiteScorer for best PDB structure
pockets = tu.tools.ProteinsPlus_predict_binding_sites(pdb_id=best_pdb_id)
# Returns: pocket locations, druggability scores, volume, surface

# Interaction diagram for co-crystal structures
if has_ligand:
    diagram = tu.tools.ProteinsPlus_generate_interaction_diagram(pdb_id=pdb_id)
```

### 8D. Domain Architecture

```python
# InterPro domains
domains = tu.tools.InterPro_get_protein_domains(uniprot_accession=uniprot_id)

# Domain details for key domains
for domain in domains[:5]:
    detail = tu.tools.InterPro_get_domain_details(entry_id=domain['accession'])
```

---

## Phase 9: Literature Deep Dive

**Objective**: Comprehensive literature analysis with collision-aware search.

### 9A. Collision Detection

```python
# Detect naming collisions before literature search
test_results = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}"[Title]', limit=20
)
# PubMed returns plain list of dicts
# Check if >20% of results are off-topic (no biology terms)
# If collision detected, add filters: AND (protein OR gene OR receptor OR kinase)
```

### 9B. Publication Metrics

```python
# Total publications
total = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND (protein OR gene)', limit=1
)
# Check total_count field

# Recent publications (5-year trend)
recent = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND (protein OR gene) AND ("2021"[PDAT] : "2026"[PDAT])',
    limit=50
)

# Drug-focused publications
drug_pubs = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND (drug OR therapeutic OR inhibitor OR antibody)',
    limit=30
)

# EuropePMC for broader coverage
epmc = tu.tools.EuropePMC_search_articles(
    query=f'"{gene_symbol}" AND drug target',
    limit=30
)
```

### 9C. Key Reviews and Landmark Papers

```python
# Reviews for target overview
reviews = tu.tools.PubMed_search_articles(
    query=f'"{gene_symbol}" AND drug target AND review[pt]',
    limit=10
)

# OpenAlex for citation metrics
openalex_works = tu.tools.openalex_search_works(
    query=f'{gene_symbol} drug target', limit=20
)
```

---

## Phase 10: Validation Roadmap (Synthesis)

**Objective**: Generate actionable recommendations based on all evidence.

This phase synthesizes all previous phases into:
1. **Target Validation Score** (0-100)
2. **Priority Tier** (1-4)
3. **GO/NO-GO Recommendation**
4. **Recommended Experiments**
5. **Tool Compounds for Testing**
6. **Biomarker Strategy**
7. **Key Risks & Mitigations**

### Score Calculation

```python
def calculate_validation_score(phase_results):
    """
    Calculate Target Validation Score (0-100).

    Components:
    - Disease Association: 0-30
    - Druggability: 0-25
    - Safety: 0-20
    - Clinical Precedent: 0-15
    - Validation Evidence: 0-10
    """
    score = {
        'disease_genetic': 0,      # 0-10
        'disease_literature': 0,   # 0-10
        'disease_pathway': 0,      # 0-10
        'drug_structural': 0,      # 0-10
        'drug_chemical': 0,        # 0-10
        'drug_class': 0,           # 0-5
        'safety_expression': 0,    # 0-5
        'safety_genetic': 0,       # 0-10
        'safety_adverse': 0,       # 0-5
        'clinical': 0,             # 0-15
        'validation_functional': 0, # 0-5
        'validation_models': 0,    # 0-5
    }

    # ... scoring logic from each phase ...

    total = sum(score.values())

    if total >= 80:
        tier = "Tier 1"
        recommendation = "GO - Highly validated target"
    elif total >= 60:
        tier = "Tier 2"
        recommendation = "CONDITIONAL GO - Needs focused validation"
    elif total >= 40:
        tier = "Tier 3"
        recommendation = "CAUTION - Significant validation needed"
    else:
        tier = "Tier 4"
        recommendation = "NO-GO - Consider alternatives"

    return total, tier, recommendation, score
```

---

## Report Template

**File**: `[TARGET]_[DISEASE]_validation_report.md`

```markdown
# Drug Target Validation Report: [TARGET]

**Target**: [Gene Symbol] ([Full Name])
**Disease Context**: [Disease Name] (if provided)
**Modality**: [Small molecule / Antibody / etc.] (if specified)
**Generated**: [Date]
**Status**: In Progress

---

## Executive Summary

**Target Validation Score**: [XX/100]
**Priority Tier**: [Tier X] - [Description]
**Recommendation**: [GO / CONDITIONAL GO / CAUTION / NO-GO]

**Key Findings**:
- [1-sentence disease association strength with evidence grade]
- [1-sentence druggability assessment]
- [1-sentence safety profile]
- [1-sentence clinical precedent]

**Critical Risks**:
- [Top risk 1]
- [Top risk 2]

---

## Validation Scorecard

| Dimension | Score | Max | Assessment | Key Evidence |
|-----------|-------|-----|------------|--------------|
| **Disease Association** | | 30 | | |
| - Genetic evidence | | 10 | | |
| - Literature evidence | | 10 | | |
| - Pathway evidence | | 10 | | |
| **Druggability** | | 25 | | |
| - Structural tractability | | 10 | | |
| - Chemical matter | | 10 | | |
| - Target class | | 5 | | |
| **Safety Profile** | | 20 | | |
| - Expression selectivity | | 5 | | |
| - Genetic validation | | 10 | | |
| - Known ADRs | | 5 | | |
| **Clinical Precedent** | | 15 | | |
| **Validation Evidence** | | 10 | | |
| - Functional studies | | 5 | | |
| - Disease models | | 5 | | |
| **TOTAL** | **XX** | **100** | **[Tier]** | |

---

## 1. Target Identity
[Researching...]

## 2. Disease Association Evidence
### 2.1 OpenTargets Disease Associations
[Researching...]
### 2.2 GWAS Genetic Evidence
[Researching...]
### 2.3 Constraint Scores (gnomAD)
[Researching...]
### 2.4 Literature Evidence
[Researching...]

## 3. Druggability Assessment
### 3.1 Tractability (OpenTargets)
[Researching...]
### 3.2 Target Classification
[Researching...]
### 3.3 Structural Tractability
[Researching...]
### 3.4 Chemical Probes & Enabling Packages
[Researching...]

## 4. Known Modulators & Chemical Matter
### 4.1 Approved/Clinical Drugs
[Researching...]
### 4.2 ChEMBL Bioactivity
[Researching...]
### 4.3 BindingDB Ligands
[Researching...]
### 4.4 PubChem Bioassays
[Researching...]
### 4.5 Chemical Probes
[Researching...]

## 5. Clinical Precedent
### 5.1 FDA-Approved Drugs
[Researching...]
### 5.2 Clinical Trial Landscape
[Researching...]
### 5.3 Failed Programs & Lessons
[Researching...]

## 6. Safety & Toxicity Profile
### 6.1 OpenTargets Safety Liabilities
[Researching...]
### 6.2 Expression in Critical Tissues
[Researching...]
### 6.3 Knockout Phenotypes
[Researching...]
### 6.4 Known Adverse Events
[Researching...]
### 6.5 Paralog & Off-Target Risks
[Researching...]

## 7. Pathway Context & Network Analysis
### 7.1 Biological Pathways
[Researching...]
### 7.2 Protein-Protein Interactions
[Researching...]
### 7.3 Functional Enrichment
[Researching...]
### 7.4 Pathway Redundancy Assessment
[Researching...]

## 8. Validation Evidence
### 8.1 Target Essentiality (DepMap)
[Researching...]
### 8.2 Functional Studies
[Researching...]
### 8.3 Animal Models
[Researching...]
### 8.4 Biomarker Potential
[Researching...]

## 9. Structural Insights
### 9.1 Experimental Structures (PDB)
[Researching...]
### 9.2 AlphaFold Prediction
[Researching...]
### 9.3 Binding Pocket Analysis
[Researching...]
### 9.4 Domain Architecture
[Researching...]

## 10. Literature Landscape
### 10.1 Publication Metrics
[Researching...]
### 10.2 Key Publications
[Researching...]
### 10.3 Research Trend
[Researching...]

## 11. Validation Roadmap
### 11.1 Recommended Validation Experiments
[Researching...]
### 11.2 Tool Compounds for Testing
[Researching...]
### 11.3 Biomarker Strategy
[Researching...]
### 11.4 Clinical Biomarker Candidates
[Researching...]
### 11.5 Disease Models to Test
[Researching...]

## 12. Risk Assessment
### 12.1 Key Risks
[Researching...]
### 12.2 Mitigation Strategies
[Researching...]
### 12.3 Competitive Landscape
[Researching...]

## 13. Completeness Checklist
[To be populated post-audit...]

## 14. Data Sources & Methodology
[Will be populated as research progresses...]
```

---

## Completeness Checklist (MANDATORY)

Before finalizing, verify:

```markdown
## 13. Completeness Checklist

### Phase Coverage
- [ ] Phase 0: Target disambiguation (all IDs resolved)
- [ ] Phase 1: Disease association (OT + GWAS + gnomAD + literature)
- [ ] Phase 2: Druggability (tractability + class + structure + probes)
- [ ] Phase 3: Chemical matter (ChEMBL + BindingDB + PubChem + drugs)
- [ ] Phase 4: Clinical precedent (FDA + trials + failures)
- [ ] Phase 5: Safety (OT safety + expression + KO + ADRs + paralogs)
- [ ] Phase 6: Pathway context (Reactome + STRING + GO)
- [ ] Phase 7: Validation evidence (DepMap + literature + models)
- [ ] Phase 8: Structural insights (PDB + AlphaFold + pockets + domains)
- [ ] Phase 9: Literature (collision-aware + metrics + key papers)
- [ ] Phase 10: Validation roadmap (score + recommendations)

### Data Quality
- [ ] All scores justified with specific data
- [ ] Evidence grades (T1-T4) assigned to key claims
- [ ] Negative results documented (not left blank)
- [ ] Failed tools with fallbacks documented
- [ ] Source citations for all data points

### Scoring
- [ ] All 12 score components calculated
- [ ] Total score summed correctly
- [ ] Priority tier assigned
- [ ] GO/NO-GO recommendation justified
```

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 | If All Fail |
|--------------|------------|------------|-------------|
| `OpenTargets_get_diseases_phenotypes_*` | `CTD_get_gene_diseases` | PubMed search | Note in report |
| `GTEx_get_median_gene_expression` (versioned) | GTEx (unversioned) | `HPA_search_genes_by_query` | Document gap |
| `ChEMBL_get_target_activities` | `BindingDB_get_ligands_by_uniprot` | `DGIdb_get_gene_info` | Note in report |
| `gnomad_get_gene_constraints` | `OpenTargets_get_target_constraint_info_*` | - | Note as unavailable |
| `Reactome_map_uniprot_to_pathways` | `OpenTargets_get_target_gene_ontology_*` | - | Use GO only |
| `STRING_get_protein_interactions` | `intact_get_interactions` | `OpenTargets interactions` | Note in report |
| `ProteinsPlus_predict_binding_sites` | `alphafold_get_prediction` | Literature pockets | Note as limited |

---

## Modality-Specific Considerations

### Small Molecule Focus
- Emphasize: binding pockets, ChEMBL compounds, Lipinski compliance
- Key tractability: OpenTargets SM tractability bucket
- Structure: co-crystal structures with small molecule ligands
- Chemical matter: IC50/Ki/Kd data from ChEMBL/BindingDB

### Antibody Focus
- Emphasize: extracellular domains, cell surface expression, glycosylation
- Key tractability: OpenTargets AB tractability bucket
- Structure: ectodomain structures, epitope mapping
- Expression: surface expression in disease vs normal tissue

### PROTAC Focus
- Emphasize: intracellular targets, surface lysines, E3 ligase proximity
- Key tractability: OpenTargets PROTAC tractability
- Structure: full-length structures for linker design
- Chemical matter: known binders + E3 ligase binders

---

## Quick Reference: Verified Tool Parameters

| Tool | Parameters | Notes |
|------|-----------|-------|
| `ensembl_lookup_gene` | `gene_id`, `species` | species="homo_sapiens" REQUIRED; response wrapped in `{status, data, url, content_type}` |
| `OpenTargets_get_*_by_ensemblID` | `ensemblId` | camelCase, NOT ensemblID |
| `OpenTargets_get_publications_by_target_ensemblID` | `entityId` | NOT ensemblId |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId`, `size` | size is REQUIRED |
| `OpenTargets_target_disease_evidence` | `efoId`, `ensemblId` | Both REQUIRED |
| `GTEx_get_median_gene_expression` | `operation`, `gencode_id` | operation="median" REQUIRED |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` | ALL 3 required |
| `PubMed_search_articles` | `query`, `limit` | Returns plain list, NOT {articles:[]} |
| `UniProt_get_function_by_accession` | `accession` | Returns list of strings |
| `alphafold_get_prediction` | `qualifier` | NOT uniprot_accession |
| `drugbank_get_safety_*` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL required |
| `STRING_get_protein_interactions` | `protein_ids`, `species` | protein_ids is array; species=9606 |
| `Reactome_map_uniprot_to_pathways` | `id` | NOT uniprot_id |
| `ChEMBL_get_target_activities` | `target_chembl_id__exact` | Note double underscore |
| `search_clinical_trials` | `query_term` | REQUIRED parameter |
| `gnomad_get_gene_constraints` | `gene_symbol` | NOT gene_id |
| `DepMap_get_gene_dependencies` | `gene_symbol` | NOT gene_id |
| `BindingDB_get_ligands_by_uniprot` | `uniprot`, `affinity_cutoff` | affinity in nM |
| `Pharos_get_target` | `gene` or `uniprot` | Both optional but need one |

---

## Example Execution: EGFR for NSCLC

### Phase 0 Result
- Symbol: EGFR, Ensembl: ENSG00000146648, UniProt: P00533, ChEMBL: CHEMBL203

### Expected Scores (EGFR for NSCLC)
- Disease Association: ~28/30 (strong genetic + pathway + literature)
- Druggability: ~24/25 (kinase, many structures, abundant compounds)
- Safety: ~14/20 (widely expressed but manageable toxicity)
- Clinical Precedent: 15/15 (multiple approved drugs)
- Validation Evidence: ~9/10 (extensive functional data)
- **Total: ~90/100 = Tier 1**

### Example for Novel Target (e.g., understudied kinase)
- Disease Association: ~8/30 (limited GWAS, few publications)
- Druggability: ~15/25 (kinase family bonus, AlphaFold structure)
- Safety: ~12/20 (limited data, unknown KO phenotype)
- Clinical Precedent: 0/15 (no clinical development)
- Validation Evidence: ~2/10 (minimal functional data)
- **Total: ~37/100 = Tier 4**
