# ontology-validator

> Validate material sample annotations and data structures against ontology constraints. Use when checking if CMSO annotations are correct, verifying that required properties are present, or validating that object property relationships have consistent domain and range. Catches unknown classes, unknown properties, domain mismatches, and missing required fields.

**Available tools:** R, e, a, d, ,,  , B, s, h

# Ontology Validator

## Goal

Validate that material sample annotations comply with ontology constraints: correct class names, valid properties, consistent domain/range relationships, and required fields present.

## Requirements

- Python 3.8+
- No external dependencies (Python standard library only)
- Requires ontology-explorer's `cmso_summary.json` and `ontology_registry.json`

## Inputs to Gather

| Input | Description | Example |
|-------|-------------|---------|
| Annotation | JSON dict or list of annotation dicts | `{"class":"UnitCell","properties":{"has Bravais lattice":"cF"}}` |
| Class name | Class to check completeness for | `Crystal Structure` |
| Provided properties | Comma-separated property names | `"has unit cell,has space group"` |
| Relationships | JSON array of subject-property-object triples | `[{"subject_class":"Material","property":"has structure","object_class":"Crystal Structure"}]` |

## Decision Guidance

```
What do you need to validate?
├── An annotation (classes and properties are correct)
│   └── schema_checker.py --ontology cmso --annotation '<json>'
├── Completeness of a class annotation
│   └── completeness_checker.py --ontology cmso --class <name> --provided <props>
└── Object property relationships
    └── relationship_checker.py --ontology cmso --relationships '<json>'
```

## Script Outputs (JSON Fields)

| Script | Key Outputs |
|--------|-------------|
| `scripts/schema_checker.py` | `results.valid`, `results.errors`, `results.warnings`, `results.class_valid`, `results.properties_valid` |
| `scripts/completeness_checker.py` | `results.completeness_score`, `results.required_missing`, `results.recommended_missing`, `results.optional_missing`, `results.unrecognized` |
| `scripts/relationship_checker.py` | `results.valid`, `results.results`, `results.errors` |

## Workflow

1. After mapping a sample with ontology-mapper, pass the annotations to `schema_checker.py` to verify correctness.
2. For a specific class, use `completeness_checker.py` to see what required/recommended properties are missing.
3. When building relationships between instances, use `relationship_checker.py` to ensure domain/range consistency.

## Conversational Workflow Example

```
User: I annotated my sample as CrystalStructure with properties hasUnitCell and hasBasis.
      Is this correct and complete?

Agent: Let me validate your annotation and check completeness.

[Runs: completeness_checker.py --ontology cmso --class "Crystal Structure" --provided "has unit cell,has basis" --json]

Your annotation is partially complete:
- has unit cell: provided (required)
- has basis: not a direct property of Crystal Structure (it belongs to Unit Cell)
- **Missing required**: has space group

The "has basis" property belongs to the Unit Cell class, not Crystal Structure.
You should add "has space group" to Crystal Structure and move "has basis"
to the Unit Cell annotation.
```

## CLI Examples

```bash
# Validate an annotation
python3 skills/ontology/ontology-validator/scripts/schema_checker.py \
  --ontology cmso \
  --annotation '{"class":"Unit Cell","properties":{"has Bravais lattice":"cF"}}' \
  --json

# Check completeness
python3 skills/ontology/ontology-validator/scripts/completeness_checker.py \
  --ontology cmso \
  --class "Crystal Structure" \
  --provided "has unit cell,has space group" \
  --json

# Validate relationships
python3 skills/ontology/ontology-validator/scripts/relationship_checker.py \
  --ontology cmso \
  --relationships '[{"subject_class":"Computational Sample","property":"has material","object_class":"Material"}]' \
  --json
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `Class 'X' not found` | Invalid class name | Use ontology-explorer to find correct name |
| `Property 'X' not found` | Invalid property name | Use property_lookup.py to search |
| `Annotation must be a dict` | Wrong input format | Provide valid JSON dict |
| `Relationships must be a non-empty list` | Wrong input format | Provide JSON array of relationship dicts |

## Interpretation Guidance

- **Errors** indicate definite problems (unknown class/property, range mismatch)
- **Warnings** indicate potential issues (domain mismatch — may be intentional for subclasses)
- **Completeness score**: 0.0-1.0 ratio of provided vs. total tracked properties
- **required_missing**: must fix for valid annotation
- **recommended_missing**: should fix for quality
- **unrecognized**: may indicate typos or properties from a different ontology

## Limitations

- Constraints file is manually curated, not derived from OWL axioms
- Does not validate data types (e.g., whether a value is actually a float vs string)
- Does not validate cardinality (e.g., exactly one space group per structure)
- Subclass checking uses simple parent traversal, not full OWL reasoning

## References

- [Validation Rules](references/validation_rules.md) — what is validated and why
- [CMSO Constraints](references/cmso_constraints.json) — required/recommended properties per class
- [CMSO Guide](../ontology-explorer/references/cmso_guide.md) — CMSO ontology overview

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-25 | 1.0 | Initial release with CMSO validation support |
