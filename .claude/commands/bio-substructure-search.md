# bio-substructure-search

> Searches molecular libraries for substructure matches using SMARTS patterns with RDKit. Filters compounds by pharmacophore features, functional groups, or scaffold matches with atom mapping. Use when finding compounds containing specific chemical moieties or filtering libraries by structural features.

## Version Compatibility

Reference examples tested with: RDKit 2024.03+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Substructure Search

**"Filter my library for compounds containing a specific functional group"** → Search molecular collections for substructure matches using SMARTS patterns, identifying compounds that contain specified chemical moieties, scaffolds, or pharmacophore features.
- Python: `mol.HasSubstructMatch()`, `Chem.MolFromSmarts()` (RDKit)

Find molecules containing specific structural patterns using SMARTS.

## Basic Substructure Search

```python
from rdkit import Chem

mol = Chem.MolFromSmiles('c1ccc(O)cc1CCO')

# Check if pattern exists
pattern = Chem.MolFromSmarts('[OH]')  # Hydroxyl group
has_hydroxyl = mol.HasSubstructMatch(pattern)
print(f'Contains hydroxyl: {has_hydroxyl}')

# Get all matches (atom indices)
matches = mol.GetSubstructMatches(pattern)
print(f'Hydroxyl positions: {matches}')
```

## Common SMARTS Patterns

| Pattern | SMARTS | Description |
|---------|--------|-------------|
| Hydroxyl | `[OH]` | Alcohol/phenol |
| Primary amine | `[NH2]` | Primary amine |
| Secondary amine | `[NH1]` | Secondary amine |
| Carboxylic acid | `[CX3](=O)[OX2H1]` | COOH |
| Amide | `[CX3](=O)[NX3]` | C(=O)N |
| Benzene | `c1ccccc1` | Phenyl ring |
| Any aromatic | `[a]` | Any aromatic atom |
| Halogen | `[F,Cl,Br,I]` | Any halogen |

## Library Filtering

**Goal:** Filter a molecular library to retain only compounds containing (or lacking) a specific structural pattern.

**Approach:** Parse a SMARTS pattern and test each molecule for a substructure match, returning those that pass the inclusion or exclusion criterion.

```python
from rdkit import Chem

def filter_by_substructure(molecules, smarts, exclude=False):
    '''
    Filter molecules by substructure presence/absence.

    Args:
        molecules: List of RDKit mol objects
        smarts: SMARTS pattern string
        exclude: If True, return molecules WITHOUT the pattern
    '''
    pattern = Chem.MolFromSmarts(smarts)
    if pattern is None:
        raise ValueError(f'Invalid SMARTS: {smarts}')

    filtered = []
    for mol in molecules:
        if mol is None:
            continue
        has_match = mol.HasSubstructMatch(pattern)
        if exclude:
            if not has_match:
                filtered.append(mol)
        else:
            if has_match:
                filtered.append(mol)

    return filtered

# Filter for amines
amines = filter_by_substructure(library, '[NX3;H2,H1,H0]')

# Exclude reactive groups
clean = filter_by_substructure(library, '[N+]([O-])=O', exclude=True)  # No nitro
```

## Multiple Pattern Filtering

**Goal:** Apply multiple inclusion and exclusion substructure filters to narrow a compound set.

**Approach:** Sequentially apply SMARTS-based inclusion filters (must match all) then exclusion filters (must match none) to progressively narrow the library.

```python
def filter_multiple_patterns(molecules, include_patterns=None, exclude_patterns=None):
    '''
    Filter by multiple inclusion and exclusion patterns.
    '''
    result = list(molecules)

    if include_patterns:
        for smarts in include_patterns:
            pattern = Chem.MolFromSmarts(smarts)
            result = [m for m in result if m and m.HasSubstructMatch(pattern)]

    if exclude_patterns:
        for smarts in exclude_patterns:
            pattern = Chem.MolFromSmarts(smarts)
            result = [m for m in result if m and not m.HasSubstructMatch(pattern)]

    return result

# Find compounds with both amine and carboxylic acid (amino acids)
amino_acids = filter_multiple_patterns(
    library,
    include_patterns=['[NX3;H2]', '[CX3](=O)[OX2H1]']
)
```

## Atom Mapping

```python
from rdkit import Chem

def get_substructure_atoms(mol, smarts):
    '''
    Get all atoms matching a pattern with their indices.
    '''
    pattern = Chem.MolFromSmarts(smarts)
    matches = mol.GetSubstructMatches(pattern)

    results = []
    for match in matches:
        atoms = [mol.GetAtomWithIdx(i) for i in match]
        results.append({
            'indices': match,
            'symbols': [a.GetSymbol() for a in atoms]
        })

    return results

# Find and characterize all aromatic rings
mol = Chem.MolFromSmiles('c1ccc2c(c1)cccc2')
rings = get_substructure_atoms(mol, 'c1ccccc1')
print(f'Found {len(rings)} aromatic 6-membered rings')
```

## Recursive SMARTS

```python
# Recursive SMARTS for complex patterns

# Phenyl attached to carbonyl
pattern = '[$(c1ccccc1C(=O))]'

# Ortho-substituted phenyl
ortho_pattern = '[$(c1ccc([*])cc1[*])]'

# Electron-withdrawing group on aromatic
ewg_aromatic = '[$(c[$(C(=O)),$(C#N),$(N(=O)=O)])]'

mol = Chem.MolFromSmiles('c1ccc(C(=O)O)cc1')
pattern = Chem.MolFromSmarts('[$(c1ccccc1C(=O))]')
print(mol.HasSubstructMatch(pattern))  # True
```

## Visualization with Highlighting

```python
from rdkit.Chem.Draw import rdMolDraw2D

def draw_with_highlights(mol, smarts, filename):
    '''Draw molecule with substructure highlighted.'''
    pattern = Chem.MolFromSmarts(smarts)
    match = mol.GetSubstructMatch(pattern)

    if not match:
        print('No match found')
        return

    drawer = rdMolDraw2D.MolDraw2DCairo(400, 300)
    drawer.DrawMolecule(mol, highlightAtoms=match)
    drawer.FinishDrawing()

    with open(filename, 'wb') as f:
        f.write(drawer.GetDrawingText())

# Highlight carboxylic acid
draw_with_highlights(mol, '[CX3](=O)[OX2H1]', 'highlighted.png')
```

## Related Skills

- molecular-io - Load molecules for searching
- similarity-searching - Fingerprint-based searching
- admet-prediction - Filter before ADMET analysis
