#!/usr/bin/env python3
__author__ = 'Jakob Willforss'

import argparse
import re

import sys

program_description = """
Creates text files containing data for taxa bar plots
"""

WEIRD_SIGNS_PATTERN = re.compile(r'\W')
PROTEO_PATTERN = re.compile(r'proteobacteria', re.IGNORECASE)
ITOL_TAXA_DEPTH = 3


def main():

    args = parse_arguments()
    otu_taxa_table_file = args.taxa_table

    header, otu_samples_dict = parse_otu_sample_table(args.otu_sample_table)
    taxa_rank_dict = taxa_file_to_dict(otu_taxa_table_file)

    # print('OTU samples dict', file=sys.stderr)
    # print(otu_samples_dict, file=sys.stderr)
    # print('Taxa dict')
    # print(taxa_rank_dict)

    write_barplot_file(taxa_rank_dict, args.barplot_cluster, header, otu_samples_dict, cluster_count_only=True)

    # taxa_rank_dict_abundance = taxa_file_to_dict(otu_taxa_table_file)
    write_barplot_file(taxa_rank_dict, args.barplot_abund, header, otu_samples_dict)


def parse_arguments():

    """Parse the command line input arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('--taxa_table', help='otu_taxa_table', required=True)
    parser.add_argument('--otu_sample_table', help='OTU sample mapping table', required=True)
    parser.add_argument('--barplot_cluster', help='Outpath for plotting clusters in barplot', required=True)
    parser.add_argument('--barplot_abund', help='Outpath for plotting abundance in barplot')
    return parser.parse_args()


def parse_otu_sample_table(otu_sample_table_fp):

    otu_samples_dict = dict()
    with open(otu_sample_table_fp) as in_fh:
        header = in_fh.readline().rstrip('\n')
        for line in in_fh:
            line = line.rstrip('\n')

            line_entries = line.split('\t')
            otu_samples_dict[line_entries[0]] = line_entries[1:]
    return header, otu_samples_dict


def taxa_file_to_dict(otu_taxa_table_file):

    """Reads the OTU taxa table file, and parses it into a dictionary"""

    taxa_otus_dict = {}
    with open(otu_taxa_table_file, 'r') as input_fh:

        for line in input_fh:
            otu, _, _, _, _, taxa, _ = line.split('\t')

            if taxa_otus_dict.get(taxa) is None:
                taxa_otus_dict[taxa] = [otu]
            else:
                taxa_otus_dict[taxa].append(otu)

    return taxa_otus_dict


def write_barplot_file(taxa_otus_dict, out_path, header, otu_samples_dict, cluster_count_only=False):

    """Write the taxa-cluster count/cluster abundance to file"""

    with open(out_path, 'w') as out_fh:

        out_fh.write('{}\n'.format(header))

        for taxon in sorted_alphanumerically(list(taxa_otus_dict.keys())):

            taxa_samples_line = get_taxa_samples_line(taxon, taxa_otus_dict[taxon], otu_samples_dict, cluster_count_only)
            out_fh.write('{}\n'.format(taxa_samples_line))


def sorted_alphanumerically(unsorted_list):

    """
    Sorts the given iterable in the way that is expected.

    Credits to Jeff Atwood
    http://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(unsorted_list, key=alphanum_key)


def get_taxa_samples_line(taxon, otus, otu_samples_dict, get_clusters_only=False):

    tot_sample_counts = [0] * len(next(iter(otu_samples_dict.values())))  # Get number of samples

    for otu in otus:

        pos = 0
        for sample_count in otu_samples_dict[otu]:

            if sample_count == '':
                add_count = 0
            else:
                if get_clusters_only:

                    count = int(sample_count)
                    add_count = 0

                    if count > 0:
                        add_count = 1
                else:
                    add_count = int(sample_count)

            tot_sample_counts[pos] += add_count
            pos += 1

    tot_sample_counts_str = [str(sample_count) for sample_count in tot_sample_counts]
    return '{}\t{}'.format(taxon, '\t'.join(tot_sample_counts_str))


if __name__ == '__main__':
    main()