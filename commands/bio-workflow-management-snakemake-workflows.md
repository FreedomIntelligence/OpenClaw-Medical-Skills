# bio-workflow-management-snakemake-workflows

> Build reproducible bioinformatics pipelines with Snakemake using rules, wildcards, and automatic dependency resolution. Use when creating Python-based workflows, automating multi-step analyses with make-like dependency tracking, or running pipelines on HPC clusters with SLURM.

**Available tools:** Read, Bash

# Snakemake Workflows

Compatible with Snakemake 7.x, 8.x, and 9.x. For Snakemake 8.0+, use `--executor` instead of `--cluster`.

## Basic Rule Structure

```python
# Snakefile

rule all:
    input:
        expand("results/{sample}_counts.txt", sample=SAMPLES)

rule align:
    input:
        r1 = "data/{sample}_R1.fq.gz",
        r2 = "data/{sample}_R2.fq.gz",
        index = "ref/genome.fa"
    output:
        bam = "aligned/{sample}.bam"
    threads: 8
    shell:
        "bwa mem -t {threads} {input.index} {input.r1} {input.r2} | "
        "samtools sort -@ {threads} -o {output.bam}"
```

## Config File

```yaml
# config.yaml
samples:
  - sample1
  - sample2
  - sample3

reference: "ref/genome.fa"
threads: 8
```

```python
# Snakefile
configfile: "config.yaml"

SAMPLES = config["samples"]
REF = config["reference"]

rule all:
    input:
        expand("results/{sample}.bam", sample=SAMPLES)
```

## Wildcards and Expand

```python
# Define samples
SAMPLES = ["A", "B", "C"]
CHROMOSOMES = [str(i) for i in range(1, 23)] + ["X", "Y"]

# Expand for all combinations
rule all:
    input:
        expand("results/{sample}_{chrom}.vcf", sample=SAMPLES, chrom=CHROMOSOMES)

# Access wildcard in rule
rule process:
    input:
        "data/{sample}.bam"
    output:
        "results/{sample}.vcf"
    params:
        sample = lambda wildcards: wildcards.sample
    shell:
        "bcftools call -s {params.sample} {input} > {output}"
```

## Python Integration

```python
rule analyze:
    input:
        counts = "data/{sample}_counts.txt"
    output:
        results = "results/{sample}_de.csv"
    run:
        import pandas as pd
        counts = pd.read_csv(input.counts, sep='\t')
        # Process data
        results = counts.groupby('gene').sum()
        results.to_csv(output.results)
```

## Conda Environments

```python
rule fastqc:
    input:
        "data/{sample}.fq.gz"
    output:
        "qc/{sample}_fastqc.html"
    conda:
        "envs/qc.yaml"
    shell:
        "fastqc {input} -o qc/"
```

```yaml
# envs/qc.yaml
channels:
  - bioconda
  - conda-forge
dependencies:
  - fastqc=0.12.1
  - multiqc=1.14
```

## Container Support

```python
rule align:
    input:
        r1 = "data/{sample}_R1.fq.gz"
    output:
        bam = "aligned/{sample}.bam"
    container:
        "docker://biocontainers/bwa:v0.7.17"
    shell:
        "bwa mem {input} | samtools sort -o {output}"
```

```bash
# Run with Singularity
snakemake --use-singularity --singularity-args "-B /data"
```

## Resource Management

```python
rule memory_intensive:
    input:
        "data/{sample}.bam"
    output:
        "results/{sample}.vcf"
    threads: 4
    resources:
        mem_mb = 16000,
        time = "4:00:00",
        gpu = 1
    shell:
        "variant_caller --threads {threads} {input} > {output}"
```

## Cluster Execution

```yaml
# cluster.yaml
__default__:
    partition: normal
    time: "1:00:00"
    mem: 4G

align:
    partition: normal
    time: "8:00:00"
    mem: 32G
    cpus-per-task: 8
```

```bash
# Snakemake 8.x with executor plugin
pip install snakemake-executor-plugin-slurm
snakemake --executor slurm --jobs 100

# Snakemake 7.x cluster execution
snakemake --cluster "sbatch --partition={cluster.partition} \
    --time={cluster.time} --mem={cluster.mem}" \
    --cluster-config cluster.yaml --jobs 100

# Or use profile (both versions)
snakemake --profile slurm
```

## Checkpoints

```python
# For rules that determine downstream files dynamically
checkpoint split_samples:
    input:
        "data/all_samples.txt"
    output:
        directory("split/")
    shell:
        "split_script.py {input} {output}"

def get_split_files(wildcards):
    checkpoint_output = checkpoints.split_samples.get(**wildcards).output[0]
    return expand("split/{sample}.txt", sample=glob_wildcards("split/{sample}.txt").sample)

rule aggregate:
    input:
        get_split_files
    output:
        "results/aggregated.txt"
    shell:
        "cat {input} > {output}"
```

## Modular Workflows

```python
# Snakefile
include: "rules/qc.smk"
include: "rules/align.smk"
include: "rules/call.smk"

rule all:
    input:
        rules.qc_all.input,
        rules.call_all.input
```

```python
# rules/qc.smk
rule fastqc:
    input: "data/{sample}.fq.gz"
    output: "qc/{sample}_fastqc.html"
    shell: "fastqc {input} -o qc/"

rule qc_all:
    input: expand("qc/{sample}_fastqc.html", sample=SAMPLES)
```

## Temporary and Protected Files

```python
rule align:
    input:
        "data/{sample}.fq.gz"
    output:
        bam = temp("aligned/{sample}.unsorted.bam"),  # Auto-deleted
        sorted = protected("aligned/{sample}.bam")     # Write-protected
    shell:
        "bwa mem {input} > {output.bam} && "
        "samtools sort {output.bam} -o {output.sorted}"
```

## Benchmarking

```python
rule heavy_computation:
    input:
        "data/{sample}.bam"
    output:
        "results/{sample}.txt"
    benchmark:
        "benchmarks/{sample}.tsv"
    shell:
        "heavy_tool {input} > {output}"
```

## Logging

```python
rule process:
    input:
        "data/{sample}.bam"
    output:
        "results/{sample}.txt"
    log:
        "logs/{sample}.log"
    shell:
        "(command {input} > {output}) 2> {log}"
```

## Run Commands

```bash
# Dry run (show what would be executed)
snakemake -n

# Run with 8 cores
snakemake --cores 8

# Force rerun of specific rule
snakemake --forcerun align

# Run until specific target
snakemake results/sample1.vcf

# Generate DAG visualization
snakemake --dag | dot -Tpdf > dag.pdf

# Generate report
snakemake --report report.html
```

## Complete RNA-seq Workflow

```python
configfile: "config.yaml"

SAMPLES = config["samples"]

rule all:
    input:
        "results/multiqc_report.html",
        "results/deseq2_results.csv"

rule fastp:
    input:
        r1 = "data/{sample}_R1.fq.gz",
        r2 = "data/{sample}_R2.fq.gz"
    output:
        r1 = "trimmed/{sample}_R1.fq.gz",
        r2 = "trimmed/{sample}_R2.fq.gz",
        json = "qc/{sample}_fastp.json"
    threads: 4
    shell:
        "fastp -i {input.r1} -I {input.r2} -o {output.r1} -O {output.r2} "
        "--json {output.json} --thread {threads}"

rule salmon_quant:
    input:
        r1 = "trimmed/{sample}_R1.fq.gz",
        r2 = "trimmed/{sample}_R2.fq.gz",
        index = config["salmon_index"]
    output:
        directory("salmon/{sample}")
    threads: 8
    shell:
        "salmon quant -i {input.index} -l A -1 {input.r1} -2 {input.r2} "
        "-o {output} --threads {threads}"

rule multiqc:
    input:
        expand("qc/{sample}_fastp.json", sample=SAMPLES),
        expand("salmon/{sample}", sample=SAMPLES)
    output:
        "results/multiqc_report.html"
    shell:
        "multiqc qc/ salmon/ -o results/"

rule deseq2:
    input:
        quants = expand("salmon/{sample}", sample=SAMPLES),
        metadata = config["metadata"]
    output:
        "results/deseq2_results.csv"
    script:
        "scripts/deseq2.R"
```

## Related Skills

- workflow-management/nextflow-pipelines - Nextflow alternative
- workflows/rnaseq-to-de - RNA-seq workflow
- read-qc/fastp-workflow - QC in pipelines
