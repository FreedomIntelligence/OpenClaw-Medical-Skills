# bio-cfdna-preprocessing

> Preprocesses cell-free DNA sequencing data including adapter trimming, alignment optimized for short fragments, and UMI-aware duplicate removal using fgbio. Applies cfDNA-specific quality thresholds and fragment length filtering. Use when processing plasma cfDNA sequencing data before downstream analysis.

## Version Compatibility

Reference examples tested with: BWA 0.7.17+, fgbio 2.1+, matplotlib 3.8+, numpy 1.26+, pysam 0.22+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# cfDNA Preprocessing

**"Preprocess my cfDNA sequencing data"** → Process cell-free DNA reads with UMI extraction, consensus calling, and error suppression for sensitive variant detection.
- CLI: `fgbio FastqToBam` → `fgbio GroupReadsByUmi` → `fgbio CallMolecularConsensusReads`

Preprocess cell-free DNA sequencing data with UMI-aware deduplication.

## Pre-Analytical Considerations

| Factor | Requirement | Rationale |
|--------|-------------|-----------|
| Collection tube | Streck (7 days) or EDTA (6 hrs) | Prevents cell lysis |
| Processing time | ASAP or per tube specs | Minimizes genomic DNA contamination |
| Hemolysis | Avoid | Releases cellular DNA |
| Storage | -80C after extraction | Prevents degradation |

## UMI-Aware Pipeline with fgbio

```bash
# fgbio 3.0+ (actively maintained)

# Step 1: Extract UMIs from reads and annotate
fgbio ExtractUmisFromBam \
    --input raw.bam \
    --output with_umis.bam \
    --read-structure 3M2S+T 3M2S+T \
    --molecular-index-tags ZA ZB \
    --single-tag RX

# Step 2: Align with BWA-MEM
# Use -Y for soft-clipping (preserves UMIs)
bwa mem -t 8 -Y reference.fa with_umis.bam | \
    samtools view -bS - > aligned.bam

# Step 3: Group reads by UMI
fgbio GroupReadsByUmi \
    --input aligned.bam \
    --output grouped.bam \
    --strategy adjacency \
    --edits 1 \
    --min-map-q 20

# Step 4: Call molecular consensus reads
fgbio CallMolecularConsensusReads \
    --input grouped.bam \
    --output consensus.bam \
    --min-reads 2 \
    --min-input-base-quality 20

# Step 5: Filter consensus reads
fgbio FilterConsensusReads \
    --input consensus.bam \
    --output filtered_consensus.bam \
    --ref reference.fa \
    --min-reads 2 \
    --max-read-error-rate 0.05 \
    --min-base-quality 30
```

## Python Implementation

**Goal:** Run the complete cfDNA UMI-consensus pipeline from raw BAM to error-suppressed consensus reads in a single Python function call.

**Approach:** Chain fgbio operations (UMI extraction, grouping, consensus calling, filtering) with BWA alignment, handling intermediate files and cleanup within the function.

```python
import subprocess
import pysam
from pathlib import Path


def preprocess_cfdna(input_bam, output_bam, reference, read_structure='3M2S+T 3M2S+T',
                     min_reads=2, threads=8):
    '''
    Full cfDNA preprocessing pipeline with fgbio.

    Args:
        input_bam: Input BAM with UMIs in reads
        output_bam: Output consensus BAM
        reference: Reference FASTA path
        read_structure: UMI read structure
        min_reads: Minimum reads per UMI group
        threads: CPU threads
    '''
    work_dir = Path(output_bam).parent
    prefix = Path(output_bam).stem

    # Extract UMIs
    with_umis = work_dir / f'{prefix}_umis.bam'
    subprocess.run([
        'fgbio', 'ExtractUmisFromBam',
        '--input', input_bam,
        '--output', str(with_umis),
        '--read-structure', read_structure,
        '--single-tag', 'RX'
    ], check=True)

    # Align
    aligned = work_dir / f'{prefix}_aligned.bam'
    cmd = f'bwa mem -t {threads} -Y {reference} {with_umis} | samtools view -bS - > {aligned}'
    subprocess.run(cmd, shell=True, check=True)

    # Sort
    sorted_bam = work_dir / f'{prefix}_sorted.bam'
    pysam.sort('-@', str(threads), '-o', str(sorted_bam), str(aligned))

    # Group by UMI
    grouped = work_dir / f'{prefix}_grouped.bam'
    subprocess.run([
        'fgbio', 'GroupReadsByUmi',
        '--input', str(sorted_bam),
        '--output', str(grouped),
        '--strategy', 'adjacency',
        '--edits', '1'
    ], check=True)

    # Consensus calling
    consensus = work_dir / f'{prefix}_consensus.bam'
    subprocess.run([
        'fgbio', 'CallMolecularConsensusReads',
        '--input', str(grouped),
        '--output', str(consensus),
        '--min-reads', str(min_reads)
    ], check=True)

    # Filter consensus
    subprocess.run([
        'fgbio', 'FilterConsensusReads',
        '--input', str(consensus),
        '--output', output_bam,
        '--ref', reference,
        '--min-reads', str(min_reads)
    ], check=True)

    return output_bam
```

## Fragment Size Analysis

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt


def analyze_fragment_sizes(bam_path, max_size=500):
    '''Analyze cfDNA fragment size distribution.'''
    bam = pysam.AlignmentFile(bam_path, 'rb')
    sizes = []

    for read in bam.fetch():
        if read.is_proper_pair and not read.is_secondary and read.template_length > 0:
            if read.template_length <= max_size:
                sizes.append(read.template_length)

    bam.close()

    # cfDNA signature: peak at ~167bp (mononucleosome)
    # Shorter fragments (90-150bp) enriched in ctDNA
    sizes = np.array(sizes)

    print(f'Fragments analyzed: {len(sizes)}')
    print(f'Median size: {np.median(sizes):.0f} bp')
    print(f'Mode: {np.bincount(sizes).argmax()} bp')

    return sizes
```

## Quality Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Modal fragment size | 150-180 bp | Peak ~167 bp indicates good cfDNA |
| UMI families >= 2 reads | > 50% | Sufficient for consensus |
| Mean base quality | >= 30 | After consensus |
| Mapping quality | >= 20 | Exclude multi-mappers |

## Related Skills

- fragment-analysis - Analyze fragmentomics after preprocessing
- tumor-fraction-estimation - Estimate ctDNA from sWGS
- ctdna-mutation-detection - Detect mutations from panel data
