# bio-splicing-qc

> Assesses RNA-seq data quality for splicing analysis including junction saturation curves, splice site strength scoring, and junction coverage metrics using RSeQC. Use when evaluating data suitability for splicing analysis or troubleshooting low event detection.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, pandas 2.2+, pysam 0.22+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Splicing Quality Control

Assess RNA-seq data quality specifically for alternative splicing analysis.

## Junction Saturation Analysis

**Goal:** Determine whether sequencing depth is sufficient for comprehensive splicing detection.

**Approach:** Run RSeQC junction saturation on BAM files and check whether the junction discovery curve reaches a plateau.

**"Assess RNA-seq quality for splicing analysis"** -> Evaluate junction saturation, junction novelty rate, splice site strength, and read coverage.
- Python/CLI: `junction_saturation.py`, `junction_annotation.py` (RSeQC)
- Python: maxentpy for splice site scoring, pysam for junction read counting

```bash
# RSeQC junction saturation (check sequencing depth)
# Note: -s flag removed in RSeQC v3.0
junction_saturation.py \
    -i sample.bam \
    -r annotation.bed \
    -o sample_junc_sat
```

```python
import subprocess
import matplotlib.pyplot as plt
import pandas as pd

# Run junction saturation for multiple samples
samples = ['sample1.bam', 'sample2.bam', 'sample3.bam']

for sample in samples:
    subprocess.run([
        'junction_saturation.py',
        '-i', sample,
        '-r', 'annotation.bed',
        '-o', sample.replace('.bam', '_junc_sat')
    ], check=True)

# Parse results and check for plateau
# Plateau indicates sufficient depth for splicing analysis
# If curves still rising, may need more sequencing depth
```

## Junction Annotation

**Goal:** Classify observed junctions as known, partially novel, or completely novel relative to annotation.

**Approach:** Run RSeQC junction annotation and compute the ratio of known to novel junctions as a data quality indicator.

```bash
# Classify junctions as known, partial novel, or complete novel
junction_annotation.py \
    -i sample.bam \
    -r annotation.bed \
    -o sample_junc_annot
```

```python
import pandas as pd

# Analyze junction annotation results
junc_stats = pd.read_csv('sample_junc_annot.junction.xls', sep='\t')

# Calculate junction type proportions
total = junc_stats['total_splicing_events'].sum()
known = junc_stats[junc_stats['annotation'] == 'known']['total_splicing_events'].sum()
novel = total - known

print(f'Known junctions: {known/total:.1%}')
print(f'Novel junctions: {novel/total:.1%}')

# High novel junction rate may indicate:
# - Incomplete annotation
# - Mapping artifacts
# - Interesting biology (cancer, tissue-specific)
```

## Splice Site Strength Scoring

**Goal:** Score donor and acceptor splice sites to identify weak or cryptic splice sites.

**Approach:** Use MaxEntScan (via maxentpy) to compute information-theoretic scores for 5' and 3' splice site sequences.

```python
# MaxEntScan scoring via maxentpy
# 5'ss (donor): typical score 8-10 bits
# 3'ss (acceptor): typical score 8-12 bits

from maxentpy import maxent
from maxentpy.maxent import score5, score3

# Score 5' splice site (9bp: 3 exon + 6 intron)
donor_seq = 'CAGGTAAGT'  # Consensus: CAG|GTAAGT
score_5ss = score5(donor_seq)
print(f"5'ss score: {score_5ss:.2f}")

# Score 3' splice site (23bp: 20 intron + 3 exon)
acceptor_seq = 'TTTTTTTTTTTTTTTTTTTTCAG'
score_3ss = score3(acceptor_seq)
print(f"3'ss score: {score_3ss:.2f}")

# Weak splice sites (score < 5) may indicate:
# - Alternative/cryptic splice sites
# - Annotation errors
# - Regulatory splice sites
```

## Junction Read Coverage

**Goal:** Profile the distribution of junction-spanning read counts across all splice sites in a BAM file.

**Approach:** Parse CIGAR strings for N operations (splice junctions) using pysam and tally reads per junction.

```python
import pysam
import pandas as pd

def count_junction_reads(bam_path, min_overhang=8):
    '''Count junction-spanning reads per splice site.'''
    bam = pysam.AlignmentFile(bam_path, 'rb')
    junction_counts = {}

    for read in bam.fetch():
        if read.is_unmapped:
            continue

        # Check CIGAR for splice junctions (N operation)
        ref_pos = read.reference_start
        for op, length in read.cigartuples:
            if op == 3:  # N = splice junction
                junction = (read.reference_name, ref_pos, ref_pos + length)
                junction_counts[junction] = junction_counts.get(junction, 0) + 1
            if op in [0, 2, 3]:  # M, D, N consume reference
                ref_pos += length

    bam.close()
    return junction_counts

# Analyze coverage distribution
junctions = count_junction_reads('sample.bam')
counts = list(junctions.values())

print(f'Total junctions: {len(junctions)}')
print(f'Junctions >= 10 reads: {sum(1 for c in counts if c >= 10)}')
print(f'Junctions >= 20 reads: {sum(1 for c in counts if c >= 20)}')
```

## Quality Thresholds

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Junction saturation | Plateau reached | Near plateau | Still rising |
| Known junctions | > 80% | > 60% | < 60% |
| Junctions >= 10 reads | > 50% | > 30% | < 30% |
| 5'ss score | > 8 | > 5 | < 5 |
| 3'ss score | > 8 | > 5 | < 5 |

## Troubleshooting Low Detection

| Issue | Possible Causes | Solutions |
|-------|-----------------|-----------|
| Few junctions | Low depth, short reads | More sequencing, longer reads |
| Low saturation | Insufficient depth | Increase sequencing |
| Many novel junctions | Annotation gaps | Update annotation, check organism |
| Weak splice sites | Cryptic splicing | Validate experimentally |

## Related Skills

- splicing-quantification - Quantify after QC passes
- read-alignment/star-alignment - Alignment quality affects junctions
- read-qc/quality-reports - General sequencing QC
