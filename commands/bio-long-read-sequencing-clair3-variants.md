# bio-long-read-sequencing-clair3-variants

> Deep learning-based variant calling from long reads using Clair3 for SNPs and small indels. Use when calling germline variants from ONT or PacBio alignments, particularly when high accuracy is needed for clinical or research applications.

## Version Compatibility

Reference examples tested with: DeepVariant 1.6+, Entrez Direct 21.0+, bcftools 1.19+, minimap2 2.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Clair3 Variant Calling

**"Call variants from my long-read data"** → Use deep learning to identify germline SNPs and small indels from ONT or PacBio aligned reads with high accuracy.
- CLI: `run_clair3.sh --bam_fn=sample.bam --ref_fn=ref.fa --platform=ont`

## Basic Usage

```bash
# ONT variant calling
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --threads=32 \
    --platform=ont \
    --model_path=${CONDA_PREFIX}/bin/models/ont \
    --output=clair3_output

# PacBio HiFi variant calling
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --threads=32 \
    --platform=hifi \
    --model_path=${CONDA_PREFIX}/bin/models/hifi \
    --output=clair3_output

# Output: clair3_output/merge_output.vcf.gz
```

## Platform-Specific Models

| Platform | Model | Recommended Coverage |
|----------|-------|---------------------|
| ONT R10 | r1041_e82_400bps_sup_v430 | 30-60x |
| ONT R9 | r941_prom_sup_g5014 | 30-60x |
| PacBio HiFi | hifi | 20-40x |
| PacBio CLR | - | Use PEPPER-Margin-DeepVariant |

```bash
# List available models
ls ${CONDA_PREFIX}/bin/models/

# Specify exact model
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --model_path=${CONDA_PREFIX}/bin/models/r1041_e82_400bps_sup_v430 \
    --output=clair3_out \
    --threads=32
```

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| --platform | ont, hifi, or ilmn |
| --model_path | Path to trained model |
| --bed_fn | Restrict calling to regions |
| --include_all_ctgs | Call on all contigs (not just chr1-22,X,Y) |
| --no_phasing_for_fa | Disable phasing |
| --gvcf | Output gVCF format |
| --qual | Minimum variant quality (default: 2) |

## Region-Specific Calling

```bash
# Call variants in specific regions
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --bed_fn=target_regions.bed \
    --threads=32 \
    --platform=ont \
    --model_path=${CONDA_PREFIX}/bin/models/ont \
    --output=clair3_targeted

# Call on non-human genomes (all contigs)
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --include_all_ctgs \
    --threads=32 \
    --platform=hifi \
    --model_path=${CONDA_PREFIX}/bin/models/hifi \
    --output=clair3_all_contigs
```

## gVCF Output

```bash
# Generate gVCF for joint calling
run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --gvcf \
    --threads=32 \
    --platform=ont \
    --model_path=${CONDA_PREFIX}/bin/models/ont \
    --output=clair3_gvcf

# Joint genotyping multiple samples
bcftools merge sample1.g.vcf.gz sample2.g.vcf.gz -o cohort.vcf.gz
```

## Phased Variant Calling

```bash
# With phasing information (requires haplotagged BAM)
run_clair3.sh \
    --bam_fn=haplotagged.bam \
    --ref_fn=reference.fasta \
    --enable_phasing \
    --longphase_for_phasing \
    --threads=32 \
    --platform=ont \
    --model_path=${CONDA_PREFIX}/bin/models/ont \
    --output=clair3_phased
```

## Quality Filtering

```bash
# Filter by quality score
bcftools view -i 'QUAL>20' clair3_output/merge_output.vcf.gz -Oz -o filtered.vcf.gz

# Filter by genotype quality
bcftools view -i 'GQ>30' clair3_output/merge_output.vcf.gz -Oz -o high_gq.vcf.gz

# SNPs only
bcftools view -v snps clair3_output/merge_output.vcf.gz -Oz -o snps.vcf.gz

# Indels only
bcftools view -v indels clair3_output/merge_output.vcf.gz -Oz -o indels.vcf.gz
```

## Python Wrapper

**Goal:** Run Clair3 variant calling and quality filtering from Python with platform-specific model auto-detection.

**Approach:** Build the Clair3 command dynamically from parameters, execute via subprocess, then filter the output VCF with bcftools.

```python
import subprocess
from pathlib import Path

def run_clair3(bam, reference, output_dir, platform='ont', model_path=None,
               threads=32, bed=None, gvcf=False, include_all_ctgs=False):
    if model_path is None:
        import os
        conda_prefix = os.environ.get('CONDA_PREFIX', '')
        model_path = f'{conda_prefix}/bin/models/{platform}'

    cmd = [
        'run_clair3.sh',
        f'--bam_fn={bam}',
        f'--ref_fn={reference}',
        f'--threads={threads}',
        f'--platform={platform}',
        f'--model_path={model_path}',
        f'--output={output_dir}'
    ]

    if bed:
        cmd.append(f'--bed_fn={bed}')
    if gvcf:
        cmd.append('--gvcf')
    if include_all_ctgs:
        cmd.append('--include_all_ctgs')

    subprocess.run(cmd, check=True)
    return Path(output_dir) / 'merge_output.vcf.gz'

def filter_variants(vcf, output, min_qual=20, variant_type=None):
    cmd = ['bcftools', 'view', '-i', f'QUAL>{min_qual}']
    if variant_type:
        cmd.extend(['-v', variant_type])
    cmd.extend([vcf, '-Oz', '-o', output])
    subprocess.run(cmd, check=True)
    subprocess.run(['bcftools', 'index', '-t', output], check=True)
    return output

# Example
vcf = run_clair3('sample.bam', 'ref.fa', 'clair3_out', platform='hifi', threads=48)
snps = filter_variants(str(vcf), 'snps_q20.vcf.gz', min_qual=20, variant_type='snps')
```

## Comparison with Other Callers

| Caller | Best For | Speed | Accuracy |
|--------|----------|-------|----------|
| Clair3 | ONT/HiFi germline | Fast | High |
| DeepVariant | HiFi, Illumina | Medium | Very high |
| PEPPER-DV | ONT (integrated) | Slow | Very high |
| Longshot | ONT SNPs | Fast | Good |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing model | Download from Clair3 releases or use conda models |
| Low call rate | Check coverage; increase --qual threshold |
| Slow performance | Reduce --threads or use --bed_fn for targeted calling |
| Wrong variants on non-human | Use --include_all_ctgs |

## Docker Usage

```bash
# Using Docker
docker run -v /data:/data \
    hkubal/clair3:latest \
    /opt/bin/run_clair3.sh \
    --bam_fn=/data/sample.bam \
    --ref_fn=/data/reference.fasta \
    --threads=32 \
    --platform=ont \
    --model_path=/opt/models/ont \
    --output=/data/clair3_output

# Singularity
singularity exec clair3.sif run_clair3.sh \
    --bam_fn=sample.bam \
    --ref_fn=reference.fasta \
    --threads=32 \
    --platform=ont \
    --model_path=/opt/models/ont \
    --output=clair3_output
```

## Related Skills

- variant-calling/bcftools-basics - VCF manipulation
- variant-calling/filtering-best-practices - Quality filtering
- long-read-sequencing/long-read-qc - Input quality control
- long-read-sequencing/long-read-alignment - Mapping with minimap2
