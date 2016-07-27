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

import re
import argparse

program_description = """Takes a fastq file as input, and outputs a fasta file."""
SPLITTER_PATTERN = r'( |\|)'


def main():

    args = parse_arguments()
    with open(args.input, 'r') as input_fh, open(args.output, 'w') as output_fh:

        row = 1
        for line in input_fh:
            line = line.rstrip()
            if row % 4 == 1:            # If row is first FASTQ header line

                header = line[1:]
                if args.extract_label:
                    header = get_label_extract_name(header)
                elif args.truncate:
                    header = get_truncated_label(header)

                fasta_head = '>' + header
                print(fasta_head, file=output_fh)

            elif row % 4 == 2:
                print(line, file=output_fh)
            row += 1


def parse_arguments():

    """ Parses the command line arguments """

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--truncate', help='Truncates fasta headers at first space', action='store_true')
    parser.add_argument('--extract_label', help='Splits on spaces, but saves an optional "|ending" part', action='store_true')
    args = parser.parse_args()
    return args


def get_label_extract_name(fasta_header):

    """Extracts added label on format '|label' from end"""

    pipe_splits = fasta_header.split('|')
    assert len(pipe_splits) >= 2, 'Unable to extract label if no label is marked!'

    truncated_splits = re.split(SPLITTER_PATTERN, fasta_header)

    return '{};label={}'.format(truncated_splits[0], pipe_splits[-1])


def get_truncated_label(fasta_header):

    """Cuts of parts of name after space"""

    return re.split(SPLITTER_PATTERN, fasta_header)[0]   # fasta_header.split(SPLITTER_PATTERN)[0].split(r' ')[0]


if __name__ == '__main__':
    main()
