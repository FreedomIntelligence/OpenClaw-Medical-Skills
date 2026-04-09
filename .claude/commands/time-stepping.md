# time-stepping

> Plan and control time-step policies for simulations. Use when coupling CFL/physics limits with adaptive stepping, ramping initial transients, scheduling outputs/checkpoints, or planning restart strategies for long runs.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Time Stepping

## Goal

Provide a reliable workflow for choosing, ramping, and monitoring time steps plus output/checkpoint cadence.

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib)

## Inputs to Gather

| Input | Description | Example |
|-------|-------------|---------|
| Stability limits | CFL/Fourier/reaction limits | `dt_max = 1e-4` |
| Target dt | Desired time step | `1e-5` |
| Total run time | Simulation duration | `10 s` |
| Output interval | Time between outputs | `0.1 s` |
| Checkpoint cost | Time to write checkpoint | `120 s` |

## Decision Guidance

### Time Step Selection

```
Is stability limit known?
├── YES → Use min(dt_target, dt_limit × safety)
└── NO → Start conservative, increase adaptively

Need ramping for startup?
├── YES → Start at dt_init, ramp to dt_target over N steps
└── NO → Use dt_target from start
```

### Ramping Strategy

| Problem Type | Ramp Steps | Initial dt |
|--------------|------------|------------|
| Smooth IC | None needed | Full dt |
| Sharp gradients | 5-10 | 0.1 × dt |
| Phase change | 10-20 | 0.01 × dt |
| Cold start | 10-50 | 0.001 × dt |

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `scripts/timestep_planner.py` | `dt_limit`, `dt_recommended`, `ramp_schedule` |
| `scripts/output_schedule.py` | `output_times`, `interval`, `count` |
| `scripts/checkpoint_planner.py` | `checkpoint_interval`, `checkpoints`, `overhead_fraction` |

## Workflow

1. **Get stability limits** - Use numerical-stability skill
2. **Plan time stepping** - Run `scripts/timestep_planner.py`
3. **Schedule outputs** - Run `scripts/output_schedule.py`
4. **Plan checkpoints** - Run `scripts/checkpoint_planner.py`
5. **Monitor during run** - Adjust dt if limits change

## Conversational Workflow Example

**User**: I'm running a 10-hour phase-field simulation. How often should I checkpoint?

**Agent workflow**:
1. Plan checkpoints based on acceptable lost work:
   ```bash
   python3 scripts/checkpoint_planner.py --run-time 36000 --checkpoint-cost 120 --max-lost-time 1800 --json
   ```
2. Interpret: Checkpoint every 30 minutes, overhead ~0.7%, max 30 min lost work on crash.

## Pre-Run Checklist

- [ ] Confirm dt limits from stability analysis
- [ ] Define ramping strategy for transient startup
- [ ] Choose output interval consistent with physics time scales
- [ ] Plan checkpoints based on restart risk
- [ ] Re-evaluate dt after parameter changes

## CLI Examples

```bash
# Plan time stepping with ramping
python3 scripts/timestep_planner.py --dt-target 1e-4 --dt-limit 2e-4 --safety 0.8 --ramp-steps 10 --json

# Schedule output times
python3 scripts/output_schedule.py --t-start 0 --t-end 10 --interval 0.1 --json

# Plan checkpoints for long run
python3 scripts/checkpoint_planner.py --run-time 36000 --checkpoint-cost 120 --max-lost-time 1800 --json
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `dt-target must be positive` | Invalid time step | Use positive value |
| `t-end must be > t-start` | Invalid time range | Check time bounds |
| `checkpoint-cost must be < run-time` | Checkpoint too expensive | Reduce checkpoint size |

## Interpretation Guidance

### dt Behavior

| Observation | Meaning | Action |
|-------------|---------|--------|
| dt stable at target | Good | Continue |
| dt shrinking | Stability issue | Check CFL, reduce target |
| dt oscillating | Borderline stability | Add safety factor |

### Checkpoint Overhead

| Overhead | Acceptability |
|----------|---------------|
| < 1% | Excellent |
| 1-5% | Good |
| 5-10% | Acceptable |
| > 10% | Too frequent, increase interval |

## Limitations

- **Not adaptive control**: Plans static schedules, not runtime adaptation
- **Assumes constant physics**: If parameters change, re-plan

## References

- `references/cfl_coupling.md` - Combining multiple stability limits
- `references/ramping_strategies.md` - Startup policies
- `references/output_checkpoint_guidelines.md` - Cadence rules

## Version History

- **v1.1.0** (2024-12-24): Enhanced documentation, decision guidance, examples
- **v1.0.0**: Initial release with 3 planning scripts
