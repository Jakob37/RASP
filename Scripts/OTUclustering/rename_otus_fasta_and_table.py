#!/usr/bin/env python3

__author__ = 'jakob'

import argparse
import re

program_description = """Renames CD-HIT OTU table and OTU list"""

TABLE_PATTERN = re.compile(r'^>(.+)\t(\w+)')
FASTA_NAME_PATTERN = re.compile(r'^>(.*)')
BASE_NAME = 'OTU'


def main():

    args = parse_arguments()

    name_dict = get_name_dict(args.name_mapping)
    output_renamed_fasta(name_dict, args.fasta, args.output_fasta)
    output_renamed_abundancy_table(name_dict, args.table, args.output_table)


def parse_arguments():

    """ Parses the command line arguments """

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-f', '--fasta', required=True)
    parser.add_argument('-t', '--table', required=True)
    parser.add_argument('-F', '--output_fasta', required=True)
    parser.add_argument('-T', '--output_table', required=True)
    parser.add_argument('--name_mapping', help='Tab delimited map with old and new OTU names', required=True)
    args = parser.parse_args()
    return args


def get_name_dict(name_map_fp):

    name_dict = dict()
    with open(name_map_fp) as in_fh:
        for entry in in_fh:
            old_name, new_name = entry.rstrip().split('\t')
            name_dict[old_name] = new_name
    return name_dict


def output_renamed_abundancy_table(naming_dict, raw_abund_table_fp, renamed_abund_table_fp):

    with open(raw_abund_table_fp) as raw_table_fh, open(renamed_abund_table_fp, 'w') as renamed_table_fh:
        for line in raw_table_fh:
            otu_header, count = line.rstrip()[1:].split('\t')
            renamed_table_fh.write('{}\t{}\n'.format(naming_dict[otu_header.split(';')[0]], count))


def output_renamed_fasta(naming_dict, raw_fasta_fp, renamed_fasta_fp):

    with open(raw_fasta_fp) as raw_fasta_fh, open(renamed_fasta_fp, 'w') as renamed_fasta_fh:
        for line in raw_fasta_fh:
            if line.startswith('>'):
                otu_header = line.rstrip()[1:]
                renamed_fasta_fh.write('>{}\n'.format(naming_dict[otu_header.split(';')[0]]))
            else:
                renamed_fasta_fh.write(line)


if __name__ == "__main__":
    main()