# crispr-guide-design

> Guide foundry

**Available tools:** Bash, Read

# CRISPR Design Agent

Automate sgRNA selection, scoring, off-target evaluation, and oligo generation for CRISPR experiments using the documented workflow.

## When to Use
- Designing CRISPR knockout/knock-in experiments that need validated guides.
- Locating all PAM-compatible target sites in a gene or locus.
- Filtering guides by efficiency/off-target metrics before cloning.

## Core Capabilities
1. **Target discovery:** Scan sequences for PAM motifs (e.g., NGG).
2. **Efficiency scoring:** Evaluate GC content, homopolymers, Doench/DeepCRISPR/CFD scores.
3. **Filtering & ranking:** Remove risky guides (SNP overlap, off-target hits) and output the best candidates.

## Workflow
1. Resolve gene symbol + organism to canonical transcript coordinates and target region.
2. Enumerate PAM-compatible sites; extract spacers for the chosen Cas variant.
3. Score guides (efficiency + specificity) and compute GC metrics.
4. Run off-target search (≤3 mismatches) to flag problematic loci.
5. Filter/rank guides, generate cloning oligos/primers, and emit JSON/CSV outputs with coordinates.

## Example Usage
```bash
python3 Skills/Genomics/CRISPR_Design_Agent/crispr_designer.py \
    --sequence "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTGTGAGTGGATCCATTGGAAGGGC" \
    --output guides.json
```

## Guardrails
- Always state genome build and Cas variant assumptions.
- Avoid guides overlapping common SNPs when `avoid_variants` is true.
- Flag high off-target density near coding regions for manual review.

## References
- See `README.md` and `prompt.md` for detailed schema plus supporting literature.
