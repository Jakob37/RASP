from src.pipeline_modules import program_module


class PreprocessingWrapper(program_module.ProgramWrapper):

    """
    Data processing PREVIOUS to running the pipeline
    Example: Decompressing compressed input
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        compressed_input_fp = file_path_dict['input']['multiple_read_files']
        labels = file_path_dict['input']['labels']

        self.add_command_entry(
            get_decompression_command(self.config_file, compressed_input_fp, self.output_dir))

        decompressed_filepaths \
            = [self.output_dir + '.'.join(fp.split('/')[-1].split('.')[:-1]) for fp in compressed_input_fp.split(' ')]

        merged_output = self.output_dir + 'merged_output.fastq'
        self.add_command_entry(get_merge_command(self.config_file, ' '.join(decompressed_filepaths),
                                                 merged_output, labels))

        file_path_dict[self._name]['decompressed_input'] = merged_output


def get_decompression_command(config_file, compressed_input_fp, decompressed_output_base):

    """Runs the decompression script, targetting .gz files only"""

    description = 'Decompression'
    short = 'dc'

    command = [config_file['scripts']['decompression_script'],
               '--input', compressed_input_fp,
               '--output_base', decompressed_output_base,
               '--decompression_mode', 'gz']

    return program_module.ProgramCommand(description, short, command)


def get_merge_command(config_file, input_fastq_files_fp, merged_output_fp, labels):

    """Runs the decompression script, targetting .gz files only"""

    description = 'Merge'
    short = 'mr'

    print('DEBUG input labels {}'.format(labels))

    command = [config_file['scripts']['merge'],
               '--input_files', input_fastq_files_fp,
               '--output', merged_output_fp,
               '--labels', labels]

    return program_module.ProgramCommand(description, short, command)