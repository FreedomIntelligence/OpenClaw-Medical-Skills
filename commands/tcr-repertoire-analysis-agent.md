# tcr-repertoire-analysis-agent

> AI-powered T-cell receptor repertoire analysis for cancer diagnosis, immunotherapy response prediction, and therapeutic TCR selection using deep learning and multi-layer ML approaches.

**Available tools:** Read, Bash

# TCR Repertoire Analysis Agent

The **TCR Repertoire Analysis Agent** provides comprehensive T-cell receptor repertoire analysis for cancer immunology applications. It leverages deep learning and multi-layer machine learning approaches to analyze TCR diversity, predict immunotherapy response, identify tumor-reactive TCRs, and support therapeutic TCR selection for cancer immunotherapy.

## When to Use This Skill

* When analyzing TCR repertoire for cancer diagnosis and staging.
* For predicting immunotherapy (anti-PD-1/PD-L1) response from TCR profiles.
* To identify tumor-reactive TCRs for adoptive cell therapy.
* When monitoring treatment response through TCR clonality changes.
* For selecting therapeutic TCRs for TCR-T cell therapy development.

## Core Capabilities

1. **Repertoire Diversity Analysis**: Quantify TCR diversity, clonality, and convergence.

2. **Cancer Diagnosis**: Distinguish cancer types from TCR signatures.

3. **Immunotherapy Response Prediction**: Predict checkpoint inhibitor response.

4. **Tumor-Reactive TCR Identification**: Find neoantigen-specific TCRs.

5. **TCR-pMHC Binding Prediction**: Predict TCR epitope specificity.

6. **Clonal Dynamics Tracking**: Monitor TCR clones during treatment.

## TCR Repertoire Metrics

| Metric | Definition | Clinical Significance |
|--------|------------|----------------------|
| Clonality | Gini coefficient of clone sizes | Immune focusing |
| Shannon Entropy | Diversity measure | Immune breadth |
| Richness | Unique clonotypes | Repertoire depth |
| Top Clone % | Largest clone fraction | Dominant response |
| Convergent TCRs | Shared across patients | Public epitope response |
| Tumor-Infiltrating % | TIL-derived TCRs | Tumor reactivity |

## Workflow

1. **Input**: TCR-seq data (bulk or single-cell), clinical metadata.

2. **Preprocessing**: CDR3 extraction, error correction, clustering.

3. **Repertoire Analysis**: Calculate diversity, clonality, convergence.

4. **ML Classification**: Cancer type, stage, response prediction.

5. **TCR Prioritization**: Rank tumor-reactive TCR candidates.

6. **TCR-pMHC Prediction**: Predict epitope specificity.

7. **Output**: Repertoire metrics, predictions, therapeutic candidates.

## Example Usage

**User**: "Analyze the TCR repertoire from this melanoma patient's tumor and blood to predict immunotherapy response and identify tumor-reactive TCRs."

**Agent Action**:
```bash
python3 Skills/Immunology_Vaccines/TCR_Repertoire_Analysis_Agent/tcr_repertoire_analysis.py \
    --tumor_tcr tumor_tils.tsv \
    --blood_tcr pbmc_tcrs.tsv \
    --cancer_type melanoma \
    --hla_type HLA-A*02:01,HLA-B*07:02 \
    --neoantigens patient_neoantigens.fasta \
    --task response_prediction,tcr_identification \
    --output tcr_analysis/
```

## Input Formats

| Format | Source | Fields |
|--------|--------|--------|
| AIRR-seq | Standardized | CDR3, V/J genes, count |
| MiXCR | MiXCR pipeline | Clone info, counts |
| 10x VDJ | Single-cell | CDR3, cell barcode |
| Custom TSV | Any pipeline | Flexible mapping |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Repertoire Metrics | Diversity scores | .json |
| Response Prediction | Immunotherapy probability | .json |
| Cancer Classification | Type/stage prediction | .json |
| Tumor-Reactive TCRs | Ranked candidates | .csv |
| TCR-pMHC Predictions | Epitope specificity | .csv |
| Clonal Tracking | Dynamics over time | .csv |
| Visualizations | Repertoire plots | .png, .pdf |

## Response Prediction Features

| Feature Category | Features | Importance |
|------------------|----------|------------|
| Diversity | Shannon, Gini, richness | High |
| Clonality | Top clones, expansion | High |
| Convergence | Public TCRs, sharing | Moderate |
| Sequence Features | CDR3 length, motifs | Moderate |
| TIL Characteristics | TIL fraction, phenotype | High |

## AI/ML Components

**Cancer Classification**:
- Multi-layer ensemble (XGBoost, RF, SVM)
- TCR embedding networks
- Attention-based sequence models

**Response Prediction**:
- Cox regression with TCR features
- Deep survival analysis
- Multi-task learning (response + survival)

**TCR-pMHC Prediction**:
- AlphaFold3-based structural prediction
- Transformer models (TCR-BERT)
- Contrastive learning embeddings

## Clinical Applications

| Application | TCR Biomarker | Clinical Utility |
|-------------|---------------|------------------|
| Diagnosis | Cancer-specific TCRs | Early detection |
| Staging | Clonality patterns | Disease extent |
| Prognosis | Intratumoral diversity | Survival prediction |
| Response | Baseline clonality | IO response |
| Monitoring | Clone dynamics | Treatment tracking |
| Therapy | Tumor-reactive TCRs | TCR-T development |

## Performance Benchmarks

| Task | Dataset | Performance |
|------|---------|-------------|
| Cancer vs Normal | Digestive cancers | AUC 0.91 |
| Metastasis Detection | CRC | AUC 0.85 |
| IO Response | Melanoma | AUC 0.78 |
| TCR-pMHC Prediction | IEDB benchmark | AUC 0.82 |

## Prerequisites

* Python 3.10+
* MiXCR, TRUST4 for TCR calling
* immunarch, tcrdist3
* PyTorch, transformers
* AlphaFold3 (optional, for structure)

## Related Skills

* TCR_pMHC_Prediction_Agent - Detailed TCR-epitope prediction
* Neoantigen_Prediction_Agent - Neoantigen identification
* TME_Immune_Profiling_Agent - Broader immune context
* TCell_Exhaustion_Analysis_Agent - T cell phenotyping

## TCR Sequence Analysis

| CDR3 Feature | Analysis | Meaning |
|--------------|----------|---------|
| Length Distribution | Histogram | V(D)J usage |
| Amino Acid Usage | Positional frequency | Binding properties |
| Hydrophobicity | CDR3 profile | MHC interaction |
| Charge | Net charge | Peptide binding |
| Motif Enrichment | k-mer analysis | Epitope specificity |

## Therapeutic TCR Selection Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Tumor Enrichment | >10-fold vs blood | Tumor specificity |
| Clone Size | Top 1% in tumor | Functional expansion |
| Neoantigen Binding | Predicted positive | Target specificity |
| Safety (Cross-react) | No self-peptide hits | Safety |
| HLA Restriction | Common alleles | Broad applicability |

## Special Considerations

1. **Sample Quality**: Fresh samples preferred for TIL analysis
2. **Sequencing Depth**: Sufficient depth for rare clones
3. **Batch Effects**: Normalize across sequencing runs
4. **HLA Context**: TCR analysis requires HLA typing
5. **Paired Chains**: Single-cell for alpha-beta pairing

## Cancer-Specific TCR Signatures

| Cancer Type | Key TCR Features | Public TCRs |
|-------------|------------------|-------------|
| Melanoma | High clonality, MAA-reactive | Yes |
| NSCLC | Moderate diversity | Limited |
| CRC-MSI | Neoantigen-reactive | Variable |
| HPV+ HNSCC | HPV-E6/E7 reactive | Yes |

## Author

AI Group - Biomedical AI Platform
