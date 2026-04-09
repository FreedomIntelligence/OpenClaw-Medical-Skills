# bio-tumor-fraction-estimation

> Estimates circulating tumor DNA fraction from shallow whole-genome sequencing using ichorCNA. Detects copy number alterations via HMM segmentation and calculates ctDNA percentage. Requires 0.1-1x sWGS coverage. Use when quantifying tumor burden from liquid biopsy or monitoring treatment response.

## Version Compatibility

Reference examples tested with: CNVkit 0.9+, ichorCNA 0.5+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Tumor Fraction Estimation

**"Estimate tumor fraction from my cfDNA data"** → Calculate the proportion of tumor-derived DNA in a liquid biopsy sample using copy number aberrations from shallow whole-genome sequencing.
- R: `ichorCNA` for tumor fraction and CNA estimation from sWGS

Estimate ctDNA tumor fraction from shallow whole-genome sequencing.

## ichorCNA Overview

ichorCNA (GavinHaLab fork, v0.5.1+) detects copy number alterations and estimates tumor fraction from sWGS (0.1-1x coverage).

**Sensitivity:** 97-100% detection at >= 3% tumor fraction (2024 validation)

## Input Requirements

| Requirement | Specification |
|-------------|---------------|
| Data type | sWGS (NOT targeted panel) |
| Coverage | 0.1-1x (0.5x recommended) |
| Input | BAM files |
| Output | Tumor fraction, ploidy, CNA segments |

## Running ichorCNA

```r
library(ichorCNA)

# Step 1: Generate read counts in bins
# Run from command line or use HMMcopy
# readCounter --window 1000000 --quality 20 sample.bam > sample.wig

# Step 2: Run ichorCNA
runIchorCNA(
    WIG = 'sample.wig',
    gcWig = 'gc_hg38_1mb.wig',
    mapWig = 'mappability_hg38_1mb.wig',
    normalPanel = 'pon_median_1mb.rds',
    centromere = 'centromeres_hg38.txt',
    outDir = 'ichor_results/',
    id = 'sample_id',

    # Tumor fraction estimation parameters
    normal = c(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99),
    ploidy = c(2, 3),
    maxCN = 5,

    # Subclonality
    estimateScPrevalence = TRUE,
    scStates = c(1, 3),

    # Segmentation
    txnE = 0.9999,
    txnStrength = 10000,

    # Chromosomes
    chrs = paste0('chr', c(1:22, 'X'))
)
```

## Batch Processing

**Goal:** Run ichorCNA tumor fraction estimation on a cohort of sWGS samples in parallel, collecting results and handling failures gracefully.

**Approach:** Apply the ichorCNA pipeline to each sample's WIG file using mclapply for parallelization, wrapping each call in tryCatch to report per-sample success or failure.

```r
library(ichorCNA)
library(parallel)

process_sample <- function(wig_file, params) {
    sample_id <- basename(wig_file)
    sample_id <- gsub('.wig$', '', sample_id)

    tryCatch({
        runIchorCNA(
            WIG = wig_file,
            gcWig = params$gcWig,
            mapWig = params$mapWig,
            normalPanel = params$normalPanel,
            centromere = params$centromere,
            outDir = params$outDir,
            id = sample_id,
            normal = c(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99),
            ploidy = c(2, 3),
            maxCN = 5
        )
        return(list(sample = sample_id, status = 'success'))
    }, error = function(e) {
        return(list(sample = sample_id, status = 'failed', error = e$message))
    })
}

# Run in parallel
wig_files <- list.files('wig/', pattern = '.wig$', full.names = TRUE)
params <- list(
    gcWig = 'gc_hg38_1mb.wig',
    mapWig = 'mappability_hg38_1mb.wig',
    normalPanel = 'pon_median_1mb.rds',
    centromere = 'centromeres_hg38.txt',
    outDir = 'ichor_results/'
)

results <- mclapply(wig_files, process_sample, params = params, mc.cores = 4)
```

## Parsing Results

```r
parse_ichor_results <- function(results_dir) {
    # Find results files
    param_files <- list.files(results_dir, pattern = '.params.txt$',
                              full.names = TRUE, recursive = TRUE)

    results <- data.frame()

    for (f in param_files) {
        params <- read.table(f, header = TRUE, sep = '\t', stringsAsFactors = FALSE)
        sample_id <- gsub('.params.txt$', '', basename(f))

        results <- rbind(results, data.frame(
            sample = sample_id,
            tumor_fraction = 1 - params$n[1],  # n is normal fraction
            ploidy = params$phi[1],
            log_likelihood = params$loglik[1]
        ))
    }

    return(results)
}

# Parse all results
tf_results <- parse_ichor_results('ichor_results/')
print(tf_results)
```

## Python Wrapper

```python
import subprocess
import pandas as pd
from pathlib import Path


def run_ichorcna(wig_file, output_dir, gc_wig, map_wig, normal_panel, centromere):
    '''Run ichorCNA from Python.'''
    sample_id = Path(wig_file).stem

    cmd = f'''
    Rscript -e "
    library(ichorCNA)
    runIchorCNA(
        WIG = '{wig_file}',
        gcWig = '{gc_wig}',
        mapWig = '{map_wig}',
        normalPanel = '{normal_panel}',
        centromere = '{centromere}',
        outDir = '{output_dir}',
        id = '{sample_id}',
        normal = c(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99),
        ploidy = c(2, 3),
        maxCN = 5
    )
    "
    '''

    subprocess.run(cmd, shell=True, check=True)


def parse_tumor_fraction(params_file):
    '''Parse tumor fraction from ichorCNA output.'''
    df = pd.read_csv(params_file, sep='\t')
    return {
        'tumor_fraction': 1 - df['n'].iloc[0],
        'ploidy': df['phi'].iloc[0],
        'log_likelihood': df['loglik'].iloc[0]
    }
```

## Interpretation

| Tumor Fraction | Interpretation |
|----------------|----------------|
| >= 10% | High ctDNA, reliable detection |
| 3-10% | Moderate ctDNA, detectable |
| < 3% | Low ctDNA, at detection limit |
| 0% | No detectable ctDNA or below LOD |

## Related Skills

- cfdna-preprocessing - Preprocess BAMs before ichorCNA
- fragment-analysis - Complementary fragmentomics analysis
- ctdna-mutation-detection - Mutation detection from panel data
- copy-number/cnvkit-analysis - CNV concepts
