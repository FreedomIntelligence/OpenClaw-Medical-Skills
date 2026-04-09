# medical-entity-extractor

> Extract medical entities (symptoms, medications, lab values, diagnoses) from patient messages.

# Medical Entity Extractor

Extract structured medical information from unstructured patient messages.

## What This Skill Does

1. **Symptom Extraction**: Identifies symptoms, severity, duration, and progression
2. **Medication Extraction**: Finds medication names, dosages, frequencies, and side effects
3. **Lab Value Extraction**: Parses lab results, vital signs, and measurements
4. **Diagnosis Extraction**: Identifies mentioned diagnoses and conditions
5. **Temporal Extraction**: Captures when symptoms started, how long they've lasted
6. **Action Items**: Identifies requested actions (appointments, refills, questions)

## Input Format

```json
[
  {
    "id": "msg-123",
    "priority_score": 78,
    "priority_bucket": "P1",
    "subject": "Medication side effects",
    "from": "patient@example.com",
    "date": "2026-02-27T10:30:00Z",
    "body": "I've been feeling dizzy since starting the new blood pressure medication (Lisinopril 10mg) three days ago. My BP this morning was 145/92."
  }
]
```

## Output Format

```json
[
  {
    "id": "msg-123",
    "entities": {
      "symptoms": [
        {
          "name": "dizziness",
          "severity": "moderate",
          "duration": "3 days",
          "onset": "since starting new medication"
        }
      ],
      "medications": [
        {
          "name": "Lisinopril",
          "dosage": "10mg",
          "frequency": null,
          "context": "new medication"
        }
      ],
      "lab_values": [
        {
          "type": "blood_pressure",
          "value": "145/92",
          "unit": "mmHg",
          "timestamp": "this morning"
        }
      ],
      "diagnoses": [
        {
          "name": "hypertension",
          "context": "implied by blood pressure medication"
        }
      ],
      "action_items": [
        {
          "type": "medication_review",
          "reason": "possible side effect (dizziness)"
        }
      ]
    },
    "summary": "Patient reports dizziness after starting Lisinopril 10mg 3 days ago. BP elevated at 145/92. Possible medication side effect requiring review."
  }
]
```

## Entity Types

### Symptoms
- Name, severity (mild/moderate/severe), duration, onset, progression (improving/stable/worsening)

### Medications
- Name, dosage, frequency, route, context (new/existing/stopped)

### Lab Values
- Type (BP, glucose, cholesterol, etc.), value, unit, timestamp, normal range

### Diagnoses
- Name, context (confirmed/suspected/ruled out)

### Vital Signs
- Temperature, heart rate, respiratory rate, oxygen saturation, blood pressure

### Action Items
- Type (appointment, refill, question, callback), urgency, reason

## Medical Terminology Handling

The skill recognizes:
- Common abbreviations (BP, HR, RR, O2 sat, etc.)
- Brand and generic medication names
- Lay terms for medical conditions ("sugar" → diabetes, "heart attack" → MI)
- Temporal expressions ("since yesterday", "for the past week")

## Integration

This skill can be invoked via the 
```bash
```

Or programmatically:

```typescript
const result = await execFileAsync('  'skill', 'run', 'medical-entity-extractor',
  '--input', JSON.stringify(scoredMessages),
  '--json'
]);
```

**Recommended Model**: Claude Sonnet 4.5 (`
## Privacy & Security

- All processing happens locally via - No data is sent to external services (except Claude API for LLM processing)
- Extracted entities remain in your local environment
