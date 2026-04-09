# nk-cell-therapy-agent

> AI-powered NK cell therapy design for cancer immunotherapy including CAR-NK engineering, memory-like NK generation, and KIR/HLA matching optimization.

**Available tools:** Read, Bash

# NK Cell Therapy Agent

The **NK Cell Therapy Agent** provides AI-driven design and optimization of natural killer cell therapies for cancer treatment. It covers CAR-NK engineering, cytokine-induced memory-like (CIML) NK generation, KIR/HLA matching, and NK cell expansion optimization.

## When to Use This Skill

* When designing CAR-NK constructs for tumor targeting.
* To optimize KIR/HLA mismatch for allogeneic NK therapy.
* For generating memory-like NK cells with enhanced persistence.
* When predicting NK cell activation against specific tumor types.
* To analyze NK cell receptor repertoires and function.

## Core Capabilities

1. **CAR-NK Design**: Design chimeric antigen receptors optimized for NK cell biology (NK-specific signaling domains).

2. **KIR/HLA Matching**: Predict KIR-HLA interactions for donor selection in allogeneic therapy.

3. **Memory-Like NK Generation**: Optimize CIML protocol with IL-12/15/18 cytokine preactivation.

4. **Expansion Optimization**: ML models for feeder-free NK expansion conditions.

5. **Tumor Target Prediction**: Match NK receptor profiles to tumor ligand expression.

6. **Persistence Enhancement**: Engineering strategies for improved in vivo survival.

## NK Cell Advantages Over T Cells

| Feature | NK Cells | T Cells |
|---------|----------|---------|
| MHC requirement | No | Yes |
| Allogeneic use | Yes (no GVHD) | Limited (GVHD risk) |
| CRS risk | Lower | Higher |
| Off-the-shelf | Yes | Autologous typical |
| Antigen escape | Multiple receptors | Single CAR |
| Persistence | Shorter | Longer |

## CAR-NK Architecture

```
[scFv] - [Hinge] - [Transmembrane] - [Costimulatory] - [Signaling]

NK-Optimized Domains:
- Transmembrane: NKG2D, CD8α, or CD28
- Costimulatory: 2B4, DAP10, or CD28
- Signaling: CD3ζ (with NK-specific adaptations)
- Additional: Cytokine secretion (IL-15), suicide switch
```

## Workflow

1. **Input**: Target antigen, tumor type, NK source (PB, UCB, iPSC, cell line).

2. **CAR Design**: Generate optimized CAR-NK construct sequence.

3. **KIR Analysis**: Determine KIR genotype and HLA matching for donors.

4. **Activation Protocol**: Optimize cytokine cocktail for desired phenotype.

5. **Expansion**: Design feeder-based or feeder-free expansion protocol.

6. **Quality Prediction**: Predict NK product functionality.

7. **Output**: CAR sequence, donor recommendations, expansion protocol, QC metrics.

## Example Usage

**User**: "Design a CAR-NK targeting CD19 for B-cell malignancies with enhanced persistence."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/NK_Cell_Therapy_Agent/nk_designer.py \
    --target CD19 \
    --tumor_type b_cell_lymphoma \
    --nk_source ucb \
    --persistence_strategy il15_secretion \
    --costimulatory 2B4_DAP10 \
    --donors donor_hla_kir.json \
    --output carnk_design/
```

## NK Receptor-Ligand Interactions

**Activating Receptors**:

| Receptor | Ligands | Tumor Expression |
|----------|---------|------------------|
| NKG2D | MICA/B, ULBPs | Stress-induced |
| DNAM-1 | CD155, CD112 | Broadly expressed |
| NKp30 | B7-H6, BAG6 | Tumor-specific |
| NKp46 | Unknown tumor | Variable |
| CD16 | IgG Fc | ADCC trigger |

**Inhibitory Receptors**:

| Receptor | Ligands | Function |
|----------|---------|----------|
| KIR2DL1 | HLA-C2 | Self tolerance |
| KIR2DL2/3 | HLA-C1 | Self tolerance |
| KIR3DL1 | HLA-Bw4 | Self tolerance |
| NKG2A | HLA-E | Checkpoint |

## Memory-Like NK (CIML) Protocol

**Cytokine Preactivation**:
- IL-12 (10 ng/mL) + IL-15 (50 ng/mL) + IL-18 (50 ng/mL)
- 16-18 hour stimulation
- Enhanced IFN-γ, cytotoxicity upon restimulation
- Improved in vivo persistence

**Clinical Evidence**: Effective in relapsed/refractory AML

## KIR/HLA Matching Optimization

**Missing-Self Recognition**:
- Donor KIR + / Patient HLA -
- Enhanced NK cytotoxicity
- Important for allo-HSCT

**Prediction Model**:
- Input: Donor KIR genotype, patient HLA
- Output: Predicted NK alloreactivity score
- Validated in transplant outcomes

## AI/ML Components

**CAR-NK Optimization**:
- Adapted CARMSeD for NK biology
- NK-specific signaling domain preferences
- Tonic signaling prediction

**Expansion Prediction**:
- Fold-expansion from culture conditions
- Phenotype shift modeling
- Exhaustion marker prediction

## Prerequisites

* Python 3.10+
* HLA/KIR databases
* NK receptor databases
* Flow cytometry analysis tools

## Related Skills

* CART_Design_Optimizer_Agent - For CAR engineering principles
* Epitope_Prediction_Agent - For target selection
* Flow_Cytometry_AI - For NK phenotyping

## Clinical Development

**Current CAR-NK Programs**:
- CD19 CAR-NK (MD Anderson - AML, lymphoma)
- NKG2D CAR-NK (various solid tumors)
- CD70 CAR-NK (renal cell carcinoma)
- HER2 CAR-NK (breast cancer)

## Author

AI Group - Biomedical AI Platform
