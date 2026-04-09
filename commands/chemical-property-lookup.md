# chemical-property-lookup

> Compute RDKit-driven molecular properties (MW, logP, TPSA, QED, Lipinski) for a SMILES string to support downstream drug discovery tools.

**Available tools:** Read, Bash

## At-a-Glance
- **description (10-20 chars):** RDKit stats
- **keywords:** SMILES, RDKit, Lipinski, QED, ADMET
- **measurable_outcome:** Return a validated property summary (JSON + Lipinski verdict) for each SMILES within 60 seconds of request.

## Workflow
1. Validate SMILES input; raise explicit errors for invalid syntax.
2. Call helpers from `molecular_tools.py` (`summarize_properties`, `check_lipinski`, etc.).
3. Report MW, logP, TPSA, HBD/HBA, QED, and Lipinski pass/fail with violations.
4. Surface any calculation warnings (e.g., aromaticity perception issues).

## Guardrails
- Never infer stereochemistry; report as "not provided".
- Log invalid SMILES for manual follow-up.
- Communicate that results are screening heuristics, not definitive ADMET outcomes.

## References
- `README.md` plus `molecular_tools.py` for function signatures and dependencies.
