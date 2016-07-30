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


class PreprocessingWrapper(program_module.ProgramWrapper):

    """
    Data processing performed before the processing steps
    """

    def setup_commands(self, file_path_dict, option_dict=None, delim=','):

        compressed_input_fp = file_path_dict['input']['multiple_read_files']
        labels = file_path_dict['input']['labels']

        self.add_command_entry(
            get_decompression_command(self.config_file, compressed_input_fp, self.output_dir))

        decompressed_filepaths \
            = [self.output_dir + '.'.join(fp.split('/')[-1].split('.')[:-1]) for fp in compressed_input_fp.split(delim)]

        merged_output = self.output_dir + 'merged_output.fastq'
        self.add_command_entry(get_merge_command(self.config_file, delim.join(decompressed_filepaths),
                                                 merged_output, labels))

        file_path_dict[self._name]['decompressed_input'] = merged_output


def get_decompression_command(config_file, compressed_input_fp, decompressed_output_base):

    """Runs the decompression script, targetting .gz files only"""

    description = 'decompress'
    short = 'dc'

    command = [config_file['scripts']['decompression_script'],
               '--input', compressed_input_fp,
               '--output_base', decompressed_output_base,
               '--decompression_mode', 'gz']

    return program_module.ProgramCommand(description, short, command)


def get_merge_command(config_file, input_fastq_files_fp, merged_output_fp, labels):

    """Runs the decompression script, targetting .gz files only"""

    description = 'merge'
    short = 'mr'

    print('DEBUG input labels {}'.format(labels))

    command = [config_file['scripts']['merge'],
               '--input_files', input_fastq_files_fp,
               '--output', merged_output_fp,
               '--labels', labels]

    return program_module.ProgramCommand(description, short, command)
