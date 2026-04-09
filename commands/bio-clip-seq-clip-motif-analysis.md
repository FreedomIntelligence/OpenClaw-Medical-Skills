# bio-clip-seq-clip-motif-analysis

> Identify enriched sequence motifs at CLIP-seq binding sites for RBP binding specificity. Use when characterizing the sequence preferences of an RNA-binding protein.

**Available tools:** Read, Bash

# CLIP Motif Analysis

## HOMER De Novo Motifs

```bash
# Extract sequences from peaks
bedtools getfasta -fi genome.fa -bed peaks.bed -fo peaks.fa

# Find enriched motifs
findMotifs.pl peaks.fa fasta output_dir \
    -len 6,7,8 \
    -rna
```

## MEME-ChIP

```bash
meme-chip -oc output_dir \
    -dna \
    peaks.fa
```

## Known Motif Enrichment

```bash
# HOMER known motif scan
findMotifs.pl peaks.fa fasta output_dir \
    -rna \
    -known
```

## Related Skills

- clip-peak-calling - Get peaks
- chip-seq/motif-analysis - General motif concepts
