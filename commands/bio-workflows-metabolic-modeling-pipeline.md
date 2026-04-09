# bio-workflows-metabolic-modeling-pipeline

> End-to-end genome-scale metabolic modeling from genome sequence to flux predictions. Covers automated reconstruction with CarveMe, model validation with memote, FBA/FVA analysis, and gene essentiality prediction. Use when building metabolic models or predicting metabolic phenotypes from genomic data.

**Available tools:** Read, Bash

# Metabolic Modeling Pipeline

Complete workflow for genome-scale metabolic modeling: from protein sequences to flux predictions and phenotype analysis.

## Workflow Overview

```
Protein FASTA (genome annotation)
        |
        v
[1. Reconstruction] --> CarveMe / gapseq / ModelSEED
        |
        v
[2. Model Curation] --> memote QC, gap-filling
        |
        | <---- Iterative refinement loop
        v
[3. FBA Analysis] --> Growth prediction, flux distribution
        |
        +-----------------------+
        |                       |
        v                       v
[4a. Gene Essentiality]   [4b. Context-Specific]
    Single/double KO       Tissue-specific models
        |                       |
        v                       v
Essential Gene List      Condition-Specific Fluxes
```

## Prerequisites

```bash
pip install cobra carveme memote escher pandas numpy matplotlib seaborn

conda install -c bioconda diamond
```

**Required data:**
- Protein FASTA file from genome annotation
- BiGG universal model (downloaded by CarveMe)

## Primary Path: Bacterial Model from Genome

### Step 1: Automated Reconstruction with CarveMe

```bash
# Basic reconstruction from protein sequences
carve genome.faa -o model_draft.xml

# With gram type specification (improves biomass composition)
carve genome.faa -o model_draft.xml --gram-neg

# Gap-fill for specific media
carve genome.faa -o model_draft.xml --gram-neg --gapfill M9
```

```python
import cobra

model = cobra.io.read_sbml_model('model_draft.xml')
print(f'Model: {model.id}')
print(f'Reactions: {len(model.reactions)}')
print(f'Metabolites: {len(model.metabolites)}')
print(f'Genes: {len(model.genes)}')

# Quick growth test
# Growth rate >0.01 h^-1 indicates viable model
solution = model.optimize()
print(f'Growth rate: {solution.objective_value:.4f} h^-1')
```

### Step 2: Model Validation with Memote

```bash
# Run memote QC
memote run --filename model_draft_report.html model_draft.xml

# Generate snapshot for comparison
memote report snapshot --filename model_snapshot.json model_draft.xml
```

```python
import json

with open('model_snapshot.json') as f:
    report = json.load(f)

# Key metrics to check
metrics = report['tests']['basic']
print('=== Model QC Metrics ===')
print(f"Reactions with genes: {metrics.get('test_gene_reaction_rule_presence', {}).get('metric', 'N/A')}")
print(f"Metabolites in reactions: {metrics.get('test_metabolites_not_produced', {}).get('metric', 'N/A')}")
print(f"Stoichiometry balance: {metrics.get('test_stoichiometric_consistency', {}).get('result', 'N/A')}")

# Target: memote score >50% for usable model
# Score >70% indicates well-curated model
total_score = report.get('score', {}).get('total_score', 0)
print(f'Total memote score: {total_score:.1%}')
```

### Step 3: Model Curation (Iterative)

```python
import cobra
from cobra.flux_analysis import gapfill

model = cobra.io.read_sbml_model('model_draft.xml')

# Check for common issues
def diagnose_model(model):
    issues = []

    # Dead-end metabolites (produced but not consumed, or vice versa)
    for met in model.metabolites:
        producing = [r for r in met.reactions if met in r.products]
        consuming = [r for r in met.reactions if met in r.reactants]
        if len(producing) > 0 and len(consuming) == 0:
            issues.append(f'Dead-end (not consumed): {met.id}')
        elif len(producing) == 0 and len(consuming) > 0:
            issues.append(f'Dead-end (not produced): {met.id}')

    # Blocked reactions
    fva = cobra.flux_analysis.flux_variability_analysis(model)
    blocked = fva[(fva['minimum'] == 0) & (fva['maximum'] == 0)]
    if len(blocked) > 0:
        issues.append(f'Blocked reactions: {len(blocked)}')

    return issues

issues = diagnose_model(model)
print(f'Found {len(issues)} issues')
for issue in issues[:10]:
    print(f'  {issue}')
```

```python
# Gap-filling for growth on specific media
from cobra.medium import minimal_medium

# Load universal reaction database for gap-filling
universal = cobra.io.read_sbml_model('universal_model.xml')

# Define target medium (e.g., glucose minimal)
target_medium = {
    'EX_glc__D_e': 10,  # Glucose uptake
    'EX_o2_e': 20,       # Oxygen
    'EX_nh4_e': 100,     # Ammonium
    'EX_pi_e': 100,      # Phosphate
    'EX_so4_e': 100,     # Sulfate
}

# Apply medium
for rxn_id in model.exchanges:
    rxn = model.reactions.get_by_id(rxn_id)
    if rxn_id in target_medium:
        rxn.lower_bound = -target_medium[rxn_id]
    else:
        rxn.lower_bound = 0  # Block other uptakes

# Gap-fill to enable growth
# Gap-filling adds minimal reactions from universal model to enable growth
gapfill_solution = gapfill(model, universal, demand_reactions=False)
print(f'Gap-fill added {len(gapfill_solution[0])} reactions')

for rxn in gapfill_solution[0]:
    model.add_reactions([rxn])
    print(f'  Added: {rxn.id} - {rxn.name}')

# Verify growth
solution = model.optimize()
print(f'Growth after gap-fill: {solution.objective_value:.4f} h^-1')
```

### Step 4: Flux Balance Analysis

```python
import cobra
import pandas as pd
import matplotlib.pyplot as plt

model = cobra.io.read_sbml_model('model_curated.xml')

# Basic FBA
solution = model.optimize()
print(f'Objective (growth): {solution.objective_value:.4f} h^-1')
print(f'Status: {solution.status}')

# Get active fluxes
fluxes = solution.fluxes
active_fluxes = fluxes[abs(fluxes) > 1e-6]
print(f'Active reactions: {len(active_fluxes)} / {len(model.reactions)}')

# Key exchange fluxes (uptake/secretion)
exchange_fluxes = fluxes[[r.id for r in model.exchanges]]
significant_exchanges = exchange_fluxes[abs(exchange_fluxes) > 0.1]
print('\nSignificant exchanges:')
print(significant_exchanges.sort_values())
```

```python
# Flux Variability Analysis (FVA)
from cobra.flux_analysis import flux_variability_analysis

# FVA identifies reaction flexibility
# Fraction 0.9 = allow 90% of optimal growth
fva = flux_variability_analysis(model, fraction_of_optimum=0.9)

# Identify rigid vs flexible reactions
fva['range'] = fva['maximum'] - fva['minimum']
rigid = fva[fva['range'] < 1e-6]
flexible = fva[fva['range'] > 1]

print(f'Rigid reactions (fixed flux): {len(rigid)}')
print(f'Flexible reactions: {len(flexible)}')

# Plot flux ranges for key pathways
glycolysis = ['PGI', 'PFK', 'FBA', 'TPI', 'GAPD', 'PGK', 'PGM', 'ENO', 'PYK']
glyc_fva = fva.loc[fva.index.isin(glycolysis)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(glyc_fva)), glyc_fva['maximum'] - glyc_fva['minimum'],
        left=glyc_fva['minimum'], alpha=0.7)
ax.set_yticks(range(len(glyc_fva)))
ax.set_yticklabels(glyc_fva.index)
ax.set_xlabel('Flux range (mmol/gDW/h)')
ax.set_title('Glycolysis Flux Variability')
plt.tight_layout()
plt.savefig('glycolysis_fva.pdf')
```

### Step 5a: Gene Essentiality Prediction

```python
from cobra.flux_analysis import single_gene_deletion, double_gene_deletion

# Single gene knockouts
single_ko = single_gene_deletion(model)
single_ko['growth_ratio'] = single_ko['growth'] / solution.objective_value

# Essential genes: knockout abolishes growth (<10% of WT)
# Threshold 0.1 is standard for essentiality
essential = single_ko[single_ko['growth_ratio'] < 0.1]
print(f'Essential genes: {len(essential)} / {len(model.genes)}')

# Export essential genes
essential_list = [list(g)[0].id for g in essential.index]
with open('essential_genes.txt', 'w') as f:
    f.write('\n'.join(essential_list))

# Compare to experimental data (if available)
# Typically expect >70% overlap with experimental essentiality screens
```

```python
# Double gene knockouts (synthetic lethality)
# WARNING: Computationally intensive for large models

# Focus on non-essential genes only
non_essential = [g.id for g in model.genes if g.id not in essential_list]

# Run pairwise deletions
double_ko = double_gene_deletion(model, gene_list=non_essential[:100])  # Subset for speed

# Find synthetic lethal pairs
# Synthetic lethality: neither single KO is lethal, but double KO is
synthetic_lethal = double_ko[double_ko['growth'] < 0.01]
print(f'Synthetic lethal pairs: {len(synthetic_lethal)}')
```

### Step 5b: Context-Specific Models

```python
# Build tissue-specific model using expression data
def build_context_model(model, expression_data, threshold_percentile=25):
    '''Build context-specific model by removing lowly-expressed reactions.

    threshold_percentile: reactions below this expression percentile are candidates for removal
    '''
    import numpy as np

    context_model = model.copy()
    threshold = np.percentile(list(expression_data.values()), threshold_percentile)

    reactions_to_remove = []
    for rxn in context_model.reactions:
        if rxn.gene_reaction_rule:
            genes_in_rxn = [g.id for g in rxn.genes]
            # Get expression for genes in reaction
            expr_values = [expression_data.get(g, 0) for g in genes_in_rxn]

            # If all genes below threshold, candidate for removal
            if all(e < threshold for e in expr_values):
                # Check if removal breaks growth
                with context_model:
                    rxn.knock_out()
                    sol = context_model.optimize()
                    if sol.objective_value > 0.01:
                        reactions_to_remove.append(rxn.id)

    for rxn_id in reactions_to_remove:
        context_model.reactions.get_by_id(rxn_id).remove_from_model()

    return context_model

# Example: liver-specific model
liver_expression = {'gene1': 100, 'gene2': 5, 'gene3': 50}  # TPM values
liver_model = build_context_model(model, liver_expression)
print(f'Liver model: {len(liver_model.reactions)} reactions')
```

## Visualization with Escher

```python
import escher

# Load model and solution
model = cobra.io.read_sbml_model('model_curated.xml')
solution = model.optimize()

# Create Escher map
builder = escher.Builder(
    map_name='e_coli_core.Core metabolism',
    model=model,
    reaction_data=solution.fluxes.to_dict()
)

builder.save_html('flux_map.html')
```

## Parameter Recommendations

| Step | Parameter | Value | Rationale |
|------|-----------|-------|-----------|
| CarveMe | --gapfill | M9 or LB | Match experimental media |
| Memote | score threshold | >50% | Minimum for usable model |
| FBA | solver | gurobi/cplex | Faster than glpk for large models |
| FVA | fraction_of_optimum | 0.9 | 90% allows realistic flexibility |
| Essentiality | growth threshold | 0.1 | Standard 10% of WT growth |
| Context | expression percentile | 25 | Balance specificity vs viability |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No growth | Missing essential reactions | Gap-fill with universal model |
| Unrealistic growth rate | Unbounded uptake | Constrain medium properly |
| Many blocked reactions | Dead-end metabolites | Check metabolite connectivity |
| Low memote score | Missing GPR, mass balance | Run memote report for details |
| Essentiality mismatch | Missing isozymes | Add alternative pathways |

## Output Files

| File | Description |
|------|-------------|
| `model_draft.xml` | Initial reconstruction (SBML) |
| `model_curated.xml` | Gap-filled and validated model |
| `model_report.html` | Memote QC report |
| `essential_genes.txt` | Predicted essential genes |
| `fba_fluxes.tsv` | Optimal flux distribution |
| `fva_results.tsv` | Flux variability ranges |
| `flux_map.html` | Escher visualization |

## Related Skills

- systems-biology/metabolic-reconstruction - CarveMe, gapseq details
- systems-biology/model-curation - Memote, gap-filling
- systems-biology/flux-balance-analysis - FBA, FVA, pFBA
- systems-biology/gene-essentiality - Single/double knockouts
- systems-biology/context-specific-models - Tissue-specific models
