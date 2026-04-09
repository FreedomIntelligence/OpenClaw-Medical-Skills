# tooluniverse-literature-deep-research

> Conduct comprehensive literature research with target disambiguation, evidence grading, and structured theme extraction. Creates a detailed report with mandatory completeness checklist, biological model synthesis, and testable hypotheses. For biological targets, resolves official IDs (Ensembl/UniProt), synonyms, naming collisions, and gathers expression/pathway context before literature search. Default deliverable is a report file; for single factoid questions, uses a fast verification mode and may include an inline answer. Use when users need thorough literature reviews, target profiles, or to verify specific claims from the literature.

# Literature Deep Research Strategy (Enhanced)

A systematic approach to comprehensive literature research that **starts with target disambiguation** to prevent missing details, uses **evidence grading** to separate signal from noise, and produces a **content-focused report** with mandatory completeness sections.

**KEY PRINCIPLES**:
1. **Target disambiguation FIRST** - Resolve IDs, synonyms, naming collisions before literature search
2. **Right-size the deliverable** - Use *Factoid / Verification Mode* for single, answerable questions; use full report mode for “deep research”
3. **Report-first output** - Default deliverable is a report file; an inline answer is allowed (and recommended) for Factoid / Verification Mode
4. **Evidence grading** - Grade every claim by evidence strength (mechanistic paper vs screen hit vs review vs text-mined)
5. **Mandatory completeness** - All checklist sections must exist, even if "unknown/limited evidence"
6. **Source attribution** - Every piece of information traceable to database/tool
7. **English-first queries** - Always use English terms for literature searches and tool calls, even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language

---

## Workflow Overview

```
User Query
  ↓
Phase 0: CLARIFY + MODE SELECT (factoid vs deep report)
  ↓
Phase 1: TARGET DISAMBIGUATION + PROFILE (default ON for biological targets)
  ├─ Resolve official IDs (Ensembl, UniProt, HGNC)
  ├─ Gather synonyms/aliases + known naming collisions
  ├─ Get protein length, isoforms, domain architecture
  ├─ Get subcellular location, expression, GO terms, pathways
  └─ Output: Target Profile section + Collision-aware search plan
  ↓
Phase 2: LITERATURE SEARCH (internal methodology, not shown)
  ├─ High-precision seed queries (build mechanistic core)
  ├─ Citation network expansion from seeds
  ├─ Collision-filtered broader queries
  └─ Theme clustering + evidence grading
  ↓
Phase 3: REPORT SYNTHESIS
  ├─ Progressive writing to [topic]_report.md
  ├─ Mandatory completeness checklist validation
  └─ Biological model + testable hypotheses
  ↓
Optional: methods_appendix.md (only if user requests)
```

---

## Phase 0: Initial Clarification

### Mandatory Questions

1. **Target type**: Is this a biological target (gene/protein), a general topic, or a disease?
2. **Scope**: Is this a *single factoid to verify* (“Which antibiotic?”, “Which strain?”, “Which year?”) or a comprehensive/deep review?
3. **Known aliases**: Any specific gene symbols or protein names you use?
4. **Constraints**: Open access only? Include preprints? Specific organisms?
5. **Methods appendix**: Do you want methodology details in a separate file?

### Mode Selection (CRITICAL)

Pick exactly one mode based on the user’s intent and the question structure:

1. **Factoid / Verification Mode** (single concrete question; answer should be a short phrase/sentence)
2. **Mini-review Mode** (narrow topic; 1–3 pages of synthesis)
3. **Full Deep-Research Mode** (use the full template + completeness checklist)

**Heuristic**:
- If the user asks “X has been evolved to be resistant to *which antibiotic*?” → **Factoid / Verification Mode**
- If the user asks “What does the literature say about X?” → **Full Deep-Research Mode**

### Factoid / Verification Mode (Fast Path)

**Goal**: Provide a correct, source-verified single answer, with minimal but explicit evidence attribution.

**Deliverables** (still file-backed):
1. `[topic]_factcheck_report.md` (≤ 1 page)
2. `[topic]_bibliography.json` (+ CSV) containing the key paper(s)

**Fact-check report template**:
```markdown
# [TOPIC]: Fact-check Report

*Generated: [Date]*
*Evidence cutoff: [Date]*

## Question
[User question]

## Answer
**[One-sentence answer]** [Evidence: ★★★/★★☆/★☆☆/☆☆☆]

## Source(s)
- [Primary paper citation: journal/year/PMID/DOI as available]

## Verification Notes
- [1–3 bullets: where in the paper the statement appears (Abstract/Results/Methods), and any key constraints]

## Limitations
- [If full text not available, or if only review evidence exists]
```

**Required verification behavior**:
- Prefer ToolUniverse literature tools (Europe PMC / PubMed / PMC / Semantic Scholar) over general web browsing.
- Use full-text snippet verification when possible (Europe PMC auto-snippet tier is ideal).
- Avoid adding extra claims (e.g., “not X”) unless the paper explicitly supports them.

**Suggested tool pattern**:
- `EuropePMC_search_articles(query=..., extract_terms_from_fulltext=[...])` to pull OA full-text snippets for the key terms.
- If OA snippets unavailable: fall back to `PMC_search_papers` (if in PMC) or `SemanticScholar_search_papers` → `SemanticScholar_get_pdf_snippets`.

**Evidence grading (factoid)**:
- If the statement is explicitly made in a primary experimental paper (Results/Methods/Abstract): label **T1 (★★★)**.
- If it’s only in a review: label **T4 (☆☆☆)** and try to locate the primary source.

### Detect Target Type

| Query Pattern | Type | Action |
|---------------|------|--------|
| Gene symbol (EGFR, TP53, ATP6V1A) | Biological target | Phase 1 required |
| Protein name ("V-ATPase", "kinase") | Biological target | Phase 1 required |
| UniProt ID (P00533, Q93050) | Biological target | Phase 1 required |
| Disease, pathway, method | General topic | Phase 1 optional |
| "Literature on X" | Depends on X | Assess X |

---

## Phase 1: Target Disambiguation + Profile (Default ON)

**CRITICAL**: This phase prevents "missing target details" when literature is sparse or noisy.

### 1.1 Resolve Official Identifiers

Use these tools to establish canonical identity:

```
UniProt_search → Get UniProt accession for human protein
UniProt_get_entry_by_accession → Full entry with cross-references
UniProt_id_mapping → Map between ID types
ensembl_lookup_gene → Ensembl gene ID, biotype
MyGene_get_gene_annotation → NCBI Gene ID, aliases, summary
```

**Output for report**:
```markdown
## Target Identity

| Identifier | Value | Source |
|------------|-------|--------|
| Official Symbol | ATP6V1A | HGNC |
| UniProt | P38606 | UniProt |
| Ensembl Gene | ENSG00000114573 | Ensembl |
| NCBI Gene ID | 523 | NCBI |
| ChEMBL Target | CHEMBL2364682 | ChEMBL |

**Full Name**: V-type proton ATPase catalytic subunit A
**Synonyms/Aliases**: ATP6A1, VPP2, Vma1, VA68
```

### 1.2 Identify Naming Collisions

**CRITICAL**: Many gene names have collisions. Examples:
- **TRAG**: T-cell regulatory gene vs bacterial TraG conjugation protein
- **WDR7-7**: Could match gene WDR7 vs lncRNA
- **JAK**: Janus kinase vs Just Another Kinase
- **CAT**: Catalase vs chloramphenicol acetyltransferase

**Detection strategy**:
1. Search PubMed for `"[SYMBOL]"[Title]` - review first 20 titles
2. If >20% off-topic, identify collision terms
3. Build negative filter: `NOT [collision_term1] NOT [collision_term2]`

**Output for report**:
```markdown
### Known Naming Collisions

- Symbol "ATP6V1A" is unambiguous (no major collisions detected)
- Related but distinct: ATP6V0A1-4 (V0 subunits vs V1 subunits)
- Search filter applied: Include "vacuolar" OR "V-ATPase", exclude "V0 domain" when V1-specific
```

### 1.3 Protein Architecture & Domains

Use annotation tools (not literature):

```
InterPro_get_protein_domains → Domain architecture
UniProt_get_ptm_processing_by_accession → PTMs, active sites
proteins_api_get_protein → Additional protein features
```

**Output for report**:
```markdown
### Protein Architecture

| Domain | Position | InterPro ID | Function |
|--------|----------|-------------|----------|
| V-ATPase A subunit, N-terminal | 1-90 | IPR022879 | ATP binding |
| V-ATPase A subunit, catalytic | 91-490 | IPR005725 | Catalysis |
| V-ATPase A subunit, C-terminal | 491-617 | IPR022878 | Complex assembly |

**Length**: 617 aa | **Isoforms**: 2 (canonical P38606-1, variant P38606-2 missing aa 1-45)
**Active sites**: Lys-168 (ATP binding), Glu-261 (catalytic)

*Sources: InterPro, UniProt*
```

### 1.4 Subcellular Location

```
HPA_get_subcellular_location → Human Protein Atlas localization
UniProt_get_subcellular_location_by_accession → UniProt annotation
```

**Output for report**:
```markdown
### Subcellular Localization

| Location | Confidence | Source |
|----------|------------|--------|
| Lysosome membrane | High | HPA + UniProt |
| Endosome membrane | High | UniProt |
| Golgi apparatus | Medium | HPA |
| Plasma membrane (subset) | Low | Literature |

**Primary location**: Lysosomal/endosomal membranes (vacuolar ATPase complex)
*Sources: Human Protein Atlas, UniProt*
```

### 1.5 Baseline Expression

```
GTEx_get_median_gene_expression → Tissue expression (TPM)
HPA_get_rna_expression_by_source → HPA expression data
```

**Output for report**:
```markdown
### Baseline Tissue Expression

| Tissue | Expression (TPM) | Specificity |
|--------|------------------|-------------|
| Kidney cortex | 145.3 | Elevated |
| Liver | 98.7 | Medium |
| Brain - Cerebellum | 87.2 | Medium |
| Lung | 76.4 | Medium |
| Ubiquitous baseline | ~50 | Broad |

**Tissue Specificity**: Low (τ = 0.28) - broadly expressed housekeeping gene
*Source: GTEx v8*
```

### 1.6 GO Terms & Pathway Placement

```
GO_get_annotations_for_gene → GO annotations
Reactome_map_uniprot_to_pathways → Reactome pathways
kegg_get_gene_info → KEGG pathways
OpenTargets_get_target_gene_ontology_by_ensemblID → Open Targets GO
```

**Output for report**:
```markdown
### Functional Annotations (GO)

**Molecular Function**:
- ATP hydrolysis activity (GO:0016887) [Evidence: IDA]
- Proton-transporting ATPase activity (GO:0046961) [Evidence: IDA]

**Biological Process**:
- Lysosomal acidification (GO:0007041) [Evidence: IMP]
- Autophagy (GO:0006914) [Evidence: IMP]
- Bone resorption (GO:0045453) [Evidence: IMP]

**Cellular Component**:
- Vacuolar proton-transporting V-type ATPase, V1 domain (GO:0000221) [Evidence: IDA]

### Pathway Involvement

| Pathway | Database | Significance |
|---------|----------|--------------|
| Lysosome | KEGG hsa04142 | Core component |
| Phagosome | KEGG hsa04145 | Acidification |
| Autophagy - animal | Reactome R-HSA-9612973 | mTORC1 regulation |

*Sources: GO Consortium, Reactome, KEGG*
```

---

## Phase 2: Literature Search (Internal Methodology)

**NOTE**: This methodology is kept internal. The report shows findings, not process.

### 2.1 Query Strategy: Collision-Aware Synonym Plan

#### Step 1: High-Precision Seed Queries (Build Mechanistic Core)

```
Query 1: "[GENE_SYMBOL]"[Title] AND (mechanism OR function OR structure)
Query 2: "[FULL_PROTEIN_NAME]"[Title] 
Query 3: "[UNIPROT_ID]" (catches supplementary materials)
```

**Purpose**: Get 15-30 high-confidence, mechanistic papers that are definitely on-target.

#### Step 2: Citation Network Expansion (Especially for Sparse Targets)

Once you have 5-15 core PMIDs:
```
PubMed_get_cited_by → Papers citing each seed
PubMed_get_related → Computationally related papers  
EuropePMC_get_citations → Alternative citation source
EuropePMC_get_references → Backward citations from seeds
```

**Citation-network first option**: For older targets with deprecated terminology, citation expansion often outperforms keyword searching.

#### Step 3: Collision-Filtered Broader Queries

```
Broader query: "[GENE_SYMBOL]" AND ([pathway1] OR [pathway2] OR [function])
Apply collision filter: NOT [collision_term1] NOT [collision_term2]
```

Example for bacterial TraG collision:
```
"TRAG" AND (T-cell OR immune OR cancer) NOT plasmid NOT conjugation NOT bacterial
```

### 2.2 Database Tools

**Literature Search** (use all relevant):
- `PubMed_search_articles` - Primary biomedical
- `PMC_search_papers` - Full-text
- `EuropePMC_search_articles` - European coverage
- `openalex_literature_search` - Broad academic
- `Crossref_search_works` - DOI registry
- `SemanticScholar_search_papers` - AI-ranked
- `BioRxiv_search_preprints` / `MedRxiv_search_preprints` - Preprints

**Citation Tools** (with failure handling):
- `PubMed_get_cited_by` - Primary (NCBI elink can be flaky)
- `EuropePMC_get_citations` - **Fallback** when PubMed fails
- `PubMed_get_related` - Related articles
- `EuropePMC_get_references` - Reference lists

**Annotation Tools** (not literature, but fill gaps):
- `UniProt_*` tools - Protein data
- `InterPro_get_protein_domains` - Domains
- `GTEx_*` tools - Expression
- `HPA_*` tools - Human Protein Atlas
- `OpenTargets_*` tools - Target-disease associations
- `GO_get_annotations_for_gene` - GO terms

### 2.3 Full-Text Verification Strategy

**WHEN TO USE**: Abstracts lack critical experimental details (exact drugs, cell lines, concentrations, specific protocols).

**Three-Tier Strategy**:

#### Tier 1: Auto-Snippet Mode (Europe PMC) - FASTEST

**Use for**: Exploratory queries with 3-5 specific terms

```python
results = EuropePMC_search_articles(
    query="bacterial antibiotic resistance evolution",
    limit=10,
    extract_terms_from_fulltext=["ciprofloxacin", "meropenem", "A. baumannii", "MIC"]
)

# Check which articles have full-text snippets
for article in results:
    if "fulltext_snippets" in article:
        # Snippets automatically extracted from OA full text
        for snippet in article["fulltext_snippets"]:
            # Use snippet["term"] and snippet["snippet"] for verification
            pass
```

**Advantages**:
- ✅ Single tool call (search + snippets)
- ✅ Bounded latency (max 3 OA articles, ~3-5 seconds total)
- ✅ No manual URL extraction
- ✅ Max 5 search terms

**Limitations**:
- ❌ Only works for OA articles with fullTextXML
- ❌ Limited to first 3 OA articles
- ❌ Europe PMC coverage only (~30-40% OA)

**When to use**: Initial exploration, quick verification of 1-2 papers

#### Tier 2: Manual Two-Step (Semantic Scholar, ArXiv) - TARGETED

**Use for**: Specific high-value papers you identified from search

```python
# Step 1: Search
papers = SemanticScholar_search_papers(
    query="machine learning interpretability",
    limit=10
)

# Step 2: Extract from specific OA papers
for paper in papers:
    if paper.get("open_access_pdf_url"):
        snippets = SemanticScholar_get_pdf_snippets(
            open_access_pdf_url=paper["open_access_pdf_url"],
            terms=["SHAP", "gradient attribution", "layer-wise relevance"],
            window_chars=300
        )
        if snippets["status"] == "success":
            # Process snippets["snippets"]
            pass
```

**ArXiv variant** (100% OA, no paywall):

```python
# All arXiv papers are freely available
snippets = ArXiv_get_pdf_snippets(
    arxiv_id="2301.12345",
    terms=["attention mechanism", "self-attention", "layer normalization"],
    max_snippets_per_term=5
)
```

**Advantages**:
- ✅ Full control over which papers to process
- ✅ Adjustable window size (20-2000 chars)
- ✅ Works for Semantic Scholar (~15-20% OA PDFs) and ArXiv (100%)
- ✅ Can process any number of papers

**Limitations**:
- ❌ Two tool calls per article (search → extract)
- ❌ Manual loop needed
- ❌ Slower than auto-snippet mode

**When to use**: Thorough review of key papers, preprint analysis

#### Tier 3: Manual Download + Parse (Fallback) - SLOWEST

**Use for**: Paywalled content via institutional access

```python
# For paywalled PDFs accessible via institution
webpage_text = get_webpage_text_from_url(
    url="https://doi.org/10.1016/...",
    # Requires institutional proxy or VPN
)

# Extract relevant sections manually
if "Methods" in webpage_text:
    # Parse methods section
    pass
```

**Limitations**:
- ❌ Requires institutional access
- ❌ No snippet extraction (full HTML)
- ❌ Quality varies by publisher
- ❌ Slowest approach

**When to use**: Last resort for critical paywalled papers

#### Decision Matrix

| Scenario | Recommended Tier | Rationale |
|----------|------------------|-----------|
| Quick verification ("Which antibiotic?") | Tier 1 (Auto-snippet) | Fast, single call |
| Preprint deep-dive (arXiv, bioRxiv) | Tier 2 (Manual ArXiv) | 100% coverage, no paywall |
| High-value paper deep analysis | Tier 2 (Manual S2) | Precise control |
| Systematic review (50+ papers) | Tier 1 + Tier 2 | Auto for OA, manual for key papers |
| Paywalled critical paper | Tier 3 (Manual download) | Only option |

#### Best Practices

**1. Limit search terms to 3-5 specific keywords**:
- ✅ Good: `["ciprofloxacin 5 μg/mL", "HEK293 cells", "RNA-seq"]`
- ❌ Bad: `["drug", "method", "significant"]` (too broad)

**2. Check OA status before extraction**:
```python
if article.get("open_access") and article.get("fulltext_xml_url"):
    # Proceed with extraction
    pass
```

**3. Adjust window size for context**:
- Methods: 400-500 chars (full sentences)
- Quick verification: 150-200 chars
- Default: 220 chars (balanced)

**4. Handle failures gracefully**:
```python
if "fulltext_snippets" not in article:
    # Fallback: use abstract or skip
    print(f"No full text available: {article['title']}")
```

**5. Document full-text sources in report**:
```markdown
## Methods Verification

**Antibiotic concentrations** (verified from full text):
- Study A: Ciprofloxacin 5 μg/mL [PMC12345, Methods section]
- Study B: Meropenem 8 μg/mL [arXiv:2301.12345, Experimental Design]

*Note: Full-text verification performed on 8/15 OA papers (53% coverage)*
```

### 2.5 Tool Failure Handling

**Automatic retry strategy**:
```
Attempt 1: Call tool
If timeout/error:
  Wait 2 seconds
  Attempt 2: Retry
If still fails:
  Wait 5 seconds  
  Attempt 3: Try fallback tool
If fallback fails:
  Document "Data unavailable" in report
```

**Fallback chains**:
| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `PubMed_get_cited_by` | `EuropePMC_get_citations` | OpenAlex citations |
| `PubMed_get_related` | SemanticScholar recommendations | Manual keyword search |
| `GTEx_get_median_gene_expression` | `HPA_get_rna_expression_by_source` | Document as unavailable |
| `Unpaywall_check_oa_status` | Europe PMC OA flags | OpenAlex OA field |

### 2.6 Open Access Handling (Best-Effort)

**If Unpaywall email provided**: Check OA status for all papers with DOIs

**If no Unpaywall email**: Use best-effort OA signals:
- Europe PMC: `isOpenAccess` field
- PMC: All PMC papers are OA
- OpenAlex: `is_oa` field
- DOAJ: All DOAJ papers are OA

**Label in report**:
```markdown
*OA Status: Best-effort (Unpaywall not configured)*
```

---

## Phase 3: Evidence Grading

**CRITICAL**: Grade every claim by evidence strength to prevent low-signal mentions from diluting the report.

### Evidence Tiers

| Tier | Label | Description | Example |
|------|-------|-------------|---------|
| **T1** | ★★★ Mechanistic | In-target mechanistic study with direct experimental evidence | CRISPR KO + rescue |
| **T2** | ★★☆ Functional | Functional study showing role (may be in pathway context) | siRNA knockdown phenotype |
| **T3** | ★☆☆ Association | Screen hit, GWAS association, correlation | High-throughput screen |
| **T4** | ☆☆☆ Mention | Review mention, text-mined interaction, peripheral reference | Review article |

### How to Apply

In report, label sections and claims:

```markdown
### Mechanism of Action

ATP6V1A is the catalytic subunit responsible for ATP hydrolysis in the V-ATPase 
complex [★★★ Mechanistic: PMID:12345678]. Loss-of-function mutations cause 
vacuolar pH dysregulation [★★★: PMID:23456789].

The target has been implicated in mTORC1 signaling through lysosomal amino acid 
sensing [★★☆ Functional: PMID:34567890], though direct interaction data is limited.

A genome-wide screen identified ATP6V1A as essential in cancer cell lines 
[★☆☆ Association: PMID:45678901, DepMap].
```

### Theme-Level Grading

For each theme section, summarize evidence quality:

```markdown
### 3.1 Lysosomal Acidification (12 papers)
**Evidence Quality**: Strong (8 mechanistic, 3 functional, 1 association)

[Theme content...]
```

---

## Report Structure: Mandatory Completeness Checklist

**CRITICAL**: This checklist/template applies to **Full Deep-Research Mode**. For **Factoid / Verification Mode**, use a short fact-check report (see Phase 0) and do not force the full 15-section template.

### Output Files

1. **`[topic]_report.md`** - Main narrative report (**Full Deep-Research Mode**)
2. **`[topic]_factcheck_report.md`** - Short verification report (**Factoid / Verification Mode**)
3. **`[topic]_bibliography.json`** - Full deduplicated bibliography (always created)
4. **`methods_appendix.md`** - Methodology details (ONLY if user requests)

### Report Template

```markdown
# [TARGET/TOPIC]: Comprehensive Research Report

*Generated: [Date]*
*Evidence cutoff: [Date]*
*Total unique papers: [N]*

---

## Executive Summary

[2-3 paragraphs synthesizing key findings across all sections]

**Bottom Line**: [One-sentence actionable conclusion]

---

## 1. Target Identity & Aliases
*[MANDATORY - even for non-target topics, clarify scope]*

### 1.1 Official Identifiers
[Table of IDs or scope definition]

### 1.2 Synonyms and Aliases  
[List all known names - critical for complete literature coverage]

### 1.3 Known Naming Collisions
[Document collisions and how they were handled]

---

## 2. Protein Architecture
*[MANDATORY for protein targets; state "N/A - not a protein target" otherwise]*

### 2.1 Domain Structure
[Table of domains with positions, InterPro IDs]

### 2.2 Isoforms
[List isoforms, functional differences if known]

### 2.3 Key Structural Features
[Active sites, binding sites, PTMs]

### 2.4 Available Structures
[PDB entries, AlphaFold availability]

---

## 3. Complexes & Interaction Partners
*[MANDATORY]*

### 3.1 Known Complexes
[List complexes the protein participates in]

### 3.2 Direct Interactors
[Table of top interactors with evidence type and scores]

### 3.3 Functional Interaction Network
[Describe network context]

---

## 4. Subcellular Localization
*[MANDATORY]*

[Table of locations with confidence levels and sources]

---

## 5. Expression Profile
*[MANDATORY]*

### 5.1 Tissue Expression
[Table of top tissues with TPM values]

### 5.2 Cell-Type Expression
[If single-cell data available]

### 5.3 Disease-Specific Expression
[Expression changes in disease contexts]

---

## 6. Core Mechanisms
*[MANDATORY - this is the heart of the report]*

### 6.1 Molecular Function
[What the protein does biochemically]
**Evidence Quality**: [Strong/Moderate/Limited]

### 6.2 Biological Role
[Role in cellular/organismal context]
**Evidence Quality**: [Strong/Moderate/Limited]

### 6.3 Key Pathways
[Pathway involvement with evidence grades]

### 6.4 Regulation
[How the target is regulated]

---

## 7. Model Organism Evidence
*[MANDATORY]*

### 7.1 Mouse Models
[Knockout/knockin phenotypes, if any]

### 7.2 Other Model Organisms
[Yeast, fly, zebrafish, worm data if relevant]

### 7.3 Cross-Species Conservation
[Conservation and functional studies]

---

## 8. Human Genetics & Variants
*[MANDATORY]*

### 8.1 Constraint Scores
[pLI, LOEUF, missense Z - with interpretation]

### 8.2 Disease-Associated Variants
[ClinVar pathogenic variants]

### 8.3 Population Variants
[gnomAD notable variants]

### 8.4 GWAS Associations
[Any GWAS hits for the locus]

---

## 9. Disease Links
*[MANDATORY - include evidence strength]*

### 9.1 Strong Evidence (Genetic + Functional)
[Diseases with causal evidence]

### 9.2 Moderate Evidence (Association + Mechanism)
[Diseases with supporting evidence]

### 9.3 Weak Evidence (Association Only)
[Diseases with correlation/association only]

### 9.4 Evidence Summary Table

| Disease | Evidence Type | Score | Key Papers | Grade |
|---------|---------------|-------|------------|-------|
| [Disease 1] | Genetic + Functional | 0.85 | PMID:xxx | ★★★ |
| [Disease 2] | GWAS + Expression | 0.45 | PMID:yyy | ★★☆ |

---

## 10. Pathogen Involvement
*[MANDATORY - state "None identified" if not applicable]*

### 10.1 Viral Interactions
[Any viral exploitation or targeting]

### 10.2 Bacterial Interactions
[Any bacterial relevance]

### 10.3 Host Defense Role
[Role in immune response if any]

---

## 11. Key Assays & Readouts
*[MANDATORY]*

### 11.1 Biochemical Assays
[Available assays for target activity]

### 11.2 Cellular Readouts
[Cell-based assays and phenotypes]

### 11.3 In Vivo Models
[Animal models and endpoints]

---

## 12. Research Themes
*[MANDATORY - structured theme extraction]*

### 12.1 [Theme 1 Name] (N papers)
**Evidence Quality**: [Strong/Moderate/Limited]
**Representative Papers**: [≥3 papers or state "insufficient"]

[Theme description with evidence-graded citations]

### 12.2 [Theme 2 Name] (N papers)
[Same structure]

[Continue for all themes - require ≥3 representative papers per theme, or state "limited evidence"]

---

## 13. Open Questions & Research Gaps
*[MANDATORY]*

### 13.1 Mechanistic Unknowns
[What we don't understand about the target]

### 13.2 Therapeutic Unknowns
[What we don't know for drug development]

### 13.3 Suggested Priority Questions
[Ranked list of important unanswered questions]

---

## 14. Biological Model & Testable Hypotheses
*[MANDATORY - synthesis section]*

### 14.1 Integrated Biological Model
[3-5 paragraph synthesis integrating all evidence into coherent model]

### 14.2 Testable Hypotheses

| # | Hypothesis | Perturbation | Readout | Expected Result | Priority |
|---|------------|--------------|---------|-----------------|----------|
| 1 | [Hypothesis] | [Experiment] | [Measure] | [Prediction] | HIGH |
| 2 | [Hypothesis] | [Experiment] | [Measure] | [Prediction] | HIGH |
| 3 | [Hypothesis] | [Experiment] | [Measure] | [Prediction] | MEDIUM |

### 14.3 Suggested Experiments
[Brief description of key experiments to test hypotheses]

---

## 15. Conclusions & Recommendations
*[MANDATORY]*

### 15.1 Key Takeaways
[Bullet points of most important findings]

### 15.2 Confidence Assessment
[Overall confidence in the findings: High/Medium/Low with justification]

### 15.3 Recommended Next Steps
[Prioritized action items]

---

## References

*[Summary reference list in report - full bibliography in separate file]*

### Key Papers (Must-Read)
1. [Citation with PMID] - [Why important] [Grade: ★★★]
2. ...

### By Theme
[Organized reference lists]

---

## Data Limitations

- [Any databases that failed or returned no data]
- [Any known gaps in coverage]
- [OA status method used]

*Full methodology available in methods_appendix.md upon request.*
```

---

## Bibliography File Format

**File**: `[topic]_bibliography.json`

```json
{
  "metadata": {
    "generated": "2026-02-04",
    "query": "ATP6V1A",
    "total_papers": 342,
    "unique_after_dedup": 287
  },
  "papers": [
    {
      "pmid": "12345678",
      "doi": "10.1038/xxx",
      "title": "Paper Title",
      "authors": ["Smith A", "Jones B"],
      "year": 2024,
      "journal": "Nature",
      "source_databases": ["PubMed", "OpenAlex"],
      "evidence_tier": "T1",
      "themes": ["lysosomal_acidification", "autophagy"],
      "oa_status": "gold",
      "oa_url": "https://...",
      "citation_count": 45,
      "in_core_set": true
    }
  ]
}
```

Also generate `[topic]_bibliography.csv` with same data in tabular format.

---

## Theme Extraction Protocol

### Standardized Theme Clustering

1. **Extract keywords** from titles and abstracts
2. **Cluster into themes** using semantic similarity
3. **Require minimum N papers** per theme (default N=3)
4. **Label themes** with standardized names

### Standard Theme Categories (adapt to target)

For V-ATPase target example:
- `lysosomal_acidification` - Core function
- `autophagy_regulation` - mTORC1 signaling
- `bone_resorption` - Osteoclast function
- `cancer_metabolism` - Tumor acidification
- `viral_infection` - Viral entry mechanism
- `neurodegenerative` - Neuronal dysfunction
- `kidney_function` - Renal acid-base
- `methodology` - Assays/tools papers

### Theme Quality Requirements

| Papers | Theme Status |
|--------|--------------|
| ≥10 | Major theme (full section) |
| 3-9 | Minor theme (subsection) |
| <3 | Insufficient (note in "limited evidence" or merge) |

---

## Completeness Checklist (Verify Before Delivery)

**ALL boxes must be checked or explicitly marked "N/A" or "Limited evidence"**

### Identity & Context
- [ ] Official identifiers resolved (UniProt, Ensembl, NCBI, ChEMBL)
- [ ] All synonyms/aliases documented
- [ ] Naming collisions identified and handled
- [ ] Protein architecture described (or N/A stated)
- [ ] Subcellular localization documented
- [ ] Baseline expression profile included

### Mechanism & Function
- [ ] Core mechanism section with evidence grades
- [ ] Pathway involvement documented
- [ ] Model organism evidence (or "none found")
- [ ] Complexes/interaction partners listed
- [ ] Key assays/readouts described

### Disease & Clinical
- [ ] Human genetic variants documented
- [ ] Constraint scores with interpretation
- [ ] Disease links with evidence strength grades
- [ ] Pathogen involvement (or "none identified")

### Synthesis
- [ ] Research themes clustered with ≥3 papers each (or noted as limited)
- [ ] Open questions/gaps articulated
- [ ] Biological model synthesized
- [ ] ≥3 testable hypotheses with experiments
- [ ] Conclusions with confidence assessment

### Technical
- [ ] All claims have source attribution
- [ ] Evidence grades applied throughout
- [ ] Bibliography file generated
- [ ] Data limitations documented

---

## Quick Reference: Tool Categories

### Literature Tools
`PubMed_search_articles`, `PMC_search_papers`, `EuropePMC_search_articles`, `openalex_literature_search`, `Crossref_search_works`, `SemanticScholar_search_papers`, `BioRxiv_search_preprints`, `MedRxiv_search_preprints`

### Citation Tools
`PubMed_get_cited_by`, `PubMed_get_related`, `EuropePMC_get_citations`, `EuropePMC_get_references`

### Protein/Gene Annotation Tools
`UniProt_get_entry_by_accession`, `UniProt_search`, `UniProt_id_mapping`, `InterPro_get_protein_domains`, `proteins_api_get_protein`

### Expression Tools
`GTEx_get_median_gene_expression`, `GTEx_get_gene_expression`, `HPA_get_rna_expression_by_source`, `HPA_get_comprehensive_gene_details_by_ensembl_id`, `HPA_get_subcellular_location`

### Variant/Disease Tools
`gnomad_get_gene_constraints`, `gnomad_get_gene`, `clinvar_search_variants`, `OpenTargets_get_diseases_phenotypes_by_target_ensembl`

### Pathway Tools
`GO_get_annotations_for_gene`, `Reactome_map_uniprot_to_pathways`, `kegg_get_gene_info`, `OpenTargets_get_target_gene_ontology_by_ensemblID`

### Interaction Tools
`STRING_get_protein_interactions`, `intact_get_interactions`, `OpenTargets_get_target_interactions_by_ensemblID`

### OA Tools
`Unpaywall_check_oa_status` (if email provided), or use OA flags from Europe PMC/OpenAlex

---

## Communication with User

**During research** (brief updates):
- "Resolving target identifiers and gathering baseline profile..."
- "Building core paper set with high-precision queries..."
- "Expanding via citation network..."
- "Clustering into themes and grading evidence..."

**When the question looks like a factoid**:
- Ask (once) if the user wants *just the verified answer* or a *full deep-research report*.
- If the user doesn’t specify, default to **Factoid / Verification Mode** and keep it short + source-backed.

**DO NOT** expose:
- Raw tool outputs
- Deduplication counts
- Search round details
- Database-by-database results

**The report is the deliverable. Methodology stays internal.**

---

## Summary

This skill produces comprehensive, evidence-graded research reports that:

1. **Start with disambiguation** to prevent naming collisions and missing details
2. **Use annotation tools** to fill gaps when literature is sparse
3. **Grade all evidence** to separate signal from noise
4. **Require completeness** even if stating "limited evidence"
5. **Synthesize into biological models** with testable hypotheses
6. **Separate narrative from bibliography** for scalability
7. **Keep methodology internal** unless explicitly requested

The result is a detailed, actionable research report that reads like an expert synthesis, not a search log.
