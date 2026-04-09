# autonomous-oncology-agent

> Precision Oncology

**Available tools:** Bash, WebFetch

# Autonomous Clinical AI Agent (Oncology)

This skill implements the capabilities of the "Autonomous Clinical AI Agent" described in Nature Cancer (2025). It combines Large Language Models (LLMs) for reasoning with specialized vision models for pathology image analysis to support precision oncology decision-making.

## When to Use This Skill

*   **Precision Oncology**: For interpreting complex cancer cases involving pathology, genomics, and clinical history.
*   **Biomarker Detection**: To identify status of key biomarkers (MSI, KRAS, BRAF) from pathology slides (H&E).
*   **Guideline Adherence**: To check treatment plans against NCCN or ASCO guidelines (via OncoKB/PubMed).
*   **Multimodal Synthesis**: When you need to combine image data and text reports.

## Core Capabilities

1.  **Vision Transformer Analysis**: Detects MSI status and key mutations (KRAS, BRAF) directly from H&E images.
2.  **Clinical Reasoning**: Synthesizes patient history, pathology, and genomics to recommend therapies.
3.  **Evidence Retrieval**: Integrates real-time knowledge from OncoKB and PubMed.
4.  **Decision Support**: Provides ranked treatment options with evidence levels.

## Workflow

1.  **Input Processing**:
    *   Text: Clinical notes, pathology reports, genomic panels.
    *   Image: H&E histology slides.
2.  **Analysis**:
    *   Vision model predicts molecular features from slides.
    *   LLM extracts key clinical entities (Stage, Histology, Mutations).
3.  **Reasoning**:
    *   Query OncoKB for actionable mutations.
    *   Match against standard of care guidelines.
4.  **Output**: Generate a comprehensive "Tumor Board" style report.

## Example Usage

**User**: "Review this case of metastatic colorectal cancer. The H&E slide is attached. What is the predicted MSI status and recommended first-line therapy?"

**Agent Action**:
1.  Runs vision model on H&E image -> Output: "MSI-High (Predicted)".
2.  Reads clinical notes -> "Patient is fit, ECOG 0."
3.  Consults Knowledge Base -> "MSI-High CRC responds to Pembrolizumab."
4.  Recommends: "Based on predicted MSI-High status, immunotherapy (Pembrolizumab) is recommended over standard chemotherapy..."
