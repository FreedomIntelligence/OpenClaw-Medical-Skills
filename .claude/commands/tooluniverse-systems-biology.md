# tooluniverse-systems-biology

> Comprehensive systems biology and pathway analysis using multiple pathway databases (Reactome, KEGG, WikiPathways, Pathway Commons, BioModels). Performs pathway enrichment, protein-pathway mapping, keyword searches, and systems-level analysis. Use when analyzing gene sets, exploring biological pathways, or investigating systems-level biology.

# Systems Biology & Pathway Analysis

Comprehensive pathway and systems biology analysis integrating multiple curated databases to provide multi-dimensional view of biological systems, pathway enrichment, and protein-pathway relationships.

## When to Use This Skill

**Triggers**:
- "Analyze pathways for this gene list"
- "What pathways is [protein] involved in?"
- "Find pathways related to [keyword/process]"
- "Perform pathway enrichment analysis"
- "Map proteins to biological pathways"
- "Find computational models for [process]"
- "Systems biology analysis of [genes/proteins]"

**Use Cases**:
1. **Gene Set Analysis**: Identify enriched pathways from RNA-seq, proteomics, or screen results
2. **Protein Function**: Discover pathways and processes a protein participates in
3. **Pathway Discovery**: Find pathways related to diseases, processes, or phenotypes
4. **Systems Integration**: Connect genes → pathways → processes → diseases
5. **Model Discovery**: Find computational systems biology models (SBML)
6. **Cross-Database Validation**: Compare pathway annotations across multiple sources

## Core Databases Integrated

| Database | Coverage | Strengths |
|----------|----------|-----------|
| **Reactome** | Human-curated reactions & pathways | Detailed mechanistic pathways with reactions |
| **KEGG** | Reference pathways across organisms | Metabolic maps, disease pathways, drug targets |
| **WikiPathways** | Community-curated pathways | Emerging processes, collaborative updates |
| **Pathway Commons** | Integrated meta-database | Aggregates multiple sources (Reactome, KEGG, etc.) |
| **BioModels** | Computational SBML models | Mathematical/dynamic systems biology models |
| **Enrichr** | Statistical enrichment | Pathway over-representation analysis |

## Workflow Overview

```
Input → Phase 1: Enrichment → Phase 2: Protein Mapping → Phase 3: Keyword Search → Phase 4: Top Pathways → Report
```

---

## Phase 1: Pathway Enrichment Analysis

**When**: Gene list provided (from experiments, screens, differentially expressed genes)

**Objective**: Identify biological pathways statistically over-represented in gene list

### Tools Used

**enrichr_gene_enrichment_analysis**:
- **Input**:
  - `gene_list`: Array of gene symbols (e.g., ["TP53", "BRCA1", "EGFR"])
  - `library`: Pathway database (e.g., "KEGG_2021_Human", "Reactome_2022")
- **Output**: Array of enriched pathways with p-values, adjusted p-values, genes
- **Use**: Statistical over-representation analysis

### Workflow

1. Submit gene list to Enrichr
2. Query KEGG pathway library for human
3. Get enriched pathways sorted by significance
4. Extract:
   - Pathway names and IDs
   - P-values (raw and adjusted)
   - Genes from input list in each pathway
   - Enrichment scores

### Decision Logic

- **Significance threshold**: Adjusted p-value < 0.05 (default)
- **Minimum genes**: At least 2 genes from input list in pathway
- **Report top pathways**: Show 10-20 most significant
- **Empty results**: If no enrichment → note "no significant pathways" (don't fail)

---

## Phase 2: Protein-Pathway Mapping

**When**: Protein UniProt ID provided

**Objective**: Map protein to all known pathways it participates in

### Tools Used

**Reactome_map_uniprot_to_pathways**:
- **Input**:
  - `id`: UniProt accession (e.g., "P53350")
- **Output**: Array of Reactome pathways containing this protein
- **Note**: Parameter is `id` (not `uniprot_id`)

**Reactome_get_pathway_reactions**:
- **Input**:
  - `stId`: Reactome pathway stable ID (e.g., "R-HSA-73817")
- **Output**: Array of reactions and subpathways
- **Use**: Get mechanistic details of pathways

### Workflow

1. Map UniProt ID to Reactome pathways
2. Get all pathways this protein appears in
3. For top pathway (or user-specified):
   - Retrieve detailed reactions and subpathways
   - Extract event names, types (Reaction vs Pathway)
   - Note disease associations if present

### Decision Logic

- **Multiple pathways**: Report all pathways, prioritize by hierarchical level
- **Top pathway details**: Get detailed reactions for 1-3 most relevant
- **Versioned IDs**: Reactome uses unversioned IDs - strip version if present
- **Empty results**: Check if protein ID valid; suggest alternative databases if Reactome empty

---

## Phase 3: Keyword-Based Pathway Search

**When**: User provides keyword or biological process name

**Objective**: Search multiple pathway databases to find relevant pathways

### Tools Used

#### KEGG Search
**kegg_search_pathway**:
- **Input**: `keyword` (e.g., "diabetes", "apoptosis")
- **Output**: Array of pathway IDs and descriptions
- **Coverage**: Reference pathways, metabolism, diseases

**kegg_get_pathway_info**:
- **Input**: `pathway_id` (e.g., "hsa04930")
- **Output**: Pathway details, genes, compounds
- **Use**: Get detailed information for specific pathway

#### WikiPathways Search
**WikiPathways_search**:
- **Input**:
  - `query`: Keyword or gene symbol
  - `organism`: Species filter (e.g., "Homo sapiens")
- **Output**: Array of pathway matches with IDs, names, URLs
- **Coverage**: Community-curated, includes emerging pathways

#### Pathway Commons Search
**pc_search_pathways**:
- **Input**:
  - `action`: "search_pathways"
  - `keyword`: Search term
  - `datasource`: Optional filter (e.g., "reactome", "kegg")
  - `limit`: Max results (default: 10)
- **Output**: Total hits and array of pathways with source attribution
- **Coverage**: Meta-database aggregating multiple sources

#### BioModels Search
**biomodels_search**:
- **Input**:
  - `query`: Keyword for computational models
  - `limit`: Max results
- **Output**: Array of SBML models with IDs, names, publications
- **Coverage**: Mathematical/computational systems biology models

### Workflow

1. Search KEGG pathways by keyword
2. Search WikiPathways with organism filter
3. Search Pathway Commons (aggregates multiple sources)
4. Search BioModels for computational models
5. Compile results from all sources
6. Note overlaps and source-specific pathways

### Decision Logic

- **Parallel queries**: Search all databases simultaneously (independent)
- **Empty from one source**: Continue with other sources (common for specialized keywords)
- **Result consolidation**: Group by pathway concept, note which databases contain each
- **Model availability**: BioModels may be empty for many processes - this is normal

---

## Phase 4: Top-Level Pathway Catalog

**When**: Always included to provide context

**Objective**: Show major biological systems/pathways for organism

### Tools Used

**Reactome_list_top_pathways**:
- **Input**: `species` (e.g., "Homo sapiens")
- **Output**: Array of top-level pathway categories
- **Use**: Provides hierarchical pathway organization

### Workflow

1. Retrieve top-level pathways for specified organism
2. Display pathway categories (metabolism, signaling, disease, etc.)
3. Serve as reference for pathway hierarchy

### Decision Logic

- **Always show**: Provides context even if other phases empty
- **Organism-specific**: Filter by species of interest
- **Hierarchical view**: These are parent pathways with many subpathways

---

## Output Structure

### Report Format

**Progressive Markdown Report**:
- Create report file first
- Add sections progressively
- Each section self-contained (handles empty gracefully)

**Required Sections**:
1. **Header**: Analysis parameters (genes, protein, keyword, organism)
2. **Phase 1 Results**: Pathway enrichment (if gene list)
3. **Phase 2 Results**: Protein-pathway mapping (if protein ID)
4. **Phase 3 Results**: Keyword search across databases (if keyword)
5. **Phase 4 Results**: Top-level pathway catalog (always)

**Per-Database Subsections**:
- Database name and result count
- Table of pathways with key metadata
- Note if database returns no results
- Links or IDs for follow-up

### Data Tables

**Enrichment Results**:
| Pathway | P-value | Adjusted P-value | Genes |
| ... | ... | ... | ... |

**Protein Pathways**:
| Pathway Name | Pathway ID | Species |
| ... | ... | ... |

**Keyword Search**:
| Pathway/Model ID | Name | Source/Database |
| ... | ... | ... |

---

## Tool Parameter Reference

**Critical Parameter Notes** (from testing):

| Tool | Parameter | CORRECT Name | Common Mistake |
|------|-----------|--------------|----------------|
| Reactome_map_uniprot_to_pathways | `id` | ✅ `id` | ❌ `uniprot_id` |
| kegg_search_pathway | `keyword` | ✅ `keyword` | - |
| WikiPathways_search | `query` | ✅ `query` | - |
| pc_search_pathways | `action` + `keyword` | ✅ Both required | ❌ `action` optional |
| enrichr_gene_enrichment_analysis | `gene_list` | ✅ `gene_list` | - |

**Response Format Notes**:
- **Reactome**: Returns list directly (not wrapped in `{status, data}`)
- **Pathway Commons**: Returns dict directly with `total_hits` and `pathways`
- **Others**: Standard `{status: "success", data: [...]}` format

---

## Fallback Strategies

### Enrichment Analysis
- **Primary**: Enrichr with KEGG library
- **Fallback**: Try alternative libraries (Reactome, GO Biological Process)
- **If all fail**: Note "enrichment analysis unavailable" and continue

### Protein Mapping
- **Primary**: Reactome protein-pathway mapping
- **Fallback**: Use keyword search with protein name
- **If empty**: Check if protein ID valid; suggest checking gene symbol

### Keyword Search
- **Primary**: Search all databases (KEGG, WikiPathways, Pathway Commons, BioModels)
- **Fallback**: If all empty, broaden keyword (e.g., "diabetes" → "glucose")
- **If still empty**: Note "no pathways found for [keyword]"

---

## Common Use Patterns

### Pattern 1: Differential Expression Analysis
```
Input: Gene list from RNA-seq (upregulated genes)
Workflow: Phase 1 (Enrichment) → Phase 4 (Context)
Output: Enriched pathways explaining expression changes
```

### Pattern 2: Protein Function Investigation
```
Input: UniProt ID of protein of interest
Workflow: Phase 2 (Protein mapping) → Phase 3 (Keyword with protein name)
Output: All pathways involving protein + related pathways
```

### Pattern 3: Disease Pathway Exploration
```
Input: Disease name or process keyword
Workflow: Phase 3 (Keyword search) → Phase 4 (Context)
Output: Pathways from multiple databases related to disease
```

### Pattern 4: Comprehensive Multi-Input
```
Input: Gene list + protein ID + keyword
Workflow: All phases
Output: Complete systems view with enrichment, specific mappings, and context
```

---

## Quality Checks

### Data Completeness
- [ ] At least one analysis phase completed successfully
- [ ] Each database result includes source attribution
- [ ] Empty results explicitly noted (not silently omitted)
- [ ] P-values reported with appropriate precision
- [ ] Pathway IDs provided for follow-up analysis

### Biological Validity
- [ ] Enrichment p-values show significance threshold
- [ ] Protein mappings consistent with known function
- [ ] Keyword results relevant to query
- [ ] Cross-database results show expected overlaps

### Report Quality
- [ ] All sections present even if "no data"
- [ ] Tables formatted consistently
- [ ] Source databases clearly attributed
- [ ] Follow-up recommendations if data sparse

---

## Limitations & Known Issues

### Database-Specific
- **Reactome**: Strong human coverage; limited for non-model organisms
- **KEGG**: Requires keyword match; may miss synonyms
- **WikiPathways**: Variable curation quality; check pathway version dates
- **Pathway Commons**: Aggregation can have duplicates; check source
- **BioModels**: Sparse for many processes; often returns no results
- **Enrichr**: Requires gene symbols (not IDs); case-sensitive

### Technical
- **Response formats**: Different databases use different response structures (handled in implementation)
- **Rate limits**: Some databases have rate limits for heavy usage
- **Version differences**: Pathway databases updated at different rates

### Analysis
- **Enrichment bias**: Pathway enrichment depends on pathway size and annotation completeness
- **Organism specificity**: Not all databases cover all organisms equally
- **Pathway definitions**: Same biological process may be modeled differently across databases

---

## Summary

**Systems Biology & Pathway Analysis Skill** provides comprehensive pathway analysis by integrating:
1. ✅ Statistical pathway enrichment (Enrichr)
2. ✅ Protein-pathway mapping (Reactome)
3. ✅ Multi-database keyword search (KEGG, WikiPathways, Pathway Commons, BioModels)
4. ✅ Hierarchical pathway context (Reactome top-level)

**Outputs**: Markdown report with pathway tables, enrichment statistics, and cross-database comparisons

**Best for**: Gene set analysis, protein function investigation, pathway discovery, systems-level biology
