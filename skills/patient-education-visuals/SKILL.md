---
name: patient-education-visuals
description: Create de-identified patient education visual briefs and optional Atlas Cloud image/video generation requests with strict medical-safety boundaries.
allowed-tools: Read Write Edit Bash
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        - ATLASCLOUD_API_KEY
    always: false
    emoji: "visual"
    os: [macos, linux]
    install: []
    trigger_keywords:
      - patient education visual
      - patient handout image
      - medical infographic
      - discharge education visual
      - explain this visually
---

# Patient Education Visuals

Use this skill when a clinician, care team, or health educator needs a plain-language visual brief for patient education. The skill prepares de-identified prompts for Atlas Cloud image or video generation, validates the selected live model schema, and defaults to dry-run previews before any generation job is submitted.

## Safety Boundary

This skill is for educational visuals only.

- Do not diagnose, triage, rank risks, or recommend treatment.
- Do not contradict or reinterpret a treating clinician's instructions.
- Do not include protected health information such as patient names, dates of birth, addresses, MRNs, phone numbers, or full dates.
- If clinical content is missing or ambiguous, ask for clinician-approved source text before generating.
- Keep wording neutral: "may help explain", "ask your care team", and "follow your clinician's instructions".
- Avoid frightening imagery, identifiable patients, realistic scans, surgical gore, or claims that an image represents the user's own condition.

## Workflow

1. Identify the audience: adult patient, child, caregiver, or public-health handout.
2. Extract only the clinician-approved education points.
3. Remove identifiers and convert sensitive details into general categories.
4. Build a short visual brief with:
   - topic
   - audience
   - education objective
   - three to five safe learning points
   - visual style and reading level
   - disclaimer text
5. Run a dry-run Atlas Cloud request preview:

```bash
python skills/patient-education-visuals/scripts/atlas_patient_education_visual.py \
  --topic "home blood pressure monitoring" \
  --audience "adult patients" \
  --objective "show the correct measurement steps" \
  --points "sit quietly for five minutes; keep feet flat; place cuff on bare upper arm; record the reading; ask the care team about concerning results" \
  --style "clean clinic handout illustration"
```

6. Review the selected model, schema fields, request body, and cost metadata.
7. Submit only when the user explicitly wants generation:

```bash
python skills/patient-education-visuals/scripts/atlas_patient_education_visual.py \
  --topic "home blood pressure monitoring" \
  --audience "adult patients" \
  --objective "show the correct measurement steps" \
  --points "sit quietly for five minutes; keep feet flat; place cuff on bare upper arm; record the reading; ask the care team about concerning results" \
  --style "clean clinic handout illustration" \
  --submit --poll
```

## Output Expectations

The dry run prints:

- selected live Atlas Cloud model
- accepted schema fields
- required schema fields
- generated patient-education prompt
- generation request body
- `submit: false`

## Review Checklist

Before submitting:

- No PHI or identifiable patient details are present.
- The content is educational, not diagnostic or prescriptive.
- The disclaimer remains in the visual prompt.
- Any clinical details come from clinician-approved source text.
- The selected model schema accepts the fields being sent.
