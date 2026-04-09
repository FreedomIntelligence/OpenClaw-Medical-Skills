# simulation-validator

> Validate simulations before, during, and after execution. Use for pre-flight checks, runtime monitoring, post-run validation, diagnosing failed simulations, checking convergence, detecting NaN/Inf, or verifying mass/energy conservation.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Simulation Validator

## Goal

Provide a three-stage validation protocol: pre-flight checks, runtime monitoring, and post-flight validation for materials simulations.

## Requirements

- Python 3.8+
- No external dependencies (uses Python standard library only)
- Works on Linux, macOS, and Windows

## Inputs to Gather

Before running validation scripts, collect from the user:

| Input | Description | Example |
|-------|-------------|---------|
| Config file | Simulation configuration (JSON/YAML) | `simulation.json` |
| Log file | Runtime output log | `simulation.log` |
| Metrics file | Post-run metrics (JSON) | `results.json` |
| Required params | Parameters that must exist | `dt,dx,kappa` |
| Valid ranges | Parameter bounds | `dt:1e-6:1e-2` |

## Decision Guidance

### When to Run Each Stage

```
Is simulation about to start?
├── YES → Run Stage 1: preflight_checker.py
│         └── BLOCK status? → Fix issues, do NOT run simulation
│         └── WARN status? → Review warnings, document if accepted
│         └── PASS status? → Proceed to run simulation
│
Is simulation running?
├── YES → Run Stage 2: runtime_monitor.py (periodically)
│         └── Alerts? → Consider stopping, check parameters
│
Has simulation finished?
├── YES → Run Stage 3: result_validator.py
│         └── Failed checks? → Do NOT use results
│                            → Run failure_diagnoser.py
│         └── All passed? → Results are valid
```

### Choosing Validation Thresholds

| Metric | Conservative | Standard | Relaxed |
|--------|--------------|----------|---------|
| Mass tolerance | 1e-6 | 1e-3 | 1e-2 |
| Residual growth | 2x | 10x | 100x |
| dt reduction | 10x | 100x | 1000x |

## Script Outputs (JSON Fields)

| Script | Output Fields |
|--------|---------------|
| `scripts/preflight_checker.py` | `report.status`, `report.blockers`, `report.warnings` |
| `scripts/runtime_monitor.py` | `alerts`, `residual_stats`, `dt_stats` |
| `scripts/result_validator.py` | `checks`, `confidence_score`, `failed_checks` |
| `scripts/failure_diagnoser.py` | `probable_causes`, `recommended_fixes` |

## Three-Stage Validation Protocol

### Stage 1: Pre-flight (Before Simulation)

1. Run `scripts/preflight_checker.py --config simulation.json`
2. **BLOCK status**: Stop immediately, fix all blocker issues
3. **WARN status**: Review warnings, document accepted risks
4. **PASS status**: Proceed to simulation

```bash
python3 scripts/preflight_checker.py \
    --config simulation.json \
    --required dt,dx,kappa \
    --ranges "dt:1e-6:1e-2,dx:1e-4:1e-1" \
    --min-free-gb 1.0 \
    --json
```

### Stage 2: Runtime (During Simulation)

1. Run `scripts/runtime_monitor.py --log simulation.log` periodically
2. Configure alert thresholds based on problem type
3. Stop simulation if critical alerts appear

```bash
python3 scripts/runtime_monitor.py \
    --log simulation.log \
    --residual-growth 10.0 \
    --dt-drop 100.0 \
    --json
```

### Stage 3: Post-flight (After Simulation)

1. Run `scripts/result_validator.py --metrics results.json`
2. **All checks PASS**: Results are valid for analysis
3. **Any check FAIL**: Do NOT use results, diagnose failure

```bash
python3 scripts/result_validator.py \
    --metrics results.json \
    --bound-min 0.0 \
    --bound-max 1.0 \
    --mass-tol 1e-3 \
    --json
```

### Failure Diagnosis

When validation fails:

```bash
python3 scripts/failure_diagnoser.py --log simulation.log --json
```

## Conversational Workflow Example

**User**: My phase field simulation crashed after 1000 steps. Can you help me figure out why?

**Agent workflow**:
1. First, check the log for obvious errors:
   ```bash
   python3 scripts/failure_diagnoser.py --log simulation.log --json
   ```
2. If diagnosis suggests numerical blow-up, check runtime stats:
   ```bash
   python3 scripts/runtime_monitor.py --log simulation.log --json
   ```
3. Recommend fixes based on findings:
   - If residual grew rapidly → reduce time step
   - If dt collapsed → check stability conditions
   - If NaN detected → check initial conditions

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Config not found` | File path invalid | Verify config path exists |
| `Non-numeric value` | Parameter is not a number | Fix config file format |
| `out of range` | Parameter outside bounds | Adjust parameter or bounds |
| `Output directory not writable` | Permission issue | Check directory permissions |
| `Insufficient disk space` | Disk nearly full | Free up space or reduce output |

## Interpretation Guidance

### Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| PASS | All checks passed | Proceed with confidence |
| WARN | Non-critical issues found | Review and document |
| BLOCK | Critical issues found | Must fix before proceeding |

### Confidence Score Interpretation

| Score | Meaning |
|-------|---------|
| 1.0 | All validation checks passed |
| 0.75+ | Most checks passed, minor issues |
| 0.5-0.75 | Significant issues, review carefully |
| < 0.5 | Major problems, do not trust results |

### Common Failure Patterns

| Pattern in Log | Likely Cause | Recommended Fix |
|----------------|--------------|-----------------|
| NaN, Inf, overflow | Numerical instability | Reduce dt, increase damping |
| max iterations, did not converge | Solver failure | Tune preconditioner, tolerances |
| out of memory | Memory exhaustion | Reduce mesh, enable out-of-core |
| dt reduced | Adaptive stepping triggered | May be okay if controlled |

## Limitations

- **Not a real-time monitor**: Scripts analyze logs after-the-fact
- **Regex-based**: Log parsing depends on pattern matching; may miss unusual formats
- **No automatic fixes**: Scripts diagnose but don't modify simulations

## References

- `references/validation_protocol.md` - Detailed checklist and criteria
- `references/log_patterns.md` - Common failure signatures and regex patterns

## Version History

- **v1.1.0** (2024-12-24): Enhanced documentation, decision guidance, Windows compatibility
- **v1.0.0**: Initial release with 4 validation scripts
