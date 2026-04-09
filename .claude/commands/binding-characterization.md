# binding-characterization

> Guidance for SPR and BLI binding characterization experiments. Use when: (1) Planning binding kinetics experiments, (2) Troubleshooting poor/no binding signal, (3) Interpreting kinetic data artifacts, (4) Choosing between SPR vs BLI platforms.

# Binding Characterization: SPR and BLI

## SPR vs BLI Decision Matrix

| Factor | Choose SPR | Choose BLI |
|--------|------------|------------|
| **Sensitivity** | Small molecules, fragments (<500 Da) | Large complexes, antibodies |
| **Throughput** | Low-medium (serial) | High (96-well parallel) |
| **Sample purity** | Required (clogs fluidics) | Tolerates crude lysates |
| **Kinetic resolution** | Higher (better for fast kinetics) | Lower |
| **Mass transport** | More sensitive (may distort kon) | Less sensitive |
| **Maintenance** | High (fluidics system) | Low (dip-and-read) |
| **Sample consumption** | Higher (continuous flow) | Lower |
| **Cost per experiment** | Lower chip cost, higher run cost | Higher tip cost, lower run cost |

## Key differences

### SPR (Surface Plasmon Resonance)
- **Mechanism**: Detects refractive index changes at gold surface
- **Surface**: Gold chip with dextran matrix (CM5, CM7, etc.)
- **Flow**: Continuous microfluidics
- **Best for**: Small molecules, high-affinity, precise kon/koff

### BLI (Biolayer Interferometry)
- **Mechanism**: Measures optical interference pattern shift
- **Surface**: Fiber optic biosensor tips (SA, Ni-NTA, AHC)
- **Flow**: Dip-and-read (no microfluidics)
- **Best for**: High-throughput, crude samples, antibody screening

---

## Troubleshooting: Why BLI works but SPR doesn't

| Cause | Mechanism | Solution |
|-------|-----------|----------|
| **Hydrophobic CDRs** | Adsorb to SPR gold/dextran surface | Add 0.05% Tween-20, use CM7 chip with longer dextran |
| **Aggregation** | Mass transport artifacts in SPR fluidics | Filter sample (0.22μm), reduce ligand density |
| **High instability** | Degrades during continuous flow | Shorter cycle time, add stabilizers (trehalose 5%) |
| **Charge mismatch** | Nonspecific binding to charged dextran | Adjust buffer pH ±1 from pI, add BSA 1mg/mL |
| **Slow dissociation** | Long regeneration needed (damages ligand) | Use BLI (disposable tips) |

### Why SPR works but BLI doesn't

| Cause | Mechanism | Solution |
|-------|-----------|----------|
| **Small analyte** | BLI less sensitive for <10 kDa | Use SPR with appropriate chip |
| **Weak affinity (KD >10μM)** | Fast dissociation in BLI dip | Increase analyte concentration |
| **Low expression** | Not enough signal | Increase biosensor loading |

---

## Mass transport considerations

Mass transport limitation occurs when analyte cannot diffuse to the surface fast enough to maintain equilibrium. This distorts kinetic parameters.

### Symptoms
- Observed kon appears slower than true kon
- Linear association phase (instead of exponential)
- kon varies with ligand density
- Rmax varies with flow rate

### When mass transport matters
- **High-affinity interactions** (kon >10^6 M^-1s^-1)
- **High ligand density** (>500 RU)
- **Slow flow rates** (<30 μL/min in SPR)
- **Large analytes** (slow diffusion)

### Mitigation strategies

| Strategy | SPR | BLI |
|----------|-----|-----|
| Reduce ligand density | <200 RU for high-affinity | <0.5 nm shift loading |
| Increase flow rate | 50-100 μL/min | Increase shake speed (1000 rpm) |
| Use oriented immobilization | His-tag capture | Biotinylated ligand |
| Include in fitting | Mass transport model (kt) | Usually less critical |

---

## Nonspecific binding mitigation

### Buffer additives (ranked by effectiveness)

| Additive | Concentration | Mechanism | Best For |
|----------|---------------|-----------|----------|
| BSA | 0.5-1 mg/mL | Blocks hydrophobic sites | General use |
| Tween-20 | 0.02-0.05% | Prevents surface adsorption | Hydrophobic analytes |
| Trehalose | 1-5% | Stabilizes + blocks | Unstable proteins |
| Sucrose | 5% | BLI-specific blocker | BLI tips |
| Carboxymethyl dextran | 1 mg/mL | Competitive blocking | SPR with charged proteins |
| NaCl | 150-500 mM | Reduces ionic interactions | Charged proteins |

### pH optimization
- Keep buffer pH at least 1 unit away from analyte pI
- pI near 7: Use pH 6.0 or 8.0 buffer
- Acidic proteins (pI <5): Use neutral or basic buffer
- Basic proteins (pI >9): Use slightly acidic buffer

### Reference subtraction
**Always include**:
- Blank reference channel (no ligand)
- Buffer-only injections
- Non-specific binding controls

---

## Regeneration conditions

### SPR regeneration scouting (try in order)

| Condition | Targets | Caution |
|-----------|---------|---------|
| 10 mM Glycine pH 2.0-2.5 | Most protein-protein | May denature ligand |
| 10 mM Glycine pH 1.5 | Strong interactions | Harsh, limit exposure |
| 1-2 M NaCl | Ionic interactions | Mild, try first |
| 10 mM NaOH | Very stable ligands | Can hydrolyze proteins |
| 10 mM Glycine pH 9-10 | Acid-stable proteins | Can aggregate |
| 10 mM EDTA | His-tag, metal-dependent | Strips Ni-NTA |
| 4 M MgCl2 | Hydrophobic interactions | Check ligand stability |

### Regeneration protocol
1. Start with mildest condition (high salt)
2. Test 30s contact time
3. Verify complete dissociation (return to baseline)
4. Verify retained ligand activity (repeat binding)
5. Use shortest effective contact time

### BLI tips
- Tips are often disposable (no regeneration needed)
- For reuse: Same conditions as SPR, but shorter exposure
- Anti-His tips: 10 mM Glycine pH 1.5, 30s
- Streptavidin tips: Generally not regenerable

---

## Common artifacts and solutions

### Biphasic binding
**Symptoms**: Two-rate association or dissociation
**Causes**:
- Sample heterogeneity (aggregates)
- Ligand heterogeneity (multiple conformations)
- Avidity effects (bivalent analyte)

**Solutions**:
- Filter/centrifuge sample
- Use monovalent Fab fragments
- Reduce ligand density
- Fit to heterogeneous model

### Negative dissociation
**Symptoms**: Signal increases during dissociation phase
**Causes**:
- Ligand leaching from surface
- Analyte aggregation on surface
- Reference channel drift

**Solutions**:
- Use capture antibody instead of direct immobilization
- Increase buffer stringency
- Better reference subtraction

### Hook effect
**Symptoms**: Signal decreases at high analyte concentrations
**Causes**:
- Surface saturation + rebinding suppression
- Crowding effects

**Solutions**:
- Reduce analyte concentration range
- Reduce ligand density
- Use smaller analyte fragments

---

## Kinetic data quality checklist

### Before analysis
- [ ] Reference-subtracted properly
- [ ] Buffer injection shows flat baseline
- [ ] Rmax consistent across concentrations
- [ ] No systematic drift during association
- [ ] Complete regeneration (return to baseline)
- [ ] Duplicate/triplicate injections consistent

### Fitting quality
- [ ] Residuals randomly distributed (no systematic deviation)
- [ ] Chi² < 10% of Rmax (or < 1 RU² for low signals)
- [ ] kon and koff errors < 20% of values
- [ ] KD from kinetics matches equilibrium KD (within 3-fold)
- [ ] Fitted Rmax reasonable (close to theoretical)

### Red flags
- kon approaching mass transport limit (>10^7 M^-1s^-1)
- koff faster than data acquisition (< 0.01 s^-1 requires faster sampling)
- Rmax >> theoretical maximum (aggregation or avidity)
- Large difference between kinetic and equilibrium KD

---

## References

### Platform comparisons
- [BLI vs SPR Comparison - Sartorius](https://www.sartorius.hr/en/news/blog/bli-vs-spr-choosing-the-ideal-method-for-analyzing-biomolecular-interactions/)
- [BLI vs SPR - Nicoya](https://nicoyalife.com/blog/biolayer-interferometry-vs-surface-plasmon-resonance/)

### SPR protocols
- [SPR Guidelines - van der Merwe, Oxford](https://www.path.ox.ac.uk/wp-content/uploads/2023/09/SPR-guidelines-1.pdf)
- [SPR Experiment Guide - Duke DHVI](https://dhvi.duke.edu/sites/default/files/2022-08/SPR%20Experiment%20Guide%20v1.3.pdf)

### Troubleshooting
- [4 Ways to Reduce NSB in SPR - Nicoya](https://nicoyalife.com/blog/4-ways-reduce-non-specific-binding-spr/)
- [3 Ways to Limit Mass Transfer Effects - Nicoya](https://nicoyalife.com/blog/3-ways-to-limit-mass-transfer-effects/)
- [Suppressing NSB in BLI - ACS Omega](https://pubs.acs.org/doi/10.1021/acsomega.1c05659)

### Regeneration
- [SPR Regeneration - SPRpages](https://www.sprpages.nl/kinetics/regeneration)
- [Mastering Regeneration - Nicoya](https://nicoyalife.com/blog/regeneration-buffer-spr-experiment/)

### Mass transport
- [Mass Transport Limitation in SPR - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4134667/)
- [Mass-Transfer Kinetics - SPRpages](https://www.sprpages.nl/data-fitting/kinetic-models/mass-transfer)
