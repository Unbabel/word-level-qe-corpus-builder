#!/bin/bash
#
# This generates the alignment data given source and target files 
#
# Flags
set -o errexit
set -o nounset
set -o pipefail

# ARGUMENTS
in_source_file=$1
in_mt_file=$2
in_pe_file=$3
in_fast_align_folder=$4
out_temporal_folder=$5
out_folder=$6
fluency_rule=$7
prefix=$8

out_src_pe_alignments=${out_folder}/${prefix}.src-pe
out_src_mt_alignments=${out_folder}/${prefix}.src-mt.alignments
out_edit_alignments=${out_folder}/${prefix}.pe-mt
out_source_tags=${out_folder}/source_tags
out_target_tags=${out_folder}/tags

# Cleanup temp
[ -d "${out_temporal_folder}" ] && rm -R "${out_temporal_folder}"
mkdir -p "${out_temporal_folder}"    

# Generate source-target alignments
echo "Generating src-pe alignments"
bash ./tools/align.sh \
    ${in_source_file} \
    ${in_pe_file} \
    ${in_fast_align_folder} \
    ${out_temporal_folder}/fast_align/ \
    ${out_src_pe_alignments}

# Generate source-mt alignments
echo "Generating src-mt alignments"
bash ./tools/align.sh \
    ${in_source_file} \
    ${in_mt_file} \
    ${in_fast_align_folder} \
    ${out_temporal_folder}/fast_align/ \
    ${out_src_mt_alignments}

# Generate tercom target-side alignments 
echo "Generating Tercom alignments"
bash ./tools/tercom.sh \
    ${in_mt_file} \
    ${in_pe_file} \
    ${out_temporal_folder}/tercom/ \
    ${out_edit_alignments} \
    false

# Generate OK/BAD tags
echo "Generating OK/BAD tags"
python ./tools/generate_BAD_tags.py \
    --in-source-tokens ${in_source_file} \
    --in-mt-tokens ${in_mt_file} \
    --in-pe-tokens ${in_pe_file} \
    --in-source-pe-alignments ${out_src_pe_alignments} \
    --in-pe-mt-alignments ${out_edit_alignments} \
    --out-source-tags ${out_source_tags} \
    --out-target-tags ${out_target_tags} \
    --fluency-rule ${fluency_rule}

# now compute HTER -- for this we allow shifts in tercom
echo "Generating Tercom alignments for HTER values"
bash ./tools/tercom.sh \
    ${in_mt_file} \
    ${in_pe_file} \
    ${out_temporal_folder}/tercom/ \
    ${out_edit_alignments} \
    true

tail -n +3 ${out_temporal_folder}/tercom/out_tercom_file.ter \
    | awk '{if ($4 > 1) hter=1; else hter=$4; printf "%.6f\n",hter}' > ${out_folder}/hter

if [ ! -z "$prefix" ]
then
  cp ${in_source_file} ${out_folder}/${prefix}.src
  cp ${in_mt_file} ${out_folder}/${prefix}.mt
  cp ${in_pe_file} ${out_folder}/${prefix}.pe
  mv ${out_folder}/hter ${out_folder}/${prefix}.hter
  mv ${out_folder}/tags ${out_folder}/${prefix}.tags
  mv ${out_folder}/source_tags ${out_folder}/${prefix}.source_tags
  rm ${out_folder}/source_tags.json
  rm ${out_folder}/${prefix}.pe-mt
  rm ${out_folder}/${prefix}.src-pe
fi
