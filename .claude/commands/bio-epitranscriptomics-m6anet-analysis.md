# bio-epitranscriptomics-m6anet-analysis

> Detect m6A modifications from Oxford Nanopore direct RNA sequencing using m6Anet. Use when analyzing epitranscriptomic modifications from long-read RNA data without immunoprecipitation.

**Available tools:** Read, Bash

# m6Anet Analysis

Documentation: https://m6anet.readthedocs.io/

## Data Preparation

```bash
# Basecall with Guppy (requires FAST5 files)
guppy_basecaller \
    -i fast5_dir \
    -s basecalled \
    --flowcell FLO-MIN106 \
    --kit SQK-RNA002

# Align to transcriptome
minimap2 -ax map-ont -uf transcriptome.fa reads.fastq > aligned.sam
```

## Run m6Anet

```python
from m6anet.utils import preprocess
from m6anet import run_inference

# Preprocess: extract features from FAST5
preprocess.run(
    fast5_dir='fast5_pass',
    out_dir='m6anet_data',
    reference='transcriptome.fa',
    n_processes=8
)

# Run m6A inference
run_inference.run(
    input_dir='m6anet_data',
    out_dir='m6anet_results',
    n_processes=4
)
```

## CLI Workflow

```bash
# Preprocess
m6anet dataprep \
    --input_dir fast5_pass \
    --output_dir m6anet_data \
    --reference transcriptome.fa \
    --n_processes 8

# Inference
m6anet inference \
    --input_dir m6anet_data \
    --output_dir m6anet_results \
    --n_processes 4
```

## Interpret Results

```python
import pandas as pd

results = pd.read_csv('m6anet_results/data.site_proba.csv')

# Filter high-confidence m6A sites
# probability > 0.9: High confidence threshold
m6a_sites = results[results['probability_modified'] > 0.9]
```

## Related Skills

- long-read-sequencing - ONT data processing
- m6a-peak-calling - MeRIP-seq alternative
- modification-visualization - Plot m6A sites
