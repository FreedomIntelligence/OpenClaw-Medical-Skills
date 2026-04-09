# claw-ancestry-pca

> Ancestry decomposition PCA against the Simons Genome Diversity Project

# 🦖 Ancestry Decomposition PCA

Place your study cohort in global genetic context by computing a joint PCA against the Simons Genome Diversity Project (SGDP) — 345 samples from 164 populations spanning every inhabited continent.

## What it does

1. Takes your VCF + population map as input
2. Finds common variants between your cohort and the SGDP reference panel (bundled)
3. Runs PLINK PCA on the merged dataset
4. Separates your cohort from SGDP reference samples
5. Matches SGDP samples to their population labels (164 populations)
6. Generates a publication-quality multi-panel figure:
   - **Panel A**: PC1 vs PC2 — main population structure of your cohort
   - **Panel B**: PC3 vs PC2 with regional groupings and confidence ellipses
   - **Panel C**: PC3 vs PC1 with language/cultural groupings
   - **Panel D**: Global context — your samples (circles) vs SGDP (triangles)
7. Produces a markdown report with variance explained, population assignments, and reproducibility bundle

## Why this exists

If you ask ChatGPT to "run a PCA against a global reference panel," it will:
- Not know which reference panel to use
- Hallucinate PLINK flags for merging datasets with different variant sets
- Skip IBD removal (related individuals distort PCA)
- Not normalise contig names between your VCF and the reference
- Produce a single scatter plot with no population labels

This skill encodes the correct methodological decisions:
- Uses SGDP (the gold-standard reference for global diversity)
- Handles contig normalisation (chr1 vs 1)
- Filters to common biallelic SNPs shared between datasets
- Removes related individuals via IBD checks
- Produces publication-quality multi-panel figures with confidence ellipses
- Differentiates your samples (circles) from reference (triangles)

## Reference Panel

The skill bundles the SGDP v4 dataset (Mallick et al., 2016, Nature):
- 345 samples from 164 populations
- Whole-genome sequencing at high coverage
- MAF > 0.1% filter applied
- Populations span: Africa, Americas, Central/South Asia, East Asia, Europe, Middle East, Oceania

## Usage

```bash
python ancestry_pca.py \
    --vcf your_cohort.vcf.gz \
    --pop-map your_populations.tsv \
    --output ancestry_report
```

### Demo (works out of the box)

```bash
python ancestry_pca.py --demo --output demo_report
```

The demo uses pre-computed PCA results from the Peruvian Genome Project (736 samples, 28 populations) and generates the full 4-panel figure instantly.

## Example Output

```
Ancestry Decomposition PCA
==========================
Cohort: 736 samples, 28 populations
Reference: SGDP (345 samples, 164 populations)
Common variants: 42,831 biallelic SNPs

Variance explained:
  PC1: 51.44%  PC2: 21.70%  PC3: 6.70%

Panel D — Global Context:
  Cohort samples cluster between European and East Asian
  reference populations, with Amazonian groups showing
  distinct positioning from Highland and Coastal groups.

Figures saved to: ancestry_report/
  Figure3_PCA_composite.png (300 dpi)
  Figure3_PCA_composite.pdf (vector)

Reproducibility:
  commands.sh | environment.yml | checksums.sha256
```

## Interpretation Guide

- **PC1** typically captures the largest axis of global differentiation (often Africa vs non-Africa)
- **PC2** separates major continental groups (Europe, East Asia, Americas)
- **PC3** often reveals finer substructure within continental groups
- Confidence ellipses show 2.5 standard deviations around each population cluster
- Your samples shown as **circles**, SGDP reference as **triangles**

## Citation

If you use this skill in a publication, please cite:

- Mallick, S. et al. (2016). The Simons Genome Diversity Project. Nature, 538, 201-206.
- Corpas, M. (2026). ClawBio. https://github.com/ClawBio/ClawBio
