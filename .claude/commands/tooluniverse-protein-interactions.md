# protein-interaction-network-analysis

> Analyze protein-protein interaction networks using STRING, BioGRID, and SASBDB databases. Maps protein identifiers, retrieves interaction networks with confidence scores, performs functional enrichment analysis (GO/KEGG/Reactome), and optionally includes structural data. No API key required for core functionality (STRING). Use when analyzing protein networks, discovering interaction partners, identifying functional modules, or studying protein complexes.

# Protein Interaction Network Analysis

Comprehensive protein interaction network analysis using ToolUniverse tools. Analyzes protein networks through a 4-phase workflow: identifier mapping, network retrieval, enrichment analysis, and optional structural data.

## Features

✅ **Identifier Mapping** - Convert protein names to database IDs (STRING, UniProt, Ensembl)
✅ **Network Retrieval** - Get interaction networks with confidence scores (0-1.0)
✅ **Functional Enrichment** - GO terms, KEGG pathways, Reactome pathways
✅ **PPI Enrichment** - Test if proteins form functional modules
✅ **Structural Data** - Optional SAXS/SANS solution structures (SASBDB)
✅ **Fallback Strategy** - STRING primary (no API key) → BioGRID secondary (if key available)

## Databases Used

| Database | Coverage | API Key | Purpose |
|----------|----------|---------|---------|
| **STRING** | 14M+ proteins, 5,000+ organisms | ❌ Not required | Primary interaction source |
| **BioGRID** | 2.3M+ interactions, 80+ organisms | ✅ Required | Fallback, curated data |
| **SASBDB** | 2,000+ SAXS/SANS entries | ❌ Not required | Solution structures |

## Quick Start

### Basic Usage

```python
from tooluniverse import ToolUniverse
from python_implementation import analyze_protein_network

# Initialize ToolUniverse
tu = ToolUniverse()

# Analyze protein network
result = analyze_protein_network(
    tu=tu,
    proteins=["TP53", "MDM2", "ATM", "CHEK2"],
    species=9606,  # Human
    confidence_score=0.7  # High confidence
)

# Access results
print(f"Mapped: {len(result.mapped_proteins)} proteins")
print(f"Network: {result.total_interactions} interactions")
print(f"Enrichment: {len(result.enriched_terms)} GO terms")
print(f"PPI p-value: {result.ppi_enrichment.get('p_value', 1.0):.2e}")
```

### Expected Output

```
🔍 Phase 1: Mapping 4 protein identifiers...
✅ Mapped 4/4 proteins (100.0%)

🕸️  Phase 2: Retrieving interaction network...
✅ STRING: Retrieved 6 interactions

🧬 Phase 3: Performing enrichment analysis...
✅ Found 245 enriched GO terms (FDR < 0.05)
✅ PPI enrichment significant (p=3.45e-05)

✅ Analysis complete!
```

## Use Cases

### 1. Single Protein Analysis

Discover interaction partners for a protein of interest:

```python
result = analyze_protein_network(
    tu=tu,
    proteins=["TP53"],  # Single protein
    species=9606,
    confidence_score=0.7
)

# Top 5 partners will be in the network
for edge in result.network_edges[:5]:
    print(f"{edge['preferredName_A']} ↔ {edge['preferredName_B']} "
          f"(score: {edge['score']})")
```

### 2. Protein Complex Validation

Test if proteins form a functional complex:

```python
# DNA damage response proteins
proteins = ["TP53", "ATM", "CHEK2", "BRCA1", "BRCA2"]

result = analyze_protein_network(tu=tu, proteins=proteins)

# Check PPI enrichment
if result.ppi_enrichment.get("p_value", 1.0) < 0.05:
    print("✅ Proteins form functional module!")
    print(f"   Expected edges: {result.ppi_enrichment['expected_number_of_edges']:.1f}")
    print(f"   Observed edges: {result.ppi_enrichment['number_of_edges']}")
else:
    print("⚠️  Proteins may be unrelated")
```

### 3. Pathway Discovery

Find enriched pathways for a protein set:

```python
result = analyze_protein_network(
    tu=tu,
    proteins=["MAPK1", "MAPK3", "RAF1", "MAP2K1"],  # MAPK pathway
    confidence_score=0.7
)

# Show top enriched processes
print("\nTop Enriched Pathways:")
for term in result.enriched_terms[:10]:
    print(f"  {term['term']}: p={term['p_value']:.2e}, FDR={term['fdr']:.2e}")
```

### 4. Multi-Protein Network Analysis

Build complete interaction network for multiple proteins:

```python
# Apoptosis regulators
proteins = ["TP53", "BCL2", "BAX", "CASP3", "CASP9"]

result = analyze_protein_network(
    tu=tu,
    proteins=proteins,
    confidence_score=0.7
)

# Export network for Cytoscape
import pandas as pd
df = pd.DataFrame(result.network_edges)
df.to_csv("apoptosis_network.tsv", sep="\t", index=False)
```

### 5. With BioGRID Validation

Use BioGRID for experimentally validated interactions:

```python
# Requires BIOGRID_API_KEY in environment
result = analyze_protein_network(
    tu=tu,
    proteins=["TP53", "MDM2"],
    include_biogrid=True  # Enable BioGRID fallback
)

print(f"Primary source: {result.primary_source}")  # "STRING" or "BioGRID"
```

### 6. Including Structural Data

Add SAXS/SANS solution structures:

```python
result = analyze_protein_network(
    tu=tu,
    proteins=["TP53"],
    include_structure=True  # Query SASBDB
)

if result.structural_data:
    print(f"\nFound {len(result.structural_data)} SAXS/SANS entries:")
    for entry in result.structural_data:
        print(f"  {entry.get('sasbdb_id')}: {entry.get('title')}")
```

## Parameters

### `analyze_protein_network()` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tu` | ToolUniverse | Required | ToolUniverse instance |
| `proteins` | list[str] | Required | Protein identifiers (gene symbols, UniProt IDs) |
| `species` | int | 9606 | NCBI taxonomy ID (9606=human, 10090=mouse) |
| `confidence_score` | float | 0.7 | Min interaction confidence (0-1). 0.4=low, 0.7=high, 0.9=very high |
| `include_biogrid` | bool | False | Use BioGRID if STRING fails (requires API key) |
| `include_structure` | bool | False | Include SASBDB structural data (slower) |
| `suppress_warnings` | bool | True | Suppress ToolUniverse loading warnings |

### Species IDs (Common)

- `9606` - Homo sapiens (human)
- `10090` - Mus musculus (mouse)
- `10116` - Rattus norvegicus (rat)
- `7227` - Drosophila melanogaster (fruit fly)
- `6239` - Caenorhabditis elegans (worm)
- `7955` - Danio rerio (zebrafish)
- `559292` - Saccharomyces cerevisiae (yeast)

### Confidence Score Guidelines

| Score | Level | Description | Use Case |
|-------|-------|-------------|----------|
| 0.15 | Very low | All evidence | Exploratory, hypothesis generation |
| 0.4 | Low | Medium evidence | Default STRING threshold |
| 0.7 | High | Strong evidence | **Recommended** - reliable interactions |
| 0.9 | Very high | Strongest evidence | Core interactions only |

## Results Structure

### `ProteinNetworkResult` Object

```python
@dataclass
class ProteinNetworkResult:
    # Phase 1: Identifier mapping
    mapped_proteins: List[Dict[str, Any]]
    mapping_success_rate: float

    # Phase 2: Network retrieval
    network_edges: List[Dict[str, Any]]
    total_interactions: int

    # Phase 3: Enrichment analysis
    enriched_terms: List[Dict[str, Any]]
    ppi_enrichment: Dict[str, Any]

    # Phase 4: Structural data (optional)
    structural_data: Optional[List[Dict[str, Any]]]

    # Metadata
    primary_source: str  # "STRING" or "BioGRID"
    warnings: List[str]
```

### Network Edge Format (STRING)

```python
{
    "stringId_A": "9606.ENSP00000269305",  # Protein A STRING ID
    "stringId_B": "9606.ENSP00000258149",  # Protein B STRING ID
    "preferredName_A": "TP53",             # Protein A name
    "preferredName_B": "MDM2",             # Protein B name
    "ncbiTaxonId": 9606,                   # Species
    "score": 0.999,                        # Combined confidence (0-1)
    "nscore": 0.0,                         # Neighborhood score
    "fscore": 0.0,                         # Gene fusion score
    "pscore": 0.0,                         # Phylogenetic profile score
    "ascore": 0.947,                       # Coexpression score
    "escore": 0.951,                       # Experimental score
    "dscore": 0.9,                         # Database score
    "tscore": 0.994                        # Text mining score
}
```

### Enrichment Term Format

```python
{
    "category": "Process",                  # GO category
    "term": "GO:0006915",                   # GO term ID
    "description": "apoptotic process",     # Term description
    "number_of_genes": 4,                   # Genes in your set
    "number_of_genes_in_background": 1234, # Genes in genome
    "p_value": 1.23e-05,                    # Enrichment p-value
    "fdr": 0.0012,                          # FDR correction
    "inputGenes": "TP53,MDM2,BAX,CASP3"    # Matching genes
}
```

## Workflow Details

### 4-Phase Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Identifier Mapping                                 │
│ ─────────────────────────────────────────────────────────── │
│ STRING_map_identifiers()                                    │
│   • Validates protein names exist in database              │
│   • Converts to STRING IDs for consistency                 │
│   • Returns mapping success rate                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Network Retrieval                                  │
│ ─────────────────────────────────────────────────────────── │
│ PRIMARY: STRING_get_network() (no API key needed)          │
│   • Retrieves all pairwise interactions                    │
│   • Returns confidence scores by evidence type             │
│                                                             │
│ FALLBACK: BioGRID_get_interactions() (if enabled)          │
│   • Used if STRING fails or for validation                 │
│   • Requires BIOGRID_API_KEY                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Enrichment Analysis                                │
│ ─────────────────────────────────────────────────────────── │
│ STRING_functional_enrichment()                              │
│   • GO terms (Process, Component, Function)                │
│   • KEGG pathways                                           │
│   • Reactome pathways                                       │
│   • FDR-corrected p-values                                  │
│                                                             │
│ STRING_ppi_enrichment()                                     │
│   • Tests if proteins interact more than random            │
│   • Returns p-value for functional coherence               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Structural Data (Optional)                         │
│ ─────────────────────────────────────────────────────────── │
│ SASBDB_search_entries()                                     │
│   • SAXS/SANS solution structures                           │
│   • Protein flexibility and conformations                   │
│   • Complements crystal/cryo-EM data                       │
└─────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Prerequisites

```bash
# Install ToolUniverse (if not already installed)
pip install tooluniverse

# Or with extras
pip install tooluniverse[all]
```

### Optional: BioGRID API Key

For BioGRID fallback functionality:

1. Register for free API key: https://webservice.thebiogrid.org/
2. Add to `.env` file:
   ```bash
   BIOGRID_API_KEY=your_key_here
   ```

### Skill Files

```
tooluniverse-protein-interactions/
├── SKILL.md                    # This file
├── python_implementation.py    # Main implementation
├── QUICK_START.md             # Quick reference
├── DOMAIN_ANALYSIS.md         # Design rationale
├── PHASE2_COMPLETE.md         # Tool testing results
├── PHASE4_IMPLEMENTATION_COMPLETE.md
└── KNOWN_ISSUES.md            # ToolUniverse limitations
```

## Known Limitations

### 1. ToolUniverse Verbose Output

**Issue**: ToolUniverse prints 40+ warning messages during analysis.

**Workaround**: Filter output when running:
```bash
python your_script.py 2>&1 | grep -v "Error loading tools"
```

See `KNOWN_ISSUES.md` for details.

### 2. BioGRID Requires API Key

BioGRID fallback requires free API key. STRING works without any API key.

### 3. SASBDB May Have API Issues

SASBDB endpoints occasionally return errors. Structural data is optional.

## Performance

### Typical Execution Times

| Operation | Time | Notes |
|-----------|------|-------|
| Identifier mapping | 1-2 sec | For 5 proteins |
| Network retrieval | 2-3 sec | Depends on network size |
| Enrichment analysis | 3-5 sec | For 374 terms |
| Full 4-phase analysis | 6-10 sec | Excluding ToolUniverse overhead |

**Note**: Add 4-8 seconds per tool call for ToolUniverse loading (framework limitation).

### Optimization Tips

1. **Disable structural data** if not needed: `include_structure=False`
2. **Use higher confidence scores** to reduce network size: `confidence_score=0.9`
3. **Filter output** to avoid processing warning messages
4. **Reuse ToolUniverse instance** across multiple analyses

## Troubleshooting

### "Error: 'protein_ids' is a required property"

✅ **Fixed in this skill** - All parameter names verified in Phase 2 testing.

### No interactions found

- Check protein names are correct (case-sensitive)
- Try lower confidence score: `confidence_score=0.4`
- Verify species ID is correct
- Check if proteins actually interact (not all proteins have known interactions)

### BioGRID not working

- Ensure `BIOGRID_API_KEY` is set in environment
- Check API key is valid at https://webservice.thebiogrid.org/
- BioGRID is optional - STRING works without it

### Slow performance

- This is expected (see KNOWN_ISSUES.md)
- ToolUniverse framework reloads tools on every call
- Use output filtering to reduce processing time

## Examples

See `python_implementation.py` for:
- `example_tp53_analysis()` - Complete TP53 network analysis
- `analyze_protein_network()` - Main function with all options
- `ProteinNetworkResult` - Result data structure

## References

- **STRING**: https://string-db.org/ (14M+ proteins, 5,000+ organisms)
- **BioGRID**: https://thebiogrid.org/ (2.3M+ interactions, experimentally validated)
- **SASBDB**: https://www.sasbdb.org/ (2,000+ SAXS/SANS entries)
- **ToolUniverse**: https://github.com/mims-harvard/ToolUniverse

## Support

For issues with:
- **This skill**: Check KNOWN_ISSUES.md and troubleshooting section
- **ToolUniverse framework**: See TOOLUNIVERSE_BUG_REPORT.md
- **API errors**: Check database status pages (STRING, BioGRID, SASBDB)

## License

Same as ToolUniverse framework license.
