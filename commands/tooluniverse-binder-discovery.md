# tooluniverse-binder-discovery

> Discover novel small molecule binders for protein targets using structure-based and ligand-based approaches. Creates actionable reports with candidate compounds, ADMET profiles, and synthesis feasibility. Use when users ask to find small molecules for a target, identify novel binders, perform virtual screening, or need hit-to-lead compound identification.

# Small Molecule Binder Discovery Strategy

Systematic discovery of novel small molecule binders using 60+ ToolUniverse tools across druggability assessment, known ligand mining, similarity expansion, ADMET filtering, and synthesis feasibility.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Target validation FIRST** - Confirm druggability before compound searching
3. **Multi-strategy approach** - Combine structure-based and ligand-based methods
4. **ADMET-aware filtering** - Eliminate poor compounds early
5. **Evidence grading** - Grade candidates by supporting evidence
6. **Actionable output** - Provide prioritized candidates with rationale
7. **English-first queries** - Always use English terms in tool calls, even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

**DO NOT** show search process or tool outputs to the user. Instead:

1. **Create the report file FIRST** - Before any data collection:
   - File name: `[TARGET]_binder_discovery_report.md`
   - Initialize with all section headers from the template
   - Add placeholder text: `[Researching...]` in each section

2. **Progressively update the report** - As you gather data:
   - Update each section with findings immediately
   - The user sees the report growing, not the search process

3. **Output separate data files**:
   - `[TARGET]_candidate_compounds.csv` - Prioritized compounds with SMILES, scores
   - `[TARGET]_bibliography.json` - Literature references (optional)

### 2. Citation Requirements (MANDATORY)

Every piece of information MUST include its source:

```markdown
### 3.2 Known Inhibitors
| Compound | ChEMBL ID | IC50 (nM) | Selectivity | Source |
|----------|-----------|-----------|-------------|--------|
| Imatinib | CHEMBL941 | 38 | ABL-selective | ChEMBL |
| Dasatinib | CHEMBL1421 | 0.5 | Multi-kinase | ChEMBL |

*Source: ChEMBL via `ChEMBL_get_target_activities` (CHEMBL1862)*
```

---

## Workflow Overview

```
Phase 0: Tool Verification (check parameter names)
    ↓
Phase 1: Target Validation
    ├─ 1.1 Resolve identifiers (UniProt, Ensembl, ChEMBL target ID)
    ├─ 1.2 Assess druggability/tractability
    │   └─ 1.2.5 Check therapeutic antibodies (Thera-SAbDab) [NEW]
    ├─ 1.3 Identify binding sites
    └─ 1.4 Predict structure (NvidiaNIM_alphafold2/esmfold)
    ↓
Phase 2: Known Ligand Mining
    ├─ Extract ChEMBL bioactivity data
    ├─ Get GtoPdb interactions
    ├─ Identify chemical probes
    ├─ BindingDB affinity data (NEW - Ki/IC50/Kd)
    ├─ PubChem BioAssay HTS data (NEW - screening hits)
    └─ Analyze SAR from known actives
    ↓
Phase 3: Structure Analysis
    ├─ Get PDB structures with ligands
    ├─ Check EMDB for cryo-EM structures (NEW - for membrane targets)
    ├─ Analyze binding pocket
    └─ Identify key interactions
    ↓
Phase 3.5: Docking Validation (NvidiaNIM_diffdock/boltz2) [NEW]
    ├─ Dock reference inhibitor
    └─ Validate binding pocket geometry
    ↓
Phase 4: Compound Expansion
    ├─ 4.1-4.3 Similarity/substructure search
    └─ 4.4 De novo generation (NvidiaNIM_genmol/molmim) [NEW]
    ↓
Phase 5: ADMET Filtering
    ├─ Predict physicochemical properties
    ├─ Predict ADMET endpoints
    └─ Flag liabilities
    ↓
Phase 6: Candidate Docking & Prioritization
    ├─ Dock all candidates (NvidiaNIM_diffdock/boltz2) [UPDATED]
    ├─ Score by docking + ADMET + novelty
    ├─ Assess synthesis feasibility
    └─ Generate final ranked list
    ↓
Phase 7: Report Synthesis
```

---

## Phase 0: Tool Verification

**CRITICAL**: Verify tool parameters before calling unfamiliar tools.

```python
# Check tool params to prevent silent failures
tool_info = tu.tools.get_tool_info(tool_name="ChEMBL_get_target_activities")
```

### Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `OpenTargets_get_target_tractability_by_ensemblID` | `ensembl_id` | `ensemblId` |
| `ChEMBL_get_target_activities` | `chembl_target_id` | `target_chembl_id` |
| `ChEMBL_search_similar_molecules` | `smiles` | `molecule` (accepts SMILES, ChEMBL ID, or name) |
| `alphafold_get_prediction` | `uniprot` | `accession` |

---

## Phase 1: Target Validation

### 1.1 Identifier Resolution Chain

```
1. UniProt_search(query=target_name, organism="human")
   └─ Extract: UniProt accession, gene name, protein name

2. MyGene_query_genes(q=gene_symbol, species="human")
   └─ Extract: Ensembl gene ID, NCBI gene ID

3. ChEMBL_search_targets(query=target_name, organism="Homo sapiens")
   └─ Extract: ChEMBL target ID, target type

4. GtoPdb_get_targets(query=target_name)
   └─ Extract: GtoPdb target ID (if GPCR/ion channel/enzyme)
```

**Store all IDs for downstream queries**:
```
ids = {
    'uniprot': 'P00533',
    'ensembl': 'ENSG00000146648',
    'chembl_target': 'CHEMBL203',
    'gene_symbol': 'EGFR',
    'gtopdb': '1797'  # if available
}
```

### 1.2 Druggability Assessment

**Multi-Source Triangulation**:

```
1. OpenTargets_get_target_tractability_by_ensemblID(ensemblId)
   └─ Extract: Small molecule tractability score, bucket
   
2. DGIdb_get_gene_druggability(genes=[gene_symbol])
   └─ Extract: Druggability categories, known drug count
   
3. OpenTargets_get_target_classes_by_ensemblID(ensemblId)
   └─ Extract: Target class (kinase, GPCR, etc.)

4. GPCRdb_get_protein(protein=entry_name)  # NEW - for GPCRs
   └─ Extract: GPCR family, receptor state, ligand binding data
```

### 1.2a GPCRdb Integration (NEW - for GPCR Targets)

~35% of all approved drugs target GPCRs. For GPCR targets, use specialized data:

```python
def check_if_gpcr_and_enrich(tu, target_name, uniprot_id):
    """Check if target is GPCR and get specialized data."""
    
    # Build GPCRdb entry name (e.g., "adrb2_human")
    entry_name = f"{target_name.lower()}_human"
    
    # Check if it's a GPCR
    gpcr_info = tu.tools.GPCRdb_get_protein(
        operation="get_protein",
        protein=entry_name
    )
    
    if gpcr_info.get('status') == 'success':
        # It's a GPCR - get specialized data
        
        # Get known structures (active/inactive states)
        structures = tu.tools.GPCRdb_get_structures(
            operation="get_structures",
            protein=entry_name
        )
        
        # Get known ligands
        ligands = tu.tools.GPCRdb_get_ligands(
            operation="get_ligands",
            protein=entry_name
        )
        
        # Get mutation data (important for SAR)
        mutations = tu.tools.GPCRdb_get_mutations(
            operation="get_mutations",
            protein=entry_name
        )
        
        return {
            'is_gpcr': True,
            'gpcr_family': gpcr_info['data'].get('family'),
            'gpcr_class': gpcr_info['data'].get('receptor_class'),
            'structures': structures['data'].get('structures', []),
            'ligands': ligands['data'].get('ligands', []),
            'mutation_data': mutations['data'].get('mutations', [])
        }
    
    return {'is_gpcr': False}
```

**GPCRdb Advantages**:
- GPCR-specific sequence alignments (Ballesteros-Weinstein numbering)
- Active vs. inactive state structures
- Curated ligand binding data
- Experimental mutation effects on ligand binding

**Druggability Scorecard**:

| Factor | Assessment | Score |
|--------|------------|-------|
| Known small molecule drugs | Yes (3+) | ★★★ |
| Tractability bucket | 1-3 | ★★☆-★★★ |
| Target class | Enzyme/GPCR/Ion channel | ★★★ |
| Binding site known | Yes (X-ray) | ★★★ |
| GPCRdb ligands available | Yes (10+) | ★★★ (GPCR only) |
| Therapeutic antibodies exist | Check Thera-SAbDab | See 1.2.5 |

**Decision Point**: If druggability score < ★★☆, warn user about challenges.

### 1.2.5 Therapeutic Antibody Landscape (NEW)

Check if therapeutic antibodies already target this protein - important for:
- Understanding competitive landscape
- Validating target tractability (if antibodies work, target is validated)
- Identifying potential combination approaches

```python
def check_therapeutic_antibodies(tu, target_name):
    """
    Check Thera-SAbDab for therapeutic antibodies against target.
    """
    # Search by target name
    results = tu.tools.TheraSAbDab_search_by_target(
        target=target_name
    )
    
    if results.get('status') == 'success':
        antibodies = results['data'].get('therapeutics', [])
        
        # Categorize by clinical stage
        by_phase = {'Approved': [], 'Phase 3': [], 'Phase 2': [], 'Phase 1': [], 'Preclinical': []}
        for ab in antibodies:
            phase = ab.get('phase', 'Unknown')
            for key in by_phase.keys():
                if key.lower() in phase.lower():
                    by_phase[key].append(ab)
                    break
        
        return {
            'total_antibodies': len(antibodies),
            'by_phase': by_phase,
            'antibodies': antibodies[:10],  # Top 10
            'competitive_alert': len(by_phase.get('Approved', [])) > 0
        }
    return None

def get_antibody_landscape(tu, target_name, uniprot_id=None):
    """
    Comprehensive antibody competitive landscape.
    """
    # Thera-SAbDab search
    therasabdab = check_therapeutic_antibodies(tu, target_name)
    
    # Also search by common synonyms
    synonyms = [target_name]
    if target_name != uniprot_id:
        synonyms.append(uniprot_id)
    
    all_antibodies = []
    for synonym in synonyms:
        results = tu.tools.TheraSAbDab_search_therapeutics(query=synonym)
        if results.get('status') == 'success':
            all_antibodies.extend(results['data'].get('therapeutics', []))
    
    # Deduplicate
    seen = set()
    unique = []
    for ab in all_antibodies:
        inn = ab.get('inn_name')
        if inn and inn not in seen:
            seen.add(inn)
            unique.append(ab)
    
    return {
        'antibodies': unique,
        'count': len(unique),
        'has_approved': any(ab.get('phase', '').lower() == 'approved' for ab in unique),
        'source': 'Thera-SAbDab'
    }
```

**Report Output**:
```markdown
### 1.2.5 Therapeutic Antibody Landscape (NEW)

**Thera-SAbDab Search Results**:

| Antibody (INN) | Target | Format | Phase | PDB |
|----------------|--------|--------|-------|-----|
| Pembrolizumab | PD-1 | IgG4 | Approved | 5DK3 |
| Nivolumab | PD-1 | IgG4 | Approved | 5WT9 |
| Cemiplimab | PD-1 | IgG4 | Approved | 7WVM |

**Competitive Landscape**: ⚠️ 3 approved antibodies target this protein
**Strategic Implication**: Small molecule approach offers differentiation (oral dosing, CNS penetration, cost)

*Source: Thera-SAbDab via `TheraSAbDab_search_by_target`*
```

**Why Include Antibody Landscape**:
- **Validation**: Approved antibodies = validated target
- **Competition**: Understand what's already in market/clinic
- **Strategy**: Identify gaps (no oral, no CNS-penetrant)
- **Synergy**: Potential combination opportunities

### 1.3 Binding Site Analysis

```
1. ChEMBL_search_binding_sites(target_chembl_id)
   └─ Extract: Binding site names, types
   
2. get_binding_affinity_by_pdb_id(pdb_id)  # For each PDB with ligand
   └─ Extract: Kd, Ki, IC50 values for co-crystallized ligands
   
3. InterPro_get_protein_domains(uniprot_accession)
   └─ Extract: Domain architecture, active sites
```

**Output for Report**:
```markdown
### 1.3 Binding Site Assessment

**Known Binding Sites**: 
| Site | Type | Evidence | Key Residues | Source |
|------|------|----------|--------------|--------|
| ATP pocket | Orthosteric | X-ray (23 PDBs) | K745, E762, M793 | PDB/ChEMBL |
| Allosteric pocket | Allosteric | X-ray (3 PDBs) | T790, C797 | PDB |

**Binding Site Druggability**: ★★★ (well-defined pocket, multiple co-crystal structures)

*Source: ChEMBL via `ChEMBL_search_binding_sites`, PDB structures*
```

### 1.4 Structure Prediction (NVIDIA NIM)

When no experimental structure is available, or for custom domain predictions.

**Requires**: `NVIDIA_API_KEY` environment variable

**Option A: AlphaFold2 (High accuracy, async)**
```
NvidiaNIM_alphafold2(
    sequence=kinase_domain_sequence,
    algorithm="mmseqs2",
    relax_prediction=False
)
└─ Returns: PDB structure with pLDDT confidence scores
└─ Use when: Accuracy is critical, time is available (~5-15 min)
```

**Option B: ESMFold (Fast, synchronous)**
```
NvidiaNIM_esmfold(sequence=kinase_domain_sequence)
└─ Returns: PDB structure (max 1024 AA)
└─ Use when: Quick assessment needed (~30 sec)
```

**Report pLDDT Confidence**:
```markdown
### 1.4 Structure Prediction Quality

**Method**: AlphaFold2 via NVIDIA NIM
**Mean pLDDT**: 90.94 (very high confidence)

| Confidence Level | Range | Fraction | Interpretation |
|------------------|-------|----------|----------------|
| Very High | ≥90 | 74.3% | Highly reliable |
| Confident | 70-90 | 16.0% | Reliable |
| Low | 50-70 | 9.0% | Use caution |
| Very Low | <50 | 0.7% | Unreliable |

**Key Binding Residue Confidence**:
| Residue | Function | pLDDT |
|---------|----------|-------|
| K745 | ATP binding | 90.0 |
| T790 | Gatekeeper | 92.3 |
| M793 | Hinge region | 95.3 |
| D855 | DFG motif | 89.5 |

*Source: NVIDIA NIM via `NvidiaNIM_alphafold2`*
```

---

## Phase 2: Known Ligand Mining

### 2.1 ChEMBL Bioactivity Data

```
1. ChEMBL_get_target_activities(target_chembl_id, limit=500)
   └─ Filter: standard_type in ["IC50", "Ki", "Kd", "EC50"]
   └─ Filter: standard_value < 10000 nM
   └─ Extract: ChEMBL molecule IDs, SMILES, potency values

2. ChEMBL_get_molecule(molecule_chembl_id)  # For top actives
   └─ Extract: Full molecular data, max_phase, oral flag
```

**Activity Summary Table**:
```markdown
### 2.1 Known Active Compounds (ChEMBL)

**Total Bioactivity Points**: 2,847 (IC50: 1,234 | Ki: 892 | Kd: 456 | EC50: 265)
**Compounds with IC50 < 100 nM**: 156
**Approved Drugs for This Target**: 5

| Compound | ChEMBL ID | IC50 (nM) | Max Phase | SMILES (truncated) |
|----------|-----------|-----------|-----------|-------------------|
| Erlotinib | CHEMBL553 | 2 | 4 | COc1cc2ncnc(Nc3ccc... |
| Gefitinib | CHEMBL939 | 5 | 4 | COc1cc2ncnc(Nc3ccc... |
| [Novel] | CHEMBL123 | 12 | 0 | c1ccc(NC(=O)c2ccc... |

*Source: ChEMBL via `ChEMBL_get_target_activities` (CHEMBL203)*
```

### 2.2 GtoPdb Interactions

```
GtoPdb_get_target_interactions(target_id)
└─ Extract: Ligands with pKi/pIC50, selectivity data
```

### 2.3 Chemical Probes

```
OpenTargets_get_chemical_probes_by_target_ensemblID(ensemblId)
└─ Extract: Validated chemical probes with ratings
```

**Output for Report**:
```markdown
### 2.3 Chemical Probes

| Probe | Target | Rating | Use | Caveat | Source |
|-------|--------|--------|-----|--------|--------|
| Probe-X | EGFR | ★★★★ | In vivo | None | Chemical Probes Portal |
| Probe-Y | EGFR | ★★★☆ | In vitro | Off-target kinase activity | Open Targets |

**Recommended Probe for Target Validation**: Probe-X (highest rating, validated in vivo)
```

### 2.4 SAR Analysis from Actives

Identify common scaffolds and SAR trends:

```markdown
### 2.4 Structure-Activity Relationships

**Core Scaffolds Identified**:
1. **4-Anilinoquinazoline** (34 compounds, IC50 range: 2-500 nM)
   - N1 position: Aryl preferred
   - C6/C7: Methoxy groups improve potency
   
2. **Pyrimidine-amine** (12 compounds, IC50 range: 15-800 nM)
   - Less potent than quinazolines
   - Better selectivity profile

**Key SAR Insights**:
- Halogen at meta position of aniline increases potency 3-5x
- C7 ethoxy group critical for binding (H-bond to M793)
```

### 2.5 BindingDB Affinity Data (NEW)

BindingDB provides experimental binding affinity data complementary to ChEMBL:

```python
def get_bindingdb_ligands(tu, uniprot_id, affinity_cutoff=10000):
    """
    Get ligands from BindingDB with measured affinities.
    
    BindingDB advantages:
    - May have compounds not in ChEMBL
    - Different affinity types (Ki, IC50, Kd)
    - Direct literature links
    """
    
    result = tu.tools.BindingDB_get_ligands_by_uniprot(
        uniprot=uniprot_id,
        affinity_cutoff=affinity_cutoff  # nM
    )
    
    if result:
        ligands = []
        for entry in result:
            ligands.append({
                'smiles': entry.get('smile'),
                'affinity_type': entry.get('affinity_type'),
                'affinity_nM': entry.get('affinity'),
                'pmid': entry.get('pmid'),
                'monomer_id': entry.get('monomerid')
            })
        
        # Sort by potency
        ligands.sort(key=lambda x: float(x['affinity_nM']) if x['affinity_nM'] else 1e6)
        return ligands[:50]  # Top 50
    
    return []

def find_compound_polypharmacology(tu, smiles, similarity_cutoff=0.85):
    """Find off-target interactions for selectivity analysis."""
    
    targets = tu.tools.BindingDB_get_targets_by_compound(
        smiles=smiles,
        similarity_cutoff=similarity_cutoff
    )
    
    return targets  # Other proteins this compound may bind
```

**BindingDB Output for Report**:
```markdown
### 2.5 Additional Ligands (BindingDB) (NEW)

**Total Unique Ligands**: 89 (non-overlapping with ChEMBL)
**Most Potent**: 0.3 nM Ki

| SMILES | Affinity Type | Value (nM) | PMID | BindingDB ID |
|--------|---------------|------------|------|--------------|
| CC(C)Cc1ccc... | Ki | 0.3 | 15737014 | 12345 |
| COc1cc2ncnc... | IC50 | 2.1 | 16460808 | 12346 |

**Novel Scaffolds from BindingDB**: 3 scaffolds not seen in ChEMBL data

*Source: BindingDB via `BindingDB_get_ligands_by_uniprot`*
```

### 2.6 PubChem BioAssay Screening Data (NEW)

PubChem BioAssay provides HTS screening results and dose-response data:

```python
def get_pubchem_assays_for_target(tu, gene_symbol):
    """
    Get bioassays and active compounds from PubChem.
    
    Advantages:
    - HTS data not in ChEMBL
    - NIH-funded screening programs (MLPCN)
    - Dose-response curves for IC50 calculation
    """
    
    # Search assays targeting this gene
    assays = tu.tools.PubChem_search_assays_by_target_gene(
        gene_symbol=gene_symbol
    )
    
    results = {
        'assays': [],
        'total_active_compounds': 0
    }
    
    if assays.get('data', {}).get('aids'):
        for aid in assays['data']['aids'][:10]:  # Top 10 assays
            # Get assay summary
            summary = tu.tools.PubChem_get_assay_summary(aid=aid)
            
            # Get active compounds
            actives = tu.tools.PubChem_get_assay_active_compounds(aid=aid)
            active_cids = actives.get('data', {}).get('cids', [])
            
            results['assays'].append({
                'aid': aid,
                'summary': summary.get('data', {}),
                'active_count': len(active_cids)
            })
            results['total_active_compounds'] += len(active_cids)
    
    return results

def get_dose_response_data(tu, aid):
    """Get dose-response curves for IC50/EC50 determination."""
    
    dr_data = tu.tools.PubChem_get_assay_dose_response(aid=aid)
    return dr_data

def get_compound_bioactivity_profile(tu, cid):
    """Get all bioactivity data for a compound."""
    
    profile = tu.tools.PubChem_get_compound_bioactivity(cid=cid)
    return profile
```

**PubChem BioAssay Output for Report**:
```markdown
### 2.6 PubChem HTS Screening Data (NEW)

**Assays Found**: 45
**Total Active Compounds Across Assays**: ~1,200

| AID | Assay Type | Active Compounds | Target | Description |
|-----|------------|------------------|--------|-------------|
| 504526 | HTS | 234 | EGFR | qHTS inhibition screen |
| 1053104 | Dose-response | 12 | EGFR kinase | Confirmatory IC50 |
| 651564 | Cellular | 8 | EGFR | Cell proliferation assay |

**Novel Actives** (not in ChEMBL/BindingDB):
- CID 12345678: Active in AID 504526, IC50 = 45 nM
- CID 23456789: Active in AID 1053104, IC50 = 120 nM

*Source: PubChem via `PubChem_search_assays_by_target_gene`, `PubChem_get_assay_active_compounds`*
```

**Why Use Both BindingDB and PubChem**:
| Source | Strengths | Best For |
|--------|-----------|----------|
| **ChEMBL** | Curated, standardized, SAR data | Primary ligand source |
| **BindingDB** | Direct affinity measurements | Ki/Kd values, PMIDs |
| **PubChem BioAssay** | HTS data, NIH screens | Novel scaffolds, broad coverage |

---

## Phase 3: Structure Analysis

### 3.1 PDB Structure Retrieval

```
1. PDB_search_similar_structures(query=uniprot_accession, type="sequence")
   └─ Extract: PDB IDs with ligands
   
2. get_protein_metadata_by_pdb_id(pdb_id)
   └─ Extract: Resolution, method, ligand codes
   
3. alphafold_get_prediction(accession=uniprot_accession)
   └─ Extract: Predicted structure (if no experimental)
```

### 3.1b EMDB Cryo-EM Structures (NEW)

**Prioritize EMDB for**: Membrane proteins (GPCRs, ion channels), large complexes, targets with multiple conformational states.

```python
def get_cryoem_structures(tu, target_name, uniprot_accession):
    """Get cryo-EM structures for membrane targets."""
    
    # Search EMDB
    emdb_results = tu.tools.emdb_search(
        query=f"{target_name} membrane receptor"
    )
    
    structures = []
    for entry in emdb_results[:5]:
        details = tu.tools.emdb_get_entry(entry_id=entry['emdb_id'])
        
        # Get associated PDB model (essential for docking)
        pdb_models = details.get('pdb_ids', [])
        
        structures.append({
            'emdb_id': entry['emdb_id'],
            'resolution': entry.get('resolution', 'N/A'),
            'title': entry.get('title', 'N/A'),
            'conformational_state': details.get('state', 'Unknown'),
            'pdb_models': pdb_models
        })
    
    return structures
```

**When to use cryo-EM over X-ray**:
| Target Type | Prefer cryo-EM? | Reason |
|-------------|-----------------|--------|
| GPCR | Yes | Native membrane conformation |
| Ion channel | Yes | Multiple functional states |
| Receptor-ligand complex | Yes | Physiological state |
| Kinase | Usually X-ray | Higher resolution typically |

**Structure Summary**:
```markdown
### 3.1 Available Structures

| PDB ID | Resolution | Method | Ligand | Affinity | State |
|--------|------------|--------|--------|----------|-------|
| 1M17 | 2.6 Å | X-ray | Erlotinib | Ki=0.4 nM | Active |
| 4HJO | 2.1 Å | X-ray | Lapatinib | Ki=3 nM | Inactive |
| AF-P00533 | - | Predicted | None | - | - |

### 3.1b Cryo-EM Structures (EMDB)

| EMDB ID | Resolution | PDB Model | Conformation | Ligand |
|---------|------------|-----------|--------------|--------|
| EMD-12345 | 3.2 Å | 7ABC | Active | Agonist |
| EMD-23456 | 3.5 Å | 8DEF | Inactive | Antagonist |

**Best Structure for Docking**: 1M17 (high resolution, relevant ligand)
*Source: RCSB PDB, EMDB, AlphaFold DB*
```

### 3.2 Binding Pocket Analysis

```
get_binding_affinity_by_pdb_id(pdb_id)
└─ Extract: Binding affinities for co-crystallized ligands
```

**Output for Report**:
```markdown
### 3.2 Binding Pocket Characterization

**Pocket Volume**: ~850 Å³ (well-defined)
**Key Interaction Residues**:
- **Hinge region**: M793 (backbone H-bond donor/acceptor)
- **Gatekeeper**: T790 (small residue, allows access)
- **DFG motif**: D855 (active conformation)
- **Selectivity pocket**: L788, G796 (unique to EGFR)

**Druggability Assessment**: High (enclosed pocket, conserved interactions)
```

---

## Phase 3.5: Docking Validation (NVIDIA NIM)

Validate structure and score compounds using molecular docking.

**Requires**: `NVIDIA_API_KEY` environment variable

### 3.5.1 Reference Compound Docking

Dock a known inhibitor to validate the structure captures the binding pocket correctly.

**Option A: DiffDock (Blind docking, PDB + SDF input)**
```
NvidiaNIM_diffdock(
    protein=pdb_content,        # PDB text content
    ligand=reference_sdf,       # SDF/MOL2 content
    num_poses=10
)
└─ Returns: Docking poses with confidence scores
└─ Use: When you have PDB structure and ligand SDF file
```

**Option B: Boltz2 (From sequence + SMILES)**
```
NvidiaNIM_boltz2(
    polymers=[{"molecule_type": "protein", "sequence": kinase_sequence}],
    ligands=[{"smiles": "COc1cc2ncnc(Nc3ccc(C#C)cc3)c2cc1OCCOC"}],
    sampling_steps=50,
    diffusion_samples=1
)
└─ Returns: Protein-ligand complex structure
└─ Use: When starting from SMILES, no SDF needed
```

### 3.5.2 Docking Score Interpretation

| Score vs Reference | Priority | Symbol |
|--------------------|----------|--------|
| Higher than reference | Top priority | ★★★★ |
| Within 5% of reference | High priority | ★★★ |
| Within 20% of reference | Moderate priority | ★★☆ |
| >20% lower | Low priority | ★☆☆ |

**Report Format**:
```markdown
### 3.5 Docking Validation Results

**Reference Compound**: Erlotinib
**Method**: DiffDock via NVIDIA NIM

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Best Pose Confidence | 0.906 | Excellent |
| Steric Clashes | None | Clean binding pose |

**Validation Status**: ✓ Structure captures binding pocket correctly

*Source: NVIDIA NIM via `NvidiaNIM_diffdock`*
```

---

## Phase 4: Compound Expansion

### 4.1 Similarity Search

Starting from top actives, expand chemical space:

```
1. ChEMBL_search_similar_molecules(molecule=top_active_smiles, similarity=70)
   └─ Extract: Similar compounds not yet tested on target
   
2. PubChem_search_compounds_by_similarity(smiles, threshold=0.7)
   └─ Extract: PubChem CIDs with similar structures
```

**Strategy**:
- Use 3-5 diverse actives as seeds
- Similarity threshold: 70-85% (balance novelty vs. activity)
- Prioritize compounds NOT in ChEMBL bioactivity for target

### 4.2 Substructure Search

```
1. ChEMBL_search_substructure(smiles=core_scaffold)
   └─ Extract: Compounds containing scaffold
   
2. PubChem_search_compounds_by_substructure(smiles=core_scaffold)
   └─ Extract: Additional scaffold-containing compounds
```

### 4.3 Cross-Database Mining

```
1. STITCH_get_chemical_protein_interactions(identifier=target_gene)
   └─ Extract: Additional chemical-protein links
   
2. DGIdb_get_drug_gene_interactions(genes=[gene_symbol])
   └─ Extract: Approved/investigational drugs
```

**Output for Report**:
```markdown
### 4. Compound Expansion Results

**Starting Seeds**: 5 diverse actives (IC50 < 100 nM)
**Similarity Expansion**: 847 compounds (70% threshold)
**Substructure Search**: 234 scaffold matches
**Cross-Database**: 45 additional hits

**After Deduplication**: 923 unique candidate compounds

| Source | Compounds | Already Tested | Novel Candidates |
|--------|-----------|----------------|------------------|
| ChEMBL similarity | 456 | 234 | 222 |
| PubChem similarity | 391 | 156 | 235 |
| ChEMBL substructure | 178 | 89 | 89 |
| STITCH | 45 | 23 | 22 |
| **Total Unique** | **923** | **355** | **568** |
```

### 4.4 De Novo Molecule Generation (NVIDIA NIM)

When database mining yields insufficient candidates, generate novel molecules.

**Requires**: `NVIDIA_API_KEY` environment variable

**Option A: GenMol (Scaffold Hopping with Masked Regions)**
```
NvidiaNIM_genmol(
    smiles="COc1cc2ncnc(Nc3ccc([*{3-8}])c([*{1-3}])c3)c2cc1OCCCN1CCOCC1",
    num_molecules=100,
    temperature=2.0,
    scoring="QED"
)
└─ Input: SMILES with [*{min-max}] masked regions
└─ Output: Generated molecules with QED/LogP scores
└─ Use: Explore specific positions while keeping scaffold
```

**Mask Design Strategy**:
| Position | Mask | Purpose |
|----------|------|---------|
| Aniline substituent | `[*{1-3}]` | Small groups (halogen, methyl) |
| Solubilizing group | `[*{5-10}]` | Morpholine, piperazine variants |
| Linker region | `[*{3-6}]` | Spacer variations |

**Example Masked SMILES for EGFR**:
```
# Keep quinazoline core, vary aniline and tail
COc1cc2ncnc(Nc3ccc([*{1-3}])c([*{1-3}])c3)c2cc1[*{5-12}]
```

**Option B: MolMIM (Controlled Generation from Reference)**
```
NvidiaNIM_molmim(
    smi="COc1cc2ncnc(Nc3ccc(Cl)cc3)c2cc1OCCN1CCOCC1",
    num_molecules=50,
    algorithm="CMA-ES"
)
└─ Input: Reference SMILES (known active)
└─ Output: Optimized analogs with property scores
└─ Use: Generate close analogs of top actives
```

**Generation Workflow**:
1. Identify top 3-5 actives from Phase 2
2. Design masked SMILES for GenMol OR use as reference for MolMIM
3. Generate 50-100 molecules per seed
4. Pass generated molecules to Phase 5 (ADMET filtering)
5. Dock survivors in Phase 6 for final ranking

**Report Format**:
```markdown
### 4.4 De Novo Generation Results

**Method**: GenMol via NVIDIA NIM
**Seed Scaffold**: 4-anilinoquinazoline (from erlotinib)
**Masked Positions**: Aniline (3,4), solubilizing tail

| Metric | Value |
|--------|-------|
| Molecules Generated | 100 |
| Passing Lipinski | 95 (95%) |
| Mean QED Score | 0.72 |
| Unique Scaffolds | 12 |

**Top Generated Compounds**:
| ID | SMILES | QED | LogP | Novelty |
|----|--------|-----|------|---------|
| GEN-001 | COc1cc2ncnc(Nc3ccc(Cl)c(Cl)c3)c2cc1OCCCN1CCOCC1 | 0.81 | 4.2 | Novel substitution |
| GEN-002 | COc1cc2ncnc(Nc3ccc(C#N)c(F)c3)c2cc1OCCCN1CCOCC1 | 0.78 | 3.8 | Novel substitution |

*Source: NVIDIA NIM via `NvidiaNIM_genmol`*
```

---

## Phase 5: ADMET Filtering

### 5.1 Physicochemical Properties

```
ADMETAI_predict_physicochemical_properties(smiles=[compound_list])
└─ Filter: Lipinski violations ≤ 1
└─ Filter: QED > 0.3
└─ Filter: MW 200-600
```

### 5.2 ADMET Endpoints

```
1. ADMETAI_predict_bioavailability(smiles=[compound_list])
   └─ Filter: Oral bioavailability > 0.3
   
2. ADMETAI_predict_toxicity(smiles=[compound_list])
   └─ Filter: AMES < 0.5, hERG < 0.5, DILI < 0.5
   
3. ADMETAI_predict_CYP_interactions(smiles=[compound_list])
   └─ Flag: CYP3A4 inhibitors (drug interaction risk)
```

### 5.3 Structural Alerts

```
ChEMBL_search_compound_structural_alerts(smiles=compound_smiles)
└─ Flag: PAINS, reactive groups, toxicophores
```

**ADMET Filter Summary**:
```markdown
### 5. ADMET Filtering Results

| Filter Stage | Input | Passed | Failed | Pass Rate |
|--------------|-------|--------|--------|-----------|
| Physicochemical (Lipinski) | 568 | 456 | 112 | 80% |
| Drug-likeness (QED > 0.3) | 456 | 398 | 58 | 87% |
| Bioavailability (> 0.3) | 398 | 312 | 86 | 78% |
| Toxicity filters | 312 | 267 | 45 | 86% |
| Structural alerts | 267 | 234 | 33 | 88% |
| **Final Candidates** | **568** | **234** | **334** | **41%** |

**Common Failure Reasons**:
1. High molecular weight (>600): 67 compounds
2. Low predicted bioavailability: 86 compounds
3. hERG liability: 28 compounds
4. PAINS alerts: 18 compounds
```

---

## Phase 6: Candidate Prioritization

### 6.1 Scoring Framework

Score each candidate on multiple dimensions:

| Dimension | Weight | Scoring Criteria |
|-----------|--------|------------------|
| **Structural Similarity** | 25% | Tanimoto to actives (0.7-1.0 → 1-5) |
| **Novelty** | 20% | Not in ChEMBL bioactivity = +2; Novel scaffold = +3 |
| **ADMET Score** | 25% | Composite of property predictions |
| **Synthesis Feasibility** | 15% | SA score (1-10), commercial availability |
| **Scaffold Diversity** | 15% | Cluster representative bonus |

### 6.2 Synthesis Feasibility

```markdown
### 6.2 Synthesis Feasibility Assessment

| Candidate | SA Score | Commercial | Estimated Steps | Flag |
|-----------|----------|------------|-----------------|------|
| Compound-1 | 2.3 | Yes (Enamine) | 0 | ★★★ |
| Compound-2 | 3.5 | Building block | 2-3 | ★★☆ |
| Compound-3 | 5.8 | No | 6-8 | ★☆☆ |

**SA Score Interpretation**:
- 1-3: Easy synthesis
- 3-5: Moderate complexity
- 5-10: Challenging synthesis
```

### 6.3 Final Prioritized List

```markdown
### 6.3 Top 20 Candidate Compounds

| Rank | ID | SMILES | Sim. Score | ADMET | Novelty | Overall | Rationale |
|------|-----|--------|------------|-------|---------|---------|-----------|
| 1 | CPD-001 | Cc1ccc... | 0.82 | 4.5 | Novel scaffold | 4.2 | High similarity, clean ADMET |
| 2 | CPD-002 | COc1cc... | 0.78 | 4.3 | Not tested | 4.0 | Quinazoline analog |
| 3 | CPD-003 | Nc1ccc... | 0.75 | 4.1 | Novel core | 3.9 | New chemotype |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Scaffold Diversity**: 7 distinct scaffolds in top 20
**Commercial Availability**: 12/20 available for purchase
**Estimated Hit Rate**: 15-25% (based on similarity to actives)
```

---

## Phase 6.5: Literature Evidence (NEW)

### 6.5.1 Literature Search for Validation

Search literature to validate candidate compounds and understand target context.

```python
def search_binder_literature(tu, target_name, compound_scaffolds):
    """Search literature for compound and target evidence."""
    
    # PubMed: Published SAR studies
    sar_papers = tu.tools.PubMed_search_articles(
        query=f"{target_name} inhibitor SAR structure-activity",
        limit=30
    )
    
    # BioRxiv: Latest unpublished findings
    preprints = tu.tools.BioRxiv_search_preprints(
        query=f"{target_name} small molecule discovery",
        limit=15
    )
    
    # MedRxiv: Clinical data on inhibitors
    clinical = tu.tools.MedRxiv_search_preprints(
        query=f"{target_name} inhibitor clinical trial",
        limit=10
    )
    
    # Citation analysis for key papers
    key_papers = sar_papers[:10]
    for paper in key_papers:
        citation = tu.tools.openalex_search_works(
            query=paper['title'],
            limit=1
        )
        paper['citations'] = citation[0].get('cited_by_count', 0) if citation else 0
    
    return {
        'published_sar': sar_papers,
        'preprints': preprints,
        'clinical_preprints': clinical,
        'high_impact_papers': sorted(key_papers, key=lambda x: x.get('citations', 0), reverse=True)
    }
```

### 6.5.2 Output for Report

```markdown
## 6.5 Literature Evidence

### Published SAR Studies

| PMID | Title | Year | Key Insight |
|------|-------|------|-------------|
| 34567890 | Discovery of novel EGFR inhibitors... | 2024 | C7 substitution critical |
| 33456789 | Structure-activity relationship of... | 2023 | Fluorine improves potency |

### Recent Preprints (⚠️ Not Peer-Reviewed)

| Source | Title | Posted | Relevance |
|--------|-------|--------|-----------|
| BioRxiv | Novel scaffolds for EGFR... | 2024-02 | New chemotype discovery |
| MedRxiv | Clinical activity of... | 2024-01 | Phase 2 results |

### High-Impact References

| PMID | Citations | Title |
|------|-----------|-------|
| 32123456 | 523 | Landmark EGFR inhibitor study... |
| 31234567 | 312 | Comprehensive SAR analysis... |

*Source: PubMed, BioRxiv, MedRxiv, OpenAlex*
```

---

## Report Template

**File**: `[TARGET]_binder_discovery_report.md`

```markdown
# Small Molecule Binder Discovery: [TARGET]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Researching...]

---

## 1. Target Validation
### 1.1 Target Identifiers
[Researching...]
### 1.2 Druggability Assessment
[Researching...]
### 1.3 Binding Site Analysis
[Researching...]

---

## 2. Known Ligand Landscape
### 2.1 ChEMBL Bioactivity Summary
[Researching...]
### 2.2 Approved Drugs & Clinical Compounds
[Researching...]
### 2.3 Chemical Probes
[Researching...]
### 2.4 SAR Insights
[Researching...]

---

## 3. Structural Information
### 3.1 Available Structures
[Researching...]
### 3.2 Binding Pocket Analysis
[Researching...]
### 3.3 Key Interactions
[Researching...]

---

## 4. Compound Expansion
### 4.1 Similarity Search Results
[Researching...]
### 4.2 Substructure Search Results
[Researching...]
### 4.3 Cross-Database Mining
[Researching...]

---

## 5. ADMET Filtering
### 5.1 Physicochemical Filters
[Researching...]
### 5.2 ADMET Predictions
[Researching...]
### 5.3 Structural Alerts
[Researching...]
### 5.4 Filter Summary
[Researching...]

---

## 6. Candidate Prioritization
### 6.1 Scoring Methodology
[Researching...]
### 6.2 Synthesis Feasibility
[Researching...]
### 6.3 Top 20 Candidates
[Researching...]

---

## 7. Recommendations
### 7.1 Immediate Actions
[Researching...]
### 7.2 Experimental Validation Plan
[Researching...]
### 7.3 Backup Strategies
[Researching...]

---

## 8. Data Gaps & Limitations
[Researching...]

---

## 9. Data Sources
[Will be populated as research progresses...]

---

## 10. Methods Summary

| Step | Tool | Purpose |
|------|------|---------|
| Sequence retrieval | UniProt_search | Get protein sequence |
| Structure prediction | NvidiaNIM_alphafold2 / NvidiaNIM_esmfold | 3D structure with pLDDT |
| Docking validation | NvidiaNIM_diffdock / NvidiaNIM_boltz2 | Validate binding pocket |
| Known ligands | ChEMBL_get_target_activities | Bioactivity data |
| Similarity search | ChEMBL_search_similar_molecules | Expand chemical space |
| De novo generation | NvidiaNIM_genmol / NvidiaNIM_molmim | Novel molecule design |
| ADMET filtering | ADMETAI_predict_* | Drug-likeness assessment |
| Candidate docking | NvidiaNIM_diffdock / NvidiaNIM_boltz2 | Final scoring |
```

---

## Evidence Grading

| Tier | Symbol | Description | Example |
|------|--------|-------------|---------|
| **T0** | ★★★★ | Docking score > reference inhibitor | Better than erlotinib |
| **T1** | ★★★ | Experimental IC50/Ki < 100 nM | ChEMBL bioactivity |
| **T2** | ★★☆ | Docking within 5% of reference OR IC50 100-1000 nM | High priority |
| **T3** | ★☆☆ | Structural similarity > 80% to T1 | Predicted active |
| **T4** | ☆☆☆ | Similarity 70-80%, scaffold match | Lower confidence |
| **T5** | ○○○ | Generated molecule, ADMET-passed, no docking | Speculative |

**Docking-Enhanced Grading**: When NVIDIA NIM docking is available, compounds gain evidence:
- Docking > reference → upgrade to T0 (★★★★)
- Docking within 5% → upgrade to T2 (★★☆)
- Docking within 20% → maintain current tier
- Docking >20% worse → downgrade one tier

Apply to all candidate compounds:
```markdown
| Compound | Evidence | Docking vs Ref | Rationale |
|----------|----------|----------------|-----------|
| CPD-001 | ★★★★ | +8.3% | 85% similar, docking > erlotinib |
| CPD-002 | ★★★ | -2.1% | IC50=45nM, validated by docking |
| CPD-003 | ★★☆ | -4.5% | 78% similar, good docking |
| GEN-001 | ★☆☆ | -15% | Generated, ADMET-passed |
```

---

## Mandatory Completeness Checklist

### Phase 1: Target Validation
- [ ] UniProt accession resolved
- [ ] ChEMBL target ID obtained
- [ ] Druggability assessed (≥2 sources)
- [ ] Target class identified
- [ ] Binding site information (or "No structural data")

### Phase 2: Known Ligands
- [ ] ChEMBL activities queried (≥100 or all available)
- [ ] Activity statistics (count, potency range)
- [ ] Top 10 actives listed with IC50
- [ ] Chemical probes identified (or "None available")
- [ ] SAR insights summarized

### Phase 3: Structure
- [ ] PDB structures listed (or "No experimental structure")
- [ ] Best structure for docking identified
- [ ] Binding pocket described (or "Predicted from AlphaFold")

### Phase 4: Expansion
- [ ] ≥3 seed compounds used
- [ ] Similarity search completed (≥100 results or exhausted)
- [ ] Substructure search completed
- [ ] Deduplicated candidate count reported

### Phase 5: ADMET
- [ ] Physicochemical filters applied
- [ ] Toxicity predictions run
- [ ] Structural alerts checked
- [ ] Filter funnel table included

### Phase 6: Prioritization
- [ ] ≥20 candidates ranked (or all if fewer)
- [ ] Scoring methodology explained
- [ ] Synthesis feasibility assessed
- [ ] Scaffold diversity noted

### Phase 7: Recommendations
- [ ] ≥3 immediate actions listed
- [ ] Experimental validation plan outlined
- [ ] Data gaps aggregated

---

## Tool Reference by Phase

### Phase 1: Target Validation
| Tool | Purpose |
|------|---------|
| `UniProt_search` | Resolve UniProt accession |
| `MyGene_query_genes` | Get Ensembl/NCBI IDs |
| `ChEMBL_search_targets` | Get ChEMBL target ID |
| `OpenTargets_get_target_tractability_by_ensemblID` | Tractability assessment |
| `DGIdb_get_gene_druggability` | Druggability categories |
| `ChEMBL_search_binding_sites` | Binding site info |
| `InterPro_get_protein_domains` | Domain architecture |

### Phase 2: Known Ligands
| Tool | Purpose |
|------|---------|
| `ChEMBL_get_target_activities` | Bioactivity data |
| `ChEMBL_get_molecule` | Molecule details |
| `GtoPdb_get_target_interactions` | Pharmacology data |
| `OpenTargets_get_chemical_probes_by_target_ensemblID` | Chemical probes |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | Known drugs |

### Phase 1.4: Structure Prediction (NVIDIA NIM)
| Tool | Purpose |
|------|---------|
| `NvidiaNIM_alphafold2` | High-accuracy structure prediction with pLDDT |
| `NvidiaNIM_esmfold` | Fast structure prediction (max 1024 AA) |
| `NvidiaNIM_msa_search` | MSA generation for AlphaFold |

### Phase 3: Structure
| Tool | Purpose |
|------|---------|
| `PDB_search_similar_structures` | Find PDB structures |
| `get_protein_metadata_by_pdb_id` | Structure metadata |
| `get_binding_affinity_by_pdb_id` | Ligand affinities |
| `alphafold_get_prediction` | Predicted structure (AlphaFold DB) |
| `get_ligand_smiles_by_chem_comp_id` | Ligand structures |
| `emdb_search` | Search cryo-EM structures (NEW) |
| `emdb_get_entry` | Get EMDB entry details (NEW) |

### Phase 3.5: Docking Validation (NVIDIA NIM)
| Tool | Purpose |
|------|---------|
| `NvidiaNIM_diffdock` | Blind molecular docking (PDB + SDF) |
| `NvidiaNIM_boltz2` | Protein-ligand complex (sequence + SMILES) |

### Phase 4: Expansion
| Tool | Purpose |
|------|---------|
| `ChEMBL_search_similar_molecules` | Similarity search |
| `PubChem_search_compounds_by_similarity` | PubChem similarity |
| `ChEMBL_search_substructure` | Substructure search |
| `PubChem_search_compounds_by_substructure` | PubChem substructure |
| `STITCH_get_chemical_protein_interactions` | Cross-database |

### Phase 4.4: De Novo Generation (NVIDIA NIM)
| Tool | Purpose |
|------|---------|
| `NvidiaNIM_genmol` | Scaffold hopping with masked regions |
| `NvidiaNIM_molmim` | Controlled generation from reference |

### Phase 5: ADMET
| Tool | Purpose |
|------|---------|
| `ADMETAI_predict_physicochemical_properties` | Drug-likeness |
| `ADMETAI_predict_bioavailability` | Oral absorption |
| `ADMETAI_predict_toxicity` | Toxicity flags |
| `ADMETAI_predict_CYP_interactions` | CYP liabilities |
| `ChEMBL_search_compound_structural_alerts` | PAINS, alerts |

### Phase 6: Candidate Docking (NVIDIA NIM)
| Tool | Purpose |
|------|---------|
| `NvidiaNIM_diffdock` | Score all candidates by docking |
| `NvidiaNIM_boltz2` | Alternative docking from SMILES |

### Phase 6.5: Literature Evidence (NEW)
| Tool | Purpose |
|------|---------|
| `PubMed_search_articles` | Published SAR studies |
| `BioRxiv_search_preprints` | Latest biology preprints |
| `MedRxiv_search_preprints` | Clinical preprints |
| `openalex_search_works` | Citation analysis |
| `SemanticScholar_search` | AI-ranked papers |

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 | Use When |
|--------------|------------|------------|----------|
| `ChEMBL_get_target_activities` | `GtoPdb_get_target_interactions` | `PubChem_search_assays` | No ChEMBL data |
| `ChEMBL_search_similar_molecules` | `PubChem_search_compounds_by_similarity` | `STITCH_get_chemical_protein_interactions` | ChEMBL exhausted |
| `PDB_search_similar_structures` | `NvidiaNIM_alphafold2` | `alphafold_get_prediction` | No PDB structure |
| `alphafold_get_prediction` | `NvidiaNIM_alphafold2` | `NvidiaNIM_esmfold` | AlphaFold DB unavailable |
| `NvidiaNIM_alphafold2` | `NvidiaNIM_esmfold` | `alphafold_get_prediction` | AlphaFold2 NIM error |
| `NvidiaNIM_diffdock` | `NvidiaNIM_boltz2` | Skip docking, use similarity | Docking error |
| `NvidiaNIM_genmol` | `NvidiaNIM_molmim` | Manual scaffold hopping | Generation error |
| `OpenTargets_get_target_tractability` | `DGIdb_get_gene_druggability` | Document "Unknown" | Open Targets error |
| `ADMETAI_*` | SwissADME tools | Basic Lipinski | Invalid SMILES |
| `PDB_search_similar_structures` | `emdb_search` + PDB | `NvidiaNIM_alphafold2` | Membrane proteins |
| `PubMed_search_articles` | `openalex_search_works` | `SemanticScholar_search` | Literature search |
| `BioRxiv_search_preprints` | `MedRxiv_search_preprints` | Skip preprints | Preprint sources |

**NVIDIA NIM API Key Required**: Tools with `NvidiaNIM_` prefix require `NVIDIA_API_KEY` environment variable. Check availability at start:
```python
import os
nvidia_available = bool(os.environ.get("NVIDIA_API_KEY"))
# If not available, fall back to non-NIM alternatives
```

---

## Common Use Cases

### Well-Characterized Target
User: "Find novel binders for EGFR"
→ Rich ChEMBL data; focus on novel scaffolds, selectivity, ADMET

### Novel Target
User: "Find small molecules for [new target with no known ligands]"
→ Limited bioactivity; rely on structure-based assessment, similar target ligands

### Lead Optimization
User: "Find analogs of compound X for target Y"
→ Deep similarity search around specific compound; focus on SAR

### Selectivity Challenge
User: "Find selective inhibitors for kinase X vs kinase Y"
→ Include selectivity analysis; filter by off-target predictions

---

## When NOT to Use This Skill

- **Drug research** → Use tooluniverse-drug-research (existing drug profiling)
- **Target research only** → Use tooluniverse-target-research
- **Single compound ADMET** → Call ADMET tools directly
- **Literature search** → Use tooluniverse-literature-deep-research
- **Protein structure only** → Use tooluniverse-protein-structure-retrieval

Use this skill for **discovering new compounds** for a protein target.

---

## Additional Resources

- **Checklist**: [CHECKLIST.md](CHECKLIST.md) - Pre-delivery verification
- **Examples**: [EXAMPLES.md](EXAMPLES.md) - Detailed workflow examples
- **Tool corrections**: [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) - Parameter corrections
