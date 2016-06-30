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

        readme_text = """Metagenomic Pipeline output README

### Run information ###

output_stats.txt
Information about how many sequences/OTUs that remains after various steps in the pipeline.

time_plot.pdf
A graphical overview over which parts of the pipeline that took the longest time to execute_test.
Programs that execute_test for more than 1% of the total running time is included here.

### Data ###

otus.fasta
The sequences of the final OTUs remaining after filtering them based on
the number of clustered sequeces in the OTU and based on how well the RDP
classifier managed to classify them.

otu_abundancies.txt
The abundancies for the filtered OTUs. Contains the same OTUs as the "otus.fasta"-file.

cluster_barplot_data.txt
Contains information on how many unique OTUs that are present in different Phylum
(and in the case of the Phylum Proteobacteria, in different Class).
This data is used to create the barplot "taxa_plot.png"

abundance_barplot_data.txt
Similiar to "cluster_barplot_data.txt", but includes information about each OTUs abundance.
This means this is the number of encountered sequences in each Phyla/Class.
This data is used to create the barplot "abund_taxa_plot.png"

fasttree.tre
The tree-file which is later used to create the tree visualization (seen in "ete_tree.svg").
NOTE: ETE, the tree visualization program, replaces the OTU names with taxa-names.

### Visualizations ###

taxa_plot.png
Displays the found taxas and how many unique OTUs that were found in each taxa.
Is based on the data "cluster_barplot_data.txt"

abund_taxa_plot.png
Displays the found taxas and the total number of sequences that were found in each taxa.
Is based on the data "abundance_barplot_data.txt"

ete_tree.svg
A visualization of the tree found in "fasttree.tre".
The visualization done using the Python module ETE2."""

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
