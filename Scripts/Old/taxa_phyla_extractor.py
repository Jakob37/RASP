#!/usr/bin/python3
__author__ = 'Jakob Willforss'

import argparse
import sys
import re

program_description = """
Takes a taxonomic file (from RDP at the moment?)
Extracts the taxa at different levels, and provides
an interface to extract information about the abundances.
"""

PHYLA_LEVEL = {'root':      1,
               'domain':    2,
               'phylum':    3,
               'class':     4,
               'order':     5,
               'family':    6,
               'genus':     7}

UNCLASSIFIED_PATTERN = re.compile(r'(u|U)nclassified')
WEIRD_SIGNS_PATTERN = re.compile(r'\W')


def main():

    # Setup
    args = parse_arguments()

    assert PHYLA_LEVEL.get(args.tax_level) is not None, 'Incorrect taxonomic level entered'

    input_fh, output_fh = get_filehandles(args)
    tax_level = args.tax_level
    custom_proteo_extraction = args.custom_extraction
    tax_level = get_taxlevel(tax_level, custom_proteo_extraction)
    entries = get_taxa_entries(input_fh)

    # if args.abundancy_table is not None:
    #     abundancy_dict = extract_abund_dict(args.abundancy_table)

    # Print the entries
    total_entries = 0
    for i in range(len(entries)):
        total_entries += entries[i].get_count()

    tax_info = extract_taxonomic_information(entries, tax_level, proteo_extend=custom_proteo_extraction)
    parsed_tax_info = get_parsed_tax_info(tax_info)
    output_tax_matrix(parsed_tax_info, args.tax_level, output_fh)

    # Abundancy entries
    # if args.abundancy_table is not None:
    #     total_entries = 0
    #     for i in range(len(entries)):

    # De-setup
    input_fh.close()
    output_fh.close()


def extract_abund_dict(abundancy_table_fp):

    """Extracts OTU abundancies from abundancy table in text file"""

    abundancy_dict = {}
    with abundancy_table_fp as fh:
        for line in fh:
            line = line.rstrip()
            name, count = line.split('\t')
            abundancy_dict[name] = count

    return abundancy_dict


def parse_arguments():

    """Parses the command line input arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='The input file', required=True)
    parser.add_argument('-o', '--output', help='The output file', required=True)
    parser.add_argument('-a', '--abundancy_table', help='Table for OTU abundancies')
    parser.add_argument('-O', '--abundancy_output', help='Taxa-abundancy counts', default='otu_abund')
    parser.add_argument('-t', '--tax_level', help='Target taxonomic level', default='phylum')
    parser.add_argument('-c', '--custom_extraction',
                        help='Custom case - phylum level with proteobacteria extended',
                        action='store_true')
    return parser.parse_args()


def get_filehandles(args):

    """Open and return input and output file handles"""

    input_fh = open(args.input, 'r')
    output_fh = open(args.output, 'w')

    return input_fh, output_fh


def get_taxlevel(tax_level, custom_proteo_extraction):

    """
    If args.special option is used, set tax-level to phylum
    Otherwise set it based on provided command line input
    """

    if custom_proteo_extraction:
        tax_level = PHYLA_LEVEL['phylum']
    else:
        tax_level = PHYLA_LEVEL[tax_level]

    return tax_level


def get_taxa_entries(input_fh):

    """
    Retrieves and returns a list with the entries
    extracted from provided input file
    """

    entries = []
    is_header = True
    for line in input_fh:
        if is_header:
            is_header = False
            continue

        entry = Entry(line)
        entries.append(entry)

    return entries


def output_tax_matrix(tax_info, tax_level, output_fh):

    """Print provided taxinfo to output filehandle"""

    print('{}'.format(tax_level), file=output_fh)
    print('{}\t{}\t{}'.format('Taxa', 'Count', 'Sample'), file=output_fh)
    for tax_pair in tax_info:

        # The Sample1 is temporary, for when we only are using one single sample
        print('{}\t{}\tSample1'.format(tax_pair[0], tax_pair[1]), file=output_fh)


def extract_taxonomic_information(entries, taxa_depth, full_depth=False, proteo_extend=False):

    """Produce and return a list with taxa - count pairs"""

    if not proteo_extend:
        if not full_depth:
            taxa_pair_list = [entry.get_taxa_pair() for entry in entries if entry.get_taxa_depth() == taxa_depth]
        else:
            taxa_pair_list =\
                [(entry.get_taxa(), entry.get_count()) for entry in entries if entry.get_taxa_depth() == taxa_depth]
    else:
        taxa_pair_list = get_phylum_proteo_data(entries)

    return taxa_pair_list


def get_phylum_proteo_data(entries):

    """
    Special case for when higher accuracy for Proteobacteria is desired
    Extracts class-information when phyla is identified as Proteobacteria
    """

    phylum_depth = PHYLA_LEVEL['phylum']

    taxa_pair_list = []
    for entry in entries:
        if entry.is_identified_as_proteobacteria():
            if entry.get_taxa_depth() == phylum_depth + 1:
                taxa_pair_list.append(entry.get_taxa_pair())
        else:
            if entry.get_taxa_depth() == phylum_depth:
                taxa_pair_list.append(entry.get_taxa_pair())

    return taxa_pair_list


def get_parsed_tax_info(tax_info_list):

    """
    Processes the tax-info list
    Removes unclassified entries and removes non alphabetical/whitespace-signs
    """

    parsed_tax_info = [entry for entry in tax_info_list if not re.search(UNCLASSIFIED_PATTERN, entry[0])]

    further_parsed_tax_info = []
    for entry in parsed_tax_info:
        entry = (re.sub(WEIRD_SIGNS_PATTERN, '', entry[0]), entry[1])
        further_parsed_tax_info.append(entry)

    return further_parsed_tax_info


class Entry(object):

    """
    Represents one line entry
    Contains taxonomic information, and the count for that particular taxa
    """

    def __init__(self, line):
        taxa_line, self.count = _extract_information(line)
        self.taxa = _parse_taxa_line(taxa_line)

    def get_taxa(self):
        return self.taxa

    def get_count(self):
        return self.count

    def get_taxa_depth(self):
        return len(self.taxa)

    def get_taxa_pair(self):
        return self.taxa[-1], self.count

    def is_identified_as_proteobacteria(self):
        if len(self.taxa) >= 3:
            return self.taxa[2] == '"Proteobacteria"'
        else:
            return False


def _extract_information(line) -> list:

    """Retrieves taxa-line and count from text file"""

    information_list = line.split('\t')

    assert len(information_list) == 5, 'Number of tab-delimited elements in line not five as expected'

    taxa_line = information_list[1]
    count = int(information_list[4])

    return taxa_line, count


def _parse_taxa_line(taxa_line):

    """
    Retrieves values in taxa-line retrieved from text file
    Returns it a a list
    """

    taxa = []
    elements = taxa_line.split(';')

    if len(elements) == 1:
        taxa.append('Root')
    else:
        for pos in range(0, len(elements) - 1, 2):
            taxa.append(elements[pos])
    return taxa

if __name__ == '__main__':
    main()
