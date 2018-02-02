#!/bin/bash
#
# This generates the alignment data given source and target files 
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# normaly this are defined in the father script
fluency_rule="normal"  
OUT_FOLDER="../DATA/WMT2018"
TEMPORAL_FOLDER=$OUT_FOLDER/temporal_files/$fluency_rule/

# Loop over sets
language_pair="en-lv.nmt"
for dataset in train dev test;do

    folder=task2_${language_pair}_${dataset}
    out_temporal_folder=$TEMPORAL_FOLDER/$folder/

    alignment_model_folder=$OUT_FOLDER/fast_align_models/
    # Cleanup temp
    [ -d "$out_temporal_folder" ] && rm -R "$out_temporal_folder"
    mkdir -p "$out_temporal_folder"    

    # Differently normalized en-lv dataset
    in_source_file_NUM_PREPRO=$OUT_FOLDER/NUM_PREPRO/task2_${language_pair}_${dataset}/${dataset}.src 
    in_mt_file_NUM_PREPRO=$OUT_FOLDER/NUM_PREPRO/task2_${language_pair}_${dataset}/${dataset}.mt 
    in_pe_file_NUM_PREPRO=$OUT_FOLDER/NUM_PREPRO/task2_${language_pair}_${dataset}/${dataset}.pe 
    in_fast_align_folder_NUM_PREPRO=$OUT_FOLDER/NUM_PREPRO/fast_align_models/${language_pair}/
    # We use the alignments for our normal set 
    out_src_pe_alignments=$out_temporal_folder/${dataset}.src-pe.alignments 
    out_src_mt_alignments=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.src-mt.alignments 
    
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
    in_source_file=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.src 
    in_mt_file=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.mt 
    in_pe_file=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.pe 
    out_temporal_folder=$out_temporal_folder 
    out_edit_alignments=$out_temporal_folder/${dataset}.pe-mt.edit_alignments 
    out_source_tags=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.source_tags 
    out_target_tags=$OUT_FOLDER/task2_${language_pair}_${dataset}/${dataset}.tags  
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
