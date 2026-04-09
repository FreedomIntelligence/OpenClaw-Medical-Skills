# bio-molecular-descriptors

> Calculates molecular descriptors and fingerprints using RDKit. Computes Morgan fingerprints (ECFP), MACCS keys, Lipinski properties, QED drug-likeness, TPSA, and 3D conformer descriptors. Use when featurizing molecules for machine learning or filtering by drug-likeness criteria.

## Version Compatibility

Reference examples tested with: RDKit 2024.03+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Molecular Descriptors

**"Calculate molecular fingerprints for my compound library"** → Compute structural fingerprints (Morgan/ECFP, MACCS keys) and physicochemical descriptors (Lipinski, QED, TPSA) for molecules, producing feature vectors for similarity analysis or ML models.
- Python: `AllChem.GetMorganFingerprintAsBitVect()`, `Descriptors.MolWt()`, `QED.qed()` (RDKit)

Calculate fingerprints and physicochemical properties for molecules.

## Morgan Fingerprints (ECFP)

**Goal:** Generate circular fingerprints that encode local chemical environments for similarity searching and ML models.

**Approach:** Use GetMorganFingerprintAsBitVect with a chosen radius (2 for ECFP4, 3 for ECFP6) and bit length, optionally including chirality information.

```python
from rdkit import Chem
from rdkit.Chem import AllChem

mol = Chem.MolFromSmiles('CCO')

# ECFP4 = radius 2 (diameter = 2 * radius + 2 = 6)
# ECFP6 = radius 3 (diameter = 8)
ecfp4 = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
ecfp6 = AllChem.GetMorganFingerprintAsBitVect(mol, radius=3, nBits=2048)

# With stereochemistry information
ecfp4_chiral = AllChem.GetMorganFingerprintAsBitVect(
    mol, radius=2, nBits=2048, useChirality=True
)

# As count vector (for some ML methods)
ecfp4_counts = AllChem.GetMorganFingerprint(mol, radius=2)

# Convert to numpy array
import numpy as np
fp_array = np.array(ecfp4)
```

## MACCS Keys

```python
from rdkit.Chem import MACCSkeys

maccs = MACCSkeys.GenMACCSKeys(mol)  # 167 bits

# As numpy array
maccs_array = np.array(maccs)
```

## Lipinski Properties

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

mol = Chem.MolFromSmiles('CCO')

# Lipinski Rule of 5 properties
mw = Descriptors.MolWt(mol)           # Molecular weight (<=500)
logp = Descriptors.MolLogP(mol)       # LogP (<=5)
hbd = Lipinski.NumHDonors(mol)        # H-bond donors (<=5)
hba = Lipinski.NumHAcceptors(mol)     # H-bond acceptors (<=10)

# Check Lipinski compliance
def passes_lipinski(mol):
    '''Check Lipinski Rule of 5 compliance.'''
    return (
        Descriptors.MolWt(mol) <= 500 and
        Descriptors.MolLogP(mol) <= 5 and
        Lipinski.NumHDonors(mol) <= 5 and
        Lipinski.NumHAcceptors(mol) <= 10
    )

# Additional properties
tpsa = Descriptors.TPSA(mol)          # Topological polar surface area
rotatable = Lipinski.NumRotatableBonds(mol)
```

## QED Drug-Likeness

```python
from rdkit.Chem.QED import qed

# QED score (0-1 scale, >0.5 generally drug-like)
qed_score = qed(mol)

# Weighted QED (default)
# Considers MW, LogP, TPSA, HBD, HBA, PSA, RotBonds, Aromatic rings
```

## Complete Descriptor Set

**Goal:** Calculate all available RDKit molecular descriptors for feature-rich ML input.

**Approach:** Build a MolecularDescriptorCalculator from the full descriptor list and apply it to each molecule, producing a descriptor DataFrame.

```python
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors

# Get all available descriptor names
descriptor_names = [d[0] for d in Descriptors.descList]

# Create descriptor calculator
calculator = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)

# Calculate for a molecule
descriptors = calculator.CalcDescriptors(mol)

# As DataFrame
import pandas as pd
desc_df = pd.DataFrame([descriptors], columns=descriptor_names)
```

## 3D Conformer Descriptors

**Goal:** Compute 3D shape descriptors (asphericity, eccentricity, radius of gyration) from molecular conformers.

**Approach:** Generate a 3D conformer with ETKDGv3, optimize geometry with MMFF, then calculate 3D descriptors from the conformer coordinates.

```python
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors3D

mol = Chem.MolFromSmiles('CCO')
mol = Chem.AddHs(mol)

# Generate 3D conformer (ETKDGv3 is now default)
AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())

# Optimize geometry
AllChem.MMFFOptimizeMolecule(mol)

# 3D descriptors (require conformer)
# Asphericity: 0 = sphere, 1 = rod
asphericity = Descriptors3D.Asphericity(mol)

# Eccentricity
eccentricity = Descriptors3D.Eccentricity(mol)

# Inertial shape factor
isf = Descriptors3D.InertialShapeFactor(mol)

# Radius of gyration
rog = Descriptors3D.RadiusOfGyration(mol)
```

## Batch Descriptor Calculation

**Goal:** Calculate a standard set of descriptors across an entire compound library.

**Approach:** Iterate over molecules, compute selected descriptors for each, and collect results into a DataFrame.

```python
def calculate_descriptors_batch(molecules, descriptor_names=None):
    '''Calculate descriptors for multiple molecules.'''
    if descriptor_names is None:
        descriptor_names = ['MolWt', 'MolLogP', 'TPSA', 'NumHDonors',
                           'NumHAcceptors', 'NumRotatableBonds', 'qed']

    results = []
    for mol in molecules:
        if mol is None:
            results.append({d: None for d in descriptor_names})
            continue

        row = {}
        for name in descriptor_names:
            if name == 'qed':
                from rdkit.Chem.QED import qed
                row[name] = qed(mol)
            else:
                row[name] = getattr(Descriptors, name)(mol)
        results.append(row)

    return pd.DataFrame(results)
```

## Related Skills

- molecular-io - Load molecules for descriptor calculation
- similarity-searching - Use fingerprints for similarity
- admet-prediction - Predict ADMET from descriptors
- machine-learning/biomarker-discovery - ML on molecular features
