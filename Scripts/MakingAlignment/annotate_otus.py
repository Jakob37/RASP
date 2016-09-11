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
Annotates OTU-fasta and OTU-abundancy matrix

Takes an OTU-fasta-file, and OTU-abundancy matrix and a taxa-file
Outputs corresponding fasta-file and abundancy matrix with added taxonomic information
"""


def main():

    args = parse_arguments()

    otu_taxa_dict = get_otu_taxa_dict(args.input_taxa)

    otu_annot_string_dict = None
    if args.fixed_rank_annotation:
        otu_annot_string_dict = get_fix_rank_annot_string_dict(args.fixed_rank_annotation)

    annotate_otu_fasta(args.input_fasta, args.annotated_fasta, otu_taxa_dict)
    annotate_otu_abund_matrix(args.input_abundancy, args.annotated_abundancy, otu_taxa_dict,
                              fixed_rank_annot_dict=otu_annot_string_dict)


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)

    parser.add_argument('-f', '--input_fasta', required=True)
    parser.add_argument('-a', '--input_abundancy', required=True)
    parser.add_argument('-t', '--input_taxa', required=True)

    parser.add_argument('-F', '--annotated_fasta', required=True)
    parser.add_argument('-A', '--annotated_abundancy', required=True)

    parser.add_argument('--fixed_rank_annotation',
                        help='Allows for full annotation string in annotation matrix. '
                             'The required file is traditionally named fixedRank.txt in RASP')

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


def get_fix_rank_annot_string_dict(fix_rank_annot_fp):

    """Retrieve dict linking OTU ID to RDP fix rank annotation string"""

    otu_annot_string_dict = dict()

    with open(fix_rank_annot_fp) as in_fh:
        for line in in_fh:
            line = line.rstrip()

            # fields = line.split('\t')
            fields = re.split(r'\t+', line)

            otu_id = fields[0]
            annot_string = ';'.join(fields[1:])
            otu_annot_string_dict[otu_id] = annot_string

    return otu_annot_string_dict


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


def annotate_otu_abund_matrix(raw_abund_fp, annotated_abund_fp, otu_taxa_dict, fixed_rank_annot_dict=None):

    """
    Reads a raw OTU-abundance file and outputs another file annotated
    according to the taxa found in the otu_taxa_dict
    """

    with open(raw_abund_fp, 'r') as input_fh, open(annotated_abund_fp, 'w') as output_fh:

        for line in input_fh:
            line = line.rstrip()

            otu, count = line.split('\t')
            taxa = otu_taxa_dict[otu]

            if not fixed_rank_annot_dict:
                print('{}\t{}\t{}'.format(otu, count, taxa), file=output_fh)
            else:
                fixed_rank_string = fixed_rank_annot_dict[otu]
                print('{}\t{}\t{}\t{}'.format(otu, count, taxa, fixed_rank_string), file=output_fh)


if __name__ == '__main__':
    main()
