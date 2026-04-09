# spatial-transcriptomics-agent

> Spatial analyst

**Available tools:** Bash, Read, WebFetch

# Spatial Transcriptomics Agent

Run STAgent to align histology images with expression matrices, perform clustering/SVG detection, and generate literature-backed spatial reports.

## When to Use
- Analysis of Visium/Xenium or similar ST datasets.
- Visual reasoning over spatial plots, H&E images, or cluster maps.
- Automatically generating Scanpy/Squidpy code for new ST workflows.
- Hypothesis generation about spatial gene expression patterns.

## Core Capabilities
1. **Dynamic code generation:** Create/execute Python scripts for QC, clustering, SVG detection.
2. **Visual reasoning:** Interpret spatial plots to identify tissue domains and cell neighborhoods.
3. **Literature retrieval:** Pull references that contextualize findings.
4. **Report generation:** Deliver publication-style writeups with plots and SVG tables.

## Workflow
1. **Env setup:** `conda env create -f environment.yml && conda activate STAgent`.
2. **Data prep:** Supply `expression_path` (`.h5ad`/Spaceranger) + `image_path` (H&E/IF) and metadata.
3. **Task selection:** Choose tasks such as `cluster`, `find_svg`, `annotate_domains`, or composite instructions; run `python repo/src/main.py --data_path ... --task "..."`.
4. **Execute & interpret:** Let STAgent generate scripts, run analyses, and interpret results with literature references.
5. **Package outputs:** Save UMAP/spatial plots, SVG tables, QC details, and summary markdown.

## Example Usage
```text
User: "Analyze this breast cancer ST dataset, find immune infiltrates."
Agent: loads data, runs `sqidpy.gr.spatial_neighbors`, computes Leiden clusters, plots marker genes (CD3D, CD19), and summarizes which clusters map to tumor core vs. stromal/immune zones.
```

## Guardrails
- Document coordinate systems and any scaling between imaging and expression coordinates.
- Avoid definitive cell-type labels without supporting markers.
- Capture QC parameters for reproducibility.

## References
- Source repo: https://github.com/LiuLab-Bioelectronics-Harvard/STAgent
- See local `README.md` for detailed instructions.
