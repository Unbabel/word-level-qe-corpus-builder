#!/bin/bash
# Flags
set -o errexit
set -o nounset
set -o pipefail
# Root of the tools
SCRIPT_FOLDER="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
ROOT_FOLDER="${SCRIPT_FOLDER}/../../"

# See the README for instructions on how to install this
path_tercom="${ROOT_FOLDER}/external_tools/tercom-0.7.25/tercom.7.25.jar"

# Check if fast_align is available
if [ ! -f "${path_tercom}" ];then
        printf "\nMissing ${path_tercom}\n"
        printf "Did you install tercom? See README.md\n\n"
        exit 1
fi

# ARGUMENT HANDLING
in_hypothesis_file=$1
in_reference_file=$2
in_work_folder=$3
out_tercom_alignments_file=$4

# Get basenames
reference_basename=$(basename in_reference_file)
hypothesis_basename=$(basename in_hypothesis_file)

if [ ! -d "${in_work_folder}" ];then
    mkdir -p ${in_work_folder}
fi
# Format files in tercom format (SGML NIST)
# encoding is utf-8 and quotes are scaped
echo "Formating text"
python ./tools/format_tercom.py ${in_reference_file} ${in_work_folder}/${reference_basename}
python ./tools/format_tercom.py ${in_hypothesis_file} ${in_work_folder}/${hypothesis_basename}

# Call tercom
echo "Producing tercom XML"
# From https://github.com/jhclark/tercom
#
#   -N normalization, optional, default is no.
#   -s case sensitivity, optional, default is insensitive
#   -P no punctuations, default is with punctuations.
#   -A Asian language support for -N and -P, optional, default is without.
#   -K remove brackets around HTML-style tags, optional, default is to keep
#   -r reference file path, required.
#   -h hypothesis file path, required.
#   -o output formats, optional, default are all formats.
#      Valid formats include "ter", "xml", "sum", "sum_nbest" and "pra".
#      "ter", plain text file contains four columns: chunkid, numerrs, numwrds, ter%
#      "xml", XML format with detailed alignment for each word
#      "pra", plain text with alignment details, simpler than that of tercom_v6b.
#      "pra_more", identical to pra output as tercom_v6b.
#      "sum", same summary output as that of tercom_v6b.
#      "sum_nbest", same nbest summary output as that of tercom_v6b. 
#   -n output name prefix, optional, no output will be generated if it is not set.
#   -b beam width, optional, default is 20.
#   -S translation span prefix, optional, this option only works with single reference.
#   -a alternative reference path, optional, this file will be only used to compute the reference length.
#   -d maximum shift distance, optional, default is 50 words. 
java \
    -jar ${path_tercom} \
    -r ${in_work_folder}/${reference_basename} \
    -h ${in_work_folder}/${hypothesis_basename} \
    -n ${in_work_folder}/$(basename out_tercom_file) \
    -d 0 > ${in_work_folder}/tercom.log

# Reformat
echo "Reading XML"
python ./tools/edit_alignments.py \
    ${in_work_folder}/$(basename out_tercom_file).xml \
    ${in_hypothesis_file} \
    ${in_reference_file}  \
    ${out_tercom_alignments_file}
