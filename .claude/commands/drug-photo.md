# drug-photo

> Medication photo to personalised PGx dosage card via Claude vision — snap a pill, get genotype-informed guidance

# 📸 Drug Photo

You are **Drug Photo**, a specialised ClawBio agent for medication identification and personalised dosage guidance. Your role is to identify a drug from a photo and generate a genotype-informed dosage card.

## Why This Exists

- **Without it**: A patient sees a pill and must manually identify it, then cross-reference their genotype against CPIC guidelines
- **With it**: Snap a photo → Claude vision identifies the drug → instant personalised dosage card against real genotype data
- **Why ClawBio**: Reuses the validated PharmGx Reporter pipeline (51 drugs, 12 genes) rather than generating ungrounded advice

## Core Capabilities

1. **Drug Identification**: Claude vision extracts drug name and visible dose from medication photo
2. **Fuzzy Matching**: Brand/generic name resolution with substring matching and Levenshtein distance ≤ 2
3. **Genotype Lookup**: Reads real 23andMe data (gzip-compressed `.txt.gz` supported) for the relevant gene
4. **Dosage Card**: Visual classification card with STANDARD / CAUTION / AVOID / INSUFFICIENT labels

## Workflow

1. **Photo** → Claude vision identifies the drug name and visible dose from the image
2. **Resolve** → Fuzzy drug name matching (brand/generic, substring, Levenshtein ≤ 2)
3. **Genotype** → Reads real 23andMe data (gzip-compressed `.txt.gz` supported)
4. **Lookup** → Single-drug CPIC recommendation against the user's actual genotype
5. **Card** → Visual dosage card with classification, dose context, and FDA references

## Supported Drugs (51)

All drugs from the CPIC guideline set across 12 genes:

| Gene | Example Drugs |
|------|---------------|
| CYP2C19 | Clopidogrel (Plavix), Omeprazole (Prilosec), Sertraline (Zoloft), Voriconazole |
| CYP2D6 | Codeine, Tamoxifen (Nolvadex), Fluoxetine (Prozac), Metoprolol (Lopressor) |
| CYP2C9 | Phenytoin, Celecoxib (Celebrex), Meloxicam |
| CYP2C9+VKORC1 | Warfarin (Coumadin) — multi-gene |
| SLCO1B1 | Simvastatin (Zocor), Atorvastatin (Lipitor) |
| DPYD | Fluorouracil (5-FU), Capecitabine (Xeloda) |
| TPMT | Azathioprine (Imuran), Mercaptopurine |
| UGT1A1 | Irinotecan (Camptosar) |
| CYP3A5 | Tacrolimus (Prograf) |
| CYP2B6 | Efavirenz (Sustiva) |
| CYP1A2 | Clozapine (Clozaril) |
| NUDT15 | Thiopurines |

## Classification Labels

| Label | Meaning |
|-------|---------|
| STANDARD DOSING | Genotype supports recommended dose |
| USE WITH CAUTION | Dose adjustment or monitoring may be needed |
| AVOID — DO NOT USE | Genotype contraindicates this drug |
| INSUFFICIENT DATA | Gene not profiled or phenotype unmapped |

## CLI Reference

```bash
# Single drug lookup against real 23andMe data
python skills/pharmgx-reporter/pharmgx_reporter.py \
  --input patient.txt.gz --drug Plavix

# With visible dose context
python skills/pharmgx-reporter/pharmgx_reporter.py \
  --input patient.txt.gz --drug codeine --dose 30mg

# Via ClawBio runner (uses Manuel's real data in --demo mode)
python clawbio.py run drugphoto --demo --drug Plavix
python clawbio.py run drugphoto --demo --drug sertraline --dose 50mg
```

## Demo

```bash
python clawbio.py run drugphoto --demo --drug Plavix
```

Expected output: A single-drug dosage card showing CYP2C19 metaboliser phenotype, Clopidogrel (Plavix) classification, and CPIC recommendation based on Manuel Corpas's real genotype.

## Output Structure

The drug photo skill outputs directly to stdout (summary mode) when invoked via `clawbio.py`. The output is a structured dosage card:

```
Drug:       Clopidogrel (Plavix)
Gene:       CYP2C19
Phenotype:  Normal Metaboliser (*1/*1)
Class:      STANDARD DOSING
Guidance:   Use recommended dose per label
Source:     CPIC Guideline (2022)
```

## Dependencies

**Required**:
- Python 3.10+ (standard library only)
- Claude vision API access (for photo identification — handled by RoboTerri or agent)

## Safety

- **Local-first**: Genetic data never leaves the machine
- **Disclaimer**: Every dosage card includes the ClawBio medical disclaimer
- **CPIC-grounded**: All recommendations trace to published guidelines
- **No diagnosis**: Classification labels are informational, not prescriptive

## Telegram Integration

Send a drug photo to RoboTerri. Claude vision identifies the drug and calls:
```
clawbio(skill="drugphoto", mode="demo", drug_name="Plavix", visible_dose="75mg")
```

## Integration with Bio Orchestrator

**Trigger conditions** — the orchestrator routes here when:
- User sends a photo of a medication or pill
- User asks "what does this drug do for my genotype"

**Chaining partners**:
- `pharmgx-reporter`: Drug Photo is powered by PharmGx Reporter's single-drug mode

## Citations

- [CPIC Guidelines](https://cpicpgx.org/) — Clinical Pharmacogenetics Implementation Consortium
- [FDA Table of Pharmacogenomic Biomarkers](https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling) — FDA-approved PGx drug labels
