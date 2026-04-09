# bio-immunoinformatics-epitope-prediction

> Predict B-cell and T-cell epitopes using BepiPred, IEDB tools, and structure-based methods for vaccine and antibody design. Identify immunogenic regions in antigens. Use when designing vaccines, mapping antibody binding sites, or predicting immunogenic peptides.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Epitope Prediction

**"Predict B-cell and T-cell epitopes in my protein"** → Identify immunogenic regions in antigens for vaccine design using sequence-based and structure-based prediction tools.
- Python: IEDB API for B-cell epitope prediction (BepiPred)
- Python: `mhcflurry` for T-cell epitope MHC binding prediction

## B-Cell Epitope Prediction

**Goal:** Predict linear B-cell epitopes from protein sequence using IEDB prediction tools.

**Approach:** Submit sequence to IEDB B-cell prediction API with selectable method (BepiPred-2.0 recommended) and parse tab-separated results.

### BepiPred-2.0 (Sequence-Based)

```python
import requests

def predict_bcell_epitopes_iedb(sequence, method='bepipred2'):
    '''Predict B-cell epitopes using IEDB API

    Methods:
    - bepipred2: Deep learning (recommended)
    - bepipred: Original BepiPred
    - emini: Surface accessibility
    - kolaskar-tongaonkar: Antigenicity
    - parker: Hydrophilicity

    BepiPred-2.0 uses deep learning on crystal structures
    Threshold: >0.5 predicted as epitope (default)
    '''
    url = 'http://tools-cluster-interface.iedb.org/tools_api/bcell/'

    params = {
        'method': method,
        'sequence_text': sequence
    }

    response = requests.post(url, data=params)

    # Parse response (tab-separated)
    lines = response.text.strip().split('\n')
    header = lines[0].split('\t')
    data = [line.split('\t') for line in lines[1:]]

    return header, data
```

### Parse BepiPred Results

```python
import pandas as pd

def parse_bepipred_results(header, data, threshold=0.5):
    '''Parse BepiPred output and identify epitope regions

    Output columns:
    - Position: Amino acid position
    - Residue: Amino acid
    - Score: BepiPred score (higher = more likely epitope)

    Epitope threshold:
    - >0.5: Default, balanced sensitivity/specificity
    - >0.6: More stringent, fewer false positives
    - >0.4: More sensitive, more candidates
    '''
    df = pd.DataFrame(data, columns=header)
    df['Score'] = df['Score'].astype(float)
    df['Position'] = df['Position'].astype(int)

    # Identify epitope regions
    df['is_epitope'] = df['Score'] > threshold

    # Find continuous epitope regions
    epitopes = []
    current_epitope = []

    for _, row in df.iterrows():
        if row['is_epitope']:
            current_epitope.append(row)
        else:
            if len(current_epitope) >= 5:  # Minimum epitope length
                epitopes.append({
                    'start': current_epitope[0]['Position'],
                    'end': current_epitope[-1]['Position'],
                    'sequence': ''.join(r['Residue'] for r in current_epitope),
                    'avg_score': sum(r['Score'] for r in current_epitope) / len(current_epitope)
                })
            current_epitope = []

    return df, epitopes
```

## T-Cell Epitope Prediction

**Goal:** Predict T-cell epitopes by MHC-I binding across multiple HLA alleles.

**Approach:** Query IEDB MHC-I API for each allele-sequence combination and aggregate predictions.

```python
def predict_tcell_epitopes_iedb(sequence, alleles, method='recommended'):
    '''Predict T-cell epitopes using IEDB

    MHC-I methods:
    - recommended: Consensus of methods
    - netmhcpan_ba: NetMHCpan binding affinity
    - netmhcpan_el: NetMHCpan eluted ligand

    MHC-II methods:
    - recommended
    - netmhciipan
    '''
    url = 'http://tools-cluster-interface.iedb.org/tools_api/mhci/'

    results = []
    for allele in alleles:
        params = {
            'method': method,
            'sequence_text': sequence,
            'allele': allele,
            'length': '9'  # Most common for MHC-I
        }

        response = requests.post(url, data=params)
        # Parse results...

    return results
```

## Linear vs Conformational Epitopes

**Goal:** Classify epitopes as linear (continuous) or conformational (discontinuous) and predict structure-based epitopes.

**Approach:** Distinguish by residue continuity in primary sequence; for conformational epitopes, use structure-based tools (DiscoTope, ElliPro) via web servers.

```python
def classify_epitope_type(epitope_info):
    '''Classify epitope as linear or conformational

    Linear (continuous) epitopes:
    - Consecutive amino acids in primary sequence
    - ~10% of B-cell epitopes
    - Easier to predict from sequence

    Conformational (discontinuous) epitopes:
    - Non-consecutive residues brought together by folding
    - ~90% of B-cell epitopes
    - Requires structure for prediction
    '''
    pass


def predict_conformational_epitopes(pdb_file, chain='A'):
    '''Predict conformational B-cell epitopes from structure

    Uses surface accessibility and protrusion index.
    Requires 3D structure (PDB/mmCIF).

    Tools:
    - DiscoTope 2.0 (structure-based)
    - ElliPro (protrusion)
    - SEPPA 3.0
    '''
    # Structure-based prediction requires specialized tools
    # Usually accessed via web servers

    print('For conformational epitopes:')
    print('- DiscoTope: http://tools.iedb.org/discotope/')
    print('- ElliPro: http://tools.iedb.org/ellipro/')
    pass
```

## Combine Multiple Predictions

**Goal:** Improve epitope prediction reliability by combining multiple methods into a consensus score.

**Approach:** Run each method independently, threshold per method, then count agreements per position and assign confidence levels.

```python
def consensus_epitope_prediction(sequence, methods=['bepipred2', 'emini', 'parker']):
    '''Combine multiple prediction methods

    Consensus approach improves reliability:
    - Regions predicted by multiple methods more reliable
    - Different methods capture different properties

    Scoring:
    - 3/3 methods: High confidence
    - 2/3 methods: Moderate confidence
    - 1/3 methods: Low confidence
    '''
    all_results = {}

    for method in methods:
        header, data = predict_bcell_epitopes_iedb(sequence, method)
        df = pd.DataFrame(data, columns=header)
        all_results[method] = df

    # Combine scores
    consensus = all_results[methods[0]][['Position', 'Residue']].copy()

    for method in methods:
        threshold = 0.5 if method == 'bepipred2' else 0  # Method-specific thresholds
        all_results[method]['is_epitope'] = all_results[method]['Score'].astype(float) > threshold
        consensus[method] = all_results[method]['is_epitope'].astype(int)

    consensus['consensus_score'] = consensus[methods].sum(axis=1)
    consensus['confidence'] = consensus['consensus_score'].map({
        3: 'high', 2: 'moderate', 1: 'low', 0: 'none'
    })

    return consensus
```

## Epitope Mapping from Experimental Data

**Goal:** Map epitope regions from overlapping peptide array binding data.

**Approach:** Process signal intensity values from overlapping peptide arrays and identify continuous high-signal regions as epitopes.

```python
def map_epitopes_from_peptide_array(array_results, overlap=11):
    '''Map epitopes from peptide array experiments

    Peptide arrays test binding of overlapping peptides
    covering the entire antigen sequence.

    Args:
        array_results: Dict mapping peptide -> signal intensity
        overlap: Overlap between consecutive peptides

    Returns:
        Epitope map with per-residue scores
    '''
    # Implementation would process experimental binding data
    pass
```

## Related Skills

- immunoinformatics/mhc-binding-prediction - T-cell epitope prediction
- immunoinformatics/immunogenicity-scoring - Epitope ranking
- structural-biology/geometric-analysis - Structure-based epitopes
