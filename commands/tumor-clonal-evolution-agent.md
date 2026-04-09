# tumor-clonal-evolution-agent

> AI-powered analysis of tumor clonal architecture, subclonal dynamics, and evolutionary trajectories from multi-region sequencing and longitudinal liquid biopsy data.

**Available tools:** Read, Bash

# Tumor Clonal Evolution Agent

The **Tumor Clonal Evolution Agent** analyzes intratumoral heterogeneity (ITH), reconstructs tumor phylogenies, and tracks clonal dynamics over time. It integrates multi-region sequencing data, longitudinal liquid biopsies, and mathematical modeling to predict treatment response and resistance emergence.

## When to Use This Skill

* When analyzing multi-region tumor sequencing to map spatial heterogeneity.
* To reconstruct tumor phylogenetic trees and identify ancestral mutations.
* For tracking clonal evolution through serial liquid biopsy samples.
* To predict time to treatment failure using evolutionary modeling.
* When identifying resistance-conferring subclones before clinical progression.

## Core Capabilities

1. **Clonal Deconvolution**: Identifies tumor subpopulations and estimates their cellular fractions using variant allele frequencies (VAF) from bulk sequencing.

2. **Phylogenetic Reconstruction**: Builds tumor evolutionary trees showing relationships between subclones and their mutational acquisition order.

3. **Longitudinal Tracking**: Monitors subclone dynamics over time using ctDNA variant frequencies from serial blood draws.

4. **Resistance Prediction**: Applies Bayesian evolutionary frameworks to forecast emergence of resistant clones and time to progression.

5. **Spatial ITH Mapping**: Integrates multi-region data to visualize spatial distribution of subclones across tumor sites.

6. **Fitness Estimation**: Calculates subclone fitness parameters to identify aggressive populations driving tumor progression.

## Workflow

1. **Input**: Multi-region or longitudinal mutation data (VCF/MAF), tumor purity estimates, copy number profiles.

2. **Clustering**: Cluster mutations into subclones using PyClone, SciClone, or MOBSTER.

3. **Phylogeny**: Reconstruct evolutionary trees using CITUP, PhyloWGS, or CALDER.

4. **Modeling**: Apply mathematical models (Lotka-Volterra, birth-death) to estimate dynamics.

5. **Prediction**: Forecast treatment response and resistance timeline.

6. **Output**: Phylogenetic trees, subclone trajectories, resistance predictions, actionable insights.

## Example Usage

**User**: "Analyze the clonal evolution from these 6 longitudinal ctDNA samples and predict time to progression."

**Agent Action**:
```bash
python3 Skills/Oncology/Tumor_Clonal_Evolution_Agent/clonal_evolution.py \
    --input longitudinal_ctdna_variants.maf \
    --timepoints 0,4,8,12,16,20 \
    --tumor_burden cea_values.csv \
    --method bayesian_evolution \
    --predict_ttp true \
    --output evolution_analysis/
```

## Key Methods and Algorithms

| Tool/Method | Application | Reference |
|-------------|-------------|-----------|
| PyClone-VI | Bayesian clustering of mutations | Nature Methods 2014 |
| MOBSTER | Subclonal deconvolution with selection | Nature Genetics 2020 |
| PhyloWGS | Phylogenetic tree reconstruction | Genome Biology 2015 |
| CALDER | Copy-number aware phylogeny | Nature Methods 2019 |
| CHESS | Cancer heterogeneity from single samples | Cell Systems 2019 |

## Mathematical Framework

The agent applies evolutionary dynamics models:

**Lotka-Volterra Competition**:
```
dNi/dt = ri * Ni * (1 - sum(aij * Nj) / Ki)
```

Where:
- Ni = population of subclone i
- ri = growth rate (fitness)
- aij = competition coefficient
- Ki = carrying capacity

**VAF Dynamics Modeling**:
- Serial ctDNA VAF measurements enable real-time fitness estimation
- Bayesian inference updates subclone parameters with each sample
- Monte Carlo simulations generate prediction intervals

## Prerequisites

* Python 3.10+
* PyClone-VI, PhyloWGS, or MOBSTER
* Copy number calling tools (ASCAT, Sequenza)
* Statistical modeling (PyMC, Stan)

## Related Skills

* ctDNA_Analysis - For cfDNA variant calling
* Liquid_Biopsy_Analysis - For blood-based biomarker detection
* Variant_Interpretation - For mutation annotation

## Clinical Applications

1. **Treatment Selection**: Identify dominant subclones to target
2. **Resistance Monitoring**: Detect emerging resistant populations early
3. **Prognosis**: Predict time to treatment failure
4. **Combination Therapy**: Design strategies targeting multiple subclones

## Author

AI Group - Biomedical AI Platform
