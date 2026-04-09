# tooluniverse-image-analysis

> Production-ready microscopy image analysis and quantitative imaging data skill for colony morphometry, cell counting, fluorescence quantification, and statistical analysis of imaging-derived measurements. Processes ImageJ/CellProfiler output (area, circularity, intensity, cell counts), performs Dunnett's test, Cohen's d effect size, power analysis, Shapiro-Wilk normality tests, two-way ANOVA, polynomial regression, natural spline regression with confidence intervals, and comparative morphometry. Supports CSV/TSV measurement tables, multi-channel fluorescence data, colony swarming assays, and neuron counting datasets. Use when analyzing microscopy measurement data, colony area/circularity, cell count statistics, swarming assays, co-culture ratio optimization, or answering questions about imaging-derived quantitative data.

# Microscopy Image Analysis and Quantitative Imaging Data

Production-ready skill for analyzing microscopy-derived measurement data using pandas, numpy, scipy, statsmodels, and scikit-image. Designed for BixBench imaging questions covering colony morphometry, cell counting, fluorescence quantification, regression modeling, and statistical comparisons.

**IMPORTANT**: This skill handles complex multi-workflow analysis. Most implementation details have been moved to `references/` for progressive disclosure. This document focuses on high-level decision-making and workflow orchestration.

---

## When to Use This Skill

Apply when users:
- Have microscopy measurement data (area, circularity, intensity, cell counts) in CSV/TSV
- Ask about colony morphometry (bacterial swarming, biofilm, growth assays)
- Need statistical comparisons of imaging measurements (t-test, ANOVA, Dunnett's, Mann-Whitney)
- Ask about cell counting statistics (NeuN, DAPI, marker counts)
- Need effect size calculations (Cohen's d) and power analysis
- Want regression models (polynomial, spline) fitted to dose-response or ratio data
- Ask about model comparison (R-squared, F-statistic, AIC/BIC)
- Need Shapiro-Wilk normality testing on imaging data
- Want confidence intervals for peak predictions from fitted models
- Questions mention imaging software output (ImageJ, CellProfiler, QuPath)
- Need fluorescence intensity quantification or colocalization analysis
- Ask about image segmentation results (counts, areas, shapes)

**BixBench Coverage**: 21 questions across 4 projects (bix-18, bix-19, bix-41, bix-54)

**NOT for** (use other skills instead):
- Phylogenetic analysis → Use `tooluniverse-phylogenetics`
- RNA-seq differential expression → Use `tooluniverse-rnaseq-deseq2`
- Single-cell scRNA-seq → Use `tooluniverse-single-cell`
- Statistical regression only (no imaging context) → Use `tooluniverse-statistical-modeling`

---

## Core Principles

1. **Data-first approach** - Load and inspect all CSV/TSV measurement data before analysis
2. **Question-driven** - Parse the exact statistic, comparison, or model requested
3. **Statistical rigor** - Proper effect sizes, multiple comparison corrections, model selection
4. **Imaging-aware** - Understand ImageJ/CellProfiler measurement columns (Area, Circularity, Round, Intensity)
5. **Workflow flexibility** - Support both pre-quantified data (CSV) and raw image processing
6. **Precision** - Match expected answer format (integer, range, decimal places)
7. **Reproducible** - Use standard Python/scipy equivalents to R functions

---

## Required Python Packages

```python
# Core (MUST be installed)
import pandas as pd
import numpy as np
from scipy import stats
from scipy.interpolate import BSpline, make_interp_spline
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.power import TTestIndPower
from patsy import dmatrix, bs, cr

# Optional (for raw image processing)
import skimage
import cv2
import tifffile
```

**Installation**:
```bash
pip install pandas numpy scipy statsmodels patsy scikit-image opencv-python-headless tifffile
```

---

## High-Level Workflow Decision Tree

```
START: User question about microscopy data
│
├─ Q1: What type of data is available?
│  │
│  ├─ PRE-QUANTIFIED DATA (CSV/TSV with measurements)
│  │  └─ Workflow: Load → Parse question → Statistical analysis
│  │     Pattern: Most common BixBench pattern (bix-18, bix-19, bix-41, bix-54)
│  │     See: Section "Quantitative Data Analysis" below
│  │
│  └─ RAW IMAGES (TIFF, PNG, multi-channel)
│     └─ Workflow: Load → Segment → Measure → Analyze
│        See: references/image_processing.md
│
├─ Q2: What type of analysis is needed?
│  │
│  ├─ STATISTICAL COMPARISON
│  │  ├─ Two groups → t-test or Mann-Whitney
│  │  ├─ Multiple groups → ANOVA or Dunnett's test
│  │  ├─ Two factors → Two-way ANOVA
│  │  └─ Effect size → Cohen's d, power analysis
│  │  See: references/statistical_analysis.md
│  │
│  ├─ REGRESSION MODELING
│  │  ├─ Dose-response → Polynomial (quadratic, cubic)
│  │  ├─ Ratio optimization → Natural spline
│  │  └─ Model comparison → R-squared, F-statistic, AIC/BIC
│  │  See: references/statistical_analysis.md
│  │
│  ├─ CELL COUNTING
│  │  ├─ Fluorescence (DAPI, NeuN) → Threshold + watershed
│  │  ├─ Brightfield → Adaptive threshold
│  │  └─ High-density → CellPose or StarDist (external)
│  │  See: references/cell_counting.md
│  │
│  ├─ COLONY SEGMENTATION
│  │  ├─ Swarming assays → Otsu threshold + morphology
│  │  ├─ Biofilms → Li threshold + fill holes
│  │  └─ Growth assays → Time-lapse tracking
│  │  See: references/segmentation.md
│  │
│  └─ FLUORESCENCE QUANTIFICATION
│     ├─ Intensity measurement → regionprops
│     ├─ Colocalization → Pearson/Manders
│     └─ Multi-channel → Channel-wise quantification
│     See: references/fluorescence_analysis.md
│
└─ Q3: When to use scikit-image vs OpenCV?
   ├─ scikit-image: Scientific analysis, measurements, regionprops
   ├─ OpenCV: Fast processing, real-time, large batches
   └─ Both: Often interchangeable for basic operations
   See: references/image_processing.md "Library Selection Guide"
```

---

## Quantitative Data Analysis Workflow

### Phase 0: Question Parsing and Data Discovery

**CRITICAL FIRST STEP**: Before writing ANY code, identify what data files are available and what the question is asking for.

```python
import os, glob, pandas as pd

# Discover data files
data_dir = "."
csv_files = glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True)
tsv_files = glob.glob(os.path.join(data_dir, '**', '*.tsv'), recursive=True)
img_files = glob.glob(os.path.join(data_dir, '**', '*.tif*'), recursive=True)

# Load and inspect first measurement file
if csv_files:
    df = pd.read_csv(csv_files[0])
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df.head())
    print(df.describe())
```

**Common Column Names**:
- Area: Colony or cell area in pixels or calibrated units
- Circularity: 4*pi*area/perimeter^2, range [0,1], 1.0 = perfect circle
- Round: Roundness = 4*area/(pi*major_axis^2)
- Genotype/Strain: Biological grouping variable
- Ratio: Co-culture mixing ratio (e.g., "1:3", "5:1")
- NeuN/DAPI/GFP: Cell marker counts or intensities

### Phase 1: Grouped Statistics

```python
def grouped_summary(df, group_cols, measure_col):
    """Calculate summary statistics by group."""
    summary = df.groupby(group_cols)[measure_col].agg(
        Mean='mean',
        SD='std',
        Median='median',
        Min='min',
        Max='max',
        N='count'
    ).reset_index()
    summary['SEM'] = summary['SD'] / np.sqrt(summary['N'])
    return summary

# Example: Colony morphometry by genotype
area_summary = grouped_summary(df, 'Genotype', 'Area')
circ_summary = grouped_summary(df, 'Genotype', 'Circularity')
```

For detailed statistical functions, see: **references/statistical_analysis.md**

### Phase 2: Statistical Testing

**Decision guide**:
- Normality test needed? → Shapiro-Wilk
- Two groups comparison? → t-test or Mann-Whitney
- Multiple groups vs control? → Dunnett's test
- Multiple groups, all comparisons? → Tukey HSD
- Two factors? → Two-way ANOVA
- Effect size? → Cohen's d
- Sample size planning? → Power analysis

See: **references/statistical_analysis.md** for complete implementations

### Phase 3: Regression Modeling

**When to use each model**:
- Polynomial (quadratic/cubic): Smooth dose-response, clear peak
- Natural spline: Flexible, non-parametric, handles complex patterns
- Linear: Simple relationships, checking for trends

Model comparison metrics:
- R-squared: Overall fit (higher = better)
- Adjusted R-squared: Penalizes complexity
- F-statistic p-value: Model significance
- AIC/BIC: Compare non-nested models

See: **references/statistical_analysis.md** for complete implementations

---

## Raw Image Processing Workflow

### When Processing Raw Images

**Workflow**: Load → Preprocess → Segment → Measure → Export

```python
# Quick start for cell counting
from scripts.segment_cells import count_cells_in_image

result = count_cells_in_image(
    image_path="cells.tif",
    channel=0,  # DAPI channel
    min_area=50
)
print(f"Found {result['count']} cells")
```

### Segmentation Method Selection

**Decision guide**:

| Cell Type | Density | Best Method | Notes |
|-----------|---------|-------------|-------|
| **Nuclei (DAPI)** | Low-Medium | Otsu + watershed | Standard approach |
| **Nuclei (DAPI)** | High | CellPose/StarDist | Handles touching |
| **Colonies** | Well-separated | Otsu threshold | Fast, reliable |
| **Colonies** | Touching | Watershed | Edge detection |
| **Cells (phase)** | Any | Adaptive threshold | Handles uneven illumination |
| **Fluorescence** | Low signal | Li threshold | More sensitive |

See: **references/segmentation.md** and **references/cell_counting.md** for detailed protocols

### Library Selection: scikit-image vs OpenCV

**Use scikit-image when**:
- Scientific measurements needed (area, perimeter, intensity)
- regionprops for object properties
- Publication-quality analysis
- Easier syntax for scientists

**Use OpenCV when**:
- Processing large image batches
- Speed is critical
- Real-time processing
- Advanced computer vision features

**Both work for**:
- Thresholding, filtering, morphological operations
- Basic image transformations
- Most segmentation tasks

See: **references/image_processing.md** "Library Selection Guide"

---

## Common BixBench Patterns

### Pattern 1: Colony Morphometry (bix-18)

**Question type**: "Mean circularity of genotype with largest area?"

**Data**: CSV with Genotype, Area, Circularity columns

**Workflow**:
1. Load CSV → group by Genotype
2. Calculate mean Area per genotype
3. Identify genotype with max mean Area
4. Report mean Circularity for that genotype

See: **references/segmentation.md** "Colony Morphometry Analysis"

### Pattern 2: Cell Counting Statistics (bix-19)

**Question type**: "Cohen's d for NeuN counts between conditions?"

**Data**: CSV with Condition, NeuN_count, Sex, Hemisphere columns

**Workflow**:
1. Load CSV → filter by hemisphere/sex if needed
2. Split by Condition (KD vs CTRL)
3. Calculate Cohen's d with pooled SD
4. Report effect size

See: **references/statistical_analysis.md** "Effect Size Calculations"

### Pattern 3: Multi-Group Comparison (bix-41)

**Question type**: "Dunnett's test: How many ratios equivalent to control?"

**Data**: CSV with multiple co-culture ratios, Area, Circularity

**Workflow**:
1. Create Strain_Ratio labels
2. Run Dunnett's test for Area (vs control)
3. Run Dunnett's test for Circularity (vs control)
4. Count groups NOT significant in BOTH tests

See: **references/statistical_analysis.md** "Dunnett's Test"

### Pattern 4: Regression Optimization (bix-54)

**Question type**: "Peak frequency from natural spline model?"

**Data**: CSV with co-culture frequencies and Area measurements

**Workflow**:
1. Convert ratio strings to frequencies
2. Fit natural spline model (df=4)
3. Find peak via grid search
4. Report peak frequency + confidence interval

See: **references/statistical_analysis.md** "Regression Modeling"

---

## Quick Reference Table

| Task | Primary Tool | Reference |
|------|-------------|-----------|
| **Load measurement CSV** | pandas.read_csv() | This file |
| **Group statistics** | df.groupby().agg() | This file |
| **T-test** | scipy.stats.ttest_ind() | statistical_analysis.md |
| **ANOVA** | statsmodels.ols + anova_lm() | statistical_analysis.md |
| **Dunnett's test** | scipy.stats.dunnett() | statistical_analysis.md |
| **Cohen's d** | Custom function (pooled SD) | statistical_analysis.md |
| **Power analysis** | statsmodels TTestIndPower | statistical_analysis.md |
| **Polynomial regression** | statsmodels.OLS + poly features | statistical_analysis.md |
| **Natural spline** | patsy.cr() + statsmodels.OLS | statistical_analysis.md |
| **Cell segmentation** | skimage.filters + watershed | cell_counting.md |
| **Colony segmentation** | skimage.filters.threshold_otsu | segmentation.md |
| **Fluorescence quantification** | skimage.measure.regionprops | fluorescence_analysis.md |
| **Colocalization** | Pearson/Manders | fluorescence_analysis.md |
| **Image loading** | tifffile, skimage.io | image_processing.md |
| **Batch processing** | scripts/batch_process.py | scripts/ |

---

## Example Scripts

Ready-to-use scripts in `scripts/` directory:

1. **segment_cells.py** - Cell/nuclei counting with watershed
2. **measure_fluorescence.py** - Multi-channel intensity quantification
3. **batch_process.py** - Process folders of images
4. **colony_morphometry.py** - Measure colony area/circularity
5. **statistical_comparison.py** - Group comparison statistics

Usage:
```bash
# Count cells in image
python scripts/segment_cells.py cells.tif --channel 0 --min-area 50

# Batch process folder
python scripts/batch_process.py input_folder/ output.csv --analysis cell_count
```

---

## Detailed Reference Guides

For complete implementations and protocols:

1. **references/statistical_analysis.md** - All statistical tests, regression models
2. **references/cell_counting.md** - Cell/nuclei counting protocols
3. **references/segmentation.md** - Colony and object segmentation
4. **references/fluorescence_analysis.md** - Intensity quantification, colocalization
5. **references/image_processing.md** - Image loading, preprocessing, library selection
6. **references/troubleshooting.md** - Common issues and solutions

---

## Important Notes

### Matching R Statistical Functions

Some BixBench questions use R for analysis. Python equivalents:

- **R's Dunnett test** (`multcomp::glht`) → `scipy.stats.dunnett()` (scipy ≥ 1.10)
- **R's natural spline** (`ns(x, df=4)`) → `patsy.cr(x, knots=...)` with explicit quantile knots
- **R's t-test** (`t.test()`) → `scipy.stats.ttest_ind()`
- **R's ANOVA** (`aov()`) → `statsmodels.formula.api.ols()` + `sm.stats.anova_lm()`

See: **references/statistical_analysis.md** for exact parameter matching

### Answer Formatting

BixBench expects specific formats:
- "to the nearest thousand": `int(round(val, -3))`
- Percentages: Usually integer or 1-2 decimal places
- Cohen's d: 3 decimal places
- Sample sizes: Always integer (ceiling)
- Ratios: String format "5:1"

---

## Completeness Checklist

Before returning your answer, verify:

- [ ] Loaded all data files and inspected column names
- [ ] Identified the specific statistic or model requested
- [ ] Used correct grouping variables and filter conditions
- [ ] Applied correct rounding or format
- [ ] For "how many" questions: counted correctly based on criteria
- [ ] For statistical tests: used appropriate multiple comparison correction
- [ ] For regression: properly prepared and transformed data
- [ ] Double-checked direction of comparisons
- [ ] Verified answer falls within expected range

---

## Getting Help

- Start with decision tree at top of this file
- Check relevant reference guide for detailed protocol
- Use example scripts as templates
- See troubleshooting guide for common issues
- All statistical implementations in statistical_analysis.md
