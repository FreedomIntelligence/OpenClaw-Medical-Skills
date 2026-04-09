# cellagent-annotation

> Cell tagger

**Available tools:** Bash, Read

# CellAgent Annotation

Use CellTypeAgent to interpret marker genes, annotate scRNA-seq clusters, and coordinate multi-agent workflows for downstream analysis.

## When to Use
- Automated annotation of scRNA-seq datasets without manual curation.
- Multi-step workflows (QC → clustering → annotation → DE analysis).
- Integrating multiple batches requiring consistent labeling.

## Core Capabilities
1. **Planning:** Multi-agent planner decomposes analysis goals into steps.
2. **Tool execution:** Generates Scanpy/Seurat code and runs it autonomously.
3. **Self-correction:** Detects execution errors and retries with fixes.

## Workflow
1. Gather marker lists per cluster, plus species/tissue context and optional atlas references.
2. Run CellTypeAgent (`pip install -r requirements.txt` then `python repo/main.py --data data.h5ad --goal annotate`).
3. Review outputs for supporting markers; downgrade ambiguous clusters when signals conflict.
4. Produce final table (cluster, label, confidence, supporting markers, notes) and cite references when used.

## Example Usage
```bash
python3 Skills/Genomics/Single_Cell/CellAgent/repo/main.py --data "./data.h5ad" --goal "annotate"
```

## Guardrails
- Avoid over-specific lineages if markers overlap; default to broader types.
- Flag clusters showing multiple signatures for manual review.
- Respect species/tissue differences when interpreting markers.

## References
- README + upstream paper (Mao et al., 2025 / arXiv 2407.09811).
