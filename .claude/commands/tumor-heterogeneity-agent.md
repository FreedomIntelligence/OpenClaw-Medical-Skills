# tumor-heterogeneity-agent

> AI-powered intratumor heterogeneity analysis for clonal architecture reconstruction, subclonal evolution tracking, and therapy resistance prediction using multi-region and longitudinal sequencing.

**Available tools:** Read, Bash

# Tumor Heterogeneity Agent

The **Tumor Heterogeneity Agent** provides comprehensive analysis of intratumor heterogeneity (ITH) for understanding clonal architecture, tracking subclonal evolution, and predicting therapy resistance. It integrates multi-region sequencing, single-cell data, and longitudinal samples to reconstruct tumor phylogenies and identify actionable subclones.

## When to Use This Skill

* When analyzing multi-region tumor sequencing for clonal architecture.
* For tracking clonal evolution under treatment pressure.
* To predict resistance emergence from subclonal populations.
* When assessing tumor heterogeneity impact on treatment response.
* For integrating single-cell and bulk sequencing for ITH analysis.

## Core Capabilities

1. **Clonal Deconvolution**: Infer clonal populations and their frequencies.

2. **Phylogeny Reconstruction**: Build tumor evolutionary trees from variants.

3. **Subclonal Tracking**: Monitor subclone dynamics over time.

4. **Resistance Prediction**: Identify pre-existing resistant subclones.

5. **Multi-Region Integration**: Combine spatial heterogeneity data.

6. **Single-Cell ITH**: Integrate scDNA-seq for ground-truth clones.

## Heterogeneity Metrics

| Metric | Definition | Clinical Relevance |
|--------|------------|-------------------|
| MATH Score | Mutant-allele tumor heterogeneity | ITH quantification |
| Shannon Index | Clonal diversity | Evolutionary potential |
| Clone Count | Number of distinct clones | Complexity |
| Truncal Fraction | % truncal mutations | Targetability |
| ITH Score | Composite heterogeneity | Prognosis |

## Workflow

1. **Input**: Multi-region/longitudinal WES/WGS, copy number, tumor purity.

2. **Preprocessing**: Variant calling, CNV calling, purity estimation.

3. **CCF Estimation**: Calculate cancer cell fraction for each mutation.

4. **Clustering**: Group mutations into clonal populations.

5. **Phylogeny**: Reconstruct evolutionary tree.

6. **Temporal Analysis**: Track clone dynamics over time.

7. **Output**: Clone structures, phylogenies, heterogeneity metrics.

## Example Usage

**User**: "Analyze the clonal architecture of this multi-region lung tumor sequencing to understand heterogeneity and identify resistant subclones."

**Agent Action**:
```bash
python3 Skills/Oncology/Tumor_Heterogeneity_Agent/ith_analysis.py \
    --multi_region_vcfs region1.vcf,region2.vcf,region3.vcf \
    --cnv_segments cnv_calls.seg \
    --purity 0.7,0.65,0.72 \
    --sample_names Primary,Met1,Met2 \
    --method pyclone-vi \
    --phylogeny_method citup \
    --output ith_analysis/
```

## Deconvolution Methods

| Method | Approach | Best For |
|--------|----------|----------|
| PyClone-VI | Variational inference | Large datasets |
| SciClone | Kernel density | High purity |
| EXPANDS | Probabilistic | Multi-region |
| Canopy | EM algorithm | CNV integration |
| Clonevol | Phylogeny-aware | Longitudinal |
| CITUP | Integer programming | Tree optimization |

## Input Requirements

| Input | Format | Required |
|-------|--------|----------|
| Somatic Variants | VCF with depth | Yes |
| Copy Number | SEG file | Yes |
| Tumor Purity | Float (0-1) | Yes |
| Sample Metadata | TSV | Yes |
| Normal BAM | BAM | Recommended |

## Output Components

| Output | Description | Format |
|--------|-------------|--------|
| Clone Assignments | Mutation-to-clone mapping | .csv |
| Clone Frequencies | Per-sample clone fractions | .csv |
| Phylogenetic Tree | Newick and visualization | .nwk, .pdf |
| ITH Metrics | Heterogeneity scores | .json |
| Subclone Variants | Clone-specific mutations | .vcf |
| Evolution Plot | Clone dynamics over time | .png |
| Actionable Subclones | Druggable clone mutations | .csv |

## Clonal Classification

| Clone Type | Definition | Implications |
|------------|------------|--------------|
| Truncal | Present in all samples | Ideal targets |
| Branch | Present in subset | Regional targets |
| Private | Single sample only | Local significance |
| Resistant | Expand under therapy | Resistance mechanism |

## AI/ML Components

**Clone Inference**:
- Variational autoencoders for CCF estimation
- Dirichlet process mixture models
- Graph neural networks for phylogeny

**Resistance Prediction**:
- Time-series models for clone trajectories
- Classification of resistant signatures
- Drug-clone interaction prediction

**Multi-Region Integration**:
- Multi-task learning across regions
- Spatial models for regional patterns
- Transfer learning across cancers

## Clinical Applications

| Application | ITH Insight | Clinical Action |
|-------------|-------------|-----------------|
| Treatment Selection | Truncal vs branch targets | Prioritize truncal targets |
| Resistance Monitoring | Pre-existing resistant clones | Early combination therapy |
| Prognosis | ITH score | Risk stratification |
| Biomarker Development | Clonal biomarkers | Robust biomarker selection |

## Cancer-Specific Patterns

| Cancer Type | Typical ITH | Key Drivers |
|-------------|-------------|-------------|
| Lung (NSCLC) | High | EGFR, KRAS subclonal |
| Breast | Moderate-High | PIK3CA, ESR1 evolution |
| Colorectal | Moderate | KRAS, BRAF clonal |
| Renal | Very High | VHL truncal, diverse branches |
| Melanoma | High | BRAF/NRAS truncal |

## Prerequisites

* Python 3.10+
* PyClone-VI, SciClone
* CITUP, Clonevol
* CNVkit/FACETS for CNV
* R with clonal evolution packages

## Related Skills

* ctDNA_Dynamics_MRD_Agent - Liquid biopsy tracking
* Single_Cell_CNV_Agent - scDNA-seq analysis
* HRD_Analysis_Agent - Genomic instability
* Pan_Cancer_MultiOmics_Agent - Multi-omic integration

## Phylogeny Visualization

| View Type | Shows | Best For |
|-----------|-------|----------|
| Fish Plot | Clone dynamics over time | Longitudinal |
| Tree Diagram | Branching evolution | Multi-region |
| Muller Plot | Population dynamics | Treatment response |
| Clone Map | Spatial distribution | Multi-region spatial |

## Special Considerations

1. **Sampling Bias**: Multi-region captures more heterogeneity
2. **Purity Effects**: Low purity reduces clone resolution
3. **CNV Complexity**: High CNV burden complicates CCF
4. **Single-Cell Validation**: Ground truth from scDNA-seq
5. **Temporal Resolution**: Frequent sampling improves tracking

## Resistance Mechanisms

| Mechanism | Detection | Intervention |
|-----------|-----------|--------------|
| Pre-existing resistant clone | Subclonal at baseline | Combination therapy |
| Acquired resistance | New clone emerges | Switch therapy |
| Phenotypic plasticity | Expression change | Monitor phenotype |
| Microenvironment | TME evolution | Immunotherapy |

## Author

AI Group - Biomedical AI Platform
