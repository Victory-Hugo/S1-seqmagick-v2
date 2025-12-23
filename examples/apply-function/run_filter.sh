#!/bin/bash


seqmagick2 convert --apply-function myfunctions.py:no_gaps \
  ../aligned.fasta empty.fasta

seqmagick2 convert --apply-function myfunctions.py:hash_starts_numeric \
  ../aligned.fasta hashed.fasta
