# molecular-glue-discovery-agent

> AI-powered molecular glue discovery for targeted protein degradation, enabling neo-substrate recruitment and undruggable target degradation through E3 ligase interface modulation.

**Available tools:** Read, Bash

# Molecular Glue Discovery Agent

The **Molecular Glue Discovery Agent** enables AI-driven discovery of molecular glue degraders that induce protein-protein interactions between E3 ligases and neo-substrates for targeted protein degradation. Unlike PROTACs, molecular glues are smaller, more drug-like molecules that can access previously "undruggable" targets through induced proximity mechanisms.

## When to Use This Skill

* When discovering new molecular glue scaffolds.
* For identifying neo-substrate targets for existing glues.
* To design glues for specific E3-substrate pairs.
* When optimizing glue selectivity and potency.
* For virtual screening of glue candidates.

## Core Capabilities

1. **Glue Scaffold Discovery**: Identify novel molecular glue chemotypes.

2. **Neo-Substrate Prediction**: Predict proteins degraded by glues.

3. **Interface Modeling**: Model E3-glue-substrate ternary interfaces.

4. **Selectivity Optimization**: Design for specific substrate profiles.

5. **SAR Analysis**: Structure-activity relationship modeling.

6. **Virtual Screening**: Screen compounds for glue activity.

## Molecular Glue Mechanisms

| Class | E3 Ligase | Mechanism | Example |
|-------|-----------|-----------|---------|
| IMiDs | CRBN | Degron recognition | Lenalidomide |
| CELMoDs | CRBN | Enhanced IKZF binding | Iberdomide |
| DCAF15 Glues | DCAF15 | Splicing factor degradation | Indisulam |
| CDK12 Glues | DDB1-CRBN | Cyclin K degradation | CR8 derivatives |
| β-catenin Glues | Novel | WNT pathway targets | Emerging |

## Key Neo-Substrates

| Substrate | Glue Class | Disease Relevance |
|-----------|------------|-------------------|
| IKZF1/3 | IMiDs | Multiple myeloma |
| CK1α | Lenalidomide | MDS del(5q) |
| GSPT1 | CC-885 | AML |
| RBM39 | Indisulam | Solid tumors |
| Cyclin K | CR8 | Cancer |
| SALL4 | Thalidomide | Teratogenicity |

## Workflow

1. **Input**: Target substrate, E3 ligase, screening library.

2. **Interface Analysis**: Model E3 surface and potential binding sites.

3. **Virtual Screening**: Screen compounds for interface binding.

4. **Glue Scoring**: Predict neo-substrate recruitment potential.

5. **Selectivity Analysis**: Predict off-target degradation.

6. **Optimization**: Iterative design for potency/selectivity.

7. **Output**: Ranked glue candidates with predicted profiles.

## Example Usage

**User**: "Discover molecular glues that degrade IKZF1 through CRBN with improved selectivity over IKZF3."

**Agent Action**:
```bash
python3 Skills/Drug_Discovery/Molecular_Glue_Discovery_Agent/discover_glue.py \
    --target_substrate IKZF1 \
    --e3_ligase CRBN \
    --selectivity_against IKZF3 \
    --scaffold_library imid_derivatives.sdf \
    --interface_model crbn_ikzf1_complex.pdb \
    --n_candidates 100 \
    --output glue_discovery/
```

## Glue Design Parameters

| Parameter | Consideration | Optimization |
|-----------|---------------|--------------|
| Interface Complementarity | E3-substrate fit | Shape/electrostatics |
| Degron Recognition | Substrate degron motifs | Motif compatibility |
| Binding Cooperativity | Positive cooperativity | Enhanced ternary |
| Selectivity | Off-target degradation | Substrate specificity |
| Drug Properties | MW, solubility, permeability | Standard optimization |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Glue Candidates | Ranked molecules | .sdf, SMILES |
| Predicted Substrates | Neo-substrate profiles | .csv |
| Interface Models | Ternary complex structures | .pdb |
| Selectivity Scores | On-target vs off-target | .csv |
| Degradation Predictions | DC50, Dmax estimates | .csv |
| SAR Analysis | Structure-activity trends | .json |

## AI/ML Components

**Interface Prediction**:
- Protein-protein docking
- Molecular surface analysis
- Deep learning interface scoring

**Neo-Substrate Discovery**:
- Degron motif prediction
- Proteome-wide screening
- Structural similarity to known substrates

**Glue Optimization**:
- Generative chemistry
- Multi-objective optimization
- Active learning for synthesis prioritization

## Glue vs PROTAC Comparison

| Feature | Molecular Glue | PROTAC |
|---------|----------------|--------|
| Molecular Weight | <500 Da | 700-1500 Da |
| Target Discovery | Serendipitous/AI | Rational |
| Selectivity | Can be exquisite | Often broader |
| Substrate Range | Induced neo-substrates | Direct binders |
| Oral Bioavailability | Generally better | Challenging |

## Clinical Pipeline (2026)

| Drug | Mechanism | Target | Phase |
|------|-----------|--------|-------|
| Iberdomide (CC-220) | CELMoD | IKZF1/3, Aiolos | Phase 3 |
| Mezigdomide (CC-92480) | CELMoD | IKZF1/3 | Phase 3 |
| Golcadomide (CC-99282) | CELMoD | IKZF1/3 | Phase 2 |
| CFT7455 | IKZF1/3 | IKZF1/3 | Phase 1 |

## Degron Motif Analysis

| Degron Type | Sequence Features | E3 Recognition |
|-------------|-------------------|----------------|
| Zinc Finger | C2H2 ZF domain | CRBN-IMiD |
| Phosphodegron | pSer/pThr motifs | SCF E3s |
| N-degron | N-terminal residues | UBR1/2 |
| Hydrophobic | Exposed hydrophobics | Quality control |

## Prerequisites

* Python 3.10+
* RDKit, Molecular modeling tools
* AlphaFold2/3, docking software
* Deep learning frameworks
* Protein structure databases

## Related Skills

* PROTAC_Design_Agent - Bifunctional degraders
* TPD_Ternary_Complex_Agent - Complex modeling
* Virtual_Screening_Agent - High-throughput screening
* Protein_Protein_Docking_Agent - PPI modeling

## Discovery Strategies

| Strategy | Approach | Success Examples |
|----------|----------|------------------|
| Phenotypic Screening | Degradation readout | IMiDs, indisulam |
| Target-Based | E3-substrate docking | Rational glues |
| Chemoproteomics | Pull-down identification | Neo-substrate discovery |
| AI-Guided | Computational prediction | Emerging |

## Special Considerations

1. **Polypharmacology**: Glues often degrade multiple substrates
2. **Species Differences**: Neo-substrates may differ across species
3. **Resistance**: Substrate mutations, E3 downregulation
4. **Toxicity**: Off-target degradation (e.g., SALL4)
5. **Hook Effect**: Less common than PROTACs

## Quality Control

| Metric | Purpose | Threshold |
|--------|---------|-----------|
| Interface Score | Complex stability | >0.6 |
| Cooperativity | Enhanced binding | >1.5 |
| Selectivity Index | On/off-target ratio | >10 |
| Drug-likeness | Developability | Lipinski compliant |

## Future Directions

| Direction | Status | Potential |
|-----------|--------|-----------|
| New E3 Ligases | Active research | Expanded target space |
| Protein-Protein Glues | Emerging | Beyond degradation |
| AI-First Discovery | Advancing | Reduced serendipity |
| Combination Glues | Conceptual | Multi-target degradation |

## Author

AI Group - Biomedical AI Platform
