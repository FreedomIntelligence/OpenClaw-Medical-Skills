# bio-ribo-seq-ribosome-periodicity

> Validate Ribo-seq data quality by checking 3-nucleotide periodicity and calculating P-site offsets. Use when assessing library quality or determining read offsets for downstream analysis.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pysam 0.22+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribosome Periodicity Analysis

**"Check if my Ribo-seq data shows triplet periodicity"** → Validate Ribo-seq library quality by verifying 3-nucleotide translocation patterns and calculating P-site offsets from metagene profiles.
- Python: `plastid` for P-site offset calculation and metagene analysis

## 3-Nucleotide Periodicity

**Goal:** Verify that Ribo-seq reads exhibit the expected 3-nucleotide translocation pattern characteristic of active translation.

**Approach:** Load P-site mapped reads and compute metagene profiles around start codons to check for triplet periodicity.

Ribosomes move 3 nucleotides per codon. Good Ribo-seq data shows strong periodicity:

```python
from plastid import BAMGenomeArray, FivePrimeMapFactory, GenomicSegment
import numpy as np
import matplotlib.pyplot as plt

# Load aligned reads
alignments = BAMGenomeArray('riboseq.bam', mapping=FivePrimeMapFactory())

# Get metagene around start codons
# Expect strong 3-nt periodicity
```

## Calculate P-site Offset

**Goal:** Determine the optimal P-site offset from the 5' end of ribosome footprints for accurate codon-level positioning.

**Approach:** Run metagene analysis around annotated start codons and identify the offset that aligns the signal peak with the AUG position.

```python
from plastid import metagene_analysis

# The P-site offset varies by read length
# Typically 12-15 nt from 5' end for 28-30 nt reads

def determine_psite_offset(bam_path, annotation_file):
    '''Determine optimal P-site offset from metagene analysis'''
    from plastid import GTF2_TranscriptAssembler, BAMGenomeArray

    # Load annotations
    transcripts = list(GTF2_TranscriptAssembler(annotation_file))

    # Load reads
    alignments = BAMGenomeArray(bam_path, mapping=FivePrimeMapFactory())

    # Metagene around start codons
    # Peak should align with start codon position
    metagene_data = metagene_analysis(
        transcripts,
        alignments,
        upstream=50,
        downstream=100
    )

    return metagene_data
```

## Metagene Plots

**Goal:** Visualize the metagene profile around start codons with frame-colored bars and a periodicity power spectrum.

**Approach:** Plot read counts by reading frame and compute FFT to confirm a dominant period of 3 nucleotides.

```python
def plot_metagene(metagene_data, offset=12):
    '''Plot metagene profile around start codon'''
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Frame 0, 1, 2 around start codon
    positions = np.arange(-50, 100)

    # Plot by frame
    for frame in range(3):
        frame_positions = positions[positions % 3 == frame]
        counts = metagene_data[positions % 3 == frame]
        axes[0].bar(frame_positions, counts, alpha=0.7, label=f'Frame {frame}')

    axes[0].set_xlabel('Position relative to start codon')
    axes[0].set_ylabel('Normalized counts')
    axes[0].legend()
    axes[0].axvline(0, color='red', linestyle='--', label='Start')

    # Periodicity
    from scipy.fft import fft
    fft_result = np.abs(fft(metagene_data))
    freq = np.fft.fftfreq(len(metagene_data))

    axes[1].plot(1/freq[1:len(freq)//2], fft_result[1:len(freq)//2])
    axes[1].set_xlabel('Period (nt)')
    axes[1].set_ylabel('Power')
    axes[1].axvline(3, color='red', linestyle='--')

    plt.tight_layout()
    plt.savefig('periodicity.pdf')
```

## Assess by Read Length

**Goal:** Evaluate 3-nucleotide periodicity strength for each read length to identify the most informative footprint sizes.

**Approach:** Group reads by query length, compute periodicity score per group, and retain lengths with strong triplet signal.

```python
def periodicity_by_length(bam_path, annotation_file):
    '''Calculate periodicity score for each read length'''
    import pysam

    # Group reads by length
    reads_by_length = {}
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for read in bam:
            if not read.is_unmapped:
                length = read.query_length
                if length not in reads_by_length:
                    reads_by_length[length] = []
                reads_by_length[length].append(read)

    # Calculate periodicity for each length
    # Good lengths show strong 3-nt periodicity
    results = {}
    for length, reads in reads_by_length.items():
        if len(reads) > 1000:  # Need sufficient reads
            periodicity = calculate_periodicity(reads, annotation_file)
            results[length] = periodicity

    return results
```

## P-site Offset Table

Common P-site offsets by read length (5' end mapping):

| Read Length | P-site Offset |
|-------------|---------------|
| 28 nt | 12 |
| 29 nt | 12 |
| 30 nt | 13 |
| 31 nt | 13 |
| 32 nt | 14 |

## Validate with RiboCode

**Goal:** Run an automated periodicity and ORF detection pipeline as an independent validation of data quality.

**Approach:** Execute RiboCode's one-step command, which internally assesses periodicity and generates diagnostic plots.

```bash
# RiboCode includes periodicity analysis
RiboCode_onestep \
    -g annotation.gtf \
    -r riboseq.bam \
    -f genome.fa \
    -o output_dir

# Check output for periodicity plots
```

## Related Skills

- riboseq-preprocessing - Generate aligned BAM
- orf-detection - Uses P-site offsets
- translation-efficiency - Requires proper positioning
