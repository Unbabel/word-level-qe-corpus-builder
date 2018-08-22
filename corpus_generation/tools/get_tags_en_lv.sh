#!/bin/bash
#
# This generates the alignment data given source and target files 
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# ARGUMENTS
in_source_file=$1
in_mt_file=$2
in_pe_file=$3
in_fast_align_folder=$4
out_temporal_folder=$5
out_src_pe_alignments=$6
out_src_mt_alignments=$7
out_edit_alignments=$8
out_source_tags=$9
out_target_tags=${10}
fluency_rule=${11}

# Generate tercom target-side alignments 
echo "Generating Tercom alignments"
bash ./tools/tercom.sh \
    ${in_mt_file} \
    ${in_pe_file} \
    ${out_temporal_folder}/tercom/ \
    ${out_edit_alignments}

# Generate OK/BAD tags
echo "Generating OK/BAD tags"
python ./tools/generate_BAD_tags.py \
    --in-source-tokens ${in_source_file} \
    --in-mt-tokens ${in_mt_file} \
    --in-pe-tokens ${in_pe_file} \
    --in-source-pe-alignments ${out_src_pe_alignments} \
    --in-pe-mt-alignments ${out_edit_alignments} \
    --out-source-tags ${out_source_tags} \
    --out-target-tags ${out_target_tags} \
    --fluency-rule ${fluency_rule}
