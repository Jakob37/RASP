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
Merges an arbitrary number of FASTA files after appending labels
to the header of respective FASTA file
"""


def main():

    args = parse_arguments()
    input_files = args.input_files.split(args.delim)

    labels = None
    if args.labels is not None:
        labels = args.labels.split(args.delim)
        assert len(input_files) == len(labels), 'Must use same number of labels as files! Labels: {}'.format(labels)

    merge_files(input_files, args.output, labels=labels)


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input_files',
                        help='Accepts multiple files divided by a space',
                        required=True)
    parser.add_argument('-l', '--labels',
                        help='Accepts labels divided by tabs, must be same length as input files string')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--delim', help='File/label separator', default=',')
    args = parser.parse_args()
    return args


def merge_files(files_fp, output_fp, labels=None):

    """Merges the target files, attaching either preset or default labels to the header lines"""

    with open(output_fp, 'w') as out_fh:
        for n in range(len(files_fp)):
            fastq_file = files_fp[n]

            if labels is None or labels[n] == '':
                label = 'sample{}'.format(n + 1)
            else:
                label = labels[n]

            with open(fastq_file) as in_fh:
                line_nbr = 1
                for line in in_fh:

                    if line_nbr % 2 == 1:
                        line = line.rstrip()
                        if len(line) > 1:  # Prevent adding labels to empty lines
                            line = line + '|{}\n'.format(label)
                        else:
                            line += '\n'

                    out_fh.write(line)
                    line_nbr += 1


if __name__ == '__main__':
    main()