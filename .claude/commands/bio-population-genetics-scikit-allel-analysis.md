# bio-population-genetics-scikit-allel-analysis

> Python population genetics with scikit-allel. Read VCF files, compute allele frequencies, calculate diversity statistics, perform PCA, and run selection scans using GenotypeArray and HaplotypeArray data structures. Use when analyzing population genetics in Python.

**Available tools:** Read, Bash

# scikit-allel Analysis

Python library for population genetics analysis with efficient array data structures.

## Installation

```bash
pip install scikit-allel
# Optional: zarr for chunked storage
pip install zarr
```

## Reading VCF Files

### Load VCF

```python
import allel

callset = allel.read_vcf('data.vcf.gz')

print(callset.keys())
# dict_keys(['samples', 'calldata/GT', 'variants/CHROM', 'variants/POS', 'variants/REF', 'variants/ALT', ...])

samples = callset['samples']
genotypes = callset['calldata/GT']
positions = callset['variants/POS']
chroms = callset['variants/CHROM']
```

### Specify Fields

```python
callset = allel.read_vcf('data.vcf.gz',
    fields=['samples', 'calldata/GT', 'variants/POS', 'variants/CHROM', 'variants/QUAL'])

callset = allel.read_vcf('data.vcf.gz', fields='*')  # All fields

callset = allel.read_vcf('data.vcf.gz',
    region='chr1:1000000-2000000',
    samples=['sample1', 'sample2'])
```

### Large Files (Chunked)

```python
import zarr

allel.vcf_to_zarr('large.vcf.gz', 'data.zarr', fields='*', overwrite=True)
callset = zarr.open('data.zarr', mode='r')
gt = allel.GenotypeArray(callset['calldata/GT'])
```

## Genotype Arrays

### GenotypeArray

```python
gt = allel.GenotypeArray(callset['calldata/GT'])

print(gt.shape)  # (n_variants, n_samples, ploidy)
print(gt.n_variants)
print(gt.n_samples)

print(gt[0])  # Genotypes at first variant
print(gt[:, 0])  # All variants for first sample
```

### Basic Operations

```python
ac = gt.count_alleles()
print(ac.shape)  # (n_variants, n_alleles)

af = ac.to_frequencies()
is_segregating = ac.is_segregating()
gt_filtered = gt.compress(is_segregating, axis=0)
```

### Missing Data

```python
is_called = gt.is_called()
is_missing = gt.is_missing()

miss_per_variant = (~is_called).sum(axis=1)
miss_per_sample = (~is_called).sum(axis=0)

call_rate_variant = is_called.mean(axis=1)
call_rate_sample = is_called.mean(axis=0)
```

## Allele Counts and Frequencies

```python
ac = gt.count_alleles()
ac_ref = ac[:, 0]
ac_alt = ac[:, 1]

af = ac.to_frequencies()
maf = af.min(axis=1)

n_singletons = (ac[:, 1] == 1).sum()
n_doubletons = (ac[:, 1] == 2).sum()
```

### By Population

```python
subpops = {
    'pop1': [0, 1, 2, 3, 4],
    'pop2': [5, 6, 7, 8, 9]
}

ac_subpops = gt.count_alleles_subpops(subpops)

ac_pop1 = ac_subpops['pop1']
ac_pop2 = ac_subpops['pop2']
```

## Haplotype Arrays

```python
h = gt.to_haplotypes()
print(h.shape)  # (n_variants, n_haplotypes)
print(h.n_haplotypes)

ac_hap = h.count_alleles()
```

## PCA

```python
import allel
import numpy as np

gn = gt.to_n_alt(fill=-1)
gn_filtered = gn[is_segregating]
gn_imputed = np.where(gn_filtered < 0, 0, gn_filtered)

coords, model = allel.pca(gn_imputed, n_components=10, scaler='patterson')
print(coords.shape)  # (n_samples, n_components)
```

### Plot PCA

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
plt.scatter(coords[:, 0], coords[:, 1], c=population_labels)
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.savefig('pca.png')
```

## Diversity Statistics

### Heterozygosity

```python
ho = allel.heterozygosity_observed(gt)
he = allel.heterozygosity_expected(ac, ploidy=2)

mean_ho = np.mean(ho)
mean_he = np.mean(he)
```

### Nucleotide Diversity (Pi)

```python
pi = allel.sequence_diversity(positions, ac)
print(f'Pi = {pi:.6f}')

windows = allel.moving_statistic(positions, statistic=lambda x: allel.sequence_diversity(x, ac), size=10000, step=5000)
```

### Watterson's Theta

```python
theta_w = allel.watterson_theta(positions, ac)
print(f'Theta_W = {theta_w:.6f}')
```

## Site Frequency Spectrum

```python
sfs = allel.sfs(ac[:, 1])

plt.figure(figsize=(10, 5))
allel.plot_sfs(sfs)
plt.savefig('sfs.png')
```

### Folded SFS

```python
sfs_folded = allel.sfs_folded(ac)

plt.figure(figsize=(10, 5))
allel.plot_sfs_folded(sfs_folded)
plt.savefig('sfs_folded.png')
```

## Windowed Statistics

```python
pos = np.array(positions)
windows = np.arange(0, pos.max(), 100000)

pi_windowed, windows_used, n_bases, counts = allel.windowed_diversity(pos, ac, size=100000, step=50000)

plt.figure(figsize=(14, 4))
plt.plot(windows_used[:, 0], pi_windowed)
plt.xlabel('Position')
plt.ylabel('Pi')
plt.savefig('pi_windows.png')
```

## Sample Subsetting

```python
pop1_idx = np.array([0, 1, 2, 3, 4])
pop2_idx = np.array([5, 6, 7, 8, 9])

gt_pop1 = gt.take(pop1_idx, axis=1)
gt_pop2 = gt.take(pop2_idx, axis=1)

ac_pop1 = gt_pop1.count_alleles()
ac_pop2 = gt_pop2.count_alleles()
```

## Filter Variants

```python
is_snp = callset['variants/is_snp']
is_biallelic = ac.max_allele() == 1
is_segregating = ac.is_segregating()
qual = callset['variants/QUAL']
is_high_qual = qual > 30

flt = is_snp & is_biallelic & is_segregating & is_high_qual

gt_filtered = gt.compress(flt, axis=0)
pos_filtered = positions[flt]
```

## Complete Workflow Example

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz', fields=['samples', 'calldata/GT', 'variants/POS'])
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']
samples = callset['samples']

ac = gt.count_alleles()
flt = ac.is_segregating() & (ac.max_allele() == 1)
gt = gt.compress(flt, axis=0)
pos = pos[flt]
ac = gt.count_alleles()

print(f'Variants after filtering: {gt.n_variants}')
print(f'Samples: {gt.n_samples}')
print(f'Nucleotide diversity: {allel.sequence_diversity(pos, ac):.6f}')
print(f'Mean Het observed: {allel.heterozygosity_observed(gt).mean():.4f}')

gn = gt.to_n_alt(fill=-1)
gn = np.where(gn < 0, 0, gn)
coords, model = allel.pca(gn, n_components=10, scaler='patterson')
```

## Related Skills

- selection-statistics - Fst, Tajima's D, iHS with scikit-allel
- linkage-disequilibrium - LD calculations in Python
- variant-calling/vcf-basics - VCF format and bcftools
