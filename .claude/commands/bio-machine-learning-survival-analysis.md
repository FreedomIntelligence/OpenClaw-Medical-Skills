# bio-machine-learning-survival-analysis

> Analyzes time-to-event data using Kaplan-Meier curves, log-rank tests, and Cox proportional hazards regression with lifelines. Builds survival models from clinical and omics features. Use when predicting patient survival or modeling time-to-event outcomes.

**Available tools:** Read, Bash

# Survival Prediction with lifelines

## Kaplan-Meier Curves

```python
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt

kmf = KaplanMeierFitter()

# T: time to event or censoring
# E: event indicator (1=event occurred, 0=censored)
kmf.fit(T, event_observed=E)

# Plot survival curve
kmf.plot_survival_function()
plt.xlabel('Time (months)')
plt.ylabel('Survival probability')
plt.savefig('km_curve.png', dpi=150)
```

## Compare Groups with Log-Rank Test

```python
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))

for group, color in zip(['high', 'low'], ['red', 'blue']):
    mask = df['risk_group'] == group
    kmf = KaplanMeierFitter()
    kmf.fit(df.loc[mask, 'time'], event_observed=df.loc[mask, 'event'], label=group)
    kmf.plot_survival_function(ax=ax, color=color)

# Log-rank test
high = df[df['risk_group'] == 'high']
low = df[df['risk_group'] == 'low']
results = logrank_test(high['time'], low['time'], event_observed_A=high['event'], event_observed_B=low['event'])
print(f'Log-rank p-value: {results.p_value:.4e}')

ax.set_xlabel('Time (months)')
ax.set_ylabel('Survival probability')
ax.set_title(f'Log-rank p = {results.p_value:.4e}')
plt.savefig('km_comparison.png', dpi=150)
```

## Cox Proportional Hazards Regression

```python
from lifelines import CoxPHFitter

# Prepare data: must have 'time' and 'event' columns
# Include covariates as additional columns
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')

# Summary with hazard ratios
cph.print_summary()

# Get hazard ratios as DataFrame
hr = cph.summary[['exp(coef)', 'exp(coef) lower 95%', 'exp(coef) upper 95%', 'p']]
print(hr)

# Concordance index (c-index): 0.5=random, 1.0=perfect
print(f'C-index: {cph.concordance_index_:.3f}')
```

## Multivariate Cox Model

```python
from lifelines import CoxPHFitter
import pandas as pd

# Combine clinical and omics features
cox_df = pd.DataFrame({
    'time': meta['survival_months'],
    'event': meta['vital_status'],
    'age': meta['age'],
    'stage': meta['stage_numeric'],
    'GENE1': expr.loc['GENE1'],
    'GENE2': expr.loc['GENE2']
})

cph = CoxPHFitter(penalizer=0.1)  # L2 regularization for stability
cph.fit(cox_df, duration_col='time', event_col='event')
cph.print_summary()
```

## Predict Risk Scores

```python
# Partial hazard (risk score)
risk_scores = cph.predict_partial_hazard(cox_df)

# Median risk split for KM plot
df['risk_group'] = (risk_scores > risk_scores.median()).map({True: 'high', False: 'low'})
```

## Check Proportional Hazards Assumption

```python
# Test PH assumption
cph.check_assumptions(df, p_value_threshold=0.05, show_plots=True)
```

## Survival at Specific Time

```python
# Survival probability at specific times
survival_probs = kmf.survival_function_at_times([12, 24, 60])
print(survival_probs)

# Median survival
print(f'Median survival: {kmf.median_survival_time_:.1f}')
```

## Feature Selection for Survival

```python
from lifelines import CoxPHFitter
import pandas as pd

# Univariate screening
results = []
for gene in expr.index[:1000]:
    cox_df = pd.DataFrame({
        'time': meta['survival_months'],
        'event': meta['vital_status'],
        'gene': expr.loc[gene]
    })
    cph = CoxPHFitter()
    cph.fit(cox_df, duration_col='time', event_col='event')
    results.append({
        'gene': gene,
        'hr': cph.hazard_ratios_['gene'],
        'p': cph.summary.loc['gene', 'p']
    })

results_df = pd.DataFrame(results)
sig_genes = results_df[results_df['p'] < 0.05].sort_values('p')
```

## Related Skills

- clinical-databases/variant-prioritization - Clinical variant interpretation
- differential-expression/de-results - Find DE genes for survival model
- machine-learning/biomarker-discovery - Select predictive features
