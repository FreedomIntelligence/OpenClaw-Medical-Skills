# tooluniverse-sequence-retrieval

> Retrieves biological sequences (DNA, RNA, protein) from NCBI and ENA with gene disambiguation, accession type handling, and comprehensive sequence profiles. Creates detailed reports with sequence metadata, cross-database references, and download options. Use when users need nucleotide sequences, protein sequences, genome data, or mention GenBank, RefSeq, EMBL accessions.

# Biological Sequence Retrieval

Retrieve DNA, RNA, and protein sequences with proper disambiguation and cross-database handling.

**IMPORTANT**: Always use English terms in tool calls (gene names, organism names, sequence descriptions), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Workflow Overview

```
Phase 0: Clarify (if needed)
    ↓
Phase 1: Disambiguate Gene/Organism
    ↓
Phase 2: Search & Retrieve (Internal)
    ↓
Phase 3: Report Sequence Profile
```

---

## Phase 0: Clarification (When Needed)

Ask the user ONLY if:
- Gene name exists in multiple organisms (e.g., "BRCA1" → human or mouse?)
- Sequence type unclear (mRNA, genomic, protein?)
- Strain/isolate matters (e.g., E. coli → K-12, O157:H7, etc.)

Skip clarification for:
- Specific accession numbers (NC_*, NM_*, U*, etc.)
- Clear organism + gene combinations
- Complete genome requests with organism specified

---

## Phase 1: Gene/Organism Disambiguation

### 1.1 Resolve Identifiers

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Strategy depends on input type
if user_provided_accession:
    # Direct retrieval based on accession type
    accession = user_provided_accession
    
elif user_provided_gene_and_organism:
    # Search NCBI Nucleotide
    result = tu.tools.NCBI_search_nucleotide(
        operation="search",
        organism=organism,
        gene=gene,
        limit=10
    )
```

### 1.2 Accession Type Decision Tree

**CRITICAL**: Accession prefix determines which tools to use.

| Prefix | Type | Use With |
|--------|------|----------|
| NC_* | RefSeq chromosome | NCBI only |
| NM_* | RefSeq mRNA | NCBI only |
| NR_* | RefSeq ncRNA | NCBI only |
| NP_* | RefSeq protein | NCBI only |
| XM_* | RefSeq predicted mRNA | NCBI only |
| U*, M*, K*, X* | GenBank | NCBI or ENA |
| CP*, NZ_* | GenBank genome | NCBI or ENA |
| EMBL format | EMBL | ENA preferred |

### 1.3 Identity Resolution Checklist

- [ ] Organism confirmed (scientific name)
- [ ] Gene symbol/name identified
- [ ] Sequence type determined (genomic/mRNA/protein)
- [ ] Strain specified (if relevant)
- [ ] Accession prefix identified → tool selection

---

## Phase 2: Data Retrieval (Internal)

Retrieve silently. Do NOT narrate the search process.

### 2.1 Search for Sequences

```python
# Search NCBI Nucleotide
result = tu.tools.NCBI_search_nucleotide(
    operation="search",
    organism=organism,
    gene=gene,
    strain=strain,  # Optional
    keywords=keywords,  # Optional
    seq_type=seq_type,  # complete_genome, mrna, refseq
    limit=10
)

# Get accession numbers from UIDs
accessions = tu.tools.NCBI_fetch_accessions(
    operation="fetch_accession",
    uids=result["data"]["uids"]
)
```

### 2.2 Retrieve Sequence Data

```python
# Get sequence in desired format
sequence = tu.tools.NCBI_get_sequence(
    operation="fetch_sequence",
    accession=accession,
    format="fasta"  # or "genbank"
)

# GenBank format for annotations
annotations = tu.tools.NCBI_get_sequence(
    operation="fetch_sequence",
    accession=accession,
    format="genbank"
)
```

### 2.3 ENA Alternative (for GenBank/EMBL accessions)

```python
# Only for non-RefSeq accessions!
if not accession.startswith(("NC_", "NM_", "NR_", "NP_", "XM_", "XR_")):
    # ENA entry info
    entry = tu.tools.ena_get_entry(accession=accession)
    
    # ENA FASTA
    fasta = tu.tools.ena_get_sequence_fasta(accession=accession)
    
    # ENA summary
    summary = tu.tools.ena_get_entry_summary(accession=accession)
```

### Fallback Chains

| Primary | Fallback | Notes |
|---------|----------|-------|
| NCBI_get_sequence | ENA (if GenBank format) | NCBI unavailable |
| ENA_get_entry | NCBI_get_sequence | ENA doesn't have RefSeq |
| NCBI_search_nucleotide | Try broader keywords | No results |

**Critical Rule**: Never try ENA tools with RefSeq accessions (NC_, NM_, etc.) - they will return 404 errors.

---

## Phase 3: Report Sequence Profile

### Output Structure

Present as a **Sequence Profile Report**. Hide search process.

```markdown
# Sequence Profile: [Gene/Organism]

**Search Summary**
- Query: [gene] in [organism]
- Database: NCBI Nucleotide
- Results: [N] sequences found

---

## Primary Sequence

### [Accession]: [Definition/Title]

| Attribute | Value |
|-----------|-------|
| **Accession** | [accession] |
| **Type** | RefSeq / GenBank |
| **Organism** | [scientific name] |
| **Strain** | [strain if applicable] |
| **Length** | [X,XXX bp / aa] |
| **Molecule** | DNA / mRNA / Protein |
| **Topology** | Linear / Circular |

**Curation Level**: ●●● RefSeq (curated) / ●●○ GenBank (submitted) / ●○○ Third-party

### Sequence Statistics
| Statistic | Value |
|-----------|-------|
| **Length** | [X,XXX] bp |
| **GC Content** | [XX.X]% |
| **Genes** | [N] (if genome) |
| **CDS** | [N] (if annotated) |

### Sequence Preview
```fasta
>[accession] [definition]
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA
... [truncated, full sequence in download]
```

### Annotations Summary (from GenBank format)
| Feature | Count | Examples |
|---------|-------|----------|
| CDS | [N] | [gene names] |
| tRNA | [N] | - |
| rRNA | [N] | 16S, 23S |
| Regulatory | [N] | promoters |

---

## Alternative Sequences

Ranked by relevance and curation level:

| Accession | Type | Length | Description | ENA Compatible |
|-----------|------|--------|-------------|----------------|
| NC_000913.3 | RefSeq | 4.6 Mb | E. coli K-12 reference | ✗ |
| U00096.3 | GenBank | 4.6 Mb | E. coli K-12 | ✓ |
| CP001509.3 | GenBank | 4.6 Mb | E. coli DH10B | ✓ |

---

## Cross-Database References

| Database | Accession | Link |
|----------|-----------|------|
| RefSeq | [NC_*] | [NCBI link] |
| GenBank | [U*] | [NCBI link] |
| ENA/EMBL | [same as GenBank] | [ENA link] |
| BioProject | [PRJNA*] | [link] |
| BioSample | [SAMN*] | [link] |

---

## Download Options

### Formats Available
| Format | Description | Use Case |
|--------|-------------|----------|
| FASTA | Sequence only | BLAST, alignment |
| GenBank | Sequence + annotations | Gene analysis |
| GFF3 | Annotations only | Genome browsers |

### Direct Commands
```python
# FASTA format
tu.tools.NCBI_get_sequence(
    operation="fetch_sequence",
    accession="[accession]",
    format="fasta"
)

# GenBank format (with annotations)
tu.tools.NCBI_get_sequence(
    operation="fetch_sequence",
    accession="[accession]",
    format="genbank"
)
```

---

## Related Sequences

### Other Strains/Isolates
| Accession | Strain | Similarity | Notes |
|-----------|--------|------------|-------|
| [acc1] | [strain1] | 99.9% | [notes] |
| [acc2] | [strain2] | 99.5% | [notes] |

### Protein Products (if applicable)
| Protein Accession | Product Name | Length |
|-------------------|--------------|--------|
| [NP_*] | [protein name] | [X] aa |

---

Retrieved: [date]
Database: NCBI Nucleotide
```

---

## Curation Level Tiers

| Tier | Symbol | Accession Prefix | Description |
|------|--------|------------------|-------------|
| RefSeq Reference | ●●●● | NC_, NM_, NP_ | NCBI-curated, gold standard |
| RefSeq Predicted | ●●●○ | XM_, XP_, XR_ | Computationally predicted |
| GenBank Validated | ●●○○ | Various | Submitted, some curation |
| GenBank Direct | ●○○○ | Various | Direct submission |
| Third Party | ○○○○ | TPA_ | Third-party annotation |

Include in report:
```markdown
**Curation Level**: ●●●● RefSeq Reference
- Curated by NCBI RefSeq project
- Regular updates and validation
- Recommended for reference use
```

---

## Completeness Checklist

Every sequence report MUST include:

### Per Sequence (Required)
- [ ] Accession number
- [ ] Organism (scientific name)
- [ ] Sequence type (DNA/RNA/protein)
- [ ] Length
- [ ] Curation level
- [ ] Database source

### Search Summary (Required)
- [ ] Query parameters
- [ ] Number of results
- [ ] Ranking rationale

### Include Even If Limited
- [ ] Alternative sequences (or "Only one sequence found")
- [ ] Cross-database references (or "No cross-references available")
- [ ] Download instructions

---

## Common Use Cases

### Reference Genome
User: "Get E. coli K-12 complete genome"
```python
result = tu.tools.NCBI_search_nucleotide(
    operation="search",
    organism="Escherichia coli",
    strain="K-12",
    seq_type="complete_genome",
    limit=3
)
# Return NC_000913.3 (RefSeq reference)
```

### Gene Sequence
User: "Find human BRCA1 mRNA"
```python
result = tu.tools.NCBI_search_nucleotide(
    operation="search",
    organism="Homo sapiens",
    gene="BRCA1",
    seq_type="mrna",
    limit=10
)
```

### Specific Accession
User: "Get sequence for NC_045512.2"
→ Direct retrieval with full metadata

### Strain Comparison
User: "Compare E. coli K-12 and O157:H7 genomes"
→ Search both strains, provide comparison table

---

## Error Handling

| Error | Response |
|-------|----------|
| "No search criteria provided" | Add organism, gene, or keywords |
| "ENA 404 error" | Accession is likely RefSeq → use NCBI only |
| "No results found" | Broaden search, check spelling, try synonyms |
| "Sequence too large" | Note size, provide download link instead of preview |
| "API rate limit" | Tools auto-retry; if persistent, wait briefly |

---

## Tool Reference

**NCBI Tools (All Accessions)**
| Tool | Purpose |
|------|---------|
| `NCBI_search_nucleotide` | Search by gene/organism |
| `NCBI_fetch_accessions` | Convert UIDs to accessions |
| `NCBI_get_sequence` | Retrieve sequence data |

**ENA Tools (GenBank/EMBL Only)**
| Tool | Purpose |
|------|---------|
| `ena_get_entry` | Entry metadata |
| `ena_get_sequence_fasta` | FASTA sequence |
| `ena_get_entry_summary` | Summary info |

---

## Search Parameters Reference

**NCBI_search_nucleotide**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `operation` | Always "search" | "search" |
| `organism` | Scientific name | "Homo sapiens" |
| `gene` | Gene symbol | "BRCA1" |
| `strain` | Specific strain | "K-12" |
| `keywords` | Free text | "complete genome" |
| `seq_type` | Sequence type | "complete_genome", "mrna", "refseq" |
| `limit` | Max results | 10 |

**NCBI_get_sequence**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `operation` | Always "fetch_sequence" | "fetch_sequence" |
| `accession` | Accession number | "NC_000913.3" |
| `format` | Output format | "fasta", "genbank" |
