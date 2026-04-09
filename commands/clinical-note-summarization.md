# clinical-note-summarization

> Structure raw clinical notes into SOAP-format summaries with explicit contradictions, missing data, and ICD-linked assessments using the provided prompt + usage script.

**Available tools:** Read, Bash

## At-a-Glance
- **description (10-20 chars):** SOAP builder
- **keywords:** clinical-notes, SOAP, guardrails, ICD10, gaps
- **measurable_outcome:** Produce SOAP markdown + JSON (when requested) covering all four sections with ≥95% note coverage and explicit missing info in ≤2 minutes per note.

## Inputs
- `note_text` (dictation, OCR, or EHR export) and optional `patient_context` metadata.
- `output_format` (`markdown` default, `json` when downstream validators need schema).

## Outputs
1. Structured SOAP summary with Subjective/Objective/Assessment/Plan bulleting.
2. Alerts plus missing-information checklist.
3. Optional JSON payload using schema from README.

## Workflow
1. **Load system prompt:** `prompt.md` enforces no hallucinations + data gap surfacing.
2. **Normalize input:** Pre-clean vitals, labs, and timeline context when available.
3. **Generate summary:** Call preferred LLM (OpenAI, Anthropic, Gemini, OSS) using `usage.py` as a template.
4. **Validate:** Cross-check extracted values vs. source text and ensure contradictions/missing data are spelled out.
5. **Deliver output:** Provide markdown + JSON as required and log PHI handling steps.

## Guardrails
- Never invent findings; state "not provided" explicitly.
- Mark outputs as documentation support only—not clinical decisions.
- Strip/re-mask PHI before storing prompts/responses.

## References
- For detailed schema, guardrails, and integration snippets see `README.md`, `prompt.md`, and `usage.py`.
