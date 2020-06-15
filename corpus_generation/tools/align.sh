#!/bin/bash

# Usage: bash align.sh text.src text.mt fast_align_folder temp_folder output.src-mt

# Flags
set -o errexit
set -o nounset
set -o pipefail
# Root of the tools. If you change the script location, this wont work!
SCRIPT_FOLDER="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
ROOT_FOLDER="${SCRIPT_FOLDER}/../../"

# See the README for instructions on how to install this
path_fast_align="${ROOT_FOLDER}/external_tools/fast_align-master/build"

# Check if fast_align is available
if [ ! -f "${path_fast_align}/force_align.py" ];then
        printf "\nMissing ${path_fast_align}/force_align.py \n"
        printf "Did you install fast align ? See README.md\n\n"
        exit 1
fi

# ARGUMENT HANDLING
in_source_sentences=$1
in_target_sentences=$2
in_fast_align_folder=$3
in_work_folder=$4
out_alignments=$5

# Check if model is trained
if [ ! -f "${in_fast_align_folder}/a.s2t.params" ];then
        printf "\nMissing ${in_fast_align_folder}/a.s2t.params \n"
        printf "Did you train fast align ? See corpus_generation/README.md\n\n"
        exit 1
fi

# Create work folder
if [ ! -d "${in_work_folder}" ];then
    mkdir -p ${in_work_folder}
fi

# Concatenate data into one single file and shuffle it
paste -d '\t' \
    ${in_source_sentences} \
    ${in_target_sentences} \
    | sed 's/	/ ||| /g' \
    > ${in_work_folder}/$(basename $in_target_sentences).pairs

# ALIGN

# Align
${path_fast_align}/force_align.py \
    ${in_fast_align_folder}/a.s2t.params \
    ${in_fast_align_folder}/a.s2t.err \
    ${in_fast_align_folder}/a.t2s.params \
    ${in_fast_align_folder}/a.t2s.err \
    < ${in_work_folder}/$(basename $in_target_sentences).pairs \
    > ${out_alignments}

echo "Created ${out_alignments}"
