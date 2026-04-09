# bio-read-qc-contamination-screening

> Detect sample contamination and cross-species reads using FastQ Screen. Screen reads against multiple reference genomes to identify bacterial, viral, adapter, or sample swap contamination. Use when suspecting cross-contamination or working with samples prone to microbial contamination.

## Version Compatibility

Reference examples tested with: BBTools 39.0+, Bowtie2 2.5.3+, FastQ Screen 0.15+, FastQC 0.12+, MultiQC 1.21+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Contamination Screening

Screen FASTQ files against multiple genomes to identify contamination sources using FastQ Screen.

**"Check for contamination in sequencing data"** → Align a sample of reads against multiple reference genomes to identify cross-species or cross-sample contamination.
- CLI: `fastq_screen --conf fastq_screen.conf reads.fq`

## FastQ Screen Overview

FastQ Screen aligns a subset of reads against multiple reference genomes to identify:
- Cross-species contamination
- Bacterial/viral contamination
- Adapter sequences
- PhiX spike-in
- Sample swaps

## Basic Usage

```bash
# Screen against configured genomes
fastq_screen sample.fastq.gz

# Multiple files
fastq_screen *.fastq.gz

# Specify output directory
fastq_screen --outdir qc_results/ sample.fastq.gz

# Custom config file
fastq_screen --conf my_screen.conf sample.fastq.gz
```

## Configuration File

Create `fastq_screen.conf`:

```
# Database locations
DATABASE	Human	/path/to/human/genome
DATABASE	Mouse	/path/to/mouse/genome
DATABASE	Ecoli	/path/to/ecoli/genome
DATABASE	PhiX	/path/to/phix/genome
DATABASE	Adapters	/path/to/adapters
DATABASE	rRNA	/path/to/rrna

# Aligner (bowtie2 recommended)
BOWTIE2	/path/to/bowtie2

# Or use BWA
# BWA	/path/to/bwa

# Threads
THREADS	8
```

### Pre-built Databases

```bash
# Download common screening databases
fastq_screen --get_genomes

# Downloads to ~/fastq_screen_databases/
# Includes: Human, Mouse, Rat, E.coli, PhiX, Adapters, etc.
```

## Screening Options

```bash
# Number of reads to sample (default 100000)
fastq_screen --subset 200000 sample.fastq.gz

# Use all reads (slow)
fastq_screen --subset 0 sample.fastq.gz

# Set threads
fastq_screen --threads 8 sample.fastq.gz

# Paired-end (screen R1 only by default)
fastq_screen sample_R1.fastq.gz

# Force screening both pairs
fastq_screen --paired sample_R1.fastq.gz sample_R2.fastq.gz
```

## Output Options

```bash
# Generate PNG plot (default)
fastq_screen sample.fastq.gz

# No plot (text only)
fastq_screen --nograph sample.fastq.gz

# Generate additional mapping statistics
fastq_screen --tag sample.fastq.gz

# Filter reads by mapping (keep unmapped to all genomes)
fastq_screen --filter 0000 sample.fastq.gz

# Keep only reads mapping to first genome (e.g., Human)
fastq_screen --filter 1--- sample.fastq.gz
```

## Filter Codes

Use `--filter` to select reads based on mapping status:

| Code | Meaning |
|------|---------|
| 0 | Did not map to genome |
| 1 | Mapped uniquely |
| 2 | Mapped more than once |
| 3 | Mapped (unique or multi) |
| - | Ignore this genome |

```bash
# Example: Keep reads mapping only to Human (first genome)
# Human:1, all others:0
fastq_screen --filter 10000 sample.fastq.gz

# Keep reads NOT mapping to anything (clean reads)
fastq_screen --filter 00000 sample.fastq.gz
```

## Output Files

| File | Description |
|------|-------------|
| `*_screen.txt` | Tab-delimited results |
| `*_screen.png` | Visualization |
| `*_screen.html` | HTML report |

### Results Format

```
#Fastq_screen version: 0.15.3
Genome	#Reads_processed	#Unmapped	%Unmapped	#One_hit_one_genome	%One_hit_one_genome	#Multiple_hits_one_genome	%Multiple_hits_one_genome	#One_hit_multiple_genomes	%One_hit_multiple_genomes	Multiple_hits_multiple_genomes	%Multiple_hits_multiple_genomes
Human	100000	2000	2.00	95000	95.00	1000	1.00	1500	1.50	500	0.50
Mouse	100000	98000	98.00	100	0.10	50	0.05	1500	1.50	350	0.35
```

## Interpreting Results

### Expected Results by Sample Type

| Sample Type | Expected Pattern |
|-------------|------------------|
| Human sample | >90% Human, <1% others |
| Mouse sample | >90% Mouse, <1% others |
| Human + PhiX | >80% Human, ~10% PhiX |
| Contaminated | Significant % to unexpected genome |

### Common Issues

| Pattern | Likely Cause |
|---------|--------------|
| High adapter % | Library prep issue |
| High PhiX % | Spike-in not removed |
| High E.coli % | Bacterial contamination |
| High rRNA % | rRNA depletion failed |
| Multiple species | Sample swap or contamination |

## MultiQC Integration

FastQ Screen results are automatically detected by MultiQC:

```bash
# Screen all samples
for f in *.fastq.gz; do
    fastq_screen --outdir screen_results/ "$f"
done

# Aggregate with MultiQC
multiqc screen_results/
```

## Custom Database Setup

### Create Bowtie2 Index

```bash
# Index a FASTA file
bowtie2-build reference.fa reference

# Add to config
# DATABASE	MyGenome	/path/to/reference
```

### Common Databases to Include

| Genome | Purpose |
|--------|---------|
| Human (GRCh38) | Human samples |
| Mouse (GRCm39) | Mouse samples |
| E. coli | Bacterial contamination |
| PhiX | Illumina spike-in |
| Adapters | Library prep |
| rRNA | Ribosomal RNA |
| Vectors | Cloning vectors |
| Mycoplasma | Cell culture contamination |

## Example Workflows

### Standard Screening

```bash
# Download databases
fastq_screen --get_genomes

# Screen samples
fastq_screen --outdir screen_results/ --threads 8 *.fastq.gz

# Check results
multiqc screen_results/
```

### Remove Contamination

```bash
# Screen and tag reads
fastq_screen --tag sample.fastq.gz

# Filter to keep only Human reads (assuming Human is first database)
fastq_screen --filter 3----- --tag sample.fastq.gz

# Or use BBDuk for removal
bbduk.sh in=sample.fastq.gz out=clean.fastq.gz \
    ref=contaminants.fa k=31 hdist=1
```

## Related Skills

- quality-reports - FastQC shows overrepresented sequences
- adapter-trimming - Remove adapter contamination
- metagenomics/kraken-classification - Deeper taxonomic analysis
