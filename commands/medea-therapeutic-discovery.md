# medea-therapeutic-discovery

> An AI agent for therapeutic discovery that executes transparent, multi-step omics analyses including research planning, code execution, and literature reasoning.

**Available tools:** Bash, Read, WebFetch

# Medea Therapeutic Discovery Agent

Medea is a multi-stage AI agent designed for therapeutic discovery, modeled after 2026 state-of-the-art open source architectures. It executes transparent, multi-step omics analyses.

## When to Use This Skill

*   "Run multi-omics therapeutic discovery pipeline"
*   "Analyze omics data for novel drug targets using Medea"
*   "Perform literature reasoning and consensus reconciliation for target X"

## Core Capabilities

1.  **Research Planning**: Formulates step-by-step omics analysis plans.
2.  **Code Execution**: Generates and executes Python/R scripts for data processing.
3.  **Literature Reasoning**: Retrieves and synthesizes current literature.
4.  **Consensus Stage**: Reconciles experimental evidence with literature to propose high-confidence targets.

## Workflow

1.  **Step 1**: Initialize Medea agent with target disease or omics dataset.
2.  **Step 2**: Execute the multi-stage pipeline across planning, coding, literature review, and consensus validation.

## Example Usage

**User**: "Run Medea analysis on the provided breast cancer multi-omics dataset."

**Agent Action**:
```bash
python3 -m medea.agent --dataset breast_cancer_omics.h5ad --mode full_discovery
```
