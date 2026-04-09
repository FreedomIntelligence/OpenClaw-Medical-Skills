# immune-checkpoint-combination-agent

> AI-powered analysis for predicting optimal immune checkpoint inhibitor combinations based on tumor microenvironment, biomarkers, and molecular profiling.

**Available tools:** Read, Bash

# Immune Checkpoint Combination Agent

The **Immune Checkpoint Combination Agent** analyzes tumor molecular profiles to predict optimal immune checkpoint inhibitor (ICI) combinations. It integrates TME characterization, checkpoint expression, resistance mechanisms, and clinical evidence for rational immunotherapy combination design.

## When to Use This Skill

* When selecting checkpoint inhibitor combinations for individual patients.
* To predict response to ICI combinations (PD-1/PD-L1 + CTLA-4, TIGIT, LAG-3).
* For identifying resistance mechanisms suggesting specific combinations.
* When analyzing tumor microenvironment to guide combination selection.
* To match patients to combination immunotherapy clinical trials.

## Core Capabilities

1. **Checkpoint Expression Profiling**: Quantify expression of PD-1, PD-L1, CTLA-4, TIGIT, LAG-3, TIM-3, and others.

2. **TME Characterization**: Classify tumors as "hot" (inflamed), "excluded", or "cold" (desert) for combination rationale.

3. **Resistance Mechanism Analysis**: Identify primary and acquired resistance patterns.

4. **Combination Prediction**: ML models predicting response to specific checkpoint combinations.

5. **Synergy Scoring**: Evaluate potential synergies based on mechanism of action overlap.

6. **Clinical Evidence Integration**: Match combinations to published efficacy data.

## Checkpoint Inhibitor Landscape

| Target | Approved Agents | Mechanism | Combination Rationale |
|--------|-----------------|-----------|----------------------|
| PD-1 | Pembrolizumab, Nivolumab | Block T-cell inhibition | Backbone therapy |
| PD-L1 | Atezolizumab, Durvalumab | Block tumor immune evasion | Alternative backbone |
| CTLA-4 | Ipilimumab, Tremelimumab | Enhance T-cell priming | Non-redundant to PD-1 |
| LAG-3 | Relatlimab | Block exhausted T-cells | PD-1 refractory |
| TIGIT | Tiragolumab | Block NK/T suppression | NK cell engagement |
| TIM-3 | Multiple in trials | Terminal exhaustion | Highly exhausted TME |

## Workflow

1. **Input**: Tumor RNA-seq, IHC markers, TMB/MSI status, clinical data.

2. **Checkpoint Profiling**: Quantify checkpoint ligand/receptor expression.

3. **TME Classification**: Determine immune infiltration pattern.

4. **Resistance Analysis**: Identify potential resistance mechanisms.

5. **Combination Scoring**: Rank combinations by predicted efficacy.

6. **Evidence Matching**: Link to clinical trial data.

7. **Output**: Ranked combinations, rationale, supporting evidence, trial matches.

## Example Usage

**User**: "Recommend optimal checkpoint inhibitor combination for this melanoma patient based on their tumor profile."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/Immune_Checkpoint_Combination_Agent/ici_combination.py \
    --rnaseq tumor_expression.tsv \
    --ihc pd-l1_tps_60.json \
    --mutations tumor_mutations.maf \
    --tmb 12.5 \
    --msi stable \
    --tumor_type melanoma \
    --prior_treatment pembrolizumab \
    --output ici_recommendations.json
```

## TME-Based Combination Rationale

**Inflamed ("Hot") Tumors**:
- High TIL infiltration
- PD-L1 high
- Respond to anti-PD-1 monotherapy
- Add CTLA-4 for improved depth

**Excluded Tumors**:
- TILs at margin, not infiltrating
- Physical/chemical barriers
- Consider anti-CTLA-4 for priming
- Add chemotherapy for barrier disruption

**Desert ("Cold") Tumors**:
- Low TIL infiltration
- Low PD-L1
- Need to induce inflammation first
- Consider chemo, radiation, or vaccines + ICI

## Resistance Mechanisms and Solutions

| Mechanism | Biomarkers | Combination Strategy |
|-----------|------------|---------------------|
| Alternative checkpoints | LAG-3+, TIGIT+, TIM-3+ | Add second checkpoint |
| WNT/β-catenin | CTNNB1 mutations | Poor ICI candidate |
| IFN signaling loss | JAK1/2, B2M mutations | Limited benefit |
| MHC loss | HLA-A/B/C loss | NK-engaging therapies |
| T-cell exclusion | TGF-β high | TGF-β inhibitor combination |

## AI/ML Models

**Response Prediction**:
- Multi-modal model (expression + mutations + clinical)
- Trained on TCGA + clinical trial data
- AUC 0.72-0.80 for response

**Synergy Prediction**:
- Network-based combination scoring
- Mechanistic pathway analysis
- Clinical validation integration

## Combination Evidence Database

| Combination | Indication | Key Trial | Benefit |
|-------------|------------|-----------|---------|
| Nivo + Ipi | Melanoma | CheckMate-067 | OS improvement |
| Nivo + Rela | Melanoma | RELATIVITY-047 | PFS improvement |
| Atezo + Tira | NSCLC | CITYSCAPE | PFS improvement (PD-L1 high) |
| Durva + Treme | HCC | HIMALAYA | OS improvement |

## Prerequisites

* Python 3.10+
* scikit-learn, XGBoost for ML
* Gene signature databases
* Clinical evidence database

## Related Skills

* TCell_Exhaustion_Analysis_Agent - For exhaustion profiling
* Tumor_Microenvironment - For TME characterization
* Neoantigen_Vaccine_Agent - For vaccine combinations

## Clinical Considerations

1. **Toxicity**: Combinations increase irAE risk
2. **Sequencing**: Optimal order of agents
3. **Biomarkers**: TMB, PD-L1, MSI as selection criteria
4. **Cost**: Combination therapy costs

## Author

AI Group - Biomedical AI Platform
