#!/bin/bash
#
# This generates the alignment data given source and target files 
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# Loop over sets
for dataset in train dev test;do

    # Cleanup temp
    [ -d "$out_temporal_folder" ] && rm -R "$out_temporal_folder"
    mkdir -p "$out_temporal_folder"    

    in_source_file_NUM_PREPRO=../DATA/WMT2018/NUM_PREPRO/task2_en-lv.nmt_${dataset}/${dataset}.src \
    in_mt_file_NUM_PREPRO=../DATA/WMT2018/NUM_PREPRO/task2_en-lv.nmt_${dataset}/${dataset}.mt \
    in_pe_file_NUM_PREPRO=../DATA/WMT2018/NUM_PREPRO/task2_en-lv.nmt_${dataset}/${dataset}.pe \
    in_fast_align_folder_NUM_PREPRO=../DATA/WMT2018/NUM_PREPRO/fast_align_models/en-lv.nmt/
 
    out_src_pe_alignments=$out_temporal_folder/${dataset}.src-pe.alignments \
    out_src_mt_alignments=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.src-mt.alignments \
    
    # Generate source-target alignments
    echo "Generating src-pe alignments"
    bash ./tools/align.sh \
        $in_source_file_NUM_PREPRO \
        $in_pe_file_NUM_PREPRO \
        $in_fast_align_folder_NUM_PREPRO \
        $out_temporal_folder/fast_align/ \
        $out_src_pe_alignments
    
    # Generate source-mt alignments
    echo "Generating src-mt alignments"
    bash ./tools/align.sh \
        $in_source_file_NUM_PREPRO \
        $in_mt_file_NUM_PREPRO \
        $in_fast_align_folder_NUM_PREPRO \
        $out_temporal_folder/fast_align/ \
        $out_src_mt_alignments

    # ARGUMENTS
    in_source_file=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.src \
    in_mt_file=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.mt \
    in_pe_file=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.pe \
    in_fast_align_folder=$alignment_model_folder/${language_pair}/ \
    out_temporal_folder=$out_temporal_folder \
    out_edit_alignments=$out_temporal_folder/${dataset}.pe-mt.edit_alignments \
    out_source_tags=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.source_tags \
    out_target_tags=../DATA/WMT2018/task2_en-lv.nmt_${dataset}/${dataset}.tags  \
    fluency_rule=$fluency_rule
 
    # Generate tercom target-side alignments 
    echo "Generating Tercom alignments"
    bash ./tools/tercom.sh \
        $in_mt_file \
        $in_pe_file \
        $out_temporal_folder/tercom/ \
        $out_edit_alignments
    
    # Generate OK/BAD tags
    echo "Generating OK/BAD tags"
    python ./tools/generate_BAD_tags.py \
        --in-source-tokens $in_source_file \
        --in-mt-tokens $in_mt_file \
        --in-pe-tokens $in_pe_file \
        --in-source-pe-alignments $out_src_pe_alignments \
        --in-pe-mt-alignments $out_edit_alignments \
        --out-source-tags $out_source_tags \
        --out-target-tags $out_target_tags \
        --fluency-rule $fluency_rule
    
done
