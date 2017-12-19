#!/bin/bash
#
# This generates the alignment data for WMT2017 as an example
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# Inputs
in_source_file="../DATA/task2_en-de_training/train.src"
in_mt_file="../DATA/task2_en-de_training/train.mt"
in_pe_file="../DATA/task2_en-de_training/train.pe"
in_fast_align_folder="../DATA/fast_align_models/en_de/"

# Outputs 
out_temporal_folder="../DATA/temporal_files/"
out_mt_alignments="$out_temporal_folder/train.src-pe.alignments"
out_edit_alignments="$out_temporal_folder/train.pe-mt.edit_alignments"
# Final tags
out_source_tags="$out_temporal_folder/source.tags"
out_target_tags="$out_temporal_folder/target.tags"

# For fast align models
[ -d "$out_temporal_folder" ] && rm -R "$out_temporal_folder"
mkdir "$out_temporal_folder"    

# Generate source-target alignments
echo "Generating alignments"
bash ./align.sh \
    $in_source_file \
    $in_pe_file \
    $in_fast_align_folder \
    $out_temporal_folder/fast_align/ \
    $out_mt_alignments

# Generate tercom target-side alignments 
echo "Generating Tercom alignments"
bash ./tercom.sh \
    $in_mt_file \
    $in_pe_file \
    $out_temporal_folder/tercom/ \
    $out_edit_alignments

# Generate OK/BAD tags
python ./generate_BAD_tags.py \
    --in-source-tokens $in_source_file \
    --in-mt-tokens $in_mt_file \
    --in-pe-tokens $in_pe_file \
    --in-source-pe-alignments $out_mt_alignments \
    --in-pe-mt-alignments $out_edit_alignments \
    --out-source-tags $out_source_tags \
    --out-target-tags $out_target_tags
