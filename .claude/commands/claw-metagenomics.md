# claw-metagenomics

> Shotgun metagenomics profiling — taxonomy, resistome, and functional pathways

# Shotgun Metagenomics Profiler

Comprehensive shotgun metagenomics analysis combining taxonomic classification, antimicrobial resistance gene detection, and functional pathway profiling from paired-end FASTQ files.

## What it does

1. Takes paired-end FASTQ files (R1, R2) or a single concatenated FASTQ as input
2. Runs **Kraken2** taxonomic classification against a standard database (e.g., Standard-8, PlusPF)
3. Refines abundances with **Bracken** at species level (read re-estimation)
4. Detects antimicrobial resistance genes with **RGI** against the **CARD** database
5. Classifies detected ARGs by **WHO critical priority pathogen** association
6. Optionally runs **HUMAnN3** for functional pathway profiling (MetaCyc + UniRef)
7. Generates three publication-quality figures:
   - **Figure 1**: Taxonomy bar chart — top 20 species by relative abundance
   - **Figure 2**: Resistome heatmap — ARG families by drug class with abundance
   - **Figure 3**: WHO-critical ARG summary — priority-tier breakdown of detected resistance genes
8. Produces a full reproducibility bundle (commands.sh, environment.yml, checksums.sha256)

## Why this exists

If you ask a general AI to "analyse a metagenome," it will:
- Not know which Kraken2 database to use or how to set confidence thresholds
- Hallucinate Bracken parameters for read-length and taxonomic level
- Miss the connection between detected ARGs and WHO priority pathogen lists
- Skip HUMAnN3 entirely (or misconfigure its database paths)
- Produce a single bar chart with no resistance context
- Not provide a reproducibility bundle

This skill encodes the correct methodological decisions:
- Kraken2 confidence threshold of 0.2 (reduces false positives in environmental samples)
- Bracken re-estimation at species level with minimum 10 reads
- RGI MAIN with "Perfect" and "Strict" hit criteria only (no "Loose" hits)
- WHO Critical Priority Pathogen list mapped to detected ARG families
- HUMAnN3 with MetaCyc stratification for pathway-level functional context
- Thread count auto-detected from available CPUs
- Full reproducibility bundle for every run

## Validated On

The skill works with any shotgun metagenome but has been validated on:
- **Peru sewage metagenomics study** (6 samples, 3 collection sites: Lima, Cusco, Iquitos)
- Environmental sewage samples with mixed microbial communities
- Read depths ranging from 2M to 15M paired-end reads per sample

## WHO-Critical ARG Detection

A key feature is the classification of detected resistance genes by WHO priority tier:

| Priority | Pathogen | Resistance |
|----------|----------|------------|
| Critical | *Acinetobacter baumannii* | Carbapenem-resistant |
| Critical | *Pseudomonas aeruginosa* | Carbapenem-resistant |
| Critical | *Enterobacteriaceae* | Carbapenem-resistant, 3rd-gen cephalosporin-resistant |
| High | *Enterococcus faecium* | Vancomycin-resistant |
| High | *Staphylococcus aureus* | Methicillin-resistant, vancomycin-resistant |
| High | *Helicobacter pylori* | Clarithromycin-resistant |
| High | *Campylobacter* | Fluoroquinolone-resistant |
| High | *Salmonella* spp. | Fluoroquinolone-resistant |
| High | *Neisseria gonorrhoeae* | 3rd-gen cephalosporin-resistant, fluoroquinolone-resistant |
| Medium | *Streptococcus pneumoniae* | Penicillin-non-susceptible |
| Medium | *Haemophilus influenzae* | Ampicillin-resistant |
| Medium | *Shigella* spp. | Fluoroquinolone-resistant |

## Usage

```bash
# Full pipeline (taxonomy + resistome + functional)
python metagenomics_profiler.py \
    --r1 sample_R1.fastq.gz \
    --r2 sample_R2.fastq.gz \
    --output metagenomics_report

# Skip HUMAnN3 (faster — taxonomy + resistome only)
python metagenomics_profiler.py \
    --r1 sample_R1.fastq.gz \
    --r2 sample_R2.fastq.gz \
    --output metagenomics_report \
    --skip-functional

# Single concatenated FASTQ
python metagenomics_profiler.py \
    --input combined.fastq.gz \
    --output metagenomics_report

# Specify Kraken2 database path
python metagenomics_profiler.py \
    --r1 sample_R1.fastq.gz \
    --r2 sample_R2.fastq.gz \
    --output metagenomics_report \
    --kraken2-db /path/to/kraken2_db \
    --read-length 150
```

### Demo (works out of the box)

```bash
python metagenomics_profiler.py --demo --output demo_report
```

The demo uses pre-computed results from the Peru sewage metagenomics study (6 samples, 3 sites) and generates all figures and reports instantly without requiring external tools.

## Example Output

```
Metagenomics Profiler — ClawBio
================================
Mode: demo (pre-computed Peru sewage data)
Samples: 6 (3 sites: Lima, Cusco, Iquitos)

Taxonomy (Kraken2 + Bracken):
  Total classified: 94.2%
  Top species: Escherichia coli (12.3%), Klebsiella pneumoniae (8.7%),
               Pseudomonas aeruginosa (5.1%), Acinetobacter baumannii (3.9%)

Resistome (RGI/CARD):
  Total ARG hits: 247 (Perfect: 89, Strict: 158)
  Drug classes: 14
  WHO-Critical ARGs detected: 23
    - Carbapenem resistance: NDM-1, OXA-48, KPC-3
    - 3rd-gen cephalosporin resistance: CTX-M-15, CTX-M-27

Functional Pathways (HUMAnN3):
  Total pathways: 312
  Top: PWY-7219 (adenosine ribonucleotides de novo biosynthesis)

Figures saved to: demo_report/figures/
  taxonomy_barplot.png (300 dpi)
  resistome_heatmap.png (300 dpi)
  who_critical_args.png (300 dpi)

Reproducibility:
  commands.sh | environment.yml | checksums.sha256
```

## Pipeline Architecture

```
FASTQ R1 + R2
     |
     v
[Kraken2] --> kraken2_report.txt
     |
     v
[Bracken] --> bracken_species.tsv   --> Figure 1: Taxonomy bar chart
     |
     v
[RGI MAIN] --> rgi_results.txt      --> Figure 2: Resistome heatmap
     |                                --> Figure 3: WHO-critical ARG summary
     v
[HUMAnN3] --> pathabundance.tsv     (optional, --skip-functional to omit)
     |
     v
[Report] --> report.md + figures/ + reproducibility/
```

## Database Requirements

| Tool | Database | Size | Notes |
|------|----------|------|-------|
| Kraken2 | Standard-8 or PlusPF | 8-70 GB | Set via `--kraken2-db` or `$KRAKEN2_DB` |
| Bracken | (built from Kraken2 DB) | included | Read-length specific (default: 150 bp) |
| RGI | CARD | ~500 MB | Auto-downloaded via `rgi auto_load` |
| HUMAnN3 | ChocoPhlAn + UniRef90 | ~15 GB | Set via `--humann-db` or `$HUMANN_DB` |

## Citations

If you use this skill in a publication, please cite:

- Wood, D.E., Lu, J. & Langmead, B. (2019). Improved metagenomic analysis with Kraken 2. Genome Biology, 20, 257.
- Lu, J. et al. (2017). Bracken: estimating species abundance in metagenomics data. PeerJ Computer Science, 3, e104.
- Alcock, B.P. et al. (2023). CARD 2023: expanded curation, support for machine learning, and resistome prediction at the Comprehensive Antibiotic Resistance Database. Nucleic Acids Research, 51(D1), D419-D430.
- Beghini, F. et al. (2021). Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities with bioBakery 3. eLife, 10, e65088.
- Corpas, M. (2026). ClawBio. https://github.com/ClawBio/ClawBio
