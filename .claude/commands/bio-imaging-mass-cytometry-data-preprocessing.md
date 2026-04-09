# bio-imaging-mass-cytometry-data-preprocessing

> Load and preprocess imaging mass cytometry (IMC) and MIBI data. Covers MCD/TIFF handling, hot pixel removal, and image normalization. Use when starting IMC analysis from raw MCD files or preparing images for segmentation.

## Version Compatibility

Reference examples tested with: anndata 0.10+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, scipy 1.12+, steinbock 0.16+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# IMC Data Preprocessing

**"Preprocess my imaging mass cytometry data"** → Load MCD files, apply hot pixel removal, channel cropping, and signal normalization to prepare multiplexed images for segmentation and analysis.
- CLI: `steinbock preprocess` for automated IMC preprocessing pipeline

## Load MCD Files with steinbock

```bash
# steinbock CLI workflow (Docker-based)
# Convert MCD to TIFF
steinbock preprocess imc \
    --mcd raw/*.mcd \
    --panel panel.csv \
    -o img

# Output: img/*.tiff (one per acquisition)
```

## Panel File Format

```csv
# panel.csv
channel,name,keep,ilastik
1,DNA1,1,1
2,CD45,1,1
3,CD3,1,0
4,CD8,1,0
5,CD4,1,0
```

## Python-Based Loading

```python
import readimc
import numpy as np
from pathlib import Path

# Read MCD file
mcd_file = Path('acquisition.mcd')
with readimc.MCDFile(mcd_file) as mcd:
    # List acquisitions
    for acquisition in mcd.acquisitions:
        print(f'Acquisition: {acquisition.id}')
        print(f'  Channels: {len(acquisition.channel_metals)}')
        print(f'  Size: {acquisition.width} x {acquisition.height}')

    # Load specific acquisition
    acq = mcd.acquisitions[0]
    img = mcd.read_acquisition(acq)  # Returns (C, H, W) array

    # Channel names
    channel_names = acq.channel_names
```

## Hot Pixel Removal

```python
from scipy import ndimage
import numpy as np

def remove_hot_pixels(img, threshold=50):
    '''Remove hot pixels using median filtering comparison'''
    filtered = ndimage.median_filter(img, size=3)
    diff = np.abs(img - filtered)
    hot_pixels = diff > threshold

    # Replace hot pixels with median
    result = img.copy()
    result[hot_pixels] = filtered[hot_pixels]

    return result

# Apply to each channel
img_clean = np.stack([remove_hot_pixels(img[c]) for c in range(img.shape[0])])
```

## Spillover Correction

**Goal:** Remove channel crosstalk caused by isotope impurities in IMC data so that each channel reflects only its intended metal target.

**Approach:** Invert the measured spillover matrix (channels x channels) and multiply each pixel's channel vector by the inverse, clipping negative values to zero.

```python
import numpy as np
import pandas as pd

def apply_spillover_correction(img, spillover_matrix):
    '''Apply spillover correction to IMC image

    spillover_matrix: (n_channels, n_channels) DataFrame or array
                      rows = measured, cols = emitting
    '''
    n_channels, height, width = img.shape

    # Reshape to (pixels, channels)
    pixels = img.reshape(n_channels, -1).T

    # Invert spillover matrix
    sm = np.array(spillover_matrix)
    sm_inv = np.linalg.inv(sm)

    # Apply correction
    corrected = pixels @ sm_inv.T
    corrected = np.clip(corrected, 0, None)  # No negative values

    # Reshape back to image
    return corrected.T.reshape(n_channels, height, width)

# Load spillover matrix (from CATALYST or manual measurement)
spillover = pd.read_csv('spillover_matrix.csv', index_col=0)
img_corrected = apply_spillover_correction(img_clean, spillover)
```

## Estimate Spillover from Single-Stain Controls

```python
def estimate_spillover(single_stains, channel_names):
    '''Estimate spillover matrix from single-stain controls'''
    n_channels = len(channel_names)
    spillover = np.eye(n_channels)

    for i, (primary_channel, control_img) in enumerate(single_stains.items()):
        primary_idx = channel_names.index(primary_channel)
        primary_signal = control_img[primary_idx].flatten()
        mask = primary_signal > np.percentile(primary_signal, 95)

        for j, ch in enumerate(channel_names):
            if i != j:
                secondary_signal = control_img[j].flatten()[mask]
                spillover[j, primary_idx] = np.median(secondary_signal / primary_signal[mask])

    return pd.DataFrame(spillover, index=channel_names, columns=channel_names)
```

## Image Normalization

```python
def percentile_normalize(img, low=1, high=99):
    '''Normalize to percentiles (per channel)'''
    normalized = np.zeros_like(img, dtype=np.float32)

    for c in range(img.shape[0]):
        channel = img[c]
        p_low = np.percentile(channel, low)
        p_high = np.percentile(channel, high)

        normalized[c] = np.clip((channel - p_low) / (p_high - p_low), 0, 1)

    return normalized

def arcsinh_transform(img, cofactor=5):
    '''Arcsinh transformation (similar to flow cytometry)'''
    return np.arcsinh(img / cofactor)

# Apply transformations
img_norm = percentile_normalize(img_clean)
img_asinh = arcsinh_transform(img_clean)
```

## steinbock Preprocessing Pipeline

```bash
# Complete preprocessing with steinbock

# 1. Extract images from MCD
steinbock preprocess imc --mcd raw/*.mcd -o img

# 2. Apply hot pixel removal
steinbock preprocess filter --img img -o img_filtered

# 3. Generate probability maps (for segmentation)
# Requires trained Ilastik classifier
steinbock classify ilastik \
    --img img_filtered \
    --ilastik-project pixel_classifier.ilp \
    -o probabilities
```

## Visualize with napari

```python
import napari
import tifffile

# Load image
img = tifffile.imread('acquisition.tiff')
channel_names = ['DNA1', 'CD45', 'CD3', 'CD8', 'CD4']

# Create viewer
viewer = napari.Viewer()

# Add channels
for i, name in enumerate(channel_names):
    viewer.add_image(img[i], name=name, colormap='gray', blending='additive')

napari.run()
```

## Create AnnData Object

```python
import anndata as ad
import pandas as pd

# After segmentation, create AnnData from single-cell data
def create_anndata(intensities, cell_info, channel_names):
    '''Create AnnData from segmented single-cell data'''

    # Intensities: cells x channels
    adata = ad.AnnData(X=intensities)

    # Channel names
    adata.var_names = channel_names

    # Cell metadata
    adata.obs = cell_info  # DataFrame with area, centroid_x, centroid_y, etc.

    return adata

# Example usage
adata = create_anndata(
    intensities=cell_intensities,  # (n_cells, n_channels)
    cell_info=cell_metadata,       # DataFrame
    channel_names=channel_names
)

adata.write('imc_data.h5ad')
```

## Batch Processing

```python
from pathlib import Path
import tifffile

def process_batch(input_dir, output_dir):
    '''Process all images in directory'''
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for img_path in input_dir.glob('*.tiff'):
        img = tifffile.imread(img_path)

        # Preprocessing
        img = np.stack([remove_hot_pixels(img[c]) for c in range(img.shape[0])])
        img = percentile_normalize(img)

        # Save
        output_path = output_dir / img_path.name
        tifffile.imwrite(output_path, img.astype(np.float32))

        print(f'Processed: {img_path.name}')

process_batch('raw_images', 'processed_images')
```

## Related Skills

- cell-segmentation - Segment preprocessed images
- spatial-transcriptomics/spatial-data-io - Similar data loading concepts
