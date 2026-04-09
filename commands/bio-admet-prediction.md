# bio-admet-prediction

> Predicts ADMET properties using ADMETlab 3.0 API or DeepChem models. Estimates bioavailability, CYP inhibition, hERG liability, and 119 toxicity endpoints with uncertainty quantification. Filters for PAINS and other structural alerts. Use when filtering compounds for drug-likeness or prioritizing leads by predicted safety.

## Version Compatibility

Reference examples tested with: RDKit 2024.03+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ADMET Prediction

**"Predict the drug-likeness and toxicity of my compounds"** → Estimate ADMET properties (bioavailability, CYP inhibition, hERG liability, toxicity) for candidate molecules using the ADMETlab 3.0 API or RDKit PAINS/structural alert filters, producing a safety/drugability profile for lead prioritization.
- Python: ADMETlab 3.0 REST API via `requests`, `FilterCatalog` for PAINS (RDKit)

Predict absorption, distribution, metabolism, excretion, and toxicity properties.

## ADMETlab 3.0 API

**Goal:** Predict ADMET properties for a batch of compounds using a web API.

**Approach:** Submit SMILES to the ADMETlab 3.0 REST endpoint and parse the returned JSON into a DataFrame of 119 endpoint predictions with uncertainty estimates.

ADMETlab 3.0 provides 119 endpoints with uncertainty estimates.

```python
import requests
import pandas as pd

def predict_admet_batch(smiles_list, api_url='https://admetlab3.scbdd.com/api/predict'):
    '''
    Predict ADMET properties using ADMETlab 3.0 API.

    Note: SwissADME has NO API - it is web-only.
    '''
    payload = {
        'smiles': smiles_list
    }

    response = requests.post(api_url, json=payload)
    response.raise_for_status()

    return pd.DataFrame(response.json())

# Example usage
# smiles = ['CCO', 'c1ccccc1O', 'CC(=O)Oc1ccccc1C(=O)O']
# results = predict_admet_batch(smiles)
```

## Key ADMET Endpoints

| Category | Endpoints | Thresholds |
|----------|-----------|------------|
| Absorption | Caco-2, HIA, Pgp substrate | HIA > 30% |
| Distribution | BBB penetration, PPB, VDss | BBB+: penetrates |
| Metabolism | CYP inhibition (1A2, 2C9, 2C19, 2D6, 3A4) | Inhibitor threshold |
| Excretion | Clearance, Half-life | - |
| Toxicity | hERG, AMES, hepatotoxicity, carcinogenicity | hERG IC50 > 10 μM |

## DeepChem Models

DeepChem supports both PyTorch and TensorFlow backends.

```python
import deepchem as dc

# Load pre-trained toxicity model
tox21_tasks, tox21_datasets, transformers = dc.molnet.load_tox21()
train_dataset, valid_dataset, test_dataset = tox21_datasets

# Featurize new molecules
featurizer = dc.feat.CircularFingerprint(size=1024)
smiles = ['CCO', 'c1ccccc1']
features = featurizer.featurize(smiles)

# Load trained model
model = dc.models.GraphConvModel(
    n_tasks=12,
    mode='classification',
    model_dir='tox21_model'
)

# Predict (after training/loading)
# predictions = model.predict_on_batch(features)
```

## PAINS Filter

**Goal:** Remove pan-assay interference compounds that produce false positives in biological screens.

**Approach:** Build a PAINS FilterCatalog and test each molecule; compounds matching any PAINS pattern are flagged and separated from clean compounds.

```python
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

def filter_pains(molecules):
    '''
    Filter out PAINS (pan-assay interference compounds).
    These are promiscuous compounds that give false positives in assays.
    '''
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog(params)

    clean = []
    flagged = []

    for mol in molecules:
        if mol is None:
            continue
        entry = catalog.GetFirstMatch(mol)
        if entry is None:
            clean.append(mol)
        else:
            flagged.append((mol, entry.GetDescription()))

    print(f'Clean: {len(clean)}, PAINS flagged: {len(flagged)}')
    return clean, flagged

# Other filter catalogs available:
# FilterCatalogs.BRENK - Brenk structural alerts
# FilterCatalogs.NIH - NIH structural alerts
# FilterCatalogs.ZINC - ZINC clean leads
```

## Lipinski and Beyond

**Goal:** Assess drug-likeness of a molecule using multiple criteria beyond Lipinski Rule of 5.

**Approach:** Calculate Lipinski properties (MW, LogP, HBD, HBA), count violations, check Veber oral bioavailability criteria (rotatable bonds, TPSA), and compute QED score.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, QED

def calculate_druglikeness(mol):
    '''
    Calculate multiple drug-likeness criteria.
    '''
    if mol is None:
        return None

    props = {
        # Lipinski Rule of 5
        'MW': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'HBD': Lipinski.NumHDonors(mol),
        'HBA': Lipinski.NumHAcceptors(mol),

        # Additional properties
        'TPSA': Descriptors.TPSA(mol),
        'RotatableBonds': Lipinski.NumRotatableBonds(mol),
        'AromaticRings': Lipinski.NumAromaticRings(mol),

        # QED (quantitative estimate of drug-likeness)
        # 0-1 scale, > 0.5 generally drug-like
        'QED': QED.qed(mol)
    }

    # Lipinski violations
    violations = 0
    if props['MW'] > 500: violations += 1
    if props['LogP'] > 5: violations += 1
    if props['HBD'] > 5: violations += 1
    if props['HBA'] > 10: violations += 1
    props['LipinskiViolations'] = violations

    # Veber criteria (oral bioavailability)
    # RotatableBonds <= 10, TPSA <= 140
    props['VeberCompliant'] = (props['RotatableBonds'] <= 10 and props['TPSA'] <= 140)

    return props
```

## Prioritization Pipeline

**Goal:** Rank compounds through a multi-stage ADMET filter to identify drug-like leads.

**Approach:** Apply sequential Lipinski, Veber, and QED filters to progressively eliminate compounds that fail drug-likeness criteria.

```python
def prioritize_compounds(molecules):
    '''
    Multi-stage ADMET filtering pipeline.
    '''
    results = []

    for mol in molecules:
        if mol is None:
            continue

        props = calculate_druglikeness(mol)
        if props is None:
            continue

        # Stage 1: Lipinski filter
        if props['LipinskiViolations'] > 1:
            continue

        # Stage 2: Additional filters
        if not props['VeberCompliant']:
            continue

        # Stage 3: QED cutoff
        if props['QED'] < 0.5:
            continue

        results.append((mol, props))

    return results
```

## Related Skills

- molecular-descriptors - Calculate descriptors for ML
- substructure-search - Filter reactive groups
- virtual-screening - Screen after ADMET filtering
