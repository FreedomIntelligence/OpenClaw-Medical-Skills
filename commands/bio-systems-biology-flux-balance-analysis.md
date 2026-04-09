# bio-systems-biology-flux-balance-analysis

> Perform flux balance analysis (FBA) and flux variability analysis (FVA) on genome-scale metabolic models using COBRApy. Predict growth rates, metabolic fluxes, and optimal resource utilization. Use when predicting metabolic phenotypes or optimizing flux distributions.

**Available tools:** Read, Bash

# Flux Balance Analysis

## Load Models

```python
import cobra

# Load built-in test models
model = cobra.io.load_model('textbook')  # E. coli core (95 reactions)
model = cobra.io.load_model('iJO1366')   # Full E. coli (2583 reactions)

# Load from file
model = cobra.io.read_sbml_model('model.xml')
model = cobra.io.load_json_model('model.json')

# BiGG models available at: http://bigg.ucsd.edu/models
```

## Basic FBA

```python
import cobra

model = cobra.io.load_model('textbook')

# Run FBA (maximizes objective function, usually biomass)
solution = model.optimize()

# Growth rate interpretation:
# >0.8 h^-1: Fast growth (rich media)
# 0.3-0.8 h^-1: Moderate growth
# <0.3 h^-1: Slow growth or stress
# 0: No growth (lethal condition or missing nutrients)
print(f'Growth rate: {solution.objective_value:.4f} h^-1')
print(f'Status: {solution.status}')

# Access flux values
for rxn in model.reactions[:5]:
    print(f'{rxn.id}: {solution.fluxes[rxn.id]:.4f}')
```

## Set Media Conditions

```python
def set_minimal_media(model, carbon_source='EX_glc__D_e', carbon_uptake=10):
    '''Configure minimal media conditions

    Args:
        carbon_source: Exchange reaction ID for carbon source
        carbon_uptake: Maximum uptake rate (mmol/gDW/h)
                      Typical glucose uptake: 10-20 mmol/gDW/h
    '''
    # Close all exchange reactions
    for rxn in model.exchanges:
        rxn.lower_bound = 0  # No uptake

    # Open essential exchanges
    essential = ['EX_o2_e', 'EX_h2o_e', 'EX_h_e', 'EX_nh4_e',
                 'EX_pi_e', 'EX_so4_e', 'EX_k_e', 'EX_mg2_e']

    for ex_id in essential:
        if ex_id in model.reactions:
            model.reactions.get_by_id(ex_id).lower_bound = -1000

    # Set carbon source
    if carbon_source in model.reactions:
        model.reactions.get_by_id(carbon_source).lower_bound = -carbon_uptake

    return model


# Example: Compare growth on different carbon sources
carbon_sources = ['EX_glc__D_e', 'EX_ac_e', 'EX_succ_e']
for cs in carbon_sources:
    with model:
        set_minimal_media(model, carbon_source=cs)
        sol = model.optimize()
        print(f'{cs}: Growth = {sol.objective_value:.4f}')
```

## Flux Variability Analysis (FVA)

```python
from cobra.flux_analysis import flux_variability_analysis

# FVA finds the range of flux values for each reaction
# while maintaining optimal (or near-optimal) growth

# Standard FVA (at 100% optimum)
fva = flux_variability_analysis(model)

# FVA at 90% of optimal growth
# fraction_of_optimum=0.9: allows 10% suboptimal solutions
# This reveals alternative optimal flux distributions
fva = flux_variability_analysis(model, fraction_of_optimum=0.9)

# FVA for specific reactions
rxns_of_interest = ['PFK', 'PGI', 'GAPD']
fva = flux_variability_analysis(model, reaction_list=rxns_of_interest)

# Identify essential vs flexible reactions
fva['essential'] = (fva['minimum'] > 0) | (fva['maximum'] < 0)
fva['flexible'] = fva['maximum'] - fva['minimum'] > 0.01

print(fva[['minimum', 'maximum', 'essential', 'flexible']])
```

## Production Envelope

```python
from cobra.flux_analysis import production_envelope

# Analyze tradeoff between growth and product secretion
# Useful for metabolic engineering to find optimal conditions

prod_env = production_envelope(
    model,
    reactions=['EX_ac_e'],  # Product (acetate)
    objective='Biomass_Ecoli_core',
    points=20
)

# prod_env is a DataFrame with:
# - EX_ac_e: acetate production rate
# - Biomass_Ecoli_core: growth rate at that production level
print(prod_env)
```

## Phenotype Phase Plane

```python
from cobra.flux_analysis import phenotype_phase_plane

# Analyze growth across two varying conditions
# Typically oxygen and carbon uptake

ppp = phenotype_phase_plane(
    model,
    variables=['EX_glc__D_e', 'EX_o2_e'],  # X and Y axes
    points=10
)

# Returns growth rate as function of both uptake rates
# Useful for identifying metabolic modes (aerobic vs anaerobic)
```

## Parsimonious FBA (pFBA)

```python
from cobra.flux_analysis import pfba

# pFBA minimizes total flux while achieving optimal growth
# Produces more biologically realistic flux distributions

pfba_solution = pfba(model)

# Compare total flux
fba_total = sum(abs(model.optimize().fluxes))
pfba_total = sum(abs(pfba_solution.fluxes))
print(f'FBA total flux: {fba_total:.1f}')
print(f'pFBA total flux: {pfba_total:.1f}')
```

## Loopless FBA

```python
from cobra.flux_analysis import loopless_solution

# Remove thermodynamically infeasible loops
# Important for realistic flux predictions

solution = loopless_solution(model)
```

## Related Skills

- systems-biology/gene-essentiality - In silico gene knockouts
- systems-biology/context-specific-models - Tissue-specific FBA
- metabolomics/pathway-mapping - Integrate metabolomics data
