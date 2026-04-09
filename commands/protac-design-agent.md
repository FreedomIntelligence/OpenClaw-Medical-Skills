# protac-design-agent

> AI-powered PROTAC (Proteolysis Targeting Chimera) design for targeted protein degradation, integrating ternary complex prediction, linker optimization, and ADMET modeling.

**Available tools:** Read, Bash

# PROTAC Design Agent

The **PROTAC Design Agent** provides AI-assisted design of Proteolysis Targeting Chimeras (PROTACs) for targeted protein degradation. It integrates machine learning for ternary complex prediction, linker design, E3 ligase selection, and ADMET optimization to accelerate degrader drug discovery for oncology and other therapeutic areas.

## When to Use This Skill

* When designing PROTAC degraders for a target protein.
* For optimizing linker chemistry and length.
* To predict ternary complex formation and degradation efficiency.
* When selecting optimal E3 ligase (CRBN, VHL) for the target.
* For optimizing ADMET properties of degrader molecules.

## Core Capabilities

1. **Warhead Selection**: Identify optimal target protein ligands.

2. **E3 Ligase Selection**: Choose CRBN, VHL, or other E3 recruiters.

3. **Linker Design**: Optimize linker length, chemistry, and rigidity.

4. **Ternary Complex Prediction**: Model POI-PROTAC-E3 formation.

5. **Degradation Efficiency Modeling**: Predict DC50 and Dmax.

6. **ADMET Optimization**: Balance potency with drug-like properties.

## PROTAC Components

| Component | Function | Optimization Target |
|-----------|----------|---------------------|
| Warhead | Binds target protein (POI) | Affinity, selectivity |
| E3 Ligand | Recruits E3 ubiquitin ligase | CRBN/VHL binding |
| Linker | Connects warhead to E3 ligand | Length, flexibility, solubility |

## E3 Ligase Options

| E3 Ligase | Ligand | Tissue Expression | Advantages |
|-----------|--------|-------------------|------------|
| CRBN | Thalidomide analogs | Ubiquitous | Well-characterized |
| VHL | VHL ligands | Ubiquitous | High selectivity |
| MDM2 | Nutlin analogs | Variable | p53-independent |
| IAP | SMAC mimetics | High in cancer | Dual mechanism |
| DCAF15 | Indisulam | Variable | Novel chemistry |

## Workflow

1. **Input**: Target protein structure/sequence, known ligands (optional).

2. **Warhead Design**: Generate/optimize POI binding moiety.

3. **E3 Selection**: Choose optimal E3 ligase for target/tissue.

4. **Linker Library**: Generate diverse linker options.

5. **Ternary Complex Modeling**: Predict complex formation.

6. **Ranking**: Score by predicted degradation and ADMET.

7. **Output**: Ranked PROTAC designs with synthesis routes.

## Example Usage

**User**: "Design a PROTAC to degrade BRD4 using CRBN as the E3 ligase, optimizing for oral bioavailability."

**Agent Action**:
```bash
python3 Skills/Drug_Discovery/PROTAC_Design_Agent/design_protac.py \
    --target BRD4 \
    --target_structure pdb:3MXF \
    --warhead_smiles "JQ1_core_smiles" \
    --e3_ligase CRBN \
    --linker_library peg,alkyl,piperdine \
    --linker_length_range 4,12 \
    --optimize_oral true \
    --output protac_designs/
```

## Linker Design Parameters

| Parameter | Options | Consideration |
|-----------|---------|---------------|
| Length | 2-20 atoms | Ternary complex geometry |
| Chemistry | PEG, alkyl, piperazine, triazole | Solubility, stability |
| Rigidity | Flexible vs constrained | Entropic penalty |
| Attachment | Connectivity points | Exit vector matching |
| MW Contribution | Varies | Total MW impact |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| PROTAC Structures | Designed molecules | .sdf, SMILES |
| Ternary Models | POI-PROTAC-E3 complexes | .pdb |
| Predicted DC50 | Degradation potency | .csv |
| Predicted Dmax | Maximum degradation | .csv |
| ADMET Predictions | Solubility, permeability, etc. | .csv |
| Synthesis Routes | Retrosynthetic analysis | .json |
| Ranking | Prioritized designs | .csv |

## Degradation Efficiency Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| DC50 | Concentration for 50% degradation | <100 nM |
| Dmax | Maximum degradation achieved | >90% |
| Kinetics | Time to half-degradation | <4 hours |
| Selectivity | Off-target degradation | Minimal |
| Hook Effect | High-dose attenuation | Minimal |

## AI/ML Components

**Ternary Complex Prediction**:
- AlphaFold-Multimer adaptation
- Geometric deep learning
- Molecular dynamics validation

**Degradation Modeling**:
- Quantitative degradation prediction
- Transfer learning from degrader databases
- Multi-task learning (DC50, Dmax, kinetics)

**Linker Optimization**:
- Generative models (VAE, diffusion)
- Reinforcement learning
- Multi-objective Bayesian optimization

**ADMET Prediction**:
- Property prediction models
- Chameleonicity assessment
- Oral bioavailability scoring

## Clinical Pipeline Status (2026)

| PROTAC | Target | Phase | E3 Ligase |
|--------|--------|-------|-----------|
| ARV-471 | ER | Phase 3, NDA filed | CRBN |
| ARV-110 | AR | Phase 2 | CRBN |
| BGB-16673 | BTK | Phase 3 | CRBN |
| NX-2127 | BTK | Phase 2 | CRBN |
| KT-474 | IRAK4 | Phase 2 | CRBN |

## Design Considerations

| Factor | PROTAC Challenge | Solution |
|--------|------------------|----------|
| High MW | Poor permeability | Chameleonicity |
| Low Solubility | Limited exposure | Solubilizing groups |
| Hook Effect | Reduced efficacy at high doses | Optimize binding balance |
| E3 Saturation | Competition with other PROTACs | Target expression |

## Prerequisites

* Python 3.10+
* RDKit, Open Babel
* AlphaFold2/3
* Molecular dynamics (GROMACS/OpenMM)
* PyTorch for ML models

## Related Skills

* Molecular_Glue_Discovery_Agent - Glue degraders
* TPD_Ternary_Complex_Agent - Complex prediction
* Molecular_Docking_Agent - Docking analysis
* ADMET_Prediction_Agent - Property prediction

## ADMET Optimization Strategies

| Property | Challenge | Approach |
|----------|-----------|----------|
| Permeability | High MW limits | Intramolecular H-bonds |
| Solubility | Lipophilicity | Polar linker groups |
| Metabolic Stability | Linker metabolism | Stable chemistries |
| Clearance | High metabolism | Optimize logD |

## Special Considerations

1. **Target Suitability**: Not all proteins are degradable
2. **E3 Expression**: Check tissue-specific E3 levels
3. **Ubiquitination Sites**: Surface lysines needed
4. **Resistance**: Target mutations, E3 downregulation
5. **Selectivity**: Validate off-target degradation

## Quality Control Metrics

| QC Check | Threshold | Rationale |
|----------|-----------|-----------|
| Ternary Complex Score | >0.7 | Productive complex |
| Linker Strain | <5 kcal/mol | Favorable geometry |
| ADMET Score | >0.5 | Drug-like properties |
| Synthetic Accessibility | <5 | Feasible synthesis |

## Author

AI Group - Biomedical AI Platform
