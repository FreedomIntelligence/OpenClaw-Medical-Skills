# tooluniverse-protein-structure-retrieval

> Retrieves protein structure data from RCSB PDB, PDBe, and AlphaFold with protein disambiguation, quality assessment, and comprehensive structural profiles. Creates detailed structure reports with experimental metadata, ligand information, and download links. Use when users need protein structures, 3D models, crystallography data, or mention PDB IDs (4-character codes like 1ABC) or UniProt accessions.

# Protein Structure Data Retrieval

Retrieve protein structures with proper disambiguation, quality assessment, and comprehensive metadata.

**IMPORTANT**: Always use English terms in tool calls (protein names, organism names), even if the user writes in another language. Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Workflow Overview

```
Phase 0: Clarify (if needed)
    ↓
Phase 1: Disambiguate Protein Identity
    ↓
Phase 2: Retrieve Structures (Internal)
    ↓
Phase 3: Report Structure Profile
```

---

## Phase 0: Clarification (When Needed)

Ask the user ONLY if:
- Protein name matches multiple genes/families (e.g., "kinase" → which kinase?)
- Organism not specified for conserved proteins
- Intent unclear: need experimental structure vs AlphaFold prediction?

Skip clarification for:
- Specific PDB IDs (4-character codes)
- UniProt accessions
- Unambiguous protein names with organism

---

## Phase 1: Protein Disambiguation

### 1.1 Resolve Protein Identity

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Strategy depends on input type
if user_provided_pdb_id:
    # Direct structure retrieval
    pdb_id = user_provided_pdb_id.upper()
    
elif user_provided_uniprot:
    # Get UniProt info, then search structures
    uniprot_id = user_provided_uniprot
    # Can also get AlphaFold structure
    af_structure = tu.tools.alphafold_get_structure_by_uniprot(
        uniprot_id=uniprot_id
    )
    
elif user_provided_protein_name:
    # Search by name
    result = tu.tools.search_structures_by_protein_name(
        protein_name=protein_name
    )
```

### 1.2 Identity Resolution Checklist

- [ ] Protein name/gene identified
- [ ] Organism confirmed
- [ ] UniProt accession (if available)
- [ ] Isoform/variant specified (if relevant)

### 1.3 Handle Naming Collisions

Common ambiguous terms:
| Term | Ambiguity | Resolution |
|------|-----------|------------|
| "kinase" | Hundreds of kinases | Ask which kinase (EGFR, CDK2, etc.) |
| "receptor" | Many receptor types | Specify receptor family |
| "protease" | Multiple families | Ask serine/cysteine/metallo/etc. |
| "hemoglobin" | Clear | Proceed (α/β chain specified if needed) |
| "insulin" | Clear | Proceed |

---

## Phase 2: Data Retrieval (Internal)

Retrieve all data silently. Do NOT narrate the search process.

### 2.1 Search Structures

```python
# Search by protein name
result = tu.tools.search_structures_by_protein_name(
    protein_name=protein_name
)

# Filter results by quality
high_res = [
    entry for entry in result["data"]
    if entry.get("resolution") and entry["resolution"] < 2.5
]
```

### 2.2 Get Structure Details

For each relevant structure:

```python
pdb_id = "4INS"

# Basic metadata
metadata = tu.tools.get_protein_metadata_by_pdb_id(pdb_id=pdb_id)

# Experimental details
exp_details = tu.tools.get_protein_experimental_details_by_pdb_id(
    pdb_id=pdb_id
)

# Resolution (if X-ray)
resolution = tu.tools.get_protein_resolution_by_pdb_id(pdb_id=pdb_id)

# Bound ligands
ligands = tu.tools.get_protein_ligands_by_pdb_id(pdb_id=pdb_id)

# Similar structures
similar = tu.tools.get_similar_structures_by_pdb_id(
    pdb_id=pdb_id,
    cutoff=2.0
)
```

### 2.3 PDBe Additional Data

```python
# Entry summary
summary = tu.tools.pdbe_get_entry_summary(pdb_id=pdb_id)

# Molecular entities
molecules = tu.tools.pdbe_get_molecules(pdb_id=pdb_id)

# Binding sites
binding_sites = tu.tools.pdbe_get_binding_sites(pdb_id=pdb_id)
```

### 2.4 AlphaFold Predictions

```python
# When no experimental structure exists, or for comparison
if uniprot_id:
    af_structure = tu.tools.alphafold_get_structure_by_uniprot(
        uniprot_id=uniprot_id
    )
```

### Fallback Chains

| Primary | Fallback | Notes |
|---------|----------|-------|
| RCSB search | PDBe search | Regional availability |
| get_protein_metadata | pdbe_get_entry_summary | Alternative source |
| Experimental structure | AlphaFold prediction | No experimental structure |
| get_protein_ligands | pdbe_get_binding_sites | Ligand info unavailable |

---

## Phase 3: Report Structure Profile

### Output Structure

Present as a **Structure Profile Report**. Hide search process.

```markdown
# Protein Structure Profile: [Protein Name]

**Search Summary**
- Query: [protein name/PDB ID]
- Organism: [species]
- Structures Found: [N] experimental, [M] AlphaFold

---

## Best Available Structure

### [PDB ID]: [Title]

| Attribute | Value |
|-----------|-------|
| **PDB ID** | [pdb_id] |
| **UniProt** | [uniprot_id] |
| **Organism** | [species] |
| **Method** | X-ray / Cryo-EM / NMR |
| **Resolution** | [X.XX] Å |
| **Release Date** | [date] |

**Quality Assessment**: ●●● High / ●●○ Medium / ●○○ Low

### Experimental Details
| Parameter | Value |
|-----------|-------|
| **Method** | [X-ray crystallography] |
| **Resolution** | [1.9 Å] |
| **R-factor** | [0.18] |
| **R-free** | [0.21] |
| **Space Group** | [P 21 21 21] |

### Structure Composition
| Component | Count | Details |
|-----------|-------|---------|
| **Chains** | [N] | [A (enzyme), B (inhibitor)] |
| **Residues** | [N] | [coverage %] |
| **Ligands** | [N] | [list ligand names] |
| **Waters** | [N] | |
| **Metals** | [N] | [Zn, Mg, etc.] |

### Bound Ligands
| Ligand ID | Name | Type | Binding Site |
|-----------|------|------|--------------|
| [ATP] | Adenosine triphosphate | Substrate | Active site |
| [MG] | Magnesium ion | Cofactor | Catalytic |

### Binding Site Details
For drug discovery applications:

**Site 1: Active Site**
- Location: Chain A, residues 45-89
- Key residues: Asp45, Glu67, His89
- Pocket volume: [X] Å³
- Druggability: High/Medium/Low

---

## Alternative Structures

Ranked by quality and relevance:

| Rank | PDB ID | Resolution | Method | Ligands | Notes |
|------|--------|------------|--------|---------|-------|
| 1 | [4INS] | 1.9 Å | X-ray | Zn | Best resolution |
| 2 | [3I40] | 2.1 Å | X-ray | Zn, phenol | With inhibitor |
| 3 | [1TRZ] | 2.3 Å | X-ray | None | Porcine |

---

## AlphaFold Prediction

### AF-[UniProt]-F1

| Attribute | Value |
|-----------|-------|
| **UniProt** | [uniprot_id] |
| **Model Version** | [v4] |
| **Confidence (pLDDT)** | [average score] |

**Confidence Distribution**:
- Very High (>90): [X]% of residues
- High (70-90): [X]% of residues
- Low (50-70): [X]% of residues
- Very Low (<50): [X]% of residues

**Use Cases**:
- ✓ Overall fold reliable
- ✓ Core domain structure
- ⚠ Loop regions uncertain
- ✗ Not suitable for binding site analysis

---

## Structure Comparison

| Property | [PDB_1] | [PDB_2] | AlphaFold |
|----------|---------|---------|-----------|
| Resolution | 1.9 Å | 2.5 Å | N/A (predicted) |
| Completeness | 98% | 85% | 100% |
| Ligands | Yes | No | No |
| Confidence | Experimental | Experimental | High (85 avg) |

---

## Download Links

### Coordinate Files
| Format | PDB ID | Link |
|--------|--------|------|
| PDB | [4INS] | [link] |
| mmCIF | [4INS] | [link] |
| AlphaFold | [UniProt] | [link] |

### Database Links
- RCSB PDB: https://www.rcsb.org/structure/[pdb_id]
- PDBe: https://www.ebi.ac.uk/pdbe/entry/pdb/[pdb_id]
- AlphaFold: https://alphafold.ebi.ac.uk/entry/[uniprot_id]

Retrieved: [date]
```

---

## Quality Assessment Tiers

### Experimental Structures

| Tier | Symbol | Criteria |
|------|--------|----------|
| Excellent | ●●●● | X-ray <1.5Å, complete, R-free <0.22 |
| High | ●●●○ | X-ray <2.0Å OR Cryo-EM <3.0Å |
| Good | ●●○○ | X-ray 2.0-3.0Å OR Cryo-EM 3.0-4.0Å |
| Moderate | ●○○○ | X-ray >3.0Å OR NMR ensemble |
| Low | ○○○○ | >4.0Å, incomplete, or problematic |

### Resolution Guide

| Resolution | Use Case |
|------------|----------|
| <1.5 Å | Atomic detail, H-bond analysis |
| 1.5-2.0 Å | Drug design, mechanism studies |
| 2.0-2.5 Å | Structure-based design |
| 2.5-3.5 Å | Overall architecture, fold |
| >3.5 Å | Domain arrangement only |

### AlphaFold Confidence

| pLDDT Score | Interpretation |
|-------------|----------------|
| >90 | Very high confidence, experimental-like |
| 70-90 | Good backbone confidence |
| 50-70 | Uncertain, flexible regions |
| <50 | Low confidence, likely disordered |

---

## Completeness Checklist

Every structure report MUST include:

### For Specific PDB ID (Required)
- [ ] PDB ID and title
- [ ] Experimental method
- [ ] Resolution (or N/A for NMR)
- [ ] Organism
- [ ] Quality assessment
- [ ] Download links

### For Protein Name Search (Required)
- [ ] Search summary with result count
- [ ] Top structures with quality ranking
- [ ] Best structure recommendation
- [ ] AlphaFold alternative (if no experimental structure)

### Always Include
- [ ] Ligand information (or "No ligands bound")
- [ ] Data sources with links
- [ ] Retrieval date

---

## Common Use Cases

### Drug Discovery Target
User: "Get structure for EGFR kinase with inhibitor"
→ Filter for ligand-bound structures, emphasize binding site

### Model Building
User: "Find best template for homology modeling of protein X"
→ High-resolution structures, note sequence coverage

### Structure Comparison
User: "Compare available SARS-CoV-2 main protease structures"
→ All structures with systematic comparison table

### AlphaFold When No Experimental
User: "Structure of protein with UniProt P12345"
→ Check PDB first, then AlphaFold, note confidence

---

## Error Handling

| Error | Response |
|-------|----------|
| "PDB ID not found" | Verify 4-character format, check if obsoleted |
| "No structures for protein" | Offer AlphaFold prediction, suggest similar proteins |
| "Download failed" | Retry once, provide alternative link |
| "Resolution unavailable" | Likely NMR/model, note in assessment |

---

## Tool Reference

**RCSB PDB (Experimental Structures)**
| Tool | Purpose |
|------|---------|
| `search_structures_by_protein_name` | Name-based search |
| `get_protein_metadata_by_pdb_id` | Basic info |
| `get_protein_experimental_details_by_pdb_id` | Method details |
| `get_protein_resolution_by_pdb_id` | Quality metric |
| `get_protein_ligands_by_pdb_id` | Bound molecules |
| `download_pdb_structure_file` | Coordinate files |
| `get_similar_structures_by_pdb_id` | Homologs |

**PDBe (European PDB)**
| Tool | Purpose |
|------|---------|
| `pdbe_get_entry_summary` | Overview |
| `pdbe_get_molecules` | Molecular entities |
| `pdbe_get_experiment_info` | Experimental data |
| `pdbe_get_binding_sites` | Ligand pockets |

**AlphaFold (Predictions)**
| Tool | Purpose |
|------|---------|
| `alphafold_get_structure_by_uniprot` | Get prediction |
| `alphafold_search_structures` | Search predictions |
