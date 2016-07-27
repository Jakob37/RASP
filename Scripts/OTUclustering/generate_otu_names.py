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

program_description = """
Create a name map for all input OTUs
"""


def main():

    args = get_parsed_arguments()
    otu_name_list = get_otu_name_list(args.input)
    output_name_map(args.output, otu_name_list)


def get_parsed_arguments():

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='FASTA file with input OTUs')
    parser.add_argument('-o', '--output', help='OTU name mapping table')
    return parser.parse_args()


def get_otu_name_list(otu_fasta_fp):

    """Retrieves list of all existing OTU names present in target file"""

    raw_otu_names = list()
    with open(otu_fasta_fp) as in_fh:
        for line in in_fh:
            line = line.rstrip()
            if line.startswith('>'):
                raw_otu_names.append(line[1:])
    return raw_otu_names


def output_name_map(otu_name_list_fp, otu_name_list):

    """Outputs table mapping OTU headers to new names"""

    otu_name_generator = generate_otu_names('OTU')

    with open(otu_name_list_fp, 'w') as out_fh:
        for otu_id in otu_name_list:
            new_name = next(otu_name_generator)
            out_fh.write('{}\t{}\n'.format(otu_id.split(';')[0], new_name))


def generate_otu_names(base_name):

    """Generator creating names 'base_name1', 'base_name2'.."""

    counter = 1
    while True:
        yield '{}{}'.format(base_name, counter)
        counter += 1

if __name__ == '__main__':
    main()