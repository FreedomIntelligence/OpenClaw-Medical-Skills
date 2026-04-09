# claw-semantic-sim

> Semantic Similarity Index for disease research literature using PubMedBERT embeddings

# 🦖 Semantic Similarity Index

Measure how isolated or connected disease research is across the global biomedical literature, using PubMedBERT embeddings on PubMed abstracts spanning 175 GBD diseases.

## What it does

1. Takes a disease list (GBD taxonomy) as input
2. Retrieves PubMed abstracts (2000-2025) for each disease with quality filtering
3. Generates 768-dimensional PubMedBERT embeddings for every abstract
4. Computes four semantic equity metrics per disease:
   - **Semantic Isolation Index (SII)**: average cosine distance to k-nearest disease neighbours; higher = more isolated, less connected research
   - **Knowledge Transfer Potential (KTP)**: cross-disease centroid similarity; higher = more potential for research spillover
   - **Research Clustering Coefficient (RCC)**: within-disease embedding variance; higher = more diverse research approaches
   - **Temporal Semantic Drift**: cosine distance between yearly centroids; measures how research focus evolves
5. Generates publication-quality multi-panel figures:
   - **Panel A**: Semantic isolation by disease category (boxplot)
   - **Panel B**: Top 20 most semantically isolated diseases (bar chart, NTD/Global South colour-coded)
   - **Panel C**: Semantic isolation vs research volume (scatter with regression)
   - **Panel D**: NTD vs non-NTD significance test (Welch's t-test, Cohen's d)
6. Produces a markdown report with all metrics, rankings, and reproducibility bundle

## Why this exists

If you ask ChatGPT to "measure research neglect for diseases," it will:
- Not know which embedding model to use for biomedical text
- Hallucinate metrics that sound plausible but have no methodological grounding
- Skip quality filtering (year coverage, abstract coverage, minimum papers)
- Not handle MPS acceleration or checkpointed batch processing
- Produce a single scatter plot with no disease classification

This skill encodes the correct methodological decisions:
- Uses PubMedBERT (the gold-standard biomedical language model)
- Fetches from PubMed with exponential backoff and NCBI rate limiting
- Quality filters: year coverage >= 70%, abstract coverage >= 95%, minimum 50 papers
- Batch embedding with Apple MPS acceleration and CPU fallback
- Checkpointed processing (resume after interruption)
- HDF5 storage with gzip compression and SHA-256 checksums
- Classification against WHO NTD list and Global South priority diseases
- Statistical significance testing (Welch's t-test, Cohen's d)

## Key Finding

Neglected tropical diseases (NTDs) are significantly more semantically isolated than other conditions (P < 0.001, Cohen's d = 0.8+). They exist in knowledge silos with limited cross-disciplinary research bridges. The 25 most isolated diseases are disproportionately Global South priority conditions.

## Pipeline

```
05-00-heim-sem-setup.py     # Validate environment, create directories
05-01-heim-sem-fetch.py     # Retrieve PubMed abstracts (checkpointed)
05-02-heim-sem-embed.py     # Generate PubMedBERT embeddings (MPS/CPU)
05-03-heim-sem-compute.py   # Compute SII, KTP, RCC, temporal drift
05-04-heim-sem-figures.py   # Generate publication figures
05-05-heim-sem-integrate.py # Merge with biobank + clinical trial dimensions
```

### Demo (works out of the box)

```bash
python semantic_sim.py --demo --output demo_report
```

The demo uses pre-computed embeddings and metrics for 175 GBD diseases and generates the full 4-panel figure instantly.

## Example Output

```
Semantic Similarity Index
=========================
Diseases analysed: 175
Total PubMed abstracts: 13,100,000
Embedding model: PubMedBERT (768-dim)

Metric Ranges:
  SII: 0.0412 - 0.1893
  KTP: 0.6234 - 0.9187
  RCC: 0.0891 - 0.3421

Key Finding:
  NTDs show +38% higher semantic isolation
  P < 0.0001, Cohen's d = 0.84
  14/25 most isolated diseases are Global South priority

Figures saved to: demo_report/
  Fig5_Semantic_Structure.png (300 dpi)
  Fig5_Semantic_Structure.pdf (vector)

Reproducibility:
  commands.sh | environment.yml | checksums.sha256
```

## Interpretation Guide

- **High SII**: Disease research exists in a knowledge silo; limited cross-disciplinary bridges
- **Low KTP**: Research on this disease has few methodological overlaps with others
- **High RCC**: Diverse research approaches within the disease (many subtopics)
- **High Temporal Drift**: Research focus has shifted significantly over time
- NTDs shown in **red**, Global South diseases in **orange**, others in **grey**
- The scatter plot (Panel C) reveals the inverse relationship between research volume and isolation

## Citation

If you use this skill in a publication, please cite:

- Corpas, M. et al. (2026). HEIM: Health Equity Index for Measuring structural bias in biomedical research. Under review.
- Corpas, M. (2026). ClawBio. https://github.com/ClawBio/ClawBio
