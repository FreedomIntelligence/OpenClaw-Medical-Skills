# leads-literature-mining

> Review Automator

**Available tools:** Bash, WebFetch

# LEADS (Literature Mining Agent)

A specialized LLM agent for automating systematic reviews and meta-analyses, capable of high-accuracy study selection and data extraction.

## When to Use

*   **Systematic Reviews**: Screening thousands of abstracts for inclusion criteria.
*   **Data Extraction**: Pulling specific metrics (e.g., hazard ratios, sample sizes) from full-text PDFs.
*   **Evidence Synthesis**: Aggregating findings across multiple studies.

## Core Capabilities

1.  **Study Selection**: Automated screening based on PICO criteria.
2.  **Data Extraction**: Structured extraction of study characteristics and results.
3.  **Quality Assessment**: Risk of bias evaluation.

## Workflow

1.  **Search**: Query PubMed/Embase.
2.  **Screen**: Apply inclusion/exclusion criteria to abstracts.
3.  **Extract**: Parse full text for data points.
4.  **Report**: Generate PRISMA flow diagram and evidence table.

## Example Usage

**User**: "Perform a systematic review on the efficacy of CAR-T in solid tumors."

**Agent Action**:
```bash
python -m leads.review --topic "CAR-T solid tumors" --criteria ./criteria.json
```
