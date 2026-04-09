# tooluniverse-chemical-compound-retrieval

> Retrieves chemical compound information from PubChem and ChEMBL with disambiguation, cross-referencing, and quality assessment. Creates comprehensive compound profiles with identifiers, properties, bioactivity, and drug information. Use when users need chemical data, drug information, or mention PubChem CID, ChEMBL ID, SMILES, InChI, or compound names.

# Chemical Compound Information Retrieval

Retrieve comprehensive chemical compound data with proper disambiguation and cross-database validation.

**IMPORTANT**: Always use English compound names and search terms in tool calls, even if the user writes in another language (e.g., translate "阿司匹林" to "aspirin"). Only try original-language terms as a fallback if English returns no results. Respond in the user's language.

## Workflow Overview

```
Phase 0: Clarify (if needed)
    ↓
Phase 1: Disambiguate Compound Identity
    ↓
Phase 2: Retrieve Data (Internal)
    ↓
Phase 3: Report Compound Profile
```

---

## Phase 0: Clarification (When Needed)

Ask the user ONLY if:
- Compound name is highly ambiguous (e.g., "vitamin E" → α, β, γ, δ-tocopherol?)
- Multiple distinct compounds share the name (e.g., "aspirin" is clear; "sterol" is not)

Skip clarification for:
- Unambiguous drug names (aspirin, ibuprofen, metformin)
- Specific identifiers provided (CID, ChEMBL ID, SMILES)
- Clear structural queries (SMILES, InChI)

---

## Phase 1: Compound Disambiguation

### 1.1 Resolve Primary Identifier

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Strategy depends on input type
if user_provided_cid:
    cid = user_provided_cid
elif user_provided_smiles:
    result = tu.tools.PubChem_get_CID_by_SMILES(smiles=smiles)
    cid = result["data"]["cid"]
elif user_provided_name:
    result = tu.tools.PubChem_get_CID_by_compound_name(compound_name=name)
    cid = result["data"]["cid"]
```

### 1.2 Cross-Reference Identifiers

Always establish compound identity across both databases:

```python
# PubChem → ChEMBL cross-reference
chembl_result = tu.tools.ChEMBL_search_compounds(query=compound_name, limit=5)
if chembl_result["data"]:
    chembl_id = chembl_result["data"][0]["molecule_chembl_id"]
```

### 1.3 Handle Naming Collisions

For generic names (e.g., "vitamin", "steroid", "acid"):
- Search returns multiple CIDs → present top matches with structures
- Verify SMILES/InChI matches user intent
- Note stereoisomers or salt forms if relevant

**Identity Resolution Checklist:**
- [ ] PubChem CID established
- [ ] ChEMBL ID cross-referenced (if exists)
- [ ] Canonical SMILES captured
- [ ] Stereochemistry noted (if relevant)
- [ ] Salt forms identified (if applicable)

---

## Phase 2: Data Retrieval (Internal)

Retrieve all data silently. Do NOT narrate the search process.

### 2.1 Core Properties (PubChem)

```python
# Basic properties
props = tu.tools.PubChem_get_compound_properties_by_CID(cid=cid)

# Bioactivity summary
bio = tu.tools.PubChem_get_bioactivity_summary_by_CID(cid=cid)

# Drug label (if approved drug)
drug = tu.tools.PubChem_get_drug_label_info_by_CID(cid=cid)

# Structure image
image = tu.tools.PubChem_get_compound_2D_image_by_CID(cid=cid)
```

### 2.2 Bioactivity Data (ChEMBL)

```python
if chembl_id:
    # Detailed bioactivity
    activity = tu.tools.ChEMBL_get_bioactivity_by_chemblid(chembl_id=chembl_id)
    
    # Protein targets
    targets = tu.tools.ChEMBL_get_target_by_chemblid(chembl_id=chembl_id)
    
    # Assay data
    assays = tu.tools.ChEMBL_get_assays_by_chemblid(chembl_id=chembl_id)
```

### 2.3 Optional Extended Data

```python
# Patents (for drugs)
patents = tu.tools.PubChem_get_associated_patents_by_CID(cid=cid)

# Similar compounds (for SAR)
similar = tu.tools.PubChem_search_compounds_by_similarity(cid=cid, threshold=85)
```

### Fallback Chains

| Primary | Fallback | Notes |
|---------|----------|-------|
| PubChem_get_CID_by_compound_name | ChEMBL_search_compounds → get SMILES → PubChem_get_CID_by_SMILES | Name lookup failed |
| ChEMBL_get_bioactivity | PubChem_get_bioactivity_summary | ChEMBL ID unavailable |
| PubChem_get_drug_label_info | Note "Drug label unavailable" | Not an approved drug |

---

## Phase 3: Report Compound Profile

### Output Structure

Present results as a **Compound Profile Report**. Hide all search process details.

```markdown
# Compound Profile: [Compound Name]

## Identity
| Property | Value |
|----------|-------|
| **PubChem CID** | [cid] |
| **ChEMBL ID** | [chembl_id or "N/A"] |
| **IUPAC Name** | [full name] |
| **Common Names** | [synonyms] |

## Chemical Properties

### Molecular Descriptors
| Property | Value | Drug-Likeness |
|----------|-------|---------------|
| **Formula** | C₉H₈O₄ | - |
| **Molecular Weight** | 180.16 g/mol | ✓ (<500) |
| **LogP** | 1.19 | ✓ (-2 to 5) |
| **H-Bond Donors** | 1 | ✓ (<5) |
| **H-Bond Acceptors** | 4 | ✓ (<10) |
| **Polar Surface Area** | 63.6 Å² | ✓ (<140) |
| **Rotatable Bonds** | 3 | ✓ (<10) |

### Structural Representation
- **SMILES**: `CC(=O)Oc1ccccc1C(=O)O`
- **InChI**: `InChI=1S/C9H8O4/...`

[2D structure image if available]

## Bioactivity Profile

### Summary
- **Active in**: [X] assays out of [Y] tested
- **Primary Targets**: [list top targets]
- **Mechanism**: [if known]

### Key Target Interactions (from ChEMBL)
| Target | Activity Type | Value | Units |
|--------|--------------|-------|-------|
| [Target 1] | IC50 | [value] | nM |
| [Target 2] | Ki | [value] | nM |

## Drug Information (if applicable)

### Clinical Status
| Property | Value |
|----------|-------|
| **Approval Status** | [Approved/Investigational/N/A] |
| **Drug Class** | [therapeutic class] |
| **Indication** | [approved uses] |
| **Route** | [oral/IV/topical/etc.] |

### Safety
- **Black Box Warning**: [Yes/No]
- **Major Interactions**: [if any]

## Related Compounds (if retrieved)

Top 5 structurally similar compounds:
| CID | Name | Similarity | Key Difference |
|-----|------|------------|----------------|
| [cid] | [name] | 95% | [note] |

## Data Sources
- PubChem: [CID link]
- ChEMBL: [ChEMBL ID link]
- Retrieved: [date]
```

---

## Data Quality Tiers

Apply to data completeness assessment:

| Tier | Symbol | Criteria |
|------|--------|----------|
| Complete | ●●● | All core properties + bioactivity + drug info |
| Substantial | ●●○ | Core properties + bioactivity OR drug info |
| Basic | ●○○ | Core properties only |
| Minimal | ○○○ | CID/name only, limited data |

Include in report header:
```markdown
**Data Completeness**: ●●● Complete (properties, bioactivity, drug data)
```

---

## Completeness Checklist

Every compound profile MUST include these sections (even if "unavailable"):

### Identity (Required)
- [ ] PubChem CID
- [ ] ChEMBL ID (or "N/A")
- [ ] IUPAC name
- [ ] Canonical SMILES

### Properties (Required)
- [ ] Molecular formula
- [ ] Molecular weight
- [ ] LogP
- [ ] Lipinski rule assessment

### Bioactivity (Required)
- [ ] Activity summary (or "No bioactivity data")
- [ ] Primary targets (or "Unknown")

### Drug Info (If Approved Drug)
- [ ] Approval status
- [ ] Indication
- [ ] Drug class

### Always Include
- [ ] Data sources with links
- [ ] Retrieval date
- [ ] Quality tier assessment

---

## Common Use Cases

### Drug Property Check
User: "Tell me about metformin"
→ Full compound profile with drug information emphasis

### Structure Verification
User: "Verify this SMILES: CC(=O)Oc1ccccc1C(=O)O"
→ Disambiguation-focused profile, confirm identity

### SAR Analysis
User: "Find compounds similar to ibuprofen"
→ Similarity search + comparative property table

### Target Identification
User: "What proteins does gefitinib target?"
→ ChEMBL bioactivity emphasis with target list

---

## Error Handling

| Error | Response |
|-------|----------|
| "Compound not found" | Try synonyms, verify spelling, offer SMILES search |
| "No ChEMBL ID" | Note in Identity section, continue with PubChem data |
| "No bioactivity data" | Include section with "No bioactivity screening data available" |
| "API timeout" | Retry once, note unavailable data with "(retrieval failed)" |

---

## Tool Reference

**PubChem (Chemical Database)**
| Tool | Purpose |
|------|---------|
| `PubChem_get_CID_by_compound_name` | Name → CID |
| `PubChem_get_CID_by_SMILES` | Structure → CID |
| `PubChem_get_compound_properties_by_CID` | Molecular properties |
| `PubChem_get_compound_2D_image_by_CID` | Structure visualization |
| `PubChem_get_bioactivity_summary_by_CID` | Activity overview |
| `PubChem_get_drug_label_info_by_CID` | FDA drug labels |
| `PubChem_get_associated_patents_by_CID` | IP information |
| `PubChem_search_compounds_by_similarity` | Find analogs |
| `PubChem_search_compounds_by_substructure` | Substructure search |

**ChEMBL (Bioactivity Database)**
| Tool | Purpose |
|------|---------|
| `ChEMBL_search_compounds` | Name/structure search |
| `ChEMBL_get_compound_by_chemblid` | Compound details |
| `ChEMBL_get_bioactivity_by_chemblid` | Activity data |
| `ChEMBL_get_target_by_chemblid` | Protein targets |
| `ChEMBL_search_targets` | Target search |
| `ChEMBL_get_assays_by_chemblid` | Assay metadata |
