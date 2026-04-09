# bio-workflows-biomarker-pipeline

> End-to-end biomarker discovery workflow from expression data to validated biomarker panels. Covers feature selection with Boruta/LASSO, classifier training with nested CV, and SHAP interpretation. Use when building and validating diagnostic or prognostic biomarker signatures from omics data.

**Available tools:** Read, Bash

# Biomarker Discovery Pipeline

Complete pipeline from expression data to validated biomarker panels with classifier.

## Workflow Overview

```
Expression matrix + Metadata
    |
    v
[1. Data Preparation] -----> StandardScaler, train/test split
    |
    v
[2. Feature Selection] ----> Boruta or LASSO stability selection
    |
    v
[3. Model Training] -------> RandomForest/XGBoost with nested CV
    |
    v
[4. Model Interpretation] -> SHAP values, feature importance
    |
    v
[5. Validation] -----------> Hold-out test, bootstrap CI
    |
    v
Validated biomarker panel + classifier
```

## Step 1: Data Preparation

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

expr = pd.read_csv('expression.csv', index_col=0)
meta = pd.read_csv('metadata.csv', index_col=0)

X = expr.T  # samples x genes
y = meta.loc[X.index, 'condition'].values

# test_size=0.2: Standard 80/20 split; use 0.3 for <100 samples
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Fit scaler on training only to prevent data leakage
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**QC Checkpoint 1:** Check class balance, sample counts per group
- Minimum 10 samples per class recommended
- Classes should be reasonably balanced (ratio <3:1)

## Step 2: Feature Selection

### Option A: Boruta (All-Relevant Selection)

```python
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif

# Pre-filter if >10k features
if X_train_scaled.shape[1] > 10000:
    selector = SelectKBest(f_classif, k=5000)
    selector.fit(X_train_scaled, y_train)
    X_train_filt = X_train_scaled[:, selector.get_support()]
    feature_mask = selector.get_support()
else:
    X_train_filt = X_train_scaled
    feature_mask = None

# max_depth=5: Shallow trees for stable importances
rf = RandomForestClassifier(n_estimators=100, max_depth=5, n_jobs=-1, random_state=42)
# max_iter=100: Usually sufficient; 200 if many tentative
boruta = BorutaPy(rf, n_estimators='auto', max_iter=100, random_state=42, verbose=0)
boruta.fit(X_train_filt, y_train)

selected_idx = boruta.support_
print(f'Selected {selected_idx.sum()} features')
```

### Option B: LASSO Stability Selection

```python
from sklearn.linear_model import LogisticRegressionCV
import numpy as np

# n_bootstrap=100: Quick; use 500 for publication
n_bootstrap = 100
stability_scores = np.zeros(X_train_scaled.shape[1])

for i in range(n_bootstrap):
    idx = np.random.choice(len(y_train), size=len(y_train), replace=True)
    # Cs=10: 10 regularization values to search
    model = LogisticRegressionCV(penalty='l1', solver='saga', Cs=10, cv=3, random_state=i, max_iter=1000)
    model.fit(X_train_scaled[idx], y_train[idx])
    stability_scores += (model.coef_[0] != 0).astype(int)

stability_scores /= n_bootstrap
# stability_threshold=0.6: Standard; 0.8 for strict
selected_idx = stability_scores > 0.6
print(f'Selected {selected_idx.sum()} features (stability >0.6)')
```

**QC Checkpoint 2:**
- Selected features: 5-200 range
- Too few (<5): lower threshold, increase iterations
- Too many (>200): increase threshold, add pre-filtering

## Step 3: Model Training with Nested CV

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

X_train_sel = X_train_scaled[:, selected_idx]
X_test_sel = X_test_scaled[:, selected_idx]

# outer_cv=5: Standard for performance estimation
outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# n_estimators=100: Sufficient for most omics
clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
cv_scores = cross_val_score(clf, X_train_sel, y_train, cv=outer_cv, scoring='roc_auc')

print(f'Nested CV AUC: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}')
```

**QC Checkpoint 3:**
- AUC >0.7 acceptable, >0.8 good
- Fold variance <0.1 (stable performance)
- Check for overfitting: train AUC should not be >>test AUC

## Step 4: Model Interpretation

```python
import shap
import matplotlib.pyplot as plt

clf.fit(X_train_sel, y_train)

# SHAP v0.47+: call explainer directly
explainer = shap.TreeExplainer(clf)
shap_values = explainer(X_train_sel)

# Beeswarm: shows importance AND direction
shap.plots.beeswarm(shap_values, max_display=20, show=False)
plt.tight_layout()
plt.savefig('shap_beeswarm.png', dpi=150, bbox_inches='tight')
plt.close()

# Extract top features
import numpy as np
mean_shap = np.abs(shap_values.values).mean(axis=0)
top_shap_idx = np.argsort(mean_shap)[-20:]
```

**QC Checkpoint 4:**
- Top 20 SHAP features should have >50% overlap with selected features
- SHAP directions should be biologically plausible

## Step 5: Final Validation

```python
from sklearn.metrics import roc_auc_score, classification_report
import numpy as np

y_prob = clf.predict_proba(X_test_sel)[:, 1]
test_auc = roc_auc_score(y_test, y_prob)
print(f'Hold-out test AUC: {test_auc:.3f}')

# Bootstrap CI for AUC
# n_bootstrap=1000: Standard for publication-quality CI
n_bootstrap = 1000
boot_aucs = []
for i in range(n_bootstrap):
    idx = np.random.choice(len(y_test), size=len(y_test), replace=True)
    boot_aucs.append(roc_auc_score(y_test[idx], y_prob[idx]))

ci_lower, ci_upper = np.percentile(boot_aucs, [2.5, 97.5])
print(f'95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]')

print(classification_report(y_test, clf.predict(X_test_sel)))
```

## Parameter Recommendations

| Step | Parameter | Recommendation |
|------|-----------|----------------|
| Split | test_size | 0.2 (standard), 0.3 for small datasets |
| Boruta | max_iter | 100 (sufficient), 200 if tentative features |
| LASSO | n_bootstrap | 100 (quick), 500 for publication |
| LASSO | stability_threshold | 0.6 (standard), 0.8 for strict |
| Nested CV | outer_folds | 5 (standard), 10 for small datasets |
| Nested CV | inner_folds | 3 (sufficient for tuning) |
| RF | n_estimators | 100-500 |
| XGBoost | learning_rate | 0.1 (conservative) |

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| No features selected | Too strict threshold | Lower stability threshold, increase iterations |
| Too many features (>200) | Noisy data | Add pre-filtering, increase regularization |
| Low CV AUC (<0.6) | No signal, low power | Check data quality, add samples |
| High variance across folds | Small sample size | Use more folds, LOOCV |
| SHAP features differ from selected | Model using different signal | Review feature correlations |

## Export Results

```python
import pandas as pd
import joblib

# Save biomarker panel
feature_names = X_train.columns[selected_idx].tolist()
pd.DataFrame({'feature': feature_names}).to_csv('biomarker_panel.csv', index=False)

# Save model and scaler for deployment
joblib.dump(clf, 'biomarker_classifier.joblib')
joblib.dump(scaler, 'feature_scaler.joblib')
```

## Related Skills

- machine-learning/biomarker-discovery - Detailed feature selection methods
- machine-learning/model-validation - Nested CV implementation details
- machine-learning/omics-classifiers - Classifier options and tuning
- machine-learning/prediction-explanation - SHAP and LIME interpretation
- differential-expression/de-results - Pre-filter with DE genes
- pathway-analysis/go-enrichment - Functional enrichment of biomarkers
