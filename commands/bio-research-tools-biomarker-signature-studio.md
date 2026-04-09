# bio-research-tools-biomarker-signature-studio

> Multi-omic biomarker discovery studio that ingests expression + metadata, performs QC, multi-strategy feature selection, nested CV model training, survival analysis hooks, and SHAP-based interpretation. Use to design translational biomarker panels with documented evidence.

**Available tools:** Read, Bash

# Biomarker Signature Studio

Design validated biomarker panels that are explainable, stable, and ready for translational follow-up. This skill stitches together the existing biomarker pipeline tooling, adds configurable feature-selection ensembles, a small survival-analysis hook, and artifact export so downstream lab teams can review QC outputs.

## What This Skill Does

1. **QC + Harmonization:** Align expression matrices (samples x features) with metadata, check label balance, and compute summary stats.
2. **Feature Selection Ensemble:** Supports Boruta, elastic-net stability, mutual-information top-K, and mRMR with optional intersection voting.
3. **Model Factory:** Trains multiple estimators (Logistic L1, RandomForest, XGBoost if present) under nested CV, picks champion by AUC.
4. **Explainability + Export:** Produces SHAP tables/plots when packages are available, exports feature rankings and model weights.
5. **Survival Hook:** If metadata contains `time_to_event` and `event` the skill computes concordance for selected features via Cox model.

All logic lives in `scripts/biomarker_signature_studio.py`.

## Inputs

- Expression matrix (`--expression`): CSV/TSV genes x samples or samples x genes (auto-detected by metadata match).
- Metadata (`--metadata`): Must contain `--label-column`. Optional `--id-column` (default `sample_id`), `time_to_event`, `event`.
- Optional gene list for filtering (`--feature-list`).
- Output directory (`--output-dir`), created if missing.

## Quick CLI Usage

```bash
python Skills/Research_Tools/Biomarker_Signature_Studio/scripts/biomarker_signature_studio.py \
  --expression data/expression.csv \
  --metadata data/metadata.csv \
  --label-column phenotype \
  --selectors boruta,lasso,mrmr \
  --models rf,logit \
  --output-dir outputs/biomarkers_run1
```

Key flags:

| Flag | Description |
|------|-------------|
| `--selectors` | Comma list of selection strategies (`boruta`, `lasso`, `mrmr`, `mi_topk`). |
| `--models` | Models to evaluate (`logit`, `rf`, `xgb`). |
| `--k-features` | Target number of features for `mrmr`/`mi_topk`. |
| `--survival` | Enable Cox evaluation when survival columns exist. |
| `--random-state` | Reproducibility. |
| `--nested-folds` | Outer CV folds (default 5). |

## Workflow

1. Load + align inputs, infer orientation, impute missing values.
2. Standardize features (fit on train set only).
3. Run requested selectors; create intersection + union candidate lists.
4. For each selector output run nested CV training across requested models.
5. Export champion metrics (`metrics.json`), feature table (`selected_features.csv`), SHAP summary (`shap_summary.csv` when available), and survival stats (`survival.json`).

## QC Expectations

- Class count ratio ≤3:1; warnings logged otherwise.
- Selected features between 5 and 250 unless user overrides.
- Nested CV AUC ≥0.70 or flagged in report.
- SHAP overlap with selected features ≥60% (reported).

## Related Assets

- `examples/configs/biomarker_studio_template.yaml` (scaffold for teams)
- `scripts/biomarker_signature_studio.py` (entry point)
- Existing biomarker workflow skill for orchestrated runs.

Use this skill whenever you need a ready-to-review biomarker dossier (data QC, model metrics, explainability artifacts) before moving to validation cohorts or lab assays.
