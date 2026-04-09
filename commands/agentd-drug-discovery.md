# agentd-drug-discovery

> Use the AgentD workflow to mine evidence, design molecules, and rank candidates with SAR plus ADMET annotations for early drug discovery tasks.

**Available tools:** Read, Bash

## At-a-Glance
- **description (10-20 chars):** Hypothesis foundry
- **keywords:** ligand-design, SAR, ADMET, docking, ranking
- **measurable_outcome:** Generate ≥10 candidate molecules (or requested count) with SMILES, key properties, and rationales per run, all delivered within 15 minutes.

## Inputs
- `target_protein`, optional `reference_compound`, disease `indication`.
- `constraints` dict (LogP, MW, TPSA, etc.) and `num_candidates`.

## Outputs
1. Ranked candidate list with SMILES + property scores + novelty metrics.
2. ADMET/toxicity alerts and SAR rationale per molecule.
3. Reproducibility manifest (data source versions, model checkpoints).

## Workflow
1. **Evidence retrieval:** Mine literature + databases for known ligands and liabilities.
2. **Generate candidates:** Run AgentD generative step (scaffold hopping/fragment growth) aligned to constraints.
3. **Score & filter:** Apply Lipinski/QED/ADMET heuristics; include docking setup when requested.
4. **Rank & explain:** Combine efficacy, developability, novelty; summarize SAR learnings.
5. **Deliver outputs:** Emit JSON/CSV plus narrative recommendations; mark as in silico.

## Guardrails
- Clearly state outputs are hypothetical and need wet-lab validation.
- Flag PAINS/reactive motifs automatically.
- Record data/model versions for audit trails.

## References
- Detailed parameter tables and dependencies listed in `README.md`.
