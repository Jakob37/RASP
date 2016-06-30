#!/usr/bin/env python3

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