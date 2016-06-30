#!/usr/bin/env python3
__author__ = 'jakob'

import sys
import argparse

program_description = """
Adds label at the end of all headers in a FASTA file
Sees the name up until first whitespace as the header name
"""


def main():

    # Get command line arguments
    args = parse_arguments()

    # Get file handles
    input_fh, output_fh = get_file_handles(args)

    # Produce output
    produce_labelled_output(input_fh, output_fh, args.label)


def get_file_handles(args):

    """
    Opens and returns provided input-file and output-file.
    If output file not provided, output handle is set to STDOUT
    """

    input_fh = open(args.input, 'r')
    if args.output:
        output_fh = open(args.output, 'w')
    else:
        output_fh = sys.stdout
    return input_fh, output_fh


def produce_labelled_output(input_fh, output_fh, label):

    """
    Iterates the input file, labels fasta headers, and
    writes sequences and labelled headers to output
    """

    for line in input_fh:
        line_arr = line.split()
        line = line_arr[0]

        if line.startswith(">"):
            line = line + label

        print(line, file=output_fh)


def parse_arguments():

    """ Parses the command line arguments """

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("-l", "--label", help="Label to be added to fasta headers", required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()