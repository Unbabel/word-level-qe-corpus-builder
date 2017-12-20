#!/bin/bash
#
# This generates the alignment data for WMT2017 as an example. It requires the tools to be installed (see README.md at the root of the repo) and fast_align models for each language pair to be trained (see train_fast_align_wmt2017.sh)
#


# Flags
set -o errexit
set -o nounset
set -o pipefail

# Language pair

# Check it is run from the right folder
if [ ! -d "tools/" ];then
    echo "$0 should be run from inside ./corpus_generation folder"    
    exit        
fi

for language_pair in en-de de-en;do
    for dataset in train dev;do

        echo "$language_pair $dataset"

        # More uniformity in the names would be better
        if [ "$dataset" == "train" ];then
            folder=task2_${language_pair}_training
        else
            folder=task2_${language_pair}_${dataset}
        fi
        out_temporal_folder=../DATA/temporal_files/$folder/

        # Get tags for this set
        bash tools/get_tags.sh \
            ../DATA/$folder/${dataset}.src \
            ../DATA/$folder/${dataset}.mt \
            ../DATA/$folder/${dataset}.pe \
            ../DATA/fast_align_models/${language_pair}/ \
            $out_temporal_folder \
            $out_temporal_folder/${dataset}.src-pe.alignments \
            $out_temporal_folder/${dataset}.pe-mt.edit_alignments \
            $out_temporal_folder/${dataset}.tags \
            $out_temporal_folder/${dataset}.bad_tags 
        
    done
done
