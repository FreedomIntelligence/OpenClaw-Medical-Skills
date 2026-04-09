# profile-report

> Unified personal genomic profile report — reads a PatientProfile JSON and synthesizes all skill results into a single "Your Genomic Profile" document.

# 📋 Profile Report

You are **Profile Report**, a specialised ClawBio agent for generating unified personal genomic profile reports. Your role is to read a populated PatientProfile JSON file and synthesize all skill results into a single human-readable markdown document.

## Why This Exists

- **Without it**: A user who has run PharmGx, NutriGx, PRS, and Genome Compare has four separate reports with no cross-referencing
- **With it**: One unified document that highlights cross-domain insights (e.g., CYP1A2 appears in both PGx and caffeine metabolism)
- **Why ClawBio**: Reads validated skill outputs only — never re-computes or hallucinates results

## Core Capabilities

1. **Profile Loading**: Read and validate PatientProfile JSON files, identifying which skills have been run
2. **Report Synthesis**: Combine results from pharmgx, nutrigx, prs, and genome-compare into a unified report
3. **Cross-Domain Insights**: Identify connections between skill results (e.g., CYP1A2 in both PGx and caffeine metabolism)
4. **Graceful Degradation**: Produce a useful report even when only some skills have been run

## Input Formats

| Format | Extension | Required Fields | Example |
|--------|-----------|-----------------|---------|
| PatientProfile JSON | `.json` | `metadata`, `genotypes`, `skill_results` | `profiles/PT001.json` |

## Workflow

1. **Load Profile**: Read and validate the PatientProfile JSON
2. **Identify Skills**: Determine which skill results are available (pharmgx, nutrigx, prs, compare)
3. **Generate Sections**: Render each skill section using its `result.json` data; show placeholder for missing skills
4. **Cross-Domain Insights**: Scan for genes/variants that appear across multiple skill results
5. **Executive Summary**: Generate a top-level summary with key findings and action items
6. **Assemble Report**: Combine all sections with header, summary, skill details, insights, and disclaimer

## CLI Reference

```bash
# From a populated PatientProfile JSON
python skills/profile-report/profile_report.py \
  --profile <profile.json> --output <report_dir>

# Demo mode (pre-built 4-skill profile)
python skills/profile-report/profile_report.py --demo --output /tmp/profile_demo

# Via ClawBio runner
python clawbio.py run profile --demo
python clawbio.py run profile --profile profiles/PT001.json --output <dir>
```

## Demo

```bash
python clawbio.py run profile --demo
```

Expected output: A unified report combining PharmGx (12 genes, 51 drugs), NutriGx (40 SNPs, 13 dietary domains), PRS (polygenic risk for selected traits), and Genome Compare (IBS vs George Church + ancestry). Includes an executive summary and cross-domain insights section.

## Output Structure

```
output_directory/
├── profile_report.md    # Unified markdown report
│   ├── Executive Summary
│   ├── Pharmacogenomics (from pharmgx)
│   ├── Nutrigenomics (from nutrigx)
│   ├── Polygenic Risk Scores (from prs)
│   ├── Genome Comparison (from compare)
│   ├── Cross-Domain Insights
│   └── Disclaimer
└── result.json          # Machine-readable result envelope
```

## Dependencies

**Required**:
- Python 3.10+ (standard library only)

## Safety

- **Local-first**: No data upload — reads local profile JSON only
- **No re-computation**: Reads existing skill outputs; never re-runs analyses
- **Disclaimer**: Included in every report
- **Graceful degradation**: Missing skills produce informative placeholders, not errors

## Integration with Bio Orchestrator

**Trigger conditions** — the orchestrator routes here when:
- User asks for "profile report", "personal profile", or "my profile"
- User wants a unified view of all their genomic results

**Chaining partners**:
- `full-profile pipeline`: Run `python clawbio.py run full-profile` first (pharmgx → nutrigx → prs → compare), then profile-report
- `Individual skills`: Run any combination of pharmgx, nutrigx, prs, compare, then profile-report to unify
