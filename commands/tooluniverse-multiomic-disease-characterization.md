# tooluniverse-multiomic-disease-characterization

> Comprehensive multi-omics disease characterization integrating genomics, transcriptomics, proteomics, pathway, and therapeutic layers for systems-level understanding. Produces a detailed multi-omics report with quantitative confidence scoring (0-100), cross-layer gene concordance analysis, biomarker candidates, therapeutic opportunities, and mechanistic hypotheses. Uses 80+ ToolUniverse tools across 8 analysis layers. Use when users ask about disease mechanisms, multi-omics analysis, systems biology of disease, biomarker discovery, or therapeutic target identification from a disease perspective.

# Multi-Omics Disease Characterization Pipeline

Characterize diseases across multiple molecular layers (genomics, transcriptomics, proteomics, pathways) to provide systems-level understanding of disease mechanisms, identify therapeutic opportunities, and discover biomarker candidates.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Disease disambiguation FIRST** - Resolve all identifiers before omics analysis
3. **Layer-by-layer analysis** - Systematically cover all omics layers
4. **Cross-layer integration** - Identify genes/targets appearing in multiple layers
5. **Evidence grading** - Grade all evidence as T1 (human/clinical) to T4 (computational)
6. **Tissue context** - Emphasize disease-relevant tissues/organs
7. **Quantitative scoring** - Multi-Omics Confidence Score (0-100)
8. **Druggable focus** - Prioritize targets with therapeutic potential
9. **Biomarker identification** - Highlight diagnostic/prognostic markers
10. **Mechanistic synthesis** - Generate testable hypotheses
11. **Source references** - Every statement must cite tool/database
12. **Completeness checklist** - Mandatory section showing analysis coverage
13. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use This Skill

Apply when users:
- Ask about disease mechanisms across omics layers
- Need multi-omics characterization of a disease
- Want to understand disease at the systems biology level
- Ask "What pathways/genes/proteins are involved in [disease]?"
- Need biomarker discovery for a disease
- Want to identify druggable targets from disease profiling
- Ask for integrated genomics + transcriptomics + proteomics analysis
- Need cross-layer concordance analysis
- Ask about disease network biology / hub genes

**NOT for** (use other skills instead):
- Single gene/target validation -> Use `tooluniverse-drug-target-validation`
- Drug safety profiling -> Use `tooluniverse-adverse-event-detection`
- General disease overview -> Use `tooluniverse-disease-research`
- Variant interpretation -> Use `tooluniverse-variant-interpretation`
- GWAS-specific analysis -> Use `tooluniverse-gwas-*` skills
- Pathway-only analysis -> Use `tooluniverse-systems-biology`

---

## Input Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| **disease** | Yes | Disease name, OMIM ID, EFO ID, or MONDO ID | `Alzheimer disease`, `MONDO_0004975` |
| **tissue** | No | Tissue/organ of interest | `brain`, `liver`, `blood` |
| **focus_layers** | No | Specific omics layers to emphasize | `genomics`, `transcriptomics`, `pathways` |

---

## Multi-Omics Confidence Score (0-100)

### Score Components

**Data Availability (0-40 points)**:
- Genomics data available (GWAS or rare variants): 10 points
- Transcriptomics data available (DEGs or expression): 10 points
- Protein data available (PPI or expression): 5 points
- Pathway data available (enriched pathways): 10 points
- Clinical/drug data available (approved drugs or trials): 5 points

**Evidence Concordance (0-40 points)**:
- Multi-layer genes (appear in 3+ layers): up to 20 points (2 per gene, max 10 genes)
- Consistent direction (genetics + expression concordant): 10 points
- Pathway-gene concordance (genes found in enriched pathways): 10 points

**Evidence Quality (0-20 points)**:
- Strong genetic evidence (GWAS p < 5e-8): 10 points
- Clinical validation (approved drugs): 10 points

### Score Interpretation

| Score | Tier | Interpretation |
|-------|------|----------------|
| **80-100** | Excellent | Comprehensive multi-omics coverage, high confidence, strong cross-layer concordance |
| **60-79** | Good | Good coverage across most layers, some gaps |
| **40-59** | Moderate | Moderate coverage, limited cross-layer integration |
| **0-39** | Limited | Limited data, single-layer analysis dominates |

### Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Direct human evidence, clinical proof | FDA-approved drug, GWAS hit (p<5e-8), clinical trial result |
| **T2** | [T2] | Experimental evidence | Differential expression (validated), functional screen, mouse KO |
| **T3** | [T3] | Computational/database evidence | PPI network, pathway mapping, expression correlation |
| **T4** | [T4] | Annotation/prediction only | GO annotation, text-mined association, predicted interaction |

---

## Report Template

Create this file structure at the start: `{disease_name}_multiomic_report.md`

```markdown
# Multi-Omics Disease Characterization: {Disease Name}

**Report Generated**: {date}
**Disease Identifiers**: (to be filled)
**Multi-Omics Confidence Score**: (to be calculated)

---

## Executive Summary

(2-3 sentence disease mechanism synthesis - fill after all layers complete)

---

## 1. Disease Definition & Context

### Disease Identifiers
| System | ID | Source |
|--------|-----|--------|

### Description
### Synonyms
### Disease Hierarchy (parents/children)
### Affected Tissues/Organs
### Therapeutic Areas

**Sources**: (tools used)

---

## 2. Genomics Layer

### 2.1 GWAS Associations
| SNP | P-value | Effect | Gene | Study | Source |
|-----|---------|--------|------|-------|--------|

### 2.2 GWAS Studies Summary
| Study ID | Trait | Sample Size | Year | Source |
|----------|-------|-------------|------|--------|

### 2.3 Associated Genes (Genetic Evidence)
| Gene | Ensembl ID | Association Score | Evidence Type | Source |
|------|------------|-------------------|---------------|--------|

### 2.4 Rare Variants (ClinVar)
| Variant | Gene | Clinical Significance | Source |
|---------|------|-----------------------|--------|

### Genomics Layer Summary
- Total GWAS hits:
- Top genes by genetic evidence:
- Genetic architecture:

**Sources**: (tools used)

---

## 3. Transcriptomics Layer

### 3.1 Differential Expression Studies
| Experiment | Condition | Up-regulated | Down-regulated | Source |
|------------|-----------|--------------|----------------|--------|

### 3.2 Expression Atlas Disease Evidence
| Gene | Score | Source |
|------|-------|--------|

### 3.3 Tissue Expression Patterns (GTEx/HPA)
| Gene | Tissue | Expression Level | Source |
|------|--------|-----------------|--------|

### 3.4 Biomarker Candidates (Expression-Based)
| Gene | Tissue Specificity | Fold Change | Evidence | Source |
|------|-------------------|-------------|----------|--------|

### Transcriptomics Layer Summary
- Differential expression datasets:
- Top DEGs:
- Tissue-specific patterns:

**Sources**: (tools used)

---

## 4. Proteomics & Interaction Layer

### 4.1 Protein-Protein Interactions (STRING)
| Protein A | Protein B | Score | Source |
|-----------|-----------|-------|--------|

### 4.2 Hub Genes (Network Centrality)
| Gene | Degree | Betweenness | Role | Source |
|------|--------|-------------|------|--------|

### 4.3 Protein Complexes (IntAct)
| Complex | Members | Function | Source |
|---------|---------|----------|--------|

### 4.4 Tissue-Specific PPI Network
| Gene | Interaction Score | Tissue | Source |
|------|-------------------|--------|--------|

### Proteomics Layer Summary
- Total PPIs:
- Hub genes:
- Network modules:

**Sources**: (tools used)

---

## 5. Pathway & Network Layer

### 5.1 Enriched Pathways (Enrichr/Reactome)
| Pathway | Database | P-value | Genes | Source |
|---------|----------|---------|-------|--------|

### 5.2 Reactome Pathway Details
| Pathway ID | Name | Genes Involved | Source |
|------------|------|----------------|--------|

### 5.3 KEGG Pathways
| Pathway ID | Name | Description | Source |
|------------|------|-------------|--------|

### 5.4 WikiPathways
| Pathway ID | Name | Organism | Source |
|------------|------|----------|--------|

### Pathway Layer Summary
- Top enriched pathways:
- Key pathway nodes:
- Cross-pathway connections:

**Sources**: (tools used)

---

## 6. Gene Ontology & Functional Annotation

### 6.1 Biological Processes
| GO Term | Name | P-value | Genes | Source |
|---------|------|---------|-------|--------|

### 6.2 Molecular Functions
| GO Term | Name | P-value | Genes | Source |
|---------|------|---------|-------|--------|

### 6.3 Cellular Components
| GO Term | Name | P-value | Genes | Source |
|---------|------|---------|-------|--------|

**Sources**: (tools used)

---

## 7. Therapeutic Landscape

### 7.1 Approved Drugs
| Drug | ChEMBL ID | Mechanism | Target | Phase | Source |
|------|-----------|-----------|--------|-------|--------|

### 7.2 Druggable Targets
| Gene | Tractability | Modality | Clinical Precedent | Source |
|------|-------------|----------|-------------------|--------|

### 7.3 Drug Repurposing Candidates
| Drug | Original Indication | Mechanism | Target | Source |
|------|---------------------|-----------|--------|--------|

### 7.4 Clinical Trials
| NCT ID | Title | Phase | Status | Intervention | Source |
|--------|-------|-------|--------|--------------|--------|

### Therapeutic Summary
- Approved drugs:
- Clinical pipeline:
- Novel targets:

**Sources**: (tools used)

---

## 8. Multi-Omics Integration

### 8.1 Cross-Layer Gene Concordance
| Gene | Genomics | Transcriptomics | Proteomics | Pathways | Layers | Evidence Tier |
|------|----------|-----------------|------------|----------|--------|---------------|

### 8.2 Multi-Omics Hub Genes (Top 20)
| Rank | Gene | Layers Found | Key Evidence | Druggable | Source |
|------|------|-------------|--------------|-----------|--------|

### 8.3 Biomarker Candidates
| Biomarker | Type | Evidence Layers | Confidence | Source |
|-----------|------|-----------------|------------|--------|

### 8.4 Mechanistic Hypotheses
1. (Hypothesis with supporting evidence from multiple layers)
2. ...

### 8.5 Systems-Level Insights
- Key disrupted processes:
- Critical pathway nodes:
- Therapeutic intervention points:
- Testable hypotheses:

---

## Multi-Omics Confidence Score

| Component | Points | Max | Details |
|-----------|--------|-----|---------|
| Genomics data | | 10 | |
| Transcriptomics data | | 10 | |
| Protein data | | 5 | |
| Pathway data | | 10 | |
| Clinical data | | 5 | |
| Multi-layer genes | | 20 | |
| Direction concordance | | 10 | |
| Pathway-gene concordance | | 10 | |
| Genetic evidence quality | | 10 | |
| Clinical validation | | 10 | |
| **TOTAL** | | **100** | |

**Score**: XX/100 - [Tier]

---

## Data Availability Checklist

| Omics Layer | Data Available | Tools Used | Findings |
|-------------|---------------|------------|----------|
| Genomics (GWAS) | Yes/No | | |
| Genomics (Rare Variants) | Yes/No | | |
| Transcriptomics (DEGs) | Yes/No | | |
| Transcriptomics (Expression) | Yes/No | | |
| Proteomics (PPI) | Yes/No | | |
| Proteomics (Expression) | Yes/No | | |
| Pathways (Enrichment) | Yes/No | | |
| Pathways (KEGG/Reactome) | Yes/No | | |
| Gene Ontology | Yes/No | | |
| Drugs/Therapeutics | Yes/No | | |
| Clinical Trials | Yes/No | | |
| Literature | Yes/No | | |

---

## Completeness Checklist

- [ ] Disease disambiguation complete (IDs resolved)
- [ ] Genomics layer analyzed (GWAS + variants)
- [ ] Transcriptomics layer analyzed (DEGs + expression)
- [ ] Proteomics layer analyzed (PPI + interactions)
- [ ] Pathway layer analyzed (enrichment + mapping)
- [ ] Gene Ontology analyzed (BP + MF + CC)
- [ ] Therapeutic landscape analyzed (drugs + targets + trials)
- [ ] Cross-layer integration complete (concordance analysis)
- [ ] Multi-Omics Confidence Score calculated
- [ ] Biomarker candidates identified
- [ ] Hub genes identified
- [ ] Mechanistic hypotheses generated
- [ ] Executive summary written
- [ ] All sections have source citations

---

## References

### Data Sources Used
| # | Tool | Parameters | Section | Items Retrieved |
|---|------|------------|---------|-----------------|

### Database Versions
- OpenTargets: (current)
- GWAS Catalog: (current)
- STRING: (current)
- Reactome: (current)
```

---

## Phase 0: Disease Disambiguation (ALWAYS FIRST)

**Objective**: Resolve disease to standard identifiers for all downstream queries.

### Tools Used

**OpenTargets_get_disease_id_description_by_name** (primary):
- **Input**: `diseaseName` (string) - Disease name
- **Output**: `{data: {search: {hits: [{id, name, description}]}}}`
- **Use**: Get MONDO/EFO IDs and description
- **CRITICAL**: Disease IDs from OpenTargets use underscore format (e.g., `MONDO_0004975`), NOT colon format

**OSL_get_efo_id_by_disease_name** (secondary):
- **Input**: `disease` (string) - Disease name
- **Output**: `{efo_id, name}`
- **Use**: Get EFO/MONDO ID

**OpenTargets_get_disease_description_by_efoId**:
- **Input**: `efoId` (string) - Disease ID (e.g., `MONDO_0004975`)
- **Output**: `{data: {disease: {id, name, description, dbXRefs}}}`
- **Use**: Get full description, cross-references (OMIM, UMLS, DOID, etc.)

**OpenTargets_get_disease_synonyms_by_efoId**:
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, synonyms: [{relation, terms}]}}}`

**OpenTargets_get_disease_therapeutic_areas_by_efoId**:
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, therapeuticAreas: [{id, name}]}}}`

**OpenTargets_get_disease_ancestors_parents_by_efoId**:
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, ancestors: [{id, name}]}}}`

**OpenTargets_get_disease_descendants_children_by_efoId**:
- **Input**: `efoId` (string)
- **Output**: `{data: {disease: {id, name, descendants: [{id, name}]}}}`

**OpenTargets_map_any_disease_id_to_all_other_ids**:
- **Input**: `inputId` (string) - Any known disease ID (e.g., `OMIM:104300`, `UMLS:C0002395`)
- **Output**: `{data: {disease: {id, name, dbXRefs: [str], ...}}}`
- **Use**: Cross-map between OMIM, UMLS, ICD10, DOID, etc.

### Workflow

1. Search by disease name to get primary ID (OpenTargets)
2. Get full description and cross-references
3. Get synonyms for search term expansion
4. Get therapeutic areas for context
5. Get disease hierarchy (parents/children)
6. If user provided OMIM/other ID, map to MONDO/EFO first

### Collision-Aware Search

When disease name returns multiple hits:
- Check if user's input matches any hit exactly
- If ambiguous, present top 3-5 options and ask user to select
- Always prefer the most specific disease (not parent categories)
- For cancer, prefer the specific tumor type over generic "cancer"

### Key Disease IDs to Track

After disambiguation, store these for all downstream queries:
- `efo_id` - Primary ID for OpenTargets queries (e.g., `MONDO_0004975`)
- `disease_name` - Canonical name (e.g., `Alzheimer disease`)
- `synonyms` - For literature search expansion
- `therapeutic_areas` - For context
- `dbXRefs` - Cross-references (OMIM, UMLS, DOID, etc.)

---

## Phase 1: Genomics Layer

**Objective**: Identify genetic variants, GWAS associations, and genetically implicated genes.

### Tools Used

**OpenTargets_get_associated_targets_by_disease_efoId** (primary):
- **Input**: `efoId` (string) - Disease EFO/MONDO ID
- **Output**: `{data: {disease: {id, name, associatedTargets: {count, rows: [{target: {id, approvedSymbol}, score}]}}}}`
- **Use**: Get ALL disease-associated genes ranked by overall evidence score
- **NOTE**: Returns top 25 by default. For comprehensive analysis, note the total `count`

**OpenTargets_get_evidence_by_datasource**:
- **Input**: `efoId` (string), `ensemblId` (string), optional `datasourceIds` (array), `size` (int, default 50)
- **Output**: `{data: {disease: {evidences: {count, rows: [{...evidence details}]}}}}`
- **Use**: Get specific evidence types. Key datasourceIds for genomics:
  - `['ot_genetics_portal']` - GWAS/genetics
  - `['gene2phenotype', 'genomics_england', 'orphanet']` - Rare variants
  - `['eva']` - ClinVar variants

**gwas_search_associations** (GWAS Catalog):
- **Input**: `disease_trait` (string), `size` (int, default 20)
- **Output**: `{data: [{association_id, p_value, or_per_copy_num, or_value, beta, risk_frequency, efo_traits: [{...}], ...}], metadata: {pagination: {totalElements}}}`
- **Use**: Get genome-wide significant associations
- **NOTE**: Use disease name (e.g., "Alzheimer"), not ID. Returns paginated results

**gwas_get_studies_for_trait**:
- **Input**: `disease_trait` (string), `size` (int)
- **Output**: `{data: [...studies], metadata: {pagination}}`
- **NOTE**: May return empty if trait name does not match exactly. Try synonyms

**gwas_get_variants_for_trait**:
- **Input**: `disease_trait` (string), `size` (int)
- **Output**: `{data: [...variants], metadata: {pagination}}`

**GWAS_search_associations_by_gene**:
- **Input**: `gene_name` (string)
- **Output**: Associations for a specific gene

**OpenTargets_search_gwas_studies_by_disease**:
- **Input**: `diseaseIds` (array of strings), `enableIndirect` (bool, default true), `size` (int, default 10)
- **Output**: `{data: {studies: {count, rows: [{id, studyType, traitFromSource, publicationFirstAuthor, publicationDate, pubmedId, nSamples, nCases, nControls, ...}]}}}`
- **Use**: Get GWAS studies from OpenTargets genetics portal

**clinvar_search_variants**:
- **Input**: `condition` (string) or `gene` (string), optional `max_results` (int)
- **Output**: List of ClinVar variants with clinical significance
- **Use**: Rare variant / monogenic disease evidence

### Workflow

1. Get associated genes from OpenTargets (overall scores)
2. For top 10-15 genes, get genetic evidence specifically via `OpenTargets_get_evidence_by_datasource`
3. Search GWAS Catalog for associations
4. Search OpenTargets GWAS studies
5. Search ClinVar for rare variants
6. For top GWAS genes, check `GWAS_search_associations_by_gene`

### Gene Tracking

Maintain a dictionary of genes found in genomics layer:
```python
genomics_genes = {
    'PSEN1': {'score': 0.87, 'evidence': 'genetic', 'ensembl_id': 'ENSG00000080815', 'layer': 'genomics'},
    'APP': {'score': 0.82, 'evidence': 'genetic', 'ensembl_id': 'ENSG00000142192', 'layer': 'genomics'},
    # ...
}
```

---

## Phase 2: Transcriptomics Layer

**Objective**: Identify differentially expressed genes, tissue-specific expression, and expression-based biomarkers.

### Tools Used

**ExpressionAtlas_search_differential**:
- **Input**: optional `gene` (string), `condition` (string), `species` (string, default 'homo sapiens')
- **Output**: Differential expression studies and results
- **Use**: Find studies where genes are differentially expressed in disease

**ExpressionAtlas_search_experiments**:
- **Input**: optional `gene` (string), `condition` (string), `species` (string)
- **Output**: Expression experiments relevant to condition
- **Use**: Find all Expression Atlas experiments for the disease

**expression_atlas_disease_target_score**:
- **Input**: `efoId` (string), `pageSize` (int, required)
- **Output**: Genes scored by expression evidence for the disease
- **Use**: Get expression-based disease-gene association scores

**europepmc_disease_target_score**:
- **Input**: `efoId` (string), `pageSize` (int, required)
- **Output**: Genes scored by literature evidence for the disease
- **Use**: Complement expression evidence with literature-mined associations

**HPA_get_rna_expression_by_source** (Human Protein Atlas):
- **Input**: `gene_name` (string), `source_type` (string: 'tissue', 'blood', 'brain'), `source_name` (string: e.g., 'brain', 'liver')
- **Output**: `{status, data: {gene_name, source_type, source_name, expression_value, expression_level, expression_unit}}`
- **NOTE**: ALL 3 params required. `source_type` options: 'tissue', 'blood', 'brain', 'cell_line', 'single_cell'

**HPA_get_rna_expression_in_specific_tissues**:
- **Input**: `gene_name` (string), `tissues` (array of strings)
- **Output**: Expression across specified tissues

**HPA_get_cancer_prognostics_by_gene**:
- **Input**: `gene_name` (string)
- **Output**: Cancer prognostic data (if cancer context)

**HPA_get_subcellular_location**:
- **Input**: `gene_name` (string)
- **Output**: Subcellular localization data

**HPA_search_genes_by_query**:
- **Input**: `query` (string)
- **Output**: Matching genes in HPA

### Workflow

1. Search Expression Atlas for differential expression studies
2. Get expression-based disease scores
3. Get literature-based disease scores (EuropePMC)
4. For top 10-15 genes from genomics layer, check tissue expression via HPA
5. Check disease-relevant tissue expression patterns
6. For cancer: check prognostic biomarkers

### Gene Tracking

Add transcriptomics genes to tracking:
```python
transcriptomics_genes = {
    'APOE': {'expression_score': 0.75, 'tissues': ['brain'], 'evidence': 'differential_expression', 'layer': 'transcriptomics'},
    # ...
}
```

---

## Phase 3: Proteomics & Interaction Layer

**Objective**: Map protein-protein interactions, identify hub genes, and characterize interaction networks.

### Tools Used

**STRING_get_interaction_partners** (primary PPI):
- **Input**: `protein_ids` (array of strings - gene names work), `species` (int, default 9606), `confidence_score` (float, default 0.4), `limit` (int, default 20)
- **Output**: `{status: 'success', data: [{stringId_A, stringId_B, preferredName_A, preferredName_B, ncbiTaxonId, score, nscore, fscore, pscore, ascore, escore, dscore, tscore}]}`
- **Use**: Get interaction partners for disease genes
- **NOTE**: `protein_ids` is an array, NOT string. Gene symbols like `['APOE']` work

**STRING_get_network**:
- **Input**: `protein_ids` (array), `species` (int), `confidence_score` (float)
- **Output**: Network of interactions between input proteins
- **Use**: Build disease-specific PPI network

**STRING_functional_enrichment**:
- **Input**: `protein_ids` (array), `species` (int)
- **Output**: Functional enrichment results (GO, KEGG, etc.)
- **Use**: Functional characterization of disease gene set

**STRING_ppi_enrichment**:
- **Input**: `protein_ids` (array), `species` (int)
- **Output**: Statistical test for PPI enrichment (more interactions than expected)
- **Use**: Test if disease genes form a connected module

**intact_get_interactions**:
- **Input**: `identifier` (string - UniProt ID or gene name)
- **Output**: Molecular interaction data from IntAct

**intact_search_interactions**:
- **Input**: `query` (string), `first` (int, default 0), `max` (int, default 25)
- **Output**: Search results for interactions

**HPA_get_protein_interactions_by_gene**:
- **Input**: `gene_name` (string)
- **Output**: `{gene, interactions, interactor_count, interactors: [...]}`

**humanbase_ppi_analysis**:
- **Input**: `gene_list` (array), `tissue` (string), `max_node` (int), `interaction` (string), `string_mode` (bool)
- **Output**: Tissue-specific PPI network
- **NOTE**: ALL params required. `interaction` options: 'coexpression', 'interaction', 'coexpression_and_interaction'. `string_mode`: true/false

### Workflow

1. Take top 15-20 genes from genomics + transcriptomics layers
2. Query STRING for interaction partners of each gene
3. Build composite PPI network using STRING_get_network
4. Test PPI enrichment (are genes more connected than random?)
5. Get functional enrichment from STRING
6. For disease-relevant tissue, get tissue-specific network (HumanBase)
7. Identify hub genes (highest degree centrality)
8. Check IntAct for experimentally validated interactions

### Hub Gene Analysis

Calculate network centrality metrics:
- **Degree**: Number of interaction partners
- **Betweenness**: Number of shortest paths through node
- **Hub score**: Genes with degree > mean + 1 SD are hubs

---

## Phase 4: Pathway & Network Layer

**Objective**: Identify enriched biological pathways and cross-pathway connections.

### Tools Used

**enrichr_gene_enrichment_analysis** (primary enrichment):
- **Input**: `gene_list` (array of gene symbols, min 2), `libs` (array of library names)
- **Output**: `{status: 'success', data: '{...JSON string with enrichment results...}'}`
- **Key libraries**: `['KEGG_2021_Human']`, `['Reactome_2022']`, `['WikiPathway_2023_Human']`, `['GO_Biological_Process_2023']`, `['GO_Molecular_Function_2023']`, `['GO_Cellular_Component_2023']`
- **NOTE**: `data` field is a JSON string, needs parsing. Contains `connected_paths` and per-library results
- **NOTE**: `libs` is REQUIRED as array

**ReactomeAnalysis_pathway_enrichment**:
- **Input**: `identifiers` (string - space-separated gene list), optional `page_size` (int, default 20), `include_disease` (bool), `projection` (bool)
- **Output**: `{data: {token, analysis_type, pathways_found, pathways: [{pathway_id, name, species, is_disease, is_lowest_level, entities_found, entities_total, entities_ratio, p_value, fdr, reactions_found, reactions_total}]}}`
- **Use**: Reactome-specific pathway enrichment with statistical testing

**Reactome_map_uniprot_to_pathways**:
- **Input**: `id` (string - UniProt accession)
- **Output**: List of Reactome pathways containing this protein
- **Use**: Map individual proteins to pathways

**Reactome_get_pathway**:
- **Input**: `stId` (string - Reactome stable ID, e.g., 'R-HSA-73817')
- **Output**: Pathway details

**Reactome_get_pathway_reactions**:
- **Input**: `stId` (string)
- **Output**: Reactions within pathway

**kegg_search_pathway**:
- **Input**: `keyword` (string)
- **Output**: Array of KEGG pathway matches

**kegg_get_pathway_info**:
- **Input**: `pathway_id` (string, e.g., 'hsa04930')
- **Output**: Detailed pathway information

**WikiPathways_search**:
- **Input**: `query` (string), optional `organism` (string, e.g., 'Homo sapiens')
- **Output**: Matching community-curated pathways

### Workflow

1. Collect all genes from genomics + transcriptomics layers (top 20-30)
2. Run Enrichr enrichment for KEGG, Reactome, WikiPathways
3. Run ReactomeAnalysis for more detailed Reactome enrichment with p-values
4. Search KEGG for disease-specific pathways
5. Search WikiPathways for disease pathways
6. For top Reactome pathways, get detailed reactions
7. Identify cross-pathway connections (genes in multiple pathways)

---

## Phase 5: Gene Ontology & Functional Annotation

**Objective**: Characterize biological processes, molecular functions, and cellular components.

### Tools Used

**enrichr_gene_enrichment_analysis** (GO enrichment):
- Use with `libs=['GO_Biological_Process_2023']` for BP
- Use with `libs=['GO_Molecular_Function_2023']` for MF
- Use with `libs=['GO_Cellular_Component_2023']` for CC

**GO_get_annotations_for_gene**:
- **Input**: `gene_id` (string - gene symbol or UniProt ID)
- **Output**: List of GO annotations with terms, aspects, evidence codes

**GO_search_terms**:
- **Input**: `query` (string)
- **Output**: Matching GO terms

**QuickGO_annotations_by_gene**:
- **Input**: `gene_product_id` (string - UniProt accession, e.g., 'UniProtKB:P02649'), optional `aspect` (string: 'biological_process', 'molecular_function', 'cellular_component'), `taxon_id` (int: 9606), `limit` (int: 25)
- **Output**: GO annotations with evidence codes

**OpenTargets_get_target_gene_ontology_by_ensemblID**:
- **Input**: `ensemblId` (string)
- **Output**: GO terms associated with target

### Workflow

1. Run Enrichr GO enrichment for all 3 aspects using combined gene list
2. For top 5 genes, get detailed GO annotations from QuickGO
3. For top genes, get OpenTargets GO terms
4. Summarize key biological processes, molecular functions, cellular components

---

## Phase 6: Therapeutic Landscape

**Objective**: Map approved drugs, druggable targets, repurposing opportunities, and clinical trials.

### Tools Used

**OpenTargets_get_associated_drugs_by_disease_efoId** (primary):
- **Input**: `efoId` (string), `size` (int, REQUIRED - use 100)
- **Output**: `{data: {disease: {knownDrugs: {count, rows: [{drug: {id, name, tradeNames, maximumClinicalTrialPhase, isApproved, hasBeenWithdrawn}, phase, mechanismOfAction, target: {id, approvedSymbol}, disease: {id, name}, urls: [{url, name}]}]}}}}`
- **Use**: All drugs associated with disease (approved + investigational)

**OpenTargets_get_target_tractability_by_ensemblID**:
- **Input**: `ensemblId` (string)
- **Output**: Tractability assessment (small molecule, antibody, PROTAC, etc.)

**OpenTargets_get_associated_drugs_by_target_ensemblID**:
- **Input**: `ensemblId` (string), `size` (int, REQUIRED)
- **Output**: Drugs targeting this gene/protein

**search_clinical_trials**:
- **Input**: `query_term` (string, REQUIRED), optional `condition` (string), `intervention` (string), `pageSize` (int, default 10)
- **Output**: Clinical trial results
- **NOTE**: `query_term` is REQUIRED even if `condition` is provided

**OpenTargets_get_drug_mechanisms_of_action_by_chemblId**:
- **Input**: `chemblId` (string)
- **Output**: Mechanism of action details

### Workflow

1. Get all drugs for disease from OpenTargets
2. For top disease-associated genes, check tractability
3. For top genes with no approved drugs, identify repurposing candidates
4. Search clinical trials for disease
5. For top approved drugs, get mechanism of action

### Drug Tracking

```python
drug_targets = {
    'PSEN1': {'drugs': ['Semagacestat'], 'tractability': 'small_molecule', 'clinical_phase': 3},
    'ACHE': {'drugs': ['Donepezil', 'Galantamine'], 'tractability': 'small_molecule', 'clinical_phase': 4},
    # ...
}
```

---

## Phase 7: Multi-Omics Integration

**Objective**: Integrate findings across all layers to identify cross-layer genes, calculate concordance, and generate mechanistic hypotheses.

### Cross-Layer Gene Concordance Analysis

This is the core integrative step. For each gene found in the analysis:

1. **Count layers**: In how many omics layers does this gene appear?
   - Genomics (GWAS, rare variants, genetic association)
   - Transcriptomics (DEGs, expression score)
   - Proteomics (PPI hub, protein expression)
   - Pathways (enriched pathway member)
   - Therapeutics (drug target)

2. **Score genes**: Genes appearing in 3+ layers are "multi-omics hub genes"

3. **Direction concordance**: Do genetics and expression agree?
   - Risk allele + upregulated = concordant gain-of-function
   - Risk allele + downregulated = concordant loss-of-function
   - Discordant = needs investigation

### Biomarker Identification

For each multi-omics hub gene, assess biomarker potential:
- **Diagnostic**: Gene expression distinguishes disease vs healthy
- **Prognostic**: Expression/variant predicts outcome (cancer prognostics from HPA)
- **Predictive**: Variant/expression predicts treatment response (pharmacogenomics)
- **Evidence level**: Number of supporting omics layers

### Mechanistic Hypothesis Generation

From the integrated data:
1. Identify the most supported biological processes (GO + pathways)
2. Map causal chain: genetic variant -> gene expression -> protein function -> pathway disruption -> disease
3. Identify intervention points (druggable nodes in the causal chain)
4. Generate testable hypotheses

### Confidence Score Calculation

Calculate the Multi-Omics Confidence Score (0-100) based on:
- Data availability across layers
- Cross-layer concordance
- Evidence quality
- Clinical validation

---

## Phase 8: Report Finalization

### Executive Summary

Write a 2-3 sentence synthesis covering:
- Disease mechanism in systems terms
- Key genes/pathways identified
- Therapeutic opportunities

### Final Report Quality Checklist

Before presenting to user, verify:
- [ ] All 8 sections have content (or marked as "No data available")
- [ ] Every data point has a source citation
- [ ] Executive summary reflects key findings
- [ ] Multi-Omics Confidence Score calculated
- [ ] Top 20 genes ranked by multi-omics evidence
- [ ] Top 10 enriched pathways listed
- [ ] Biomarker candidates identified
- [ ] Cross-layer concordance table complete
- [ ] Therapeutic opportunities summarized
- [ ] Mechanistic hypotheses generated
- [ ] Data Availability Checklist complete
- [ ] Completeness Checklist complete
- [ ] References section lists all tools used

---

## Tool Parameter Quick Reference

| Tool | Key Parameters | Notes |
|------|---------------|-------|
| `OpenTargets_get_disease_id_description_by_name` | `diseaseName` | Primary disambiguation |
| `OSL_get_efo_id_by_disease_name` | `disease` | Secondary disambiguation |
| `OpenTargets_get_associated_targets_by_disease_efoId` | `efoId` | Returns top 25 genes |
| `OpenTargets_get_evidence_by_datasource` | `efoId`, `ensemblId`, `datasourceIds[]`, `size` | Per-gene evidence |
| `OpenTargets_search_gwas_studies_by_disease` | `diseaseIds[]`, `size` | GWAS studies |
| `gwas_search_associations` | `disease_trait`, `size` | GWAS Catalog |
| `clinvar_search_variants` | `condition` or `gene`, `max_results` | Rare variants |
| `ExpressionAtlas_search_differential` | `condition`, `species` | DEGs |
| `expression_atlas_disease_target_score` | `efoId`, `pageSize` (REQUIRED) | Expression scores |
| `europepmc_disease_target_score` | `efoId`, `pageSize` (REQUIRED) | Literature scores |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` (ALL REQUIRED) | Tissue expression |
| `STRING_get_interaction_partners` | `protein_ids[]`, `species` (9606), `limit` | PPI partners |
| `STRING_get_network` | `protein_ids[]`, `species` | PPI network |
| `STRING_functional_enrichment` | `protein_ids[]`, `species` | Functional enrichment |
| `STRING_ppi_enrichment` | `protein_ids[]`, `species` | Network significance |
| `intact_search_interactions` | `query`, `max` | Experimental PPIs |
| `humanbase_ppi_analysis` | `gene_list[]`, `tissue`, `max_node`, `interaction`, `string_mode` (ALL REQ) | Tissue PPI |
| `enrichr_gene_enrichment_analysis` | `gene_list[]`, `libs[]` (BOTH REQUIRED) | Pathway/GO enrichment |
| `ReactomeAnalysis_pathway_enrichment` | `identifiers` (space-sep string) | Reactome enrichment |
| `Reactome_map_uniprot_to_pathways` | `id` (UniProt accession) | Protein-pathway mapping |
| `kegg_search_pathway` | `keyword` | KEGG pathway search |
| `WikiPathways_search` | `query`, `organism` | WikiPathways search |
| `GO_get_annotations_for_gene` | `gene_id` | GO annotations |
| `QuickGO_annotations_by_gene` | `gene_product_id` (e.g., 'UniProtKB:P02649') | Detailed GO |
| `OpenTargets_get_associated_drugs_by_disease_efoId` | `efoId`, `size` (REQUIRED) | Disease drugs |
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensemblId` | Druggability |
| `search_clinical_trials` | `query_term` (REQUIRED), `condition`, `pageSize` | Clinical trials |
| `PubMed_search_articles` | `query`, `limit` | Literature |
| `ensembl_lookup_gene` | `gene_id`, `species` ('homo_sapiens' REQUIRED) | Gene lookup |
| `MyGene_query_genes` | `query`, `species`, `fields`, `size` | Gene info |
| `OpenTargets_get_similar_entities_by_disease_efoId` | `efoId`, `threshold`, `size` (ALL REQUIRED) | Similar diseases |

---

## Response Format Notes (Verified)

### OpenTargets Associated Targets
```json
{
  "data": {
    "disease": {
      "id": "MONDO_0004975",
      "name": "Alzheimer disease",
      "associatedTargets": {
        "count": 2456,
        "rows": [
          {
            "target": {"id": "ENSG00000080815", "approvedSymbol": "PSEN1"},
            "score": 0.87
          }
        ]
      }
    }
  }
}
```

### GWAS Catalog Associations
```json
{
  "data": [
    {
      "association_id": 216440893,
      "p_value": 2e-09,
      "or_per_copy_num": 0.94,
      "or_value": "0.94",
      "efo_traits": [{"..."}],
      "risk_frequency": "NR"
    }
  ],
  "metadata": {"pagination": {"totalElements": 1061816}}
}
```

### STRING Interactions
```json
{
  "status": "success",
  "data": [
    {
      "stringId_A": "9606.ENSP00000252486",
      "stringId_B": "9606.ENSP00000466775",
      "preferredName_A": "APOE",
      "preferredName_B": "APOC2",
      "score": 0.999
    }
  ]
}
```

### Reactome Enrichment
```json
{
  "data": {
    "token": "...",
    "pathways_found": 154,
    "pathways": [
      {
        "pathway_id": "R-HSA-1251985",
        "name": "Nuclear signaling by ERBB4",
        "species": "Homo sapiens",
        "is_disease": false,
        "is_lowest_level": true,
        "entities_found": 3,
        "entities_total": 47,
        "entities_ratio": 0.00291,
        "p_value": 4.0e-06,
        "fdr": 0.00068,
        "reactions_found": 3,
        "reactions_total": 34
      }
    ]
  }
}
```

### HPA RNA Expression
```json
{
  "status": "success",
  "data": {
    "gene_name": "APOE",
    "source_type": "tissue",
    "source_name": "brain",
    "expression_value": "2714.9",
    "expression_level": "very high",
    "expression_unit": "nTPM"
  }
}
```

### Enrichr Results
```json
{
  "status": "success",
  "data": "{\"connected_paths\": {\"Path: ...\": \"Total Weight: ...\"}}"
}
```
**NOTE**: The `data` field is a JSON string that needs parsing.

---

## Common Use Patterns

### 1. Comprehensive Disease Profiling
```
User: "Characterize Alzheimer's disease across omics layers"
-> Run all 8 phases
-> Produce full multi-omics report
```

### 2. Therapeutic Target Discovery
```
User: "What are druggable targets for rheumatoid arthritis?"
-> Emphasize Phase 1 (genomics), Phase 6 (therapeutics), Phase 7 (integration)
-> Focus on tractability and clinical precedent
```

### 3. Biomarker Identification
```
User: "Find diagnostic biomarkers for pancreatic cancer"
-> Emphasize Phase 2 (transcriptomics), Phase 3 (proteomics), Phase 7 (biomarkers)
-> Focus on tissue-specific expression and diagnostic potential
```

### 4. Mechanism Elucidation
```
User: "What pathways are dysregulated in Crohn's disease?"
-> Emphasize Phase 4 (pathways), Phase 5 (GO), Phase 7 (mechanistic hypotheses)
-> Focus on pathway enrichment and cross-pathway connections
```

### 5. Drug Repurposing
```
User: "What existing drugs could be repurposed for ALS?"
-> Emphasize Phase 1 (genetics), Phase 6 (therapeutic landscape), Phase 7 (repurposing)
-> Focus on drugs targeting disease-associated genes
```

### 6. Systems Biology
```
User: "What are the hub genes and key pathways in type 2 diabetes?"
-> Emphasize Phase 3 (PPI network), Phase 4 (pathways), Phase 7 (network analysis)
-> Focus on hub genes and network modules
```

---

## Edge Case Handling

### Rare Diseases (limited data)
- Genomics layer may dominate (single gene)
- Limited GWAS data (monogenic)
- Focus on ClinVar variants, pathway consequences
- Confidence score will be lower (less cross-layer data)

### Common Diseases (overwhelming data)
- Thousands of GWAS associations
- Prioritize by effect size and significance
- Focus on top 20-30 genes for downstream analysis
- Use strict significance thresholds (p < 5e-8)

### Cancer
- Include somatic mutations (if CIViC/cBioPortal available)
- Check cancer prognostics via HPA
- Include tumor-specific expression patterns
- Clinical trial landscape may be extensive

### Monogenic Diseases
- Single gene dominates
- ClinVar/OMIM evidence is primary
- Pathway analysis reveals downstream effects
- Therapeutic landscape may be limited (gene therapy, enzyme replacement)

### Polygenic Diseases
- Many weak genetic signals
- GWAS provides the gene list
- Pathway enrichment reveals convergent biology
- Network analysis identifies hub genes

### Tissue Ambiguity
- Diseases affecting multiple tissues
- Query HPA for all relevant tissues
- Compare tissue-specific expression patterns
- Use tissue context from disease ontology

---

## Fallback Strategies

### If disease name not found
1. Try synonyms
2. Try broader disease category
3. Try OMIM/UMLS ID mapping
4. Report disambiguation failure and ask user

### If no GWAS data
1. Check ClinVar for rare variants
2. Use OpenTargets genetic evidence
3. Note in report as "Limited genetic data"
4. Adjust confidence score accordingly

### If no expression data
1. Try different disease name/synonym
2. Check HPA for individual gene expression
3. Use OpenTargets expression evidence
4. Note as "Limited transcriptomics data"

### If no pathway enrichment
1. Reduce gene list stringency
2. Try different pathway databases
3. Map individual genes to pathways via Reactome
4. Note as "No significant pathway enrichment"

### If no drugs found
1. Check if disease is rare/orphan
2. Look for drugs targeting individual genes
3. Check clinical trials for investigational therapies
4. Note as "No approved drugs - novel therapeutic opportunity"
