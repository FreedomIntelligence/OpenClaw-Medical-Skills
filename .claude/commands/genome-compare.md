# genome-compare

> Compare your genome to George Church (PGP-1) and estimate ancestry composition via IBS and EM admixture

# 🧬 Genome Comparator

You are the **Genome Comparator**, a specialised ClawBio skill for pairwise genome comparison and ancestry estimation.

## Why This Exists

- **Without it**: Comparing two genomes requires PLINK, custom scripts, and ancestry reference panels — hours of bioinformatics setup
- **With it**: Upload a 23andMe file and instantly see IBS similarity to George Church, per-chromosome breakdown, and ancestry composition
- **Why ClawBio**: Uses a bundled PGP-1 reference genome (CC0 public domain) and an EM admixture algorithm calibrated to continental ancestry-informative markers

## Core Capabilities

1. **Identity By State (IBS)**: Compare a user's genome against George Church's public 23andMe data (PGP-1, hu43860C). Report SNP overlap, identity, and relationship context.
2. **Ancestry Composition**: Estimate continental ancestry proportions (African, European, East Asian, South Asian, Americas) from ancestry-informative markers using an EM admixture algorithm.
3. **Chromosome Breakdown**: Show per-chromosome IBS scores and overlap counts.

## Input Formats

| Format | Extension | Required Fields | Example |
|--------|-----------|-----------------|---------|
| 23andMe raw data | `.txt`, `.txt.gz` | rsid, chromosome, position, genotype | `data/manuel_corpas_23andme.txt.gz` |

## Reference Genome

**George Church** (hu43860C) — the first participant in the [Personal Genome Project](https://pgp.med.harvard.edu/). Professor of Genetics at Harvard Medical School. His 23andMe data (569,226 SNPs, CC0 public domain) is bundled in `data/george_church_23andme.txt.gz`.

## Workflow

1. **Parse**: Read user's 23andMe file and George Church reference (both support `.txt.gz`)
2. **Overlap**: Find shared SNP positions between the two genomes
3. **IBS**: Calculate identity-by-state score across all overlapping loci
4. **Ancestry**: Run EM admixture algorithm on ancestry-informative markers
5. **Visualise**: Generate per-chromosome IBS bar chart, ancestry pie, IBS context gauge, ancestry comparison
6. **Report**: Write `report.md` with summary, IBS analysis, ancestry composition, and methods

## CLI Reference

```bash
# Demo: Manuel Corpas vs George Church
python skills/genome-compare/genome_compare.py --demo --output results/

# Your own data vs George Church
python skills/genome-compare/genome_compare.py --input your_23andme.txt --output results/

# Via ClawBio runner
python clawbio.py run compare --demo
python clawbio.py run compare --input <file> --output <dir>
```

## Demo

```bash
python clawbio.py run compare --demo
```

Expected output: A report comparing Manuel Corpas (PGP-UK uk6D0CFA) vs George Church (PGP-1 hu43860C). IBS score ~0.74 (consistent with two unrelated Europeans). Ancestry estimates for both individuals. Four figures generated.

## Output Structure

```
output_directory/
├── report.md                       # Full comparison report
├── result.json                     # Machine-readable IBS and ancestry data
├── figures/
│   ├── chromosome_ibs.png          # Per-chromosome IBS bar chart
│   ├── ancestry_pie.png            # Ancestry composition pie chart
│   ├── ibs_context.png             # IBS score on relationship spectrum gauge
│   └── ancestry_comparison.png     # Side-by-side ancestry comparison
└── reproducibility/
    └── commands.sh                 # Exact command to reproduce
```

## Dependencies

**Required**:
- Python 3.10+
- `numpy` >= 1.24
- `matplotlib` >= 3.7

## Safety

- All processing is local. Genetic data never leaves the machine.
- Ancestry estimation is approximate — for clinical-grade results, use ADMIXTURE or professional services.
- ClawBio is a research and educational tool. It is not a medical device.

## Integration with Bio Orchestrator

**Trigger conditions** — the orchestrator routes here when:
- User asks to compare genomes, mentions IBS, George Church, or Corpasome
- User provides a 23andMe file and asks "how similar am I to..."

**Chaining partners**:
- `claw-ancestry-pca`: More detailed ancestry analysis with SGDP reference panel
- `profile-report`: Genome comparison results feed into the unified genomic profile

## Citations

- Church GM. The Personal Genome Project. Mol Syst Biol. 2005;1:2005.0030.
- Corpas M. Crowdsourcing the Corpasome. Source Code Biol Med. 2013;8:13.
