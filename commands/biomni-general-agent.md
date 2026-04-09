# biomni-general-agent

> Use the local Biomni checkout to orchestrate its 150+ biomedical tools, databases, and know-how workflows for complex research questions.

**Available tools:** Read, Bash

## At-a-Glance
- **description (10-20 chars):** Omni bio agent
- **keywords:** multi-tool, know-how, tutorials, protocols, databases
- **measurable_outcome:** Execute a Biomni workflow that touches ≥2 tool categories and returns a cited research summary or artifact within 15 minutes per request.

## Workflow
1. **Environment:** `cd repo && pip install .` (or follow tutorials env set up). Activate the environment with required GPUs if using heavy models.
2. **Select mode:** Choose Standard (full stack), Light (API-only), or Commercial (license-safe) per task.
3. **Plan tools:** Query the Know-How library for relevant protocols/databases before executing.
4. **Execute notebooks/scripts:** Use `repo/tutorials` or CLI entrypoints to run pipelines; log tool versions.
5. **Summarize:** Provide outputs + citations pulled from the Know-How metadata.

## Guardrails
- Respect tool/data licenses when selecting Light vs Commercial mode.
- Track provenance (tool versions, dataset snapshots) in final response.
- Keep workflows modular—reuse Biomni recipes rather than ad-hoc scripts when possible.

## References
- Full capability list, tool inventory, and tutorial notebooks documented in `README.md` and `repo/tutorials/`.
