# nonlinear-solvers

> Select and configure nonlinear solvers for f(x)=0 or min F(x). Use for Newton methods, quasi-Newton (BFGS, L-BFGS), Broyden, Anderson acceleration, diagnosing convergence issues, choosing line search vs trust region, and analyzing Jacobian quality.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Nonlinear Solvers

## Goal

Provide a universal workflow to select a nonlinear solver, configure globalization strategies, and diagnose convergence for root-finding, optimization, and least-squares problems.

## Requirements

- Python 3.8+
- NumPy (for Jacobian diagnostics)
- SciPy (optional, for advanced analysis)

## Inputs to Gather

| Input | Description | Example |
|-------|-------------|---------|
| Problem type | Root-finding, optimization, least-squares | `root-finding` |
| Problem size | Number of unknowns | `n = 10000` |
| Jacobian availability | Analytic, finite-diff, unavailable | `analytic` |
| Jacobian cost | Cheap or expensive to compute | `expensive` |
| Constraints | None, bounds, equality, inequality | `none` |
| Smoothness | Is objective/residual smooth? | `yes` |
| Residual history | Sequence of residual norms | `1,0.1,0.01,...` |

## Decision Guidance

### Solver Selection Flowchart

```
Is Jacobian available and cheap?
├── YES → Problem size?
│   ├── Small (n < 1000) → Newton (full)
│   └── Large (n ≥ 1000) → Newton-Krylov
└── NO → Is objective smooth?
    ├── YES → Memory limited?
    │   ├── YES → L-BFGS or Broyden
    │   └── NO → BFGS
    └── NO → Anderson acceleration or Picard
```

### Quick Reference

| Problem Type | First Choice | Alternative | Globalization |
|--------------|--------------|-------------|---------------|
| Small root-finding | Newton | Broyden | Line search |
| Large root-finding | Newton-Krylov | Anderson | Trust region |
| Optimization | L-BFGS | BFGS | Wolfe line search |
| Least-squares | Levenberg-Marquardt | Gauss-Newton | Trust region |
| Bound constrained | L-BFGS-B | Trust-region reflective | Projected |

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `scripts/solver_selector.py` | `recommended`, `alternatives`, `notes` |
| `scripts/convergence_analyzer.py` | `converged`, `convergence_type`, `estimated_rate`, `diagnosis` |
| `scripts/jacobian_diagnostics.py` | `condition_number`, `jacobian_quality`, `rank_deficient` |
| `scripts/globalization_advisor.py` | `strategy`, `line_search_type`, `trust_region_type`, `parameters` |
| `scripts/residual_monitor.py` | `patterns_detected`, `alerts`, `recommendations` |
| `scripts/step_quality.py` | `ratio`, `step_quality`, `accept_step`, `trust_radius_action` |

## Workflow

1. **Characterize problem** - Identify type, size, Jacobian availability
2. **Select solver** - Run `scripts/solver_selector.py`
3. **Choose globalization** - Run `scripts/globalization_advisor.py`
4. **Analyze Jacobian** - If available, run `scripts/jacobian_diagnostics.py`
5. **Monitor residuals** - During solve, use `scripts/residual_monitor.py`
6. **Analyze convergence** - Run `scripts/convergence_analyzer.py`
7. **Evaluate steps** - For trust region, use `scripts/step_quality.py`

## Conversational Workflow Example

**User**: My Newton solver for a phase-field simulation is converging very slowly. After 50 iterations, the residual only dropped from 1 to 0.1.

**Agent workflow**:
1. Analyze convergence:
   ```bash
   python3 scripts/convergence_analyzer.py --residuals 1,0.8,0.6,0.5,0.4,0.3,0.2,0.15,0.12,0.1 --json
   ```
2. Check globalization strategy:
   ```bash
   python3 scripts/globalization_advisor.py --problem-type root-finding --jacobian-quality ill-conditioned --previous-failures 0 --json
   ```
3. Recommend: Switch to trust region with Levenberg-Marquardt regularization, or use Newton-Krylov with better preconditioning.

## Pre-Solve Checklist

- [ ] Confirm problem type (root-finding, optimization, least-squares)
- [ ] Assess Jacobian availability and cost
- [ ] Check initial guess quality
- [ ] Set appropriate tolerances
- [ ] Choose globalization strategy
- [ ] Prepare to monitor convergence

## CLI Examples

```bash
# Select solver for large unconstrained optimization
python3 scripts/solver_selector.py --size 50000 --smooth --memory-limited --json

# Analyze convergence from residual history
python3 scripts/convergence_analyzer.py --residuals 1,0.1,0.01,0.001,0.0001 --tolerance 1e-6 --json

# Diagnose Jacobian quality
python3 scripts/jacobian_diagnostics.py --matrix jacobian.txt --json

# Get globalization recommendation
python3 scripts/globalization_advisor.py --problem-type optimization --jacobian-quality good --json

# Monitor residual patterns
python3 scripts/residual_monitor.py --residuals 1,0.8,0.9,0.7,0.75,0.6 --target-tolerance 1e-8 --json

# Evaluate step quality for trust region
python3 scripts/step_quality.py --predicted-reduction 0.5 --actual-reduction 0.4 --step-norm 0.8 --gradient-norm 1.0 --trust-radius 1.0 --json
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `problem_size must be positive` | Invalid size | Check problem dimension |
| `constraint_type must be one of...` | Unknown constraint | Use: none, bound, equality, inequality |
| `residuals must be non-negative` | Invalid residual data | Check residual computation |
| `Matrix file not found` | Invalid path | Verify Jacobian file exists |

## Interpretation Guidance

### Convergence Type

| Type | Meaning | Action |
|------|---------|--------|
| quadratic | Optimal Newton | Continue, near solution |
| superlinear | Quasi-Newton working | Monitor for stagnation |
| linear | Acceptable | May improve with preconditioner |
| sublinear | Too slow | Change method or formulation |
| stagnated | No progress | Check Jacobian, preconditioner |
| diverged | Increasing residual | Add globalization, check Jacobian |

### Jacobian Quality

| Quality | Condition Number | Action |
|---------|------------------|--------|
| good | < 10⁶ | Standard Newton works |
| moderately-conditioned | 10⁶ - 10¹⁰ | Consider scaling |
| ill-conditioned | > 10¹⁰ | Use regularization |
| near-singular | ∞ | Reformulate or use LM |

### Step Quality (Trust Region)

| Ratio ρ | Quality | Trust Radius |
|---------|---------|--------------|
| ρ < 0 | very_poor | Shrink aggressively |
| ρ < 0.25 | marginal | Shrink |
| 0.25 ≤ ρ < 0.75 | good | Maintain |
| ρ ≥ 0.75 | excellent | Expand if at boundary |

## Limitations

- **No global convergence guarantee**: All methods may fail for pathological problems
- **Jacobian accuracy**: Finite-difference Jacobian may be inaccurate near discontinuities
- **Large dense problems**: May require specialized solvers not covered here
- **Constrained optimization**: Complex constraints need SQP or interior point methods

## References

- `references/solver_decision_tree.md` - Problem-based solver selection
- `references/method_catalog.md` - Method details and parameters
- `references/convergence_diagnostics.md` - Diagnosing convergence issues
- `references/globalization_strategies.md` - Line search and trust region

## Version History

- **v1.0.0** : Initial release with 6 analysis scripts
