#!/usr/bin/env bash

output_dir="output_files"
test_files="Testfiles/DRR051733.fastq.gz,Testfiles/DRR051734.fastq.gz,Testfiles/DRR051735.fastq.gz"
test_labels="sample1,sample2,sample3"
rasp_out="${output_dir}/rasp.out"
rasp_err="${output_dir}/rasp.err"

echo "Preparing new folder for output files"
rm -rf ${output_dir}
mkdir ${output_dir}

rasp_command="main.py --input_files ${test_files} --input_labels ${test_labels} --output_directory ${output_dir}"

echo "Starting RASP, using the command: ${rasp_command}"
echo "Output are written to ${rasp_out} and ${rasp_err}"

python3 "../${rasp_command}"

echo "The test run is done. If the run was successful you will now find the full output dataset in ${output_dir}"
echo "If the run was unsuccessful, check the error log ${rasp_err} for further hints"
echo "If still unsuccessful, ask for help at: LINK, and attach the two log files to your query"
