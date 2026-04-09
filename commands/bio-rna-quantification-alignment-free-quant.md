# bio-rna-quantification-alignment-free-quant

> Quantify transcript expression using pseudo-alignment with Salmon or kallisto. Use when quantifying transcripts with Salmon or kallisto.

**Available tools:** Read, Bash

# Alignment-Free Quantification

Quantify transcript abundance directly from FASTQ reads using pseudo-alignment (kallisto) or selective alignment (Salmon).

## Salmon Workflow

### Build Index

```bash
# Download transcriptome FASTA
# Ensembl: Homo_sapiens.GRCh38.cdna.all.fa.gz

# Basic index (fast, less accurate)
salmon index -t transcripts.fa -i salmon_index

# Decoy-aware index (recommended for accuracy)
# First, create decoys from genome
grep "^>" genome.fa | cut -d " " -f 1 | sed 's/>//g' > decoys.txt
cat transcripts.fa genome.fa > gentrome.fa
salmon index -t gentrome.fa -d decoys.txt -i salmon_index -p 8
```

### Quantify Samples

```bash
# Paired-end reads
salmon quant -i salmon_index -l A \
    -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
    -o sample_quant -p 8

# Single-end reads
salmon quant -i salmon_index -l A \
    -r sample.fastq.gz \
    -o sample_quant -p 8
```

**Key flags:**
- `-l A` - Automatically detect library type
- `-p` - Number of threads
- `--validateMappings` - More accurate (default in recent versions)
- `--gcBias` - Correct for GC bias
- `--seqBias` - Correct for sequence-specific bias

### Library Types

| Code | Description |
|------|-------------|
| `A` | Automatic detection (recommended) |
| `ISR` | Inward, stranded, read 1 from reverse |
| `ISF` | Inward, stranded, read 1 from forward |
| `IU` | Inward, unstranded |

### Batch Processing

```bash
for sample in sample1 sample2 sample3; do
    salmon quant -i salmon_index -l A \
        -1 ${sample}_R1.fastq.gz -2 ${sample}_R2.fastq.gz \
        -o ${sample}_quant -p 8
done
```

### Output Files

```
sample_quant/
├── quant.sf           # Main quantification file
├── aux_info/          # Auxiliary information
├── cmd_info.json      # Command used
├── lib_format_counts.json  # Library format detection
└── logs/              # Log files
```

**quant.sf format:**
```
Name                    Length  EffectiveLength TPM         NumReads
ENST00000456328.2       1657    1477.000        0.000000    0.000
ENST00000450305.2       632     452.000         12.345678   156.789
```

## kallisto Workflow

### Build Index

```bash
kallisto index -i kallisto_index transcripts.fa
```

### Quantify Samples

```bash
# Paired-end
kallisto quant -i kallisto_index -o sample_quant \
    sample_R1.fastq.gz sample_R2.fastq.gz

# Single-end (must specify fragment length)
kallisto quant -i kallisto_index -o sample_quant \
    --single -l 200 -s 20 sample.fastq.gz

# With bootstraps (for sleuth)
kallisto quant -i kallisto_index -o sample_quant -b 100 \
    sample_R1.fastq.gz sample_R2.fastq.gz
```

**Key flags:**
- `-b` - Number of bootstrap samples
- `-t` - Number of threads
- `--single` - Single-end mode
- `-l` - Estimated fragment length (single-end)
- `-s` - Fragment length standard deviation

### Output Files

```
sample_quant/
├── abundance.tsv      # Main quantification (text)
├── abundance.h5       # HDF5 format (for sleuth)
└── run_info.json      # Run information
```

**abundance.tsv format:**
```
target_id               length  eff_length  est_counts  tpm
ENST00000456328.2       1657    1477.00     0.00        0.000000
ENST00000450305.2       632     452.00      156.79      12.345678
```

## Salmon vs kallisto

| Feature | Salmon | kallisto |
|---------|--------|----------|
| Speed | Fast | Fastest |
| Accuracy | Higher | Good |
| GC bias correction | Yes | No |
| Decoy sequences | Yes | No |
| Memory usage | Moderate | Low |

**Recommendation:** Use Salmon for production, kallisto for quick exploratory analysis.

## Combining Results

```bash
# Salmon: use tximport in R
# kallisto: use tximport or sleuth

# Quick Python combination
python << 'EOF'
import pandas as pd
from pathlib import Path

samples = ['sample1', 'sample2', 'sample3']
tpm_data = {}
counts_data = {}

for sample in samples:
    quant_file = Path(f'{sample}_quant/quant.sf')  # Salmon
    # quant_file = Path(f'{sample}_quant/abundance.tsv')  # kallisto
    df = pd.read_csv(quant_file, sep='\t', index_col=0)
    tpm_data[sample] = df['TPM']
    counts_data[sample] = df['NumReads']  # or est_counts for kallisto

tpm_matrix = pd.DataFrame(tpm_data)
counts_matrix = pd.DataFrame(counts_data)
tpm_matrix.to_csv('tpm_matrix.csv')
counts_matrix.to_csv('counts_matrix.csv')
EOF
```

## Quality Checks

```bash
# Check mapping rate from Salmon logs
grep "Mapping rate" sample_quant/logs/salmon_quant.log

# Check library type detection
cat sample_quant/lib_format_counts.json
```

**Good metrics:**
- Mapping rate > 70%
- Consistent library type across samples

## Common Issues

**Low mapping rate:**
- Wrong transcriptome version
- Contamination in samples
- Wrong library type

**Inconsistent library types:**
- Mixed library preparations
- Sample swap

## Related Skills

- read-qc/fastp-workflow - Upstream preprocessing
- rna-quantification/tximport-workflow - Import results to R
- rna-quantification/count-matrix-qc - QC of quantification
- differential-expression/deseq2-basics - Downstream analysis
