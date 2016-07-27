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

import argparse
import re

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
    taxa_rank_dict_clusters = taxa_file_to_dict(otu_taxa_table_file)

    write_barplot_file(taxa_rank_dict_clusters, args.barplot_cluster, header, otu_samples_dict)

    taxa_rank_dict_abundance = taxa_file_to_dict(otu_taxa_table_file)
    write_barplot_file(taxa_rank_dict_abundance, args.barplot_abund, header, otu_samples_dict)


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


def write_barplot_file(taxa_otus_dict, out_path, header, otu_samples_dict):

    """Write the taxa-cluster count/cluster abundance to file"""

    with open(out_path, 'w') as out_fh:

        # fh.write('phylum\n')
        # fh.write('{}\t{}\t{}\n'.format('Taxa', 'OTU abundance', 'Sample'))

        for taxon in sorted(list(taxa_otus_dict.keys())):

            taxa_samples_line = get_taxa_samples_line(taxon, taxa_otus_dict[taxon], otu_samples_dict)
            out_fh.write('{}\n'.format(taxa_samples_line))

            # fh.write('{}\t{}\t{}\n'.format(taxa, taxa_otus_dict[taxa], hardcoded_sample))


def get_taxa_samples_line(taxon, otus, otu_samples_dict):

    print(taxon)
    print(otus)
    print(otu_samples_dict)

    tot_sample_counts = [0] * len(next(iter(otu_samples_dict.values())))  # Get number of samples
    for otu in otus:

        pos = 0
        for sample_count in otu_samples_dict[otu]:

            if sample_count == '':
                add_count = 0
            else:
                add_count = int(sample_count)

            tot_sample_counts[pos] += add_count
            pos += 1

        # otu_sample_counts = [int(sample_count) for sample_count in otu_samples_dict[otu]]
        # tot_sample_counts = [sum(x) for x in zip(tot_sample_counts, otu_sample_counts)]

    tot_sample_counts_str = [str(sample_count) for sample_count in tot_sample_counts]
    return '{}\t{}'.format(taxon, '\t'.join(tot_sample_counts_str))


# def taxa_file_to_dict(otu_taxa_table_file, include_abundance=False):
#
#     """Reads the OTU taxa table file, and parses it into a dictionary"""
#
#     otu_taxa_dict = {}
#     with open(otu_taxa_table_file, 'r') as input_fh:
#
#         for line in input_fh:
#             _, _, _, _, _, taxa, abundance = line.split('\t')
#
#             if include_abundance:
#                 count = int(abundance)
#             else:
#                 count = 1
#
#             if otu_taxa_dict.get(taxa) is None:
#                 otu_taxa_dict[taxa] = count
#             else:
#                 otu_taxa_dict[taxa] += count
#
#     return otu_taxa_dict


# def write_barplot_file(taxa_rank_dict, out_path, header, otu_samples_dict):
#
#     """Write the taxa-cluster count/cluster abundance to file"""
#
#     with open(out_path, 'w') as fh:
#
#         fh.write('phylum\n')
#         fh.write('{}\t{}\t{}\n'.format('Taxa', 'OTU abundance', 'Sample'))
#
#         for taxa in sorted(list(taxa_rank_dict.keys())):
#             hardcoded_sample = 'sample1'
#             fh.write('{}\t{}\t{}\n'.format(taxa, taxa_rank_dict[taxa], hardcoded_sample))


if __name__ == '__main__':
    main()