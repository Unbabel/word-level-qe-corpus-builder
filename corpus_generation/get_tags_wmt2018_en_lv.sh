#!/bin/bash
#
# This generates the alignment data for WMT2018 as an example. It requires the
# tools to be installed (see README.md at the root of the repo) and fast_align
# models for each language pair to be trained (see train_fast_align_wmt2018.sh)
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

#
# DO EVERYTIHG FOR THE NUM PREPROCESSED
#

# General folder
OUT_FOLDER="../DATA/WMT2018/NUM_PREPRO/"

# Define alignment model
alignment_model_folder=$OUT_FOLDER/fast_align_models/

# Temporal folder
TEMPORAL_FOLDER=$OUT_FOLDER/temporal_files/$fluency_rule/

# Loop over language pairs
for language_pair in en-lv.nmt en-lv.smt;do
    # Loop over sets
    for dataset in train dev test;do

        folder=task2_${language_pair}_${dataset}
        out_temporal_folder=$TEMPORAL_FOLDER/$folder/

        # Get tags for this set
        printf "Getting tags for \033[94m$language_pair: $dataset\033[0m\n"
        bash tools/get_tags.sh \
            $OUT_FOLDER/$folder/${dataset}.src \
            $OUT_FOLDER/$folder/${dataset}.mt \
            $OUT_FOLDER/$folder/${dataset}.pe \
            $alignment_model_folder/${language_pair}/ \
            $out_temporal_folder \
            $out_temporal_folder/${dataset}.src-pe.alignments \
            $OUT_FOLDER/$folder/${dataset}.src-mt.alignments \
            $out_temporal_folder/${dataset}.pe-mt.edit_alignments \
            $OUT_FOLDER/$folder/${dataset}.source_tags \
            $OUT_FOLDER/$folder/${dataset}.tags  \
            $fluency_rule
    done
done


#
# BORROW THE ALIGNMENTS AND USE THE NORMAL NORMALIZED
#

# General folder
OUT_FOLDER2="../DATA/WMT2018/"

# Define alignment model
alignment_model_folder2=$OUT_FOLDER2/fast_align_models/

# Temporal folder
TEMPORAL_FOLDER2=$OUT_FOLDER2/temporal_files/$fluency_rule/

# Here alignments are computed with other normalization
#for language_pair in en-lv.nmt en-lv.smt;do
for language_pair in en-lv.smt;do
    # Loop over sets
    for dataset in train dev test;do

        folder=task2_${language_pair}_${dataset}
        out_temporal_folder2=$TEMPORAL_FOLDER2/$folder/

        [ ! -d "$OUT_FOLDER2/$folder/" ] && { mkdir -p "$OUT_FOLDER2/$folder/"; }
        # Cleanup temp
        [ -d "$out_temporal_folder2" ] && rm -R "$out_temporal_folder2"
        mkdir -p "$out_temporal_folder2"    

        # Copy NUM_PREPRO alignments
        cp $TEMPORAL_FOLDER/$folder/${dataset}.src-pe.alignments $out_temporal_folder2/${dataset}.src-pe.alignments
        cp $OUT_FOLDER/$folder/${dataset}.src-mt.alignments $OUT_FOLDER2/$folder/${dataset}.src-mt.alignments

        bash tools/get_tags_en_lv.sh \
            $OUT_FOLDER2/$folder/${dataset}.src \
            $OUT_FOLDER2/$folder/${dataset}.mt \
            $OUT_FOLDER2/$folder/${dataset}.pe \
            $alignment_model_folder2/${language_pair}/ \
            $out_temporal_folder2 \
            $out_temporal_folder2/${dataset}.src-pe.alignments \
            $OUT_FOLDER2/$folder/${dataset}.src-mt.alignments \
            $out_temporal_folder2/${dataset}.pe-mt.edit_alignments \
            $OUT_FOLDER2/$folder/${dataset}.source_tags \
            $OUT_FOLDER2/$folder/${dataset}.tags  \
            $fluency_rule
    done
done
