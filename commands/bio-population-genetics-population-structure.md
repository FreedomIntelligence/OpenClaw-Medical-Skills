# bio-population-genetics-population-structure

> Analyze population structure using PCA and admixture analysis with PLINK and ADMIXTURE. Identify population clusters, assess ancestry proportions, visualize genetic structure, and choose optimal K for admixture models. Use when analyzing population stratification with PCA or admixture.

**Available tools:** Read, Bash

# Population Structure

Analyze genetic ancestry and population stratification using PCA and ADMIXTURE.

## Principal Component Analysis (PCA)

### PLINK 2.0 PCA

```bash
# Basic PCA (10 PCs)
plink2 --bfile data --pca 10 --out pca_results

# More PCs
plink2 --bfile data --pca 20 --out pca_results

# Approximate PCA (faster for large datasets)
plink2 --bfile data --pca 10 approx --out pca_results

# Output variant loadings
plink2 --bfile data --pca 10 var-wts --out pca_results
```

### Output Files

| File | Contents |
|------|----------|
| `.eigenvec` | PC scores per sample (FID, IID, PC1, PC2, ...) |
| `.eigenval` | Eigenvalues (variance explained) |
| `.eigenvec.var` | Variant loadings (if var-wts) |

### Variance Explained

```python
import numpy as np

eigenvalues = np.loadtxt('pca_results.eigenval')
variance_explained = eigenvalues / eigenvalues.sum() * 100
cumulative = np.cumsum(variance_explained)

for i, (ve, cum) in enumerate(zip(variance_explained, cumulative), 1):
    print(f'PC{i}: {ve:.2f}% (cumulative: {cum:.2f}%)')
```

### PCA Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt

eigenvec = pd.read_csv('pca_results.eigenvec', sep='\s+', header=None)
eigenvec.columns = ['FID', 'IID'] + [f'PC{i}' for i in range(1, len(eigenvec.columns) - 1)]

pop_info = pd.read_csv('population_labels.txt', sep='\t')  # FID, IID, Population
eigenvec = eigenvec.merge(pop_info, on=['FID', 'IID'])

plt.figure(figsize=(10, 8))
for pop in eigenvec['Population'].unique():
    subset = eigenvec[eigenvec['Population'] == pop]
    plt.scatter(subset['PC1'], subset['PC2'], label=pop, s=20, alpha=0.7)

plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.savefig('pca_plot.png', dpi=150)
```

## LD Pruning (Before Admixture)

ADMIXTURE requires LD-pruned SNPs:

```bash
# Calculate LD and identify pruned set
plink2 --bfile data --indep-pairwise 50 10 0.1 --out prune

# Extract pruned variants
plink2 --bfile data --extract prune.prune.in --make-bed --out data_pruned
```

### Pruning Parameters

| Parameter | Description |
|-----------|-------------|
| Window (50) | SNPs in each window |
| Step (10) | SNPs to shift per step |
| r² threshold (0.1) | Max LD allowed |

## ADMIXTURE Analysis

### Basic Usage

```bash
# Run ADMIXTURE for K=3 clusters
admixture data_pruned.bed 3

# With cross-validation
admixture --cv data_pruned.bed 3

# Multithreaded
admixture -j4 data_pruned.bed 3
```

### Output Files

| File | Contents |
|------|----------|
| `.Q` | Ancestry proportions (samples × K) |
| `.P` | Allele frequencies per cluster |

### Testing Multiple K Values

```bash
# Run for K=2 through K=10
for K in $(seq 2 10); do
    admixture --cv -j4 data_pruned.bed $K 2>&1 | tee log${K}.out
done

# Extract CV errors
grep -h "CV" log*.out | awk '{print NR+1, $4}' > cv_errors.txt
```

### Choose Optimal K

```python
import matplotlib.pyplot as plt

cv_errors = []
with open('cv_errors.txt') as f:
    for line in f:
        k, cv = line.strip().split()
        cv_errors.append((int(k), float(cv)))

ks, cvs = zip(*cv_errors)
plt.figure(figsize=(8, 5))
plt.plot(ks, cvs, 'o-')
plt.xlabel('K')
plt.ylabel('Cross-validation error')
plt.title('Admixture CV Error')
plt.savefig('admixture_cv.png', dpi=150)

optimal_k = ks[cvs.index(min(cvs))]
print(f'Optimal K: {optimal_k}')
```

### Visualize Admixture

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

K = 3
Q = pd.read_csv(f'data_pruned.{K}.Q', sep='\s+', header=None)
fam = pd.read_csv('data_pruned.fam', sep='\s+', header=None)
Q.columns = [f'Cluster{i}' for i in range(1, K + 1)]
Q['IID'] = fam[1].values

pop_info = pd.read_csv('population_labels.txt', sep='\t')
Q = Q.merge(pop_info, on='IID')
Q = Q.sort_values('Population')

colors = plt.cm.Set1(range(K))
fig, ax = plt.subplots(figsize=(14, 4))

bottom = np.zeros(len(Q))
for i in range(K):
    ax.bar(range(len(Q)), Q[f'Cluster{i+1}'], bottom=bottom, color=colors[i], width=1)
    bottom += Q[f'Cluster{i+1}'].values

ax.set_xlim(0, len(Q))
ax.set_ylim(0, 1)
ax.set_ylabel('Ancestry proportion')
plt.savefig('admixture_barplot.png', dpi=150, bbox_inches='tight')
```

## FlashPCA2 (Fast PCA for Large Datasets)

FlashPCA2 is optimized for very large datasets (100,000+ samples). Uses randomized algorithms for speed.

### Installation

```bash
# From conda
conda install -c bioconda flashpca

# Or download binaries from GitHub
# https://github.com/gabraham/flashpca
```

### Basic Usage

```bash
# Standard PCA
flashpca2 --bfile data --ndim 10 --outpc pcs.txt --outvec loadings.txt --outval eigenvalues.txt

# --ndim 10: Number of PCs to compute
# --outpc: Principal components output
# --outvec: Eigenvectors (variant loadings)
# --outval: Eigenvalues
```

### FlashPCA2 Options

| Option | Description |
|--------|-------------|
| --bfile | PLINK binary prefix |
| --ndim | Number of PCs (default 10) |
| --outpc | PC scores output file |
| --outvec | Eigenvectors output |
| --outval | Eigenvalues output |
| --numthreads | CPU threads to use |
| --mem | Memory limit (GB) |
| --seed | Random seed for reproducibility |

### Large Dataset Settings

```bash
# For biobank-scale data (>100k samples)
# numthreads=16: Adjust to available cores.
# mem=64: Memory in GB. Increase for larger datasets.
flashpca2 \
    --bfile large_data \
    --ndim 20 \
    --numthreads 16 \
    --mem 64 \
    --outpc pcs.txt \
    --outval eigenvalues.txt \
    --seed 42
```

### FlashPCA2 vs PLINK2

| Feature | FlashPCA2 | PLINK2 |
|---------|-----------|--------|
| Speed (100k samples) | Faster | Good |
| Memory efficiency | Better | Good |
| Randomized algorithm | Yes | Optional (approx) |
| Part of standard toolkit | No | Yes |

Use FlashPCA2 for biobank-scale data; PLINK2 sufficient for most studies.

### Parse FlashPCA2 Output

```python
import pandas as pd

# Load PCs
pcs = pd.read_csv('pcs.txt', sep='\t', header=None)
pcs.columns = ['FID', 'IID'] + [f'PC{i}' for i in range(1, len(pcs.columns) - 1)]

# Load eigenvalues
eigenvals = pd.read_csv('eigenvalues.txt', header=None)[0].values
var_explained = eigenvals / eigenvals.sum() * 100

print('Variance explained:')
for i, ve in enumerate(var_explained[:10], 1):
    print(f'  PC{i}: {ve:.2f}%')
```

## MDS (Alternative to PCA)

```bash
# PLINK 1.9 MDS
plink --bfile data --cluster --mds-plot 10 --out mds_results

# Output: mds_results.mds (sample coordinates)
```

## Kinship/Relatedness

### PLINK 2.0 KING-robust

```bash
# Calculate kinship matrix
plink2 --bfile data --make-king-table --out kinship

# Output: kinship.kin0 (pairs with kinship > 0.0442)
```

### Identify Related Individuals

```python
import pandas as pd

kin = pd.read_csv('kinship.kin0', sep='\t')
related = kin[kin['KINSHIP'] > 0.0884]  # First-degree relatives
print(f'Related pairs (1st degree): {len(related)}')

related = kin[kin['KINSHIP'] > 0.0442]  # Second-degree
print(f'Related pairs (2nd degree): {len(related)}')
```

### Remove Related Individuals

```bash
# Create list to remove (keep one per pair)
plink2 --bfile data --king-cutoff 0.0884 --out unrelated

# Filter to unrelated
plink2 --bfile data --keep unrelated.king.cutoff.in.id --make-bed --out unrelated
```

## Complete Workflow

```bash
# 1. QC filtering
plink2 --bfile raw --maf 0.01 --geno 0.05 --hwe 1e-6 --make-bed --out qc

# 2. LD pruning
plink2 --bfile qc --indep-pairwise 50 10 0.1 --out prune
plink2 --bfile qc --extract prune.prune.in --make-bed --out pruned

# 3. PCA
plink2 --bfile pruned --pca 20 --out pca

# 4. Admixture (multiple K)
for K in 2 3 4 5 6; do
    admixture --cv -j4 pruned.bed $K 2>&1 | tee log${K}.out
done
```

## Related Skills

- plink-basics - Data preparation and QC
- linkage-disequilibrium - LD pruning details
- association-testing - Use PCs as covariates
