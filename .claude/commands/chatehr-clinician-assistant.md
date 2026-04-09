# chatehr-clinician-assistant

> EHR Chat Assistant

**Available tools:** Bash, Read

# ChatEHR

AI software for clinicians to interact with patient medical records via natural language queries and automatic chart summarization.

## When to Use

*   **Rapid Review**: "Summarize the patient's cardiology history."
*   **Data Extraction**: "What was the last creatinine level?"
*   **Documentation**: Generating draft notes or discharge summaries.

## Core Capabilities

1.  **Chart Summarization**: Condense complex history into readable notes.
2.  **QA**: Answer specific questions about the patient's data.
3.  **FHIR Integration**: Works with standard FHIR resources.

## Workflow

1.  **Connect**: Authenticate with the EHR system (sandbox or secure instance).
2.  **Select Patient**: Load patient context.
3.  **Query**: Submit natural language questions.

## Example Usage

**User**: "Summarize the last 3 oncology visits."

**Agent Action**:
```bash
python -m chatehr.query --patient_id 12345 --prompt "Summarize last 3 oncology visits"
```
