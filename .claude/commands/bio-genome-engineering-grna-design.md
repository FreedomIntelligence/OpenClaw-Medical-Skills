# bio-genome-engineering-grna-design

> Design guide RNAs for CRISPR-Cas9/Cas12a experiments using CRISPRscan and local scoring algorithms. Score guides for on-target activity using Rule Set 2 and Azimuth models. Use when designing sgRNAs for gene knockout, activation, or repression experiments.

## Version Compatibility

Reference examples tested with: BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Guide RNA Design

**"Design guide RNAs for my CRISPR knockout experiment"** → Scan a target gene sequence for PAM sites, extract candidate spacer sequences, and score them for on-target activity using Rule Set 2 or CRISPRscan algorithms.
- Python: custom PAM scanning with `Bio.Seq`, CRISPRscan scoring models

## Find PAM Sites

```python
from Bio.Seq import Seq
import re

def find_pam_sites(sequence, pam='NGG', guide_length=20):
    '''Find all PAM sites and extract guide sequences

    PAM patterns:
    - NGG: SpCas9 (most common)
    - TTTN: Cas12a/Cpf1 (5' PAM)
    - NNGRRT: SaCas9 (smaller, for AAV delivery)
    '''
    sequence = sequence.upper()
    guides = []

    # NGG PAM - guide is 20bp upstream of PAM
    if pam == 'NGG':
        for match in re.finditer(r'(?=(.GG))', sequence):
            pos = match.start()
            if pos >= guide_length:
                guide = sequence[pos - guide_length:pos]
                guides.append({
                    'sequence': guide,
                    'pam': sequence[pos:pos + 3],
                    'position': pos - guide_length,
                    'strand': '+'
                })

    # Also search reverse complement
    rc_seq = str(Seq(sequence).reverse_complement())
    for match in re.finditer(r'(?=(.GG))', rc_seq):
        pos = match.start()
        if pos >= guide_length:
            guide = rc_seq[pos - guide_length:pos]
            original_pos = len(sequence) - pos
            guides.append({
                'sequence': guide,
                'pam': rc_seq[pos:pos + 3],
                'position': original_pos,
                'strand': '-'
            })

    return guides
```

## Score On-Target Activity

```python
# Rule Set 2 position-weight matrix (Doench et al. 2016)
# Position 0 = PAM-distal, Position 19 = PAM-proximal
# Higher scores indicate preferred nucleotides at each position
RULE_SET_2_WEIGHTS = {
    # Position: {nucleotide: weight}
    0: {'A': 0, 'C': 0, 'G': 0.08, 'T': -0.08},
    1: {'A': 0.02, 'C': -0.06, 'G': 0.06, 'T': -0.02},
    # ... simplified - full matrix has all 20 positions
    18: {'A': -0.07, 'C': 0.13, 'G': -0.01, 'T': -0.05},
    19: {'A': -0.07, 'C': 0.03, 'G': 0.11, 'T': -0.07},
}

def calculate_gc_content(sequence):
    gc = sum(1 for nt in sequence.upper() if nt in 'GC')
    return gc / len(sequence)

def score_guide_activity(guide_seq):
    '''Score guide on-target activity (0-1 scale)

    Scoring criteria:
    - GC content 40-70%: optimal range (outside this = penalty)
    - Position-specific nucleotide preferences
    - No poly-T stretches (terminates Pol III transcription)

    Interpretation:
    - >0.6: High activity expected
    - 0.4-0.6: Moderate activity
    - <0.4: Low activity, consider alternatives
    '''
    guide_seq = guide_seq.upper()
    score = 0.5  # Base score

    # GC content penalty
    gc = calculate_gc_content(guide_seq)
    if gc < 0.4 or gc > 0.7:
        score -= 0.15

    # Poly-T penalty (>=4 consecutive T's)
    if 'TTTT' in guide_seq:
        score -= 0.3

    # Position-specific scoring (simplified)
    for pos, weights in RULE_SET_2_WEIGHTS.items():
        if pos < len(guide_seq):
            nt = guide_seq[pos]
            score += weights.get(nt, 0)

    return max(0, min(1, score))
```

## CRISPRscan Scoring

```python
# CRISPRscan uses a different model optimized for zebrafish
# but works well across species for Cas9

def crisprscan_score(guide_35mer):
    '''Score using CRISPRscan model

    Input: 35-mer (6bp upstream + 20bp guide + 3bp PAM + 6bp downstream)
    Output: Activity score 0-100

    Requires the crisprscan package:
    pip install crisprscan
    '''
    try:
        import crisprscan
        return crisprscan.score(guide_35mer)
    except ImportError:
        # Fallback to simplified scoring
        return score_guide_activity(guide_35mer[6:26]) * 100
```

## Design Workflow

**Goal:** Design the top N guide RNAs for a target gene, optionally restricted to coding exon regions.

**Approach:** Scan both strands for PAM sites, optionally filter to guides within exon coordinates, score each guide for on-target activity using GC content and position-weight criteria, and return the highest-scoring candidates.

```python
def design_guides_for_gene(gene_sequence, exon_coords=None, n_guides=5):
    '''Design top N guides for a gene

    Args:
        gene_sequence: Full gene sequence (DNA)
        exon_coords: List of (start, end) tuples for coding exons
        n_guides: Number of top guides to return

    Returns:
        List of guide dicts sorted by activity score
    '''
    # Find all PAM sites
    all_guides = find_pam_sites(gene_sequence)

    # Filter to coding regions if exon coordinates provided
    if exon_coords:
        coding_guides = []
        for guide in all_guides:
            for start, end in exon_coords:
                if start <= guide['position'] <= end:
                    coding_guides.append(guide)
                    break
        all_guides = coding_guides

    # Score each guide
    for guide in all_guides:
        guide['activity_score'] = score_guide_activity(guide['sequence'])

    # Sort by activity and return top N
    all_guides.sort(key=lambda x: x['activity_score'], reverse=True)
    return all_guides[:n_guides]
```

## Cas12a Guide Design

```python
def find_cas12a_guides(sequence, guide_length=23):
    '''Find Cas12a (Cpf1) guide sequences

    Cas12a differences from Cas9:
    - 5' PAM (TTTV where V = A/C/G)
    - Longer guide (23nt vs 20nt)
    - Staggered cut (5nt 5' overhang)
    - Lower off-target activity
    '''
    sequence = sequence.upper()
    guides = []

    # TTTV PAM pattern (5' of guide)
    for match in re.finditer(r'TTT[ACG]', sequence):
        pos = match.end()
        if pos + guide_length <= len(sequence):
            guide = sequence[pos:pos + guide_length]
            guides.append({
                'sequence': guide,
                'pam': match.group(),
                'position': pos,
                'strand': '+',
                'nuclease': 'Cas12a'
            })

    return guides
```

## Related Skills

- genome-engineering/off-target-prediction - Check off-targets after design
- crispr-screens/library-design - Pool multiple guides for screens
- primer-design/primer-basics - Design flanking primers for validation
