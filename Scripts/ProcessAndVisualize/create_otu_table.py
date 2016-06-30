#!/usr/bin/env python3
__author__ = 'Jakob Willforss'

import argparse
import re


def main():

    args = parse_arguments()

    derep_dict = get_derep_dict(args.derep_mapping)
    cluster_groups = get_cluster_groups(args.cluster_mapping)

    existing_samples_list = sorted_alphanumerically(retrieve_existing_samples(derep_dict))
    output_formatted_sample_list = [sample.split('=')[-1] for sample in existing_samples_list]

    for cluster_group in cluster_groups:
        cluster_group.assign_sample_counts(derep_dict)

    if args.name_mapping:
        name_map_dict = get_name_mapping_dict(args.name_mapping)
        for cluster_group in cluster_groups:
            cluster_group.assign_otu_name(name_map_dict)

    with open(args.output, 'w') as out_fh:
        print('{}\t{}'.format('OTU', '\t'.join(output_formatted_sample_list)), file=out_fh)
        for cluster_group in cluster_groups:
            print(cluster_group.output_cluster_string(existing_samples_list), file=out_fh)


def sorted_alphanumerically(unsorted_list):

    """
    Sorts the given iterable in the way that is expected.

    Credits to Jeff Atwood
    http://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(unsorted_list, key=alphanum_key)


def parse_arguments():

    """ Parses the command line arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster_mapping', required=True)
    parser.add_argument('--derep_mapping', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--name_mapping',
                        help='Allows for renaming the raw OTU name to another name provided in tab delimited table.')
    return parser.parse_args()


def retrieve_existing_samples(derep_dict):

    """Retrieves all different sample labels present"""

    existing_samples = list()
    for sample_dict in derep_dict.values():
        for key in sample_dict.keys():
            if key not in existing_samples:
                existing_samples.append(key)
    return existing_samples


def get_name_mapping_dict(name_mapping_fp):

    """Retrieve header-to-new-name mapping dict"""

    name_map_dict = dict()
    with open(name_mapping_fp) as in_fh:
        for line in in_fh:
            old_name, new_name = line.rstrip().split('\t')
            name_map_dict[old_name] = new_name
    return name_map_dict


def get_derep_dict(derep_map_fp):

    """Retrieve dict containing derep leader seq header linked to dict containing counts for the constituting samples"""

    derep_dict = dict()
    with open(derep_map_fp, 'r') as in_fp:
        for derep_line in in_fp:
            derep_line = derep_line.rstrip()
            leader_id = derep_line.split('\t')[0].split(';')[0]
            derep_dict[leader_id] = parse_derep_line(derep_line)
    return derep_dict


def parse_derep_line(derep_line):

    """Retrieves dictionary containing sample headers linked to their respective counts"""

    headers = derep_line.split('\t')
    sample_dict = dict()
    for header in headers:
        header_id, sample = header.split(';')
        if sample not in sample_dict.keys():
            sample_dict[sample] = 1
        else:
            sample_dict[sample] += 1

    return sample_dict


def get_cluster_groups(cluster_map_fp):

    """Retrieves a list containing ClusterGroup instances"""

    cluster_groups = list()
    with open(cluster_map_fp, 'r') as in_fp:
        for line in in_fp:
            line = line.rstrip()
            cluster_groups.append(ClusterGroup(line))
    return cluster_groups


class ClusterGroup:

    """
    Represents one OTU cluster, and contains information about its leader ID, as well as
    related derep-ids, ie what dereplication groups the cluster contains.
    """

    def __init__(self, cluster_line):
        self.leader_id, self.related_ids = self._parse_line(cluster_line)
        self.sample_counts = dict()

    @staticmethod
    def _parse_line(cluster_line):

        headers = cluster_line.split('\t')
        leader_id = headers[0].split(';')[0]
        related_ids = [header.split(';')[0] for header in headers]
        return leader_id, related_ids

    def assign_sample_counts(self, derep_dict):

        for header_id in self.related_ids:

            sample_dict = derep_dict[header_id]
            for sample in sample_dict:
                if sample not in self.sample_counts.keys():
                    self.sample_counts[sample] = sample_dict[sample]
                else:
                    self.sample_counts[sample] += sample_dict[sample]

    def assign_otu_name(self, otu_mapping_dict):
        self.leader_id = otu_mapping_dict[self.leader_id]

    def output_cluster_string(self, sample_list):
        output_str = '{}'.format(self.leader_id)

        for sample in sample_list:
            if sample in self.sample_counts.keys():
                output_str += '\t{}'.format(self.sample_counts[sample])
            else:
                output_str += '\t0'

        return output_str


if __name__ == '__main__':
    main()