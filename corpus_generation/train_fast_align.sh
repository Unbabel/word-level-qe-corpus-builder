#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# Get root of the tools
SCRIPT_FOLDER="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
ROOT_FOLDER=$(realpath "$SCRIPT_FOLDER/../")

# See the README for instructions on how to install this
path_fast_align="${ROOT_FOLDER}/external_tools/fast_align-master/build"

# Check if fast_align is available
if [ ! -f "${path_fast_align}/fast_align" ];then
        printf "\nMissing ${path_fast_align}/fast_align\n"
        printf "Did you install fast align ? See README.md\n\n"
        exit 1
fi

# ARGUMENT HANDLING
source_sentences=$1
target_sentences=$2
work_folder=$3

# Determine dataset from basename
dataset=$(basename $target_sentences)

# Create work folder
if [ ! -d "${work_folder}" ];then
    echo "mkdir -p ${work_folder}"
    mkdir -p ${work_folder}
fi

# PRE-PROCESS 

# Generate source ||| target pairs
paste -d '\t' $source_sentences $target_sentences > ${work_folder}/${dataset}.src-pe
sed -i 's/\t/ ||| /g' ${work_folder}/${dataset}.src-pe

# TRAIN FAST ALIGN

# Source to Target 
${path_fast_align}/fast_align \
	-i ${work_folder}/${dataset}.src-pe \
	-d -o -v \
    -p ${work_folder}/a.s2t.params \
    > ${work_folder}/${dataset}.s2t.src-pe.align

# Target to Source 
${path_fast_align}/fast_align \
	-i ${work_folder}/${dataset}.src-pe \
	-d -o -v -r \
    -p ${work_folder}/a.t2s.params \
    > ${work_folder}/${dataset}.t2s.src-pe.align

echo "Trained model stored under ${work_folder}/"
