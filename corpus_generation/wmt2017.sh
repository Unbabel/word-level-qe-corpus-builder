#!/bin/bash
#
# This generates the alignment data for WMT2017 as an example
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# For fast align models
# For the extracted features
#mkdir ../DATA/TMP/

# Train forward and backward models for fast align
echo "Training fast_align"
bash ./train_fast_align.sh \
    ../DATA/task2_en-de_training/train.src \
    ../DATA/task2_en-de_training/train.mt \
    ../DATA/temporal_files/fast_align/ \
    ../DATA/fast_align_models/en_de/

# Generate source-target alignments
echo "Generating alignments"
bash ./align.sh \
    ../DATA/task2_en-de_training/train.src \
    ../DATA/task2_en-de_training/train.mt \
    ../DATA/fast_align_models/en_de/ \
    ../DATA/temporal_files/fast_align/ \
    ../DATA/temporal_files/train.src-mt.alignments

# Generate tercom target-side alignments 
echo "Generating Tercom alignments"
bash ./tercom.sh \
    ../DATA/task2_en-de_training/train.mt \
    ../DATA/task2_en-de_training/train.pe \
    ../DATA/temporal_files/tercom/ \
    ../DATA/temporal_files/tercom/train.mt-pe.tercom

echo "../DATA/temporal_files/tercom/train.mt-pe.tercom"
