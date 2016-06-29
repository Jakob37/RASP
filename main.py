#!/usr/bin/python3

import argparse
import os
import shutil
import configparser

from src.pipeline_modules import preprocessing
from src.util_scripts import util_functions

from src.pipeline_modules import a_prinseq
from src.pipeline_modules import b_prepare_otus_cdhit
from src.pipeline_modules import c_rdpclassifier
from src.pipeline_modules import d_pynast
from src.pipeline_modules import e_build_tree
from src.pipeline_modules import f_indices
from src.pipeline_modules import g_visualize_data

PATH_DIR = {
    'preprocessing':    '0_preprocessing/',
    'prinseq':          '1_prinseq/',
    'prepare_otus':     '2_prepare_otus/',
    'rdp_classifier':   '3_rdp_classifier/',
    'pynast':           '4_pynast/',
    'build_tree':       '5_build_tree/',
    'indices':          '6_indices/',
    'visualize_data':   '7_visualize_data/',
    'postprocessing':   'z_postprocessing/',
    'output':           'output/',
    'log':              'log/'
}

FILE_PATH_DICT = {
    'preprocessing': {},
    'input': {},
    'prinseq': {},
    'prepare_otus': {},
    'rdp_classifier': {},
    'pynast': {},
    'build_tree': {},
    'indices': {},
    'visualize_data': {},
    'output': {},
    'log': {},
}

TIME_LOG_SUBPATH = 'log/log.txt'
TIME_MATRIX_SUBPATH = 'log/log_table.txt'


def main():

    args = parse_arguments()
    config_obj = get_config_settings('settings.conf')
    print_initiation_message(args)

    tot_base_path = args.output_directory + '/'
    path_func = get_path_function(tot_base_path)

    log_dir = path_func('log')
    os.makedirs(log_dir)
    output_dir = path_func('output')
    os.makedirs(output_dir)

    FILE_PATH_DICT['input']['multiple_read_files'] = args.input_files
    FILE_PATH_DICT['input']['labels'] = args.input_labels
    print('DEBUG main labels {}'.format(args.input_labels))
    options_dict = get_option_dict(args)

    log_fp = tot_base_path + TIME_LOG_SUBPATH
    log_table_fp = tot_base_path + TIME_MATRIX_SUBPATH
    FILE_PATH_DICT['input']['log_file'] = log_fp
    FILE_PATH_DICT['input']['log_table'] = log_table_fp

    run_pipeline_module('preprocessing',    path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)

    output_program_setup(log_table_fp, FILE_PATH_DICT['preprocessing']['decompressed_input'])

    run_pipeline_module('prinseq',          path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('prepare_otus',     path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('rdp_classifier',   path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('pynast',           path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('build_tree',       path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('indices',          path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)
    run_pipeline_module('visualize_data',   path_func, FILE_PATH_DICT, log_fp, log_table_fp, options_dict, config_obj)

    output_stats = path_func('output') + 'output_stats.txt'
    util_functions.extract_run_information(FILE_PATH_DICT, output_stats)

    input_stats = path_func('output') + 'input_stats.txt'
    util_functions.extract_input_information(FILE_PATH_DICT, input_stats)

    readme_path = path_func('output') + 'README'
    util_functions.write_output_readme(readme_path)

    results_folder_path = path_func('output')
    prepare_results_folder(results_folder_path)


def parse_arguments():

    """Parses the command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_files',
                        help='Comma-delimited input files (requires gzipped FASTQ format)',
                        required=True)
    parser.add_argument('--input_labels',
                        help='Comma-delimited labels for the input files (sample1,sample2...)',
                        required=True)
    parser.add_argument('--output_directory',
                        help='The output directory',
                        required=True)

    parser.add_argument('--otu_filter_threshold',
                        help='Specifies the minimum count in OTUs to not be filtered out',
                        type=int, default=5)
    parser.add_argument('--otu_cluster_identity',
                        help='Specifies how similar sequences needs to be in order to be clustered',
                        type=float, default=0.97)
    parser.add_argument('--pynast_identity',
                        help='Specifies alignment identity used by PyNAST',
                        type=int, default=0)
    parser.add_argument('--rdp_identity',
                        help='RDP classification threshold',
                        type=float, default=0.8)
    parser.add_argument('--rdp_database',
                        help='RDP classification database (currently only 16S implemented)',
                        default='16S')
    parser.add_argument('--rdp_depth',
                        help='RDP classification depth',
                        choices=['phylum', 'class'], default='phylum')
    parser.add_argument('--tree_software',
                        help='Tree building software',
                        choices=['fasttree', 'raxml'], default='fasttree')
    parser.add_argument('--chimera_checking',
                        help='How chimera checking is performed',
                        choices=['none', 'uchime'], default='none')

    args = parser.parse_args()
    return args


def get_config_settings(config_file_name):

    """Retrieves setting object, 'settings.conf', which should reside in the same folder as this script"""

    current_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config_file_full_path = '{}/{}'.format(current_dir, config_file_name)

    if not os.path.isfile(config_file_full_path):
        raise FileNotFoundError('No file found at specified config path: {}'.format(config_file_full_path))

    config.read(config_file_full_path)

    program_str = 'programs'
    script_str = 'scripts'
    db_str = 'databases'

    for program_key in config[program_str]:
        config[program_str][program_key] = \
            '{}/{}/{}'.format(current_dir, config['basepaths'][program_str], config[program_str][program_key])

    for script_key in config[script_str]:
        config[script_str][script_key] = \
            '{}/{}/{}'.format(current_dir, config['basepaths'][script_str], config[script_str][script_key])

    for database_key in config[db_str]:
        config[db_str][database_key] = \
            '{}/{}/{}'.format(current_dir, config['basepaths'][db_str], config[db_str][database_key])

    return config


def get_option_dict(args):

    option_dict = dict()

    option_dict['otu_filter_threshold'] = args.otu_filter_threshold
    option_dict['otu_cluster_identity'] = args.otu_cluster_identity

    option_dict['rdp_identity'] = args.rdp_identity
    option_dict['rdp_database'] = args.rdp_database
    option_dict['rdp_depth'] = args.rdp_depth

    option_dict['pynast_identity'] = args.pynast_identity

    option_dict['tree_software'] = args.tree_software
    option_dict['chimera_checking'] = args.chimera_checking

    return option_dict


def run_pipeline_module(module_name, path_func, file_path_dict, log_fh, log_table_fh, option_dict, config_file):

    """Creates, initializes and returns the target module"""

    switch_dict = {
        'preprocessing':    preprocessing.PreprocessingWrapper(module_name, path_func, config_file),
        'prinseq':          a_prinseq.PrinseqWrapper(module_name, path_func, config_file),
        'prepare_otus':     b_prepare_otus_cdhit.PrepareOTUsWrapper(module_name, path_func, config_file),
        'rdp_classifier':   c_rdpclassifier.RDPClassifierWrapper(module_name, path_func, config_file),
        'pynast':           d_pynast.PynastWrapper(module_name, path_func, config_file),
        'build_tree':       e_build_tree.BuildTreeModule(module_name, path_func, config_file),
        'indices':          f_indices.IndicesWrapper(module_name, path_func, config_file),
        'visualize_data':   g_visualize_data.CreateBarplotsWrapper(module_name, path_func, config_file)
    }

    base_path = path_func(module_name)
    os.makedirs(base_path)

    option_dict = option_dict

    module = switch_dict[module_name]
    module.setup_commands(file_path_dict, option_dict)

    module.run(log_fh, log_table_fh)

    return module


def print_initiation_message(args):

    """Outputs the first displayed information about the execute_test"""

    print('##########################################################################')
    print('# PROGRAM RUN STARTED')
    print('##########################################################################')

    argument_dictionary = vars(args)

    for key in argument_dictionary.keys():
        print('Argument: {}, Value: {}'.format(key, argument_dictionary[key]))


def get_path_function(tot_base_path):

    """
    Returns a function able to generate
    particular out-folders for each module
    """

    def get_path(keyword):
        folder = PATH_DIR.get(keyword)

        if folder is None:
            raise KeyError('You entered an unvalid keyword "{}"'.format(keyword))

        return tot_base_path + folder

    return get_path


def output_program_setup(log_table_fp, decompressed_input_fp):

    """
    Writes out the initial settings for the pipeline,
    and initiates the logging
    """

    read_count = get_fastq_read_count(decompressed_input_fp)

    setup_text = ['Reads: {}'.format(int(read_count)),
                  '{}\t{}\t{}'.format('Program', 'ElapsedTime', 'Short')]

    util_functions.prepend_text_to_file(log_table_fp, setup_text)


def get_fastq_read_count(raw_reads_fastq_fh):

    """
    Calculates the read count for a fastq-file,
    and displays the information to the user
    """

    format_line_count = 4

    lines = sum(1 for _ in open(raw_reads_fastq_fh))
    print('Total sequence count: {}'.format(lines / format_line_count))
    return lines / format_line_count


def prepare_results_folder(results_folder_path):

    """
    Copies output files to output directory and create
    a compressed file which can be downloaded by the user
    """

    copy_list = list()
    copy_list.append((FILE_PATH_DICT['build_tree']['tree_file'], 'fasttree.tre'))
    copy_list.append((FILE_PATH_DICT['pynast']['annotated_otus'], 'otus.fasta'))
    copy_list.append((FILE_PATH_DICT['pynast']['annotated_abundance'], 'otu_abundancies.txt'))
    copy_list.append((FILE_PATH_DICT['visualize_data']['abundance_barplot_data'], 'abundance_barplot_data.txt'))
    copy_list.append((FILE_PATH_DICT['visualize_data']['cluster_barplot_data'], 'cluster_barplot_data.txt'))
    copy_list.append((FILE_PATH_DICT['indices']['rarefaction_curve'], 'rarefaction.png'))
    copy_list.append((FILE_PATH_DICT['indices']['chao1_curve'], 'chao1.png'))
    copy_list.append((FILE_PATH_DICT['indices']['otu_mapping_table'], 'otu_mapping_table.txt'))
    copy_list.append((FILE_PATH_DICT['visualize_data']['time_plot'], 'time_plot.pdf'))

    copy_to_result(copy_list, results_folder_path)


def copy_to_result(filepath_tuples, results_folder):

    """Copies a list of files to a target directory"""

    for tup in filepath_tuples:
        filepath = tup[0]
        filename = tup[1]
        shutil.copyfile(filepath, results_folder + filename)


if __name__ == '__main__':
    main()
