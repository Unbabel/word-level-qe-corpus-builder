#!/bin/bash
#
# This generates the alignment data for WMT2015 as an example.
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

# Corpus config 
OUT_FOLDER="../DATA/WMT2015"

# Loop over language pairs
for language_pair in en-es;do

    echo ${language_pair}
    
    # Out Variables
    out_temporal_folder=${OUT_FOLDER}/temporal_files/fast_align_train_${language_pair}/
    out_fast_align_folder=${OUT_FOLDER}/fast_align_models/${language_pair}/
   
    # For fast align models
    [ -d "${out_temporal_folder}" ] && rm -R "${out_temporal_folder}"
    mkdir -p "${out_temporal_folder}"    
    
    # Train forward and backward models for fast align
    echo "Training fast_align ${language_pair}"
    bash ./tools/train_fast_align.sh \
        ${OUT_FOLDER}/task2_${language_pair}_training/train.source \
        ${OUT_FOLDER}/task2_${language_pair}_training/train.pe \
        ${out_temporal_folder} \
        ${out_fast_align_folder}
    
done
