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

from src.pipeline_modules import program_module

TRIM_QUAL = 15
MIN_LEN = 60
MIN_QUAL = 20
MAX_NS = 0


class PrinseqWrapper(program_module.ProgramWrapper):

    """
    Uses the program Prinseq to clean reads
    Outputs cleaned reads
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        # input_fp = file_path_dict['input']['initial_reads']
        input_fp = file_path_dict['preprocessing']['decompressed_input']

        good_output_fp = self.output_dir + 'output_good'
        bad_output_fp = self.output_dir + 'output_bad'

        file_path_dict[self._name]['good_output'] = self.output_dir + 'output_good.fastq'

        command = get_prinseq_command(self.config_file, input_fp, good_output_fp, bad_output_fp)
        self.add_command_entry(command)


def get_prinseq_command(config_file, input_file, good_output, bad_output):

    """
    Runs the Prinseq program which performs various cleaning on the reads

    Currently performs:
        - Quality trimming for both ends
        - Evaluating that the remaining length is long enough
        - Evaluating the quality of the read
        - Evaluating that it contains a low number of Ns
    """

    description = 'Prinseq'
    short = 'pq'

    prinseq = [config_file['programs']['prinseq']]
    input_command = ['-fastq', input_file]
    output_command = ['-out_good', good_output,
                      '-out_bad', bad_output]
    # phred_command = ['-phred64']
    trim_command = ['-trim_qual_left', str(TRIM_QUAL), '-trim_qual_right', str(TRIM_QUAL)]
    minlen_command = ['-min_len', str(MIN_LEN)]
    minqual_command = ['-min_qual_mean', str(MIN_QUAL)]
    ns_command = ['-ns_max_p', str(MAX_NS)]

    process_command = prinseq + input_command + output_command\
        + trim_command + minlen_command + minqual_command + ns_command  # + derep_command

    return program_module.ProgramCommand(description, short, process_command)