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