# bio-metagenomics-strain-tracking

> Track bacterial strains using MASH, sourmash, fastANI, and inStrain. Compare genomes, detect contamination, and monitor strain-level variation. Use when needing sub-species resolution for outbreak tracking, transmission analysis, or within-host strain dynamics.

## Version Compatibility

Reference examples tested with: Bowtie2 2.5.3+, MetaPhlAn 4.1+, numpy 1.26+, pandas 2.2+, samtools 1.19+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Strain Tracking

**"Track bacterial strains across my samples"** → Resolve sub-species variation using genome sketching (Mash/sourmash), average nucleotide identity (fastANI), or within-sample strain profiling (inStrain) for outbreak tracking and transmission analysis.
- CLI: `mash dist`, `sourmash compare`, `fastANI`, `inStrain profile`

Identify and track bacterial strains at sub-species resolution.

## Tool Comparison

| Tool | Method | Best For |
|------|--------|----------|
| MASH | MinHash sketches | Fast distance estimation |
| sourmash | MinHash + containment | Metagenome comparisons |
| fastANI | ANI calculation | Accurate species/strain ID |
| inStrain | SNV profiling | Strain dynamics in metagenomes |

## MASH

### Installation

```bash
conda install -c bioconda mash
```

### Create Sketch

```bash
# Single genome
mash sketch -o genome.msh genome.fasta

# Multiple genomes
mash sketch -o reference_db.msh genomes/*.fasta

# From reads (with coverage)
mash sketch -m 2 -r -o reads.msh reads.fastq.gz
```

### Calculate Distance

```bash
# Pairwise distance
mash dist genome1.fasta genome2.fasta

# Query against database
mash dist reference_db.msh query.fasta > distances.tsv

# Screen for containment (metagenome)
mash screen reference_db.msh reads.fastq.gz > screen_results.tsv
```

### Interpret MASH Distance

| Distance | Interpretation |
|----------|----------------|
| < 0.05 | Same species/strain |
| 0.05-0.15 | Same species |
| 0.15-0.25 | Same genus |
| > 0.25 | Different genus |

### Cluster Genomes

```bash
# All-vs-all distances
mash triangle genomes/*.fasta > distances.phylip

# Build tree
mash triangle -E genomes/*.fasta > distances.tsv
```

## sourmash

### Installation

```bash
conda install -c bioconda sourmash
```

### Create Signatures

```bash
# Genome signature
sourmash sketch dna -p scaled=1000,k=31 genome.fasta -o genome.sig

# Multiple genomes
sourmash sketch dna -p scaled=1000,k=31 genomes/*.fasta -o genomes.sig

# Protein signatures
sourmash sketch protein -p scaled=100,k=10 proteins.faa -o proteins.sig
```

### Compare Signatures

```bash
# Pairwise comparison
sourmash compare *.sig -o comparison.npy --csv comparison.csv

# Search against database
sourmash search query.sig database.sig --threshold 0.8

# Gather (metagenome decomposition)
sourmash gather metagenome.sig database.sig -o gather_results.csv
```

### Taxonomy Assignment

```bash
# Download taxonomy database
sourmash database download gtdb-rs214-k31.zip

# Classify
sourmash lca classify --db gtdb-rs214-k31.lca.json.gz --query query.sig

# Summarize metagenome
sourmash lca summarize --db gtdb-rs214-k31.lca.json.gz --query metagenome.sig
```

## fastANI

### Installation

```bash
conda install -c bioconda fastani
```

### Calculate ANI

```bash
# Single pair
fastANI -q query.fasta -r reference.fasta -o ani_result.txt

# Query vs multiple references
fastANI -q query.fasta --rl reference_list.txt -o ani_results.txt

# All-vs-all
fastANI --ql genome_list.txt --rl genome_list.txt -o all_vs_all.txt --matrix
```

### Interpret ANI

| ANI | Interpretation |
|-----|----------------|
| >99% | Same strain |
| 95-99% | Same species |
| <95% | Different species |

## inStrain

For strain-level analysis in metagenomes.

### Installation

```bash
conda install -c bioconda instrain
```

### Profile Strains

```bash
# Map reads to reference
bowtie2 -x reference -1 reads_1.fq -2 reads_2.fq | \
    samtools sort -o mapped.bam

# Profile with inStrain
inStrain profile mapped.bam reference.fasta -o instrain_output -p 8
```

### Compare Samples

```bash
# Profile multiple samples
for bam in sample*.bam; do
    inStrain profile $bam reference.fasta -o ${bam%.bam}_IS -p 8
done

# Compare strain populations
inStrain compare -i sample*_IS -o comparison_IS -p 8
```

### Key Outputs

```bash
# SNV table
cat instrain_output/output/SNVs.tsv

# Gene-level info
cat instrain_output/output/gene_info.tsv

# Genome info
cat instrain_output/output/genome_info.tsv
```

## Complete Workflow: Outbreak Tracking

**Goal:** Identify potential outbreak clusters by computing pairwise genomic distances across isolate genomes using multiple complementary methods.

**Approach:** Sketch genomes with MASH for fast distance estimation, compute ANI with fastANI for accurate species-level resolution, compare sourmash signatures for containment analysis, and cluster close matches to identify transmission pairs.

```bash
#!/bin/bash
set -euo pipefail

GENOMES_DIR=$1
OUTPUT_DIR=$2

mkdir -p $OUTPUT_DIR

echo "=== MASH sketching ==="
mash sketch -o $OUTPUT_DIR/genomes.msh $GENOMES_DIR/*.fasta

echo "=== MASH distances ==="
mash dist $OUTPUT_DIR/genomes.msh $OUTPUT_DIR/genomes.msh > $OUTPUT_DIR/mash_distances.tsv

echo "=== fastANI ==="
ls $GENOMES_DIR/*.fasta > $OUTPUT_DIR/genome_list.txt
fastANI --ql $OUTPUT_DIR/genome_list.txt \
        --rl $OUTPUT_DIR/genome_list.txt \
        -o $OUTPUT_DIR/fastani_results.txt \
        --matrix

echo "=== sourmash signatures ==="
sourmash sketch dna -p scaled=1000,k=31 $GENOMES_DIR/*.fasta -o $OUTPUT_DIR/all.sig
sourmash compare $OUTPUT_DIR/all.sig -o $OUTPUT_DIR/sourmash.npy --csv $OUTPUT_DIR/sourmash.csv

echo "=== Identify clusters ==="
python3 << 'EOF'
import pandas as pd
import numpy as np

# Load MASH distances
mash = pd.read_csv('${OUTPUT_DIR}/mash_distances.tsv', sep='\t', header=None,
                   names=['ref', 'query', 'distance', 'pvalue', 'shared'])

# Filter for close matches (potential outbreak cluster)
close = mash[(mash['distance'] < 0.001) & (mash['ref'] != mash['query'])]
print("Potential outbreak pairs (MASH distance < 0.001):")
print(close[['ref', 'query', 'distance']])
EOF

echo "=== Complete ==="
```

## Python Analysis

```python
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

# Load MASH distances
mash = pd.read_csv('mash_distances.tsv', sep='\t', header=None,
                   names=['ref', 'query', 'dist', 'pval', 'shared'])

# Pivot to matrix
samples = sorted(set(mash['ref'].tolist()))
dist_matrix = mash.pivot(index='ref', columns='query', values='dist').fillna(0)
dist_matrix = dist_matrix.loc[samples, samples]

# Cluster
condensed = squareform(dist_matrix.values)
Z = linkage(condensed, method='average')

# Cut tree at species level (0.05)
clusters = fcluster(Z, t=0.05, criterion='distance')
cluster_df = pd.DataFrame({'sample': samples, 'cluster': clusters})
print(cluster_df.groupby('cluster').size())
```

## Related Skills

- metagenomics/kraken-classification - Taxonomic classification
- genome-assembly/contamination-detection - Contamination screening
- phylogenetics/modern-tree-inference - Phylogenetic analysis
- metagenomics/metaphlan-profiling - Species profiling
