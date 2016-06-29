#!/usr/bin/python3
__author__ = "Jakob Willforss"

import argparse
import sys

program_description = """
Reads Usearch uc-mapping-textfile and calculates the mapped read
count for each OTU.
The result is printed as a unordered matrix on the form: [Name]\\t[Count]
"""


def main():

    # Setup
    args = parse_arguments()
    input_fh = open(args.input, 'r')

    output_matrix_fh = None
    if args.map_matrix:
        output_matrix_fh = open(args.map_matrix, 'w')

    mapped_seqs_dictionary = {}
    mapped_counts_dictionary = {}
    for row in input_fh:

        if row.startswith('H'):
            row = row.rstrip()
            row_cells = row.split('\t')

            read_header = row_cells[8]
            mapped_otu = row_cells[9]

            if not mapped_otu in mapped_counts_dictionary:
                mapped_counts_dictionary[mapped_otu] = 1
            else:
                mapped_counts_dictionary[mapped_otu] += 1

            if not mapped_otu in mapped_seqs_dictionary:
                mapped_seqs_dictionary[mapped_otu] = [read_header]
            else:
                mapped_seqs_dictionary[mapped_otu].append(read_header)

    if args.output:
        output_fh = open(args.output, 'w')
    else:
        output_fh = sys.stdout

    if args.threshold:
        assert args.threshold > 0, "The filtering threshold must be higher than zero!"
        thres = args.threshold
        filtered_out_fh = open(args.output + '.filtered', 'w')

    for key in mapped_counts_dictionary.keys():
        outstring = "{}\t{}".format(key, mapped_counts_dictionary[key])

        print(outstring, file=output_fh)

        if args.threshold:
            if mapped_counts_dictionary[key] >= thres:
                print(outstring, file=filtered_out_fh)

    if args.map_matrix:
        for key in mapped_seqs_dictionary.keys():
            outstring = "\t".join(mapped_seqs_dictionary[key])
            print(outstring, file=output_matrix_fh)

    input_fh.close()
    if args.output:
        output_fh.close()


def parse_arguments():

    """ Parses the provided command line arguments """

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument("-i", "--input", help="Input - Usearch mapping .uc-file", required=True)
    parser.add_argument("-o", "--output", help="Output - Unsorted read count matrix")
    parser.add_argument("-t", "--threshold",
                        help="Creates a second output file (output.filtered) where OTUs with "
                             "counts lower than the threshold are filtered.", type=int)
    parser.add_argument("-m", "--map_matrix", help="Outputs a tab delimited matrix where"
                                                   "each row contains reads mapped to one OTU")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()