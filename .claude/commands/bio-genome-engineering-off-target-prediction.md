# bio-genome-engineering-off-target-prediction

> Predict CRISPR off-target sites using Cas-OFFinder and CFD scoring algorithms. Identify potential unintended cleavage sites genome-wide and assess guide specificity. Use when evaluating guide RNA specificity or selecting guides with minimal off-target risk.

## Version Compatibility

Reference examples tested with: pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Off-Target Prediction

**"Check my guide RNA for off-target sites"** → Search the genome for potential unintended cleavage sites allowing mismatches, then score each off-target by cutting frequency determination (CFD) to assess guide specificity.
- CLI: `cas-offinder` for genome-wide off-target search
- Python: CFD scoring with mismatch penalty matrices

## Cas-OFFinder (CLI)

Cas-OFFinder searches genomes for potential off-target sites allowing mismatches.

```bash
# Input file format (input.txt):
# Line 1: Path to genome directory (2bit or fasta index)
# Line 2: PAM pattern (N = any, R = A/G, Y = C/T)
# Line 3+: Guide sequences with mismatch tolerance

# Example input.txt:
# /path/to/genome
# NNNNNNNNNNNNNNNNNNNNNGG
# ATCGATCGATCGATCGATCGNNN 4

# Run Cas-OFFinder
cas-offinder input.txt C output.txt  # C = use CPU
cas-offinder input.txt G output.txt  # G = use GPU (faster)
```

## Cas-OFFinder Input Preparation

```python
def prepare_cas_offinder_input(guides, genome_path, max_mismatches=4, pam='NGG'):
    '''Prepare Cas-OFFinder input file

    Args:
        guides: List of 20nt guide sequences
        genome_path: Path to genome directory with .2bit or indexed fasta
        max_mismatches: Maximum mismatches to search (0-6 typical)
                       More mismatches = slower but more comprehensive
                       4 mismatches: good balance of speed and sensitivity
        pam: PAM sequence (NGG for SpCas9)
    '''
    lines = [genome_path]

    # Build pattern: 20 N's for guide + PAM
    pattern = 'N' * 20 + pam
    lines.append(pattern)

    # Add each guide with mismatch tolerance
    for guide in guides:
        # Append NNN to represent PAM positions (not matched)
        lines.append(f'{guide}NNN {max_mismatches}')

    return '\n'.join(lines)
```

## Parse Cas-OFFinder Output

```python
import pandas as pd

def parse_cas_offinder_output(output_file):
    '''Parse Cas-OFFinder results

    Output columns:
    - Guide: Query guide sequence
    - Chromosome: Target chromosome
    - Position: Genomic position (0-based)
    - Sequence: Off-target sequence found
    - Strand: + or -
    - Mismatches: Number of mismatches
    '''
    columns = ['guide', 'chrom', 'position', 'sequence', 'strand', 'mismatches']
    df = pd.read_csv(output_file, sep='\t', header=None, names=columns)

    # Sort by mismatches (fewer = more concerning)
    df = df.sort_values('mismatches')

    return df

def summarize_off_targets(df):
    '''Summarize off-target counts by mismatch number'''
    summary = df.groupby(['guide', 'mismatches']).size().unstack(fill_value=0)

    # Calculate specificity score
    # Fewer off-targets with 0-2 mismatches = higher specificity
    summary['specificity'] = 1 / (1 + summary.get(0, 0) * 100 +
                                      summary.get(1, 0) * 10 +
                                      summary.get(2, 0))
    return summary
```

## CFD Score Calculation

```python
# Cutting Frequency Determination (CFD) score
# Predicts cleavage probability at off-target sites
# From Doench et al. 2016

# Position-specific mismatch penalties
CFD_MISMATCH_SCORES = {
    # (position, ref_nt, target_nt): penalty_multiplier
    # Position 1 = PAM-proximal, Position 20 = PAM-distal
    # Values < 1 indicate reduced cutting
    (1, 'C', 'A'): 0.5, (1, 'C', 'G'): 0.7, (1, 'C', 'T'): 0.3,
    (1, 'G', 'A'): 0.4, (1, 'G', 'C'): 0.6, (1, 'G', 'T'): 0.3,
    # ... (full matrix has all 20 positions x 12 mismatch types)
    (20, 'C', 'A'): 0.9, (20, 'C', 'G'): 0.95, (20, 'C', 'T'): 0.85,
}

# PAM mismatch penalties
CFD_PAM_SCORES = {
    'AGG': 0.26, 'CGG': 0.11, 'TGG': 0.02,  # First position
    'GAG': 0.07, 'GCG': 0.03, 'GTG': 0.02,  # Second position
    'GGA': 0.01, 'GGC': 0.01, 'GGT': 0.01,  # Third position
}

def calculate_cfd_score(guide, off_target, pam='NGG'):
    '''Calculate CFD score for an off-target site

    CFD score interpretation:
    - 1.0: Perfect match (on-target)
    - >0.5: High probability of cleavage (concerning)
    - 0.1-0.5: Moderate probability
    - <0.1: Low probability (likely acceptable)
    '''
    score = 1.0

    # Apply mismatch penalties
    for i, (g, t) in enumerate(zip(guide, off_target[:20]), 1):
        if g != t:
            key = (i, g, t)
            penalty = CFD_MISMATCH_SCORES.get(key, 0.5)  # Default 0.5
            score *= penalty

    # Apply PAM penalty if not NGG
    off_pam = off_target[20:23]
    if off_pam != 'NGG' and off_pam in CFD_PAM_SCORES:
        score *= CFD_PAM_SCORES[off_pam]

    return score
```

## Aggregate Off-Target Score

```python
def calculate_guide_specificity(guide, off_targets):
    '''Calculate aggregate specificity score for a guide

    Uses sum of CFD scores for all off-targets.
    Lower aggregate = more specific guide.

    Specificity score interpretation:
    - >0.9: Highly specific (excellent)
    - 0.7-0.9: Specific (good)
    - 0.5-0.7: Moderate specificity (acceptable)
    - <0.5: Poor specificity (consider alternatives)
    '''
    cfd_sum = sum(calculate_cfd_score(guide, ot['sequence'], ot.get('pam', 'NGG'))
                  for ot in off_targets)

    # Specificity = 1 / (1 + sum of off-target CFD scores)
    specificity = 1 / (1 + cfd_sum)

    return specificity
```

## CRISPOR-style Analysis

**Goal:** Run a complete off-target analysis pipeline from a single guide sequence to a scored, ranked list of potential off-target sites.

**Approach:** Prepare a Cas-OFFinder input file, run the genome-wide mismatch search, parse the tabular output, calculate CFD scores for each hit, and flag high-risk off-targets by cleavage probability.

```python
def analyze_guide_specificity(guide_seq, genome_fasta, max_mm=4):
    '''Full off-target analysis workflow

    1. Run Cas-OFFinder to find potential sites
    2. Calculate CFD scores for each site
    3. Compute aggregate specificity
    4. Flag high-risk off-targets
    '''
    import subprocess
    import tempfile

    # Prepare input
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(f'{genome_fasta}\n')
        f.write('N' * 20 + 'NGG\n')
        f.write(f'{guide_seq}NNN {max_mm}\n')
        input_file = f.name

    output_file = input_file.replace('.txt', '_out.txt')

    # Run Cas-OFFinder
    subprocess.run(['cas-offinder', input_file, 'C', output_file], check=True)

    # Parse results
    off_targets = parse_cas_offinder_output(output_file)

    # Calculate CFD for each
    off_targets['cfd_score'] = off_targets.apply(
        lambda row: calculate_cfd_score(guide_seq, row['sequence']), axis=1
    )

    # Flag high-risk (CFD > 0.5 and in exon)
    # Would need exon annotations for full implementation

    return off_targets
```

## Related Skills

- genome-engineering/grna-design - Design guides before off-target check
- variant-calling/variant-annotation - Check if off-targets overlap known variants
- genome-intervals/bed-file-basics - Intersect off-targets with genomic features
