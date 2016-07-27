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
Filter OTUs based on their taxa level

Uses table containing information and OTUs and their taxa depth
Filters away OTUs in OTU file that hasn't been determined on sufficient depth
Can also be used to filter abundancy matrix and rdp-fixrank-output
"""

FILTER_DEPTH_THRESHOLD = 3
OTU_PATTERN = re.compile(r'OTU\d+')


def main():
    args = parse_arguments()

    filehandles = open_filehandles(args)

    # Mandatory filehandles. Will never return None.
    otu_fh                      = filehandles[0]
    tax_table_fh                = filehandles[1]
    filtered_otu_fh             = filehandles[2]

    # Optional, None is returned if option isn't specified.
    abund_matrix_fh             = filehandles[3]
    filtered_abund_matrix_fh    = filehandles[4]
    fixrank_fh                  = filehandles[5]
    # filtered_fixrank_fh         = filehandles[6]

    tax_depth_dict = get_tax_depth_dict(tax_table_fh)
    tax_table_fh.close()

    # Produces filtered otu file
    remaining_labels = output_filtered_otus(otu_fh, filtered_otu_fh, tax_depth_dict, FILTER_DEPTH_THRESHOLD)

    # Produces filtered abundancy-matrix file
    if args.abund_matrix:
        output_linefiltered_file(abund_matrix_fh, filtered_abund_matrix_fh, remaining_labels)

    # Produces filtered fix-rank file
    if args.fixed_rank:
        output_linefiltered_file(fixrank_fh, tax_depth_dict, remaining_labels)

    for fh in filehandles:
        if fh is not None:
            fh.close()


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-t', '--taxa_table', required=True)

    # Optional files to parse
    parser.add_argument('-a', '--abund_matrix')
    parser.add_argument('-f', '--fixed_rank')

    parser.add_argument('-d', '--output_dir', required=True)
    parser.add_argument('-s', '--suffix', default='.taxfiltered')
    args = parser.parse_args()
    return args


def open_filehandles(args):

    """
    Opens and returns file handles

    Mandatory
    (1) OTUs                        (input)
    (2) OTU/taxa-table              (input)
    (3) Filtered OTUs               (output)

    Optional (returns None-handle if option not specified)
    (4) Abundancy matrix            (input)
    (5) Filtered abundancy matrix   (output)
    (6) Fixrank file                (input)
    (7) Filtered fixrank file       (output)
    """

    out_format_string = args.output_dir + '/{}' + args.suffix

    otu_name = args.input.split('/')[-1]
    otu_fh = open(args.input, 'r')
    tax_table_fh = open(args.taxa_table, 'r')
    filtered_otu_fh = open(out_format_string.format(otu_name), 'w')

    abund_matrix_fh = None
    filtered_abund_matrix_fh = None
    if args.abund_matrix:
        abund_matrix_name = args.abund_matrix.split('/')[-1]
        abund_matrix_fh = open(args.abund_matrix, 'r')
        filtered_abund_matrix_fh = open(out_format_string.format(abund_matrix_name), 'w')

    fixrank_fh = None
    filtered_fixrank_fh = None
    if args.fixed_rank:
        fixrank_name = args.fixed_rank.split('/')[-1]
        fixrank_fh = open(args.fixed_rank, 'r')
        filtered_fixrank_fh = open(out_format_string.format(fixrank_name), 'w')

    fhs = [otu_fh,                      # (1)
           tax_table_fh,                # (2)
           filtered_otu_fh,             # (3)
           abund_matrix_fh,             # (4)
           filtered_abund_matrix_fh,    # (5)
           fixrank_fh,                  # (6)
           filtered_fixrank_fh]         # (7)

    return fhs


def output_linefiltered_file(input_fh, output_fh, remaining_labels):

    """
    Output filtered files with lines starting with 'OTU\d+'
    """

    for line in input_fh:

        line = line.rstrip()

        re_match = re.match(OTU_PATTERN, line)
        if re_match is None:
            raise Exception('Unexpected input, each line should start with "OTU\d+"')

        otu = re_match.group(0)

        if otu in remaining_labels:
            output_fh.write('{}\n'.format(line))


def output_filtered_otus(input_otu_fh, output_otu_fh, tax_depth_dict, tax_depth_threshold):

    """
    Output those OTUs that are identified at a taxa depth of
    filter_depth or deeper
    """

    remaining_labels = []

    output_flag = False
    for line in input_otu_fh:

        line = line.rstrip()
        if line.startswith('>'):

            label = line.replace('>', '')
            output_flag = evaluate_otu(label, tax_depth_dict, tax_depth_threshold)

            if output_flag:
                remaining_labels.append(label)

        if output_flag:
            output_otu_fh.write('{}\n'.format(line))

    return remaining_labels


def evaluate_otu(label, tax_depth_dict, tax_depth_threshold):

    """
    Check OTU header in OTU file in the tax_depth_dict to evaluate
    how deep the RDP taxa identification managed to go
    Returns a bool showing of the identification went deep enough
    """

    otu_taxa_depth = tax_depth_dict.get(label)

    if otu_taxa_depth is not None:

        if otu_taxa_depth >= tax_depth_threshold:
            output_flag = True
        else:
            output_flag = False
        return output_flag
    else:
        print('WARNING - The key {} was not present in dictionary'.format(label))


def get_tax_depth_dict(tax_table_fh):

    """Retrieve dictionary with taxa depth from otu taxa table"""

    tax_depth_dict = {}
    for line in tax_table_fh:

        line_args = line.split('\t')
        otu = line_args[0]
        depth = line_args[2]

        tax_depth_dict[otu] = int(depth)

    return tax_depth_dict

if __name__ == '__main__':
    main()
