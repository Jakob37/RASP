#!/usr/bin/python3
__author__ = "Jakob Willforss"

import argparse
import re

program_description = """
A program that based on mapping counts, filters out OTUs with mapping counts
above a certain threshold and prints those to an output file.
"""

MATRIX_COUNT_PATTERN = re.compile(r'(\S+?)\t(\d+)')


def main():

    args = get_parsed_arguments()

    otu_count_dict = build_map_count_dict(args.mapping_matrix)
    output_filtered_otus(args.input, args.output, otu_count_dict, args.threshold)

    if args.output_matrix:
        output_filtered_matrix(args.mapping_matrix, args.output_matrix, args.threshold)


def get_parsed_arguments():

    default_filter_threshold = 10

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='OTU fasta file', required=True)
    parser.add_argument('-m', '--mapping_matrix', help='Matrix with OTUs and number of mapped reads', required=True)
    parser.add_argument('-o', '--output', help='Output file - filtered OTU fasta file', required=True)
    parser.add_argument('-O', '--output_matrix', help='Optional output of filtered abundancy matrix')
    parser.add_argument('-t', '--threshold', help='The filter threshold', default=default_filter_threshold, type=int)

    return parser.parse_args()


def build_map_count_dict(map_matrix):

    """
    Builds and returns a dictionary containing key-value-pairs
    for entry names and counts found in the mapping matrix
    """

    with open(map_matrix, 'r') as map_matrix_fh:

        mapping_dict = {}
        for entry in map_matrix_fh:
            name, count = entry.split('\t')
            mapping_dict[name] = int(count)

    return mapping_dict


def evaluate_otu_header(header, map_dict, threshold):

    """
    Retrieves the mapped count for the target OTU
    Returns true if count is above threshold
    """

    label = header
    otu_count = map_dict.get(label)

    if otu_count is not None:

        if otu_count >= threshold:
            output_flag = True
        else:
            output_flag = False
        return output_flag   # , label, otu_count
    else:
        print('WARNING - The key {} was not present in dictionary'.format(label))


def output_filtered_otus(input_otu, output_otu, otu_count_dict, threshold):

    """
    Uses the otu_count_dict to compare the input otus with the given threshold.
    When their count is higher than the threshold, they are written to the output file.
    """

    with open(input_otu, 'r') as input_otu_fh, open(output_otu, 'w') as output_otu_fh:

        output_flag = False
        for line in input_otu_fh:

            line = line.rstrip()
            if line.startswith('>'):
                output_flag = evaluate_otu_header(line, otu_count_dict, threshold)

            if output_flag:
                print(line, file=output_otu_fh)


def output_filtered_matrix(input_matrix, output_matrix, threshold):

    """
    Iterates through abundancy matrix and outputs entries with a count higher
    than specified threshold. The output is written to provided output handle.
    """

    with open(input_matrix, 'r') as input_matrix_fh, open(output_matrix, 'w') as output_matrix_fh:

        for line in input_matrix_fh:

            reg_match = re.search(MATRIX_COUNT_PATTERN, line)

            if reg_match is None:
                raise Exception('Matching failed, input lines should match {}'.format(MATRIX_COUNT_PATTERN))

            name = reg_match.group(1)
            count = reg_match.group(2)

            if int(count) >= threshold:
                output_matrix_fh.write('{}\t{}\n'.format(name, count))


if __name__ == '__main__':
    main()