# performance-profiling

> Identify computational bottlenecks, analyze scaling behavior, estimate memory requirements, and receive optimization recommendations for any computational simulation. Use when simulations are slow, investigating parallel efficiency, planning resource allocation, or seeking performance improvements through timing analysis, scaling studies, memory profiling, or bottleneck detection.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Performance Profiling

## Goal

Provide tools to analyze simulation performance, identify bottlenecks, and recommend optimization strategies for computational materials science simulations.

## Requirements

- Python 3.8+
- No external dependencies (uses Python standard library only)
- Works on Linux, macOS, and Windows

## Inputs to Gather

Before running profiling scripts, collect from the user:

| Input | Description | Example |
|-------|-------------|---------|
| Simulation log | Log file with timing information | `simulation.log` |
| Scaling data | JSON with multi-run performance data | `scaling_data.json` |
| Simulation parameters | JSON with mesh, fields, solver config | `params.json` |
| Available memory | System memory in GB (optional) | `16.0` |

## Decision Guidance

### When to Use Each Script

```
Need to identify slow phases?
├── YES → Use timing_analyzer.py
│         └── Parse simulation logs for timing data
│
Need to understand parallel performance?
├── YES → Use scaling_analyzer.py
│         └── Analyze strong or weak scaling efficiency
│
Need to estimate memory requirements?
├── YES → Use memory_profiler.py
│         └── Estimate memory from problem parameters
│
Need optimization recommendations?
└── YES → Use bottleneck_detector.py
          └── Combine analyses and get actionable advice
```

### Choosing Analysis Thresholds

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Phase dominance | <30% | 30-50% | >50% |
| Parallel efficiency | >0.80 | 0.70-0.80 | <0.70 |
| Memory usage | <60% | 60-80% | >80% |

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `timing_analyzer.py` | `timing_data.phases`, `timing_data.slowest_phase`, `timing_data.total_time` |
| `scaling_analyzer.py` | `scaling_analysis.results`, `scaling_analysis.efficiency_threshold_processors` |
| `memory_profiler.py` | `memory_profile.total_memory_gb`, `memory_profile.per_process_gb`, `memory_profile.warnings` |
| `bottleneck_detector.py` | `bottlenecks`, `recommendations` |

## Workflow

### Complete Profiling Workflow

1. **Analyze timing** from simulation logs
2. **Analyze scaling** from multi-run data (if available)
3. **Profile memory** from simulation parameters
4. **Detect bottlenecks** and get recommendations
5. **Implement optimizations** based on recommendations
6. **Re-profile** to verify improvements

### Quick Profiling (Timing Only)

1. **Run timing analyzer** on simulation log
2. **Identify dominant phases** (>50% of runtime)
3. **Apply targeted optimizations** to dominant phases

## CLI Examples

### Timing Analysis

```bash
# Basic timing analysis
python3 scripts/timing_analyzer.py \
    --log simulation.log \
    --json

# Custom timing pattern
python3 scripts/timing_analyzer.py \
    --log simulation.log \
    --pattern 'Step\s+(\w+)\s+took\s+([\d.]+)s' \
    --json
```

### Scaling Analysis

```bash
# Strong scaling (fixed problem size)
python3 scripts/scaling_analyzer.py \
    --data scaling_data.json \
    --type strong \
    --json

# Weak scaling (constant work per processor)
python3 scripts/scaling_analyzer.py \
    --data scaling_data.json \
    --type weak \
    --json
```

### Memory Profiling

```bash
# Estimate memory requirements
python3 scripts/memory_profiler.py \
    --params simulation_params.json \
    --available-gb 16.0 \
    --json
```

### Bottleneck Detection

```bash
# Detect bottlenecks from timing only
python3 scripts/bottleneck_detector.py \
    --timing timing_results.json \
    --json

# Comprehensive analysis with all inputs
python3 scripts/bottleneck_detector.py \
    --timing timing_results.json \
    --scaling scaling_results.json \
    --memory memory_results.json \
    --json
```

## Conversational Workflow Example

**User**: My simulation is taking too long. Can you help me identify what's slow?

**Agent workflow**:
1. Ask for simulation log file
2. Run timing analyzer:
   ```bash
   python3 scripts/timing_analyzer.py --log simulation.log --json
   ```
3. Interpret results:
   - If solver dominates (>50%): Recommend preconditioner tuning
   - If assembly dominates: Recommend caching or vectorization
   - If I/O dominates: Recommend reducing output frequency
4. If user has multi-run data, analyze scaling:
   ```bash
   python3 scripts/scaling_analyzer.py --data scaling.json --type strong --json
   ```
5. Generate comprehensive recommendations:
   ```bash
   python3 scripts/bottleneck_detector.py --timing timing.json --scaling scaling.json --json
   ```

## Interpretation Guidance

### Timing Analysis

| Scenario | Meaning | Action |
|----------|---------|--------|
| Solver >70% | Solver-dominated | Tune preconditioner, check tolerance |
| Assembly >50% | Assembly-dominated | Cache matrices, vectorize, parallelize |
| I/O >30% | I/O-dominated | Reduce frequency, use parallel I/O |
| Balanced (<30% each) | Well-balanced | Look for algorithmic improvements |

### Scaling Analysis

| Efficiency | Meaning | Action |
|------------|---------|--------|
| >0.80 | Excellent scaling | Continue scaling up |
| 0.70-0.80 | Good scaling | Monitor at larger scales |
| 0.50-0.70 | Poor scaling | Investigate communication/load balance |
| <0.50 | Very poor scaling | Reduce processor count or redesign |

### Memory Profile

| Usage | Meaning | Action |
|-------|---------|--------|
| <60% available | Safe | No action needed |
| 60-80% available | Moderate | Monitor, consider optimization |
| >80% available | High | Reduce resolution or increase processors |
| >100% available | Exceeds capacity | Must reduce problem size |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Log file not found` | Invalid path | Verify log file path |
| `No timing data found` | Pattern mismatch | Provide custom pattern with --pattern |
| `At least 2 runs required` | Insufficient data | Provide more scaling runs |
| `Missing required parameters` | Incomplete params | Add mesh and fields to params file |

## Optimization Strategies by Bottleneck Type

### Solver Bottlenecks
- Use algebraic multigrid (AMG) preconditioner
- Tighten solver tolerance if over-solving
- Consider direct solver for small problems
- Profile matrix assembly vs solve time

### Assembly Bottlenecks
- Cache element matrices if geometry is static
- Use vectorized assembly routines
- Consider matrix-free methods
- Parallelize assembly with coloring

### I/O Bottlenecks
- Reduce output frequency
- Use parallel I/O (HDF5, MPI-IO)
- Write to fast scratch storage
- Compress output data

### Scaling Bottlenecks
- Investigate communication overhead
- Check for load imbalance
- Reduce synchronization points
- Use asynchronous communication
- Consider hybrid MPI+OpenMP

### Memory Bottlenecks
- Reduce mesh resolution
- Use iterative solver (lower memory than direct)
- Enable out-of-core computation
- Increase number of processors
- Use single precision where appropriate

## Limitations

- **Log parsing**: Depends on pattern matching; may miss unusual formats
- **Scaling analysis**: Requires at least 2 runs for meaningful results
- **Memory estimation**: Approximate; actual usage may vary
- **Recommendations**: General guidance; may need domain-specific tuning

## References

- `references/profiling_guide.md` - Profiling concepts and interpretation
- `references/optimization_strategies.md` - Detailed optimization approaches

## Version History

- **v1.0.0** (2025-01-22): Initial release with 4 profiling scripts
