# tooluniverse-network-pharmacology

> Construct and analyze compound-target-disease networks for drug repurposing, polypharmacology discovery, and systems pharmacology. Builds multi-layer networks from ChEMBL, OpenTargets, STRING, DrugBank, Reactome, FAERS, and 60+ other ToolUniverse tools. Calculates Network Pharmacology Scores (0-100), identifies repurposing candidates, predicts mechanisms, and analyzes polypharmacology. Use when users ask about drug repurposing via network analysis, multi-target drug effects, compound-target-disease networks, systems pharmacology, or polypharmacology.

# Network Pharmacology Pipeline

Construct and analyze compound-target-disease (C-T-D) networks to identify drug repurposing opportunities, understand polypharmacology, and predict drug mechanisms using systems pharmacology approaches.

**IMPORTANT**: Always use English terms in tool calls (drug names, disease names, target names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

---

## When to Use This Skill

Apply when users:
- Ask "Can [drug] be repurposed for [disease] based on network analysis?"
- Want to understand multi-target (polypharmacology) effects of a compound
- Need compound-target-disease network construction and analysis
- Ask about network proximity between drug targets and disease genes
- Want systems pharmacology analysis of a drug or target
- Ask about drug repurposing candidates ranked by network metrics
- Need mechanism prediction for a drug in a new indication
- Want to identify hub genes in disease networks as therapeutic targets
- Ask about disease module coverage by a compound's targets

**NOT for** (use other skills instead):
- Simple drug repurposing without network analysis -> Use `tooluniverse-drug-repurposing`
- Single target validation -> Use `tooluniverse-drug-target-validation`
- Adverse event detection only -> Use `tooluniverse-adverse-event-detection`
- General disease research -> Use `tooluniverse-disease-research`
- GWAS interpretation -> Use `tooluniverse-gwas-snp-interpretation`

---

## Input Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| **entity** | Yes | Compound name/ID, target gene symbol/ID, or disease name/ID | `metformin`, `EGFR`, `Alzheimer disease` |
| **entity_type** | No | Type hint: `compound`, `target`, or `disease` (auto-detected if omitted) | `compound` |
| **analysis_mode** | No | `compound-to-disease`, `disease-to-compound`, `target-centric`, `bidirectional` (default) | `bidirectional` |
| **secondary_entity** | No | Second entity for focused analysis (e.g., disease for compound input) | `Alzheimer disease` |

---

## Network Pharmacology Score (0-100)

### Score Components

**Network Proximity** (0-35 points):
- Strong proximity (Z < -2, p < 0.01): 35 points
- Moderate proximity (Z < -1, p < 0.05): 20 points
- Weak proximity (Z < -0.5): 10 points
- No proximity: 0 points

**Clinical Evidence** (0-25 points):
- Approved for related indication: 25 points
- Active clinical trials: 15 points
- Completed trials with positive results: 10 points
- Preclinical only: 5 points

**Target-Disease Association** (0-20 points):
- Strong genetic evidence (GWAS, rare variants): 20 points
- Moderate evidence (pathways, literature): 12 points
- Weak evidence (computational only): 5 points

**Safety Profile** (0-10 points):
- FDA-approved, favorable safety: 10 points
- Known manageable adverse events: 7 points
- Significant safety concerns: 3 points
- Black box warning relevant to indication: 0 points

**Mechanism Plausibility** (0-10 points):
- Clear pathway mechanism with functional evidence: 10 points
- Indirect mechanism via network neighbors: 6 points
- Purely computational prediction: 2 points

### Priority Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| **80-100** | Tier 1 | High repurposing potential - proceed with experimental validation |
| **60-79** | Tier 2 | Good potential - needs mechanistic validation |
| **40-59** | Tier 3 | Moderate potential - high-risk/high-reward, needs extensive validation |
| **0-39** | Tier 4 | Low potential - consider alternative approaches |

### Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Human clinical proof, regulatory evidence | FDA-approved indication, Phase III trial, patient genomics |
| **T2** | [T2] | Functional experimental evidence | Bioactivity data (IC50 < 1 uM), CRISPR screen, animal model |
| **T3** | [T3] | Association/computational evidence | GWAS hit, network proximity, pathway enrichment, expression |
| **T4** | [T4] | Prediction, annotation, text-mining | AlphaFold prediction, database annotation, literature co-mention |

---

## KEY PRINCIPLES

1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Entity disambiguation FIRST** - Resolve all identifiers before analysis
3. **Bidirectional network** - Construct C-T-D network comprehensively from both directions
4. **Network metrics** - Calculate proximity, centrality, module overlap quantitatively
5. **Rank candidates** - Prioritize by composite Network Pharmacology Score
6. **Mechanism prediction** - Explain HOW drug could work for disease via network paths
7. **Clinical feasibility** - FDA-approved drugs ranked higher than preclinical
8. **Safety context** - Flag known adverse events and off-target liabilities
9. **Evidence grading** - Grade all evidence T1-T4
10. **Negative results documented** - "No data" is data; empty sections are failures
11. **Source references** - Every finding must cite the source tool/database
12. **Completeness checklist** - Mandatory section at end showing analysis coverage

---

## Complete Workflow

### Phase 0: Entity Disambiguation and Report Setup

**Step 0.1**: Create the report file immediately.

```python
# Create report file FIRST
report_path = "[entity]_network_pharmacology_report.md"
# Write header and placeholder sections
```

**Step 0.2**: Resolve the input entity to all required identifiers.

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse(use_cache=True)
tu.load_tools()

# === COMPOUND DISAMBIGUATION ===
# Get ChEMBL ID from drug name
drug_info = tu.tools.OpenTargets_get_drug_chembId_by_generic_name(
    drugName="metformin"
)
# Returns: {data: {search: {hits: [{id: "CHEMBL1431", name: "METFORMIN", ...}]}}}
chembl_id = drug_info['data']['search']['hits'][0]['id']

# Get drug details (mechanism, indications)
drug_desc = tu.tools.OpenTargets_get_drug_id_description_by_name(
    drugName="metformin"
)

# Get DrugBank info
drugbank_info = tu.tools.drugbank_get_drug_basic_info_by_drug_name_or_id(
    query="metformin", case_sensitive=False, exact_match=True, limit=1
)
# Returns: {status: "success", data: {drug_name: ..., drugbank_id: ..., ...}}

# Get PubChem CID and SMILES
pubchem_cid = tu.tools.PubChem_get_CID_by_compound_name(
    name="metformin"
)
# Returns: {IdentifierList: {CID: [4091]}}
cid = pubchem_cid['IdentifierList']['CID'][0]

# Get SMILES
pubchem_props = tu.tools.PubChem_get_compound_properties_by_CID(
    cid=cid
)
# Returns: {CID: ..., MolecularWeight: ..., ConnectivitySMILES: ..., IUPACName: ...}

# === TARGET DISAMBIGUATION ===
# Get Ensembl ID from gene symbol
target_info = tu.tools.OpenTargets_get_target_id_description_by_name(
    targetName="PSEN1"
)
# Returns: {data: {search: {hits: [{id: "ENSG00000080815", name: "PSEN1", ...}]}}}
ensembl_id = target_info['data']['search']['hits'][0]['id']

# Get gene details from Ensembl
gene_details = tu.tools.ensembl_lookup_gene(
    gene_id=ensembl_id, species='homo_sapiens'
)
# Returns: {status: "success", data: {display_name: ..., biotype: ..., ...}}

# Get MyGene info for cross-references
mygene = tu.tools.MyGene_query_genes(query="PSEN1")

# === DISEASE DISAMBIGUATION ===
# Get disease ID and description
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(
    diseaseName="Alzheimer disease"
)
# Returns: {data: {search: {hits: [{id: "MONDO_0004975", name: "Alzheimer disease", ...}]}}}
disease_id = disease_info['data']['search']['hits'][0]['id']

# Get disease description
disease_desc = tu.tools.OpenTargets_get_disease_description_by_efoId(
    efoId=disease_id
)

# Get cross-references
disease_ids = tu.tools.OpenTargets_get_disease_ids_by_efoId(efoId=disease_id)
```

---

### Phase 1: Network Node Identification

**Step 1.1**: Identify compound nodes.

```python
# Get drug targets and mechanism of action from OpenTargets
drug_moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(
    chemblId=chembl_id
)
# Returns: {data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction: ..., actionType: ..., targetName: ..., targets: [{id, approvedSymbol}]}]}}}}

# Get associated targets from OpenTargets
drug_targets_ot = tu.tools.OpenTargets_get_associated_targets_by_drug_chemblId(
    chemblId=chembl_id, size=50
)
# Returns: {data: {drug: {linkedTargets: {count: N, rows: [{id, approvedSymbol}]}}}}

# Get targets from DrugBank
drug_targets_db = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    query="metformin", case_sensitive=False, exact_match=True, limit=1
)
# Returns: {status: "success", data: {drug_name: ..., targets: [{id, name, organism, actions}]}}

# Get drug-gene interactions from DGIdb
dgidb_interactions = tu.tools.DGIdb_get_drug_gene_interactions(
    genes=["PSEN1", "APP", "BACE1"]  # for disease-to-compound mode
)
# Returns: {data: {genes: {nodes: [{name, interactions: [{drug: {name, conceptId}, interactionTypes: [{type}]}]}]}}}

# Get chemical-gene interactions from CTD
ctd_genes = tu.tools.CTD_get_chemical_gene_interactions(
    input_terms="Metformin"
)
# Returns: {data: [{ChemicalName, GeneSymbol, InteractionActions, ...}]}

# Get STITCH chemical-protein interactions
stitch_id = tu.tools.STITCH_resolve_identifier(
    identifier="metformin", species=9606
)
# Then query interactions
stitch_interactions = tu.tools.STITCH_get_chemical_protein_interactions(
    identifiers=["CIDm000004091"], species=9606
)

# Get current indications
drug_indications = tu.tools.OpenTargets_get_drug_indications_by_chemblId(
    chemblId=chembl_id, size=50
)
# Returns: {data: {drug: {indications: {rows: [{disease: {id, name}, maxPhaseForIndication, references}]}}}}

# Check FDA approval status
fda_approval = tu.tools.OpenTargets_get_drug_approval_status_by_chemblId(
    chemblId=chembl_id
)

# Get associated diseases for drug (all trials/investigations)
drug_diseases = tu.tools.OpenTargets_get_associated_diseases_by_drug_chemblId(
    chemblId=chembl_id, size=50
)
# Returns: {data: {drug: {linkedDiseases: {count: N, rows: [{id, name, description}]}}}}
```

**Step 1.2**: Identify target nodes (disease-associated targets).

```python
# Get disease-associated targets from OpenTargets
disease_targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(
    efoId=disease_id, limit=50
)
# Returns: {data: {disease: {associatedTargets: {count: N, rows: [{target: {id, approvedSymbol}, score}]}}}}

# Get disease-target evidence for top targets
for target in disease_targets['data']['disease']['associatedTargets']['rows'][:10]:
    evidence = tu.tools.OpenTargets_target_disease_evidence(
        efoId=disease_id,
        ensemblId=target['target']['id']
    )

# Get GWAS evidence for targets
gwas_studies = tu.tools.OpenTargets_search_gwas_studies_by_disease(
    diseaseIds=[disease_id], size=20
)
# Returns: {data: {studies: {count: N, rows: [...]}}}

# Get gene-disease associations from CTD
ctd_diseases = tu.tools.CTD_get_gene_diseases(
    input_terms="PSEN1"
)

# Get Pharos target info (druggability levels)
for gene in ["PSEN1", "APP", "BACE1"]:
    pharos = tu.tools.Pharos_get_target(target_name=gene)
    # Returns target development level (Tclin, Tchem, Tbio, Tdark)
```

**Step 1.3**: Identify disease nodes and related conditions.

```python
# Get related/similar diseases
related_diseases = tu.tools.OpenTargets_get_similar_entities_by_disease_efoId(
    efoId=disease_id, size=10, threshold=0.5
)
# Returns: {data: {disease: {similarEntities: [{id, category, score, object: {id, name}}]}}}

# Get disease hierarchy (children/parents)
disease_children = tu.tools.OpenTargets_get_disease_descendants_children_by_efoId(
    efoId=disease_id
)
disease_parents = tu.tools.OpenTargets_get_disease_ancestors_parents_by_efoId(
    efoId=disease_id
)

# Get phenotypes associated with disease
disease_phenotypes = tu.tools.OpenTargets_get_associated_phenotypes_by_disease_efoId(
    efoId=disease_id, size=20
)

# Get therapeutic areas
disease_areas = tu.tools.OpenTargets_get_disease_therapeutic_areas_by_efoId(
    efoId=disease_id
)
```

---

### Phase 2: Network Edge Construction

**Step 2.1**: Compound-target edges (bioactivity data).

```python
# Get ChEMBL bioactivity data for drug targets
chembl_activities = tu.tools.ChEMBL_get_target_activities(
    target_chembl_id__exact="CHEMBL2111455",  # example target ChEMBL ID
    limit=50
)
# Returns activity data with pchembl_value, standard_type (IC50, Ki, etc.)

# Search ChEMBL mechanisms (all mechanisms for drug)
all_mechanisms = tu.tools.ChEMBL_search_mechanisms(
    query="metformin", limit=50
)

# Get DrugBank drug targets with action types
db_targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    query="metformin", case_sensitive=False, exact_match=True, limit=1
)
# Returns: targets with action type (inhibitor, substrate, etc.)

# Get pharmacology from DrugBank
db_pharmacology = tu.tools.drugbank_get_pharmacology_by_drug_name_or_drugbank_id(
    query="metformin", case_sensitive=False, exact_match=True, limit=1
)

# Get BindingDB ligands for key targets (if UniProt ID available)
# binding_data = tu.tools.BindingDB_get_ligands_by_uniprot(uniprot_accession="P49768")
```

**Step 2.2**: Target-disease edges (genetic and functional associations).

```python
# Get OpenTargets target-disease evidence
for target in top_disease_targets[:10]:
    td_evidence = tu.tools.OpenTargets_target_disease_evidence(
        efoId=disease_id,
        ensemblId=target['target']['id']
    )
    # Returns: evidence across datasources (genetics, pathways, literature, etc.)

# Get GWAS associations for key genes
for gene_symbol in ["PSEN1", "APP", "APOE"]:
    gwas_assoc = tu.tools.GWAS_search_associations_by_gene(gene_name=gene_symbol)

# Get gene-disease links from CTD
ctd_gene_diseases = tu.tools.CTD_get_gene_diseases(
    input_terms="PSEN1"
)

# Get PharmGKB gene details (pharmacogenomics)
pharmgkb_gene = tu.tools.PharmGKB_get_gene_details(gene_symbol="PSEN1")
```

**Step 2.3**: Compound-disease edges (clinical evidence).

```python
# Get clinical trial evidence
trials = tu.tools.search_clinical_trials(
    query_term="metformin",
    condition="Alzheimer",
    pageSize=20
)
# Returns: {studies: [{NCT ID, brief_title, brief_summary, ...}]}

# Also search with clinical_trials_search
trials2 = tu.tools.clinical_trials_search(
    query="metformin Alzheimer disease",
    limit=20
)

# Get CTD chemical-disease associations
ctd_chem_diseases = tu.tools.CTD_get_chemical_diseases(
    input_terms="Metformin"
)
# Returns: [{ChemicalName, DiseaseName, DirectEvidence: "therapeutic"|"marker/mechanism", ...}]

# Literature evidence (PubMed co-mentions)
pubmed_results = tu.tools.PubMed_search_articles(
    query="metformin Alzheimer disease",
    max_results=50
)
# Returns: list of {pmid, title, authors, journal, pub_date, ...}

# Europe PMC search for broader coverage
europepmc_results = tu.tools.EuropePMC_search_articles(
    query="metformin Alzheimer disease",
    limit=50
)
```

**Step 2.4**: Target-target edges (PPI network).

```python
# Get STRING protein-protein interactions
string_ppi = tu.tools.STRING_get_interaction_partners(
    protein_ids=["PSEN1", "APP", "APOE", "BACE1", "MAPT"],
    species=9606,
    limit=20
)
# Returns: {status: "success", data: [{stringId_A, stringId_B, preferredName_A, preferredName_B, score, ...}]}

# Get full STRING network
string_network = tu.tools.STRING_get_network(
    protein_ids=["PSEN1", "APP", "APOE", "BACE1", "MAPT"],
    species=9606
)

# Get IntAct interactions
intact_results = tu.tools.intact_search_interactions(
    query="PSEN1", max=20
)

# Get OpenTargets target interactions
ot_interactions = tu.tools.OpenTargets_get_target_interactions_by_ensemblID(
    ensemblId="ENSG00000080815",  # PSEN1
    size=20
)
# Returns: {data: {target: {interactions: {count: N, rows: [{intA, targetA: {id, approvedSymbol}, intB, targetB: {id, approvedSymbol}, score, sourceDatabase}]}}}}

# HumanBase tissue-specific PPI
humanbase_ppi = tu.tools.humanbase_ppi_analysis(
    gene_list=["PSEN1", "APP", "APOE", "BACE1", "MAPT"],
    tissue="brain",
    max_node=50,
    interaction="sn",
    string_mode="physical"
)
```

---

### Phase 3: Network Analysis

**Step 3.1**: Network topology analysis (computed from collected data).

```
Compute from Phase 2 data:

1. Node Degree:
   - Count connections per node from STRING + IntAct + OpenTargets interactions
   - Drug targets: connections from bioactivity data
   - Disease genes: connections from PPI data

2. Hub Identification:
   - Nodes with degree > mean + 2*SD are hubs
   - Hub genes in disease module = priority therapeutic targets

3. Betweenness Centrality:
   - Nodes on shortest paths between drug targets and disease genes
   - High betweenness = potential mediating/bridging targets

4. Network Modules:
   - Disease module: cluster of disease-associated genes in PPI
   - Drug module: cluster of drug target genes in PPI
   - Module overlap = direct network relevance

5. Shortest Paths:
   - Paths from each drug target to each disease gene via PPI
   - Shortest path length < 2 = direct interaction
   - Path length 2-3 = close proximity
   - Path length > 4 = distant, weaker association
```

**Step 3.2**: Network proximity calculation.

```
Network Proximity Z-score (computed from data):

1. Collect drug target set T_d from Phase 1
2. Collect disease gene set G_d from Phase 1
3. For each drug target t in T_d and disease gene g in G_d:
   - Find shortest path d(t,g) in PPI network from Phase 2
4. Compute closest proximity: d_c = mean of min distances
5. Compare against random expectation:
   - Sample N random gene sets of same size as T_d
   - Compute proximity for each random set
   - Z = (d_c - mean_random) / sd_random
6. Z < -2: strong proximity (35 points)
   Z < -1: moderate proximity (20 points)
   Z < -0.5: weak proximity (10 points)
   Z >= -0.5: no proximity (0 points)

Practical computation from STRING/OpenTargets PPI data:
- Count direct interactions between drug targets and disease genes
- Count shared PPI partners (second-degree connections)
- Calculate overlap coefficient = shared_partners / min(degree_t, degree_d)
- Use number of shared pathways as additional proximity metric
```

**Step 3.3**: Functional enrichment analysis.

```python
# STRING functional enrichment for disease genes
disease_gene_symbols = [t['target']['approvedSymbol']
                        for t in disease_targets['data']['disease']['associatedTargets']['rows'][:20]]

string_enrichment = tu.tools.STRING_functional_enrichment(
    protein_ids=disease_gene_symbols,
    species=9606
)

# STRING PPI enrichment (statistical test for network connectivity)
string_ppi_enrich = tu.tools.STRING_ppi_enrichment(
    protein_ids=disease_gene_symbols,
    species=9606
)

# Enrichr pathway analysis
enrichr_results = tu.tools.enrichr_gene_enrichment_analysis(
    gene_list=disease_gene_symbols,
    libs=["KEGG_2021_Human", "Reactome_2022", "GO_Biological_Process_2023"]
)
# Returns enrichment results per library

# Reactome pathway enrichment
reactome_enrichment = tu.tools.ReactomeAnalysis_pathway_enrichment(
    identifiers=" ".join(disease_gene_symbols)
)
# Returns: {data: {pathways: [{pathway_id, name, p_value, fdr, entities_found, ...}]}}
```

---

### Phase 4: Drug Repurposing Predictions

**Step 4.1**: Identify and rank repurposing candidates.

```python
# For disease-to-compound mode: Find drugs targeting disease genes
repurposing_candidates = []

for target in disease_targets['data']['disease']['associatedTargets']['rows'][:20]:
    gene_symbol = target['target']['approvedSymbol']
    ensembl_id = target['target']['id']
    target_score = target['score']

    # Get drugs from OpenTargets
    target_drugs = tu.tools.OpenTargets_get_associated_drugs_by_target_ensemblID(
        ensemblId=ensembl_id, size=20
    )

    # Get drugs from DGIdb
    dgidb_drugs = tu.tools.DGIdb_get_drug_gene_interactions(genes=[gene_symbol])

    # Get drugs from DrugBank
    drugbank_drugs = tu.tools.drugbank_get_drug_name_and_description_by_target_name(
        query=gene_symbol, case_sensitive=False, exact_match=False, limit=20
    )

    # Collect and deduplicate candidates
    # Score each by: target_disease_score * drug_target_affinity * approval_status

# For compound-to-disease mode: Already have drug targets, find their diseases
for target in drug_targets:
    # Get diseases associated with each drug target
    target_diseases = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(
        ensemblId=target['id'], size=20
    )
```

**Step 4.2**: Mechanism prediction for repurposing candidates.

```python
# For each repurposing candidate, trace the network path:
# Drug -> Direct targets -> PPI neighbors -> Disease genes

# Get drug mechanism
drug_moa = tu.tools.OpenTargets_get_drug_mechanisms_of_action_by_chemblId(
    chemblId=candidate_chembl_id
)

# Get pathways shared between drug targets and disease genes
drug_target_genes = [t['approvedSymbol'] for t in drug_moa_targets]
combined_genes = list(set(drug_target_genes + disease_gene_symbols[:10]))

# Pathway enrichment for combined gene set
combined_pathways = tu.tools.ReactomeAnalysis_pathway_enrichment(
    identifiers=" ".join(combined_genes)
)

# Check for specific pathway overlap
drug_pathways = tu.tools.drugbank_get_pathways_reactions_by_drug_or_id(
    query=drug_name, case_sensitive=False, exact_match=True, limit=1
)
```

---

### Phase 5: Polypharmacology Analysis

**Step 5.1**: Multi-target profiling.

```python
# Get ALL targets of compound (on-targets + off-targets)
# From OpenTargets
all_drug_targets = tu.tools.OpenTargets_get_associated_targets_by_drug_chemblId(
    chemblId=chembl_id, size=100
)

# From DrugBank (includes enzymes, carriers, transporters)
db_full_targets = tu.tools.drugbank_get_targets_by_drug_name_or_drugbank_id(
    query=drug_name, case_sensitive=False, exact_match=True, limit=1
)

# From CTD (chemical-gene interactions, includes indirect)
ctd_interactions = tu.tools.CTD_get_chemical_gene_interactions(
    input_terms=drug_name
)

# Classify targets: primary (mechanism) vs secondary (off-target)
# Count disease module coverage
drug_target_set = set(drug_target_genes)
disease_gene_set = set(disease_gene_symbols[:50])
overlap = drug_target_set & disease_gene_set
coverage = len(overlap) / len(disease_gene_set) if disease_gene_set else 0

# Target family analysis
for gene in drug_target_genes[:10]:
    target_class = tu.tools.OpenTargets_get_target_classes_by_ensemblID(
        ensemblId=gene_ensembl_id
    )
```

**Step 5.2**: Selectivity analysis.

```python
# Get target druggability and development levels
for gene in drug_target_genes[:10]:
    # DGIdb druggability
    druggability = tu.tools.DGIdb_get_gene_druggability(genes=[gene])

    # Pharos target development level
    pharos_info = tu.tools.Pharos_get_target(target_name=gene)
    # Tclin = known drug targets, Tchem = has chemical tools, Tbio = has biology, Tdark = dark target

    # OpenTargets tractability
    tractability = tu.tools.OpenTargets_get_target_tractability_by_ensemblID(
        ensemblId=gene_ensembl_id
    )
```

---

### Phase 6: Safety and Toxicity Context

**Step 6.1**: Adverse event profiling.

```python
# Get FAERS adverse event data
faers_ae = tu.tools.FAERS_search_reports_by_drug_and_reaction(
    drug_name=drug_name, limit=100
)

# Get serious events
faers_serious = tu.tools.FAERS_filter_serious_events(
    operation="filter_serious_events",
    drug_name=drug_name,
    seriousness_type="all"
)

# Get death reports
faers_death = tu.tools.FAERS_count_death_related_by_drug(
    medicinalproduct=drug_name
)
# Returns: [{term: "alive", count: N}, {term: "death", count: N}]

# Calculate disproportionality for key AEs
faers_signal = tu.tools.FAERS_calculate_disproportionality(
    operation="calculate_disproportionality",
    drug_name=drug_name,
    adverse_event="lactic acidosis"  # example
)
# Returns: {metrics: {PRR: {value, ci_95_lower, ci_95_upper}, ROR: {...}}, signal_detection: {signal_detected, signal_strength}}

# Get FDA warnings
fda_warnings = tu.tools.FDA_get_warnings_and_cautions_by_drug_name(
    drug_name=drug_name
)

# Get black box warning status
bbox_warning = tu.tools.OpenTargets_get_drug_blackbox_status_by_chembl_ID(
    chemblId=chembl_id
)

# Get drug adverse events from OpenTargets
ot_ae = tu.tools.OpenTargets_get_drug_adverse_events_by_chemblId(
    chemblId=chembl_id
)
# Returns: {data: {drug: {adverseEvents: {count, rows: [{name, meddraCode, count, logLR}]}}}}

# Get drug warnings from OpenTargets
drug_warnings = tu.tools.OpenTargets_get_drug_warnings_by_chemblId(
    chemblId=chembl_id
)
```

**Step 6.2**: Target safety profiling.

```python
# For each drug target, assess safety
for target_ensembl_id in drug_target_ensembl_ids[:10]:
    # OpenTargets target safety profile
    safety = tu.tools.OpenTargets_get_target_safety_profile_by_ensemblID(
        ensemblId=target_ensembl_id
    )

    # Gene constraint (is target essential?)
    constraints = tu.tools.gnomad_get_gene_constraints(gene_symbol=gene_symbol)
    # High pLI (>0.9) = loss-of-function intolerant = essential gene = safety concern

    # Expression pattern (broadly expressed = more off-target risk)
    expression = tu.tools.HPA_get_rna_expression_by_source(
        gene_name=gene_symbol,
        source_type="tissue",
        source_name="brain"
    )
```

---

### Phase 7: Validation Evidence

**Step 7.1**: Clinical precedent.

```python
# Search clinical trials for drug + disease combination
trials = tu.tools.search_clinical_trials(
    query_term=drug_name,
    condition=disease_name,
    pageSize=20
)

# Get trial details for each match
for trial in trials.get('studies', [])[:5]:
    nct_id = trial['NCT ID']
    trial_details = tu.tools.clinical_trials_get_details(nct_id=nct_id)
    trial_outcomes = tu.tools.extract_clinical_trial_outcomes(nct_id=nct_id)
    trial_ae = tu.tools.extract_clinical_trial_adverse_events(nct_id=nct_id)

# Check approved indications
approved = tu.tools.OpenTargets_get_approved_indications_by_drug_chemblId(
    chemblId=chembl_id
)
# Returns: {data: {drug: {approvedIndications: ["EFO_XXXXX", ...]}}}
```

**Step 7.2**: Literature evidence.

```python
# PubMed search for drug-disease co-mentions
pubmed_evidence = tu.tools.PubMed_search_articles(
    query=f"{drug_name} {disease_name} repurposing OR repositioning OR network pharmacology",
    max_results=50
)
# Returns: list of {pmid, title, authors, journal, pub_date, ...}

# Europe PMC with broader scope
europepmc_evidence = tu.tools.EuropePMC_search_articles(
    query=f"{drug_name} {disease_name}",
    limit=50
)

# OpenTargets publications for drug
ot_drug_pubs = tu.tools.OpenTargets_get_publications_by_drug_chemblId(
    chemblId=chembl_id, size=20
)

# OpenTargets publications for disease
ot_disease_pubs = tu.tools.OpenTargets_get_publications_by_disease_efoId(
    efoId=disease_id, size=20
)

# Get guideline searches
guidelines = tu.tools.PubMed_Guidelines_Search(query=f"{drug_name} {disease_name}")
```

**Step 7.3**: Experimental evidence.

```python
# ChEMBL bioactivity data
chembl_bioactivity = tu.tools.ChEMBL_search_drugs(
    query=drug_name, limit=10
)

# Check ADMET predictions (for novel formulation contexts)
if smiles:
    admet = tu.tools.ADMETAI_predict_toxicity(smiles=[smiles])
    bbb = tu.tools.ADMETAI_predict_BBB_penetrance(smiles=[smiles])
    bioavail = tu.tools.ADMETAI_predict_bioavailability(smiles=[smiles])

# PharmGKB pharmacogenomics data
pharmgkb_drug = tu.tools.PharmGKB_get_drug_details(drug_name=drug_name)
pharmgkb_clin = tu.tools.PharmGKB_get_clinical_annotations(query=drug_name)
```

---

### Phase 8: Report Generation

**Step 8.1**: Compute Network Pharmacology Score.

```
Score Calculation:

1. Network Proximity Score (0-35):
   - Count direct drug target <-> disease gene interactions in PPI
   - Count shared PPI partners
   - Count shared pathways
   - Map to Z-score equivalent based on overlap significance

2. Clinical Evidence Score (0-25):
   - Search clinical trials for drug-disease pair
   - Check approved indications for related diseases
   - Check max clinical trial phase

3. Target-Disease Association Score (0-20):
   - Average OpenTargets association score for drug targets in disease
   - Weight by evidence type (genetic > functional > computational)

4. Safety Score (0-10):
   - FDA approval status (+5)
   - Black box warning (-3)
   - Death reports proportion
   - Off-target count penalty

5. Mechanism Plausibility Score (0-10):
   - Known mechanism for related indication (+5)
   - Pathway evidence (+3)
   - Network path length to disease module (+2)

Total: sum of components (0-100)
```

**Step 8.2**: Generate comprehensive report.

```markdown
# Network Pharmacology Analysis: [Entity]

## Executive Summary
[2-3 sentence summary of key findings]

## Network Pharmacology Score: [X]/100 - [Tier]
| Component | Score | Max | Evidence |
|-----------|-------|-----|----------|
| Network Proximity | X | 35 | [summary] |
| Clinical Evidence | X | 25 | [summary] |
| Target-Disease Association | X | 20 | [summary] |
| Safety Profile | X | 10 | [summary] |
| Mechanism Plausibility | X | 10 | [summary] |
| **TOTAL** | **X** | **100** | |

## 1. Entity Profile
### Compound: [Name]
- ChEMBL ID: [ID]
- DrugBank ID: [ID]
- SMILES: [SMILES]
- Mechanism: [MOA]
- Approval status: [status]
- Current indications: [list]

### Disease: [Name]
- MONDO/EFO ID: [ID]
- Description: [brief]
- Top associated targets: [list with scores]
- Related diseases: [list]

## 2. Network Topology Summary
- **Total nodes**: X (Y compounds, Z targets, W diseases)
- **Total edges**: X (Y C-T, Z T-D, W C-D, V T-T)
- **Network density**: X
- **Hub nodes**: [list of top hub genes]
- **Modules detected**: X

### Drug Target Module
[List drug targets with degree and betweenness]

### Disease Gene Module
[List disease genes with degree and betweenness]

### Module Overlap
[Shared genes, shared pathways, overlap coefficient]

## 3. Network Proximity
- **Proximity measure**: [metric used]
- **Z-score**: [value]
- **Direct interactions**: X drug target-disease gene pairs
- **Shared PPI partners**: X genes
- **Shared pathways**: X pathways
- **Interpretation**: [strong/moderate/weak proximity]

## 4. Top Repurposing Candidates (Ranked)

### Candidate 1: [Drug Name] - Score: X/100
**ChEMBL ID**: [ID] | **Status**: [Approved/Clinical/Preclinical]
**Current indications**: [list]
**Network path**: Drug -> [target1, target2] -> [PPI] -> [disease gene1, gene2]
**Mechanism prediction**: [how drug could work for disease]
**Clinical evidence**: [trials, literature]
**Safety**: [key concerns]
**Evidence grade**: [T1-T4]

[Repeat for top 10 candidates]

## 5. Polypharmacology Profile
### Target Coverage
- Total drug targets: X
- Disease module targets hit: Y (Z%)
- Primary targets: [list with actions]
- Off-targets: [list with potential effects]

### Multi-Target Effects
[Analysis of synergistic vs antagonistic target modulation]

### Disease Module Coverage
[How well drug targets cover the disease network]

## 6. Pathway Analysis
### Drug-Affected Pathways
[Ranked list of pathways affected by drug]

### Disease-Associated Pathways
[Ranked list of pathways associated with disease]

### Overlapping Pathways (Mechanism)
[Pathways shared between drug and disease - these explain the mechanism]

## 7. Safety Considerations
### Adverse Events
[Top AEs with PRR/ROR where available]

### Target Safety Flags
[Targets with known safety liabilities]

### Off-Target Risks
[Off-targets in critical tissues]

### Drug-Drug Interaction Context
[Key DDI considerations]

## 8. Clinical Precedent
### Clinical Trials
[List of relevant trials with NCT IDs and status]

### Literature Evidence
[Key publications supporting or refuting repurposing hypothesis]
- N papers found for [drug] + [disease]
- Key findings: [summary]

### Pharmacogenomics
[Relevant PGx data]

## 9. Evidence Summary Table
| Finding | Source | Evidence Grade | Confidence |
|---------|--------|---------------|------------|
| [finding1] | [tool/database] | [T1-T4] | [High/Medium/Low] |
| ... | ... | ... | ... |

## 10. Recommendations
### Immediate Actions
1. [Action 1 - e.g., review clinical trial NCT00620191]
2. [Action 2 - e.g., validate mechanism in cell model]

### Further Investigation
1. [Investigation 1]
2. [Investigation 2]

### Risk Mitigation
1. [Risk 1 and mitigation strategy]

## Completeness Checklist
| Phase | Status | Tools Used | Key Findings |
|-------|--------|------------|--------------|
| Entity Disambiguation | Done/Partial/Failed | [tools] | [summary] |
| Compound Node ID | Done/Partial/Failed | [tools] | [summary] |
| Target Node ID | Done/Partial/Failed | [tools] | [summary] |
| Disease Node ID | Done/Partial/Failed | [tools] | [summary] |
| C-T Edges | Done/Partial/Failed | [tools] | [summary] |
| T-D Edges | Done/Partial/Failed | [tools] | [summary] |
| C-D Edges | Done/Partial/Failed | [tools] | [summary] |
| T-T Edges (PPI) | Done/Partial/Failed | [tools] | [summary] |
| Network Topology | Done/Partial/Failed | [computed] | [summary] |
| Network Proximity | Done/Partial/Failed | [computed] | [summary] |
| Pathway Enrichment | Done/Partial/Failed | [tools] | [summary] |
| Repurposing Candidates | Done/Partial/Failed | [tools] | [summary] |
| Mechanism Prediction | Done/Partial/Failed | [analysis] | [summary] |
| Polypharmacology | Done/Partial/Failed | [tools] | [summary] |
| Safety/Toxicity | Done/Partial/Failed | [tools] | [summary] |
| Clinical Precedent | Done/Partial/Failed | [tools] | [summary] |
| Literature Evidence | Done/Partial/Failed | [tools] | [summary] |
| Report Generation | Done/Partial/Failed | - | [summary] |
```

---

## Tool Parameter Reference (Verified)

### Compound Identification
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_chembId_by_generic_name` | `drugName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_drug_id_description_by_name` | `drugName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `drugbank_get_drug_basic_info_by_drug_name_or_id` | `query: str`, `case_sensitive: bool`, `exact_match: bool`, `limit: int` (ALL required) | `{status, data: {drug_name, drugbank_id, ...}}` |
| `PubChem_get_CID_by_compound_name` | `name: str` | `{IdentifierList: {CID: [int]}}` |
| `PubChem_get_compound_properties_by_CID` | `cid: int` | `{CID, MolecularWeight, ConnectivitySMILES, IUPACName}` |
| `ChEMBL_search_drugs` | `query: str`, `limit: int` | `{status, data: {drugs: [...]}}` |

### Target Identification
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_target_id_description_by_name` | `targetName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `ensembl_lookup_gene` | `gene_id: str`, `species: str` (REQUIRED, e.g., "homo_sapiens") | `{status, data: {display_name, biotype, ...}}` |
| `MyGene_query_genes` | `query: str` | Gene info with cross-references |
| `Pharos_get_target` | `target_name: str` | Target with development level |

### Disease Identification
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName: str` | `{data: {search: {hits: [{id, name, description}]}}}` |
| `OpenTargets_get_disease_description_by_efoId` | `efoId: str` | `{data: {disease: {id, name, description}}}` |
| `OpenTargets_get_disease_ids_by_efoId` | `efoId: str` | Disease cross-references |

### Network Edges
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `STRING_get_interaction_partners` | `protein_ids: list[str]`, `species: int` (9606), `limit: int` | `{status, data: [{stringId_A, stringId_B, preferredName_A, preferredName_B, score}]}` |
| `STRING_get_network` | `protein_ids: list[str]`, `species: int` | Network data |
| `STRING_functional_enrichment` | `protein_ids: list[str]`, `species: int` | Enrichment results |
| `STRING_ppi_enrichment` | `protein_ids: list[str]`, `species: int` | PPI enrichment statistics |
| `OpenTargets_get_target_interactions_by_ensemblID` | `ensemblId: str`, `size: int` | `{data: {target: {interactions: {count, rows: [{intA, targetA, intB, targetB, score}]}}}}` |
| `intact_search_interactions` | `query: str`, `max: int` | Interaction data |
| `humanbase_ppi_analysis` | `gene_list: list`, `tissue: str`, `max_node: int`, `interaction: str`, `string_mode: str` (ALL required) | Tissue-specific PPI |

### Drug-Target Edges
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_mechanisms_of_action_by_chemblId` | `chemblId: str` | `{data: {drug: {mechanismsOfAction: {rows: [{mechanismOfAction, actionType, targets}]}}}}` |
| `OpenTargets_get_associated_targets_by_drug_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {linkedTargets: {count, rows}}}}` |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | `query, case_sensitive, exact_match, limit` (ALL required) | `{status, data: {targets: [{id, name, organism, actions}]}}` |
| `DGIdb_get_drug_gene_interactions` | `genes: list[str]` | `{data: {genes: {nodes: [{name, interactions}]}}}` |
| `CTD_get_chemical_gene_interactions` | `input_terms: str` | `{data: [{ChemicalName, GeneSymbol, InteractionActions}]}` |
| `ChEMBL_get_target_activities` | `target_chembl_id__exact: str` | Activity data with pchembl_value |

### Target-Disease Edges
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_associated_targets_by_disease_efoId` | `efoId: str`, `limit: int` | `{data: {disease: {associatedTargets: {count, rows: [{target: {id, approvedSymbol}, score}]}}}}` |
| `OpenTargets_target_disease_evidence` | `efoId: str`, `ensemblId: str` (BOTH required) | Evidence data across datasources |
| `CTD_get_gene_diseases` | `input_terms: str` | `{data: [{GeneName, DiseaseName, DirectEvidence}]}` |
| `GWAS_search_associations_by_gene` | `gene_name: str` | GWAS association data |

### Drug-Disease Edges
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `OpenTargets_get_drug_indications_by_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {indications: {rows: [{disease, maxPhaseForIndication}]}}}}` |
| `OpenTargets_get_associated_diseases_by_drug_chemblId` | `chemblId: str`, `size: int` | `{data: {drug: {linkedDiseases: {count, rows}}}}` |
| `CTD_get_chemical_diseases` | `input_terms: str` | `{data: [{ChemicalName, DiseaseName, DirectEvidence}]}` |
| `search_clinical_trials` | `query_term: str` (REQUIRED), `condition: str`, `pageSize: int` | `{studies: [{NCT ID, brief_title, ...}]}` |

### Pathway Analysis
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `ReactomeAnalysis_pathway_enrichment` | `identifiers: str` (space-separated, NOT array) | `{data: {pathways: [{pathway_id, name, p_value, fdr, entities_found}]}}` |
| `enrichr_gene_enrichment_analysis` | `gene_list: list[str]`, `libs: list[str]` (REQUIRED) | Enrichment per library |
| `drugbank_get_pathways_reactions_by_drug_or_id` | `query, case_sensitive, exact_match, limit` | Pathway data |

### Safety Tools
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `FAERS_calculate_disproportionality` | `operation: str`, `drug_name: str`, `adverse_event: str` | `{metrics: {PRR, ROR, IC}, signal_detection}` |
| `FAERS_filter_serious_events` | `operation: str`, `drug_name: str`, `seriousness_type: str` | Serious event data |
| `FAERS_count_death_related_by_drug` | `medicinalproduct: str` | `[{term, count}]` |
| `OpenTargets_get_drug_adverse_events_by_chemblId` | `chemblId: str` | `{data: {drug: {adverseEvents: {count, rows}}}}` |
| `OpenTargets_get_drug_warnings_by_chemblId` | `chemblId: str` | Drug warning data |
| `OpenTargets_get_target_safety_profile_by_ensemblID` | `ensemblId: str` | Target safety data |
| `gnomad_get_gene_constraints` | `gene_symbol: str` | Gene constraint (pLI, LOEUF) |
| `FDA_get_warnings_and_cautions_by_drug_name` | `drug_name: str` | FDA warning text |

### Literature Tools
| Tool | Key Parameters | Response Structure |
|------|---------------|-------------------|
| `PubMed_search_articles` | `query: str`, `max_results: int` | list of `{pmid, title, authors, journal, pub_date}` |
| `EuropePMC_search_articles` | `query: str`, `limit: int` | Article list |
| `OpenTargets_get_publications_by_drug_chemblId` | `chemblId: str`, `size: int` | Publication data |

---

## Response Format Notes

**DrugBank tools**: ALL require `query`, `case_sensitive`, `exact_match`, `limit` (4 params, ALL required).

**FAERS analytics tools** (disproportionality, compare, filter, stratify, rollup, trends): ALL require `operation` parameter.

**FAERS count tools** (count_death, count_reactions, etc.): Use `medicinalproduct` NOT `drug_name`.

**OpenTargets tools**: Return nested `{data: {entity: {field: ...}}}` structure.

**PubMed_search_articles**: Returns plain **list** of dicts, NOT `{articles: [...]}`.

**PubChem CID lookup**: Returns `{IdentifierList: {CID: [...]}}` (NO data wrapper).

**ReactomeAnalysis_pathway_enrichment**: Takes space-separated `identifiers` string, NOT array.

**ensembl_lookup_gene**: REQUIRES `species='homo_sapiens'` parameter.

**STRING tools**: Return `{status: "success", data: [...]}`.

**CTD tools**: Return `{data: [...]}` with potentially large result sets.

---

## Fallback Strategies

| Phase | Primary Tool | Fallback 1 | Fallback 2 |
|-------|-------------|-----------|-----------|
| Compound ID | OpenTargets drug lookup | ChEMBL search | PubChem CID lookup |
| Target ID | OpenTargets target lookup | ensembl_lookup_gene | MyGene_query_genes |
| Disease ID | OpenTargets disease lookup | ols_search_efo_terms | CTD_get_chemical_diseases |
| Drug targets | OpenTargets drug mechanisms | DrugBank targets | DGIdb interactions |
| Disease targets | OpenTargets disease targets | CTD gene-diseases | GWAS associations |
| PPI network | STRING interactions | OpenTargets interactions | IntAct interactions |
| Pathways | ReactomeAnalysis enrichment | enrichr enrichment | STRING functional enrichment |
| Clinical trials | search_clinical_trials | clinical_trials_search | PubMed clinical |
| Safety | FAERS + FDA | OpenTargets AEs | DrugBank safety |
| Literature | PubMed search | EuropePMC search | OpenTargets publications |

---

## Common Use Patterns

### Pattern 1: Drug Repurposing via Network Proximity
```
Input: compound (metformin) + disease (Alzheimer disease)
Mode: compound-to-disease

Flow:
1. Resolve metformin -> CHEMBL1431, DB00331, CID:4091
2. Get metformin targets (OpenTargets, DrugBank, DGIdb)
3. Get Alzheimer disease genes (OpenTargets, GWAS)
4. Build PPI network (STRING, OpenTargets interactions)
5. Calculate proximity between drug targets and disease genes
6. Score and rank by Network Pharmacology Score
7. Predict mechanism via shared pathways
8. Validate with clinical trials and literature
```

### Pattern 2: Disease-Driven Drug Discovery
```
Input: disease (lupus)
Mode: disease-to-compound

Flow:
1. Resolve lupus -> MONDO/EFO ID
2. Get disease-associated targets (top 50)
3. For each target, find approved drugs (OpenTargets, DGIdb, DrugBank)
4. Build C-T-D network from all drug-target-disease edges
5. Rank drugs by: number of disease targets hit, network proximity, safety
6. Identify polypharmacology advantages (drugs hitting multiple disease targets)
```

### Pattern 3: Target-Centric Network
```
Input: target (EGFR)
Mode: target-centric

Flow:
1. Resolve EGFR -> ENSG00000146648
2. Get all compounds targeting EGFR (with bioactivity)
3. Get all diseases associated with EGFR
4. Build PPI network around EGFR
5. Identify which compounds could bridge to which diseases
6. Rank compound-disease pairs by network metrics
```

### Pattern 4: Polypharmacology Profiling
```
Input: compound (aspirin)
Mode: bidirectional

Flow:
1. Resolve aspirin -> CHEMBL25
2. Get ALL targets (not just primary)
3. Map targets to disease modules
4. Identify multi-target coverage across diseases
5. Analyze synergistic vs antagonistic effects
6. Compare selectivity across target families
```

### Pattern 5: Mechanism Elucidation
```
Input: compound (rapamycin) + disease (aging/longevity)
Mode: compound-to-disease

Flow:
1. Resolve rapamycin -> CHEMBL413 (sirolimus)
2. Get mechanism: mTOR inhibitor
3. Map mTOR pathway to aging-related genes
4. Trace network paths: rapamycin -> mTOR -> autophagy -> aging genes
5. Assess pathway overlap and functional enrichment
6. Provide mechanistic explanation
```

---

## Edge Cases

### Promiscuous Compounds (many targets)
- Limit initial target retrieval to top 50 by confidence
- Classify into primary (mechanism) vs secondary (off-target)
- Focus network analysis on primary targets first
- Note polypharmacology implications

### Orphan Diseases (limited data)
- Expand to parent disease categories in ontology
- Use related diseases from OpenTargets similar entities
- Leverage pathway-level analysis over gene-level
- Note data limitations in report

### Novel Targets (no known drugs)
- Focus on target biology and disease association
- Use DGIdb druggability assessment
- Search for chemical probes (OpenTargets chemical probes)
- Suggest target-based screening approaches

### Large Networks (>100 nodes)
- Prioritize top-scored edges
- Use network modules rather than full network
- Focus on shortest paths between entities
- Summarize statistics rather than listing all nodes

### Disconnected Networks
- Report disconnection explicitly
- Analyze drug module and disease module separately
- Look for pathway-level connections as bridge
- Note that disconnection suggests low repurposing potential

---

## Troubleshooting

**"Disease not found"**:
- Try disease synonyms (e.g., "Alzheimer's disease" vs "Alzheimer disease")
- Use EFO/MONDO ID directly if known
- Search with `OpenTargets_multi_entity_search_by_query_string(queryString=...)` for broader matching
- Try parent disease category

**"No drugs found for target"**:
- Target may be Tdark (no chemical tools) - check with Pharos
- Expand to target family or pathway
- Search DGIdb which aggregates multiple sources
- Check chemical probes as starting points

**"No PPI data"**:
- Try different protein identifiers (gene symbol, UniProt, Ensembl protein)
- Use multiple PPI databases (STRING + IntAct + OpenTargets)
- Lower confidence threshold in STRING
- Use pathway co-membership as proxy for interaction

**"Network proximity not significant"**:
- Drug targets may be functionally distant from disease module
- Try expanding disease gene set (increase limit)
- Consider indirect mechanisms via shared pathways
- Report honestly - not all drug-disease pairs have network support

**"DrugBank parameter errors"**:
- ALL DrugBank tools require 4 params: `query`, `case_sensitive`, `exact_match`, `limit`
- Use `case_sensitive=False`, `exact_match=True` for exact drug name matching
- Use `exact_match=False` for broader searches

**"FAERS operation errors"**:
- Analytics tools (disproportionality, compare, filter, stratify) need `operation` param
- Count tools use `medicinalproduct` NOT `drug_name`
- Check FAERS tool name carefully to determine which pattern

---

## Resources

For focused drug repurposing (without network analysis): [tooluniverse-drug-repurposing](../tooluniverse-drug-repurposing/SKILL.md)
For target validation: [tooluniverse-drug-target-validation](../tooluniverse-drug-target-validation/SKILL.md)
For adverse event detection: [tooluniverse-adverse-event-detection](../tooluniverse-adverse-event-detection/SKILL.md)
For systems biology: [tooluniverse-systems-biology](../tooluniverse-systems-biology/SKILL.md)
For protein interactions: [tooluniverse-protein-interactions](../tooluniverse-protein-interactions/SKILL.md)
