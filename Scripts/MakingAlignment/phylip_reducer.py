#!/usr/bin/python3
__author__ = "Jakob Willforss"

import argparse
import sys

program_description = """
A script for removing empty columns in phylip alignments.
"""


def main():

    # Setup
    args = parse_arguments()
    input_fh = open(args.input, "r")
    if args.output:
        output_fh = open(args.output, "w")
    else:
        output_fh = sys.stdout

    # Get the phylip content
    first_line = True
    titles = []
    alignment = []
    for line in input_fh:
        if first_line:
            header_rows, header_cols = line.split()
            first_line = False
            continue

        title, alignment_line = line.split()
        titles.append(title)
        alignment.append(alignment_line)

    # Parsing
    empty_columns = get_empty_columns(alignment)
    for col in reversed(empty_columns):
        remove_column_from_alignment(alignment, col)
    parsed_row_length = len(alignment[0])

    # Output parsed alignment
    print_parsed_alignment(header_rows, parsed_row_length, titles, alignment, output_fh)

    # De-setup
    input_fh.close()
    output_fh.close()


def parse_arguments():

    """Retrieves and returns command line arguments"""

    parser = argparse.ArgumentParser(description = program_description)
    parser.add_argument("-i", "--input", help="The input file (phylip alignment)", required=True)
    parser.add_argument("-o", "--output", help="The output file (reduced phylip alignment")
    return parser.parse_args()


def get_empty_columns(alignment) -> list:

    """Checks the alignment for empty columns, and return empty column numbers in a list"""

    empty_columns = []
    for pos in range(len(alignment[0])):
        letter_in_column = is_letter_in_column(alignment, pos)
        if not letter_in_column:
            empty_columns.append(pos)
    return empty_columns


def is_letter_in_column(alignment, col_nbr) -> bool:

    """Evaluates if a particular column is empty"""

    non_blank_encountered = False
    for line_nbr in range(len(alignment)):
        if not alignment[line_nbr][col_nbr] == "-":
            non_blank_encountered = True
            break
    return non_blank_encountered


def remove_column_from_alignment(alignment, col_nbr):

    """Removes a particular column from the alignment"""

    for line_nbr in range(len(alignment)):
        alignment[line_nbr] = alignment[line_nbr][:col_nbr] + alignment[line_nbr][(col_nbr+1):]


def print_parsed_alignment(header_rows, header_cols, labels, alignment, out_fh):

    """Creates a new phylip-file from the provided information"""

    print("{} {}".format(header_rows, header_cols), file=out_fh)
    for row_nbr in range(len(alignment)):
        out_fh.write('{} {}\n'.format(labels[row_nbr], alignment[row_nbr]))
        # print("{} {}".format(labels[row_nbr], alignment[row_nbr]), file=out_fh)

if __name__ == "__main__":
    main()
