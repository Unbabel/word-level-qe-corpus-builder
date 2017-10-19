#!/bin/bash
# Flags
set -o errexit
set -o nounset
set -o pipefail
# Root of the tools
SCRIPT_FOLDER="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
ROOT_FOLDER=$(realpath "$SCRIPT_FOLDER/../")

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
out_tercom_file=$4

# Get basenames
reference_basename=$(basename in_reference_file)
hypothesis_basename=$(basename in_hypothesis_file)

if [ ! -d "$in_work_folder" ];then
    mkdir -p $in_work_folder
fi
# Format files in tercom format
python format_tercom.py $in_reference_file > $in_work_folder/$reference_basename
python format_tercom.py $in_hypothesis_file > $in_work_folder/$hypothesis_basename

# Call tercom
java \
    -jar $path_tercom \
    -r $in_work_folder/$reference_basename \
    -h $in_work_folder/$hypothesis_basename \
    -n $out_tercom_file \
    -d 0 > $in_work_folder/tercom.log

# Reformat
python ./edit_alignments.py $out_tercom_file.xml  
