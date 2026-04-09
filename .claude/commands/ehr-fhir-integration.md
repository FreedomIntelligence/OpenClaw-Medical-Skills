# ehr-fhir-integration

> Provides comprehensive tools for working with Electronic Health Records (EHR) using the HL7 FHIR standard.

**Available tools:** Read, Bash

# EHR/FHIR Integration

The **EHR/FHIR Integration Skill** enables AI agents to interact with FHIR servers to search, read, and analyze clinical data.

## When to Use This Skill

*   When you need to retrieve patient demographics, conditions, medications, or lab results from an EHR.
*   When performing population health analysis on a cohort of patients.
*   When validating clinical data against the FHIR R4 standard.

## Core Capabilities

1.  **Patient Search**: Find patients by name, birthdate, or ID.
2.  **Clinical Data Retrieval**: Fetch Conditions, Observations, MedicationRequests, and Procedures.
3.  **Data Export**: Export clinical data to JSON or Pandas-ready formats.

## Workflow

1.  **Configure**: Set up the FHIR server URL and authentication (if needed).
2.  **Execute**: Run the `fhir_client.py` script with the desired resource and parameters.

## Example Usage

**User**: "Find patient John Smith born after 1980."

**Agent Action**:
```bash
python3 Skills/Clinical/EHR_FHIR_Integration/fhir_client.py \
    --server https://hapi.fhir.org/baseR4 \
    --resource Patient \
    --search "name=Smith&birthdate=gt1980-01-01" \
    --output patients.json
```
