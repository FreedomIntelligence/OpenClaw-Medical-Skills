# compbioagent-explorer

> scRNA-seq Explorer

**Available tools:** Bash, WebFetch

# CompBioAgent (Single-Cell Explorer)

An LLM-powered web application for single-cell RNA-seq data exploration, integrating with CellDepot and Cellxgene VIP.

## When to Use

*   **Interactive Exploration**: When you need to visually explore a dataset without writing code.
*   **Hypothesis Generation**: Quickly checking expression of specific markers across clusters.
*   **Sharing**: Presenting data to non-computational collaborators.

## Core Capabilities

1.  **Natural Language Querying**: "Show me the expression of TP53 in the B-cell cluster."
2.  **Cellxgene Integration**: Leverages robust visualization tools.
3.  **Data Integration**: Connects with CellDepot for dataset retrieval.

## Workflow

1.  **Setup**: `pip install compbioagent`.
2.  **Launch**: `compbioagent start --data ./data.h5ad`.
3.  **Interact**: Open the local URL (e.g., http://localhost:8050) and chat with the agent to generate plots.

## Example Usage

**User**: "Launch the explorer for my kidney dataset."

**Agent Action**:
```bash
compbioagent launch --port 8080 --data ./kidney_atlas.h5ad
```
