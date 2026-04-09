# cart-design-optimizer-agent

> AI-guided CAR-T cell design for solid tumors using antigen prioritization, safety-by-design architectures, and exhaustion-resistant engineering.

**Available tools:** Read, Bash

# CAR-T Design Optimizer Agent

The **CAR-T Design Optimizer Agent** provides end-to-end AI-guided design of chimeric antigen receptor T-cells. It integrates antigen prioritization, safety-constrained CAR architectures, exhaustion resistance engineering, and computational modeling of CAR-T kinetics for optimized therapeutic design.

## When to Use This Skill

* When designing CAR-T therapies for solid tumors with limited target antigens.
* To optimize CAR construct sequences for reduced exhaustion and self-activation.
* For selecting safety-by-design architectures (logic-gated, modular, armored).
* When predicting CAR-T expansion, persistence, and efficacy.
* To engineer exhaustion-resistant CAR-T cells via gene editing strategies.

## Core Capabilities

1. **Antigen Prioritization**: AI-driven ranking of target antigens based on tumor specificity, expression levels, and safety profiles.

2. **CARMSeD Prediction**: Predictive model forecasting CAR constructs prone to tonic signaling, self-activation, and dysfunction.

3. **Safety Architecture Design**: Logic-gated (synNotch), ON/OFF switches, armored designs for solid tumor safety.

4. **Exhaustion Resistance**: CRISPR target selection (TOX, NR4A, PD-1 knockouts) and PD-1 locus integration strategies.

5. **Pharmacokinetic Modeling**: Multi-population models predicting CAR-T expansion, distribution, and persistence.

6. **LLM-Assisted Design**: Constrained large language model reasoning for evidence synthesis and design justification.

## CAR Architecture Options

| Architecture | Mechanism | Best For |
|--------------|-----------|----------|
| Standard 2nd Gen | CD28 or 4-1BB costimulation | Hematological malignancies |
| Logic-Gated (AND) | Requires 2 antigens for activation | Solid tumors, safety |
| synNotch Priming | TME signal triggers CAR expression | Local activation |
| Armored CAR | Cytokine secretion (IL-15, IL-21) | Hostile TME |
| Universal/SUPRA | Adaptable targeting via adaptor | Multi-antigen, flexibility |
| PD-1 Knock-in | CAR in PD-1 locus | Exhaustion resistance |

## Workflow

1. **Antigen Selection**: Analyze tumor expression data to prioritize targets.

2. **Safety Assessment**: Evaluate off-tumor expression in normal tissues.

3. **CAR Design**: Generate construct sequences with selected domains.

4. **CARMSeD Screening**: Predict self-activation and exhaustion propensity.

5. **Architecture Selection**: Match patient/tumor to optimal CAR design.

6. **Gene Editing Design**: Select CRISPR targets for enhanced function.

7. **Output**: Optimized CAR sequence, predicted performance, manufacturing specs.

## Example Usage

**User**: "Design an optimized CAR-T construct targeting HER2 for breast cancer with minimized exhaustion."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/CART_Design_Optimizer_Agent/cart_designer.py \
    --target HER2 \
    --tumor_type breast_cancer \
    --expression_data tumor_rnaseq.tsv \
    --normal_tissues gtex_expression.tsv \
    --architecture synnotch_armored \
    --exhaustion_engineering tox_knockout \
    --model carmsed_v2 \
    --output cart_design_report/
```

## CARMSeD Model Details

**Prediction Targets**:
- Tonic signaling propensity
- Self-activation risk
- Exhaustion trajectory
- Proliferative capacity

**Input Features**:
- scFv binding affinity
- Hinge/spacer length
- Costimulatory domain
- Transmembrane sequence
- Expression system

**Validated Performance**:
- AUC > 0.85 for dysfunction prediction
- In vitro to in vivo correlation

## Anti-Exhaustion Engineering Strategies

| Target | Method | Effect |
|--------|--------|--------|
| TOX | CRISPR KO | Prevents exhaustion program |
| NR4A1-3 | Triple KO | Blocks exhaustion TFs |
| PD-1 locus | CAR integration | TME-responsive expression |
| c-Jun | Overexpression | Overcomes AP-1 imbalance |
| DNMT3A | KO | Epigenetic reprogramming |

## Computational Pharmacokinetics

**Lotka-Volterra Model**:
```
dC/dt = r*C*(1 - C/K) - k*C*T  # CAR-T expansion
dT/dt = -α*C*T                   # Tumor killing
```

**Multi-Population Extensions**:
- Memory vs. effector subsets
- Exhaustion state transitions
- Cytokine-mediated effects
- Checkpoint interactions

## Prerequisites

* Python 3.10+
* PyTorch for ML models
* CRISPRscan for guide design
* Protein structure tools (optional)

## Related Skills

* TCell_Exhaustion_Analysis_Agent - For exhaustion profiling
* Neoantigen_Vaccine_Agent - For antigen identification
* CRISPR_Design_Agent - For gene editing optimization

## Clinical Considerations

1. **Cytokine Release Syndrome**: Risk assessment and mitigation designs
2. **ICANS Neurotoxicity**: CNS penetration modeling
3. **Manufacturing**: Transduction efficiency predictions
4. **Persistence**: Memory phenotype engineering

## Author

AI Group - Biomedical AI Platform
