#!/usr/bin/env python3

import itertools
import argparse


def main():

    args = parse_arguments()

    clustered_dict = retrieve_dereplicate_dict(args.input)
    output_dereplicated_data(clustered_dict, args.output)
    output_cluster_file(clustered_dict, args.mapping_file)


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-m', '--mapping_file')
    return parser.parse_args()


def retrieve_dereplicate_dict(input_fp):

    """Dereplication happens here. A dict containing sequences mapped to lists with headers is returned."""

    ishead = lambda x: x.startswith('>')
    all_seqs = set()
    clustered_dict = dict()

    with open(input_fp, 'r') as in_fh:
        head = None
        for h, lines in itertools.groupby(in_fh, ishead):
            if h:
                head = next(lines).rstrip()
            else:
                seq = ''.join(lines).rstrip()
                if seq not in all_seqs:
                    all_seqs.add(seq)
                    clustered_dict[seq] = [head]
                else:
                    clustered_dict[seq].append(head)

    return clustered_dict


def output_dereplicated_data(clustered_dict, derep_fp):

    """Writes dereplicated fasta file with cluster size information"""

    with open(derep_fp, 'w') as out_fh:
        # Sort keys first by cluster size, and then alphanumerically
        ordered_keys = sorted(clustered_dict.keys(), key=lambda k: (len(clustered_dict[k]), k))
        for key in reversed(ordered_keys):
            header_list = clustered_dict[key]
            out_fh.write('{};size={};\n{}\n'.format(header_list[0], len(header_list), key))


def output_cluster_file(clustered_dict, output_fp):

    """
    Writes file containing header to cluster mapping
    Clustered sequences tab delimited on same line, with the representant as the first cluster
    """

    header_lists = clustered_dict.values()

    with open(output_fp, 'w') as out_fh:
        for header_list in header_lists:
            header_list_trunc_arrow = [header.replace('>', '') for header in header_list]
            print('{}'.format('\t'.join(header_list_trunc_arrow)), file=out_fh)


if __name__ == '__main__':
    main()