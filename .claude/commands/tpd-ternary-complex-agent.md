# tpd-ternary-complex-agent

> AI-powered ternary complex prediction for targeted protein degradation, modeling POI-degrader-E3 ligase assemblies to optimize PROTAC and molecular glue efficacy.

**Available tools:** Read, Bash

# TPD Ternary Complex Agent

The **TPD Ternary Complex Agent** specializes in predicting and modeling ternary complex formation for targeted protein degradation (TPD). It uses AlphaFold-Multimer, molecular dynamics, and deep learning to model Protein of Interest (POI)-degrader-E3 ligase assemblies, enabling rational optimization of PROTACs and molecular glues.

## When to Use This Skill

* When predicting ternary complex formation for degrader design.
* For understanding POI-E3 interface complementarity.
* To optimize linker geometry based on complex structure.
* When assessing ubiquitination site accessibility.
* For comparing E3 ligase options for a target.

## Core Capabilities

1. **Ternary Structure Prediction**: Model full POI-degrader-E3 complexes.

2. **Interface Analysis**: Assess protein-protein interactions in complex.

3. **Linker Geometry Optimization**: Guide linker design from structures.

4. **Ubiquitination Site Analysis**: Identify accessible lysines for Ub transfer.

5. **Cooperativity Scoring**: Predict binding cooperativity (α factor).

6. **E3 Comparison**: Evaluate different E3 ligases for same target.

## Supported E3 Ligases

| E3 Ligase | Structure | Complex Quality |
|-----------|-----------|-----------------|
| CRBN-DDB1-CUL4A | High resolution | Excellent |
| VHL-ELOB-ELOC-CUL2 | High resolution | Excellent |
| MDM2 | Good | Good |
| IAP (cIAP1/XIAP) | Moderate | Moderate |
| DCAF15-DDB1 | Emerging | Developing |
| KEAP1 | High resolution | Good |

## Workflow

1. **Input**: POI structure, degrader, E3 ligase specification.

2. **Binary Modeling**: Model POI-warhead and E3-ligand complexes.

3. **Ternary Assembly**: Predict full ternary complex structure.

4. **MD Refinement**: Molecular dynamics for complex stability.

5. **Interface Scoring**: Quantify POI-E3 interface quality.

6. **Lysine Analysis**: Map ubiquitination sites.

7. **Output**: Ternary structure, scores, optimization suggestions.

## Example Usage

**User**: "Model the ternary complex for this BRD4 PROTAC with VHL to understand the protein-protein interface."

**Agent Action**:
```bash
python3 Skills/Drug_Discovery/TPD_Ternary_Complex_Agent/predict_ternary.py \
    --poi_structure brd4_bd1.pdb \
    --warhead_pose brd4_warhead_docked.sdf \
    --e3_ligase VHL \
    --e3_ligand vhl_ligand.sdf \
    --protac_smiles "PROTAC_SMILES_STRING" \
    --linker_conformations 100 \
    --md_refinement true \
    --output ternary_complex_results/
```

## Ternary Complex Scoring

| Score Component | Weight | Interpretation |
|-----------------|--------|----------------|
| Interface Area | 20% | Larger = more stable |
| Shape Complementarity | 25% | Better fit = stability |
| Electrostatics | 20% | Charge matching |
| Linker Strain | 15% | Lower = better geometry |
| Complex Stability (ΔG) | 20% | Favorable energetics |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Ternary Structure | POI-PROTAC-E3 model | .pdb |
| Confidence Scores | pLDDT, PAE | .json |
| Interface Map | Contact residues | .csv |
| Lysine Accessibility | Ubiquitination sites | .csv |
| Cooperativity | α factor estimate | .json |
| Optimization Suggestions | Design recommendations | .md |
| MD Trajectory | Stability simulation | .xtc |

## Interface Quality Metrics

| Metric | Definition | Good Value |
|--------|------------|------------|
| Buried Surface Area | Contact area | >800 Å² |
| Shape Complementarity | Sc score | >0.65 |
| Gap Volume Index | Interface packing | <2.0 |
| Hydrogen Bonds | Intermolecular H-bonds | >3 |
| Salt Bridges | Charged interactions | >1 |

## AI/ML Components

**Structure Prediction**:
- AlphaFold-Multimer for ternary modeling
- Template-based homology
- Deep learning interface prediction

**Conformational Sampling**:
- Linker conformer generation
- Ensemble docking
- MD for dynamics

**Scoring Functions**:
- Physics-based energy
- ML-derived interface scores
- Cooperativity prediction models

## Cooperativity Analysis

| α Factor | Interpretation | Mechanism |
|----------|----------------|-----------|
| α > 1 | Positive cooperativity | E3 binding enhances POI binding |
| α = 1 | No cooperativity | Independent binding |
| α < 1 | Negative cooperativity | E3 binding reduces POI binding |

## Ubiquitination Site Requirements

| Requirement | Threshold | Rationale |
|-------------|-----------|-----------|
| Surface Accessibility | >30 Å² | E2 access |
| Distance to E2~Ub | <15 Å | Transfer distance |
| Lysine Environment | Favorable | Not buried |
| Number of Sites | ≥1 | At least one Lys |

## E3 Ligase Comparison

| E3 | Advantages | Considerations |
|----|------------|----------------|
| CRBN | Broad applicability, many ligands | Some immune targets |
| VHL | High selectivity, well-validated | Limited tissue in some organs |
| MDM2 | No CRBN competition | Fewer validated targets |
| IAP | Cancer expression, dual mechanism | Complex biology |

## Prerequisites

* Python 3.10+
* AlphaFold-Multimer
* GROMACS/OpenMM for MD
* RDKit, BioPython
* GPU compute (recommended)

## Related Skills

* PROTAC_Design_Agent - Full PROTAC design
* Molecular_Glue_Discovery_Agent - Glue discovery
* Protein_Protein_Docking_Agent - PPI docking
* Molecular_Dynamics_Agent - MD simulations

## Validation Approaches

| Method | Purpose | Confidence |
|--------|---------|------------|
| Crystal Structure | Ground truth | Highest |
| Cryo-EM | Large complexes | High |
| HDX-MS | Interface mapping | Moderate-High |
| Crosslinking MS | Distance constraints | Moderate |
| Mutagenesis | Interface validation | Functional |

## Special Considerations

1. **Conformational Flexibility**: Multiple ternary conformations possible
2. **Linker Dynamics**: Flexible linkers sample many geometries
3. **Induced Fit**: Proteins may reorganize upon complex formation
4. **Crystal Packing**: May influence observed geometries
5. **Kinetic vs Thermodynamic**: Ternary stability ≠ degradation efficiency

## Design Implications

| Structural Finding | Design Action |
|--------------------|---------------|
| Poor interface | Change E3 or target site |
| Long distance | Longer linker |
| Steric clash | Shorter linker or different exit vector |
| No accessible Lys | Different binding mode |
| High flexibility | Constrained linker |

## Quality Control

| QC Metric | Threshold | Interpretation |
|-----------|-----------|----------------|
| pLDDT (interface) | >70 | Reliable prediction |
| PAE (POI-E3) | <10 Å | Good relative positioning |
| MD RMSD | <3 Å | Stable complex |
| Clash Score | <50 | Good packing |

## Author

AI Group - Biomedical AI Platform
