# fastq-analysis-pipeline

> Guide through omicverse's alignment module for SRA downloading, FASTQ quality control, STAR alignment, gene quantification, and single-cell kallisto/bustools pipelines covering both bulk and single-cell RNA-seq workflows.

## Overview

OmicVerse provides a complete FASTQ-to-count-matrix pipeline via the `ov.alignment` module. This skill covers:

- **SRA data acquisition**: `prefetch` and `fqdump` (fasterq-dump wrapper)
- **Quality control**: `fastp` for adapter trimming and QC reports
- **RNA-seq alignment**: `STAR` aligner with auto-index building
- **Gene quantification**: `featureCount` (subread featureCounts wrapper)
- **Single-cell path**: `ref` and `count` via kb-python (kallisto/bustools)
- **Parallel SRA download**: `parallel_fastq_dump`

All functions share a common CLI infrastructure (`_cli_utils.py`) that handles tool resolution, auto-installation via conda/mamba, parallel execution, and streaming output.

## Instructions

1. **Environment setup**
   - Bioinformatics tools are resolved automatically from PATH or the active conda environment.
   - If `auto_install=True` (default), missing tools are installed via mamba/conda on demand.
   - Supported tools: `prefetch`, `vdb-validate`, `fasterq-dump`, `fastp`, `STAR`, `samtools`, `featureCounts`, `pigz`, `gzip`.
   - For the single-cell path, ensure `kb-python` is installed: `pip install kb-python`.

2. **SRA data download** (`ov.alignment.prefetch` + `ov.alignment.fqdump`)
   - Use `prefetch` first for reliable downloads with integrity validation (`vdb-validate`).
   - Then convert to FASTQ with `fqdump`. It auto-detects single-end vs paired-end.
   - `fqdump` can also work directly from SRR accessions without prefetch.
   - Both support retry with exponential backoff for network errors.
   ```python
   import omicverse as ov

   # Step 1: Prefetch SRA files (optional but recommended)
   pre = ov.alignment.prefetch(['SRR1234567', 'SRR1234568'], output_dir='prefetch', jobs=4)

   # Step 2: Convert to FASTQ
   fq = ov.alignment.fqdump(['SRR1234567', 'SRR1234568'],
                             output_dir='fastq', sra_dir='prefetch',
                             gzip=True, threads=8, jobs=4)
   ```

3. **FASTQ quality control** (`ov.alignment.fastp`)
   - Runs fastp for adapter trimming, quality filtering, and QC reporting.
   - Supports single-end and paired-end reads.
   - Produces per-sample JSON and HTML QC reports.
   - Sample format: tuple of `(sample_name, fq1_path, fq2_path_or_None)`.
   ```python
   samples = [
       ('S1', 'fastq/SRR1234567/SRR1234567_1.fastq.gz', 'fastq/SRR1234567/SRR1234567_2.fastq.gz'),
       ('S2', 'fastq/SRR1234568/SRR1234568_1.fastq.gz', 'fastq/SRR1234568/SRR1234568_2.fastq.gz'),
   ]
   clean = ov.alignment.fastp(samples, output_dir='fastp', threads=8, jobs=2)
   ```

4. **STAR alignment** (`ov.alignment.STAR`)
   - Aligns FASTQ reads using the STAR aligner.
   - **Auto-index building**: set `auto_index=True` (default) with `genome_fasta_files` and `gtf` to build index automatically if missing.
   - Produces coordinate-sorted BAM files.
   - Handles gzip-compressed FASTQs automatically (uses pigz/gzip/zcat).
   - Use `strict=False` (default) for graceful error handling per sample.
   ```python
   # Prepare samples from fastp output
   star_samples = [
       ('S1', 'fastp/S1/S1_clean_1.fastq.gz', 'fastp/S1/S1_clean_2.fastq.gz'),
       ('S2', 'fastp/S2/S2_clean_1.fastq.gz', 'fastp/S2/S2_clean_2.fastq.gz'),
   ]
   bams = ov.alignment.STAR(
       star_samples,
       genome_dir='star_index',
       output_dir='star_out',
       gtf='genes.gtf',
       genome_fasta_files=['genome.fa'],
       threads=8,
       memory='50G',
   )
   ```

5. **Gene quantification** (`ov.alignment.featureCount`)
   - Counts aligned reads per gene using featureCounts (subread).
   - Auto-detects paired-end from BAM headers (via pysam or samtools).
   - `auto_fix=True` (default) retries with corrected paired-end flag on error.
   - `gene_mapping=True` maps gene_id to gene_name from the GTF.
   - `merge_matrix=True` produces a combined count matrix across all samples.
   ```python
   bam_items = [
       ('S1', 'star_out/S1/Aligned.sortedByCoord.out.bam'),
       ('S2', 'star_out/S2/Aligned.sortedByCoord.out.bam'),
   ]
   counts = ov.alignment.featureCount(
       bam_items,
       gtf='genes.gtf',
       output_dir='counts',
       gene_mapping=True,
       merge_matrix=True,
       threads=8,
   )
   # counts is a pandas DataFrame (gene_id x samples)
   ```

6. **Single-cell path** (`ov.alignment.ref` + `ov.alignment.count`)
   - Uses kb-python (kallisto + bustools) for single-cell RNA-seq quantification.
   - `ref()` builds a kallisto index and transcript-to-gene mapping.
   - `count()` quantifies single-cell data with barcode/UMI handling.
   - Supports technologies: 10XV2, 10XV3, BULK, and custom.
   - Output formats: h5ad, loom, cellranger MTX.
   ```python
   # Build reference index
   ref_result = ov.alignment.ref(
       index_path='kb_ref/index.idx',
       t2g_path='kb_ref/t2g.txt',
       fasta_paths=['genome.fa'],
       gtf_paths=['genes.gtf'],
       threads=8,
   )

   # Quantify 10x v3 data
   count_result = ov.alignment.count(
       index_path='kb_ref/index.idx',
       t2g_path='kb_ref/t2g.txt',
       technology='10XV3',
       fastq_paths=['sample_R1.fastq.gz', 'sample_R2.fastq.gz'],
       output_path='kb_out',
       h5ad=True,
       filter_barcodes=True,
       threads=8,
   )
   ```

7. **Wiring fastp output into STAR input**
   - fastp output is a list of dicts with keys: `sample`, `clean1`, `clean2`, `json`, `html`.
   - Convert to STAR sample tuples:
   ```python
   star_samples = [
       (r['sample'], r['clean1'], r['clean2'] if r['clean2'] else None)
       for r in (clean if isinstance(clean, list) else [clean])
   ]
   ```

8. **Wiring STAR output into featureCount input**
   - STAR output is a list of dicts with keys: `sample`, `bam` (or `error`).
   - Convert to featureCount items:
   ```python
   bam_items = [
       (r['sample'], r['bam'])
       for r in (bams if isinstance(bams, list) else [bams])
       if 'bam' in r
   ]
   ```

9. **Skipping completed steps**
   - All functions check for existing outputs and skip if `overwrite=False` (default).
   - Set `overwrite=True` to force re-execution.

10. **Troubleshooting**
    - If a tool is not found, check `auto_install=True` and that conda/mamba is accessible.
    - For STAR index errors, ensure `genome_fasta_files` points to uncompressed or gzip FASTA files.
    - For featureCounts paired-end detection errors, `auto_fix=True` handles most cases automatically.
    - GTF files can be gzip-compressed; they are auto-decompressed as needed.

## Critical API Reference

### Sample Format Convention

All alignment functions use a consistent sample tuple format:
- **FASTQ samples**: `(sample_name, fq1_path, fq2_path_or_None)`
- **BAM items**: `(sample_name, bam_path)` or `(sample_name, bam_path, is_paired_bool)`
- Single samples can be passed as a single tuple; multiple as a list of tuples.
- When a single tuple is passed, the return value is a single dict; for a list, a list of dicts.

### Auto-installation

```python
# All functions support these parameters:
auto_install=True   # Auto-install missing tools via conda/mamba
overwrite=False     # Skip if outputs already exist
threads=8           # Per-tool thread count
jobs=None           # Concurrent job count (auto-detected from CPU count)
```

## Examples

- **Bulk RNA-seq from SRA**: `prefetch` -> `fqdump` -> `fastp` -> `STAR` -> `featureCount` -> pandas DataFrame
- **Single-cell 10x v3**: `ref` -> `count` with `technology='10XV3'` -> h5ad AnnData
- **Local FASTQ files**: Skip download steps, start directly with `fastp` -> `STAR` -> `featureCount`

## References

- See [reference.md](reference.md) for copy-paste-ready code templates.
