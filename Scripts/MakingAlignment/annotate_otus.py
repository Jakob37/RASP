#!/usr/bin/env python3
__author__ = "Jakob Willforss"

import argparse
import re

program_description = """
Annotates OTU-fasta and OTU-abundancy matrix

Takes an OTU-fasta-file, and OTU-abundancy matrix and a taxa-file
Outputs corresponding fasta-file and abundancy matrix with added taxonomic information
"""

# FILTER_DEPTH_THRESHOLD = 3
# OTU_PATTERN = re.compile(r'OTU\d+')


def main():

    args = parse_arguments()

    otu_taxa_dict = get_otu_taxa_dict(args.input_taxa)

    annotate_otu_fasta(args.input_fasta, args.annotated_fasta, otu_taxa_dict)
    annotate_otu_abund_matrix(args.input_abundancy, args.annotated_abundancy, otu_taxa_dict)


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)

    parser.add_argument('-f', '--input_fasta', required=True)
    parser.add_argument('-a', '--input_abundancy', required=True)
    parser.add_argument('-t', '--input_taxa', required=True)

    parser.add_argument('-F', '--annotated_fasta', required=True)
    parser.add_argument('-A', '--annotated_abundancy', required=True)

    args = parser.parse_args()
    return args


def get_otu_taxa_dict(taxa_fp):

    """Parses a OTU-taxa file and returns a dictionary with the information"""

    otu_taxa_dict = {}
    with open(taxa_fp, 'r') as fh:
        for line in fh:
            otu, _, _, taxa, _, _, _ = line.split('\t')
            otu_taxa_dict[otu] = taxa
    return otu_taxa_dict


def annotate_otu_fasta(raw_fasta_fp, annotated_fasta_fp, otu_taxa_dict):

    """
    Reads a raw OTU-fasta file and outputs another file annotated
    according to the taxa found in the otu_taxa_dict
    """

    with open(raw_fasta_fp, 'r') as input_fh, open(annotated_fasta_fp, 'w') as output_fh:

        for line in input_fh:

            line = line.rstrip()

            if line.startswith('>'):
                otu = line[1:]
                taxa = otu_taxa_dict[otu]
                print('{} {}'.format(line, taxa), file=output_fh)
            else:
                print(line, file=output_fh)


def annotate_otu_abund_matrix(raw_abund_fp, annotated_abund_fp, otu_taxa_dict):

    """
    Reads a raw OTU-abundance file and outputs another file annotated
    according to the taxa found in the otu_taxa_dict
    """

    with open(raw_abund_fp, 'r') as input_fh, open(annotated_abund_fp, 'w') as output_fh:

        for line in input_fh:

            line = line.rstrip()

            otu, count = line.split('\t')
            taxa = otu_taxa_dict[otu]
            print('{}\t{}\t{}'.format(otu, count, taxa), file=output_fh)


if __name__ == '__main__':
    main()
