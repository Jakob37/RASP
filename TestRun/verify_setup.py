#!/usr/bin/env python3

"""
RASP: Rapid Amplicon Sequence Pipeline

Copyright (C) 2016, Jakob Willforss and Björn Canbäck
All rights reserved.

This file is part of RASP.

RASP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RASP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RASP.  If not, <http://www.gnu.org/licenses/>.
"""

import shutil
import os
import subprocess


def main():

    output_dir = 'output_files'
    test_files = 'Testfiles/DRR051733.fastq.gz,Testfiles/DRR051734.fastq.gz,Testfiles/DRR051735.fastq.gz'
    test_labels = 'sample1,sample2,sample3'
    rasp_out_log = '{}/rasp.out'.format(output_dir)
    rasp_err_log = '{}/rasp.err'.format(output_dir)

    print('Preparing output folder')
    if os.path.exists(output_dir):
        print('Found previous results, removing...')
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    print('New output directory created at: {}'.format(output_dir))

    rasp_command = '../main.py --input_files {test_files} --input_labels {test_labels} --output_directory {output_dir}'\
        .format(test_files=test_files, test_labels=test_labels, output_dir=output_dir)

    print('Will run the RASP command: {}'.format(rasp_command))
    print('Output is written to {out} and {err}'.format(out=rasp_out_log, err=rasp_err_log))

    print('Process is running! Please be patient, this can take a few minutes...')
    with open(rasp_out_log, 'w') as stdout_fh, open(rasp_err_log, 'w') as stderr_fh:

        rasp_process = subprocess.call(rasp_command.split(' '), stdout=stdout_fh, stderr=stderr_fh)
        if rasp_process == 0:
            print('Processing completed without crashes!')
        else:
            print('')
            print('RASP crashed! The following file count investigation might give hints about where')
            print('Also, check the logs found at {} and {}'.format(rasp_out_log, rasp_err_log))

    print('Validating output...')

    current_file_counts = get_current_output_counts(output_dir)
    expected_file_counts = get_expected_output_counts()
    evaluate_output_count(expected_file_counts, current_file_counts)


def get_expected_output_counts():

    """Return a dictionary containing the file counts from a previous successful run"""

    return_dict = dict()

    return_dict['1_prinseq'] = 1
    return_dict['2_prepare_otus'] = 14
    return_dict['3_rdp_classifier'] = 7
    return_dict['4_pynast'] = 9
    return_dict['5_build_tree'] = 1
    return_dict['6_indices'] = 3
    return_dict['7_visualize_data'] = 3
    return_dict['output'] = 15

    return return_dict


def get_current_output_counts(output_dir):

    """Retrieve dictionary with output counts from target directory"""

    file_counts = dict()
    for dir_content in os.listdir(output_dir):
        if os.path.isdir('{}/{}'.format(output_dir, dir_content)):
            file_counts[dir_content] = len(os.listdir(output_dir + '/' + dir_content))
    return file_counts


def evaluate_output_count(expected_count_dict, current_count_dict):

    """Output comparison of expected and received file counts"""

    print('')
    print('--- Comparing the number of output files with expected counts ---')

    fatal_errors = 0
    likely_errors = 0

    for current_dir in sorted(expected_count_dict):
        expected_count = expected_count_dict[current_dir]
        current_count = current_count_dict.get(current_dir)

        if current_count == expected_count:
            print('{:<20} Expected {} and got {}, great!'
                  .format(current_dir, expected_count, current_count))
        elif current_count == 0 or current_count is None:
            print('{:<20} Expected {} but found zero files, likely fatal error!'
                  .format(current_dir, expected_count))
            fatal_errors += 1
        elif current_count < expected_count:
            print('{:<20} Expected {} but only got {}, likely error'
                  .format(current_dir, expected_count, current_count))
            likely_errors += 1
        else:
            print('{:<20} Expected {} but got {}, unpredicted behaviour! '
                  'Are you running an outdated version of "verify_setup"?'
                  .format(current_dir, expected_count, current_count))

    print('')

    if fatal_errors > 0:
        print('You received {} fatal errors, this needs to be fixed'.format(fatal_errors))
    if likely_errors > 0:
        print('You received {} likely errors, this needs to be investigated'.format(likely_errors))

    if fatal_errors == 0 and likely_errors == 0:
        print('You received no errors. You are good to go!')


if __name__ == '__main__':
    main()
