# bio-hi-c-analysis-contact-pairs

> Process Hi-C read pairs using pairtools. Parse alignments, filter duplicates, classify pairs, and generate contact statistics from Hi-C sequencing data. Use when processing raw Hi-C read pairs.

## Version Compatibility

Reference examples tested with: cooler 0.9+, pairtools 1.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Hi-C Contact Pairs Processing

**"Process my Hi-C read pairs"** → Parse aligned Hi-C reads into contact pairs, filter duplicates, classify pair types (cis/trans), and generate contact statistics.
- CLI: `pairtools parse` → `pairtools sort` → `pairtools dedup` → `pairtools stats`

Process Hi-C read pairs with pairtools.

## Pairtools Workflow Overview

```
BAM (aligned reads)
    |
    v
pairtools parse (extract pairs)
    |
    v
pairtools sort
    |
    v
pairtools dedup (remove duplicates)
    |
    v
pairtools select (filter by type)
    |
    v
Valid pairs for matrix generation
```

## Parse Alignments to Pairs

```bash
# Parse BAM to pairs format
pairtools parse \
    --chroms-path chromsizes.txt \
    --min-mapq 30 \
    --walks-policy 5unique \
    --output parsed.pairs.gz \
    aligned.bam

# With restriction enzyme cut sites
pairtools parse \
    --chroms-path chromsizes.txt \
    --min-mapq 30 \
    --walks-policy 5unique \
    --add-columns mapq \
    aligned.bam | \
pairtools restrict -f enzyme_sites.bed | \
gzip > parsed.restricted.pairs.gz
```

## Sort Pairs

```bash
# Sort pairs by position
pairtools sort \
    --nproc 8 \
    --output sorted.pairs.gz \
    parsed.pairs.gz
```

## Remove Duplicates

```bash
# Mark and remove PCR duplicates
pairtools dedup \
    --max-mismatch 1 \
    --mark-dups \
    --output deduped.pairs.gz \
    --output-stats dedup_stats.txt \
    sorted.pairs.gz

# Without outputting dups
pairtools dedup \
    --max-mismatch 1 \
    --output deduped.pairs.gz \
    sorted.pairs.gz
```

## View Pairs File

```bash
# View header
pairtools header deduped.pairs.gz

# View first few pairs
zcat deduped.pairs.gz | head -100

# Pairs format: readID chrom1 pos1 chrom2 pos2 strand1 strand2 pair_type
```

## Filter by Pair Type

```bash
# Select only valid pairs (UU = unique-unique mapping)
pairtools select '(pair_type == "UU")' \
    --output valid_pairs.pairs.gz \
    deduped.pairs.gz

# Multiple types
pairtools select '(pair_type == "UU") or (pair_type == "RU") or (pair_type == "UR")' \
    --output all_valid.pairs.gz \
    deduped.pairs.gz
```

## Filter by Distance

```bash
# Remove self-ligations (very short range)
pairtools select '(chrom1 != chrom2) or (abs(pos1 - pos2) > 1000)' \
    --output filtered.pairs.gz \
    deduped.pairs.gz
```

## Filter by MAPQ

```bash
# If MAPQ column was added during parsing
pairtools select '(mapq1 >= 30) and (mapq2 >= 30)' \
    --output hq_pairs.pairs.gz \
    deduped.pairs.gz
```

## Generate Statistics

```bash
# Get pair statistics
pairtools stats \
    --output stats.txt \
    deduped.pairs.gz

# View stats
cat stats.txt
```

## Split by Pair Type

```bash
# Split into different files by pair type
pairtools split \
    --output-pairs valid.pairs.gz \
    --output-sam unmapped.sam \
    parsed.pairs.gz
```

## Merge Pairs Files

```bash
# Merge multiple pairs files
pairtools merge \
    --output merged.pairs.gz \
    sample1.pairs.gz sample2.pairs.gz sample3.pairs.gz

# Then dedup the merged file
pairtools sort merged.pairs.gz | pairtools dedup > merged_dedup.pairs.gz
```

## Generate Fragment Pairs (Restriction Sites)

```bash
# Create restriction site fragments
# First generate sites with cooler
cooler digest hg38.fa HindIII > hindiii_sites.bed

# Then use pairtools restrict
pairtools restrict -f hindiii_sites.bed \
    --output restricted.pairs.gz \
    parsed.pairs.gz
```

## Convert to Different Formats

```bash
# Pairs to 2D positions (for visualization)
zcat valid.pairs.gz | awk 'BEGIN{OFS="\t"} !/^#/ {print $2,$3,$4,$5}' > contacts_2d.txt

# Pairs to BEDPE
zcat valid.pairs.gz | awk 'BEGIN{OFS="\t"} !/^#/ {print $2,$3,$3+1,$4,$5,$5+1,$1,1,$6,$7}' > contacts.bedpe
```

## Create Cooler from Pairs

```bash
# Aggregate pairs into cooler matrix
cooler cload pairs \
    -c1 2 -p1 3 -c2 4 -p2 5 \
    chromsizes.txt:10000 \
    valid.pairs.gz \
    matrix.cool
```

## Python: Parse Pairs File

```python
import pandas as pd

# Read pairs file (skip header)
with open('valid.pairs.gz', 'rt') as f:
    header_lines = 0
    for line in f:
        if line.startswith('#'):
            header_lines += 1
        else:
            break

pairs = pd.read_csv(
    'valid.pairs.gz',
    sep='\t',
    skiprows=header_lines,
    names=['readID', 'chrom1', 'pos1', 'chrom2', 'pos2', 'strand1', 'strand2', 'pair_type']
)

print(f'Total pairs: {len(pairs):,}')
print(f'\nPair types:')
print(pairs['pair_type'].value_counts())
```

## Full Processing Pipeline

**Goal:** Process raw Hi-C alignments into a balanced contact matrix ready for downstream analysis (TADs, loops, compartments).

**Approach:** Chain pairtools operations (parse, restrict, sort, dedup, select) into a single pipeline, then aggregate valid pairs into a cooler matrix file.

```bash
#!/bin/bash
SAMPLE=$1
CHROMSIZES=chromsizes.txt
ENZYME_SITES=hindiii_sites.bed

# Parse
pairtools parse \
    --chroms-path $CHROMSIZES \
    --min-mapq 30 \
    --walks-policy 5unique \
    ${SAMPLE}.bam | \
pairtools restrict -f $ENZYME_SITES | \
pairtools sort --nproc 8 | \
pairtools dedup \
    --max-mismatch 1 \
    --output-stats ${SAMPLE}.dedup_stats.txt | \
pairtools select '(pair_type == "UU")' \
    --output ${SAMPLE}.valid.pairs.gz

# Generate matrix
cooler cload pairs \
    -c1 2 -p1 3 -c2 4 -p2 5 \
    ${CHROMSIZES}:10000 \
    ${SAMPLE}.valid.pairs.gz \
    ${SAMPLE}.cool

# Stats
pairtools stats ${SAMPLE}.valid.pairs.gz > ${SAMPLE}.stats.txt

echo "Done processing $SAMPLE"
```

## Related Skills

- hic-data-io - Work with cooler matrices
- matrix-operations - Balance resulting matrices
- read-alignment - Align Hi-C reads before processing
