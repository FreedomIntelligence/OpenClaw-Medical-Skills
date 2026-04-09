# biomaster-workflows

> Pipeline maestro

**Available tools:** Bash, Read

# BioMaster Workflows

Orchestrate BioMaster’s multi-agent pipelines (RNA-seq, ChIP-seq, single-cell, Hi-C) using the provided configs and repos to deliver reproducible outputs.

## Workflow
1. **Config prep:** Populate YAML with tool paths, reference genomes, and workflow selection (`rnaseq`, `chipseq`, `singlecell`, `hic`).
2. **Environment:** `cd repo && pip install -r requirements.txt` (or container) prior to running.
3. **Launch:** `python repo/run.py --config repo/config.yaml` (or chosen config) and monitor progress.
4. **Error recovery:** Let BioMaster agents retry failing stages; review logs for missing reference/index files.
5. **Output packaging:** Collect BAMs/counts/peaks + QC + narrative summary of parameters and runtimes.

## Guardrails
- Fail fast when reference files or indices are absent to avoid wasted compute.
- Record tool versions for every stage (alignment, quantification, etc.).
- Require confirmation before deleting intermediates or rerunning destructive steps.

## References
- Full workflow descriptions, supported modalities, and repo links reside in `README.md`.
