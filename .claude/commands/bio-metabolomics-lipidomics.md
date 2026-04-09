# bio-metabolomics-lipidomics

> Specialized lipidomics analysis for lipid identification, quantification, and pathway interpretation. Covers LC-MS lipidomics with LipidSearch, MS-DIAL, and LipidMaps annotation. Use when analyzing lipid classes, chain composition, or lipid-specific pathways.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Lipidomics Analysis

**"Analyze my lipidomics data"** → Identify and quantify lipid species by class and chain composition, then perform differential lipid analysis and pathway interpretation.
- R: `lipidr::as_lipidomics_experiment()`, `de_analysis()`
- CLI: MS-DIAL or LipidSearch for lipid identification

## R Workflow with lipidr

```r
library(lipidr)
library(ggplot2)

# Load lipidomics data (LipidSearch or Skyline format)
lipid_data <- read_lipidomes('lipidsearch_export.csv', data_type = 'LipidSearch')

# Or from generic matrix
lipid_data <- as_lipidomics_experiment(
    data = intensity_matrix,
    sample_info = sample_metadata,
    lipid_info = lipid_annotations
)

# Data summary
print(lipid_data)
plot_samples(lipid_data, type = 'tic')
```

## Lipid Annotation

```r
# Parse lipid names to extract class, chain info
lipid_data <- annotate_lipids(lipid_data)

# View lipid classes
table(rowData(lipid_data)$Class)

# Chain length and saturation
plot_chain_distribution(lipid_data)
```

## Normalization

```r
# Normalize by internal standards
lipid_data <- normalize_pqn(lipid_data)

# Or by specific internal standard class
lipid_data <- normalize_istd(lipid_data, istd_class = 'PC')

# Log transform
lipid_data <- log_transform(lipid_data)

# QC plot
plot_samples(lipid_data, type = 'boxplot')
```

## Differential Analysis

```r
# Define contrasts
de_results <- de_analysis(
    lipid_data,
    Treatment - Control,
    measure = 'Area'
)

# Significant lipids
sig_lipids <- significant_lipids(de_results, p.cutoff = 0.05, logFC.cutoff = 1)

# Volcano plot
plot_results_volcano(de_results, show.labels = TRUE)

# By lipid class
plot_results_volcano(de_results, facet = 'Class')
```

## Enrichment Analysis

```r
# Lipid class enrichment
enrich_results <- lsea(de_results, rank.by = 'logFC')

# Plot enrichment
plot_enrichment(enrich_results, significant.only = TRUE)

# Chain length enrichment
chain_enrich <- lsea(de_results, rank.by = 'logFC', type = 'chain')
```

## Python Workflow with LipidFinder

**Goal:** Identify and classify lipid species from LC-MS data using PyOpenMS and LipidMaps annotation.

**Approach:** Load mzML data, extract features from XCMS preprocessing, annotate by m/z against LipidMaps, and parse lipid nomenclature for class and chain composition.

```python
import pandas as pd
import numpy as np
from pyopenms import MSExperiment, MzMLFile

# Load mzML
exp = MSExperiment()
MzMLFile().load('lipidomics.mzML', exp)

# Extract lipid features (after XCMS preprocessing)
features = pd.read_csv('xcms_features.csv')

# LipidMaps annotation by m/z
def annotate_lipidmaps(mz, adduct='[M+H]+', tolerance_ppm=10):
    '''Query LipidMaps for lipid annotation'''
    import requests

    url = f'https://www.lipidmaps.org/rest/compound/lm_id/{mz}'
    # Note: Use local database for production
    return None  # Placeholder

# Parse lipid nomenclature
def parse_lipid_name(name):
    '''Extract lipid class and chain info from shorthand notation'''
    import re

    pattern = r'(\w+)\s*\((\d+):(\d+)(?:/(\d+):(\d+))?\)'
    match = re.match(pattern, name)

    if match:
        lipid_class = match.group(1)
        chain1_carbon = int(match.group(2))
        chain1_unsat = int(match.group(3))
        return {
            'class': lipid_class,
            'total_carbons': chain1_carbon,
            'total_unsaturation': chain1_unsat
        }
    return None

# Example
parse_lipid_name('PC(34:1)')  # {'class': 'PC', 'total_carbons': 34, 'total_unsaturation': 1}
```

## MS-DIAL Lipidomics

```r
# Load MS-DIAL alignment results
msdial_data <- read.csv('msdial_lipidomics.csv')

# Extract lipid annotations
lipid_cols <- c('Metabolite.name', 'Ontology', 'INCHIKEY', 'SMILES')
annotations <- msdial_data[, lipid_cols]

# Intensity matrix
intensity_cols <- grep('Area', colnames(msdial_data), value = TRUE)
intensities <- msdial_data[, intensity_cols]

# Filter by annotation confidence
high_conf <- msdial_data$Annotation.tag == 'Lipid'
msdial_lipids <- msdial_data[high_conf, ]
```

## Lipid Class Visualization

```r
library(ggplot2)

# Summarize by class
class_summary <- lipid_data %>%
    group_by(Class, Condition) %>%
    summarise(mean_intensity = mean(Intensity), .groups = 'drop')

# Stacked bar plot
ggplot(class_summary, aes(x = Condition, y = mean_intensity, fill = Class)) +
    geom_bar(stat = 'identity', position = 'fill') +
    scale_fill_brewer(palette = 'Set3') +
    theme_bw() +
    labs(y = 'Relative Abundance', title = 'Lipid Class Composition')
ggsave('lipid_class_composition.png', width = 8, height = 6)

# Heatmap by class
library(pheatmap)
class_matrix <- lipid_data %>%
    group_by(Class, Sample) %>%
    summarise(total = sum(Intensity), .groups = 'drop') %>%
    pivot_wider(names_from = Sample, values_from = total)

pheatmap(as.matrix(class_matrix[, -1]),
         labels_row = class_matrix$Class,
         scale = 'row',
         clustering_method = 'ward.D2')
```

## Pathway Mapping

```r
library(KEGGREST)

# Map lipids to KEGG pathways
lipid_kegg <- keggFind('compound', 'lipid')

# Glycerophospholipid metabolism
pathway_lipids <- keggGet('hsa00564')

# Or use LipidMaps classification
# Classes: FA, GL, GP, SP, ST, PR, SL, PK
```

## Saturation Analysis

```r
# Analyze saturation patterns
sat_analysis <- lipid_data %>%
    mutate(
        saturation_class = case_when(
            total_db == 0 ~ 'Saturated',
            total_db == 1 ~ 'Monounsaturated',
            TRUE ~ 'Polyunsaturated'
        )
    ) %>%
    group_by(Condition, saturation_class) %>%
    summarise(mean_abundance = mean(Intensity), .groups = 'drop')

ggplot(sat_analysis, aes(x = Condition, y = mean_abundance, fill = saturation_class)) +
    geom_bar(stat = 'identity', position = 'dodge') +
    theme_bw() +
    labs(title = 'Saturation Profile by Condition')
```

## Export Results

```r
# Comprehensive results table
results_table <- data.frame(
    Lipid = rownames(de_results),
    Class = rowData(lipid_data)$Class,
    Chain = rowData(lipid_data)$total_chain,
    logFC = de_results$logFC,
    pvalue = de_results$P.Value,
    adj_pvalue = de_results$adj.P.Val
)

write.csv(results_table, 'lipidomics_results.csv', row.names = FALSE)
```

## Related Skills

- xcms-preprocessing - Peak detection for lipidomics
- metabolite-annotation - General annotation methods
- statistical-analysis - Multivariate analysis
- pathway-mapping - Lipid pathway enrichment
