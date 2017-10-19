#!/bin/bash

bam_in=$1
coord=$2
bam_out=$3

/usr/local/samtools/1.3.1/bin/samtools view -hb $bam_in $coord > $bam_out
/usr/local/samtools/1.3.1/bin/samtools index $bam_out

exit 0
