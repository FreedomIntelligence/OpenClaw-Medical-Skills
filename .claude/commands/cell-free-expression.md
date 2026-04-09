# cell-free-expression

> Guidance for cell-free protein synthesis (CFPS) optimization. Use when: (1) Planning CFPS experiments, (2) Troubleshooting low yield or aggregation, (3) Optimizing DNA template design for CFPS, (4) Expressing difficult proteins (disulfide-rich, toxic, membrane).

# Cell-Free Protein Synthesis (CFPS)

## System Selection Guide

| System | Best For | Yield | PTMs | Disulfides | Cost |
|--------|----------|-------|------|------------|------|
| **E. coli extract** | Rapid prototyping, prokaryotic proteins | High (100-400 μg/mL) | None | Poor (reducing) | Low |
| **E. coli PURE** | Defined conditions, unnatural AAs | Medium (50-150 μg/mL) | None | Controllable | High |
| **Wheat germ** | Eukaryotic proteins, membrane proteins | High (100-500 μg/mL) | Limited | Moderate | Medium |
| **Rabbit reticulocyte** | Mammalian proteins, post-translational studies | Low (10-50 μg/mL) | Some | Poor | High |
| **Insect (Sf21)** | Glycoproteins, complex folds | Medium (50-100 μg/mL) | Glycosylation | Good | High |
| **HeLa/CHO** | Native mammalian proteins | Low (10-50 μg/mL) | Full mammalian | Good | Very High |

---

## CFPS Troubleshooting Matrix

| Problem | Likely Causes | Design Fix | Reagent Fix |
|---------|---------------|------------|-------------|
| **No expression** | Rare codons at N-terminus, poor RBS | Codon optimize first 30 codons | Use BL21-CodonPlus extract |
| **Low yield** | Strong mRNA secondary structure, template issues | Optimize 5' UTR (ΔG > -5 kcal/mol) | Increase Mg²⁺ (10-18 mM), ATP |
| **Aggregation** | Hydrophobic protein, fast translation | Add solubility tags (MBP, SUMO) | Add 0.1% Tween-20, chaperones |
| **Inactive protein** | Misfolding, missing cofactors | Slow translation (use rare codons!) | Add GroEL/ES, DnaK/J |
| **Truncation** | Rare codon clusters, mRNA instability | Remove AGG/AGA/CUA clusters | Supplement rare tRNAs |
| **Degradation** | Proteolysis | N-terminal Met-Ala | Add protease inhibitors |

---

## Codon Optimization for CFPS

### Codons to Avoid in E. coli CFPS

| Codon | Amino Acid | Issue | tRNA Abundance |
|-------|------------|-------|----------------|
| AGG | Arg | Very rare, stalling | 0.2% |
| AGA | Arg | Very rare, stalling | 0.4% |
| CUA | Leu | Low abundance | 0.4% |
| AUA | Ile | Rare | 0.5% |
| CGA | Arg | Inefficient decoding | 0.6% |
| CCC | Pro | Can cause pausing | 0.5% |
| GGA | Gly | Moderate | 1.1% |

### Design Rules

1. **First 30 codons**: Most critical - use only high-frequency codons
2. **Rare codon clusters**: Avoid 2+ rare codons within 10 nt
3. **Rare codon content**: Keep overall <5% of coding sequence
4. **GC content**: Target 40-60% for balanced expression
5. **Avoid runs**: No >6 consecutive G or C residues (secondary structure)
6. **Strategic slow codons**: Place rare codons between domains (aids folding!)

### When to Use Rare Codons
- Domain boundaries (allow cotranslational folding)
- Before complex structural elements
- When protein is prone to misfolding

---

## mRNA Template Design

### 5' UTR Optimization

| Element | Optimal Design | Impact |
|---------|----------------|--------|
| **RBS (SD sequence)** | AGGAGG, 7-9 nt from start | Ribosome binding |
| **Spacing** | 7 nt between SD and AUG | Translation initiation |
| **Secondary structure** | ΔG > -5 kcal/mol | Accessibility |
| **Upstream AUG** | Avoid (causes false starts) | Reduces truncations |

### Secondary Structure Targets

| Region | Ideal ΔG | Impact |
|--------|----------|--------|
| -30 to +30 around AUG | > -5 kcal/mol | Translation initiation |
| Full 5' UTR | > -10 kcal/mol | Ribosome loading |
| RBS accessibility | Unpaired | Critical |

### Template Format

| Format | Advantages | Disadvantages |
|--------|------------|---------------|
| **Plasmid** | Stable, high yield | Requires cloning |
| **Linear PCR** | Fast, no cloning | May need stabilization |
| **mRNA** | Direct translation | Unstable, expensive |

---

## Disulfide Bond Formation

### System Capabilities

| System | Native Disulfide Support | Additives Needed |
|--------|--------------------------|------------------|
| Standard E. coli extract | Poor (DTT present) | IAM, PDI, GSSG/GSH |
| Oxidizing E. coli extract | Good | Pre-oxidized glutathione |
| Wheat germ | Moderate | Lower DTT, add PDI |
| PURE system | Minimal | Full oxidative system |
| Insect/Mammalian | Good | Microsome membranes |

### Oxidative Folding Protocol (E. coli extract)

```
1. Deplete DTT from extract (dialysis or treatment with IAM 5 mM)
2. Add oxidized/reduced glutathione: 4 mM GSSG, 1 mM GSH (4:1 ratio)
3. Add 10 μM PDI (protein disulfide isomerase)
4. Optional: Add 5 μM DsbC (disulfide isomerase)
5. Express at 25°C (not 37°C) for better folding
6. Incubation time: 4-6 hours
```

### Disulfide-Rich Protein Tips
- Start with wheat germ or oxidizing extract
- Use PURE system for precise control
- Consider co-expression of PDI/DsbC
- Verify by non-reducing SDS-PAGE

---

## Expression Prediction from Sequence

| Feature | Good | Marginal | Bad |
|---------|------|----------|-----|
| **Rare codon content** | <3% | 3-8% | >10% |
| **First 30 codons rare** | 0 | 1-2 | >2 |
| **GC content** | 45-55% | 35-45% or 55-65% | <30% or >70% |
| **5' UTR ΔG** | > -3 kcal/mol | -3 to -8 | < -10 kcal/mol |
| **Hydrophobic stretches** | <5 consecutive | 5-7 | >8 consecutive |
| **N-terminal residue** | Met-Ala, Met-Ser, Met-Gly | Met-Val, Met-Thr | Met-Arg, Met-Lys |
| **Cysteine pairs** | Paired (even number) | Mixed | Odd number (free thiols) |

---

## Solubility Enhancement Strategies

### Fusion Tags (ranked by effectiveness)

| Tag | Size | Solubility Enhancement | Cleavage | Notes |
|-----|------|------------------------|----------|-------|
| **MBP** | 40 kDa | Excellent | TEV, Factor Xa | Best overall |
| **SUMO** | 11 kDa | Very Good | SUMO protease | Native N-terminus after cleavage |
| **NusA** | 55 kDa | Excellent | - | Large size |
| **Trx** | 12 kDa | Good | Enterokinase | For disulfide proteins |
| **GST** | 26 kDa | Moderate | - | Dimeric |
| **His₆** | 1 kDa | Minimal | - | Mainly for purification |

### Buffer Additives for Solubility

| Additive | Concentration | Mechanism |
|----------|---------------|-----------|
| Trehalose | 50-100 mM | Chemical chaperone |
| Glycerol | 5-10% | Reduces hydrophobic aggregation |
| L-Arginine | 50-100 mM | Suppresses aggregation |
| Tween-20 | 0.05-0.1% | Prevents surface adsorption |
| Proline | 50 mM | Osmolyte stabilization |

### Chaperone Supplementation

| Chaperone System | Target Problem | Concentration |
|------------------|----------------|---------------|
| GroEL/GroES | General folding | 1-2 μM |
| DnaK/DnaJ/GrpE | Aggregation-prone | 1 μM each |
| Trigger Factor | Nascent chain | 1-2 μM |
| ClpB | Aggregate resolubilization | 0.5 μM |

---

## Temperature Optimization

| Temperature | Use Case | Trade-offs |
|-------------|----------|------------|
| **37°C** | Fast expression, stable proteins | Higher aggregation risk |
| **30°C** | Balanced (default) | Good compromise |
| **25°C** | Disulfide proteins, complex folds | Slower, better folding |
| **18-20°C** | Aggregation-prone proteins | Much slower, best folding |
| **16°C** | Cold-shock proteins | Very slow, specialized |

---

## E. coli Extract Preparation (Key Variables)

| Variable | Impact | Optimal Range |
|----------|--------|---------------|
| **Cell density at harvest** | Ribosome content | OD₆₀₀ 2.5-3.5 |
| **Lysis method** | Extract activity | Sonication, bead beating |
| **Run-off reaction** | Removes endogenous mRNA | 20-80 min at 37°C |
| **Mg²⁺ concentration** | Translation fidelity | 10-18 mM |
| **K⁺ concentration** | Translation rate | 150-200 mM |
| **Energy system** | Sustained synthesis | ATP/GTP, creatine phosphate |

---

## PURE System Specifics

### Advantages
- Defined composition (no proteases/nucleases)
- Linear DNA templates work well
- Unnatural amino acid incorporation
- Reproducible between batches

### Limitations
- No chaperones (add separately)
- No post-translational modifications
- Lower yields than crude extracts
- Higher cost

### When to Use PURE
- Unnatural amino acid incorporation
- Studying translation mechanisms
- "Clean" proteins needed
- Protease-sensitive targets
- Linear template expression

---

## Common Artifacts and Solutions

### Low Molecular Weight Bands
**Causes**: Premature termination, proteolysis, internal initiation
**Solutions**:
- Optimize rare codon clusters
- Add protease inhibitors
- Check for internal AUG codons
- Use PURE system

### Higher MW Bands
**Causes**: Incomplete termination, read-through, aggregation
**Solutions**:
- Ensure strong stop codon (UAA preferred)
- Check template 3' end
- Add release factors (RF1/RF2)
- Reduce protein concentration

### No Soluble Protein
**Causes**: Aggregation during synthesis
**Solutions**:
- Lower temperature (25°C → 18°C)
- Add chaperones
- Use solubility tag
- Optimize translation rate

---

## References

### CFPS Overview
- [User's Guide to CFPS - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6481089/)
- [Optimising Protein Synthesis in Cell-Free Systems - PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9996726/)
- [CFPS Systems Comparison - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8258279/)

### Extract Preparation
- [Crude Extract Preparation - MDPI Methods](https://www.mdpi.com/2409-9279/2/3/68)
- [Simple Rapid Cell-Free Lysate - PLOS One](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0165137)
- [High-Throughput Extract Preparation - Nature Scientific Reports](https://www.nature.com/articles/srep08663)

### PURE System
- [PURE System Evolution - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10521753/)
- [PURE System for Membrane Proteins - Nature Protocols](https://www.nature.com/articles/nprot.2015.082)

### Wheat Germ
- [Wheat Germ Systems Review - FEBS Letters](https://febs.onlinelibrary.wiley.com/doi/10.1016/j.febslet.2014.05.061)
- [Wheat Germ for Structural Biology - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8027086/)

### Codon Optimization
- [Rare Codons and Solubility - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2723077/)
- [Codon Influence on Expression - Nature](https://www.nature.com/articles/nature16509)
- [Synonymous Codon Substitutions Perturb Folding - PNAS](https://www.pnas.org/doi/10.1073/pnas.1907126117)

### Disulfide Formation
- [Oxidative Protein Folding in ER - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4312752/)
- [PDI-Regulated Disulfide Formation - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7794689/)

### Solubility Tags
- [SUMO Fusion for Difficult Proteins - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7129290/)
- [Fusion Tags Review - Frontiers Microbiol](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2014.00063/full)

### Temperature Effects
- [Cold Shock Promoters - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9800685/)
- [Strategies to Optimize E. coli Expression - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7162232/)
