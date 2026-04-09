# radgpt-radiology-reporter

> Radiology Reporter

**Available tools:** Bash, Read

# RadGPT (Radiology Report Assistant)

An LLM-based agent designed to summarize and explain complex radiology reports for patients and clinicians.

## When to Use

*   **Patient Communication**: Converting technical findings into plain language.
*   **Clinician Review**: Highlighting critical findings (e.g., "Pneumothorax detected").
*   **Follow-up**: Suggesting appropriate next steps based on findings.

## Core Capabilities

1.  **Simplification**: Translates "bilateral opacity" to "cloudiness in both lungs".
2.  **Entity Extraction**: Identifies key anatomical structures and pathologies.
3.  **Q&A**: Answers follow-up questions about the report.

## Workflow

1.  **Input**: Raw text of the radiology report.
2.  **Process**: LLM summarizes and identifies key findings.
3.  **Output**: Structured summary or conversational explanation.

## Example Usage

**User**: "Explain this chest X-ray report to the patient."

**Agent Action**:
```bash
python -m radgpt.explain --report ./report.txt --target_audience patient
```
