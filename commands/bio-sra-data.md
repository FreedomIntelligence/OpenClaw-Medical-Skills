# bio-sra-data

> Download sequencing data from NCBI SRA using the SRA toolkit. Use when downloading FASTQ files from SRA accessions, prefetching large datasets, or validating SRA downloads.

**Available tools:** Read, Bash

# SRA Data

Download raw sequencing data from the Sequence Read Archive using the SRA toolkit.

## Installation

```bash
# macOS
brew install sratoolkit

# Ubuntu/Debian
sudo apt install sra-toolkit

# conda (recommended)
conda install -c bioconda sra-tools

# Verify installation
fasterq-dump --version
```

## Core Commands

### fasterq-dump - Download FASTQ (Recommended)

Fast, multithreaded FASTQ extraction. Preferred over `fastq-dump`.

```bash
# Download single SRA run as FASTQ
fasterq-dump SRR12345678

# Output: SRR12345678.fastq (single-end)
# Or: SRR12345678_1.fastq, SRR12345678_2.fastq (paired-end)
```

**Key Options:**
| Option | Description | Example |
|--------|-------------|---------|
| `-O` / `--outdir` | Output directory | `-O ./fastq/` |
| `-o` / `--outfile` | Output filename | `-o sample.fastq` |
| `-e` / `--threads` | Number of threads | `-e 8` |
| `-p` / `--progress` | Show progress bar | `-p` |
| `-S` / `--split-files` | Split paired reads (default) | `-S` |
| `-3` / `--split-3` | Also output unpaired reads | `-3` |
| `--skip-technical` | Skip technical reads | `--skip-technical` |
| `-t` / `--temp` | Temp directory | `-t /tmp` |
| `-f` / `--force` | Overwrite existing | `-f` |

```bash
# Common usage with options
fasterq-dump SRR12345678 -O ./data/ -e 8 -p --skip-technical

# Force split files (paired-end)
fasterq-dump SRR12345678 -S -O ./data/
```

### prefetch - Download SRA Files First

For large files or unreliable connections, prefetch first, then convert.

```bash
# Prefetch SRA file (downloads .sra to ~/ncbi/sra/)
prefetch SRR12345678

# Then convert to FASTQ
fasterq-dump ~/ncbi/sra/SRR12345678.sra

# Or convert in place
fasterq-dump SRR12345678  # Will find prefetched file
```

**Prefetch Options:**
| Option | Description |
|--------|-------------|
| `-O` / `--output-directory` | Download location |
| `-p` / `--progress` | Show progress |
| `-f` / `--force` | Re-download if exists |
| `--max-size` | Max file size (e.g., `50G`) |
| `-X` / `--max-size` | Same as above |

```bash
# Prefetch with size limit
prefetch SRR12345678 --max-size 100G -p

# Prefetch multiple accessions
prefetch SRR12345678 SRR12345679 SRR12345680

# Prefetch from a list file
prefetch --option-file accessions.txt
```

### vdb-validate - Verify Downloads

Check integrity of downloaded SRA files.

```bash
# Validate a downloaded file
vdb-validate SRR12345678

# Validate with detailed output
vdb-validate SRR12345678 2>&1
```

### sra-stat - Get Run Statistics

Get information about an SRA run without downloading.

```bash
# Basic stats
sra-stat --quick SRR12345678

# Detailed XML output
sra-stat --xml SRR12345678
```

## Configuration

### vdb-config - Configure SRA Toolkit

Set up cache location and other settings.

```bash
# Interactive configuration
vdb-config -i

# Set cache directory
vdb-config --set /repository/user/main/public/root=/path/to/cache

# Check current configuration
vdb-config --cfg
```

### Cache Location

Default: `~/ncbi/` on Linux/macOS

```bash
# Create dedicated cache
mkdir -p /data/sra_cache
vdb-config --set /repository/user/main/public/root=/data/sra_cache
```

## Code Patterns

### Download Single Run

```bash
#!/bin/bash
SRR="SRR12345678"
OUTDIR="./fastq"

mkdir -p $OUTDIR
fasterq-dump $SRR -O $OUTDIR -e 8 -p
```

### Download Multiple Runs

```bash
#!/bin/bash
# From a list of accessions
while read SRR; do
    echo "Downloading $SRR..."
    fasterq-dump $SRR -O ./fastq/ -e 4 -p
done < accessions.txt
```

### Prefetch Then Convert (Large Files)

```bash
#!/bin/bash
SRR="SRR12345678"

# Prefetch first (resumable)
prefetch $SRR -p

# Validate
vdb-validate $SRR

# Convert to FASTQ
fasterq-dump $SRR -O ./fastq/ -e 8 -p

# Optionally remove .sra file
rm -f ~/ncbi/sra/${SRR}.sra
```

### Batch Download Script

```bash
#!/bin/bash
# download_sra.sh - Download multiple SRA runs

ACCESSIONS="$1"
OUTDIR="${2:-./fastq}"
THREADS="${3:-4}"

mkdir -p $OUTDIR

while read SRR; do
    if [[ -z "$SRR" ]] || [[ "$SRR" == \#* ]]; then
        continue
    fi

    echo "Processing $SRR..."

    # Prefetch
    prefetch $SRR -p -O $OUTDIR

    # Validate
    if ! vdb-validate ${OUTDIR}/${SRR}/${SRR}.sra 2>/dev/null; then
        echo "Validation failed for $SRR, skipping..."
        continue
    fi

    # Convert
    fasterq-dump ${OUTDIR}/${SRR}/${SRR}.sra -O $OUTDIR -e $THREADS -p

    # Cleanup .sra
    rm -rf ${OUTDIR}/${SRR}

    echo "Completed $SRR"
done < "$ACCESSIONS"
```

### Python Wrapper

```python
import subprocess
import os

def download_sra(accession, outdir='.', threads=4, skip_technical=True):
    os.makedirs(outdir, exist_ok=True)

    cmd = ['fasterq-dump', accession, '-O', outdir, '-e', str(threads), '-p']
    if skip_technical:
        cmd.append('--skip-technical')

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"fasterq-dump failed: {result.stderr}")

    return result.stdout

# Download a run
download_sra('SRR12345678', outdir='./data', threads=8)
```

### Find SRA Accessions with Entrez

```python
from Bio import Entrez

Entrez.email = 'your.email@example.com'

def find_sra_runs(term, max_results=100):
    handle = Entrez.esearch(db='sra', term=term, retmax=max_results)
    search = Entrez.read(handle)
    handle.close()

    if not search['IdList']:
        return []

    handle = Entrez.efetch(db='sra', id=','.join(search['IdList']), rettype='runinfo', retmode='text')
    runinfo = handle.read()
    handle.close()

    # Parse CSV-like output
    runs = []
    for line in runinfo.strip().split('\n')[1:]:
        if line:
            fields = line.split(',')
            if len(fields) > 0:
                runs.append(fields[0])  # First field is Run accession
    return runs

# Find runs for a project
runs = find_sra_runs('PRJNA123456[bioproject]')
print(f"Found {len(runs)} runs")
```

## SRA Accession Types

| Prefix | Type | Description |
|--------|------|-------------|
| SRR | Run | Individual sequencing run |
| SRX | Experiment | Experimental design |
| SRS | Sample | Biological sample |
| SRP | Project/Study | Research project |
| PRJNA | BioProject | NCBI BioProject ID |
| SAMN | BioSample | NCBI BioSample ID |

Use Run accessions (SRR*) with fasterq-dump.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `item not found` | Invalid accession | Check accession exists |
| `disk full` | Insufficient space | Check temp and output dirs |
| `timeout` | Network issues | Use prefetch first |
| `path not found` | Bad output path | Create output directory |
| `permission denied` | Cache permission | Check vdb-config |

## Comparison: fasterq-dump vs fastq-dump

| Feature | fasterq-dump | fastq-dump |
|---------|--------------|------------|
| Speed | Fast (multithreaded) | Slow (single-threaded) |
| Memory | Higher | Lower |
| Progress | Built-in | None |
| Recommended | Yes | Legacy only |

Always prefer `fasterq-dump` unless memory constrained.

## Decision Tree

```
Need SRA sequencing data?
├── Know the SRR accession?
│   └── fasterq-dump SRR... -O ./fastq/ -p
├── Large file (>20GB)?
│   └── prefetch first, then fasterq-dump
├── Multiple runs?
│   └── Loop through accessions or use prefetch --option-file
├── Need to find accessions?
│   └── Search SRA database with Entrez
├── Download interrupted?
│   └── prefetch supports resume
└── Verify integrity?
    └── vdb-validate SRR...
```

## Related Skills

- entrez-search - Search SRA database to find accessions
- sequence-io - Read downloaded FASTQ files with Biopython
- sequence-io/paired-end-fastq - Handle paired R1/R2 files
- alignment-files - Align downloaded reads
