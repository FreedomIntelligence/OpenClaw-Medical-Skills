# bio-genome-assembly-assembly-qc

> Assess genome assembly quality using QUAST for contiguity metrics and BUSCO for completeness. Essential for evaluating assembly success and comparing assemblers. Use when evaluating assembly completeness and quality.

**Available tools:** Read, Bash

# Assembly QC

Evaluate genome assembly quality with contiguity metrics (QUAST) and gene completeness (BUSCO).

## Key Metrics

| Metric | Good Assembly |
|--------|---------------|
| N50 | High (relative to genome) |
| L50 | Low |
| Contigs | Few |
| Misassemblies | 0 (with reference) |
| BUSCO Complete | >95% |
| BUSCO Duplicated | <5% (unless polyploid) |

## QUAST

### Installation

```bash
conda install -c bioconda quast
```

### Basic Usage

```bash
quast.py assembly.fasta -o quast_output
```

### With Reference Genome

```bash
quast.py assembly.fasta -r reference.fasta -o quast_output
```

### Compare Multiple Assemblies

```bash
quast.py assembly1.fa assembly2.fa assembly3.fa -o comparison
```

### Key Options

| Option | Description |
|--------|-------------|
| `-o` | Output directory |
| `-r` | Reference genome |
| `-g` | Gene annotations (GFF) |
| `-t` | Threads |
| `-m` | Min contig length (default: 500) |
| `--large` | For large genomes (>100Mb) |
| `--fragmented` | For highly fragmented assemblies |
| `--scaffolds` | Input is scaffolds (includes N-gaps) |

### With Gene Annotations

```bash
quast.py assembly.fasta -r reference.fasta -g genes.gff -o quast_output
```

### For Large Genomes

```bash
quast.py --large assembly.fasta -o quast_output -t 16
```

### Output Files

```
quast_output/
├── report.txt        # Summary statistics
├── report.html       # Interactive report
├── report.tsv        # Tab-separated stats
├── icarus.html       # Contig viewer
└── aligned_stats/    # If reference provided
```

### Key Output Metrics

| Metric | Description |
|--------|-------------|
| Total length | Sum of contig lengths |
| # contigs | Number of contigs (>= min length) |
| Largest contig | Length of largest contig |
| N50 | 50% of assembly in contigs >= this length |
| N90 | 90% of assembly in contigs >= this length |
| L50 | Number of contigs comprising N50 |
| GC % | GC content |
| # misassemblies | With reference: structural errors |
| Genome fraction | With reference: % of reference covered |

## BUSCO

### Installation

```bash
conda install -c bioconda busco
```

### Basic Usage

```bash
busco -i assembly.fasta -m genome -l bacteria_odb10 -o busco_output
```

### Key Options

| Option | Description |
|--------|-------------|
| `-i` | Input assembly |
| `-m` | Mode: genome, proteins, transcriptome |
| `-l` | Lineage dataset |
| `-o` | Output name |
| `-c` | CPU threads |
| `--auto-lineage` | Auto-detect lineage |
| `--offline` | Use downloaded datasets only |
| `--list-datasets` | List available lineages |

### List Available Lineages

```bash
busco --list-datasets
```

### Common Lineages

| Lineage | Use For |
|---------|---------|
| bacteria_odb10 | Bacteria |
| archaea_odb10 | Archaea |
| eukaryota_odb10 | General eukaryote |
| fungi_odb10 | Fungi |
| metazoa_odb10 | Animals |
| vertebrata_odb10 | Vertebrates |
| mammalia_odb10 | Mammals |
| viridiplantae_odb10 | Plants |
| saccharomycetes_odb10 | Yeasts |

### Auto-Lineage Detection

```bash
busco -i assembly.fasta -m genome --auto-lineage -o busco_output
```

### Output Files

```
busco_output/
├── short_summary.txt           # Quick summary
├── full_table.tsv              # All BUSCO results
├── missing_busco_list.tsv      # Missing genes
└── busco_sequences/            # BUSCO gene sequences
```

### Interpret Results

```
C:98.5%[S:97.0%,D:1.5%],F:0.5%,M:1.0%,n:4085

C - Complete (total)
S - Single-copy
D - Duplicated
F - Fragmented
M - Missing
n - Total BUSCO groups
```

### Quality Thresholds

| Quality | Complete | Missing |
|---------|----------|---------|
| Excellent | >95% | <2% |
| Good | >90% | <5% |
| Acceptable | >80% | <10% |
| Poor | <80% | >10% |

## Complete QC Workflow

```bash
#!/bin/bash
set -euo pipefail

ASSEMBLY=$1
REFERENCE=${2:-}
LINEAGE=${3:-bacteria_odb10}
OUTDIR=${4:-assembly_qc}

mkdir -p $OUTDIR

echo "=== Assembly QC ==="

# QUAST
echo "Running QUAST..."
if [ -n "$REFERENCE" ]; then
    quast.py $ASSEMBLY -r $REFERENCE -o ${OUTDIR}/quast -t 8
else
    quast.py $ASSEMBLY -o ${OUTDIR}/quast -t 8
fi

# BUSCO
echo "Running BUSCO..."
busco -i $ASSEMBLY -m genome -l $LINEAGE -o busco_run -c 8
mv busco_run ${OUTDIR}/busco

# Summary
echo ""
echo "=== QUAST Summary ==="
cat ${OUTDIR}/quast/report.txt

echo ""
echo "=== BUSCO Summary ==="
cat ${OUTDIR}/busco/short_summary*.txt

echo ""
echo "Reports saved to $OUTDIR"
```

## Compare Assemblies

### QUAST Comparison

```bash
quast.py \
    spades_assembly.fa \
    flye_assembly.fa \
    canu_assembly.fa \
    -r reference.fa \
    -l "SPAdes,Flye,Canu" \
    -o assembly_comparison
```

### BUSCO Comparison

```bash
# Run BUSCO on each assembly
for asm in spades.fa flye.fa canu.fa; do
    name=$(basename $asm .fa)
    busco -i $asm -m genome -l bacteria_odb10 -o busco_${name}
done

# Generate comparison plot
generate_plot.py -wd . busco_spades busco_flye busco_canu
```

## Python: Parse QUAST Output

```python
import pandas as pd

def parse_quast(report_tsv):
    '''Parse QUAST report.tsv file.'''
    df = pd.read_csv(report_tsv, sep='\t', index_col=0)
    return df.T

stats = parse_quast('quast_output/report.tsv')
print(f"N50: {stats['N50'].values[0]}")
print(f"Total length: {stats['Total length'].values[0]}")
print(f"# contigs: {stats['# contigs'].values[0]}")
```

## Python: Parse BUSCO Output

```python
import re

def parse_busco_summary(summary_file):
    '''Parse BUSCO short summary.'''
    with open(summary_file) as f:
        text = f.read()

    pattern = r'C:(\d+\.\d+)%\[S:(\d+\.\d+)%,D:(\d+\.\d+)%\],F:(\d+\.\d+)%,M:(\d+\.\d+)%,n:(\d+)'
    match = re.search(pattern, text)

    if match:
        return {
            'complete': float(match.group(1)),
            'single': float(match.group(2)),
            'duplicated': float(match.group(3)),
            'fragmented': float(match.group(4)),
            'missing': float(match.group(5)),
            'total': int(match.group(6))
        }
    return None

result = parse_busco_summary('busco_output/short_summary.txt')
print(f"Complete: {result['complete']}%")
```

## MetaQUAST (Metagenomes)

```bash
metaquast.py metagenome_assembly.fa -o metaquast_output -t 16
```

## Troubleshooting

### Low N50
- Check coverage depth
- Consider longer reads
- Try different assembler

### Low BUSCO Completeness
- Check input read quality
- Verify correct lineage dataset
- May indicate real gene loss (compare to relatives)

### High Duplication in BUSCO
- Normal for polyploids
- May indicate contamination
- Check for collapsed haplotypes

## Related Skills

- short-read-assembly - SPAdes assembly
- long-read-assembly - Flye/Canu assembly
- assembly-polishing - Improve accuracy
- metagenomics - Metagenome analysis
