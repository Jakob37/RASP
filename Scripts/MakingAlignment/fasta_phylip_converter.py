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

# Inspired by:
# https://github.com/Phylogenetics-Brown-BIOL1425/phylogeneticbiology/blob/master/scripts/fasta2phylip.py

import sys
from Bio import AlignIO
import argparse

program_description = """
Convert FASTA format to Phylip format
"""


def main():

    args = parse_arguments()

    fasta_align = AlignIO.read(args.input_fasta, 'fasta')
    output_text = '{} {}\n'.format(len(fasta_align), fasta_align.get_alignment_length())

    for align_rec in fasta_align:
        name = '{0:}'.format(align_rec.id)
        line = '{0}\t{1}\n'.format(name, align_rec.seq)
        output_text += line

    output_phylip(output_text, args.output_phylip)


def get_longest_id(alignment):

    """Retrieve the longest ID in alignment"""

    longest_id = 0
    num_seqs = 0

    for align_rec in alignment:
        num_seqs += 1
        if len(align_rec.id) > longest_id:
            longest_id = len(align_rec.id)

    return longest_id


def output_phylip(output_text, output_fp=None):

    """Write the final Phylip format either to file or to STDOUT"""

    if output_fp:
        with open(output_fp, 'w') as out_fh:
            print(output_text, file=out_fh, end='')
    else:
        print(output_text, file=sys.stdout, end='')


def parse_arguments():

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input_fasta', required=True)
    parser.add_argument('-o', '--output_phylip')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
