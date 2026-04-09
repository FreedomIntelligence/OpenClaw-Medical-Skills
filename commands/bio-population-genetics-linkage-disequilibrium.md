# bio-population-genetics-linkage-disequilibrium

> Calculate linkage disequilibrium statistics (r², D'), perform LD pruning for population structure analysis, identify haplotype blocks, and visualize LD patterns using PLINK, scikit-allel, and LDBlockShow. Use when calculating LD or pruning variants.

**Available tools:** Read, Bash

# Linkage Disequilibrium

Calculate LD statistics, prune correlated variants, and identify haplotype blocks.

## PLINK LD Calculations

### Pairwise r²

```bash
# All pairs within window
plink2 --bfile data --r2 --ld-window-kb 1000 --ld-window-r2 0.2 --out ld_results

# With SNP names in output
plink2 --bfile data --r2 inter-chr --ld-window-r2 0 --out all_pairs

# Squared correlation matrix
plink2 --bfile data --r2-phased square --out ld_matrix
```

### Output Format

```
# ld_results.ld contains:
CHR_A  BP_A  SNP_A  CHR_B  BP_B  SNP_B  R2
```

### PLINK 1.9 Options

```bash
# r² with D' statistics
plink --bfile data --r2 dprime --ld-window-kb 500 --out ld_with_dprime

# Inter-chromosome LD
plink --bfile data --r2 inter-chr --ld-snp-list target_snps.txt --out target_ld
```

## LD Pruning

### Standard Pruning

```bash
# Calculate pruning list
plink2 --bfile data --indep-pairwise 50 10 0.1 --out prune

# Output files:
# prune.prune.in  - Variants to keep
# prune.prune.out - Variants to remove

# Extract pruned set
plink2 --bfile data --extract prune.prune.in --make-bed --out data_pruned
```

### Pruning Parameters

| Parameter | Description | Common Values |
|-----------|-------------|---------------|
| Window (50) | Variants per window | 50-200 |
| Step (10) | Variants to shift | 5-50 |
| r² threshold (0.1) | Max LD allowed | 0.1-0.5 |

### Use Cases

```bash
# Strict pruning for PCA/Admixture
plink2 --bfile data --indep-pairwise 50 10 0.1 --out strict_prune

# Moderate pruning for polygenic scores
plink2 --bfile data --indep-pairwise 200 50 0.5 --out moderate_prune

# Region-based pruning
plink2 --bfile data --indep-pairwise 50 10 0.2 --chr 6 --from-mb 25 --to-mb 35 --out mhc_prune
```

## scikit-allel LD

### Pairwise r²

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']

gn = gt.to_n_alt()

r2 = allel.rogers_huff_r(gn[:100]) ** 2
```

### LD Decay

```python
import allel
import numpy as np
import matplotlib.pyplot as plt

gn = gt.to_n_alt()

r2, dist = [], []
n_variants = min(1000, gn.shape[0])

for i in range(n_variants):
    for j in range(i + 1, min(i + 100, n_variants)):
        r = allel.rogers_huff_r(gn[[i, j]])[0, 1] ** 2
        d = pos[j] - pos[i]
        r2.append(r)
        dist.append(d)

r2 = np.array(r2)
dist = np.array(dist)

bins = np.arange(0, 100001, 1000)
bin_means = []
for i in range(len(bins) - 1):
    mask = (dist >= bins[i]) & (dist < bins[i + 1])
    if mask.sum() > 0:
        bin_means.append(np.mean(r2[mask]))
    else:
        bin_means.append(np.nan)

plt.figure(figsize=(10, 6))
plt.plot(bins[:-1] / 1000, bin_means)
plt.xlabel('Distance (kb)')
plt.ylabel('Mean r²')
plt.title('LD Decay')
plt.savefig('ld_decay.png')
```

## Haplotype Blocks

### PLINK

```bash
# Identify haplotype blocks (Gabriel et al.)
plink --bfile data --blocks no-pheno-req --out blocks

# Output: blocks.blocks (block boundaries)
# Output: blocks.blocks.det (block details)
```

### Block Statistics

```python
import pandas as pd

blocks = pd.read_csv('blocks.blocks.det', sep='\s+')

print(f'Number of blocks: {len(blocks)}')
print(f'Mean block size: {blocks["KB"].mean():.1f} kb')
print(f'Mean SNPs per block: {blocks["NSNPS"].mean():.1f}')
```

## LD Matrix Visualization

```python
import allel
import numpy as np
import matplotlib.pyplot as plt

gn = gt.to_n_alt()[:200]

r = allel.rogers_huff_r(gn)
r2_matrix = r ** 2

plt.figure(figsize=(10, 10))
plt.imshow(r2_matrix, cmap='hot', vmin=0, vmax=1)
plt.colorbar(label='r²')
plt.xlabel('Variant index')
plt.ylabel('Variant index')
plt.title('LD Matrix')
plt.savefig('ld_matrix.png', dpi=150)
```

## LD-based Clumping (GWAS)

```bash
# Clump GWAS results by LD
plink --bfile data \
    --clump gwas_results.txt \
    --clump-p1 5e-8 \
    --clump-p2 1e-5 \
    --clump-r2 0.1 \
    --clump-kb 250 \
    --out clumped

# Output: clumped.clumped (independent signals)
```

### Clump Parameters

| Parameter | Description |
|-----------|-------------|
| --clump-p1 | Index SNP p-value threshold |
| --clump-p2 | Clumped SNP p-value threshold |
| --clump-r2 | LD threshold for clumping |
| --clump-kb | Physical distance threshold |

## vcftools LD

```bash
# Pairwise LD for region
vcftools --vcf data.vcf --geno-r2 --ld-window-bp 100000 --out ld_results

# Output: ld_results.geno.ld

# Haplotype-based r²
vcftools --vcf data.vcf --hap-r2 --ld-window-bp 100000 --out hap_ld
```

## Complete Workflow

```bash
# 1. Calculate genome-wide LD
plink2 --bfile data --r2 --ld-window-kb 500 --ld-window-r2 0.2 --out ld_genome

# 2. Generate pruned set for PCA
plink2 --bfile data --indep-pairwise 50 10 0.1 --out prune
plink2 --bfile data --extract prune.prune.in --make-bed --out pruned

# 3. Identify haplotype blocks
plink --bfile data --blocks no-pheno-req --out blocks

# 4. Visualize LD for specific region
plink --bfile data --r2 dprime --chr 6 --from-mb 28 --to-mb 34 --out mhc_ld
```

## Related Skills

- plink-basics - File format handling
- population-structure - Use pruned data for PCA
- association-testing - LD clumping for GWAS
- selection-statistics - LD affects EHH statistics
