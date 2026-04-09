# bio-reaction-enumeration

> Enumerates chemical libraries through reaction SMARTS transformations using RDKit. Generates virtual compound libraries from building blocks using defined chemical reactions with product validation. Use when creating combinatorial libraries or enumerating products from synthetic routes.

## Version Compatibility

Reference examples tested with: RDKit 2024.03+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Reaction Enumeration

**"Generate a combinatorial library from my building blocks"** → Enumerate virtual compound libraries by applying reaction SMARTS transformations to sets of building-block molecules, producing and validating all product combinations for a defined synthetic route.
- Python: `AllChem.ReactionFromSmarts()`, `rxn.RunReactants()` (RDKit)

Generate virtual compound libraries using reaction SMARTS.

## Reaction SMARTS Basics

```python
from rdkit import Chem
from rdkit.Chem import AllChem

# Define reaction (reactants >> products with atom mapping)
# Amide coupling: carboxylic acid + amine -> amide
amide_rxn = AllChem.ReactionFromSmarts(
    '[C:1](=[O:2])O.[N:3]>>[C:1](=[O:2])[N:3]'
)

# Validate reaction definition
n_errors = amide_rxn.Validate()
if n_errors[0] == 0:
    print('Reaction is valid')

# Run reaction
acid = Chem.MolFromSmiles('CC(=O)O')
amine = Chem.MolFromSmiles('CCN')

products = amide_rxn.RunReactants((acid, amine))
# products is a tuple of tuples: ((product1,), (product2,), ...)
for prod_set in products:
    for prod in prod_set:
        Chem.SanitizeMol(prod)
        print(Chem.MolToSmiles(prod))
```

## Common Reaction SMARTS

```python
REACTIONS = {
    'amide_coupling': '[C:1](=[O:2])O.[N:3]>>[C:1](=[O:2])[N:3]',
    'reductive_amination': '[C:1]=O.[N:2]>>[C:1][N:2]',
    'suzuki': '[c:1][Br].[c:2][B](O)O>>[c:1][c:2]',
    'buchwald': '[c:1][Br].[N:2]>>[c:1][N:2]',
    'ester_formation': '[C:1](=[O:2])O.[O:3]>>[C:1](=[O:2])[O:3]',
    'michael_addition': '[C:1]=[C:2]C(=O).[C:3]>>[C:1][C:2]([C:3])C(=O)',
}
```

## Combinatorial Library Enumeration

**Goal:** Generate all possible products from a combinatorial reaction of building-block sets.

**Approach:** Enumerate all reactant combinations via Cartesian product, apply the reaction SMARTS to each, sanitize products, and deduplicate by canonical SMILES.

```python
from rdkit import Chem
from rdkit.Chem import AllChem
from itertools import product

def enumerate_library(rxn_smarts, reactant_lists, deduplicate=True):
    '''
    Enumerate products from combinatorial reaction.

    Args:
        rxn_smarts: Reaction SMARTS string
        reactant_lists: List of lists of SMILES for each reactant position
        deduplicate: Remove duplicate products

    Returns:
        List of unique product SMILES
    '''
    rxn = AllChem.ReactionFromSmarts(rxn_smarts)

    # Validate reaction
    if rxn.Validate()[0] != 0:
        raise ValueError('Invalid reaction SMARTS')

    products = []
    seen = set()

    # Generate all combinations
    for reactants in product(*reactant_lists):
        mols = [Chem.MolFromSmiles(s) for s in reactants]
        if None in mols:
            continue

        try:
            prods = rxn.RunReactants(tuple(mols))
            for prod_set in prods:
                for prod in prod_set:
                    try:
                        Chem.SanitizeMol(prod)
                        smiles = Chem.MolToSmiles(prod)

                        if deduplicate:
                            if smiles not in seen:
                                seen.add(smiles)
                                products.append(smiles)
                        else:
                            products.append(smiles)
                    except Exception:
                        continue  # Skip invalid products
        except Exception:
            continue

    return products

# Example: Amide library
acids = ['CC(=O)O', 'c1ccccc1C(=O)O', 'OC(=O)CC(=O)O']
amines = ['CCN', 'c1ccc(N)cc1', 'NCCN']

products = enumerate_library(
    '[C:1](=[O:2])O.[N:3]>>[C:1](=[O:2])[N:3]',
    [acids, amines]
)
print(f'Generated {len(products)} unique products')
```

## Multi-Step Synthesis

**Goal:** Enumerate products from a multi-step synthetic route with intermediate building blocks at each step.

**Approach:** Iteratively apply each reaction SMARTS to the current product pool and the next set of building blocks, carrying forward intermediates through the synthesis chain.

```python
def multi_step_enumeration(building_blocks, reaction_sequence):
    '''
    Enumerate products from multi-step synthesis.

    Args:
        building_blocks: Dict of {step: [smiles_list]}
        reaction_sequence: List of reaction SMARTS
    '''
    current = building_blocks[0]

    for step, rxn_smarts in enumerate(reaction_sequence):
        next_bbs = building_blocks.get(step + 1, [])
        if not next_bbs:
            break

        current = enumerate_library(rxn_smarts, [current, next_bbs])
        print(f'Step {step + 1}: {len(current)} intermediates')

    return current
```

## Product Validation

**Goal:** Filter enumerated products to remove invalid, oversized, or reactive compounds.

**Approach:** Parse each product SMILES, check molecular weight against a maximum, screen for reactive functional groups via SMARTS, and verify valence sanity.

```python
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

def validate_products(smiles_list, mw_max=500, remove_reactive=True):
    '''
    Validate and filter enumerated products.
    '''
    valid = []

    reactive_smarts = [
        '[N+]([O-])=O',  # Nitro
        '[Cl,Br,I]',     # Halogens (optional)
        'C#N',           # Nitrile
    ]
    reactive_patterns = [Chem.MolFromSmarts(s) for s in reactive_smarts]

    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            continue

        # Check MW
        if Descriptors.MolWt(mol) > mw_max:
            continue

        # Check reactive groups
        if remove_reactive:
            has_reactive = any(mol.HasSubstructMatch(p) for p in reactive_patterns)
            if has_reactive:
                continue

        # Check valence
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            continue

        valid.append(smiles)

    return valid
```

## Reaction Templates

```python
def apply_template(core_smiles, r_groups, attachment_smarts='[*:1]'):
    '''
    Apply R-group decoration to a core scaffold.

    Args:
        core_smiles: Core with attachment point (e.g., '*c1ccccc1')
        r_groups: List of R-group SMILES
        attachment_smarts: SMARTS for attachment point
    '''
    products = []

    for rg in r_groups:
        # Simple string replacement for single attachment
        product_smiles = core_smiles.replace('*', rg, 1)
        mol = Chem.MolFromSmiles(product_smiles)
        if mol:
            try:
                Chem.SanitizeMol(mol)
                products.append(Chem.MolToSmiles(mol))
            except Exception:
                continue

    return products

# Example: Decorate benzene core
core = '*c1ccccc1'
r_groups = ['C', 'CC', 'C(=O)O', 'O']
decorated = apply_template(core, r_groups)
```

## Related Skills

- molecular-io - Save enumerated libraries
- molecular-descriptors - Filter by properties
- admet-prediction - Screen for drug-likeness
