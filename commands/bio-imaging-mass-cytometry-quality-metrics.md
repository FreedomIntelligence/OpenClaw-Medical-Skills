# bio-imaging-mass-cytometry-quality-metrics

> Quality metrics for IMC data including signal-to-noise, channel correlation, tissue integrity, and acquisition QC. Use when assessing data quality before analysis or troubleshooting problematic acquisitions.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Quality Metrics

**"Assess quality of my IMC acquisition"** → Evaluate IMC data quality through signal-to-noise ratios, channel correlations, tissue integrity scores, and acquisition-specific QC metrics.
- Python: `numpy`/`scipy` for SNR calculation and channel correlation analysis

## Signal-to-Noise Ratio

```python
import numpy as np
from scipy import ndimage
from skimage import io

def calculate_snr(image, mask=None):
    '''Calculate signal-to-noise ratio for an image channel.'''
    if mask is None:
        mask = image > np.percentile(image, 10)

    signal = np.mean(image[mask])
    noise = np.std(image[~mask])

    if noise == 0:
        return np.inf

    snr = signal / noise
    return snr

def calculate_snr_all_channels(image_stack, channel_names, tissue_mask=None):
    '''Calculate SNR for all channels in stack.'''
    results = {}
    for i, name in enumerate(channel_names):
        snr = calculate_snr(image_stack[i], tissue_mask)
        results[name] = snr
    return results

image_stack = io.imread('imc_image.tiff')
channel_names = ['CD45', 'CD3', 'CD68', 'panCK', 'DNA']
snr_values = calculate_snr_all_channels(image_stack, channel_names)

for ch, snr in snr_values.items():
    status = 'PASS' if snr > 3 else 'WARN' if snr > 1.5 else 'FAIL'
    print(f'{ch}: SNR = {snr:.2f} [{status}]')
```

## Channel Correlation

```python
def calculate_channel_correlation(image_stack, channel_names):
    '''Calculate pairwise correlation between channels.'''
    n_channels = image_stack.shape[0]
    flat_data = image_stack.reshape(n_channels, -1)

    corr_matrix = np.corrcoef(flat_data)

    import pandas as pd
    corr_df = pd.DataFrame(corr_matrix, index=channel_names, columns=channel_names)
    return corr_df

def flag_unexpected_correlations(corr_df, expected_pairs=None, threshold=0.7):
    '''Flag unexpected high correlations (possible spillover).'''
    issues = []

    if expected_pairs is None:
        expected_pairs = []

    for i, ch1 in enumerate(corr_df.columns):
        for j, ch2 in enumerate(corr_df.columns):
            if i >= j:
                continue

            corr = corr_df.loc[ch1, ch2]
            pair = (ch1, ch2)
            is_expected = pair in expected_pairs or (ch2, ch1) in expected_pairs

            if corr > threshold and not is_expected:
                issues.append({'channel_1': ch1, 'channel_2': ch2, 'correlation': corr, 'expected': is_expected})

    return pd.DataFrame(issues)

corr_matrix = calculate_channel_correlation(image_stack, channel_names)
print('Channel correlations:')
print(corr_matrix.round(2))

expected = [('CD3', 'CD45')]
issues = flag_unexpected_correlations(corr_matrix, expected)
if len(issues) > 0:
    print('\nUnexpected high correlations:')
    print(issues)
```

## Tissue Integrity

```python
def assess_tissue_integrity(dna_channel, min_coverage=0.3):
    '''Assess tissue coverage and integrity from DNA channel.'''
    threshold = np.percentile(dna_channel, 50)
    tissue_mask = dna_channel > threshold

    total_pixels = dna_channel.size
    tissue_pixels = np.sum(tissue_mask)
    coverage = tissue_pixels / total_pixels

    labeled, n_fragments = ndimage.label(tissue_mask)
    fragment_sizes = ndimage.sum(tissue_mask, labeled, range(1, n_fragments + 1))

    largest_fragment = np.max(fragment_sizes) if len(fragment_sizes) > 0 else 0
    fragmentation = 1 - (largest_fragment / tissue_pixels) if tissue_pixels > 0 else 1

    return {
        'coverage': coverage,
        'n_fragments': n_fragments,
        'fragmentation': fragmentation,
        'intact': coverage > min_coverage and fragmentation < 0.5
    }

dna_channel = image_stack[channel_names.index('DNA')]
integrity = assess_tissue_integrity(dna_channel)

print(f"Tissue coverage: {integrity['coverage']:.1%}")
print(f"Fragments: {integrity['n_fragments']}")
print(f"Fragmentation: {integrity['fragmentation']:.2f}")
print(f"Status: {'PASS' if integrity['intact'] else 'FAIL'}")
```

## Acquisition QC

```python
def check_acquisition_artifacts(image_stack, channel_names):
    '''Check for common acquisition artifacts.'''
    results = []

    for i, name in enumerate(channel_names):
        channel = image_stack[i]

        saturated = np.sum(channel >= channel.max() * 0.99) / channel.size
        if saturated > 0.01:
            results.append({'channel': name, 'issue': 'saturation', 'severity': saturated})

        hot_pixels = np.sum(channel > np.percentile(channel, 99.9) * 2) / channel.size
        if hot_pixels > 0.001:
            results.append({'channel': name, 'issue': 'hot_pixels', 'severity': hot_pixels})

        dead_regions = np.sum(channel == 0) / channel.size
        if dead_regions > 0.05:
            results.append({'channel': name, 'issue': 'dead_regions', 'severity': dead_regions})

        row_means = np.mean(channel, axis=1)
        row_cv = np.std(row_means) / np.mean(row_means)
        if row_cv > 0.3:
            results.append({'channel': name, 'issue': 'striping', 'severity': row_cv})

    return pd.DataFrame(results)

artifacts = check_acquisition_artifacts(image_stack, channel_names)
if len(artifacts) > 0:
    print('Artifacts detected:')
    print(artifacts)
else:
    print('No major artifacts detected')
```

## Dynamic Range

```python
def assess_dynamic_range(channel, percentiles=(1, 99)):
    '''Assess if channel uses full dynamic range.'''
    low, high = np.percentile(channel, percentiles)
    channel_range = high - low
    max_possible = channel.max()

    utilized = channel_range / max_possible if max_possible > 0 else 0

    return {
        'range_low': low,
        'range_high': high,
        'range_utilized': utilized,
        'adequate': utilized > 0.1
    }

for i, name in enumerate(channel_names):
    dr = assess_dynamic_range(image_stack[i])
    status = 'OK' if dr['adequate'] else 'LOW'
    print(f"{name}: {dr['range_utilized']:.1%} range used [{status}]")
```

## Segmentation Quality Metrics

```python
def segmentation_qc(segmentation_mask, image_stack, channel_names):
    '''QC metrics for cell segmentation.'''
    from skimage.measure import regionprops

    props = regionprops(segmentation_mask)
    n_cells = len(props)

    if n_cells == 0:
        return {'error': 'No cells found'}

    areas = [p.area for p in props]
    eccentricities = [p.eccentricity for p in props]

    area_cv = np.std(areas) / np.mean(areas)
    very_small = np.sum(np.array(areas) < np.percentile(areas, 5)) / n_cells
    very_large = np.sum(np.array(areas) > np.percentile(areas, 95)) / n_cells
    elongated = np.sum(np.array(eccentricities) > 0.9) / n_cells

    return {
        'n_cells': n_cells,
        'mean_area': np.mean(areas),
        'area_cv': area_cv,
        'pct_very_small': very_small,
        'pct_very_large': very_large,
        'pct_elongated': elongated,
        'quality': 'GOOD' if area_cv < 0.5 and elongated < 0.1 else 'REVIEW'
    }

seg_mask = io.imread('cell_segmentation.tiff')
seg_qc = segmentation_qc(seg_mask, image_stack, channel_names)
print(f"Cells: {seg_qc['n_cells']}")
print(f"Mean area: {seg_qc['mean_area']:.1f} pixels")
print(f"Quality: {seg_qc['quality']}")
```

## Batch QC Summary

**Goal:** Generate a consolidated quality report across all acquisitions in a batch to identify samples requiring re-acquisition or exclusion.

**Approach:** For each image, compute SNR, tissue integrity, segmentation metrics, and artifact counts, then aggregate into a summary table with pass/fail calls based on combined threshold criteria.

```python
def batch_qc_report(image_files, seg_files, channel_names, output_file):
    '''Generate QC report for batch of images.'''
    all_results = []

    for img_file, seg_file in zip(image_files, seg_files):
        image_stack = io.imread(img_file)
        seg_mask = io.imread(seg_file)

        result = {'sample': Path(img_file).stem}

        snr_values = calculate_snr_all_channels(image_stack, channel_names)
        result['mean_snr'] = np.mean(list(snr_values.values()))
        result['min_snr'] = min(snr_values.values())

        dna_idx = channel_names.index('DNA') if 'DNA' in channel_names else 0
        integrity = assess_tissue_integrity(image_stack[dna_idx])
        result['tissue_coverage'] = integrity['coverage']

        seg_qc = segmentation_qc(seg_mask, image_stack, channel_names)
        result['n_cells'] = seg_qc.get('n_cells', 0)

        artifacts = check_acquisition_artifacts(image_stack, channel_names)
        result['n_artifacts'] = len(artifacts)

        result['pass_qc'] = (result['min_snr'] > 1.5 and result['tissue_coverage'] > 0.3 and result['n_artifacts'] == 0)

        all_results.append(result)

    results_df = pd.DataFrame(all_results)
    results_df.to_csv(output_file, index=False)

    print(f"QC Summary: {results_df['pass_qc'].sum()}/{len(results_df)} samples passed")
    return results_df
```

## Visualization

```python
import matplotlib.pyplot as plt

def plot_qc_summary(image_stack, channel_names, output_file):
    '''Generate QC summary visualization.'''
    n_channels = len(channel_names)

    fig, axes = plt.subplots(2, n_channels, figsize=(3*n_channels, 6))

    for i, name in enumerate(channel_names):
        channel = image_stack[i]

        axes[0, i].imshow(channel, cmap='viridis')
        axes[0, i].set_title(name)
        axes[0, i].axis('off')

        axes[1, i].hist(channel.flatten(), bins=100, log=True)
        axes[1, i].set_xlabel('Intensity')
        axes[1, i].set_ylabel('Count')

    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()

plot_qc_summary(image_stack, channel_names, 'qc_summary.png')
```

## Related Skills

- data-preprocessing - Clean data before QC
- cell-segmentation - Segmentation affects QC metrics
- interactive-annotation - Manual review of QC failures
- phenotyping - Analysis after QC passes
