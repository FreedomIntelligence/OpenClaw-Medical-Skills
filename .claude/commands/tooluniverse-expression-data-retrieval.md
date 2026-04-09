# tooluniverse-expression-data-retrieval

> Retrieves gene expression and omics datasets from ArrayExpress and BioStudies with gene disambiguation, experiment quality assessment, and structured reports. Creates comprehensive dataset profiles with metadata, sample information, and download links. Use when users need expression data, omics datasets, or mention ArrayExpress (E-MTAB, E-GEOD) or BioStudies (S-BSST) accessions.

# Gene Expression & Omics Data Retrieval

Retrieve gene expression experiments and multi-omics datasets with proper disambiguation and quality assessment.

**IMPORTANT**: Always use English terms in tool calls (gene names, tissue names, condition descriptions), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Workflow Overview

```
Phase 0: Clarify Query (if ambiguous)
    ↓
Phase 1: Disambiguate Gene/Condition
    ↓
Phase 2: Search & Retrieve (Internal)
    ↓
Phase 3: Report Dataset Profile
```

---

## Phase 0: Clarification (When Needed)

Ask the user ONLY if:
- Gene name is ambiguous (e.g., "p53" → TP53 or MDM2 studies?)
- Tissue/condition unclear for comparative studies
- Organism not specified for non-human research

Skip clarification for:
- Specific accession numbers (E-MTAB-*, E-GEOD-*, S-BSST*)
- Clear disease/tissue + organism combinations
- Explicit platform requests (RNA-seq, microarray)

---

## Phase 1: Query Disambiguation

### 1.1 Gene Name Resolution

If searching by gene, first resolve official identifiers:

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# For gene-focused searches, resolve official symbol first
# This helps construct better search queries
# Example: "p53" → "TP53" (official HGNC symbol)
```

**Gene Disambiguation Checklist:**
- [ ] Official gene symbol identified (HGNC for human, MGI for mouse)
- [ ] Common aliases noted for search expansion
- [ ] Species confirmed

### 1.2 Construct Search Strategy

| User Query Type | Search Strategy |
|-----------------|-----------------|
| Specific accession | Direct retrieval |
| Gene + condition | "[gene] [condition]" + species filter |
| Disease only | "[disease]" + species filter |
| Technology-specific | Add platform keywords (RNA-seq, microarray) |

---

## Phase 2: Data Retrieval (Internal)

Search silently. Do NOT narrate the process.

### 2.1 Search Experiments

```python
# ArrayExpress search
result = tu.tools.arrayexpress_search_experiments(
    keywords="[gene/disease] [condition]",
    species="[species]",
    limit=20
)

# BioStudies for multi-omics
biostudies_result = tu.tools.biostudies_search_studies(
    query="[keywords]",
    limit=10
)
```

### 2.2 Get Experiment Details

For top results, retrieve full metadata:

```python
# Get details for each relevant experiment
details = tu.tools.arrayexpress_get_experiment_details(
    accession=accession
)

# Get sample information
samples = tu.tools.arrayexpress_get_experiment_samples(
    accession=accession
)

# Get available files
files = tu.tools.arrayexpress_get_experiment_files(
    accession=accession
)
```

### 2.3 BioStudies Retrieval

```python
# Multi-omics study details
study_details = tu.tools.biostudies_get_study_details(
    accession=study_accession
)

# Study structure
sections = tu.tools.biostudies_get_study_sections(
    accession=study_accession
)

# Available files
files = tu.tools.biostudies_get_study_files(
    accession=study_accession
)
```

### Fallback Chains

| Primary | Fallback | Notes |
|---------|----------|-------|
| ArrayExpress search | BioStudies search | ArrayExpress empty |
| arrayexpress_get_experiment_details | biostudies_get_study_details | E-GEOD may have BioStudies mirror |
| arrayexpress_get_experiment_files | Note "Files unavailable" | Some studies restrict downloads |

---

## Phase 3: Report Dataset Profile

### Output Structure

Present as a **Dataset Search Report**. Hide search process.

```markdown
# Expression Data: [Query Topic]

**Search Summary**
- Query: [gene/disease] in [species]
- Databases: ArrayExpress, BioStudies
- Results: [N] relevant experiments found

**Data Quality Overview**: [assessment based on criteria below]

---

## Top Experiments

### 1. [E-MTAB-XXXX]: [Title]

| Attribute | Value |
|-----------|-------|
| **Accession** | [accession with link] |
| **Organism** | [species] |
| **Experiment Type** | RNA-seq / Microarray |
| **Platform** | [specific platform] |
| **Samples** | [N] samples |
| **Release Date** | [date] |

**Description**: [Brief description from metadata]

**Experimental Design**:
- Conditions: [treatment vs control, etc.]
- Replicates: [N biological, M technical]
- Tissue/Cell type: [if specified]

**Sample Groups**:
| Group | Samples | Description |
|-------|---------|-------------|
| Control | [N] | [description] |
| Treatment | [N] | [description] |

**Data Files Available**:
| File | Type | Size |
|------|------|------|
| [filename] | Processed data | [size] |
| [filename] | Raw data | [size] |
| [filename] | Sample metadata | [size] |

**Quality Assessment**: ●●● High / ●●○ Medium / ●○○ Low
- Sample size: [adequate/limited]
- Replication: [yes/no]
- Metadata completeness: [complete/partial]

---

### 2. [E-GEOD-XXXXX]: [Title]
[Same structure as above]

---

## Multi-Omics Studies (from BioStudies)

### [S-BSST-XXXXX]: [Title]

| Attribute | Value |
|-----------|-------|
| **Accession** | [accession] |
| **Study Type** | [proteomics/metabolomics/integrated] |
| **Organism** | [species] |
| **Samples** | [N] |

**Data Types Included**:
- [ ] Transcriptomics
- [ ] Proteomics
- [ ] Metabolomics
- [ ] Other: [specify]

---

## Summary Table

| Accession | Type | Samples | Platform | Quality |
|-----------|------|---------|----------|---------|
| [E-MTAB-X] | RNA-seq | [N] | Illumina | ●●● |
| [E-GEOD-X] | Microarray | [N] | Affymetrix | ●●○ |

---

## Recommendations

**For [specific analysis type]**:
- Best experiment: [accession] - [reason]
- Alternative: [accession] - [reason]

**Data Integration Notes**:
- Platform compatibility: [notes on combining datasets]
- Batch considerations: [if applicable]

---

## Data Access

### Direct Download Links
- [E-MTAB-XXXX processed data](link)
- [E-MTAB-XXXX raw data](link)

### Database Links
- ArrayExpress: https://www.ebi.ac.uk/arrayexpress/experiments/[accession]
- BioStudies: https://www.ebi.ac.uk/biostudies/studies/[accession]

Retrieved: [date]
```

---

## Data Quality Tiers

Assessment criteria for expression experiments:

| Tier | Symbol | Criteria |
|------|--------|----------|
| High Quality | ●●● | ≥3 bio replicates, complete metadata, processed data available |
| Medium Quality | ●●○ | 2-3 replicates OR some metadata gaps, data accessible |
| Low Quality | ●○○ | No replicates, sparse metadata, or data access issues |
| Use with Caution | ○○○ | Single sample, no replication, outdated platform |

Include assessment rationale:
```markdown
**Quality**: ●●● High
- ✓ 4 biological replicates per condition
- ✓ Complete sample annotations
- ✓ Processed and raw data available
- ✓ Recent RNA-seq platform
```

---

## Completeness Checklist

Every dataset report MUST include:

### Per Experiment (Required)
- [ ] Accession number with database link
- [ ] Organism
- [ ] Experiment type (RNA-seq/microarray/etc.)
- [ ] Sample count
- [ ] Brief description
- [ ] Quality assessment

### Search Summary (Required)
- [ ] Query parameters stated
- [ ] Number of results
- [ ] Databases searched

### Recommendations (Required)
- [ ] Best dataset for user's purpose (or "No suitable data found")
- [ ] Data access notes

### Include Even If Empty
- [ ] Multi-omics studies section (or "No multi-omics studies found")
- [ ] Data integration notes (or "Single-platform data, no integration needed")

---

## Common Use Cases

### Disease Gene Expression
User: "Find breast cancer RNA-seq data"
```python
result = tu.tools.arrayexpress_search_experiments(
    keywords="breast cancer RNA-seq",
    species="Homo sapiens",
    limit=20
)
```
→ Report top experiments with quality assessment

### Gene-Specific Studies
User: "Find TP53 expression experiments in mouse"
```python
result = tu.tools.arrayexpress_search_experiments(
    keywords="TP53 p53",  # Include aliases
    species="Mus musculus",
    limit=15
)
```
→ Report experiments studying this gene

### Specific Accession Lookup
User: "Get details for E-MTAB-5214"
→ Single experiment profile with all details and files

### Multi-Omics Integration
User: "Find proteomics and transcriptomics studies for liver disease"
→ Search both ArrayExpress and BioStudies, note integration potential

---

## Error Handling

| Error | Response |
|-------|----------|
| "No experiments found" | Broaden keywords, remove species filter, try synonyms |
| "Accession not found" | Verify format (E-MTAB-*, E-GEOD-*, S-BSST*), check if withdrawn |
| "Files not available" | Note in report: "Data files restricted by submitter" |
| "API timeout" | Retry once, then note: "(metadata retrieval incomplete)" |

---

## Tool Reference

**ArrayExpress (Gene Expression)**
| Tool | Purpose |
|------|---------|
| `arrayexpress_search_experiments` | Keyword/species search |
| `arrayexpress_get_experiment_details` | Full metadata |
| `arrayexpress_get_experiment_files` | Download links |
| `arrayexpress_get_experiment_samples` | Sample annotations |

**BioStudies (Multi-Omics)**
| Tool | Purpose |
|------|---------|
| `biostudies_search_studies` | Multi-omics search |
| `biostudies_get_study_details` | Study metadata |
| `biostudies_get_study_files` | Data files |
| `biostudies_get_study_sections` | Study structure |

---

## Search Parameters Reference

**ArrayExpress**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `keywords` | Free text search | "breast cancer RNA-seq" |
| `species` | Scientific name | "Homo sapiens" |
| `array` | Platform filter | "Illumina" |
| `limit` | Max results | 20 |

**BioStudies**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Free text | "proteomics liver" |
| `limit` | Max results | 10 |
