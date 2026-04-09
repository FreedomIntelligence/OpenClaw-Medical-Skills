# bio-longread-alignment

> Align long reads using minimap2 for Oxford Nanopore and PacBio data. Supports various presets for different read types and applications. Use when aligning ONT or PacBio reads to a reference genome for variant calling, SV detection, or coverage analysis.

## Version Compatibility

Reference examples tested with: minimap2 2.26+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Long-Read Alignment with minimap2

**"Align my long reads to the reference"** → Map ONT or PacBio reads using minimap2 with technology-specific presets for optimal sensitivity and accuracy.
- CLI: `minimap2 -ax map-ont ref.fa reads.fq | samtools sort -o aligned.bam` (ONT), `minimap2 -ax map-hifi` (PacBio HiFi)

## Oxford Nanopore Alignment

```bash
# Basic ONT alignment
minimap2 -ax map-ont reference.fa reads.fastq.gz | \
    samtools sort -o aligned.bam
samtools index aligned.bam
```

## PacBio HiFi Alignment

```bash
# PacBio HiFi reads (high accuracy)
minimap2 -ax map-hifi reference.fa reads.fastq.gz | \
    samtools sort -o aligned.bam
samtools index aligned.bam
```

## PacBio CLR Alignment

```bash
# PacBio CLR (continuous long reads, lower accuracy)
minimap2 -ax map-pb reference.fa reads.fastq.gz | \
    samtools sort -o aligned.bam
samtools index aligned.bam
```

## Pre-Build Index for Multiple Runs

```bash
# Build index once
minimap2 -d reference.mmi reference.fa

# Use index for alignment
minimap2 -ax map-ont reference.mmi reads.fastq.gz | samtools sort -o aligned.bam
```

## Common Options

```bash
minimap2 -ax map-ont \
    -t 8 \                         # Threads
    -R '@RG\tID:sample\tSM:sample' \  # Read group
    --secondary=no \               # No secondary alignments
    --MD \                         # Generate MD tag for variants
    -Y \                           # Use soft clipping for supplementary
    reference.fa reads.fastq.gz | \
    samtools sort -@ 4 -o aligned.bam
```

## Splice-Aware Alignment (RNA)

```bash
# For direct RNA or cDNA sequencing
minimap2 -ax splice reference.fa reads.fastq.gz | \
    samtools sort -o aligned.bam
```

## With Junction BED (Known Splice Sites)

```bash
# Provide known splice junctions
minimap2 -ax splice --junc-bed junctions.bed \
    reference.fa reads.fastq.gz | samtools sort -o aligned.bam
```

## Assembly to Reference Alignment

```bash
# Assembly with ~0.1% divergence
minimap2 -ax asm5 reference.fa assembly.fa > aligned.sam

# Assembly with higher divergence (~5%)
minimap2 -ax asm20 reference.fa assembly.fa > aligned.sam
```

## Output PAF (Faster, No BAM)

```bash
# PAF format (faster, for quick analysis)
minimap2 -x map-ont reference.fa reads.fastq.gz > alignments.paf
```

## Keep Secondary and Supplementary

```bash
# Keep all alignments (for SV calling)
minimap2 -ax map-ont \
    --secondary=yes \
    -N 5 \                         # Max secondary alignments
    reference.fa reads.fastq.gz | samtools sort -o aligned.bam
```

## Filter Alignments

```bash
# During alignment pipeline
minimap2 -ax map-ont reference.fa reads.fastq.gz | \
    samtools view -b -q 10 | \     # Min mapping quality 10
    samtools sort -o aligned.bam
```

## Multiple FASTQ Files

```bash
# Concatenate inputs
minimap2 -ax map-ont reference.fa reads1.fastq.gz reads2.fastq.gz | \
    samtools sort -o aligned.bam

# Or use file list
cat file_list.txt | xargs minimap2 -ax map-ont reference.fa | \
    samtools sort -o aligned.bam
```

## Output Statistics

```bash
# Get alignment statistics
samtools flagstat aligned.bam

# Detailed stats
samtools stats aligned.bam | grep ^SN
```

## Convert PAF to BED

```bash
# Extract alignments to BED
awk 'OFS="\t" {print $6, $8, $9, $1, $12, ($5=="+")?"+":"-"}' alignments.paf > alignments.bed
```

## Key Presets

| Preset | Description | Best For |
|--------|-------------|----------|
| map-ont | ONT reads | Nanopore genomic |
| map-hifi | PacBio HiFi | PacBio genomic |
| map-pb | PacBio CLR | PacBio CLR |
| splice | Long RNA reads | cDNA, direct RNA |
| asm5 | Low divergence | Same species assembly |
| asm20 | High divergence | Cross-species assembly |
| sr | Short reads | Illumina (basic) |

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| -t | 3 | CPU threads |
| -k | 15 | K-mer size |
| -w | 10 | Minimizer window |
| -a | off | Output SAM |
| -x | none | Preset |
| --secondary | yes | Output secondary |
| -N | 5 | Max secondary alignments |
| --MD | off | Generate MD tag |
| -R | none | Read group header |
| -Y | off | Soft clipping for supplementary |

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| PAF | (default) | Pairwise Alignment Format |
| SAM | -a | Sequence Alignment Map |
| BAM | -a \| samtools | Binary SAM |

## Related Skills

- medaka-polishing - Polish consensus with medaka
- structural-variants - Call SVs from alignments
- alignment-files/sam-bam-basics - BAM manipulation
