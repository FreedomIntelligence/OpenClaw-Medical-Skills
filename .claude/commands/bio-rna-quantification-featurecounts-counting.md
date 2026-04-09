# bio-rna-quantification-featurecounts-counting

> Count reads per gene from aligned BAM files using Subread featureCounts. Use when processing BAM files from STAR/HISAT2 to generate gene-level counts for DESeq2/edgeR.

**Available tools:** Read, Bash

# featureCounts Counting

Count reads mapping to genomic features (genes, exons) from BAM files.

## Basic Usage

```bash
# Single sample
featureCounts -a annotation.gtf -o counts.txt aligned.bam

# Multiple samples (recommended - single matrix output)
featureCounts -a annotation.gtf -o counts.txt sample1.bam sample2.bam sample3.bam

# All BAMs in directory
featureCounts -a annotation.gtf -o counts.txt *.bam
```

## Paired-End Data

```bash
# Count fragments, not reads (required for paired-end)
featureCounts -p --countReadPairs -a annotation.gtf -o counts.txt *.bam

# Check proper pairs only
featureCounts -p --countReadPairs -B -C -a annotation.gtf -o counts.txt *.bam
```

**Flags:**
- `-p` - Input is paired-end
- `--countReadPairs` - Count fragments instead of reads
- `-B` - Only count properly paired reads
- `-C` - Don't count chimeric fragments

## Strand-Specific Libraries

```bash
# Unstranded (default)
featureCounts -s 0 -a annotation.gtf -o counts.txt *.bam

# Forward stranded (e.g., dUTP, NSR)
featureCounts -s 1 -a annotation.gtf -o counts.txt *.bam

# Reverse stranded (e.g., Illumina TruSeq, most common)
featureCounts -s 2 -a annotation.gtf -o counts.txt *.bam
```

**Determining strandedness:** Use `infer_experiment.py` from RSeQC or check library prep protocol.

## Feature Types

```bash
# Count at gene level (default)
featureCounts -t exon -g gene_id -a annotation.gtf -o counts.txt *.bam

# Count at transcript level
featureCounts -t exon -g transcript_id -a annotation.gtf -o counts.txt *.bam

# Count CDS only
featureCounts -t CDS -g gene_id -a annotation.gtf -o counts.txt *.bam
```

**Flags:**
- `-t` - Feature type in GTF (default: exon)
- `-g` - Meta-feature attribute (default: gene_id)

## Multi-Mapping Reads

```bash
# Discard multi-mappers (default, recommended for DE)
featureCounts -a annotation.gtf -o counts.txt *.bam

# Count multi-mappers (fractional)
featureCounts -M --fraction -a annotation.gtf -o counts.txt *.bam

# Count multi-mappers (full count to each location)
featureCounts -M -a annotation.gtf -o counts.txt *.bam
```

## Overlapping Features

```bash
# Discard reads overlapping multiple features (default)
featureCounts -a annotation.gtf -o counts.txt *.bam

# Count reads overlapping multiple features
featureCounts -O -a annotation.gtf -o counts.txt *.bam

# Fractional count for overlaps
featureCounts -O --fraction -a annotation.gtf -o counts.txt *.bam
```

## Performance Options

```bash
# Use multiple threads
featureCounts -T 8 -a annotation.gtf -o counts.txt *.bam

# Use less memory (slower)
featureCounts --largeBAM -a annotation.gtf -o counts.txt *.bam
```

## Output Files

featureCounts produces two files:

1. **counts.txt** - Main count matrix
```
Geneid  Chr     Start   End     Strand  Length  sample1.bam  sample2.bam
GENE1   chr1    100     500     +       400     1523         1891
GENE2   chr1    1000    2000    -       1000    892          756
```

2. **counts.txt.summary** - Assignment statistics
```
Status                  sample1.bam  sample2.bam
Assigned                1523456      1678234
Unassigned_Unmapped     12345        11234
Unassigned_NoFeatures   234567       245678
```

## Extract Count Matrix

```bash
# Remove first 6 columns (metadata) to get just counts
cut -f1,7- counts.txt | tail -n +2 > count_matrix.txt
```

## Python Processing

```python
import pandas as pd

counts = pd.read_csv('counts.txt', sep='\t', comment='#')
count_matrix = counts.set_index('Geneid').iloc[:, 5:]  # Skip metadata columns
count_matrix.columns = [c.replace('.bam', '') for c in count_matrix.columns]
count_matrix.to_csv('count_matrix.csv')
```

## R Processing

```r
counts <- read.table('counts.txt', header=TRUE, row.names=1, skip=1)
count_matrix <- counts[, 6:ncol(counts)]  # Skip metadata columns
colnames(count_matrix) <- gsub('.bam', '', colnames(count_matrix))
```

## Common Issues

**Low assignment rate:**
- Check strandedness setting (`-s`)
- Verify GTF matches reference genome version
- Check BAM alignment quality

**Zero counts for known expressed genes:**
- Ensure feature type matches GTF (`-t exon` vs `-t gene`)
- Check gene_id attribute name in GTF

## Related Skills

- alignment-files/sam-bam-basics - Input BAM file handling
- genome-intervals/gtf-gff-handling - GTF annotation files
- differential-expression/deseq2-basics - Downstream analysis with counts
- rna-quantification/count-matrix-qc - QC of count data
