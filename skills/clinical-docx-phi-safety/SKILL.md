---
name: clinical-docx-phi-safety
description: Safely extract text from clinical DOCX files while checking hidden PHI in comments, tracked changes, document properties, headers, footers, and embedded objects.
---

# Clinical DOCX PHI Safety

Use this skill when working with a clinical or healthcare `.docx` file that may contain protected health information (PHI), hidden comments, tracked changes, reviewer names, document properties, headers, footers, embedded objects, or copied EHR text.

## Safety Boundary

- Treat every clinical document as potentially sensitive, even if the visible text appears de-identified.
- Do not upload the document to external services unless the user explicitly confirms that sharing is permitted.
- Do not summarize patient-specific diagnosis, treatment, medication, or prognosis as medical advice.
- Extract only the minimum text needed for the user's stated task.
- If de-identification status is unclear, say so and ask the user to confirm the intended use.

## Recommended Workflow

1. **Work locally first.**
   Use local parsing tools rather than web upload tools for the first pass.

2. **Inspect visible text and hidden channels.**
   Check the main document body, headers, footers, footnotes, endnotes, comments, tracked revisions, document properties, custom properties, embedded objects, and image alt text.

3. **Strip or quarantine hidden metadata before analysis.**
   Remove comments, tracked revisions, author/reviewer names, template paths, company fields, last-modified metadata, and document IDs unless they are explicitly needed.

4. **Create a clean text artifact.**
   Save a plain-text or Markdown extraction that excludes hidden metadata. Mark whether the extraction includes headers, footers, tables, or footnotes.

5. **Run a PHI check on the extracted text.**
   Look for names, dates, phone numbers, emails, addresses, medical record numbers, accession numbers, device IDs, insurance identifiers, and free-text identifiers.

6. **Report uncertainty.**
   If a field could be PHI but cannot be verified, flag it instead of silently keeping it.

## Python Starting Point

```python
from docx import Document

def extract_visible_docx_text(path: str) -> str:
    doc = Document(path)
    parts: list[str] = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            parts.append(text)

    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))

    return "\n".join(parts)
```

This starting point extracts visible body text and tables only. It does not prove that hidden metadata is absent. For clinical workflows, pair it with explicit checks of the zipped DOCX XML parts and document properties before using the text with an AI agent.

## Red Flags

- The document was copied from an EHR, portal, PACS/RIS report, or discharge summary.
- Track Changes is enabled or the file has multiple reviewers.
- The file contains comments, footnotes, embedded Excel objects, pasted screenshots, or scanned pages.
- The document title, template, author, company, or last-saved-by fields contain names or institutional identifiers.
- The user asks to send the file to a web service or model endpoint without confirming authorization.

## Output Template

```markdown
## Clinical DOCX Extraction Safety Report

- Source file: <local filename only>
- Visible body extracted: yes/no
- Tables extracted: yes/no
- Headers/footers checked: yes/no
- Comments checked: yes/no
- Tracked changes checked: yes/no
- Document properties checked: yes/no
- Embedded objects checked: yes/no
- PHI found: yes/no/uncertain
- Action taken: removed / retained with reason / needs user review
- Safe-to-analyze text artifact: <path or not created>

Notes:
- <brief notes, no patient identifiers>
```
