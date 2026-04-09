# bio-pileup-generation

> Generate pileup data for variant calling using samtools mpileup and pysam. Use when preparing data for variant calling, analyzing per-position read data, or calculating allele frequencies.

**Available tools:** Read, Bash

# Pileup Generation

Generate pileup data for variant calling and position-level analysis.

## What is Pileup?

Pileup shows all reads covering each position in the reference, used for:
- Variant calling (with bcftools)
- Coverage analysis
- Allele frequency calculation
- SNP/indel detection

## samtools mpileup

### Basic Pileup
```bash
samtools mpileup -f reference.fa input.bam > pileup.txt
```

### Pileup for Variant Calling (Output BCF)
```bash
samtools mpileup -f reference.fa -g input.bam -o output.bcf
```

### Pileup Specific Region
```bash
samtools mpileup -f reference.fa -r chr1:1000000-2000000 input.bam
```

### Regions from BED
```bash
samtools mpileup -f reference.fa -l targets.bed input.bam
```

### Multiple BAM Files
```bash
samtools mpileup -f reference.fa sample1.bam sample2.bam sample3.bam > pileup.txt
```

## Output Format

Text pileup format (6 columns per sample):
```
chr1    1000    A    15    ...............    FFFFFFFFFFF
chr1    1001    T    12    ............      FFFFFFFFFFFF
```

| Column | Description |
|--------|-------------|
| 1 | Chromosome |
| 2 | Position (1-based) |
| 3 | Reference base |
| 4 | Read depth |
| 5 | Read bases |
| 6 | Base qualities |

### Read Bases Encoding

| Symbol | Meaning |
|--------|---------|
| `.` | Match on forward strand |
| `,` | Match on reverse strand |
| `ACGT` | Mismatch (uppercase = forward) |
| `acgt` | Mismatch (lowercase = reverse) |
| `^Q` | Start of read (Q = MAPQ as ASCII) |
| `$` | End of read |
| `+NNN` | Insertion of N bases |
| `-NNN` | Deletion of N bases |
| `*` | Deleted base |
| `>` / `<` | Reference skip (intron) |

## Quality Filtering Options

### Minimum Mapping Quality
```bash
samtools mpileup -f reference.fa -q 20 input.bam
```

### Minimum Base Quality
```bash
samtools mpileup -f reference.fa -Q 20 input.bam
```

### Combined Quality Filters
```bash
samtools mpileup -f reference.fa -q 20 -Q 20 input.bam
```

### Maximum Depth
```bash
# Prevent memory issues with high coverage
samtools mpileup -f reference.fa -d 1000 input.bam
```

## Variant Calling Pipeline

### mpileup to bcftools call
```bash
samtools mpileup -f reference.fa input.bam | bcftools call -mv -o variants.vcf
```

### Direct BCF Output
```bash
samtools mpileup -f reference.fa -g -o output.bcf input.bam
bcftools call -mv output.bcf -o variants.vcf
```

### Full Pipeline
```bash
samtools mpileup -f reference.fa -q 20 -Q 20 input.bam | \
    bcftools call -mv -Oz -o variants.vcf.gz
bcftools index variants.vcf.gz
```

## pysam Python Alternative

### Basic Pileup
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1001000):
        print(f'{pileup_column.reference_name}:{pileup_column.pos} depth={pileup_column.n}')
```

### Access Reads at Position
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1000001, truncate=True):
        print(f'Position: {pileup_column.pos}')
        print(f'Depth: {pileup_column.n}')

        for pileup_read in pileup_column.pileups:
            if pileup_read.is_del:
                print('  Deletion')
            elif pileup_read.is_refskip:
                print('  Reference skip')
            else:
                qpos = pileup_read.query_position
                base = pileup_read.alignment.query_sequence[qpos]
                qual = pileup_read.alignment.query_qualities[qpos]
                print(f'  {base} (Q{qual})')
```

### Count Alleles at Position
```python
import pysam
from collections import Counter

def allele_counts(bam_path, chrom, pos):
    counts = Counter()

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup_column in bam.pileup(chrom, pos, pos + 1, truncate=True):
            if pileup_column.pos != pos:
                continue

            for pileup_read in pileup_column.pileups:
                if pileup_read.is_del:
                    counts['DEL'] += 1
                elif pileup_read.is_refskip:
                    continue
                else:
                    qpos = pileup_read.query_position
                    base = pileup_read.alignment.query_sequence[qpos]
                    counts[base.upper()] += 1

    return dict(counts)

counts = allele_counts('input.bam', 'chr1', 1000000)
print(counts)  # {'A': 45, 'G': 5}
```

### Calculate Allele Frequency
```python
import pysam
from collections import Counter

def allele_frequency(bam_path, chrom, pos, min_qual=20):
    counts = Counter()

    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        for pileup_column in bam.pileup(chrom, pos, pos + 1, truncate=True,
                                         min_base_quality=min_qual):
            if pileup_column.pos != pos:
                continue

            for pileup_read in pileup_column.pileups:
                if pileup_read.is_del or pileup_read.is_refskip:
                    continue
                qpos = pileup_read.query_position
                base = pileup_read.alignment.query_sequence[qpos]
                counts[base.upper()] += 1

    total = sum(counts.values())
    if total == 0:
        return {}

    return {base: count / total for base, count in counts.items()}

freq = allele_frequency('input.bam', 'chr1', 1000000)
for base, f in sorted(freq.items(), key=lambda x: -x[1]):
    print(f'{base}: {f:.1%}')
```

### Pileup with Quality Filtering
```python
import pysam

with pysam.AlignmentFile('input.bam', 'rb') as bam:
    for pileup_column in bam.pileup('chr1', 1000000, 1001000,
                                     truncate=True,
                                     min_mapping_quality=20,
                                     min_base_quality=20):
        print(f'{pileup_column.pos}: {pileup_column.n}')
```

### Generate Pileup Text
```python
import pysam

def pileup_text(bam_path, ref_path, chrom, start, end):
    with pysam.AlignmentFile(bam_path, 'rb') as bam:
        with pysam.FastaFile(ref_path) as ref:
            for pileup_column in bam.pileup(chrom, start, end, truncate=True):
                pos = pileup_column.pos
                ref_base = ref.fetch(chrom, pos, pos + 1)
                depth = pileup_column.n

                bases = []
                for pileup_read in pileup_column.pileups:
                    if pileup_read.is_del:
                        bases.append('*')
                    elif pileup_read.is_refskip:
                        bases.append('>')
                    else:
                        qpos = pileup_read.query_position
                        base = pileup_read.alignment.query_sequence[qpos]
                        if base.upper() == ref_base.upper():
                            bases.append('.' if not pileup_read.alignment.is_reverse else ',')
                        else:
                            bases.append(base.upper() if not pileup_read.alignment.is_reverse else base.lower())

                print(f'{chrom}\t{pos+1}\t{ref_base}\t{depth}\t{"".join(bases)}')

pileup_text('input.bam', 'reference.fa', 'chr1', 1000000, 1000100)
```

## Pileup Options Summary

| Option | Description |
|--------|-------------|
| `-f FILE` | Reference FASTA (required) |
| `-r REGION` | Restrict to region |
| `-l FILE` | BED file of regions |
| `-q INT` | Min mapping quality |
| `-Q INT` | Min base quality |
| `-d INT` | Max depth (default 8000) |
| `-g` | Output BCF format |
| `-u` | Uncompressed BCF output |

## Quick Reference

| Task | Command |
|------|---------|
| Basic pileup | `samtools mpileup -f ref.fa in.bam` |
| Quality filter | `samtools mpileup -f ref.fa -q 20 -Q 20 in.bam` |
| Region | `samtools mpileup -f ref.fa -r chr1:1-1000 in.bam` |
| BCF output | `samtools mpileup -f ref.fa -g in.bam -o out.bcf` |
| To bcftools | `samtools mpileup -f ref.fa in.bam \| bcftools call -mv` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No FASTA reference` | Missing -f option | Add `-f reference.fa` |
| `Reference mismatch` | Wrong reference | Use same reference as alignment |
| Out of memory | High coverage region | Use `-d` to cap depth |

## Related Skills

- alignment-filtering - Filter BAM before pileup
- reference-operations - Index reference for pileup
- bam-statistics - depth command for coverage
- variant-calling - bcftools call from pileup
