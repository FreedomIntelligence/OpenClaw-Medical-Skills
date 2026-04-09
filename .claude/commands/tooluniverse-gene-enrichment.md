# tooluniverse-gene-enrichment

> Perform comprehensive gene enrichment and pathway analysis using gseapy (ORA and GSEA), PANTHER, STRING, Reactome, and 40+ ToolUniverse tools. Supports GO enrichment (BP, MF, CC), KEGG, Reactome, WikiPathways, MSigDB Hallmark, and 220+ Enrichr libraries. Handles multiple ID types (gene symbols, Ensembl, Entrez, UniProt), multiple organisms (human, mouse, rat, fly, worm, yeast), customizable backgrounds, and multiple testing correction (BH, Bonferroni). Use when users ask about gene enrichment, pathway analysis, GO term enrichment, KEGG pathway analysis, GSEA, over-representation analysis, functional annotation, or gene set analysis.

# Gene Enrichment and Pathway Analysis

Perform comprehensive gene enrichment analysis including Gene Ontology (GO), KEGG, Reactome, WikiPathways, and MSigDB enrichment using both Over-Representation Analysis (ORA) and Gene Set Enrichment Analysis (GSEA). Integrates local computation via gseapy with ToolUniverse pathway databases for cross-validated, publication-ready results.

**IMPORTANT**: Always use English terms in tool calls (gene names, pathway names, organism names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

---

## When to Use This Skill

Apply when users:
- Ask about gene enrichment analysis (GO, KEGG, Reactome, etc.)
- Have a gene list from differential expression, clustering, or any experiment
- Want to know which biological processes, molecular functions, or cellular components are enriched
- Need KEGG or Reactome pathway enrichment analysis
- Ask about GSEA (Gene Set Enrichment Analysis) with ranked gene lists
- Want over-representation analysis (ORA) with Fisher's exact test
- Need multiple testing correction (Benjamini-Hochberg, Bonferroni)
- Ask about enrichGO, gseapy, clusterProfiler-style analyses

**NOT for** (use other skills instead):
- Network pharmacology / drug repurposing → Use `tooluniverse-network-pharmacology`
- Disease characterization → Use `tooluniverse-multiomic-disease-characterization`
- Single gene function lookup → Use `tooluniverse-disease-research`
- Spatial omics analysis → Use `tooluniverse-spatial-omics-analysis`
- Protein-protein interaction analysis only → Use `tooluniverse-protein-interactions`

---

## Input Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| **gene_list** | Yes | List of gene symbols, Ensembl IDs, or Entrez IDs | `["TP53", "BRCA1", "EGFR"]` |
| **organism** | No | Organism (default: human). Supported: human, mouse, rat, fly, worm, yeast, zebrafish | `human` |
| **analysis_type** | No | `ORA` (default) or `GSEA` | `ORA` |
| **enrichment_databases** | No | Which databases to query. Default: all applicable | `["GO_BP", "GO_MF", "GO_CC", "KEGG", "Reactome"]` |
| **gene_id_type** | No | Input ID type: `symbol`, `ensembl`, `entrez`, `uniprot` (auto-detected if omitted) | `symbol` |
| **p_value_cutoff** | No | Significance threshold (default: 0.05) | `0.05` |
| **correction_method** | No | Multiple testing: `BH` (Benjamini-Hochberg, default), `bonferroni`, `fdr` | `BH` |
| **background_genes** | No | Custom background gene set (default: genome-wide) | `["GENE1", "GENE2", ...]` |
| **ranked_gene_list** | No | For GSEA: gene-to-score mapping (e.g., log2FC) | `{"TP53": 2.5, "BRCA1": -1.3, ...}` |

---

## Core Principles

1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **ID disambiguation FIRST** - Detect and convert gene IDs before ANY enrichment
3. **Multi-source validation** - Run enrichment on at least 2 independent tools, cross-validate
4. **Exact p-values** - Report raw p-values AND adjusted p-values with correction method
5. **Multiple testing correction** - ALWAYS apply Benjamini-Hochberg unless user specifies otherwise
6. **Gene set size filtering** - Filter by min/max gene set size to avoid trivial/overly broad terms
7. **Evidence grading** - Grade enrichment sources T1-T4
8. **Negative results documented** - "No significant enrichment" is a valid finding
9. **Source references** - Every enrichment result must cite the tool/database/library used
10. **Completeness checklist** - Mandatory section at end showing analysis coverage

---

## Decision Tree: ORA vs GSEA

```
Q: Do you have a ranked gene list (with scores/fold-changes)?
  YES → Use GSEA (gseapy.prerank)
        - Input: Gene-to-score mapping (e.g., log2FC)
        - Statistics: Running enrichment score, permutation test
        - Cutoff: FDR q-val < 0.25 (standard for GSEA)
        - Output: NES (Normalized Enrichment Score), lead genes
        See: references/gsea_workflow.md

  NO  → Use ORA (gseapy.enrichr)
        - Input: Gene list only
        - Statistics: Fisher's exact test, hypergeometric
        - Cutoff: Adjusted P-value < 0.05 (or user specified)
        - Output: P-value, adjusted P-value, overlap, odds ratio
        See: references/ora_workflow.md
```

---

## Decision Tree: gseapy vs ToolUniverse Tools

```
Q: Which enrichment method should I use?

Primary Analysis (ALWAYS):
  ├─ gseapy.enrichr (ORA) OR gseapy.prerank (GSEA)
  │  - Most comprehensive (225+ Enrichr libraries)
  │  - GO (BP, MF, CC), KEGG, Reactome, WikiPathways, MSigDB
  │  - All organisms supported
  │  - Returns: P-value, Adjusted P-value, Overlap, Genes
  │  See: references/enrichr_guide.md

Cross-Validation (REQUIRED for publication):
  ├─ PANTHER_enrichment [T1 - curated]
  │  - Curated GO enrichment
  │  - Multiple organisms (taxonomy ID)
  │  - GO BP, MF, CC, PANTHER pathways, Reactome
  │
  ├─ STRING_functional_enrichment [T2 - validated]
  │  - Returns ALL categories in one call
  │  - Filter by category: Process, Function, Component, KEGG, Reactome
  │  - Network-based enrichment
  │
  └─ ReactomeAnalysis_pathway_enrichment [T1 - curated]
     - Reactome curated pathways
     - Cross-species projection
     - Detailed pathway hierarchy

Additional Context (Optional):
  ├─ GO_get_term_by_id, QuickGO_get_term_detail (GO term details)
  ├─ Reactome_get_pathway, Reactome_get_pathway_hierarchy (pathway context)
  ├─ WikiPathways_search, WikiPathways_get_pathway (community pathways)
  └─ STRING_ppi_enrichment (network topology analysis)
```

---

## Quick Start Workflow

### Step 1: Create Report File (IMMEDIATE)

```python
report_path = f"{analysis_name}_enrichment_report.md"
# Write header with placeholder sections
# Update progressively as analysis proceeds
```

### Step 2: ID Conversion and Validation

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Detect ID type
gene_list = ["TP53", "BRCA1", "EGFR"]
# Auto-detect: ENSG* = Ensembl, numeric = Entrez, pattern = UniProt, else = Symbol

# Convert if needed (Ensembl/Entrez → Symbol)
result = tu.tools.MyGene_batch_query(
    gene_ids=gene_list,
    fields="symbol,entrezgene,ensembl.gene"
)
# Extract symbols from results

# Validate with STRING
mapped = tu.tools.STRING_map_identifiers(
    protein_ids=gene_symbols,
    species=9606  # human
)
# Use preferredName for canonical symbols
```

**See**: references/id_conversion.md for complete examples

### Step 3: Primary Enrichment with gseapy

**For ORA (gene list only)**:
```python
import gseapy

# GO Biological Process
go_bp = gseapy.enrichr(
    gene_list=gene_symbols,
    gene_sets='GO_Biological_Process_2021',
    organism='human',
    outdir=None,
    no_plot=True,
    background=background_genes  # None = genome-wide
)
go_bp_sig = go_bp.results[go_bp.results['Adjusted P-value'] < 0.05]
```

**For GSEA (ranked gene list)**:
```python
import pandas as pd

# Ranked by log2FC
ranked_series = pd.Series(gene_to_score).sort_values(ascending=False)

gsea_result = gseapy.prerank(
    rnk=ranked_series,
    gene_sets='GO_Biological_Process_2021',
    outdir=None,
    no_plot=True,
    seed=42,
    min_size=5,
    max_size=500,
    permutation_num=1000
)
gsea_sig = gsea_result.res2d[gsea_result.res2d['FDR q-val'] < 0.25]
```

**See**:
- references/ora_workflow.md for complete ORA examples
- references/gsea_workflow.md for complete GSEA examples
- references/enrichr_guide.md for all 225+ libraries

### Step 4: Cross-Validation with ToolUniverse

```python
# PANTHER [T1 - curated]
panther_bp = tu.tools.PANTHER_enrichment(
    gene_list=','.join(gene_symbols),  # comma-separated string
    organism=9606,
    annotation_dataset='GO:0008150'  # biological_process
)

# STRING [T2 - validated]
string_result = tu.tools.STRING_functional_enrichment(
    protein_ids=gene_symbols,
    species=9606
)
# Filter by category: Process, Function, Component, KEGG, Reactome

# Reactome [T1 - curated]
reactome_result = tu.tools.ReactomeAnalysis_pathway_enrichment(
    identifiers=' '.join(gene_symbols),  # space-separated
    page_size=50,
    include_disease=True
)
```

**See**: references/cross_validation.md for comparison strategies

### Step 5: Report Compilation

```markdown
## Results

### GO Biological Process (Top 10)
| Term | P-value | Adj. P-value | Overlap | Genes | Evidence |
|------|---------|-------------|---------|-------|----------|
| regulation of cell cycle (GO:0051726) | 1.2e-08 | 3.4e-06 | 12/45 | TP53;BRCA1;... | [T2] gseapy |

### Cross-Validation
| GO Term | gseapy FDR | PANTHER FDR | STRING FDR | Consensus |
|---------|-----------|-------------|-----------|-----------|
| GO:0051726 | 3.4e-06 | 2.1e-05 | 1.8e-05 | 3/3 ✓ |

### Completeness Checklist
- [x] ID Conversion (MyGene, STRING) - 95% mapped
- [x] GO BP (gseapy, PANTHER, STRING) - 24 significant terms
- [x] GO MF (gseapy, PANTHER, STRING) - 18 significant terms
- [x] GO CC (gseapy, PANTHER, STRING) - 12 significant terms
- [x] KEGG (gseapy, STRING) - 8 significant pathways
- [x] Reactome (gseapy, ReactomeAPI) - 15 significant pathways
- [x] Cross-validation - 12 consensus terms (2+ sources)
```

**See**: scripts/format_enrichment_output.py for automated formatting

---

## Evidence Grading

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Curated/experimental enrichment | PANTHER, Reactome Analysis Service |
| **T2** | [T2] | Computational enrichment, well-validated | gseapy ORA/GSEA, STRING functional enrichment |
| **T3** | [T3] | Text-mining/predicted enrichment | Enrichr non-curated libraries |
| **T4** | [T4] | Single-source annotation | Individual gene GO annotations from QuickGO |

---

## Supported Organisms

| Organism | Taxonomy ID | gseapy | PANTHER | STRING | Reactome |
|----------|------------|--------|---------|--------|----------|
| Human | 9606 | Yes | Yes | Yes | Yes |
| Mouse | 10090 | Yes (`*_Mouse`) | Yes | Yes | Yes (projection) |
| Rat | 10116 | Limited | Yes | Yes | Yes (projection) |
| Fly | 7227 | Limited | Yes | Yes | Yes (projection) |
| Worm | 6239 | Limited | Yes | Yes | Yes (projection) |
| Yeast | 4932 | Limited | Yes | Yes | Yes |

**See**: references/organism_support.md for organism-specific libraries

---

## Common Patterns

### Pattern 1: Standard DEG Enrichment (ORA)
```
Input: List of differentially expressed gene symbols
Flow: ID validation → gseapy ORA (GO + KEGG + Reactome) →
      PANTHER + STRING cross-validation → Report top enriched terms
Use: When you have unranked gene list from DESeq2/edgeR
```

### Pattern 2: Ranked Gene List (GSEA)
```
Input: Gene-to-log2FC mapping from differential expression
Flow: Convert to ranked Series → gseapy GSEA (GO + KEGG + MSigDB) →
      Filter by FDR < 0.25 → Report NES and lead genes
Use: When you have fold-changes or other ranking metric
```

### Pattern 3: BixBench Enrichment Question
```
Input: Specific question about enrichment (e.g., "What is the adjusted p-val for neutrophil activation?")
Flow: Parse question for gene list and library → Run gseapy with exact library →
      Find specific term → Report exact p-value and adjusted p-value
Use: When answering targeted questions about specific terms
```

### Pattern 4: Multi-Organism Enrichment
```
Input: Gene list from mouse experiment
Flow: Use organism='mouse' for gseapy → organism=10090 for PANTHER/STRING →
      projection=True for Reactome human pathway mapping
Use: When working with non-human organisms
```

**See**: references/common_patterns.md for more examples

---

## Troubleshooting

**"No significant enrichment found"**:
- Verify gene symbols are valid (STRING_map_identifiers)
- Try different library versions (2021 vs 2023 vs 2025)
- Try relaxing significance cutoff or use GSEA instead

**"Gene not found" errors**:
- Check ID type and convert using MyGene_batch_query
- Remove version suffixes from Ensembl IDs (ENSG00000141510.16 → ENSG00000141510)

**"STRING returns all categories"**:
- This is expected; filter by `d['category'] == 'Process'` after receiving results

**See**: references/troubleshooting.md for complete guide

---

## Tool Reference

### Primary Enrichment Tools
| Tool | Input | Output | Use For |
|------|-------|--------|---------|
| `gseapy.enrichr()` | gene_list, gene_sets, organism | `.results` DataFrame | ORA with 225+ libraries |
| `gseapy.prerank()` | rnk (ranked Series), gene_sets | `.res2d` DataFrame | GSEA analysis |

### Cross-Validation Tools
| Tool | Key Parameters | Evidence Grade |
|------|---------------|----------------|
| `PANTHER_enrichment` | gene_list (comma-sep), organism, annotation_dataset | [T1] |
| `STRING_functional_enrichment` | protein_ids, species | [T2] |
| `ReactomeAnalysis_pathway_enrichment` | identifiers (space-sep), page_size | [T1] |

### ID Conversion Tools
| Tool | Input | Output |
|------|-------|--------|
| `MyGene_batch_query` | gene_ids, fields | Symbol, Entrez, Ensembl mappings |
| `STRING_map_identifiers` | protein_ids, species | Preferred names, STRING IDs |

**See**: references/tool_parameters.md for complete parameter documentation

---

## Detailed Documentation

All detailed examples, code blocks, and advanced topics have been moved to `references/`:

- **references/ora_workflow.md** - Complete ORA examples with all databases
- **references/gsea_workflow.md** - Complete GSEA workflow with ranked lists
- **references/enrichr_guide.md** - All 225+ Enrichr libraries and usage
- **references/cross_validation.md** - Multi-source validation strategies
- **references/id_conversion.md** - Gene ID disambiguation and conversion
- **references/tool_parameters.md** - Complete tool parameter reference
- **references/organism_support.md** - Organism-specific configurations
- **references/common_patterns.md** - Detailed use case examples
- **references/troubleshooting.md** - Complete troubleshooting guide
- **references/multiple_testing.md** - Correction methods (BH, Bonferroni, BY)
- **references/report_template.md** - Standard report format

Helper scripts:
- **scripts/format_enrichment_output.py** - Format results for reports
- **scripts/compare_enrichment_sources.py** - Cross-validation analysis
- **scripts/filter_by_gene_set_size.py** - Filter terms by size

---

## Resources

For network-level analysis: [tooluniverse-network-pharmacology](../tooluniverse-network-pharmacology/SKILL.md)
For disease characterization: [tooluniverse-multiomic-disease-characterization](../tooluniverse-multiomic-disease-characterization/SKILL.md)
For spatial omics: [tooluniverse-spatial-omics-analysis](../tooluniverse-spatial-omics-analysis/SKILL.md)
For protein interactions: [tooluniverse-protein-interactions](../tooluniverse-protein-interactions/SKILL.md)

gseapy documentation: https://gseapy.readthedocs.io/
PANTHER API: http://pantherdb.org/services/oai/pantherdb/
STRING API: https://string-db.org/cgi/help?sessionId=&subpage=api
Reactome Analysis: https://reactome.org/AnalysisService/
