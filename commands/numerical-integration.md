# numerical-integration

> Select and configure time integration methods for ODE/PDE simulations. Use when choosing explicit/implicit schemes, setting error tolerances, adapting time steps, diagnosing integration accuracy, planning IMEX splitting, or handling stiff/non-stiff coupled systems.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Numerical Integration

## Goal

Provide a reliable workflow to select integrators, set tolerances, and manage adaptive time stepping for time-dependent simulations.

## Requirements

- Python 3.8+
- NumPy (for some scripts)
- No heavy dependencies for core functionality

## Inputs to Gather

| Input | Description | Example |
|-------|-------------|---------|
| Problem type | ODE/PDE, stiff/non-stiff | `stiff PDE` |
| Jacobian available | Can compute ∂f/∂u? | `yes` |
| Target accuracy | Desired error level | `1e-6` |
| Constraints | Memory, implicit allowed? | `implicit OK` |
| Time scale | Characteristic time | `1e-3 s` |

## Decision Guidance

### Choosing an Integrator

```
Is the problem stiff?
├── YES → Is Jacobian available?
│   ├── YES → Use Rosenbrock or BDF
│   └── NO → Use BDF with numerical Jacobian
└── NO → Is high accuracy needed?
    ├── YES → Use RK45 or DOP853
    └── NO → Use RK4 or Adams-Bashforth
```

### Stiff vs Non-Stiff Detection

| Symptom | Likely Stiff | Action |
|---------|--------------|--------|
| dt shrinks to tiny values | Yes | Switch to implicit |
| Eigenvalues span many decades | Yes | Use BDF/Radau |
| Smooth solution, reasonable dt | No | Stay explicit |

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `scripts/error_norm.py` | `error_norm`, `scale_min`, `scale_max` |
| `scripts/adaptive_step_controller.py` | `accept`, `dt_next`, `factor` |
| `scripts/integrator_selector.py` | `recommended`, `alternatives`, `notes` |
| `scripts/imex_split_planner.py` | `implicit_terms`, `explicit_terms`, `splitting_strategy` |
| `scripts/splitting_error_estimator.py` | `error_estimate`, `substeps` |

## Workflow

1. **Classify stiffness** - Check eigenvalue spread or use stiffness_detector
2. **Choose tolerances** - See `references/tolerance_guidelines.md`
3. **Select integrator** - Run `scripts/integrator_selector.py`
4. **Compute error norms** - Use `scripts/error_norm.py` for step acceptance
5. **Adapt step size** - Use `scripts/adaptive_step_controller.py`
6. **Plan IMEX/splitting** - If mixed stiff/nonstiff, use `scripts/imex_split_planner.py`
7. **Validate convergence** - Repeat with tighter tolerances

## Conversational Workflow Example

**User**: I'm solving the Allen-Cahn equation with a stiff double-well potential. What integrator should I use?

**Agent workflow**:
1. Check integrator options:
   ```bash
   python3 scripts/integrator_selector.py --stiff --jacobian-available --accuracy high --json
   ```
2. Plan the IMEX splitting (diffusion implicit, reaction explicit):
   ```bash
   python3 scripts/imex_split_planner.py --stiff-terms diffusion --nonstiff-terms reaction --coupling weak --json
   ```
3. Recommend: Use IMEX-BDF2 with diffusion term implicit, double-well reaction explicit.

## Pre-Integration Checklist

- [ ] Identify stiffness and dominant time scales
- [ ] Set `rtol`/`atol` consistent with physics and units
- [ ] Confirm integrator compatibility with stiffness
- [ ] Use error norm to accept/reject steps
- [ ] Verify convergence with tighter tolerance run

## CLI Examples

```bash
# Select integrator for stiff problem with Jacobian
python3 scripts/integrator_selector.py --stiff --jacobian-available --accuracy high --json

# Compute scaled error norm
python3 scripts/error_norm.py --error 0.01,0.02 --solution 1.0,2.0 --rtol 1e-3 --atol 1e-6 --json

# Adaptive step control with PI controller
python3 scripts/adaptive_step_controller.py --dt 1e-2 --error-norm 0.8 --order 4 --controller pi --json

# Plan IMEX splitting
python3 scripts/imex_split_planner.py --stiff-terms diffusion,elastic --nonstiff-terms reaction --coupling strong --json

# Estimate splitting error
python3 scripts/splitting_error_estimator.py --dt 1e-4 --scheme strang --commutator-norm 50 --target-error 1e-6 --json
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `rtol and atol must be positive` | Invalid tolerances | Use positive values |
| `error-norm must be positive` | Negative error norm | Check error computation |
| `Unknown controller` | Invalid controller type | Use `i`, `pi`, or `pid` |
| `Splitting requires at least one term` | Empty term list | Specify stiff or nonstiff terms |

## Interpretation Guidance

### Error Norm Values

| Error Norm | Meaning | Action |
|------------|---------|--------|
| < 1.0 | Step acceptable | Accept, maybe increase dt |
| ≈ 1.0 | At tolerance boundary | Accept with current dt |
| > 1.0 | Step rejected | Reject, reduce dt |

### Controller Selection

| Controller | Properties | Best For |
|------------|------------|----------|
| I (integral) | Simple, some overshoot | Non-stiff, moderate accuracy |
| PI (proportional-integral) | Smooth, robust | General use |
| PID | Aggressive adaptation | Rapidly varying dynamics |

### IMEX Strategy

| Coupling | Strategy |
|----------|----------|
| Weak | Simple operator splitting |
| Moderate | Strang splitting |
| Strong | Fully coupled IMEX-RK |

## Limitations

- **No automatic stiffness detection**: Use stiffness_detector from numerical-stability
- **Splitting assumes separability**: Terms must be cleanly separable
- **Jacobian requirement**: Some methods need analytical or numerical Jacobian

## References

- `references/method_catalog.md` - Integrator options and properties
- `references/tolerance_guidelines.md` - Choosing rtol/atol
- `references/error_control.md` - Error norm and adaptation formulas
- `references/imex_guidelines.md` - Stiff/non-stiff splitting
- `references/splitting_catalog.md` - Operator splitting patterns
- `references/multiphase_field_patterns.md` - Phase-field specific splits

## Version History

- **v1.1.0** (2024-12-24): Enhanced documentation, decision guidance, examples
- **v1.0.0**: Initial release with 5 integration scripts
