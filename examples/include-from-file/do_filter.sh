#!/bin/bash 
seqmagick2 convert --include-from-file selection.txt \
  ../aligned.fasta filtered.fasta
