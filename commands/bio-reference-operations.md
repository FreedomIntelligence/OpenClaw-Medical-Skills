# bio-reference-operations

> Generate consensus sequences and manage reference files using samtools. Use when creating consensus from alignments, indexing references, or creating sequence dictionaries.

**Available tools:** Read, Bash

# Reference Operations

Generate consensus sequences and manage reference files using samtools.

## samtools faidx - Index Reference FASTA

Create index for random access to reference sequences.

### Create Index
```bash
samtools faidx reference.fa
# Creates reference.fa.fai
```

### Fetch Region from Reference
```bash
samtools faidx reference.fa chr1:1000-2000
```

### Fetch Multiple Regions
```bash
samtools faidx reference.fa chr1:1000-2000 chr2:3000-4000
```

### Fetch Entire Chromosome
```bash
samtools faidx reference.fa chr1
```

### Output to File
```bash
samtools faidx reference.fa chr1:1000-2000 > region.fa
```

### Reverse Complement
```bash
samtools faidx -i reference.fa chr1:1000-2000
```

### FAI File Format
```
chr1    248956422    6    60    61
chr2    242193529    253404903    60    61
```
Columns: name, length, offset, line bases, line width

## samtools dict - Create Sequence Dictionary

Create SAM header dictionary for reference (used by GATK, Picard).

### Create Dictionary
```bash
samtools dict reference.fa -o reference.dict
```

### With Assembly Info
```bash
samtools dict -a GRCh38 -s "Homo sapiens" reference.fa -o reference.dict
```

### Dictionary Format
```
@HD VN:1.6 SO:unsorted
@SQ SN:chr1 LN:248956422 M5:6aef897c3d6ff0c78aff06ac189178dd UR:file:reference.fa
@SQ SN:chr2 LN:242193529 M5:f98db672eb0993dcfdabafe2a882905c UR:file:reference.fa
```

## samtools consensus - Generate Consensus

Create consensus sequence from alignments.

### Basic Consensus
```bash
samtools consensus input.bam -o consensus.fa
```

### From Specific Region
```bash
samtools consensus -r chr1:1000-2000 input.bam -o region_consensus.fa
```

### Output Formats
```bash
# FASTA (default)
samtools consensus -f fasta input.bam -o consensus.fa

# FASTQ (includes quality)
samtools consensus -f fastq input.bam -o consensus.fq
```

### Quality Options
```bash
# Minimum depth to call base
samtools consensus -d 5 input.bam -o consensus.fa

# Call all positions (including low coverage)
samtools consensus -a input.bam -o consensus.fa
```

### Ambiguity Handling
```bash
# Use IUPAC codes for heterozygous positions
samtools consensus --show-ins no --show-del no input.bam -o consensus.fa
```

## pysam Python Alternative

### Fetch from Indexed FASTA
```python
import pysam

with pysam.FastaFile('reference.fa') as ref:
    seq = ref.fetch('chr1', 999, 2000)  # 0-based
    print(seq)
```

### Get Reference Lengths
```python
with pysam.FastaFile('reference.fa') as ref:
    for name in ref.references:
        length = ref.get_reference_length(name)
        print(f'{name}: {length:,} bp')
```

### Fetch All Chromosomes
```python
with pysam.FastaFile('reference.fa') as ref:
    for chrom in ref.references:
        seq = ref.fetch(chrom)
        print(f'>{chrom}')
        print(seq[:100] + '...')
```

### Generate Simple Consensus
```python
import pysam
from collections import Counter

def consensus_at_position(bam, chrom, pos):
    bases = Counter()
    for pileup in bam.pileup(chrom, pos, pos + 1, truncate=True):
        if pileup.pos == pos:
            for read in pileup.pileups:
                if not read.is_del and not read.is_refskip:
                    bases[read.alignment.query_sequence[read.query_position]] += 1
    if bases:
        return bases.most_common(1)[0][0]
    return 'N'

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    consensus = consensus_at_position(bam, 'chr1', 1000000)
    print(f'Consensus at chr1:1000000 = {consensus}')
```

### Build Consensus Sequence
```python
import pysam
from collections import Counter

def build_consensus(bam_path, chrom, start, end, min_depth=3):
    consensus = []

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup in bam.pileup(chrom, start, end, truncate=True):
            bases = Counter()
            for read in pileup.pileups:
                if not read.is_del and not read.is_refskip:
                    base = read.alignment.query_sequence[read.query_position]
                    bases[base] += 1

            if sum(bases.values()) >= min_depth:
                consensus.append(bases.most_common(1)[0][0])
            else:
                consensus.append('N')

    return ''.join(consensus)

seq = build_consensus('input.bam', 'chr1', 1000, 2000, min_depth=5)
print(f'>{chrom}:{start}-{end}')
print(seq)
```

### Create Dictionary Header
```python
import pysam

def create_dict_header(fasta_path):
    header = {'HD': {'VN': '1.6', 'SO': 'unsorted'}, 'SQ': []}

    with pysam.FastaFile(fasta_path) as ref:
        for name in ref.references:
            length = ref.get_reference_length(name)
            header['SQ'].append({'SN': name, 'LN': length})

    return header

header = create_dict_header('reference.fa')
for sq in header['SQ'][:5]:
    print(f'{sq["SN"]}: {sq["LN"]:,} bp')
```

## Reference Preparation Workflow

### Prepare Reference for Analysis
```bash
# 1. Index FASTA for samtools/pysam
samtools faidx reference.fa

# 2. Create sequence dictionary for GATK/Picard
samtools dict reference.fa -o reference.dict

# 3. Index for BWA
bwa index reference.fa

# 4. Index for Bowtie2
bowtie2-build reference.fa reference
```

### Check Reference Setup
```bash
# Verify FAI exists
ls -la reference.fa.fai

# Verify dict exists
head reference.dict

# Test fetch
samtools faidx reference.fa chr1:1-100
```

## Common Operations

### Extract Chromosome
```bash
samtools faidx reference.fa chr1 > chr1.fa
samtools faidx chr1.fa  # Index the subset
```

### Get Chromosome Sizes
```bash
cut -f1,2 reference.fa.fai > chrom.sizes
```

### Subset Reference
```bash
samtools faidx reference.fa chr1 chr2 chr3 > subset.fa
samtools faidx subset.fa
```

### Compare Consensus to Reference
```bash
# Generate consensus
samtools consensus input.bam -o consensus.fa

# Align consensus back to reference
minimap2 -a reference.fa consensus.fa > comparison.sam
```

## Quick Reference

| Task | Command |
|------|---------|
| Index FASTA | `samtools faidx ref.fa` |
| Fetch region | `samtools faidx ref.fa chr1:1-1000` |
| Create dict | `samtools dict ref.fa -o ref.dict` |
| Build consensus | `samtools consensus in.bam -o out.fa` |
| Chrom sizes | `cut -f1,2 ref.fa.fai` |

## Related Skills

- sam-bam-basics - Reference required for CRAM
- alignment-indexing - faidx for reference access
- pileup-generation - Pileup for consensus building
- variant-calling - bcftools consensus from VCF
- sequence-io/read-sequences - Parse FASTA with Biopython
