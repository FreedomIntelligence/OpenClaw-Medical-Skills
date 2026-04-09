# mesh-generation

> Plan and evaluate mesh generation for numerical simulations. Use when choosing grid resolution, checking aspect ratios/skewness, estimating mesh quality constraints, or planning adaptive mesh refinement for PDE discretization.

**Available tools:** R, e, a, d, ,,  , B, s, h, W, r, i, t, G, p, l, o, b

# Mesh Generation

## Goal

Provide a consistent workflow for selecting mesh resolution and checking mesh quality for PDE simulations.

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib)

## Inputs to Gather

| Input | Description | Example |
|-------|-------------|---------|
| Domain size | Physical dimensions | `1.0 × 1.0 m` |
| Feature size | Smallest feature to resolve | `0.01 m` |
| Points per feature | Resolution requirement | `10 points` |
| Aspect ratio limit | Maximum dx/dy ratio | `5:1` |
| Quality threshold | Skewness limit | `< 0.8` |

## Decision Guidance

### Resolution Selection

```
What is the smallest feature size?
├── Interface width → dx ≤ width / 5
├── Boundary layer → dx ≤ layer_thickness / 10
├── Wave length → dx ≤ lambda / 20
└── Diffusion length → dx ≤ sqrt(D × dt) / 2
```

### Mesh Type Selection

| Problem | Recommended Mesh |
|---------|------------------|
| Simple geometry, uniform | Structured Cartesian |
| Complex geometry | Unstructured triangular/tetrahedral |
| Boundary layers | Hybrid (structured near walls) |
| Adaptive refinement | Quadtree/Octree or AMR |

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `scripts/grid_sizing.py` | `dx`, `nx`, `ny`, `nz`, `notes` |
| `scripts/mesh_quality.py` | `aspect_ratio`, `skewness`, `quality_flags` |

## Workflow

1. **Estimate resolution** - From physics scales
2. **Compute grid sizing** - Run `scripts/grid_sizing.py`
3. **Check quality metrics** - Run `scripts/mesh_quality.py`
4. **Adjust if needed** - Fix aspect ratios, reduce skewness
5. **Validate** - Mesh convergence study

## Conversational Workflow Example

**User**: I need to mesh a 1mm × 1mm domain for a phase-field simulation with interface width of 10 μm.

**Agent workflow**:
1. Compute grid sizing:
   ```bash
   python3 scripts/grid_sizing.py --length 0.001 --resolution 200 --json
   ```
2. Verify interface is resolved: dx = 5 μm, interface width = 10 μm → 2 points per interface width.
3. Recommend: Increase to 500 points (dx = 2 μm) for 5 points across interface.

## Pre-Mesh Checklist

- [ ] Define target resolution per feature/interface
- [ ] Ensure dx meets stability constraints (see numerical-stability)
- [ ] Check aspect ratio < limit (typically 5:1)
- [ ] Check skewness < threshold (typically 0.8)
- [ ] Validate mesh convergence with refinement study

## CLI Examples

```bash
# Compute grid sizing for 1D domain
python3 scripts/grid_sizing.py --length 1.0 --resolution 200 --json

# Check mesh quality
python3 scripts/mesh_quality.py --dx 1.0 --dy 0.5 --dz 0.5 --json

# High aspect ratio check
python3 scripts/mesh_quality.py --dx 1.0 --dy 0.1 --json
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `length must be positive` | Invalid domain size | Use positive value |
| `resolution must be > 1` | Insufficient points | Use at least 2 |
| `dx, dy must be positive` | Invalid spacing | Use positive values |

## Interpretation Guidance

### Aspect Ratio

| Aspect Ratio | Quality | Impact |
|--------------|---------|--------|
| 1:1 | Excellent | Optimal accuracy |
| 1:1 - 3:1 | Good | Acceptable |
| 3:1 - 5:1 | Fair | May affect accuracy |
| > 5:1 | Poor | Solver issues likely |

### Skewness

| Skewness | Quality | Impact |
|----------|---------|--------|
| 0 - 0.25 | Excellent | Optimal |
| 0.25 - 0.50 | Good | Acceptable |
| 0.50 - 0.80 | Fair | May affect accuracy |
| > 0.80 | Poor | Likely problems |

### Resolution Guidelines

| Application | Points per Feature |
|-------------|-------------------|
| Phase-field interface | 5-10 |
| Boundary layer | 10-20 |
| Shock | 3-5 (with capturing) |
| Wave propagation | 10-20 per wavelength |
| Smooth gradients | 5-10 |

## Limitations

- **2D/3D only**: No unstructured mesh generation
- **Quality metrics**: Basic aspect ratio and skewness only
- **No mesh generation**: Sizing recommendations only

## References

- `references/mesh_types.md` - Structured vs unstructured
- `references/quality_metrics.md` - Aspect ratio/skewness thresholds

## Version History

- **v1.1.0** (2024-12-24): Enhanced documentation, decision guidance, examples
- **v1.0.0**: Initial release with 2 mesh quality scripts
