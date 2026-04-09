# tooluniverse-protein-therapeutic-design

> Design novel protein therapeutics (binders, enzymes, scaffolds) using AI-guided de novo design. Uses RFdiffusion for backbone generation, ProteinMPNN for sequence design, ESMFold/AlphaFold2 for validation. Use when asked to design protein binders, therapeutic proteins, or engineer protein function.

# Therapeutic Protein Designer

AI-guided de novo protein design using RFdiffusion backbone generation, ProteinMPNN sequence optimization, and structure validation for therapeutic protein development.

**KEY PRINCIPLES**:
1. **Structure-first design** - Generate backbone geometry before sequence
2. **Target-guided** - Design binders with target structure in mind
3. **Iterative validation** - Predict structure to validate designs
4. **Developability-aware** - Consider aggregation, immunogenicity, expression
5. **Evidence-graded** - Grade designs by confidence metrics
6. **Actionable output** - Provide sequences ready for experimental testing
7. **English-first queries** - Always use English terms in tool calls (protein names, target names), even if the user writes in another language. Only try original-language terms as a fallback. Respond in the user's language

---

## When to Use

Apply when user asks:
- "Design a protein binder for [target]"
- "Create a therapeutic protein against [protein/epitope]"
- "Design a protein scaffold with [property]"
- "Optimize this protein sequence for [function]"
- "Design a de novo enzyme for [reaction]"
- "Generate protein variants for [target binding]"

---

## Critical Workflow Requirements

### 1. Report-First Approach (MANDATORY)

1. **Create the report file FIRST**:
   - File name: `[TARGET]_protein_design_report.md`
   - Initialize with section headers
   - Add placeholder: `[Designing...]`

2. **Progressively update** as designs are generated

3. **Output separate files**:
   - `[TARGET]_designed_sequences.fasta` - All designed sequences
   - `[TARGET]_top_candidates.csv` - Ranked candidates with metrics

### 2. Design Documentation (MANDATORY)

Every design MUST include:

```markdown
### Design: Binder_001

**Sequence**: MVLSPADKTN...
**Length**: 85 amino acids
**Target**: PD-L1 (UniProt: Q9NZQ7)
**Method**: RFdiffusion → ProteinMPNN → ESMFold validation

**Quality Metrics**:
| Metric | Value | Interpretation |
|--------|-------|----------------|
| pLDDT | 88.5 | High confidence |
| pTM | 0.82 | Good fold |
| ProteinMPNN score | -2.3 | Favorable |
| Predicted binding | Strong | Based on interface pLDDT |

*Source: NVIDIA NIM via `NvidiaNIM_rfdiffusion`, `NvidiaNIM_proteinmpnn`, `NvidiaNIM_esmfold`*
```

---

## Phase 0: Tool Verification

### NVIDIA NIM Tools Required

| Tool | Purpose | API Key Required |
|------|---------|------------------|
| `NvidiaNIM_rfdiffusion` | Backbone generation | Yes |
| `NvidiaNIM_proteinmpnn` | Sequence design | Yes |
| `NvidiaNIM_esmfold` | Fast structure validation | Yes |
| `NvidiaNIM_alphafold2` | High-accuracy validation | Yes |
| `NvidiaNIM_esm2_650m` | Sequence embeddings | Yes |

### Parameter Verification

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `NvidiaNIM_rfdiffusion` | `num_steps` | `diffusion_steps` |
| `NvidiaNIM_proteinmpnn` | `pdb` | `pdb_string` |
| `NvidiaNIM_esmfold` | `seq` | `sequence` |

---

## Workflow Overview

```
Phase 1: Target Characterization
├── Get target structure (PDB, EMDB cryo-EM, or AlphaFold)
├── Identify binding epitope
├── Analyze existing binders
├── Check EMDB for membrane protein structures (NEW)
└── OUTPUT: Target profile
    ↓
Phase 2: Backbone Generation (RFdiffusion)
├── Define design constraints
├── Generate multiple backbones
├── Filter by geometry quality
└── OUTPUT: Candidate backbones
    ↓
Phase 3: Sequence Design (ProteinMPNN)
├── Design sequences for each backbone
├── Sample multiple sequences per backbone
├── Score by ProteinMPNN likelihood
└── OUTPUT: Designed sequences
    ↓
Phase 4: Structure Validation
├── Predict structure (ESMFold/AlphaFold2)
├── Compare to designed backbone
├── Assess fold quality (pLDDT, pTM)
└── OUTPUT: Validated designs
    ↓
Phase 5: Developability Assessment
├── Aggregation propensity
├── Expression likelihood
├── Immunogenicity prediction
└── OUTPUT: Developability scores
    ↓
Phase 6: Report Synthesis
├── Ranked candidate list
├── Experimental recommendations
├── Next steps
└── OUTPUT: Final report
```

---

## Phase 1: Target Characterization

### 1.1 Get Target Structure

```python
def get_target_structure(tu, target_id):
    """Get target structure from PDB, EMDB, or predict."""
    
    # Try PDB first (X-ray/NMR)
    pdb_results = tu.tools.PDB_search_by_uniprot(uniprot_id=target_id)
    
    if pdb_results:
        # Get highest resolution structure
        best_pdb = sorted(pdb_results, key=lambda x: x['resolution'])[0]
        structure = tu.tools.PDB_get_structure(pdb_id=best_pdb['pdb_id'])
        return {'source': 'PDB', 'pdb_id': best_pdb['pdb_id'], 
                'resolution': best_pdb['resolution'], 'structure': structure}
    
    # Try EMDB for cryo-EM structures (valuable for membrane proteins)
    protein_info = tu.tools.UniProt_get_protein_by_accession(accession=target_id)
    emdb_results = tu.tools.emdb_search(
        query=protein_info['proteinDescription']['recommendedName']['fullName']['value']
    )
    
    if emdb_results and len(emdb_results) > 0:
        # Get highest resolution cryo-EM entry
        best_emdb = sorted(emdb_results, key=lambda x: x.get('resolution', 99))[0]
        # Get associated PDB model if available
        emdb_details = tu.tools.emdb_get_entry(entry_id=best_emdb['emdb_id'])
        if emdb_details.get('pdb_ids'):
            structure = tu.tools.PDB_get_structure(pdb_id=emdb_details['pdb_ids'][0])
            return {'source': 'EMDB cryo-EM', 'emdb_id': best_emdb['emdb_id'],
                    'pdb_id': emdb_details['pdb_ids'][0], 
                    'resolution': best_emdb.get('resolution'), 'structure': structure}
    
    # Fallback to AlphaFold prediction
    sequence = tu.tools.UniProt_get_protein_sequence(accession=target_id)
    structure = tu.tools.NvidiaNIM_alphafold2(
        sequence=sequence['sequence'],
        algorithm="mmseqs2"
    )
    return {'source': 'AlphaFold2 (predicted)', 'structure': structure}
```

### 1.1b EMDB for Membrane Proteins (NEW)

**When to prioritize EMDB**: Membrane proteins, large complexes, and targets where conformational states matter.

```python
def get_cryoem_structures(tu, target_name):
    """Get cryo-EM structures for membrane proteins/complexes."""
    
    # Search EMDB
    emdb_results = tu.tools.emdb_search(
        query=f"{target_name} membrane OR receptor"
    )
    
    structures = []
    for entry in emdb_results[:5]:
        details = tu.tools.emdb_get_entry(entry_id=entry['emdb_id'])
        structures.append({
            'emdb_id': entry['emdb_id'],
            'resolution': entry.get('resolution', 'N/A'),
            'title': entry.get('title', 'N/A'),
            'conformational_state': details.get('state', 'Unknown'),
            'pdb_models': details.get('pdb_ids', [])
        })
    
    return structures
```

**Output for Report**:

```markdown
### 1.1b Cryo-EM Structures (EMDB)

| EMDB ID | Resolution | PDB Model | Conformation |
|---------|------------|-----------|--------------|
| EMD-12345 | 2.8 Å | 7ABC | Active state |
| EMD-23456 | 3.1 Å | 8DEF | Inactive state |

**Note**: Cryo-EM structures capture physiologically relevant conformations for membrane protein targets.

*Source: EMDB*
```

### 1.2 Identify Binding Epitope

```python
def identify_epitope(tu, target_structure, epitope_residues=None):
    """Identify or validate binding epitope."""
    
    if epitope_residues:
        # User-specified epitope
        return {'residues': epitope_residues, 'source': 'user-defined'}
    
    # Find surface-exposed regions
    # Use structural analysis to identify potential epitopes
    return analyze_surface(target_structure)
```

### 1.3 Output for Report

```markdown
## 1. Target Characterization

### 1.1 Target Information

| Property | Value |
|----------|-------|
| **Target** | PD-L1 (Programmed death-ligand 1) |
| **UniProt** | Q9NZQ7 |
| **Structure source** | PDB: 4ZQK (2.0 Å resolution) |
| **Binding epitope** | IgV domain, residues 19-127 |
| **Known binders** | Atezolizumab, durvalumab, avelumab |

### 1.2 Epitope Analysis

| Residue Range | Type | Surface Area | Druggability |
|---------------|------|--------------|--------------|
| 54-68 | Loop | 850 Å² | High |
| 115-125 | Beta strand | 420 Å² | Medium |
| 19-30 | N-terminus | 380 Å² | Medium |

**Selected Epitope**: Residues 54-68 (PD-1 binding interface)

*Source: PDB 4ZQK, surface analysis*
```

---

## Phase 2: Backbone Generation

### 2.1 RFdiffusion Design

```python
def generate_backbones(tu, design_params):
    """Generate de novo backbones using RFdiffusion."""
    
    backbones = tu.tools.NvidiaNIM_rfdiffusion(
        diffusion_steps=design_params.get('steps', 50),
        # Additional parameters depending on design type
    )
    
    return backbones
```

### 2.2 Design Modes

| Mode | Use Case | Key Parameters |
|------|----------|----------------|
| **Unconditional** | De novo scaffold | `diffusion_steps` only |
| **Binder design** | Target-guided binder | `target_structure`, `hotspot_residues` |
| **Motif scaffolding** | Functional motif embedding | `motif_sequence`, `motif_structure` |

### 2.3 Output for Report

```markdown
## 2. Backbone Generation

### 2.1 Design Parameters

| Parameter | Value |
|-----------|-------|
| **Method** | RFdiffusion via NVIDIA NIM |
| **Design mode** | Unconditional scaffold generation |
| **Diffusion steps** | 50 |
| **Number generated** | 10 backbones |

### 2.2 Generated Backbones

| Backbone | Length | Topology | Quality |
|----------|--------|----------|---------|
| BB_001 | 85 aa | 3-helix bundle | Good |
| BB_002 | 92 aa | Beta sandwich | Good |
| BB_003 | 78 aa | Alpha-beta | Good |
| BB_004 | 88 aa | All-alpha | Moderate |
| BB_005 | 95 aa | Mixed | Good |

**Selected for sequence design**: BB_001, BB_002, BB_003, BB_005 (top 4)

*Source: NVIDIA NIM via `NvidiaNIM_rfdiffusion`*
```

---

## Phase 3: Sequence Design

### 3.1 ProteinMPNN Design

```python
def design_sequences(tu, backbone_pdb, num_sequences=8):
    """Design sequences for backbone using ProteinMPNN."""
    
    sequences = tu.tools.NvidiaNIM_proteinmpnn(
        pdb_string=backbone_pdb,
        num_sequences=num_sequences,
        temperature=0.1  # Lower = more conservative
    )
    
    return sequences
```

### 3.2 Sampling Parameters

| Parameter | Conservative | Moderate | Diverse |
|-----------|--------------|----------|---------|
| Temperature | 0.1 | 0.2 | 0.5 |
| Sequences per backbone | 4 | 8 | 16 |
| Use case | Validated scaffold | Exploration | Diversity |

### 3.3 Output for Report

```markdown
## 3. Sequence Design

### 3.1 Design Parameters

| Parameter | Value |
|-----------|-------|
| **Method** | ProteinMPNN via NVIDIA NIM |
| **Temperature** | 0.1 (conservative) |
| **Sequences per backbone** | 8 |
| **Total sequences** | 32 |

### 3.2 Designed Sequences (Top 10 by Score)

| Rank | Backbone | Sequence ID | Length | MPNN Score | Predicted pI |
|------|----------|-------------|--------|------------|--------------|
| 1 | BB_001 | Seq_001_A | 85 | -1.89 | 6.2 |
| 2 | BB_002 | Seq_002_C | 92 | -1.95 | 5.8 |
| 3 | BB_001 | Seq_001_B | 85 | -2.01 | 7.1 |
| 4 | BB_003 | Seq_003_A | 78 | -2.08 | 6.5 |
| 5 | BB_005 | Seq_005_B | 95 | -2.12 | 5.4 |

### 3.3 Top Sequence: Seq_001_A

```
>Seq_001_A (85 aa, MPNN score: -1.89)
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH
GSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKL
```

*Source: NVIDIA NIM via `NvidiaNIM_proteinmpnn`*
```

---

## Phase 4: Structure Validation

### 4.1 ESMFold Validation

```python
def validate_structure(tu, sequence):
    """Validate designed sequence by structure prediction."""
    
    # Fast validation with ESMFold
    predicted = tu.tools.NvidiaNIM_esmfold(sequence=sequence)
    
    # Extract quality metrics
    plddt = extract_plddt(predicted)
    ptm = extract_ptm(predicted)
    
    return {
        'structure': predicted,
        'mean_plddt': np.mean(plddt),
        'ptm': ptm,
        'passes': np.mean(plddt) > 70 and ptm > 0.7
    }
```

### 4.2 Validation Criteria

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Mean pLDDT | >70 | Confident fold |
| pTM | >0.7 | Good global topology |
| RMSD to backbone | <2 Å | Design recapitulated |

### 4.3 Output for Report

```markdown
## 4. Structure Validation

### 4.1 Validation Results

| Sequence | pLDDT | pTM | RMSD to Design | Status |
|----------|-------|-----|----------------|--------|
| Seq_001_A | 88.5 | 0.85 | 1.2 Å | ✓ PASS |
| Seq_002_C | 82.3 | 0.79 | 1.5 Å | ✓ PASS |
| Seq_001_B | 85.1 | 0.82 | 1.3 Å | ✓ PASS |
| Seq_003_A | 79.8 | 0.76 | 1.8 Å | ✓ PASS |
| Seq_005_B | 68.2 | 0.65 | 2.8 Å | ✗ FAIL |

### 4.2 Top Validated Design: Seq_001_A

| Region | Residues | pLDDT | Interpretation |
|--------|----------|-------|----------------|
| Helix 1 | 1-28 | 92.3 | Very high confidence |
| Loop 1 | 29-35 | 78.4 | Moderate confidence |
| Helix 2 | 36-58 | 91.8 | Very high confidence |
| Loop 2 | 59-65 | 75.2 | Moderate confidence |
| Helix 3 | 66-85 | 90.1 | Very high confidence |

**Overall**: Well-folded 3-helix bundle with high confidence core

*Source: NVIDIA NIM via `NvidiaNIM_esmfold`*
```

---

## Phase 5: Developability Assessment

### 5.1 Aggregation Propensity

```python
def assess_aggregation(sequence):
    """Assess aggregation propensity."""
    
    # Calculate hydrophobic patches
    # Calculate isoelectric point
    # Identify aggregation-prone motifs
    
    return {
        'aggregation_score': score,
        'hydrophobic_patches': patches,
        'risk_level': 'Low' if score < 0.5 else 'Medium' if score < 0.7 else 'High'
    }
```

### 5.2 Developability Metrics

| Metric | Favorable | Marginal | Unfavorable |
|--------|-----------|----------|-------------|
| Aggregation score | <0.5 | 0.5-0.7 | >0.7 |
| Isoelectric point | 5-9 | 4-5 or 9-10 | <4 or >10 |
| Hydrophobic patches | <3 | 3-5 | >5 |
| Cysteine count | 0 or even | Odd | Multiple unpaired |

### 5.3 Output for Report

```markdown
## 5. Developability Assessment

### 5.1 Developability Scores

| Design | Aggregation | pI | Cysteines | Expression | Overall |
|--------|-------------|-----|-----------|------------|---------|
| Seq_001_A | 0.32 (Low) | 6.2 | 0 | High | ★★★ |
| Seq_002_C | 0.45 (Low) | 5.8 | 2 (paired) | Medium | ★★☆ |
| Seq_001_B | 0.38 (Low) | 7.1 | 0 | High | ★★★ |
| Seq_003_A | 0.58 (Med) | 6.5 | 0 | Medium | ★★☆ |

### 5.2 Recommendations

**Best candidate for expression**: Seq_001_A
- Low aggregation propensity
- Neutral pI (easy purification)
- No cysteines (no misfolding risk)
- Predicted high E. coli expression

*Source: Sequence analysis*
```

---

## Report Template

```markdown
# Therapeutic Protein Design Report: [TARGET]

**Generated**: [Date] | **Query**: [Original query] | **Status**: In Progress

---

## Executive Summary
[Designing...]

---

## 1. Target Characterization
### 1.1 Target Information
[Designing...]
### 1.2 Binding Epitope
[Designing...]

---

## 2. Backbone Generation
### 2.1 Design Parameters
[Designing...]
### 2.2 Generated Backbones
[Designing...]

---

## 3. Sequence Design
### 3.1 ProteinMPNN Results
[Designing...]
### 3.2 Top Sequences
[Designing...]

---

## 4. Structure Validation
### 4.1 ESMFold Validation
[Designing...]
### 4.2 Quality Metrics
[Designing...]

---

## 5. Developability Assessment
### 5.1 Scores
[Designing...]
### 5.2 Recommendations
[Designing...]

---

## 6. Final Candidates
### 6.1 Ranked List
[Designing...]
### 6.2 Sequences for Testing
[Designing...]

---

## 7. Experimental Recommendations
[Designing...]

---

## 8. Data Sources
[Will be populated...]
```

---

## Evidence Grading

| Tier | Symbol | Criteria |
|------|--------|----------|
| **T1** | ★★★ | pLDDT >85, pTM >0.8, low aggregation, neutral pI |
| **T2** | ★★☆ | pLDDT >75, pTM >0.7, acceptable developability |
| **T3** | ★☆☆ | pLDDT >70, pTM >0.65, developability concerns |
| **T4** | ☆☆☆ | Failed validation or major developability issues |

---

## Completeness Checklist

### Phase 1: Target
- [ ] Target structure obtained (PDB or predicted)
- [ ] Binding epitope identified
- [ ] Existing binders noted

### Phase 2: Backbones
- [ ] ≥5 backbones generated
- [ ] Top 3-5 selected for sequence design
- [ ] Selection criteria documented

### Phase 3: Sequences
- [ ] ≥8 sequences per backbone designed
- [ ] MPNN scores reported
- [ ] Top 10 sequences listed

### Phase 4: Validation
- [ ] All sequences validated by ESMFold
- [ ] pLDDT and pTM reported
- [ ] Pass/fail criteria applied
- [ ] ≥3 passing designs

### Phase 5: Developability
- [ ] Aggregation assessed
- [ ] pI calculated
- [ ] Expression prediction
- [ ] Final ranking

### Phase 6: Deliverables
- [ ] Ranked candidate list
- [ ] FASTA file with sequences
- [ ] Experimental recommendations

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `NvidiaNIM_rfdiffusion` | Manual backbone design | Scaffold from PDB |
| `NvidiaNIM_proteinmpnn` | Rosetta ProteinMPNN | Manual sequence design |
| `NvidiaNIM_esmfold` | `NvidiaNIM_alphafold2` | AlphaFold DB |
| PDB structure | `NvidiaNIM_alphafold2` | AlphaFold DB |

---

## Tool Reference

See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation.
