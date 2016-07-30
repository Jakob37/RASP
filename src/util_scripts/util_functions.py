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

import gzip


def extract_input_information(file_path_dict, output_path, delim=','):

    """
    Reads the input strings with filepaths and labels and outputs
    linecounts for each file to target path
    """

    compressed_input_fp = file_path_dict['input']['multiple_read_files']
    label_string = file_path_dict['input']['labels']

    filepaths = compressed_input_fp.split(delim)
    labels = label_string.split(delim)

    linecounts = list()

    for filepath in filepaths:
        num_lines = sum(1 for _ in gzip.open(filepath, 'rb'))
        linecounts.append(num_lines)

    with open(output_path, 'w') as output_fh:
        output_fh.write('Label:Number of sequences\n')
        for pos in range(0, len(labels)):
            output_fh.write('{}:{}\n'.format(labels[pos], int(linecounts[pos] / 4)))


def extract_run_information(file_path_dict, output_path):

    """
    Extracts information after finished pipeline-execute_test from the outfiles
    about the status of the output at that point
    Outputs it to provided file
    """

    with open(output_path, 'w') as output_fh:

        raw_reads_fp = file_path_dict['preprocessing']['decompressed_input']
        prinseq_cleaned_reads_fp = file_path_dict['prinseq']['good_output']
        derep_reads_fp = file_path_dict['prepare_otus']['derep_seq']
        raw_otus_fp = file_path_dict['prepare_otus']['cdhit_raw_otus']
        abundance_filtered_otus_fp = file_path_dict['prepare_otus']['abund_filteted_otus']
        chimera_checked_otus = file_path_dict['prepare_otus'].get('chimera_checked_otus')
        taxa_filtered_otus_fp = file_path_dict['pynast']['taxa_filtered_otus']

        # tree_fp = file_path_dict['build_tree']['tree_file']

        output_fh.write('Initial read count: {} reads\n'.format(int(_get_fastq_count_for_file(raw_reads_fp))))
        output_fh.write('After quality filtering: {} reads\n'.format(int(_get_fastq_count_for_file(prinseq_cleaned_reads_fp))))
        output_fh.write('After dereplication: {} unique sequences\n'.format(_get_fasta_count_for_file(derep_reads_fp)))
        output_fh.write('Initial number of OTUs: {} OTUs\n'.format(_get_fasta_count_for_file(raw_otus_fp)))
        output_fh.write('After abundance filtering: {} OTUs\n'.format(_get_fasta_count_for_file(abundance_filtered_otus_fp)))

        if chimera_checked_otus is not None:
            output_fh.write('After chimera checking: {} OTUs\n'.format(_get_fasta_count_for_file(chimera_checked_otus)))
        output_fh.write('After filtering uncertain taxa: {} OTUs\n'.format(_get_fasta_count_for_file(taxa_filtered_otus_fp)))

        output_fh.write('\n')


def write_output_readme(output_path):

    """Writes a description of the various output files to a README file"""

    with open(output_path, 'w') as output_fh:

        readme_text = """RASP (Rapid Amplicon Sequence Pipeline) output README

This document describes the output files received from the RASP software.

Main page and web implementation: http://mbio-serv2.mbioekol.lu.se/RASP/
Source code: https://github.com/Jakob37/RASP
Contact: jakob.willforss@hotmail.com

### Run information ###

output_stats.txt
Information about how many sequences/OTUs that remained after different processing steps.

time_plot.pdf
Visualization of processing times for internal parts of RASP.
Programs taking more than 1% of the total running time is included in the plot.

### Data ###

otus.fasta
Representative sequences for the final OTUs. The OTU headers are annotated with the most
specific taxa for which RDP Classifier achieved a threshold level of certainty.

otu_abundancies.tsv
Total abundancies for the final OTUs, i.e. the number of reads represented by the different OTUs.
The IDs matches those found in otus.fasta.

cluster_barplot_data.tsv
The number of OTUs of certain taxa found in the different samples. This data is used to create
the barplot "taxa_plot.png".

abundance_barplot_data.tsv
Similar to "cluster_barplot_data.tsv", but counts representing the total number of reads
contained in those OTUs.

fasttree.tre
The tree-file visualized in "ete_tree.svg".

### Visualizations ###

taxa_plot.png
Proportion of OTUs classified as different taxa in the different samples.
Based on the data "cluster_barplot_data.txt".

abund_taxa_plot.png
Similar to "taxa_plot.png", but taking the abundance of the OTUs into account.
Is based on the data "abundance_barplot_data.txt".

ete_tree.svg
Visualization of the tree-file "fasttree.tre".
"""

        output_fh.write(readme_text)


def _get_fastq_count_for_file(filepath):

    """
    Calculates number of entries in fastq-file
    based on line-count
    """

    with open(filepath) as handle:
        lines = sum(1 for _ in handle)
    return lines / 4


def _get_fasta_count_for_file(filepath):

    """Calculates number of fasta-headers in file"""

    header_count = 0
    with open(filepath) as handle:
        for line in handle:
            if line.startswith('>'):
                header_count += 1

    return header_count


def _get_word_occurence_count_for_file(filepath, word):

    """Counts the number of times 'word' appears in the file"""

    with open(filepath, 'r') as input_fh:
        total_word_count = 0
        for line in input_fh:
            total_word_count += line.count(word)
    return total_word_count


def prepend_text_to_file(filepath, text_list):

    """Writes lines in list to the beginning of the target file"""

    with open(filepath, 'r') as read_fh:
        file_text = read_fh.read()

    file_text = '\n'.join(text_list) + '\n' + file_text

    with open(filepath, 'w') as write_fh:
        write_fh.write(file_text)
