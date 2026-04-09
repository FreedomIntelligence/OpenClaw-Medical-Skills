# bio-ribo-seq-ribosome-stalling

> Detect ribosome pausing and stalling sites from Ribo-seq data at codon resolution. Use when studying translational regulation, identifying pause sites, or analyzing codon-specific translation dynamics.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, numpy 1.26+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribosome Stalling Detection

**"Find ribosome pause sites in my data"** → Detect codon-level ribosome stalling and pausing events from Ribo-seq footprint density, identifying positions with abnormally high ribosome occupancy.
- Python: `plastid` for codon-resolution density calculation, `scipy` for statistical scoring

## Concept

Ribosome stalling/pausing occurs when ribosomes slow or stop at specific codons:
- Rare codons (low tRNA availability)
- Specific amino acid motifs (polyproline)
- Regulatory pause sites (upstream of stress response genes)
- Nascent chain interactions

## Calculate Codon-Level Occupancy

**Goal:** Quantify ribosome occupancy at each codon position across all transcripts.

**Approach:** Map reads to P-sites using a fixed offset, then bin counts into codons along each CDS.

```python
from plastid import BAMGenomeArray, GTF2_TranscriptAssembler, FivePrimeMapFactory
import numpy as np
from collections import defaultdict

def get_codon_occupancy(bam_path, gtf_path, psite_offset=12):
    '''Calculate ribosome occupancy per codon'''
    # Load reads with P-site mapping
    alignments = BAMGenomeArray(
        bam_path,
        mapping=FivePrimeMapFactory(offset=psite_offset)
    )

    transcripts = list(GTF2_TranscriptAssembler(gtf_path))

    codon_counts = defaultdict(lambda: defaultdict(int))

    for tx in transcripts:
        if tx.cds_start is None:
            continue

        cds = tx.get_cds()
        cds_seq = tx.get_sequence(cds)

        # Get counts at each position
        counts = alignments.count_in_region(cds)

        # Assign to codons
        for i in range(0, len(cds_seq) - 2, 3):
            codon = cds_seq[i:i+3]
            codon_pos = i // 3
            codon_counts[tx.get_name()][codon_pos] = counts  # Simplified

    return codon_counts
```

## Identify Pause Sites

**Goal:** Detect codon positions with significantly elevated ribosome occupancy indicative of translational pausing.

**Approach:** Z-score normalize occupancy per transcript and flag positions exceeding a threshold (default z > 3).

```python
def find_pause_sites(codon_occupancy, threshold_zscore=3):
    '''Find positions with significantly elevated ribosome occupancy

    Pause sites have much higher occupancy than surrounding codons
    '''
    pause_sites = []

    for tx, occupancy in codon_occupancy.items():
        values = np.array(list(occupancy.values()))

        if len(values) < 10 or values.sum() < 100:
            continue

        # Z-score normalization
        mean_occ = values.mean()
        std_occ = values.std()

        if std_occ == 0:
            continue

        zscores = (values - mean_occ) / std_occ

        # Find positions above threshold
        for pos, zscore in enumerate(zscores):
            if zscore > threshold_zscore:
                pause_sites.append({
                    'transcript': tx,
                    'codon_position': pos,
                    'occupancy': values[pos],
                    'zscore': zscore
                })

    return pause_sites
```

## Codon-Specific Occupancy

**Goal:** Calculate average ribosome occupancy for each of the 64 codon types across all genes.

**Approach:** Aggregate read density per codon identity across all CDS positions and compute per-codon mean occupancy.

```python
from Bio.Seq import Seq
from Bio.Data import CodonTable

def codon_occupancy_table(bam_path, gtf_path, psite_offset=12):
    '''Calculate average occupancy per codon type'''
    # Count reads per codon type
    codon_reads = defaultdict(list)

    alignments = BAMGenomeArray(bam_path,
                                 mapping=FivePrimeMapFactory(offset=psite_offset))
    transcripts = list(GTF2_TranscriptAssembler(gtf_path))

    for tx in transcripts:
        if tx.cds_start is None:
            continue

        cds = tx.get_cds()
        cds_seq = str(tx.get_sequence(cds))

        # Get read density
        density = alignments.get_density(cds)

        for i in range(0, len(cds_seq) - 2, 3):
            codon = cds_seq[i:i+3]
            if len(density) > i + 2:
                codon_reads[codon].append(sum(density[i:i+3]))

    # Calculate mean occupancy per codon
    codon_means = {codon: np.mean(reads) for codon, reads in codon_reads.items()}

    return codon_means
```

## Correlate with Codon Usage

**Goal:** Test whether ribosome pausing correlates with tRNA availability across codons.

**Approach:** Compute Spearman rank correlation between per-codon occupancy and tRNA abundance; expect a negative relationship.

```python
def correlate_with_trna(codon_occupancy, trna_abundance):
    '''Test if pausing correlates with tRNA availability

    Rare codons (low tRNA) should have higher occupancy
    '''
    from scipy import stats

    codons = list(set(codon_occupancy.keys()) & set(trna_abundance.keys()))

    occ = [codon_occupancy[c] for c in codons]
    trna = [trna_abundance[c] for c in codons]

    corr, pval = stats.spearmanr(occ, trna)

    return corr, pval  # Expect negative correlation
```

## Motif Analysis at Pause Sites

**Goal:** Extract amino acid sequence context around identified pause sites to discover recurrent motifs.

**Approach:** Translate the coding region flanking each pause site and collect fixed-width windows for motif analysis.

```python
def extract_pause_motifs(pause_sites, sequences, window=10):
    '''Extract amino acid context around pause sites'''
    motifs = []

    for site in pause_sites:
        tx = site['transcript']
        pos = site['codon_position']
        seq = sequences.get(tx, '')

        if len(seq) > pos * 3 + window * 3:
            start = max(0, (pos - window) * 3)
            end = min(len(seq), (pos + window + 1) * 3)
            aa_seq = str(Seq(seq[start:end]).translate())
            motifs.append(aa_seq)

    return motifs
```

## Known Pause Motifs

| Motif | Description |
|-------|-------------|
| PPP | Polyproline (ribosome tunnel interaction) |
| XPX | Proline-containing |
| D/E-rich | Negatively charged nascent chain |
| Stop codon context | Influenced by nucleotides around stop |

## Related Skills

- ribosome-periodicity - Validate data quality
- orf-detection - Context for pause sites
- translation-efficiency - Gene-level translation
