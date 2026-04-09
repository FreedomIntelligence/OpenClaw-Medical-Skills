# bio-alignment-msa-statistics

> Calculate alignment statistics including sequence identity, conservation scores, substitution matrices, and similarity metrics. Use when comparing alignment quality, measuring sequence divergence, and analyzing evolutionary patterns.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# MSA Statistics

Calculate sequence identity, conservation scores, substitution counts, and other alignment metrics.

## Required Import

**Goal:** Load modules for alignment I/O, substitution scoring, and statistical calculations.

**Approach:** Import AlignIO for reading alignments, Counter for column analysis, numpy for matrix operations, and math for entropy calculations.

```python
from Bio import AlignIO
from Bio.Align import substitution_matrices
from collections import Counter
import numpy as np
import math
```

## Pairwise Identity

**"Calculate percent identity"** → Compute the fraction of identical aligned residues between sequence pairs.

**Goal:** Measure sequence similarity as percent identity for individual pairs or across all sequences in an alignment.

**Approach:** Count matching non-gap positions divided by total aligned positions; optionally compute a full N-by-N identity matrix.

### Calculate Identity Between Two Sequences
```python
def pairwise_identity(seq1, seq2):
    matches = sum(a == b and a != '-' for a, b in zip(seq1, seq2))
    aligned_positions = sum(a != '-' or b != '-' for a, b in zip(seq1, seq2))
    return matches / aligned_positions if aligned_positions > 0 else 0

alignment = AlignIO.read('alignment.fasta', 'fasta')
seq1, seq2 = str(alignment[0].seq), str(alignment[1].seq)
identity = pairwise_identity(seq1, seq2)
print(f'Identity: {identity * 100:.1f}%')
```

### Identity Matrix for All Sequences
```python
def identity_matrix(alignment):
    n = len(alignment)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            seq_i = str(alignment[i].seq)
            seq_j = str(alignment[j].seq)
            ident = pairwise_identity(seq_i, seq_j)
            matrix[i, j] = matrix[j, i] = ident
    return matrix

alignment = AlignIO.read('alignment.fasta', 'fasta')
mat = identity_matrix(alignment)
seq_ids = [r.id for r in alignment]
print('Pairwise Identity Matrix:')
print(f'{"":>10}', ' '.join(f'{s[:8]:>8}' for s in seq_ids))
for i, row in enumerate(mat):
    print(f'{seq_ids[i][:10]:>10}', ' '.join(f'{v*100:>7.1f}%' for v in row))
```

## Conservation Score

**Goal:** Quantify per-column and overall alignment conservation to identify conserved and variable regions.

**Approach:** Calculate the fraction of the most common residue at each column, optionally ignoring gaps, and smooth with a sliding window.

### Per-Column Conservation
```python
def column_conservation(alignment, col_idx, ignore_gaps=True):
    column = alignment[:, col_idx]
    if ignore_gaps:
        column = column.replace('-', '')
    if not column:
        return 0.0
    counts = Counter(column)
    most_common_count = counts.most_common(1)[0][1]
    return most_common_count / len(column)

alignment = AlignIO.read('alignment.fasta', 'fasta')
for i in range(min(20, alignment.get_alignment_length())):
    cons = column_conservation(alignment, i)
    print(f'Column {i}: {cons*100:.0f}% conserved')
```

### Average Conservation Across Alignment
```python
def average_conservation(alignment, ignore_gaps=True):
    scores = []
    for col_idx in range(alignment.get_alignment_length()):
        scores.append(column_conservation(alignment, col_idx, ignore_gaps))
    return sum(scores) / len(scores)

avg_cons = average_conservation(alignment)
print(f'Average conservation: {avg_cons*100:.1f}%')
```

### Conservation Profile
```python
def conservation_profile(alignment, window=10):
    profile = []
    for i in range(alignment.get_alignment_length()):
        start = max(0, i - window // 2)
        end = min(alignment.get_alignment_length(), i + window // 2)
        scores = [column_conservation(alignment, j) for j in range(start, end)]
        profile.append(sum(scores) / len(scores))
    return profile

profile = conservation_profile(alignment, window=10)
```

## Substitution Counts

**Goal:** Tabulate observed substitution frequencies from the alignment for evolutionary analysis or custom scoring matrices.

**Approach:** Enumerate all pairwise non-gap character comparisons at each column and tally substitution pairs.

### Count Substitutions from Alignment
```python
def substitution_counts(alignment):
    from collections import defaultdict
    counts = defaultdict(int)
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        chars = [c for c in column if c != '-']
        for i, c1 in enumerate(chars):
            for c2 in chars[i+1:]:
                if c1 != c2:
                    pair = tuple(sorted([c1, c2]))
                    counts[pair] += 1
    return dict(counts)

subs = substitution_counts(alignment)
print('Substitution counts:')
for pair, count in sorted(subs.items(), key=lambda x: -x[1])[:10]:
    print(f'  {pair[0]}<->{pair[1]}: {count}')
```

### Build Substitution Matrix from MSA
```python
def build_substitution_matrix(alignment):
    from collections import defaultdict
    matrix = defaultdict(lambda: defaultdict(int))

    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        chars = [c for c in column if c != '-']
        for c1 in chars:
            for c2 in chars:
                matrix[c1][c2] += 1

    return {k: dict(v) for k, v in matrix.items()}

sub_matrix = build_substitution_matrix(alignment)
```

### Using Alignment.substitutions (Pairwise Alignments)
For pairwise alignments created with `PairwiseAligner`, use the built-in `.substitutions` property:

```python
from Bio.Align import PairwiseAligner

aligner = PairwiseAligner(mode='global', match_score=1, mismatch_score=-1)
alignments = aligner.align(seq1, seq2)
substitutions = alignments[0].substitutions

# Returns Array with substitution counts
print(substitutions)
```

## Information Content

**Goal:** Measure column variability using Shannon entropy and derive information content for identifying functionally important positions.

**Approach:** Compute Shannon entropy from character frequencies per column; information content is max entropy minus observed entropy.

### Shannon Entropy Per Column
```python
import math

def shannon_entropy(column, ignore_gaps=True):
    if ignore_gaps:
        column = column.replace('-', '')
    if not column:
        return 0.0
    counts = Counter(column)
    total = len(column)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

alignment = AlignIO.read('alignment.fasta', 'fasta')
for i in range(min(20, alignment.get_alignment_length())):
    column = alignment[:, i]
    ent = shannon_entropy(column)
    print(f'Column {i}: entropy = {ent:.2f} bits')
```

### Information Content (Max Entropy - Observed Entropy)
```python
def information_content(column, alphabet_size=4):
    max_entropy = math.log2(alphabet_size)  # 4 for DNA, 20 for protein
    observed_entropy = shannon_entropy(column)
    return max_entropy - observed_entropy

# DNA alignment
for i in range(min(20, alignment.get_alignment_length())):
    column = alignment[:, i]
    ic = information_content(column, alphabet_size=4)
    print(f'Column {i}: IC = {ic:.2f} bits')
```

## Gap Statistics

**Goal:** Summarize gap distribution across the alignment to assess alignment quality and identify problematic regions.

**Approach:** Calculate gap fractions per column and aggregate statistics including total gaps, gap-free columns, and gappiest sequence/column.

### Gap Fraction Per Column
```python
def gap_profile(alignment):
    profile = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        gap_fraction = column.count('-') / len(alignment)
        profile.append(gap_fraction)
    return profile

gaps = gap_profile(alignment)
avg_gaps = sum(gaps) / len(gaps)
print(f'Average gap fraction: {avg_gaps*100:.1f}%')
```

### Gap Statistics Summary
```python
def gap_statistics(alignment):
    num_seqs = len(alignment)
    num_cols = alignment.get_alignment_length()

    total_positions = num_seqs * num_cols
    total_gaps = sum(str(r.seq).count('-') for r in alignment)

    gaps_per_seq = [str(r.seq).count('-') for r in alignment]
    gaps_per_col = [alignment[:, i].count('-') for i in range(num_cols)]

    return {
        'total_gaps': total_gaps,
        'gap_fraction': total_gaps / total_positions,
        'gappiest_seq': max(range(num_seqs), key=lambda i: gaps_per_seq[i]),
        'gappiest_col': max(range(num_cols), key=lambda i: gaps_per_col[i]),
        'gap_free_cols': sum(1 for g in gaps_per_col if g == 0),
    }

stats = gap_statistics(alignment)
print(f"Total gaps: {stats['total_gaps']}")
print(f"Gap fraction: {stats['gap_fraction']*100:.1f}%")
print(f"Gap-free columns: {stats['gap_free_cols']}")
```

## Alignment Quality Metrics

**Goal:** Score alignment quality using sum-of-pairs or simple match/mismatch/gap scoring across all columns.

**Approach:** For each column, score all pairwise residue comparisons and sum across the alignment.

### Overall Alignment Score
```python
def alignment_score(alignment, match=1, mismatch=-1, gap=-2):
    total_score = 0
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        for i, c1 in enumerate(column):
            for c2 in column[i+1:]:
                if c1 == '-' or c2 == '-':
                    total_score += gap
                elif c1 == c2:
                    total_score += match
                else:
                    total_score += mismatch
    return total_score

score = alignment_score(alignment)
print(f'Alignment score: {score}')
```

### Sum of Pairs Score
```python
def sum_of_pairs(alignment, substitution_matrix=None):
    if substitution_matrix is None:
        substitution_matrix = substitution_matrices.load('BLOSUM62')

    total = 0
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        for i, c1 in enumerate(column):
            for c2 in column[i+1:]:
                if c1 != '-' and c2 != '-':
                    total += substitution_matrix.get((c1, c2), 0)
    return total
```

## Position-Specific Score Matrix (PSSM)

**Goal:** Build a position-specific score matrix (PSSM) from the alignment for motif analysis or sequence scoring.

**Approach:** Count non-gap character frequencies at each column, producing a list of per-position dictionaries.

```python
def position_specific_score_matrix(alignment):
    pssm = []
    for col_idx in range(alignment.get_alignment_length()):
        column = alignment[:, col_idx]
        counts = Counter(column)
        if '-' in counts:
            del counts['-']
        pssm.append(dict(counts))
    return pssm

alignment = AlignIO.read('alignment.fasta', 'fasta')
pssm = position_specific_score_matrix(alignment)
for i, row in enumerate(pssm[:10]):
    print(f'Position {i}: {row}')
```

## Note on Bio.Align.AlignInfo

The `AlignInfo.SummaryInfo` class is **deprecated** in recent Biopython versions. Use the custom functions in this skill instead:
- For PSSM: use `position_specific_score_matrix()` above
- For information content: use `information_content()` function earlier in this skill
- For consensus: see msa-parsing skill

## Quick Reference: Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| Identity | Fraction of identical residues | 0-1 |
| Conservation | Most common residue frequency | 0-1 |
| Shannon Entropy | Variability measure | 0 to log2(alphabet) |
| Information Content | Max entropy - observed entropy | 0 to log2(alphabet) |
| Gap Fraction | Proportion of gaps | 0-1 |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ZeroDivisionError` | Empty column after gap removal | Check for gap-only columns |
| `KeyError` | Character not in substitution matrix | Handle gaps separately |
| Negative IC | Wrong alphabet size | Use 4 for DNA, 20 for protein |

## Related Skills

- msa-parsing - Parse and manipulate alignments
- alignment-io - Read/write alignment files
- pairwise-alignment - Create and score pairwise alignments
- sequence-manipulation/sequence-properties - Sequence-level statistics
