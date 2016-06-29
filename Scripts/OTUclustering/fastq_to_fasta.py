#!/usr/bin/python3
__author__ = "Jakob Willforss"

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
