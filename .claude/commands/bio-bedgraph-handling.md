# bio-bedgraph-handling

> Create, manipulate, and convert bedGraph files for genome browser visualization. Covers bedGraph format, conversion to/from bigWig, normalization, and signal processing. Use when handling coverage and signal tracks from ChIP-seq, ATAC-seq, or RNA-seq.

**Available tools:** Read, Bash

# bedGraph Handling

bedGraph is a text format for displaying continuous-valued data on genome browsers. Common for coverage, signal intensity, and scores.

## bedGraph Format

```
track type=bedGraph name="Sample" description="Coverage"
chr1    0       100     1.5
chr1    100     200     2.3
chr1    200     300     0.8
```

Four columns: chrom, start, end, value (0-based, half-open)

## Create bedGraph from BAM

### Using bedtools genomecov

```bash
bedtools genomecov -ibam sample.bam -bg > sample.bedgraph
bedtools genomecov -ibam sample.bam -bg -split > sample.bedgraph
bedtools genomecov -ibam sample.bam -bg -scale 1.5 > sample.scaled.bedgraph
```

### Strand-Specific

```bash
bedtools genomecov -ibam sample.bam -bg -strand + > sample.plus.bedgraph
bedtools genomecov -ibam sample.bam -bg -strand - > sample.minus.bedgraph
```

### 5' End Coverage (ChIP-seq)

```bash
bedtools genomecov -ibam sample.bam -bg -5 > sample.5prime.bedgraph
```

### Normalize by Library Size (CPM)

```bash
total_reads=$(samtools view -c -F 260 sample.bam)
scale=$(echo "scale=10; 1000000 / $total_reads" | bc)

bedtools genomecov -ibam sample.bam -bg -scale $scale > sample.cpm.bedgraph
```

## Sort bedGraph

bedGraph must be sorted for conversion to bigWig.

```bash
sort -k1,1 -k2,2n sample.bedgraph > sample.sorted.bedgraph
LC_ALL=C sort -k1,1 -k2,2n sample.bedgraph > sample.sorted.bedgraph
```

## Convert bedGraph to bigWig

### Using UCSC bedGraphToBigWig

```bash
bedGraphToBigWig sample.sorted.bedgraph chrom.sizes sample.bw
fetchChromSizes hg38 > hg38.chrom.sizes
bedGraphToBigWig sample.sorted.bedgraph hg38.chrom.sizes sample.bw
```

### Generate chrom.sizes

```bash
samtools faidx reference.fa
cut -f1,2 reference.fa.fai > chrom.sizes
fetchChromSizes hg38 > hg38.chrom.sizes
mysql --user=genome --host=genome-mysql.soe.ucsc.edu -A -e \
    "select chrom, size from hg38.chromInfo" > hg38.chrom.sizes
```

### Clip to Chromosome Boundaries

```bash
bedClip sample.bedgraph chrom.sizes sample.clipped.bedgraph
bedGraphToBigWig sample.clipped.bedgraph chrom.sizes sample.bw
```

## Convert bigWig to bedGraph

```bash
bigWigToBedGraph sample.bw sample.bedgraph
bigWigToBedGraph sample.bw sample.chr1.bedgraph -chrom=chr1
bigWigToBedGraph sample.bw sample.region.bedgraph -chrom=chr1 -start=1000 -end=2000
```

## Merge bedGraph Files

### Using bedtools unionbedg

```bash
bedtools unionbedg -i sample1.bedgraph sample2.bedgraph sample3.bedgraph \
    -header -names sample1 sample2 sample3 > merged.bedgraph
```

### Average Across Samples

```bash
bedtools unionbedg -i sample1.bedgraph sample2.bedgraph sample3.bedgraph | \
    awk '{sum=0; for(i=4;i<=NF;i++) sum+=$i; print $1,$2,$3,sum/(NF-3)}' OFS='\t' \
    > average.bedgraph
```

## Mathematical Operations

### bedtools map for Region Statistics

```bash
bedtools map -a regions.bed -b sample.bedgraph -c 4 -o mean > region_means.bed
bedtools map -a regions.bed -b sample.bedgraph -c 4 -o sum > region_sums.bed
bedtools map -a regions.bed -b sample.bedgraph -c 4 -o max > region_max.bed
```

### Subtract Background

```bash
bedtools unionbedg -i treatment.bedgraph input.bedgraph | \
    awk '{diff=$4-$5; if(diff<0) diff=0; print $1,$2,$3,diff}' OFS='\t' \
    > subtracted.bedgraph
```

### Log Transform

```bash
awk '{print $1,$2,$3,log($4+1)/log(2)}' OFS='\t' sample.bedgraph > sample.log2.bedgraph
```

### Smooth Signal

```bash
bedtools slop -i sample.bedgraph -g chrom.sizes -b 50 | \
    bedtools merge -i - -c 4 -o mean > smoothed.bedgraph
```

## Python with pyBigWig

### Write bedGraph

```python
import pyBigWig

bw = pyBigWig.open('output.bedgraph', 'w')
bw.addHeader([('chr1', 248956422), ('chr2', 242193529)])

chroms = ['chr1', 'chr1', 'chr1']
starts = [0, 100, 200]
ends = [100, 200, 300]
values = [1.5, 2.3, 0.8]
bw.addEntries(chroms, starts, ends=ends, values=values)
bw.close()
```

### Read bigWig to bedGraph Format

```python
import pyBigWig

bw = pyBigWig.open('sample.bw')

for chrom, size in bw.chroms().items():
    intervals = bw.intervals(chrom)
    if intervals:
        for start, end, value in intervals:
            print(f'{chrom}\t{start}\t{end}\t{value}')

bw.close()
```

### Convert bigWig Region to bedGraph

```python
import pyBigWig

bw = pyBigWig.open('sample.bw')
intervals = bw.intervals('chr1', 1000000, 2000000)

with open('region.bedgraph', 'w') as f:
    for start, end, value in intervals:
        f.write(f'chr1\t{start}\t{end}\t{value}\n')

bw.close()
```

## deepTools for Normalization

### bamCoverage (BAM to bedGraph/bigWig)

```bash
bamCoverage -b sample.bam -o sample.bw --normalizeUsing RPKM
bamCoverage -b sample.bam -o sample.bw --normalizeUsing CPM
bamCoverage -b sample.bam -o sample.bw --normalizeUsing BPM
bamCoverage -b sample.bam -o sample.bedgraph --outFileFormat bedgraph --normalizeUsing CPM
```

### bamCompare (Treatment vs Control)

```bash
bamCompare -b1 treatment.bam -b2 input.bam -o log2ratio.bw --scaleFactorsMethod readCount
bamCompare -b1 treatment.bam -b2 input.bam -o subtracted.bw --ratio subtract
```

### bigwigCompare

```bash
bigwigCompare -b1 treatment.bw -b2 input.bw -o ratio.bw --ratio log2
bigwigCompare -b1 sample1.bw -b2 sample2.bw -o diff.bw --ratio subtract
```

## Filtering and Subsetting

### Filter by Value

```bash
awk '$4 >= 1.0' sample.bedgraph > high_signal.bedgraph
awk '$4 > 0' sample.bedgraph > nonzero.bedgraph
```

### Extract Regions

```bash
bedtools intersect -a sample.bedgraph -b regions.bed > subset.bedgraph
```

### Remove Specific Chromosomes

```bash
grep -v "^chrM" sample.bedgraph | grep -v "_random" > filtered.bedgraph
awk '$1 ~ /^chr[0-9XY]+$/' sample.bedgraph > standard_chroms.bedgraph
```

## Aggregate to Bins

### Fixed-Size Bins

```bash
bedtools makewindows -g chrom.sizes -w 1000 > bins.bed
bedtools map -a bins.bed -b sample.bedgraph -c 4 -o mean > binned.bedgraph
```

### Gene Bodies

```bash
bedtools map -a genes.bed -b sample.bedgraph -c 4 -o mean > gene_signal.bed
```

## Quality Control

### Check for Overlapping Intervals

```bash
bedtools merge -i sample.bedgraph -c 4 -o collapse | \
    awk 'index($4,",") > 0' | head
```

### Verify Sorted Order

```bash
sort -c -k1,1 -k2,2n sample.bedgraph && echo "Sorted" || echo "Not sorted"
```

### Check Value Range

```bash
awk 'NR==1 {min=$4; max=$4} {if($4<min) min=$4; if($4>max) max=$4}
     END {print "Min:", min, "Max:", max}' sample.bedgraph
```

## Complete Pipeline

```bash
#!/bin/bash
BAM=$1
NAME=$(basename $BAM .bam)
CHROM_SIZES=$2

total_reads=$(samtools view -c -F 260 $BAM)
scale=$(echo "scale=10; 1000000 / $total_reads" | bc)

bedtools genomecov -ibam $BAM -bg -scale $scale > ${NAME}.bedgraph

sort -k1,1 -k2,2n ${NAME}.bedgraph > ${NAME}.sorted.bedgraph

bedClip ${NAME}.sorted.bedgraph $CHROM_SIZES ${NAME}.clipped.bedgraph

bedGraphToBigWig ${NAME}.clipped.bedgraph $CHROM_SIZES ${NAME}.bw

rm ${NAME}.bedgraph ${NAME}.sorted.bedgraph ${NAME}.clipped.bedgraph

echo "Created ${NAME}.bw (CPM normalized)"
```

## Track Header for UCSC

```bash
echo 'track type=bedGraph name="Sample" description="CPM normalized" visibility=full color=0,0,255 altColor=255,0,0 autoScale=on graphType=bar' > track.bedgraph
cat sample.bedgraph >> track.bedgraph
```

## Related Skills

- coverage-analysis - Generate coverage from alignments
- bigwig-tracks - Work with bigWig format
- chip-seq/chipseq-visualization - Visualize signal tracks
- alignment-files/sam-bam-basics - BAM file processing
