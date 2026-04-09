# bio-systems-biology-model-curation

> Validate, gap-fill, and curate genome-scale metabolic models using memote for quality scores and COBRApy for manual curation. Ensure models meet SBML standards and produce biologically meaningful predictions. Use when improving draft models or preparing models for publication.

**Available tools:** Read, Bash

# Model Curation

## Memote Quality Assessment

```bash
# Install memote
pip install memote

# Run full quality report
memote report snapshot model.xml --filename report.html

# Quick score
memote run model.xml

# Continuous integration testing
memote run --pytest-args "--tb=short" model.xml
```

## Memote Python API

```python
import memote
import cobra

model = cobra.io.read_sbml_model('model.xml')

# Run all tests
result = memote.suite.api.run(model)

# Get score breakdown
scores = memote.suite.api.snapshot(model)
print(f"Total score: {scores['score']['total_score']:.2%}")

# Detailed test results
for test_name, test_result in scores['tests'].items():
    if not test_result['passed']:
        print(f"Failed: {test_name}")
```

## Gap-Filling

```python
import cobra
from cobra.flux_analysis import gapfill

model = cobra.io.read_sbml_model('model.xml')

# Load universal reaction database
universal = cobra.io.read_sbml_model('universal_model.xml')

# Find reactions to add for growth
# demand: reaction to optimize (usually biomass exchange)
# iterations: number of alternative solutions
solution = gapfill(model, universal,
                   demand=model.reactions.BIOMASS,
                   iterations=5)

# solution contains list of reaction sets to add
for i, rxn_set in enumerate(solution):
    print(f'Solution {i+1}: {[r.id for r in rxn_set]}')

# Add first solution
for rxn in solution[0]:
    model.add_reactions([rxn])
```

## Identify Dead-End Metabolites

```python
def find_dead_end_metabolites(model):
    '''Find metabolites that cannot be produced or consumed

    Dead-end metabolites indicate:
    - Missing reactions in the network
    - Incorrect reaction stoichiometry
    - Incomplete pathways
    '''
    dead_ends = []

    for met in model.metabolites:
        producing = [r for r in met.reactions if r.get_coefficient(met) > 0]
        consuming = [r for r in met.reactions if r.get_coefficient(met) < 0]

        if not producing or not consuming:
            dead_ends.append({
                'metabolite': met.id,
                'name': met.name,
                'producers': len(producing),
                'consumers': len(consuming)
            })

    return dead_ends


dead_ends = find_dead_end_metabolites(model)
print(f'Found {len(dead_ends)} dead-end metabolites')
```

## Check Mass and Charge Balance

```python
def check_reaction_balance(reaction):
    '''Check if reaction is mass and charge balanced

    Unbalanced reactions indicate:
    - Missing metabolites
    - Wrong stoichiometry
    - Proton accounting issues
    '''
    mass_balance = {}
    charge_balance = 0

    for met, coef in reaction.metabolites.items():
        # Check mass
        if met.formula:
            for element, count in met.elements.items():
                mass_balance[element] = mass_balance.get(element, 0) + coef * count

        # Check charge
        if met.charge is not None:
            charge_balance += coef * met.charge

    is_balanced = all(abs(v) < 1e-6 for v in mass_balance.values())
    is_charge_balanced = abs(charge_balance) < 1e-6

    return {
        'mass_balanced': is_balanced,
        'charge_balanced': is_charge_balanced,
        'mass_imbalance': {k: v for k, v in mass_balance.items() if abs(v) > 1e-6}
    }


# Check all reactions
unbalanced = []
for rxn in model.reactions:
    result = check_reaction_balance(rxn)
    if not result['mass_balanced']:
        unbalanced.append((rxn.id, result['mass_imbalance']))
```

## Fix Gene-Protein-Reaction Rules

```python
def standardize_gpr(model):
    '''Standardize gene-protein-reaction rules

    GPR format: (gene1 and gene2) or gene3
    - 'and' = protein complex (all genes required)
    - 'or' = isozymes (any gene sufficient)
    '''
    for rxn in model.reactions:
        if rxn.gene_reaction_rule:
            # Standardize formatting
            rule = rxn.gene_reaction_rule
            rule = rule.replace(' AND ', ' and ')
            rule = rule.replace(' OR ', ' or ')
            rxn.gene_reaction_rule = rule


def identify_orphan_reactions(model):
    '''Find reactions without gene associations

    Orphan reactions may be:
    - Spontaneous reactions
    - Unannotated genes
    - Transport reactions (often orphan)
    '''
    orphans = [r for r in model.reactions if not r.genes]

    # Classify orphans
    exchange = [r for r in orphans if r in model.exchanges]
    transport = [r for r in orphans if 'transport' in r.name.lower() or 't_' in r.id.lower()]
    other = [r for r in orphans if r not in exchange and r not in transport]

    return {
        'exchange': len(exchange),
        'transport': len(transport),
        'other': len(other),
        'total': len(orphans)
    }
```

## Annotation Standards

```python
def add_standard_annotations(model):
    '''Add standard database annotations

    Required annotations for SBML compliance:
    - KEGG IDs for reactions and metabolites
    - ChEBI IDs for metabolites
    - BiGG IDs if applicable
    '''
    for met in model.metabolites:
        if not hasattr(met, 'annotation'):
            met.annotation = {}

        # Add SBO term for metabolite
        met.annotation['sbo'] = 'SBO:0000247'  # Simple chemical

    for rxn in model.reactions:
        if not hasattr(rxn, 'annotation'):
            rxn.annotation = {}

        # Add SBO term based on reaction type
        if rxn in model.exchanges:
            rxn.annotation['sbo'] = 'SBO:0000627'  # Exchange
        else:
            rxn.annotation['sbo'] = 'SBO:0000176'  # Biochemical reaction
```

## Related Skills

- systems-biology/metabolic-reconstruction - Generate draft models
- systems-biology/flux-balance-analysis - Test curated models
- pathway-analysis/kegg-pathways - Add KEGG annotations
