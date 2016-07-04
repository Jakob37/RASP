from src.pipeline_modules import program_module

__author__ = 'Jakob Willforss'

CDHIT_WORD_SIZE = 8
CDHIT_THREADS = 7
CDHIT_MEMORY = 8000

# Development options
DO_DEREPLICATION = True
ACCURATE_CLUSTERING = False


class PrepareOTUsWrapper(program_module.ProgramWrapper):

    """
    Takes cleaned FASTQ-data
    Converts the data to FASTA, process it and produce OTU clusters
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        filter_threshold = option_dict['otu_filter_threshold']
        clustering_identity = option_dict['otu_cluster_identity']
        chimera_checking = option_dict['chimera_checking']

        # FASTQ to FASTA
        raw_fastq_fp = file_path_dict['prinseq']['good_output']
        raw_fasta_fp = self.output_dir + 'raw_reads_fp.fasta'
        self.add_command_entry(get_fastq_to_fasta_command(self.config_file, raw_fastq_fp, raw_fasta_fp))

        # Dereplication
        derep_fp = self.output_dir + 'derep_fp.fasta'
        derep_mapping_fp = self.output_dir + 'derep_mapping.txt'
        if DO_DEREPLICATION:
            # self.add_command_entry(get_derep_command(self.config_file, raw_fasta_fp, derep_fp))
            self.add_command_entry(get_script_dereplicator_command(self.config_file, raw_fasta_fp, derep_fp,
                                                                   derep_mapping_fp))
        else:
            self.add_command_entry(get_label_fasta_header_command(self.config_file, raw_fasta_fp, derep_fp))

        # CD-HIT
        cdhit_out = self.output_dir + 'cdhit'
        self.add_command_entry(get_run_cdhit_command(self.config_file, derep_fp, cdhit_out,
                                                     clustering_identity))

        # Create name mapping
        name_mapping = self.output_dir + 'otu_name_mapping.txt'
        self.add_command_entry(get_generate_otu_names_command(self.config_file,
                                                              cdhit_out, name_mapping))

        # Extract abundancy table
        cdhit_clusters = cdhit_out + '.clstr'
        raw_otu_fasta = cdhit_out
        raw_abund_table = cdhit_out + '.table'
        cluster_mapping_fp = self.output_dir + 'cluster_mapping.txt'
        self.add_command_entry(get_cdhit_parser_command(self.config_file, cdhit_clusters, raw_abund_table,
                                                        cluster_mapping_fp))

        # Filter OTUs based on abundancy
        otu_fasta_abund_filtered = self.output_dir + 'otus.fasta'
        otu_abund_table_abund_filtered = self.output_dir + 'otus_abundancies.fasta.filtered'
        self.add_command_entry(get_filter_otu_command(self.config_file, raw_otu_fasta,
                               raw_abund_table,
                               otu_fasta_abund_filtered,
                               otu_abund_table_abund_filtered,
                               filter_threshold))

        chimera_checked_otu_fasta = None
        if chimera_checking == 'vsearch':

            # Perform chimeric checking
            chimera_checked_otu_fasta = self.output_dir + 'non_chimeric_fp.fasta'
            self.add_command_entry(get_chimera_checking_command(self.config_file,
                                                                otu_fasta_abund_filtered,
                                                                chimera_checked_otu_fasta))
            rename_otu_input = chimera_checked_otu_fasta
        elif chimera_checking == 'none':

            rename_otu_input = otu_fasta_abund_filtered
        else:
            raise Exception('Unknown chimera checking option: {}'.format(chimera_checking))

        # Rename OTU fasta and list, filter table to match OTU fasta

        renamed_otu_abund_table = self.output_dir + 'renamed_otu.table'
        renamed_otu_fasta = self.output_dir + 'renamed_otu.fasta'
        self.add_command_entry(get_rename_otus_command(self.config_file,
                                                       rename_otu_input,
                                                       otu_abund_table_abund_filtered,
                                                       renamed_otu_fasta,
                                                       renamed_otu_abund_table,
                                                       name_mapping))

        file_path_dict[self._name]['derep_seq'] = derep_fp
        file_path_dict[self._name]['cdhit_raw_otus'] = cdhit_out
        file_path_dict[self._name]['raw_otu_table'] = raw_abund_table
        file_path_dict[self._name]['abund_filteted_otus'] = otu_fasta_abund_filtered
        file_path_dict[self._name]['chimera_checked_otus'] = chimera_checked_otu_fasta
        file_path_dict[self._name]['filtered_otu_abundancy'] = renamed_otu_abund_table
        file_path_dict[self._name]['final_otus'] = renamed_otu_fasta

        file_path_dict[self._name]['derep_mapping'] = derep_mapping_fp
        file_path_dict[self._name]['cluster_mapping'] = cluster_mapping_fp
        file_path_dict[self._name]['otu_name_mapping'] = name_mapping


def get_fastq_to_fasta_command(config, fastq_fp, fasta_fp):

    """
    Command for converting the input files from fastq to fasta format
    This format is needed in the following steps
    """

    description = 'Convert fq to fa'
    short = 'FQA'

    command = [config['scripts']['fasta_to_fastq'],
               '--input', fastq_fp,
               '--output', fasta_fp,
               '--extract_label'
               ]

    return program_module.ProgramCommand(description, short, command)


def get_derep_command(config, raw_reads_fp, dereplicated_fp):

    """
    Adds the -derep_fulllength execute_test
    Dereplicates full-length sequences
    Outputs fasta-file with dereplication counts
    """

    description = 'dereplicate reads'
    short = 'dr'

    command = [config['programs']['dereplicate'], raw_reads_fp, dereplicated_fp]

    return program_module.ProgramCommand(description, short, command)


def get_script_dereplicator_command(config, raw_reads_fp, dereplicated_fp, mapping_fp):

    """
    Home-made dereplication script
    """

    description = 'dereplicate reads'
    short = 'dr'

    # command = [config['programs']['dereplicate'], raw_reads_fp, dereplicated_fp]

    command = [config['scripts']['script_dereplicator'],
               '--input', raw_reads_fp,
               '--output', dereplicated_fp,
               '--mapping_file', mapping_fp]

    return program_module.ProgramCommand(description, short, command)


def get_label_fasta_header_command(config, raw_reads_fp, labelled_fp):

    """
    Adds labels to fasta headers
    Is used to add ';size=1;' if the derep command isn't used
    """

    description = 'label reads'
    short = 'lr'

    label = ';size=1;'

    command = [config['scripts']['label_fasta_headers'],
               '-i', raw_reads_fp,
               '-o', labelled_fp,
               '-l', label]

    return program_module.ProgramCommand(description, short, command)


def get_run_cdhit_command(config, input_reads_fp, output_otus_fp, clustering_identity):

    """
    Runs CD-HIT, clustering sequences into OTUs
    """

    description = 'CD-HIT'
    short = 'CH'

    output_description_length_option = 0

    command = [config['programs']['cdhit'],
               '-i', input_reads_fp,
               '-o', output_otus_fp,
               '-c', clustering_identity,
               '-n', CDHIT_WORD_SIZE,
               '-T', CDHIT_THREADS,
               '-M', CDHIT_MEMORY,
               '-d', output_description_length_option]

    if ACCURATE_CLUSTERING:
        command.append('-g')
        command.append(1)
        print('CD-HIT command: {}'.format(command))

    return program_module.ProgramCommand(description, short, command)


def get_generate_otu_names_command(config, raw_otus, otu_name_map):

    """Generates mapping table between old and newly generated OTU names"""

    description = 'Generate OTU names'
    short = 'GOn'

    command = [config['scripts']['generate_otu_names'],
               '--input', raw_otus,
               '--output', otu_name_map]

    return program_module.ProgramCommand(description, short, command)


def get_cdhit_parser_command(config, input_mapping_matrix_fp, output_mapping_table_fp, cluster_mapping_fp):

    """
    Extracts OTU counts from CDHIT mapping table and outputs them
    as an abundancy matrix
    """

    description = 'extract OTU table'
    short = 'eOt'

    command = [config['scripts']['cdhit_output_parser'],
               '-i', input_mapping_matrix_fp,
               '-o', output_mapping_table_fp,
               '--count_dereplicated',
               '--seq_matrix', cluster_mapping_fp]

    return program_module.ProgramCommand(description, short, command)


def get_filter_otu_command(config, complete_otu_fp, otu_abundancy_fp, output_fp, abund_filt_fp, filter_threshold):

    """
    Filters the otus based on mapped read count
    """

    description = 'abund. filtering'
    short = 'af'

    command = [config['scripts']['filter_otus'],
               '-i', complete_otu_fp,
               '-m', otu_abundancy_fp,
               '-o', output_fp,
               '-t', filter_threshold,
               '-O', abund_filt_fp]

    return program_module.ProgramCommand(description, short, command)


def get_chimera_checking_command(config, unchecked_fp, non_chimeric_fp):

    """
    Runs chimeric checking
    Identifies chimeric reads, and outputs non-chimeric reads to target file path
    """

    description = 'chim. checking'
    short = 'cc'

    command = [config['programs']['vsearch'],
               '-uchime_ref', unchecked_fp,
               '-db', config['databases']['vsearch_16S_ref'],
               '-uchimeout', str(non_chimeric_fp + '.OUTPUT'),
               '-nonchimeras', non_chimeric_fp]

    return program_module.ProgramCommand(description, short, command)


def get_rename_otus_command(config, input_otus, input_table, renamed_fasta, renamed_table, name_mapping):

    """
    Renames OTUs in fasta-file and abundancy matrix
    Outputs then as 'output.fasta' and 'output.table'
    """

    description = 'rename OTUs'
    short = 'rO'

    command = [config['scripts']['rename_otus'],
               '--fasta', input_otus,
               '--table', input_table,
               '--output_fasta', renamed_fasta,
               '--output_table', renamed_table,
               '--name_mapping', name_mapping]

    return program_module.ProgramCommand(description, short, command)

