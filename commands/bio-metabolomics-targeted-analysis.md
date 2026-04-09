# bio-metabolomics-targeted-analysis

> Targeted metabolomics analysis using MRM/SRM with standard curves. Covers absolute quantification, method validation, and quality assessment. Use when quantifying specific metabolites using calibration curves and internal standards.

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scikit-learn 1.4+, scipy 1.12+, xcms 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Targeted Metabolomics Analysis

**"Quantify specific metabolites from my MRM data"** → Perform absolute quantification using calibration curves, internal standards, and quality assessment for targeted metabolomics.
- CLI: Skyline for peak integration and export
- Python/R: calibration curve fitting and sample quantification

## Skyline Data Export Processing

```r
library(tidyverse)

# Load Skyline export
skyline_data <- read.csv('skyline_export.csv')

# Expected columns: Replicate, Peptide/Molecule, Area, Concentration (for standards)
colnames(skyline_data)

# Filter to quantifier transitions
quant_data <- skyline_data %>%
    filter(Quantitative == TRUE | is.na(Quantitative))

# Pivot to matrix format
intensity_matrix <- quant_data %>%
    select(Replicate, Molecule, Area) %>%
    pivot_wider(names_from = Replicate, values_from = Area)
```

## Standard Curve Fitting

```r
# Standard curve data
standards <- data.frame(
    concentration = c(0, 1, 5, 10, 50, 100, 500, 1000),  # nM
    area = c(100, 5000, 25000, 50000, 240000, 480000, 2300000, 4500000)
)

# Linear regression (log-log for wide range)
fit_linear <- lm(area ~ concentration, data = standards)
fit_loglog <- lm(log10(area) ~ log10(concentration + 1), data = standards)

# Weighted linear regression (1/x^2 weighting)
fit_weighted <- lm(area ~ concentration, data = standards,
                   weights = 1 / (standards$concentration + 1)^2)

# R-squared
summary(fit_linear)$r.squared
summary(fit_weighted)$r.squared

# Plot standard curve
ggplot(standards, aes(x = concentration, y = area)) +
    geom_point(size = 3) +
    geom_smooth(method = 'lm', se = TRUE) +
    scale_x_log10() +
    scale_y_log10() +
    theme_bw() +
    labs(title = 'Standard Curve', x = 'Concentration (nM)', y = 'Peak Area')
```

## Calculate Concentrations

```r
calculate_concentration <- function(area, fit, method = 'linear') {
    if (method == 'linear') {
        coef <- coef(fit)
        conc <- (area - coef[1]) / coef[2]
    } else if (method == 'loglog') {
        coef <- coef(fit)
        conc <- 10^((log10(area) - coef[1]) / coef[2]) - 1
    }
    return(pmax(conc, 0))  # No negative concentrations
}

# Apply to samples
samples <- data.frame(
    sample = paste0('Sample', 1:10),
    area = c(12000, 45000, 8000, 120000, 35000, 78000, 22000, 95000, 41000, 63000)
)

samples$concentration <- calculate_concentration(samples$area, fit_weighted)

# Account for dilution factor
dilution_factor <- 10
samples$concentration_original <- samples$concentration * dilution_factor
```

## Internal Standard Normalization

```r
# Data with internal standard
data_with_istd <- data.frame(
    sample = paste0('Sample', 1:10),
    analyte_area = c(12000, 45000, 8000, 120000, 35000, 78000, 22000, 95000, 41000, 63000),
    istd_area = c(50000, 52000, 48000, 51000, 49000, 53000, 47000, 50000, 51000, 49000)
)

# Calculate response ratio
data_with_istd$response_ratio <- data_with_istd$analyte_area / data_with_istd$istd_area

# IS-normalized concentration (using IS-corrected standard curve)
istd_conc <- 100  # nM - known ISTD concentration
data_with_istd$concentration <- calculate_concentration(
    data_with_istd$response_ratio * istd_conc,
    fit_weighted
)
```

## Method Validation Metrics

```r
# Accuracy and precision from QC samples
qc_data <- data.frame(
    level = rep(c('Low', 'Medium', 'High'), each = 6),
    nominal = rep(c(10, 100, 500), each = 6),
    measured = c(
        c(9.5, 10.2, 11.1, 9.8, 10.5, 10.0),
        c(98, 102, 95, 105, 99, 101),
        c(485, 510, 495, 520, 490, 505)
    )
)

# Calculate metrics
validation_metrics <- qc_data %>%
    group_by(level, nominal) %>%
    summarise(
        mean = mean(measured),
        sd = sd(measured),
        cv_percent = sd(measured) / mean(measured) * 100,
        accuracy_percent = mean(measured) / nominal * 100,
        bias_percent = (mean(measured) - nominal) / nominal * 100,
        .groups = 'drop'
    )

print(validation_metrics)

# Acceptance criteria
# CV < 15% (< 20% at LLOQ)
# Accuracy 85-115% (80-120% at LLOQ)
```

## Limit of Detection/Quantification

```r
# LOD/LOQ from standard curve
# LOD = 3.3 * (SD of response / slope)
# LOQ = 10 * (SD of response / slope)

# Residual standard deviation
residuals_sd <- sd(residuals(fit_weighted))
slope <- coef(fit_weighted)[2]

LOD <- 3.3 * residuals_sd / slope
LOQ <- 10 * residuals_sd / slope

cat('LOD:', round(LOD, 2), 'nM\n')
cat('LOQ:', round(LOQ, 2), 'nM\n')

# Signal-to-noise based LOD (from blank samples)
blank_areas <- c(100, 120, 95, 110, 105)
LOD_SN <- mean(blank_areas) + 3 * sd(blank_areas)
```

## Multi-Compound Analysis

```r
# Multiple analytes with individual standard curves
analytes <- c('Glucose', 'Lactate', 'Pyruvate', 'Citrate', 'Succinate')

# Store calibration curves
calibrations <- list()
for (analyte in analytes) {
    std_data <- standards_all[standards_all$analyte == analyte, ]
    calibrations[[analyte]] <- lm(area ~ concentration, data = std_data,
                                   weights = 1 / (std_data$concentration + 1)^2)
}

# Quantify all samples
quantify_sample <- function(sample_data, calibrations) {
    results <- data.frame(analyte = names(calibrations))
    results$concentration <- sapply(names(calibrations), function(a) {
        area <- sample_data$area[sample_data$analyte == a]
        calculate_concentration(area, calibrations[[a]])
    })
    return(results)
}
```

## Python Workflow

**Goal:** Perform absolute quantification of targeted metabolites from LC-MS/MRM data using weighted calibration curves and validation metrics.

**Approach:** Fit weighted linear regression to standard curve data, back-calculate sample concentrations, compute CV and accuracy metrics, and visualize results.

```python
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv('targeted_data.csv')

# Standard curve fitting
def fit_standard_curve(concentrations, areas, weighted=True):
    X = np.array(concentrations).reshape(-1, 1)
    y = np.array(areas)

    if weighted:
        weights = 1 / (np.array(concentrations) + 1)**2
        model = LinearRegression()
        model.fit(X, y, sample_weight=weights)
    else:
        model = LinearRegression()
        model.fit(X, y)

    r2 = model.score(X, y)
    return model, r2

model, r2 = fit_standard_curve(standards['concentration'], standards['area'])
print(f'R² = {r2:.4f}')

# Calculate concentrations
def calculate_conc(areas, model):
    return (np.array(areas) - model.intercept_) / model.coef_[0]

samples['concentration'] = calculate_conc(samples['area'], model)

# Validation metrics
def calc_cv(values):
    return np.std(values) / np.mean(values) * 100

def calc_accuracy(measured, nominal):
    return np.mean(measured) / nominal * 100

# Plot results
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Standard curve
axes[0].scatter(standards['concentration'], standards['area'])
x_line = np.linspace(0, max(standards['concentration']), 100)
axes[0].plot(x_line, model.predict(x_line.reshape(-1, 1)), 'r-')
axes[0].set_xlabel('Concentration')
axes[0].set_ylabel('Area')
axes[0].set_title(f'Standard Curve (R² = {r2:.4f})')

# Sample concentrations
axes[1].bar(samples['sample'], samples['concentration'])
axes[1].set_xlabel('Sample')
axes[1].set_ylabel('Concentration')
axes[1].set_title('Sample Quantification')

plt.tight_layout()
plt.savefig('targeted_results.png', dpi=150)
```

## Quality Control

```r
# QC sample tracking
qc_chart <- function(qc_values, target, warning_sd = 2, action_sd = 3) {
    mean_val <- mean(qc_values)
    sd_val <- sd(qc_values)

    ggplot(data.frame(run = 1:length(qc_values), value = qc_values)) +
        geom_point(aes(x = run, y = value), size = 3) +
        geom_line(aes(x = run, y = value)) +
        geom_hline(yintercept = target, color = 'green', linetype = 'solid') +
        geom_hline(yintercept = target + warning_sd * sd_val, color = 'orange', linetype = 'dashed') +
        geom_hline(yintercept = target - warning_sd * sd_val, color = 'orange', linetype = 'dashed') +
        geom_hline(yintercept = target + action_sd * sd_val, color = 'red', linetype = 'dashed') +
        geom_hline(yintercept = target - action_sd * sd_val, color = 'red', linetype = 'dashed') +
        theme_bw() +
        labs(title = 'QC Levey-Jennings Chart', x = 'Run', y = 'Measured Concentration')
}
```

## Export Results

```r
# Final results table
results_final <- data.frame(
    sample = samples$sample,
    concentration_nM = round(samples$concentration, 2),
    concentration_uM = round(samples$concentration / 1000, 4),
    cv_percent = round(samples$cv, 1),
    qc_flag = ifelse(samples$cv > 20, 'FAIL', 'PASS')
)

write.csv(results_final, 'targeted_results.csv', row.names = FALSE)
```

## Related Skills

- xcms-preprocessing - Peak detection for targeted features
- normalization-qc - QC-based normalization
- statistical-analysis - Group comparisons
