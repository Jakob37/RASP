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
import re

program_description = """
Parses CD-HIT output matrix, and prints an OTU table
Optionally also prints a read matrix, with clustered reads
grouped on the same rows
"""

REG_PATTERN = re.compile(r">(.*)\.\.\.")
SIZE_PATTERN = re.compile(r"size=(\d+)")


def main():

    # Setup
    args = parse_arguments()

    # Parse CDhit lines
    entry = CDhitEntry()
    with open(args.input) as input_fh, open(args.output, 'w') as output_fh, open(args.seq_matrix, 'w') as seq_matrix_fh:
        for line in input_fh:

            if line.startswith('>'):
                if entry.has_information():
                    entry.output_information(output_fh, seq_matrix_fh)

                entry = CDhitEntry()

            else:
                entry.add_line(line)

        # Outputs the last cluster
        entry.output_information(output_fh, seq_matrix_fh)


def parse_arguments():

    """ Parses the command line arguments """

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output')
    parser.add_argument('-t', '--threshold',
                        help='Creates a second output file (output.filtered) where OTUs with '
                             'counts lower than the threshold are filtered.', type=int)
    parser.add_argument('-d', '--count_dereplicated',
                        help='Searches read names for size-annotation ("size=xx;") and'
                             'includes that in the cluster count.', action='store_true')
    parser.add_argument('--seq_matrix',
                        help='Produce tab delimited file with clustered sequences on single lines.')
    args = parser.parse_args()
    return args


class CDhitEntry(object):

    """
    Gathers and displays information from a single OTU found
    in the CD-hit output file
    """

    def __init__(self):
        self.representative_seq = None
        self.count = 0
        self.included_seqs = []

    def add_line(self, line):

        """
        Parses a line from the cd-hit output
        Stores information about total count, representative seq,
        and the included sequence headers
        """

        if line.startswith('>'):
            raise Exception('FASTA header encountered, this class should only take body lines')

        get_dereplicate_size = True
        count = get_seq_count(get_dereplicate_size, line)
        self.count += count

        seq_header = get_seq_header_from_line(line)

        if '*' in line:
            self.representative_seq = seq_header
            self.included_seqs.insert(0, seq_header)
        else:
            self.included_seqs.append(seq_header)

    def has_information(self):
        return self.representative_seq is not None and self.count != 0

    def get_reps_information(self):

        """ Returns a string with header and count information """

        if not self.has_information():
            raise Exception("No representative sequence is assigned")

        return ">{}\t{}".format(self.representative_seq, self.count)

    def get_matrix_information(self):

        """ Returns a tab-delimited matrix file with clustered reads on one line """

        return "\t".join(self.included_seqs)

    def output_information(self, output_fh, matrix_fh=None):

        """Outputs representative cluster information, and potentially matrix information"""

        if self.representative_seq is None:
            raise Exception('No representative sequence is assigned')

        print(self.get_reps_information(), file=output_fh)  # The last cluster

        if matrix_fh is not None:
            print(self.get_matrix_information(), file=matrix_fh)



def get_seq_count(include_dereplicated_read_counts, line):

    """
    Return the count number that should represent that sequence entry.
    If not the option count_dereplicated is used, all sequences are represented
    by the number one.
    """

    if not include_dereplicated_read_counts:
        return 1
    else:
        sequence_size = get_sequence_size(line)
        return sequence_size


def get_sequence_size(line):

    """
    Retrieve the size from size annotation of line
    Size annotation should match the pattern 'size=(\d+)'
    """

    regex_match = re.search(SIZE_PATTERN, line)

    if regex_match.group(1) is None:
        raise Exception("Error! The input headers doesn't contain size information.")

    size = regex_match.group(1)
    return int(size)


def get_seq_header_from_line(line):

    """ Retrieve fasta header from matrix file """

    regex_match = re.search(REG_PATTERN, line)
    assert regex_match is not None, "The regex failed to match CD-HIT matrix!"
    fasta_header = regex_match.group(1)
    return fasta_header

if __name__ == "__main__":
    main()
