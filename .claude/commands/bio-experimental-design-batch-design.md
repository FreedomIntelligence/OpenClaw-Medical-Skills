# bio-experimental-design-batch-design

> Designs experiments to minimize and account for batch effects using balanced layouts and blocking strategies. Use when planning multi-batch experiments, assigning samples to sequencing lanes, or designing studies where technical variation could confound biological signals.

**Available tools:** Read, Bash

# Batch Design and Mitigation

## Core Principle

Batch effects are unavoidable. Good design makes them correctable.

## Design Rules

1. **Never confound batch with condition** - Each batch must contain all conditions
2. **Balance samples across batches** - Equal numbers per condition per batch
3. **Randomize within constraints** - Avoid systematic patterns
4. **Include controls** - Same samples across batches if possible

## Balanced Design Example

```r
# BAD: Confounded design
# Batch 1: All treated samples
# Batch 2: All control samples
# -> Cannot separate batch from treatment

# GOOD: Balanced design
# Batch 1: 3 treated, 3 control
# Batch 2: 3 treated, 3 control
# -> Batch effect can be estimated and removed
```

## Sample Assignment

```r
library(designit)

# Create balanced assignment
samples <- data.frame(
  sample_id = paste0('S', 1:24),
  condition = rep(c('ctrl', 'treat'), each = 12),
  sex = rep(c('M', 'F'), 12)
)

# Optimize batch assignment
batch_design <- osat(samples, batch_size = 8,
                     balance_cols = c('condition', 'sex'))
```

## Detecting Batch Effects

```r
library(sva)

# From count matrix
mod <- model.matrix(~condition, colData)
mod0 <- model.matrix(~1, colData)

# Estimate number of surrogate variables (hidden batches)
n_sv <- num.sv(counts_normalized, mod)

# Estimate surrogate variables
svobj <- sva(counts_normalized, mod, mod0, n.sv = n_sv)
```

## Correction Methods

| Method | When to Use |
|--------|-------------|
| ComBat | Known batches, moderate effects |
| SVA | Unknown batches, exploratory |
| RUVseq | Using control genes |
| limma::removeBatchEffect | Visualization only |

## Documenting Design

Always record:
- Date of sample processing
- Reagent lot numbers
- Operator
- Equipment/lane assignments
- Any deviations from protocol

## Related Skills

- experimental-design/power-analysis - Account for batch in power calculations
- differential-expression/batch-correction - Correcting batch effects in analysis
- single-cell/batch-integration - scRNA-seq batch correction
