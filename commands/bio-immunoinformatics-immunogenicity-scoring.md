# bio-immunoinformatics-immunogenicity-scoring

> Score and prioritize neoantigens and epitopes for immunogenicity using multi-factor models combining MHC binding, processing, expression, and sequence features. Rank candidates for vaccine design. Use when prioritizing epitopes for vaccine development or identifying the most immunogenic neoantigens.

## Version Compatibility

Reference examples tested with: MHCflurry 2.1+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Immunogenicity Scoring

**"Rank my neoantigen candidates by immunogenicity"** → Score and prioritize epitopes using multi-factor models combining MHC binding, proteasomal processing, expression level, and sequence foreignness for vaccine candidate selection.
- Python: `mhcflurry` for binding + processing predictions, custom scoring pipeline

## Multi-Factor Scoring

**Goal:** Calculate a composite immunogenicity score from multiple weighted factors (binding, agretopicity, processing, expression, clonality, foreignness).

**Approach:** Score each factor on a 0-1 scale, then combine via weighted sum with domain-informed weights.

```python
import pandas as pd
import numpy as np

def calculate_immunogenicity_score(peptide_data):
    '''Calculate composite immunogenicity score

    Factors considered:
    1. MHC binding affinity (IC50)
    2. Agretopicity (MT vs WT binding ratio)
    3. Proteasomal processing
    4. TAP transport
    5. Expression level
    6. Clonality (VAF for neoantigens)
    7. Self-similarity (avoid tolerance)

    Each factor scored 0-1, then weighted and combined.
    '''
    scores = {}

    # 1. Binding affinity (lower IC50 = better)
    # Transform to 0-1: 1 at 0nM, 0 at 5000nM
    ic50 = peptide_data.get('ic50_nM', 500)
    scores['binding'] = 1 - min(ic50 / 5000, 1)

    # 2. Agretopicity (MT binds better than WT)
    # Ratio of WT/MT IC50, capped at 10
    agretopicity = peptide_data.get('agretopicity', 1.0)
    scores['agretopicity'] = min(agretopicity / 10, 1)

    # 3. Processing score (from MHCflurry)
    processing = peptide_data.get('processing_score', 0.5)
    scores['processing'] = processing

    # 4. Expression (log scale, capped)
    expression = peptide_data.get('expression_tpm', 10)
    scores['expression'] = min(np.log10(expression + 1) / 3, 1)

    # 5. Clonality (for neoantigens)
    vaf = peptide_data.get('vaf', 0.5)
    scores['clonality'] = vaf

    # 6. Self-similarity (lower = better, less tolerance)
    self_sim = peptide_data.get('self_similarity', 0.5)
    scores['foreignness'] = 1 - self_sim

    # Weighted combination
    weights = {
        'binding': 0.25,
        'agretopicity': 0.20,
        'processing': 0.10,
        'expression': 0.15,
        'clonality': 0.15,
        'foreignness': 0.15
    }

    total = sum(scores[k] * weights[k] for k in weights)

    return total, scores
```

## Processing Prediction

**Goal:** Predict proteasomal cleavage and TAP transport probability for candidate peptides.

**Approach:** Use MHCflurry's Class1ProcessingPredictor to score peptide processing likelihood.

```python
from mhcflurry import Class1ProcessingPredictor

def predict_processing_score(peptides):
    '''Predict proteasomal cleavage and TAP transport

    Processing score reflects probability that peptide will be:
    1. Cleaved from protein by proteasome
    2. Transported by TAP into ER
    3. Loaded onto MHC

    Higher processing score = more likely to be presented
    '''
    predictor = Class1ProcessingPredictor.load()

    results = []
    for peptide in peptides:
        # Need surrounding sequence context for processing
        # In practice, extract from protein context
        pred = predictor.predict(peptides=[peptide])
        results.append({
            'peptide': peptide,
            'processing_score': pred['processing_score'].values[0]
        })

    return pd.DataFrame(results)
```

## Self-Similarity Assessment

**Goal:** Determine whether a candidate peptide resembles self-peptides, indicating potential T-cell tolerance.

**Approach:** Compute pairwise sequence identity against a proteome peptide set and flag high-similarity matches.

```python
def calculate_self_similarity(peptide, proteome_peptides, threshold=0.8):
    '''Check if peptide is similar to self-peptides

    High similarity to self-peptides suggests:
    - T-cells may be tolerized (deleted during development)
    - Lower likelihood of immune response

    Threshold 0.8 = 80% identity considered "self-like"
    '''
    def sequence_identity(seq1, seq2):
        if len(seq1) != len(seq2):
            return 0
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / len(seq1)

    max_similarity = 0
    most_similar = None

    for self_peptide in proteome_peptides:
        sim = sequence_identity(peptide, self_peptide)
        if sim > max_similarity:
            max_similarity = sim
            most_similar = self_peptide

    return {
        'similarity': max_similarity,
        'is_self_like': max_similarity >= threshold,
        'closest_self': most_similar
    }
```

## Hydrophobicity at Position 2

**Goal:** Assess MHC anchor residue quality by checking hydrophobicity at key positions.

**Approach:** Check whether position 2 and C-terminal residues fall within the hydrophobic amino acid set preferred by HLA-A*02:01-like alleles.

```python
def check_anchor_hydrophobicity(peptide):
    '''Check hydrophobicity at MHC anchor positions

    For HLA-A*02:01 and similar alleles:
    - Position 2: Prefers hydrophobic (L, I, V, M)
    - Position 9 (C-terminus): Prefers hydrophobic (L, V, I)

    Strong anchors improve binding stability.
    '''
    hydrophobic = set('LIVMFYW')

    pos2 = peptide[1] if len(peptide) > 1 else ''
    pos_last = peptide[-1]

    return {
        'pos2_hydrophobic': pos2 in hydrophobic,
        'pos_last_hydrophobic': pos_last in hydrophobic,
        'anchor_score': (pos2 in hydrophobic) + (pos_last in hydrophobic)
    }
```

## Rank Epitopes

**Goal:** Rank epitopes by composite immunogenicity score and assign confidence tiers for prioritization.

**Approach:** Score all candidates, sort by immunogenicity, and assign high/medium/low tiers based on percentile ranking.

```python
def rank_epitopes(epitope_df, top_n=20):
    '''Rank epitopes by immunogenicity

    Returns top candidates with scores and confidence tiers.

    Confidence tiers:
    - High: Top 5%, all factors favorable
    - Medium: Top 20%, most factors favorable
    - Low: Remaining, some factors favorable
    '''
    epitope_df = epitope_df.copy()

    # Calculate scores
    scores = []
    factor_scores = []
    for _, row in epitope_df.iterrows():
        total, factors = calculate_immunogenicity_score(row.to_dict())
        scores.append(total)
        factor_scores.append(factors)

    epitope_df['immunogenicity_score'] = scores
    factor_df = pd.DataFrame(factor_scores)

    # Combine
    result = pd.concat([epitope_df, factor_df], axis=1)

    # Rank
    result = result.sort_values('immunogenicity_score', ascending=False)

    # Assign tiers
    n = len(result)
    result['tier'] = 'low'
    result.iloc[:int(n * 0.20), result.columns.get_loc('tier')] = 'medium'
    result.iloc[:int(n * 0.05), result.columns.get_loc('tier')] = 'high'

    return result.head(top_n)
```

## Compare Candidates

**Goal:** Select a diverse set of vaccine candidates with broad HLA coverage and non-overlapping positions.

**Approach:** Iterate through ranked candidates, selecting those with non-overlapping genomic positions to maximize epitope diversity.

```python
def compare_vaccine_candidates(candidates_df):
    '''Compare and select vaccine candidates

    Vaccine design typically selects:
    - Multiple epitopes (5-20)
    - Diverse HLA coverage
    - High immunogenicity scores
    - Non-overlapping sequences
    '''
    # Group by HLA coverage
    hla_coverage = candidates_df.groupby('allele').size()

    # Select diverse set
    selected = []
    used_positions = set()

    for _, candidate in candidates_df.iterrows():
        # Check for overlap with selected
        pos = candidate.get('position', 0)
        if not any(abs(pos - p) < 5 for p in used_positions):
            selected.append(candidate)
            used_positions.add(pos)

        if len(selected) >= 20:
            break

    return pd.DataFrame(selected)
```

## Related Skills

- immunoinformatics/mhc-binding-prediction - Binding affinity component
- immunoinformatics/neoantigen-prediction - Input candidates
- immunoinformatics/epitope-prediction - Epitope identification
