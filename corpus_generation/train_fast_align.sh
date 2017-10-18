#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# See the README for instructions on how to install this
path_fast_align=./external_tools/fast_align-master/build/

source_sentences=$1
target_sentences=$2
work_folder=$3

# Determine dataset from basename
dataset=$(basename $target_sentences)

# Create work folder
if [ ! -d "${work_folder}" ];then
    mkdir -p ${work_folder}
fi

# Generate source ||| target pairs
paste -d '\t' $source_sentences $target_sentences > ${work_folder}/${dataset}.src-pe
sed -i 's/\t/ ||| /g' ${work_folder}/${dataset}.src-pe

# Train fast align
# Forward
${path_fast_align}/fast_align \
	-i ${work_folder}/${dataset}.src-pe \
	-d -o -v \
    -p ./external_tools/config/a.s2t.params \
    > ${work_folder}/${dataset}.s2t.src-pe.align
# Backward
${path_fast_align}/fast_align \
	-i ${work_folder}/${dataset}.src-pe \
	-d -o -v \
    -p ./external_tools/config/a.t2s.params \
    > ${work_folder}/${dataset}.t2s.src-pe.align
