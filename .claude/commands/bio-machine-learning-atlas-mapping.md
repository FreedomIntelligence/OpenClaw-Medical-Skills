# bio-machine-learning-atlas-mapping

> Maps query single-cell data to reference atlases using scArches transfer learning with scVI and scANVI models. Transfers cell type labels without retraining on combined data. Use when annotating new single-cell datasets using pre-trained reference models.

**Available tools:** Read, Bash

# Transfer Learning for Single-Cell Data

## scVI Reference Mapping (scArches)

```python
import scvi
import scanpy as sc

# Load pre-trained reference model
adata_ref = sc.read_h5ad('reference.h5ad')
# Model must have been saved with save_anndata=True
scvi.model.SCVI.setup_anndata(adata_ref, layer='counts', batch_key='batch')
ref_model = scvi.model.SCVI.load('reference_model/', adata=adata_ref)

# Prepare query data
adata_query = sc.read_h5ad('query.h5ad')
# Subset to reference genes
adata_query = adata_query[:, adata_ref.var_names].copy()

# Set up query AnnData using reference setup
scvi.model.SCVI.prepare_query_anndata(adata_query, ref_model)

# Load query into model (creates "surgical" fine-tuned model)
query_model = scvi.model.SCVI.load_query_data(adata_query, ref_model)

# Surgical training: update only query-specific parameters
# weight_decay=0.0: Standard for surgery; prevents reference drift
query_model.train(max_epochs=200, plan_kwargs={'weight_decay': 0.0})

# Get latent representation
adata_query.obsm['X_scVI'] = query_model.get_latent_representation()
```

## scANVI for Label Transfer

```python
import scvi
import scanpy as sc

# Reference with cell type labels
adata_ref = sc.read_h5ad('reference_labeled.h5ad')
scvi.model.SCVI.setup_anndata(adata_ref, layer='counts', batch_key='batch')
ref_vae = scvi.model.SCVI(adata_ref, n_latent=30)
ref_vae.train(max_epochs=100)

# Convert to scANVI (semi-supervised)
scvi.model.SCANVI.setup_anndata(adata_ref, layer='counts', batch_key='batch', labels_key='cell_type', unlabeled_category='Unknown')
ref_scanvi = scvi.model.SCANVI.from_scvi_model(ref_vae, labels_key='cell_type', unlabeled_category='Unknown')
ref_scanvi.train(max_epochs=50)
ref_scanvi.save('reference_scanvi/')

# Map query data
adata_query = sc.read_h5ad('query.h5ad')
adata_query = adata_query[:, adata_ref.var_names].copy()

scvi.model.SCANVI.prepare_query_anndata(adata_query, ref_scanvi)
query_scanvi = scvi.model.SCANVI.load_query_data(adata_query, ref_scanvi)
query_scanvi.train(max_epochs=100, plan_kwargs={'weight_decay': 0.0})

# Transfer labels
adata_query.obs['predicted_cell_type'] = query_scanvi.predict()
adata_query.obsm['X_scANVI'] = query_scanvi.get_latent_representation()
```

## Prediction Confidence

```python
# Get prediction probabilities
soft_predictions = query_scanvi.predict(soft=True)
adata_query.obs['prediction_confidence'] = soft_predictions.max(axis=1)

# Flag low-confidence predictions
# confidence < 0.5: May be novel cell type or poor mapping
low_conf = adata_query.obs['prediction_confidence'] < 0.5
print(f'Low confidence predictions: {low_conf.sum()} ({low_conf.mean():.1%})')
```

## Joint Embedding Visualization

```python
import scanpy as sc

# Combine reference and query for visualization
adata_combined = adata_ref.concatenate(adata_query, batch_key='dataset', batch_categories=['reference', 'query'])

# Use latent space for neighbors/UMAP
sc.pp.neighbors(adata_combined, use_rep='X_scVI')
sc.tl.umap(adata_combined)
sc.pl.umap(adata_combined, color=['dataset', 'cell_type'], save='_transfer.png')
```

## Pre-trained Reference Atlases

| Atlas | Model | URL |
|-------|-------|-----|
| Human Lung Cell Atlas | scANVI | cellxgene.cziscience.com |
| Tabula Sapiens | scVI | tabula-sapiens-portal.ds.czbiohub.org |
| Mouse Cell Atlas | scVI | bis.zju.edu.cn/MCA |

## Training Parameters

| Parameter | Surgical | Full Retrain | Notes |
|-----------|----------|--------------|-------|
| weight_decay | 0.0 | 0.001 | 0.0 preserves reference |
| max_epochs | 100-200 | 200-400 | Less for surgery |
| early_stopping | True | True | Prevents overfitting |

## Related Skills

- single-cell/cell-annotation - Manual annotation methods
- single-cell/batch-integration - Batch effect correction
- single-cell/preprocessing - Data preparation before transfer
