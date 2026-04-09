# bio-epidemiological-genomics-pathogen-typing

> Perform multi-locus sequence typing (MLST), core genome MLST, and SNP-based strain typing for bacterial isolate characterization using mlst and chewBBACA. Use when identifying strain types, tracking outbreak clones, or characterizing bacterial isolates.

## Version Compatibility

Reference examples tested with: mlst 2.23+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Pathogen Typing

**"Type my bacterial isolates by MLST"** → Assign multi-locus sequence types to bacterial genomes for isolate characterization, outbreak clone identification, and strain tracking.
- CLI: `mlst assembly.fasta` for 7-gene MLST typing
- CLI: `chewBBACA.py AlleleCall` for core genome MLST (cgMLST)

## MLST with mlst Tool

```bash
# Install mlst
conda install -c bioconda mlst

# Basic MLST typing
mlst genome.fasta
# Output: genome.fasta  ecoli  ST131  adk(53) fumC(40) gyrB(47) ...

# Batch typing
mlst *.fasta > typing_results.tsv

# Specify scheme
mlst --scheme senterica genome.fasta

# List available schemes
mlst --list

# Include allele sequences in output
mlst --csv genome.fasta > results.csv
```

## Parse MLST Results

```python
import pandas as pd
import subprocess

def run_mlst(fasta_files, scheme=None):
    '''Run MLST on multiple genomes

    Returns DataFrame with:
    - Sample name
    - Scheme (auto-detected or specified)
    - Sequence type (ST)
    - Allele profiles

    ST interpretation:
    - Known ST: Matches existing type in database
    - Novel allele: New allele combination, may be unreported ST
    - Failed: Unable to determine (poor assembly or wrong scheme)
    '''
    cmd = ['mlst'] + fasta_files
    if scheme:
        cmd.extend(['--scheme', scheme])

    result = subprocess.run(cmd, capture_output=True, text=True)

    lines = result.stdout.strip().split('\n')
    data = [line.split('\t') for line in lines]

    return pd.DataFrame(data, columns=['file', 'scheme', 'ST'] +
                       [f'locus{i}' for i in range(1, len(data[0])-2)])
```

## Core Genome MLST (cgMLST)

```bash
# chewBBACA for cgMLST
pip install chewbbaca

# Download or create schema
chewBBACA.py DownloadSchema -sp "Salmonella enterica" -o schema_dir

# Run cgMLST
chewBBACA.py AlleleCall -i genomes/ -g schema_dir -o results/

# Analyze results
chewBBACA.py ExtractCgMLST -i results/results_alleles.tsv \
    -o cgmlst_results.tsv --threshold 0.95
```

## cgMLST Distance Analysis

**Goal:** Compute pairwise allelic distances between isolates and cluster them to identify potential outbreak groups.

**Approach:** Count allelic differences between each pair of isolate profiles (ignoring missing data), then apply single-linkage hierarchical clustering with a pathogen-specific distance threshold.

```python
import pandas as pd
import numpy as np

def calculate_cgmlst_distance(profiles):
    '''Calculate allelic distances between isolates

    Distance interpretation (typical thresholds):
    - 0-5 allele differences: Same cluster (likely recent transmission)
    - 6-15 differences: Related (possible epidemiological link)
    - >15 differences: Different clones

    Note: Thresholds are pathogen-specific. Consult literature.
    '''
    n = len(profiles)
    distances = np.zeros((n, n))

    for i in range(n):
        for j in range(i+1, n):
            # Count allelic differences (excluding missing data)
            diff = sum(1 for a, b in zip(profiles.iloc[i], profiles.iloc[j])
                      if a != b and a != 0 and b != 0)
            distances[i, j] = distances[j, i] = diff

    return pd.DataFrame(distances, index=profiles.index, columns=profiles.index)


def identify_clusters(distance_matrix, threshold=5):
    '''Identify cgMLST clusters

    Threshold values by organism:
    - E. coli: 10 alleles
    - Salmonella: 7 alleles
    - Listeria: 7 alleles
    - S. aureus: 24 alleles
    '''
    from scipy.cluster.hierarchy import linkage, fcluster

    # Convert to condensed distance matrix
    condensed = distance_matrix.values[np.triu_indices(len(distance_matrix), k=1)]

    # Hierarchical clustering
    Z = linkage(condensed, method='single')
    clusters = fcluster(Z, t=threshold, criterion='distance')

    return dict(zip(distance_matrix.index, clusters))
```

## SNP-Based Typing

```python
def snp_typing_from_vcf(vcf_file, reference_positions):
    '''Extract SNP profile for typing

    Some organisms use canonical SNP positions for typing
    (e.g., Mycobacterium tuberculosis lineages)
    '''
    from cyvcf2 import VCF

    vcf = VCF(vcf_file)
    profile = {}

    for pos in reference_positions:
        chrom, position = pos.split(':')
        for variant in vcf(f'{chrom}:{position}-{position}'):
            profile[pos] = variant.ALT[0] if variant.ALT else variant.REF

    return profile
```

## Enterobase Integration

```python
import requests

def query_enterobase(st, organism='ecoli'):
    '''Query Enterobase for ST metadata

    Enterobase provides:
    - Geographic distribution
    - Temporal trends
    - Associated serotypes
    - Virulence gene profiles
    '''
    # Note: Requires API token
    url = f'https://enterobase.warwick.ac.uk/api/v2.0/{organism}/sts/{st}'

    # Would need authentication headers
    # response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    print(f'Query Enterobase for ST{st}: {url}')
    return None  # Placeholder - requires authentication
```

## Related Skills

- epidemiological-genomics/phylodynamics - Time-scaled trees from typed isolates
- epidemiological-genomics/transmission-inference - Outbreak investigation
- metagenomics/kraken-classification - Species identification
