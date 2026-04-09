# bio-chipseq-motif-analysis

> De novo motif discovery and known motif enrichment analysis using HOMER and MEME-ChIP. Identify transcription factor binding motifs in ChIP-seq, ATAC-seq, or other genomic peak data. Use when finding enriched DNA motifs in peak sequences.

## Version Compatibility

Reference examples tested with: BioPython 1.83+, bedtools 2.31+, matplotlib 3.8+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Motif Analysis

**"Find enriched motifs in my ChIP-seq peaks"** → Discover de novo DNA-binding motifs and test for known TF motif enrichment in peak sequences.
- CLI: `findMotifsGenome.pl peaks.bed hg38 output/` (HOMER), `meme-chip -db JASPAR peaks.fa` (MEME)

Identify DNA sequence motifs enriched in ChIP-seq or ATAC-seq peaks to discover transcription factor binding sites.

## Tool Comparison

| Tool | Strengths | Use Case |
|------|-----------|----------|
| HOMER | Fast, comprehensive, built-in databases | General motif analysis |
| MEME-ChIP | Multiple algorithms, web interface | Publication-quality |
| MEME | De novo discovery only | Simple discovery |
| FIMO | Known motif scanning | Genome-wide scanning |

## HOMER

### Installation

```bash
conda install -c bioconda homer

# Configure genome (required once)
perl /path/to/homer/configureHomer.pl -install hg38
perl /path/to/homer/configureHomer.pl -install mm10
```

### De Novo Motif Discovery

**Goal:** Discover enriched DNA-binding motifs directly from ChIP-seq peak sequences.

**Approach:** Run findMotifsGenome.pl on a peak BED file with a specified fragment size, optionally providing background regions and target motif lengths.

```bash
# Basic motif finding
findMotifsGenome.pl peaks.bed hg38 output_dir/ -size 200

# With background regions
findMotifsGenome.pl peaks.bed hg38 output_dir/ -size 200 -bg background.bed

# Specify motif lengths to search
findMotifsGenome.pl peaks.bed hg38 output_dir/ -size 200 -len 8,10,12
```

### Key Options

| Option | Description |
|--------|-------------|
| `-size <#>` | Fragment size for analysis (default 200) |
| `-size given` | Use actual peak sizes |
| `-bg <file>` | Background regions (BED) |
| `-len <#,#,...>` | Motif lengths to search |
| `-mask` | Mask repeats |
| `-p <#>` | Number of CPUs |
| `-S <#>` | Number of motifs to find (default 25) |
| `-mis <#>` | Mismatches allowed (default 2) |
| `-noweight` | Don't adjust for GC content |

### Output Files

```
output_dir/
├── homerResults.html      # Main results page
├── knownResults.html      # Known motif enrichment
├── homerMotifs.all.motifs # All discovered motifs
├── knownResults.txt       # Known motif statistics
└── motif1.motif           # Individual motif files
```

### Known Motif Enrichment Only

```bash
# Skip de novo, only check known motifs
findMotifsGenome.pl peaks.bed hg38 output_dir/ -size 200 -nomotif
```

### Scan for Specific Motifs

```bash
# Find instances of motif in peaks
annotatePeaks.pl peaks.bed hg38 -m motif.motif > annotated.txt

# Scan genome for motif occurrences
scanMotifGenomeWide.pl motif.motif hg38 > motif_sites.bed
```

### Motif Comparison

```bash
# Compare discovered motifs to known database
compareMotifs.pl motifs.motif output_dir/ -known
```

### Create Custom Motif

```bash
# From consensus sequence
seq2profile.pl CACGTG 4 > MYC.motif

# From aligned sequences
cat aligned_seqs.txt | alignAndConvert.pl - > custom.motif
```

## MEME Suite

### Installation

```bash
conda install -c bioconda meme
```

### Extract Sequences from Peaks

```bash
# Get FASTA sequences under peaks
bedtools getfasta -fi genome.fa -bed peaks.bed -fo peaks.fa

# Center peaks and resize
bedtools slop -i peaks.bed -g genome.sizes -b 100 | \
    bedtools getfasta -fi genome.fa -bed - -fo peaks_centered.fa
```

### MEME (De Novo Discovery)

```bash
# Basic de novo discovery
meme peaks.fa -dna -oc meme_output -mod zoops -nmotifs 10 -minw 6 -maxw 20

# With Markov background
fasta-get-markov peaks.fa > background.model
meme peaks.fa -dna -oc meme_output -bfile background.model -mod zoops -nmotifs 10
```

### MEME Options

| Option | Description |
|--------|-------------|
| `-mod zoops` | Zero or one per sequence (default for ChIP) |
| `-mod oops` | Exactly one per sequence |
| `-mod anr` | Any number of repeats |
| `-nmotifs <#>` | Number of motifs to find |
| `-minw <#>` | Minimum motif width |
| `-maxw <#>` | Maximum motif width |
| `-revcomp` | Search both strands |
| `-bfile <file>` | Background model file |

### MEME-ChIP (Comprehensive Pipeline)

**Goal:** Run a comprehensive motif analysis pipeline combining de novo discovery, central enrichment testing, and database comparison.

**Approach:** Provide peak FASTA sequences and a motif database to MEME-ChIP, which runs MEME, DREME, CentriMo, TOMTOM, and FIMO in a single invocation.

```bash
# All-in-one ChIP-seq motif analysis
meme-chip -oc meme_chip_output -db motif_database.meme peaks.fa
```

MEME-ChIP runs:
1. MEME - De novo discovery (central enrichment)
2. DREME - Short motif discovery
3. CentriMo - Central enrichment analysis
4. TOMTOM - Compare to known motifs
5. FIMO - Find motif instances

### DREME (Short Motifs)

```bash
# Find short enriched motifs
dreme -oc dreme_output -p peaks.fa -n background.fa
```

### CentriMo (Central Enrichment)

```bash
# Test for central enrichment of known motifs
centrimo -oc centrimo_output peaks.fa motif_database.meme
```

### TOMTOM (Motif Comparison)

```bash
# Compare discovered motifs to database
tomtom -oc tomtom_output discovered.meme database.meme
```

### FIMO (Motif Scanning)

```bash
# Scan sequences for motif matches
fimo --oc fimo_output motif.meme sequences.fa

# Scan genome
fimo --oc fimo_output --max-stored-scores 1000000 motif.meme genome.fa
```

## Motif Databases

### HOMER Built-in

```bash
# List available motif sets
ls /path/to/homer/data/knownTFs/

# Vertebrate, known motifs (default)
findMotifsGenome.pl peaks.bed hg38 output/ -mknown vertebrates/known.motifs
```

### JASPAR

```bash
# Download JASPAR motifs
wget https://jaspar.genereg.net/download/data/2024/CORE/JASPAR2024_CORE_vertebrates_non-redundant_pfms_meme.txt

# Use with MEME suite
meme-chip -db JASPAR2024_CORE_vertebrates_non-redundant_pfms_meme.txt peaks.fa
```

### HOCOMOCO

```bash
# Download HOCOMOCO
wget https://hocomoco11.autosome.org/final_bundle/hocomoco11/core/HUMAN/mono/HOCOMOCOv11_core_HUMAN_mono_meme_format.meme

# Use with MEME suite
tomtom discovered.meme HOCOMOCOv11_core_HUMAN_mono_meme_format.meme
```

## Python: Parse HOMER Results

```python
import pandas as pd

def parse_homer_known(results_file):
    '''Parse HOMER knownResults.txt.'''
    df = pd.read_csv(results_file, sep='\t')
    df.columns = ['Motif', 'Consensus', 'P-value', 'Log P-value',
                  'q-value', 'Targets', 'Target%', 'Background', 'Background%']
    df['P-value'] = df['P-value'].astype(float)
    return df.sort_values('P-value')

known = parse_homer_known('output_dir/knownResults.txt')
print(known[['Motif', 'P-value', 'Target%']].head(20))
```

## Python: Parse MEME Results

```python
from Bio import motifs

def parse_meme_file(meme_file):
    '''Parse MEME output file.'''
    with open(meme_file) as f:
        record = motifs.parse(f, 'meme')
    return record

record = parse_meme_file('meme_output/meme.txt')
for m in record:
    print(f'{m.name}: {m.consensus}')
    print(m.counts)
```

## Complete Workflows

### ChIP-seq Motif Analysis

**Goal:** Run a complete motif analysis workflow combining HOMER and MEME-ChIP on ChIP-seq peaks.

**Approach:** Run HOMER findMotifsGenome.pl for fast de novo and known motif discovery, then extract centered peak sequences and run MEME-ChIP for a complementary analysis.

```bash
#!/bin/bash
set -euo pipefail

PEAKS=$1  # narrowPeak or BED file
GENOME=$2  # hg38, mm10, etc.
OUTDIR=$3

mkdir -p $OUTDIR

# HOMER analysis
echo "Running HOMER..."
findMotifsGenome.pl $PEAKS $GENOME ${OUTDIR}/homer \
    -size 200 -p 8 -mask

# Extract sequences for MEME
echo "Extracting sequences..."
bedtools slop -i $PEAKS -g ${GENOME}.chrom.sizes -b 0 | \
    awk 'BEGIN{OFS="\t"} {center=int(($2+$3)/2); print $1,center-100,center+100}' | \
    bedtools getfasta -fi ${GENOME}.fa -bed - -fo ${OUTDIR}/peaks.fa

# MEME-ChIP analysis
echo "Running MEME-ChIP..."
meme-chip -oc ${OUTDIR}/meme_chip \
    -db /path/to/JASPAR.meme \
    ${OUTDIR}/peaks.fa

echo "Done. Results in ${OUTDIR}/"
```

### ATAC-seq Footprint Motifs

```bash
# Analyze motifs in footprint regions
findMotifsGenome.pl footprints.bed hg38 footprint_motifs/ \
    -size given -mask -p 8

# Compare to accessible regions background
findMotifsGenome.pl footprints.bed hg38 footprint_motifs/ \
    -size given -bg accessible_peaks.bed -mask -p 8
```

## Visualization

### HOMER Logo

```bash
# Generate sequence logo
motif2Logo.pl motif.motif > logo.eps
```

### Plot with Python

```python
import logomaker
import pandas as pd
import matplotlib.pyplot as plt

def plot_motif(pwm_file):
    '''Plot sequence logo from HOMER PWM.'''
    pwm = pd.read_csv(pwm_file, sep='\t', skiprows=1, header=None)
    pwm.columns = ['A', 'C', 'G', 'T']
    logo = logomaker.Logo(pwm, shade_below=0.5, fade_below=0.5)
    plt.show()
```

## Quality Metrics

| Metric | Good | Concerning |
|--------|------|------------|
| P-value | < 1e-10 | > 1e-5 |
| Target % | > 20% | < 5% |
| Background % | < Target/2 | Similar to Target |
| Bit score | > 10 | < 5 |

## Common Issues

### No Significant Motifs
- Check peak quality (too few peaks?)
- Try different peak sizes (`-size`)
- Ensure genome build matches
- Check for repeat masking issues

### Too Many Motifs
- Increase significance threshold
- Use `-S` to limit number of motifs
- Filter by target percentage

### Wrong Background
- Use matched GC content background
- Consider using input/control peaks
- Try shuffled sequences

## Related Skills

- peak-calling - Generate input peaks
- peak-annotation - Annotate peaks with genes
- atac-seq/footprinting - TF footprint analysis
- genome-intervals - BED file operations
