# bio-imaging-mass-cytometry-interactive-annotation

> Interactive cell type annotation for IMC data. Covers napari-based annotation, marker-guided labeling, training data generation, and annotation validation. Use when manually annotating cell types for training classifiers or validating automated phenotyping results.

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Interactive Annotation

**"Manually annotate cell types in my IMC data"** → Interactively label cells using napari visualization with marker overlays for training classifiers or validating automated phenotyping results.
- Python: `napari.Viewer()` with label layer for interactive annotation

## Napari-Based Annotation

```python
import napari
import numpy as np
from skimage import io
import pandas as pd

# Load IMC image stack
image_stack = io.imread('imc_image.tiff')  # (C, H, W)
segmentation_mask = io.imread('cell_segmentation.tiff')

# Create napari viewer
viewer = napari.Viewer()

# Add channels as separate layers for visualization
channel_names = ['CD45', 'CD3', 'CD68', 'panCK', 'DNA']
for i, name in enumerate(channel_names):
    viewer.add_image(image_stack[i], name=name, visible=False, colormap='gray', blending='additive')

# Add segmentation
viewer.add_labels(segmentation_mask, name='Cells')

# Add annotation layer (start empty)
annotation_layer = viewer.add_labels(
    np.zeros_like(segmentation_mask),
    name='Cell_Types'
)

# Define cell types
cell_type_mapping = {1: 'T_cell', 2: 'Macrophage', 3: 'Epithelial', 4: 'Stromal', 5: 'Other'}
```

## Marker-Guided Annotation

```python
def create_marker_overlay(image_stack, channel_indices, colors):
    '''Create RGB overlay of selected markers for easier annotation.'''
    h, w = image_stack.shape[1:]
    overlay = np.zeros((h, w, 3), dtype=np.float32)

    for idx, color in zip(channel_indices, colors):
        channel = image_stack[idx].astype(np.float32)
        channel = (channel - channel.min()) / (channel.max() - channel.min() + 1e-8)
        for c, weight in enumerate(color):
            overlay[:, :, c] += channel * weight

    overlay = np.clip(overlay, 0, 1)
    return overlay

# Create T cell overlay (CD3=green, CD45=blue)
t_cell_overlay = create_marker_overlay(
    image_stack,
    channel_indices=[0, 1],  # CD45, CD3
    colors=[[0, 0, 1], [0, 1, 0]]  # Blue, Green
)

# Create tumor overlay (panCK=red)
tumor_overlay = create_marker_overlay(
    image_stack,
    channel_indices=[3],  # panCK
    colors=[[1, 0, 0]]  # Red
)

# Add overlays to viewer
viewer.add_image(t_cell_overlay, name='T_cell_markers', visible=True)
viewer.add_image(tumor_overlay, name='Tumor_markers', visible=False)
```

## Training Data Generation

```python
def extract_training_data(image_stack, segmentation_mask, annotation_mask, channel_names):
    '''Extract mean marker intensities per cell with annotations.'''
    from skimage.measure import regionprops_table

    cells = []
    for cell_id in np.unique(segmentation_mask):
        if cell_id == 0:
            continue

        cell_mask = segmentation_mask == cell_id
        annotation = annotation_mask[cell_mask]
        annotation = annotation[annotation > 0]

        if len(annotation) == 0:
            continue

        cell_type = int(np.median(annotation))

        cell_data = {'cell_id': cell_id, 'cell_type': cell_type}
        for i, name in enumerate(channel_names):
            cell_data[name] = np.mean(image_stack[i][cell_mask])

        cells.append(cell_data)

    return pd.DataFrame(cells)

# After manual annotation in napari
annotation_data = annotation_layer.data
training_df = extract_training_data(image_stack, segmentation_mask, annotation_data, channel_names)
training_df.to_csv('training_annotations.csv', index=False)
print(f'Annotated {len(training_df)} cells')
print(training_df['cell_type'].value_counts())
```

## Semi-Automated Annotation

**Goal:** Propagate a small set of manual cell type annotations to all unannotated cells using marker expression similarity.

**Approach:** Train a k-nearest-neighbors classifier on manually annotated cells' marker intensities, predict labels for remaining cells, and report classification confidence to flag uncertain assignments for review.

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

def propagate_annotations(training_df, all_cells_df, marker_columns):
    '''Use annotated cells to classify unannotated cells.'''
    X_train = training_df[marker_columns].values
    y_train = training_df['cell_type'].values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train_scaled, y_train)

    unannotated = all_cells_df[~all_cells_df['cell_id'].isin(training_df['cell_id'])]
    X_test = scaler.transform(unannotated[marker_columns].values)

    predictions = knn.predict(X_test)
    probabilities = knn.predict_proba(X_test)
    confidence = np.max(probabilities, axis=1)

    unannotated = unannotated.copy()
    unannotated['predicted_type'] = predictions
    unannotated['confidence'] = confidence

    return unannotated

marker_cols = ['CD45', 'CD3', 'CD68', 'panCK']
predictions = propagate_annotations(training_df, all_cells_df, marker_cols)

high_conf = predictions[predictions['confidence'] > 0.8]
print(f'{len(high_conf)} cells classified with high confidence')
```

## Annotation Validation

```python
def validate_annotations(annotation_df, image_stack, segmentation_mask, channel_names, output_dir):
    '''Generate validation plots for manual review.'''
    import matplotlib.pyplot as plt
    from pathlib import Path

    Path(output_dir).mkdir(exist_ok=True)

    cell_types = annotation_df['cell_type'].unique()

    for ct in cell_types:
        cells = annotation_df[annotation_df['cell_type'] == ct]
        n_sample = min(20, len(cells))
        sample_cells = cells.sample(n_sample)

        fig, axes = plt.subplots(n_sample, len(channel_names), figsize=(2*len(channel_names), 2*n_sample))

        for i, (_, cell) in enumerate(sample_cells.iterrows()):
            cell_mask = segmentation_mask == cell['cell_id']
            bbox = get_bounding_box(cell_mask, padding=10)

            for j, ch_name in enumerate(channel_names):
                ax = axes[i, j] if n_sample > 1 else axes[j]
                crop = image_stack[j][bbox[0]:bbox[1], bbox[2]:bbox[3]]
                ax.imshow(crop, cmap='gray')
                ax.axis('off')
                if i == 0:
                    ax.set_title(ch_name)

        plt.suptitle(f'Cell Type: {ct} (n={len(cells)})')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/validation_type_{ct}.png', dpi=150)
        plt.close()

def get_bounding_box(mask, padding=10):
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin = max(0, rmin - padding)
    cmin = max(0, cmin - padding)
    rmax = min(mask.shape[0], rmax + padding)
    cmax = min(mask.shape[1], cmax + padding)
    return rmin, rmax, cmin, cmax

validate_annotations(training_df, image_stack, segmentation_mask, channel_names, 'validation/')
```

## Napari Plugin Interface

```python
from magicgui import magicgui
from napari.types import LabelsData

@magicgui(call_button='Apply Annotation')
def annotate_selected(viewer: napari.Viewer, cell_type: int = 1):
    '''Annotate selected cells with specified type.'''
    labels_layer = viewer.layers['Cells']
    annotation_layer = viewer.layers['Cell_Types']

    selected = labels_layer.selected_label
    if selected > 0:
        mask = labels_layer.data == selected
        annotation_layer.data[mask] = cell_type
        annotation_layer.refresh()
        print(f'Annotated cell {selected} as type {cell_type}')

@magicgui(call_button='Export Annotations')
def export_annotations(viewer: napari.Viewer, filename: str = 'annotations.csv'):
    '''Export current annotations to CSV.'''
    annotation_layer = viewer.layers['Cell_Types']
    segmentation_layer = viewer.layers['Cells']

    annotations = []
    for cell_id in np.unique(segmentation_layer.data):
        if cell_id == 0:
            continue
        cell_mask = segmentation_layer.data == cell_id
        cell_type = annotation_layer.data[cell_mask]
        cell_type = cell_type[cell_type > 0]
        if len(cell_type) > 0:
            annotations.append({'cell_id': cell_id, 'cell_type': int(np.median(cell_type))})

    pd.DataFrame(annotations).to_csv(filename, index=False)
    print(f'Exported {len(annotations)} annotations to {filename}')

# Add widgets to viewer
viewer.window.add_dock_widget(annotate_selected)
viewer.window.add_dock_widget(export_annotations)
```

## Batch Annotation Workflow

```python
def batch_annotation_session(image_files, seg_files, existing_annotations=None):
    '''Set up batch annotation session for multiple images.'''
    viewer = napari.Viewer()

    all_annotations = existing_annotations or {}

    for img_file, seg_file in zip(image_files, seg_files):
        image_stack = io.imread(img_file)
        seg_mask = io.imread(seg_file)

        sample_name = Path(img_file).stem

        for layer in list(viewer.layers):
            viewer.layers.remove(layer)

        for i, name in enumerate(channel_names):
            viewer.add_image(image_stack[i], name=name, visible=False)

        viewer.add_labels(seg_mask, name='Cells')

        if sample_name in all_annotations:
            viewer.add_labels(all_annotations[sample_name], name='Cell_Types')
        else:
            viewer.add_labels(np.zeros_like(seg_mask), name='Cell_Types')

        viewer.title = f'Annotating: {sample_name}'
        input('Press Enter when done annotating this image...')

        all_annotations[sample_name] = viewer.layers['Cell_Types'].data.copy()

    return all_annotations
```

## Related Skills

- cell-segmentation - Generate cell masks for annotation
- phenotyping - Automated phenotyping as alternative
- spatial-analysis - Use annotations for spatial analysis
- quality-metrics - QC annotated data
