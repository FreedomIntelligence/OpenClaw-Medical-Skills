# scfoundation-model-agent

> Unified agent for leveraging single-cell foundation models (scGPT, scBERT, Geneformer, scFoundation) for cross-species annotation, perturbation prediction, and gene network inference.

**Available tools:** Read, Bash

# scFoundation Model Agent

The **scFoundation Model Agent** provides a unified interface to leverage state-of-the-art single-cell foundation models for diverse downstream tasks. It integrates scGPT, scBERT, Geneformer, scFoundation, and emerging models to enable cross-species cell annotation, in silico perturbation prediction, gene regulatory network inference, and batch integration.

## When to Use This Skill

* When annotating cell types across species (human, mouse, cross-species).
* For predicting perturbation effects (knockouts, drug treatments) in silico.
* To infer gene regulatory networks from single-cell data.
* When integrating batches without losing biological signal.
* For generating cell embeddings for downstream analysis.

## Core Capabilities

1. **Cross-Species Cell Annotation**: Transfer cell type labels across species using unified embeddings.

2. **In Silico Perturbation**: Predict gene expression changes from knockouts/treatments.

3. **Gene Regulatory Network Inference**: Discover TF-target relationships from attention patterns.

4. **Batch Integration**: Remove technical variation while preserving biology.

5. **Cell Embedding Generation**: Generate universal cell representations for any downstream task.

6. **Multi-Model Ensemble**: Combine predictions from multiple foundation models.

## Supported Foundation Models

| Model | Parameters | Training Data | Strengths |
|-------|------------|---------------|-----------|
| scGPT | 50M | 33M human cells | General purpose, perturbations |
| Geneformer | 10M | 30M cells | Chromatin, gene networks |
| scBERT | 20M | 1.2M cells | Cell type annotation |
| scFoundation | 100M | 50M cells | Large-scale, multi-species |
| scTab | 15M | 22M cells | Tabular prediction |
| UCE (Universal Cell Embeddings) | 100M | 36M cells | Cross-species transfer |

## Workflow

1. **Input**: Single-cell RNA-seq data (AnnData format).

2. **Model Selection**: Choose appropriate model(s) for task.

3. **Preprocessing**: Tokenize genes, normalize expression.

4. **Inference**: Generate embeddings or predictions.

5. **Task Execution**: Annotation, perturbation, or network inference.

6. **Ensemble (Optional)**: Combine multi-model predictions.

7. **Output**: Annotated data, predictions, networks.

## Example Usage

**User**: "Use scGPT to predict the effect of CRISPR knockout of TP53 on these cancer cells."

**Agent Action**:
```bash
python3 Skills/Genomics/scFoundation_Model_Agent/foundation_predict.py \
    --input cancer_cells.h5ad \
    --model scgpt \
    --task perturbation \
    --perturbation "TP53 knockout" \
    --model_checkpoint scgpt_human_gene_v1.pt \
    --output tp53_ko_predictions.h5ad
```

## Task-Specific Usage

### Cell Type Annotation
```bash
python3 foundation_predict.py \
    --input query_cells.h5ad \
    --model geneformer \
    --task annotation \
    --reference tabula_sapiens.h5ad \
    --output annotated_cells.h5ad
```

### Gene Network Inference
```bash
python3 foundation_predict.py \
    --input cells.h5ad \
    --model scgpt \
    --task grn_inference \
    --transcription_factors tf_list.txt \
    --output gene_network.csv
```

### Batch Integration
```bash
python3 foundation_predict.py \
    --input multi_batch.h5ad \
    --model scfoundation \
    --task integration \
    --batch_key batch \
    --output integrated.h5ad
```

## Output Formats

| Task | Output | Format |
|------|--------|--------|
| Annotation | Cell type labels | .h5ad obs column |
| Perturbation | Predicted expression | .h5ad layer |
| GRN | TF-target edges | .csv, .graphml |
| Integration | Corrected embeddings | .h5ad obsm |
| Embeddings | Cell representations | .h5ad obsm |

## Performance Benchmarks

| Task | Model | Dataset | Performance |
|------|-------|---------|-------------|
| Annotation | scGPT | Tabula Sapiens | 93% accuracy |
| Annotation | Geneformer | HLCA | 91% accuracy |
| Perturbation (R²) | scGPT | Norman 2019 | 0.87 |
| Integration (kBET) | scFoundation | Multi-atlas | 0.92 |
| Cross-species | UCE | Human→Mouse | 85% F1 |

## AI/ML Architecture

**Transformer Backbone**:
- Gene-level tokenization
- Attention-based gene interactions
- Masked expression prediction pretraining

**Perturbation Module**:
- Conditional generation
- Counterfactual prediction
- Dose-response modeling

**Transfer Learning**:
- Zero-shot annotation
- Few-shot fine-tuning
- Domain adaptation

## Prerequisites

* Python 3.10+
* PyTorch 2.0+
* transformers, flash-attn
* Scanpy, AnnData
* Model-specific weights
* GPU with 16GB+ VRAM

## Related Skills

* Nicheformer_Spatial_Agent - For spatial foundation models
* scGPT_Agent - Dedicated scGPT workflows
* Cell_Type_Annotation - Traditional annotation methods
* Pathway_Analysis - Gene set enrichment

## Model Selection Guide

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| General annotation | scGPT | Broad training, robust |
| Cross-species | UCE | Species-agnostic embeddings |
| Perturbation | scGPT | Best perturbation performance |
| GRN inference | Geneformer | Attention → regulatory links |
| Large-scale | scFoundation | Efficient, scalable |
| Tabular prediction | scTab | Optimized for classification |

## Special Considerations

1. **Gene Coverage**: Models trained on variable gene sets; check overlap
2. **Species**: Some models human-only; use UCE for cross-species
3. **Compute**: Large models need significant GPU memory
4. **Fine-Tuning**: Task-specific fine-tuning improves performance
5. **Versioning**: Model weights update frequently; track versions

## Ensemble Strategies

| Strategy | Method | Benefit |
|----------|--------|---------|
| Majority Vote | Mode of predictions | Robust to outliers |
| Weighted Average | Confidence-weighted | Leverages uncertainty |
| Stacking | Meta-model | Learns model strengths |
| Attention Fusion | Cross-model attention | Deep integration |

## Author

AI Group - Biomedical AI Platform
