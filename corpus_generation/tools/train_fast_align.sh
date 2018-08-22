#!/bin/bash
# Flags
set -o errexit
set -o nounset
set -o pipefail
# Root of the tools
SCRIPT_FOLDER="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
ROOT_FOLDER="${SCRIPT_FOLDER}/../../"

# See the README for instructions on how to install this
path_fast_align="${ROOT_FOLDER}/external_tools/fast_align-master/build"

# Check if fast_align is available
if [ ! -f "${path_fast_align}/fast_align" ];then
        printf "\nMissing ${path_fast_align}/fast_align\n"
        printf "Did you install fast align ? See README.md\n\n"
        exit 1
fi

# ARGUMENT HANDLING
in_source_sentences=$1
in_target_sentences=$2
in_work_folder=$3
out_fast_align_folder=$4

# Create work folder
if [ ! -d "${in_work_folder}" ];then
    echo "mkdir -p ${in_work_folder}"
    mkdir -p ${in_work_folder}
fi

# Create work folder
if [ ! -d "${out_fast_align_folder}" ];then
    echo "mkdir -p ${out_fast_align_folder}"
    mkdir -p ${out_fast_align_folder}
fi

# Concatenate data into one single file and shuffle it
paralel_corpus=${in_work_folder}/$(basename $in_target_sentences).pairs

# Remove
python tools/remove_aligned_to_empty.py \
	${in_source_sentences} \
	${in_target_sentences} \
	${paralel_corpus}
echo ${paralel_corpus}

# TRAIN FAST ALIGN

echo "Training Source to Target model"

align_file=${out_fast_align_folder}/$(basename $in_target_sentences).s2t.align
${path_fast_align}/fast_align \
	-i ${paralel_corpus} \
	-d -o -v \
    -p ${out_fast_align_folder}/a.s2t.params \
    > ${align_file} \
    2> ${out_fast_align_folder}/a.s2t.err

echo "Training Target to Source model"

align_file=${out_fast_align_folder}/$(basename $in_target_sentences).t2s.align
${path_fast_align}/fast_align \
	-i ${paralel_corpus} \
	-d -o -v -r \
    -p ${out_fast_align_folder}/a.t2s.params \
    > ${align_file} \
    2> ${out_fast_align_folder}/a.t2s.err

echo "Trained model stored under ${out_fast_align_folder}"
