# bio-population-genetics-selection-statistics

> Detect signatures of natural selection using Fst, Tajima's D, iHS, XP-EHH, and other selection statistics. Calculate population differentiation, test for departures from neutrality, and identify selective sweeps with scikit-allel and vcftools. Use when computing selection signatures like Fst or Tajima's D.

**Available tools:** Read, Bash

# Selection Statistics

Detect natural selection signatures using diversity statistics and extended haplotype homozygosity.

## Fst - Population Differentiation

### scikit-allel

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']

subpops = {'pop1': [0, 1, 2, 3, 4], 'pop2': [5, 6, 7, 8, 9]}
ac_subpops = gt.count_alleles_subpops(subpops)

num, den = allel.hudson_fst(ac_subpops['pop1'], ac_subpops['pop2'])
fst_per_snp = num / den
print(f'Mean Fst: {np.nanmean(fst_per_snp):.4f}')
```

### Windowed Fst

```python
fst_windowed, windows, n_snps = allel.windowed_hudson_fst(
    pos, ac_subpops['pop1'], ac_subpops['pop2'],
    size=100000, step=50000)

import matplotlib.pyplot as plt
plt.figure(figsize=(14, 4))
plt.plot(windows[:, 0], fst_windowed)
plt.xlabel('Position')
plt.ylabel('Fst')
plt.savefig('fst_windows.png')
```

### vcftools

```bash
# Calculate Fst between populations
vcftools --vcf data.vcf --weir-fst-pop pop1.txt --weir-fst-pop pop2.txt --out fst_result

# With window
vcftools --vcf data.vcf --weir-fst-pop pop1.txt --weir-fst-pop pop2.txt \
         --fst-window-size 100000 --fst-window-step 50000 --out fst_windowed
```

## Tajima's D - Departures from Neutrality

### scikit-allel

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']
ac = gt.count_alleles()

D, windows, counts = allel.windowed_tajima_d(pos, ac, size=100000, step=50000)

plt.figure(figsize=(14, 4))
plt.plot(windows[:, 0], D)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Position')
plt.ylabel("Tajima's D")
plt.savefig('tajima_d.png')
```

### Interpretation

| D Value | Interpretation |
|---------|---------------|
| D < -2 | Recent selective sweep or population expansion |
| D ≈ 0 | Neutral evolution |
| D > 2 | Balancing selection or population bottleneck |

### vcftools

```bash
vcftools --vcf data.vcf --TajimaD 100000 --out tajima
# Output: tajima.Tajima.D (CHROM, BIN_START, N_SNPS, TajimaD)
```

## iHS - Integrated Haplotype Score

Detects ongoing selective sweeps.

```python
import allel
import numpy as np

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']
h = gt.to_haplotypes()
ac = h.count_alleles()
flt = (ac[:, 0] > 1) & (ac[:, 1] > 1)
h_flt = h.compress(flt, axis=0)
pos_flt = pos[flt]
ac_flt = ac.compress(flt, axis=0)

ihs = allel.ihs(h_flt, pos_flt, include_edges=True)
ihs_std = allel.standardize_by_allele_count(ihs, ac_flt[:, 1])

significant_ihs = np.abs(ihs_std[0]) > 2
print(f'Significant iHS hits: {significant_ihs.sum()}')
```

### Plot iHS

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 4))
plt.scatter(pos_flt, ihs_std[0], s=1)
plt.axhline(y=2, color='r', linestyle='--')
plt.axhline(y=-2, color='r', linestyle='--')
plt.xlabel('Position')
plt.ylabel('Standardized iHS')
plt.savefig('ihs.png')
```

## XP-EHH - Cross-Population Extended Haplotype Homozygosity

Detects completed sweeps by comparing populations.

```python
import allel
import numpy as np

h = gt.to_haplotypes()
h_pop1 = h.take(pop1_hap_idx, axis=1)
h_pop2 = h.take(pop2_hap_idx, axis=1)

xpehh = allel.xpehh(h_pop1, h_pop2, pos, include_edges=True)

significant = np.abs(xpehh) > 2
print(f'Significant XP-EHH hits: {significant.sum()}')
```

## NSL - Number of Segregating Sites by Length

Alternative to iHS, less sensitive to recombination rate variation.

```python
nsl = allel.nsl(h_flt)
nsl_std = allel.standardize_by_allele_count(nsl, ac_flt[:, 1])
```

## Garud's H Statistics

Detect soft sweeps.

```python
h1, h12, h123, h2_h1 = allel.garud_h(h)

h12_windowed = allel.moving_garud_h(h, size=100)
```

## Composite Selection Score

Combine multiple statistics:

```python
import numpy as np
from scipy import stats

def composite_score(fst, tajD, ihs_abs):
    fst_rank = stats.rankdata(fst) / len(fst)
    tajD_rank = stats.rankdata(-tajD) / len(tajD)  # Low Tajima's D
    ihs_rank = stats.rankdata(ihs_abs) / len(ihs_abs)
    return (fst_rank + tajD_rank + ihs_rank) / 3

css = composite_score(fst_per_snp, tajD_values, np.abs(ihs_values))
```

## Complete Selection Scan

```python
import allel
import numpy as np
import matplotlib.pyplot as plt

callset = allel.read_vcf('data.vcf.gz')
gt = allel.GenotypeArray(callset['calldata/GT'])
pos = callset['variants/POS']
ac = gt.count_alleles()

flt = ac.is_segregating() & (ac.max_allele() == 1)
gt = gt.compress(flt, axis=0)
pos = pos[flt]
ac = ac.compress(flt, axis=0)

window_size = 100000
window_step = 50000

tajD, tajD_windows, _ = allel.windowed_tajima_d(pos, ac, size=window_size, step=window_step)

pi, pi_windows, _, _ = allel.windowed_diversity(pos, ac, size=window_size, step=window_step)

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

axes[0].plot(tajD_windows[:, 0], tajD)
axes[0].axhline(0, color='r', linestyle='--')
axes[0].set_ylabel("Tajima's D")

axes[1].plot(pi_windows[:, 0], pi)
axes[1].set_ylabel('Pi')
axes[1].set_xlabel('Position')

plt.tight_layout()
plt.savefig('selection_scan.png', dpi=150)
```

## Related Skills

- scikit-allel-analysis - Data loading and basic statistics
- population-structure - Population assignment for Fst
- linkage-disequilibrium - EHH depends on LD patterns
