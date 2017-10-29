#!/bin/bash
#
# This generates the alignment data for WMT2017 as an example
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# In Variables
in_source_file="../DATA/task2_en-de_training/train.src"
in_mt_file="../DATA/task2_en-de_training/train.mt"
in_pe_file="../DATA/task2_en-de_training/train.pe"

# Out Variables
out_temporal_folder="../DATA/temporal_files/"
out_fast_align_folder="../DATA/fast_align_models/en_de/"

# For fast align models
[ -d "$out_temporal_folder" ] && rm -R "$out_temporal_folder"
mkdir "$out_temporal_folder"    

# Train forward and backward models for fast align
echo "Training fast_align"
bash ./train_fast_align.sh \
    $in_source_file \
    $in_pe_file \
    $out_temporal_folder/fast_align/ \
    $out_fast_align_folder
