#!/bin/bash
#
# This generates the alignment data for WMT2018. It requires the tools to be
# installed (see README.md at the root of the repo) and fast_align models for
# each language pair to be trained (see train_fast_align_wmt2018.sh)
#

# Flags
set -o errexit
set -o nounset
set -o pipefail

# Check it is run from the right folder
if [ ! -d "tools/" ];then
    echo "$0 should be run from inside ./corpus_generation folder"    
    exit        
fi

# Define rule
# normal               All BAD tokens are propagated to their aligned words
# ignore-shift-set     if a BAD token appears also in PE do not propagate to source
# missing-only         only propagate for missing words
fluency_rule="normal"  

# General folder
OUT_FOLDER="../DATA/WMT2018"

# Define alignment model
alignment_model_folder=${OUT_FOLDER}/fast_align_models/

# Temporal folder
TEMPORAL_FOLDER=${OUT_FOLDER}/temporal_files/$fluency_rule/

# Loop over language pairs
for language_pair in de-en.smt en-cs.smt en-de.nmt en-de.smt;do
    # Loop over sets
    for dataset in train dev test;do

        folder=task2_${language_pair}_${dataset}
        out_temporal_folder=$TEMPORAL_FOLDER/$folder/

        # Get tags for this set
        printf "Getting tags for \033[94m$language_pair: $dataset\033[0m\n"
        bash tools/get_tags.sh \
            ${OUT_FOLDER}/$folder/${dataset}.src \
            ${OUT_FOLDER}/$folder/${dataset}.mt \
            ${OUT_FOLDER}/$folder/${dataset}.pe \
            $alignment_model_folder/${language_pair}/ \
            $out_temporal_folder \
            $out_temporal_folder/${dataset}.src-pe.alignments \
            ${OUT_FOLDER}/$folder/${dataset}.src-mt.alignments \
            $out_temporal_folder/${dataset}.pe-mt.edit_alignments \
            ${OUT_FOLDER}/$folder/${dataset}.source_tags \
            ${OUT_FOLDER}/$folder/${dataset}.tags  \
            ${fluency_rule}
    done
done
