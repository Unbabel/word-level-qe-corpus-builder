#!/bin/bash
#
# This generates the alignment data for WMT2017 as an example. It requires the
# tools to be installed (see README.md at the root of the repo) and fast_align
# models for each language pair to be trained (see train_fast_align_wmt2017.sh)
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
# ignore-shift-set     if a BAD token apears also in PE do not propagate to source
# missing-only         only propagate for missing words
fluency_rule="normal"  

# General folder
CORPUS_FOLDER="../DATA/WMT2017"

# Define alignment model
alignment_model_folder=${CORPUS_FOLDER}/fast_align_models/

# Temporal folder
TEMPORAL_FOLDER=${CORPUS_FOLDER}/temporal_files/${fluency_rule}/

# Loop over language pairs
for language_pair in en-de de-en;do
    # Loop over sets
    for dataset in train dev;do

        if [ "${dataset}" == "train" ];then
            folder=task2_${language_pair}_training
        else
            folder=task2_${language_pair}_${dataset}
        fi
        out_temporal_folder=${TEMPORAL_FOLDER}/${folder}/

        # Get tags for this set
        printf "Getting tags for \033[94m${language_pair}: ${dataset}\033[0m\n"
        bash tools/get_tags.sh \
            ${CORPUS_FOLDER}/${folder}/${dataset}.src \
            ${CORPUS_FOLDER}/${folder}/${dataset}.mt \
            ${CORPUS_FOLDER}/${folder}/${dataset}.pe \
            ${alignment_model_folder}/${language_pair}/ \
            ${out_temporal_folder} \
            ${out_temporal_folder}/${dataset}.src-pe.alignments \
            ${out_temporal_folder}/${dataset}.src-mt.alignments \
            ${out_temporal_folder}/${dataset}.pe-mt.edit_alignments \
            ${out_temporal_folder}/${dataset}.source_tags \
            ${out_temporal_folder}/${dataset}.tags \
            ${fluency_rule}

        # Copy the original files to the new corpus
        cp ${CORPUS_FOLDER}/${folder}/${dataset}.src ${out_temporal_folder}/
        cp ${CORPUS_FOLDER}/${folder}/${dataset}.mt ${out_temporal_folder}/
        cp ${CORPUS_FOLDER}/${folder}/${dataset}.pe ${out_temporal_folder}/

    done
done
