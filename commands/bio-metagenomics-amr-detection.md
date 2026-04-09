# bio-metagenomics-amr-detection

> Detect antimicrobial resistance genes using AMRFinderPlus, ResFinder, and CARD. Screen isolates and metagenomes for resistance determinants. Use when characterizing resistance profiles in clinical isolates, surveillance samples, or metagenomic data.

## Version Compatibility

Reference examples tested with: AMRFinderPlus 3.12+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# AMR Detection

**"Screen my isolates for antibiotic resistance genes"** → Identify antimicrobial resistance determinants in bacterial genomes or metagenomes by searching against curated resistance gene databases.
- CLI: `amrfinder -n assembly.fasta --organism Escherichia` (AMRFinderPlus)
- CLI: ResFinder, CARD/RGI for alternative database searches

Identify antimicrobial resistance (AMR) genes in bacterial genomes and metagenomes.

## Tool Comparison

| Tool | Database | Best For |
|------|----------|----------|
| AMRFinderPlus | NCBI | Comprehensive, curated |
| ResFinder | CGE | Clinical isolates |
| CARD/RGI | CARD | Detailed resistance mechanisms |
| ABRicate | Multiple | Quick screening |

## AMRFinderPlus (NCBI)

### Installation

```bash
conda install -c bioconda ncbi-amrfinderplus
amrfinder -u  # Update database
```

### From Nucleotide Sequences

```bash
# Assembled contigs
amrfinder -n contigs.fasta -o amr_results.tsv --threads 8

# With organism for point mutations
amrfinder -n contigs.fasta -O Escherichia -o amr_results.tsv

# Include stress/virulence genes
amrfinder -n contigs.fasta -O Salmonella --plus -o amr_results.tsv
```

### From Protein Sequences

```bash
# If you have predicted proteins
amrfinder -p proteins.faa -o amr_results.tsv

# Combined nucleotide and protein
amrfinder -n contigs.fasta -p proteins.faa -g gff_annotation.gff \
    -O Escherichia -o amr_results.tsv
```

### Output Fields

| Column | Description |
|--------|-------------|
| Gene symbol | AMR gene name |
| Sequence name | Contig/protein ID |
| Element type | AMR, STRESS, VIRULENCE |
| Element subtype | Specific class |
| Class | Drug class |
| Subclass | Specific drug |
| % Coverage | Query coverage |
| % Identity | Sequence identity |

### Batch Processing

```bash
for fasta in assemblies/*.fasta; do
    sample=$(basename $fasta .fasta)
    amrfinder -n $fasta -O Escherichia --plus \
        -o results/${sample}_amr.tsv --threads 4
done

# Combine results
head -1 results/sample1_amr.tsv > combined_amr.tsv
for f in results/*_amr.tsv; do
    tail -n+2 $f >> combined_amr.tsv
done
```

## ResFinder

### Installation

```bash
conda install -c bioconda resfinder
# Or use web: https://cge.food.dtu.dk/services/ResFinder/
```

### Run ResFinder

```bash
# Assembled genome
python -m resfinder -ifa contigs.fasta -o resfinder_output \
    -db_res /path/to/resfinder_db -acq

# With species for point mutations
python -m resfinder -ifa contigs.fasta -o resfinder_output \
    -db_res /path/to/resfinder_db \
    -db_point /path/to/pointfinder_db \
    -s "Escherichia coli" -acq
```

### From Raw Reads (KMA)

```bash
python -m resfinder -ifq reads_1.fq reads_2.fq -o resfinder_output \
    -db_res /path/to/resfinder_db -acq
```

## CARD/RGI

Resistance Gene Identifier with detailed mechanism annotations.

### Installation

```bash
conda install -c bioconda rgi
rgi load --card_json /path/to/card.json --local
```

### Run RGI

```bash
# From contigs
rgi main --input_sequence contigs.fasta --output_file rgi_output \
    --input_type contig --local --clean

# From protein
rgi main --input_sequence proteins.faa --output_file rgi_output \
    --input_type protein --local

# Include loose hits (more sensitive)
rgi main --input_sequence contigs.fasta --output_file rgi_output \
    --input_type contig --include_loose --local
```

### RGI Output

```bash
# Main results
cat rgi_output.txt

# JSON with full details
cat rgi_output.json
```

## ABRicate (Quick Screening)

### Installation

```bash
conda install -c bioconda abricate
abricate --setupdb  # Update databases
```

### Available Databases

```bash
abricate --list
# ncbi, card, resfinder, argannot, megares, ecoh, ecoli_vf, plasmidfinder, vfdb
```

### Run ABRicate

```bash
# Default (ncbi)
abricate contigs.fasta > abricate_results.tsv

# Specific database
abricate --db resfinder contigs.fasta > resfinder_results.tsv
abricate --db card contigs.fasta > card_results.tsv

# Multiple databases
for db in ncbi card resfinder; do
    abricate --db $db contigs.fasta > ${db}_results.tsv
done
```

### Batch Summary

```bash
# Run on multiple samples
abricate assemblies/*.fasta > all_results.tsv

# Generate summary matrix
abricate --summary all_results.tsv > summary_matrix.tsv
```

## Metagenome AMR Profiling

### Using ShortBRED

```bash
# Map reads to AMR markers
shortbred_quantify.py --markers amr_markers.faa \
    --wgs reads_1.fq reads_2.fq \
    --results amr_abundance.tsv \
    --threads 8
```

### Using GROOT

```bash
# Index database
groot index -m card.90 -i groot_index -p 8

# Align and report
groot align -i groot_index -f reads_1.fq,reads_2.fq -p 8 | \
    groot report > amr_report.tsv
```

## Complete Workflow

**Goal:** Screen a bacterial assembly for antimicrobial resistance genes using multiple databases for comprehensive resistance profiling.

**Approach:** Run AMRFinderPlus with organism-specific point mutation detection, then ABRicate against NCBI/CARD/ResFinder databases, and summarize drug class counts.

```bash
#!/bin/bash
set -euo pipefail

ASSEMBLY=$1
ORGANISM=$2
OUTPUT_DIR=$3

mkdir -p $OUTPUT_DIR

echo "=== AMRFinderPlus ==="
amrfinder -n $ASSEMBLY -O $ORGANISM --plus \
    -o $OUTPUT_DIR/amrfinder.tsv --threads 8

echo "=== ABRicate (multiple databases) ==="
for db in ncbi card resfinder; do
    abricate --db $db $ASSEMBLY > $OUTPUT_DIR/abricate_${db}.tsv
done

echo "=== Summary ==="
echo "AMR genes found:"
cut -f6 $OUTPUT_DIR/amrfinder.tsv | sort | uniq -c | sort -rn | head -20

echo "=== Complete ==="
echo "Results in $OUTPUT_DIR/"
```

## Summarize Results

```python
import pandas as pd

# Load AMRFinderPlus results
amr = pd.read_csv('amrfinder.tsv', sep='\t')

# Count by drug class
class_counts = amr['Class'].value_counts()
print(class_counts)

# Pivot for heatmap (multiple samples)
import glob
results = []
for f in glob.glob('results/*_amr.tsv'):
    sample = f.split('/')[-1].replace('_amr.tsv', '')
    df = pd.read_csv(f, sep='\t')
    df['Sample'] = sample
    results.append(df)

combined = pd.concat(results)
matrix = pd.crosstab(combined['Sample'], combined['Gene symbol'])
```

## Related Skills

- metagenomics/kraken-classification - Taxonomic context
- metagenomics/functional-profiling - Functional pathways
- genome-assembly/contamination-detection - Sample QC
- workflows/metagenomics-pipeline - Full metagenomics workflow
