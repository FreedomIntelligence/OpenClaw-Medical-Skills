# bio-machine-learning-prediction-explanation

> Explains machine learning predictions on omics data using SHAP values and LIME for feature attribution. Identifies which genes or features drive classifier decisions. Use when interpreting biomarker classifiers or understanding model predictions.

**Available tools:** Read, Bash

# Model Interpretation for Omics Classifiers

## SHAP TreeExplainer (v0.47+ API)

```python
import shap
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

explainer = shap.TreeExplainer(model)
# CORRECT (v0.47+): Call explainer directly, NOT .shap_values()
shap_values = explainer(X_test)

# shap_values is an Explanation object
# .values has shape (n_samples, n_features) for binary
# .base_values has expected value
print(f'SHAP values shape: {shap_values.values.shape}')
```

## Summary Plot (Global Feature Importance)

```python
import shap
import matplotlib.pyplot as plt

# Beeswarm plot: shows impact direction and magnitude
shap.plots.beeswarm(shap_values, max_display=20, show=False)
plt.tight_layout()
plt.savefig('shap_summary.png', dpi=150, bbox_inches='tight')
plt.close()

# Bar plot: mean absolute SHAP values
shap.plots.bar(shap_values, max_display=20, show=False)
plt.savefig('shap_bar.png', dpi=150, bbox_inches='tight')
```

## Force Plot (Individual Prediction)

```python
# Explain single prediction
sample_idx = 0
shap.plots.force(shap_values[sample_idx], matplotlib=True, show=False)
plt.savefig('shap_force_single.png', dpi=150, bbox_inches='tight')

# Waterfall plot (cleaner alternative)
shap.plots.waterfall(shap_values[sample_idx], max_display=15, show=False)
plt.savefig('shap_waterfall.png', dpi=150, bbox_inches='tight')
```

## SHAP for XGBoost

```python
from xgboost import XGBClassifier
import shap

xgb = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
xgb.fit(X_train, y_train)

explainer = shap.TreeExplainer(xgb)
shap_values = explainer(X_test)

# For XGBoost, shap_values contains log-odds contributions
shap.plots.beeswarm(shap_values, max_display=20)
```

## LIME (Local Interpretable Model-agnostic Explanations)

```python
from lime.lime_tabular import LimeTabularExplainer
import numpy as np

explainer = LimeTabularExplainer(
    X_train.values,
    feature_names=X_train.columns.tolist(),
    class_names=['control', 'disease'],
    mode='classification'
)

# Explain single instance
sample_idx = 0
exp = explainer.explain_instance(
    X_test.iloc[sample_idx].values,
    model.predict_proba,
    num_features=20
)

exp.save_to_file('lime_explanation.html')
# Or get as list: exp.as_list()
```

## Extract Top Features from SHAP

```python
import pandas as pd
import numpy as np

# Mean absolute SHAP value per feature
mean_shap = np.abs(shap_values.values).mean(axis=0)
feature_importance = pd.DataFrame({
    'feature': X_test.columns,
    'mean_shap': mean_shap
}).sort_values('mean_shap', ascending=False)

top_features = feature_importance.head(20)
top_features.to_csv('shap_top_features.csv', index=False)
```

## Dependence Plot (Feature Interactions)

```python
# Shows how SHAP value varies with feature value
# Automatically colors by interacting feature
shap.plots.scatter(shap_values[:, 'GENE1'], color=shap_values, show=False)
plt.savefig('shap_dependence.png', dpi=150, bbox_inches='tight')
```

## Multi-class SHAP

```python
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# For multi-class, shap_values.values has shape (n_samples, n_features, n_classes)
# Access class-specific values:
class_idx = 1
shap.plots.beeswarm(shap_values[:, :, class_idx], max_display=20)
```

## Related Skills

- machine-learning/omics-classifiers - Train models to interpret
- machine-learning/biomarker-discovery - Compare with selection-based importance
- data-visualization/heatmaps-clustering - Visualize SHAP values as heatmap
