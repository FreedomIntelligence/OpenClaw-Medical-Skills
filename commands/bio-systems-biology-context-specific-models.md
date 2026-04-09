# bio-systems-biology-context-specific-models

> Build tissue and condition-specific metabolic models using GIMME, iMAT, and INIT algorithms with expression data constraints. Create models that reflect cell-type specific metabolism. Use when building tissue-specific metabolic models or integrating transcriptomics with FBA.

**Available tools:** Read, Bash

# Context-Specific Models

## GIMME Algorithm

```python
import cobra
import numpy as np

def gimme(model, expression_data, threshold=0.25, required_growth=0.1):
    '''Gene Inactivity Moderated by Metabolism and Expression (GIMME)

    Creates context-specific model by:
    1. Penalizing flux through lowly-expressed reactions
    2. Requiring minimum biomass production

    Args:
        expression_data: dict mapping gene_id -> expression value
        threshold: Expression percentile below which genes are inactive
                  0.25 = bottom 25% considered inactive
        required_growth: Minimum growth rate to maintain

    Returns:
        Context-specific model with inactive reactions constrained
    '''
    # Calculate expression threshold
    values = list(expression_data.values())
    cutoff = np.percentile(values, threshold * 100)

    # Identify lowly-expressed genes
    low_expressed = {g for g, v in expression_data.items() if v < cutoff}

    # Create context model
    context_model = model.copy()

    # Set minimum growth constraint
    context_model.reactions.get_by_id('Biomass_Ecoli_core').lower_bound = required_growth

    # Minimize flux through reactions with low-expressed genes
    for rxn in context_model.reactions:
        genes = {g.id for g in rxn.genes}
        if genes and genes.issubset(low_expressed):
            # This reaction is likely inactive - constrain it
            rxn.upper_bound = min(rxn.upper_bound, 1.0)
            rxn.lower_bound = max(rxn.lower_bound, -1.0)

    return context_model
```

## iMAT Algorithm

```python
def imat(model, expression_data, high_threshold=0.75, low_threshold=0.25):
    '''Integrative Metabolic Analysis Tool (iMAT)

    Maximizes agreement between flux activity and expression:
    - Highly expressed reactions should carry flux
    - Lowly expressed reactions should have zero flux

    More sophisticated than GIMME - uses MILP optimization.
    '''
    from cobra import Reaction

    # Classify reactions by expression
    high_expr_rxns = []
    low_expr_rxns = []

    for rxn in model.reactions:
        if rxn.genes:
            # Aggregate gene expression (use max for OR, min for AND)
            gene_expr = [expression_data.get(g.id, 0.5) for g in rxn.genes]
            rxn_expr = max(gene_expr)  # Simplified OR logic

            if rxn_expr > np.percentile(list(expression_data.values()), high_threshold * 100):
                high_expr_rxns.append(rxn.id)
            elif rxn_expr < np.percentile(list(expression_data.values()), low_threshold * 100):
                low_expr_rxns.append(rxn.id)

    # Create MILP to maximize consistent reactions
    # This is a simplified version - full iMAT uses binary variables
    context_model = model.copy()

    # Force flux through highly expressed reactions
    for rxn_id in high_expr_rxns:
        rxn = context_model.reactions.get_by_id(rxn_id)
        rxn.lower_bound = max(rxn.lower_bound, 0.01)

    # Constrain lowly expressed reactions
    for rxn_id in low_expr_rxns:
        rxn = context_model.reactions.get_by_id(rxn_id)
        rxn.upper_bound = min(rxn.upper_bound, 0.1)
        rxn.lower_bound = max(rxn.lower_bound, -0.1)

    return context_model, high_expr_rxns, low_expr_rxns
```

## Expression Data Integration

```python
def load_expression_data(filepath, gene_col='gene_id', expr_col='TPM'):
    '''Load and normalize expression data

    Accepts:
    - RNA-seq counts (TPM, FPKM)
    - Microarray intensities
    - Proteomics abundances

    Returns dict mapping gene_id -> normalized expression
    '''
    import pandas as pd

    df = pd.read_csv(filepath)

    # Log-transform if needed (high dynamic range)
    expr = df[expr_col].values
    if expr.max() / expr.mean() > 100:
        expr = np.log2(expr + 1)

    # Normalize to 0-1 range
    expr_norm = (expr - expr.min()) / (expr.max() - expr.min())

    return dict(zip(df[gene_col], expr_norm))


def aggregate_gene_expression(model, expression_data, method='max'):
    '''Map gene expression to reactions

    Methods:
    - 'max': Use maximum gene expression (OR logic)
    - 'min': Use minimum gene expression (AND logic)
    - 'mean': Average across genes

    For GPR: (A and B) or C
    - min(A, B) for the complex
    - max(complex, C) for the alternatives
    '''
    rxn_expression = {}

    for rxn in model.reactions:
        if not rxn.genes:
            rxn_expression[rxn.id] = 0.5  # Default for non-enzymatic
            continue

        gene_expr = [expression_data.get(g.id, 0.5) for g in rxn.genes]

        if method == 'max':
            rxn_expression[rxn.id] = max(gene_expr)
        elif method == 'min':
            rxn_expression[rxn.id] = min(gene_expr)
        else:
            rxn_expression[rxn.id] = np.mean(gene_expr)

    return rxn_expression
```

## Tissue-Specific Human Models

```python
def create_tissue_model(generic_model, gtex_expression, tissue='liver'):
    '''Create tissue-specific model from GTEx expression data

    GTEx provides median TPM for 54 human tissues.
    Download from: https://gtexportal.org/home/datasets
    '''
    import pandas as pd

    # Load GTEx median expression
    gtex = pd.read_csv(gtex_expression, sep='\t')

    # Extract tissue column
    tissue_col = [c for c in gtex.columns if tissue.lower() in c.lower()][0]
    expression = dict(zip(gtex['gene_id'], gtex[tissue_col]))

    # Apply GIMME
    tissue_model = gimme(generic_model, expression, threshold=0.25)

    return tissue_model
```

## Validate Context Model

```python
def validate_context_model(original, context, expression_data):
    '''Compare original and context-specific models

    Checks:
    1. Growth capability maintained
    2. Inactive reactions reduced
    3. Active reactions maintained
    '''
    # Growth comparison
    orig_growth = original.optimize().objective_value
    context_growth = context.optimize().objective_value

    # Count constrained reactions
    constrained = 0
    for rxn in context.reactions:
        orig_rxn = original.reactions.get_by_id(rxn.id)
        if rxn.upper_bound < orig_rxn.upper_bound:
            constrained += 1

    return {
        'original_growth': orig_growth,
        'context_growth': context_growth,
        'growth_ratio': context_growth / orig_growth,
        'constrained_reactions': constrained,
        'total_reactions': len(context.reactions)
    }
```

## Related Skills

- systems-biology/flux-balance-analysis - Run FBA on context models
- differential-expression/de-results - Generate expression data
- single-cell/clustering - Cell-type specific expression
