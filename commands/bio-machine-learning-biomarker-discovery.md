# bio-machine-learning-biomarker-discovery

> Selects informative features for biomarker discovery using Boruta all-relevant selection, mRMR minimum redundancy, and LASSO regularization. Use when identifying biomarkers from high-dimensional omics data.

**Available tools:** Read, Bash

# Feature Selection for Biomarker Discovery

## Boruta All-Relevant Selection

Identifies all features that are significantly better than random (shadow features).

```python
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

rf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)

# max_iter=100: Typically sufficient; increase to 200 if many features remain tentative
# perc=100: Use max of shadow features (default); lower for stricter selection
boruta = BorutaPy(rf, n_estimators='auto', max_iter=100, random_state=42, verbose=0)
boruta.fit(X.values, y)

selected = X.columns[boruta.support_]
tentative = X.columns[boruta.support_weak_]
print(f'Selected: {len(selected)}, Tentative: {len(tentative)}')

feature_ranks = pd.DataFrame({
    'feature': X.columns,
    'rank': boruta.ranking_,
    'selected': boruta.support_
}).sort_values('rank')
```

## mRMR (Minimum Redundancy Maximum Relevance)

Selects features that are individually relevant but minimally redundant with each other.

```python
from mrmr import mrmr_classif

# K: Number of features to select; start with 50-100 for omics
selected_features = mrmr_classif(X=X, y=pd.Series(y), K=50)
X_selected = X[selected_features]
```

## LASSO Feature Selection

L1 regularization drives irrelevant coefficients to zero.

```python
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# cv=5: Standard for selection; eps and n_alphas control alpha grid
lasso = LassoCV(cv=5, random_state=42)
lasso.fit(X_scaled, y)

selected_mask = lasso.coef_ != 0
selected = X.columns[selected_mask]
print(f'LASSO selected {len(selected)} features at alpha={lasso.alpha_:.4f}')

coefs = pd.Series(lasso.coef_, index=X.columns)
nonzero = coefs[coefs != 0].sort_values(key=abs, ascending=False)
```

## Univariate Filtering (Pre-filter)

Reduce dimensionality before more expensive methods.

```python
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# f_classif: Fast, assumes normality; good for log-counts
# mutual_info_classif: Nonlinear relationships but slower
# k=1000: Reasonable pre-filter; increase for larger omics datasets (>10k features)
selector = SelectKBest(f_classif, k=1000)
X_filtered = selector.fit_transform(X, y)
selected_idx = selector.get_support(indices=True)
```

## Combined Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Pre-filter then Boruta for efficiency
pipe = Pipeline([
    ('prefilter', SelectKBest(f_classif, k=5000)),
    ('boruta', BorutaPy(RandomForestClassifier(n_jobs=-1), max_iter=100, random_state=42))
])
# Note: BorutaPy doesn't follow sklearn API perfectly; manual fit may be needed
```

## Method Comparison

| Method | Strengths | Weaknesses | Use When |
|--------|-----------|------------|----------|
| Boruta | Finds all relevant features | Slow on large data | Want complete biomarker panel |
| mRMR | Reduces redundancy | Fixed K | Want compact signature |
| LASSO | Sparse, interpretable | Picks one of correlated | Want minimal predictive set |
| Univariate | Fast | Ignores interactions | Pre-filtering |

## Stability Selection

```python
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel
import numpy as np

n_bootstrap = 100
selection_counts = np.zeros(X.shape[1])

for i in range(n_bootstrap):
    idx = np.random.choice(len(X), size=len(X), replace=True)
    X_boot, y_boot = X.iloc[idx], y[idx]

    lasso = LogisticRegression(penalty='l1', solver='saga', C=0.1, max_iter=1000)
    lasso.fit(X_boot, y_boot)
    selection_counts += (lasso.coef_[0] != 0)

# stability_threshold=0.6: Features selected in >60% of bootstrap samples
stable_features = X.columns[selection_counts / n_bootstrap > 0.6]
```

## Related Skills

- differential-expression/de-results - Pre-filter with DE genes
- pathway-analysis/go-enrichment - Functional enrichment of selected features
- machine-learning/omics-classifiers - Use selected features for prediction
