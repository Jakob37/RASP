#!/usr/bin/env python3
__author__ = 'Jakob Willforss'

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