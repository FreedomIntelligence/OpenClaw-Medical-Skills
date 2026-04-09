# bio-systems-biology-gene-essentiality

> Perform in silico gene knockout analysis and synthetic lethality screens using COBRApy single and double deletions. Predict essential genes and identify synthetic lethal pairs for drug target discovery. Use when identifying essential genes or finding synthetic lethal drug targets.

**Available tools:** Read, Bash

# Gene Essentiality Analysis

## Single Gene Knockouts

```python
import cobra
from cobra.flux_analysis import single_gene_deletion

model = cobra.io.load_model('textbook')

# Perform all single gene deletions
# Returns growth rate with each gene knocked out
deletion_results = single_gene_deletion(model)

# deletion_results is a DataFrame with:
# - ids: gene IDs (frozenset)
# - growth: growth rate after deletion
# - status: solver status

# Find essential genes (no growth when deleted)
# Essential: growth < 0.01 (allowing for numerical tolerance)
essential = deletion_results[deletion_results['growth'] < 0.01]
print(f'Essential genes: {len(essential)}')
```

## Classify Gene Essentiality

```python
def classify_gene_essentiality(model, growth_threshold=0.1):
    '''Classify genes by their impact on growth

    Categories:
    - Essential: Growth < 1% of WT (lethal)
    - Growth-reducing: 1-50% of WT
    - Non-essential: >50% of WT
    '''
    from cobra.flux_analysis import single_gene_deletion

    # Get wild-type growth
    wt_growth = model.optimize().objective_value

    # Run deletions
    results = single_gene_deletion(model)
    results['relative_growth'] = results['growth'] / wt_growth

    # Classify
    results['classification'] = 'non-essential'
    results.loc[results['relative_growth'] < 0.5, 'classification'] = 'growth-reducing'
    results.loc[results['relative_growth'] < 0.01, 'classification'] = 'essential'

    classification_counts = results['classification'].value_counts()
    return results, classification_counts
```

## Synthetic Lethality

```python
from cobra.flux_analysis import double_gene_deletion

# Warning: O(n^2) complexity - can be slow for large models
# For full E. coli (~1500 genes), this is ~1M combinations

# Subset to genes of interest
genes_of_interest = [g.id for g in model.genes[:50]]

# Run double deletions
double_results = double_gene_deletion(
    model,
    gene_list1=genes_of_interest,
    gene_list2=genes_of_interest
)

# Find synthetic lethal pairs
# Synthetic lethal: double KO is lethal when singles are viable

# Get single deletion results first
single_results = single_gene_deletion(model, gene_list=genes_of_interest)
single_dict = {list(ids)[0]: growth for ids, growth in
               zip(single_results['ids'], single_results['growth'])}
```

## Identify Synthetic Lethal Pairs

```python
def find_synthetic_lethal_pairs(model, genes=None, growth_threshold=0.01):
    '''Find synthetic lethal gene pairs

    Synthetic lethality criteria:
    - Single KO of gene A: viable (growth > threshold)
    - Single KO of gene B: viable (growth > threshold)
    - Double KO of A+B: lethal (growth < threshold)

    Useful for:
    - Drug combination targets
    - Genetic interaction networks
    - Backup pathway identification
    '''
    from cobra.flux_analysis import single_gene_deletion, double_gene_deletion

    if genes is None:
        genes = [g.id for g in model.genes]

    # Single deletions
    single = single_gene_deletion(model, gene_list=genes)
    viable_singles = single[single['growth'] > growth_threshold]
    viable_genes = [list(ids)[0] for ids in viable_singles['ids']]

    # Double deletions (only for viable single KOs)
    double = double_gene_deletion(model, gene_list1=viable_genes,
                                  gene_list2=viable_genes)

    # Find synthetic lethal pairs
    sl_pairs = []
    for _, row in double.iterrows():
        genes_in_pair = list(row['ids'])
        if len(genes_in_pair) == 2 and row['growth'] < growth_threshold:
            sl_pairs.append({
                'gene1': genes_in_pair[0],
                'gene2': genes_in_pair[1],
                'double_ko_growth': row['growth']
            })

    return sl_pairs
```

## Condition-Specific Essentiality

```python
def compare_essentiality_conditions(model, conditions):
    '''Compare gene essentiality across conditions

    Args:
        conditions: dict mapping condition name to media setup function

    Example:
        conditions = {
            'aerobic': lambda m: m.reactions.EX_o2_e.lower_bound = -20,
            'anaerobic': lambda m: m.reactions.EX_o2_e.lower_bound = 0
        }
    '''
    from cobra.flux_analysis import single_gene_deletion

    essentiality_by_condition = {}

    for condition_name, setup_func in conditions.items():
        with model:
            setup_func(model)
            results = single_gene_deletion(model)
            essential = set(list(ids)[0] for ids in
                          results[results['growth'] < 0.01]['ids'])
            essentiality_by_condition[condition_name] = essential

    # Find condition-specific essential genes
    all_essential = set.union(*essentiality_by_condition.values())
    core_essential = set.intersection(*essentiality_by_condition.values())
    condition_specific = {cond: ess - core_essential
                         for cond, ess in essentiality_by_condition.items()}

    return {
        'core_essential': core_essential,
        'condition_specific': condition_specific,
        'total_essential': len(all_essential)
    }
```

## Robustness Analysis

```python
def gene_robustness_analysis(model, gene_id, flux_levels=10):
    '''Analyze growth as function of gene expression level

    Instead of complete knockout, simulate reduced expression
    by constraining reactions associated with the gene.
    '''
    from cobra.flux_analysis import flux_variability_analysis

    gene = model.genes.get_by_id(gene_id)

    # Get reactions associated with this gene
    rxns = list(gene.reactions)

    results = []
    for level in [i/flux_levels for i in range(flux_levels + 1)]:
        with model:
            for rxn in rxns:
                # Get FVA bounds at wild-type
                fva = flux_variability_analysis(model, reaction_list=[rxn])
                max_flux = fva.loc[rxn.id, 'maximum']
                min_flux = fva.loc[rxn.id, 'minimum']

                # Constrain to fraction of wild-type
                rxn.upper_bound = max_flux * level
                rxn.lower_bound = min_flux * level

            sol = model.optimize()
            results.append({
                'expression_level': level,
                'growth': sol.objective_value
            })

    return results
```

## Related Skills

- systems-biology/flux-balance-analysis - Base FBA methods
- pathway-analysis/go-enrichment - Enrich essential gene sets
- clinical-databases/variant-prioritization - Link to disease genes
