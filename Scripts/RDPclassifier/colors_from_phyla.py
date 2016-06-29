#!/usr/bin/python3

PROGRAM_DESCRIPTION = """
Extracts phylogenetic information for OTUs and links the OTUs
to color based on their taxa
"""
__author__ = 'Jakob Willforss'

import argparse
import re
from matplotlib import cm

NON_ALPHABETIC_PATTERN = re.compile(r'\W')


def main():

    """The starting point for the script"""

    args = parse_arguments()

    otu_taxa_dict = get_otu_taxa_dict(args.input)
    taxa_color_dict = get_taxa_color_dict(otu_taxa_dict)

    output_otu_color_taxa_table(args.otu_color_taxa, otu_taxa_dict, taxa_color_dict)

    if args.taxa_color:
        output_taxa_color_table(args.taxa_color, taxa_color_dict)


def parse_arguments():

    """Get command line arguments"""

    parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    parser.add_argument('-i', '--input',
                        help='Input table with OTU names and phyla/class taxas', required=True)
    parser.add_argument('--otu_color_taxa',
                        help='Output table with OTU names and hex colors', required=True)
    parser.add_argument('--taxa_color',
                        help='Output table with taxa and OTUs')
    args = parser.parse_args()
    return args


def remove_non_alphabetic_from_string(raw_taxa):

    """Removes non-alphabetic signs"""

    parsed_taxa = re.sub(NON_ALPHABETIC_PATTERN, '', raw_taxa)
    return parsed_taxa


def get_otu_taxa_dict(input_file) -> dict:

    """
    Retrieve OTU/taxa-dictionary from input file
    OTU is linked to Phyla, or if the Phyla is proteobactera, to Class
    """

    with open(input_file, 'r') as input_fh:
        mapping_dict = {}
        for line in input_fh:
            line = line.rstrip()
            line_entries = line.split('\t')

            name = line_entries[0]
            taxa = line_entries[5]

            mapping_dict[name] = taxa

    return mapping_dict


def get_taxa_color_dict(otu_taxa_dict) -> dict:

    """
    Retrieve a taxa/color-dictionary where all present taxas
    are linked to a unique color
    """

    present_taxa = list(otu_taxa_dict.values())
    unique_taxa = list(set(present_taxa))
    unique_taxa.sort()
    nbr_of_entries = len(unique_taxa)

    taxa_color_dict = {}
    for nbr in range(nbr_of_entries):
        hex_color_str = get_color_string(nbr_of_entries, nbr)
        taxa_color_dict[unique_taxa[nbr]] = hex_color_str
    return taxa_color_dict


def output_taxa_color_table(out_path, taxa_color_dict):

    """Writes a table with taxa-color informaiton"""

    with open(out_path, 'w') as output_fh:
        for taxa, color in taxa_color_dict.items():
            output_fh.write('{}\t{}\n'.format(taxa, color))


def output_otu_color_taxa_table(output_path, otu_taxa_dict, taxa_color_dict):

    """Writes a table with otu-color-taxa information"""

    with open(output_path, 'w') as output_fh:
        for otu in otu_taxa_dict.keys():

            raw_taxa = otu_taxa_dict[otu]
            color_str = taxa_color_dict[raw_taxa]
            parsed_taxa = remove_non_alphabetic_from_string(raw_taxa)

            output_fh.write('{}\t{}\t{}\n'.format(otu, color_str, parsed_taxa))


def get_color_string(tot_number, nbr):

    """Calculates evenly distributed colors, and returns them as hex strings"""

    # Get a evenly spaced number between 0 and 255 based on the number of samples
    color_nbr = int((255 / (tot_number + 1)) * (nbr + 1))

    decimal_color_tuple = cm.Set1(color_nbr)

    # Convert the three 0-1 indices to 0-255 indices
    int255_tuple = [int(255 * n) for n in decimal_color_tuple[0:3]]

    # Convert those to two-letter hex
    hex255_tuple = [hex(n)[2:] for n in int255_tuple]

    # Elongate the single hexes (h -> 0h) and leave the double as they are
    hex255filled_tuple = [entry if len(entry) == 2 else '0' + entry for entry in hex255_tuple]

    # Create the final hex string through concatenating the hex-pairs
    final_hex_string = '#' + ''.join(hex255filled_tuple)

    return final_hex_string

if __name__ == '__main__':
    main()
