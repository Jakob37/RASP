#!/usr/bin/env python2

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

import argparse
import math
# noinspection PyUnresolvedReferences
from ete2 import Tree, TreeStyle, TextFace, AttrFace, faces, NodeStyle, CircleFace
import sys

TREE_TITLE = 'Phylogenetic tree (produced using ETE)'


def main():

    args = parse_arguments()

    tree = Tree(args.input)
    midpoint_root = tree.get_midpoint_outgroup()

    if midpoint_root is None:
        print('Warning: Was unable to assign midpoint outgroup - Likely consequence of too few OTUs')
        print('Terminating tree building')
        sys.exit()

    tree.set_outgroup(midpoint_root)

    circle_size_dict = get_scaled_abundancy_dict(args.abundancies)
    label_dict = get_label_dict(args.labels)
    color_dict = get_color_dict(args.color_taxa)
    filtered_taxa_color_dict = get_filtered_taxa_color_dict(args.color_taxa)

    rename_labels(tree, label_dict, circle_size_dict, color_dict, font_size=11)

    style = get_tree_style(scale=400, vertical_margin=0)
    style.title.add_face(TextFace(TREE_TITLE, fsize=18), column=0)
    add_legend(style, filtered_taxa_color_dict)

    # tree.render(args.output + '.png', w=500, units='mm', tree_style=style)
    tree.render(args.output + '.svg', tree_style=style)


def parse_arguments():

    """Parses the command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-l', '--labels', required=True)
    parser.add_argument('-a', '--abundancies', required=True)
    parser.add_argument('-c', '--color_taxa', required=True)
    args = parser.parse_args()
    return args


def get_label_dict(label_file_path):

    """Retrieves a dictionary with OTU - label information from a textfile"""

    label_dict = extract_dictionary_from_file(label_file_path, lambda val: val[0])
    return label_dict


def get_scaled_abundancy_dict(abundancy_file_path, circle_max_radius=30):

    """
    Retrieve a dictionary with OTU - abundancy circle size information
    Sees the raw abundancy as areas, and calculates the corresponding radius
    """

    abund_dict = extract_dictionary_from_file(abundancy_file_path, lambda val: float(val[0]))

    max_abund_area = max([value for value in abund_dict.values()])
    circle_max_area = math.pi * (circle_max_radius ** 2)
    scale_factor = circle_max_area / max_abund_area

    for key in abund_dict.keys():
        abund_dict[key] *= scale_factor

    abund_radius_dict = dict()
    for otu in abund_dict:
        abund_radius_dict[otu] = math.sqrt(abund_dict[otu] / math.pi)

    return abund_radius_dict


def get_color_dict(color_taxa_fp):

    """Retrieve a dictionary with OTU - color information"""

    color_dict = extract_dictionary_from_file(color_taxa_fp, lambda val: val[0])
    return color_dict


def get_filtered_taxa_color_dict(color_taxa_fp):

    """Retrieve a dictionary with taxa - color information"""

    taxa_color_dict = extract_dictionary_from_file(color_taxa_fp)

    filtered_taxa_color_dict = {}
    for key in taxa_color_dict.keys():

        value = taxa_color_dict[key]
        color = value[0]
        taxa = value[1]

        if taxa not in filtered_taxa_color_dict.keys():
            filtered_taxa_color_dict[taxa] = color

    return filtered_taxa_color_dict


def add_legend(style, taxa_color_dict):

    """Adds legend to the tree style"""

    style.legend_position = 1
    circle_radius = 7

    for item in taxa_color_dict.items():
        taxa = item[0] + "  "
        color = item[1]
        style.legend.add_face(TextFace(taxa, fsize=14), column=0)
        style.legend.add_face(CircleFace(radius=circle_radius, color=color), column=1)


def get_tree_style(scale=None, vertical_margin=None):

    """Setups the tree-style used when rendering the tree"""

    style = TreeStyle()
    style.show_leaf_name = False

    if scale:
        style.scale = scale

    style.show_border = True

    if vertical_margin:
        style.branch_vertical_margin = vertical_margin

    return style


def extract_dictionary_from_file(filepath, val_extraction=None):

    """
    Extracts tab-delimited information from text file and returns it as a dictionary
    The first column for each line is used as key, the rest as values
    If no value-extraction function is provided, the value contains a list with
    the remaining line entries.
    """

    dictionary = {}
    with open(filepath) as filehandle:

        for line in filehandle:
            line = line.rstrip()
            line_entries = line.split('\t')
            dictionary[line_entries[0]] = line_entries[1:]

    if val_extraction is None:
        return dictionary
    else:
        processed_val_dict = dict()
        for key in dictionary:
            processed_val_dict[key] = val_extraction(dictionary[key])

        return processed_val_dict


def rename_labels(tree, label_dict, circle_size_dict, color_dict, font_size=12):

    """Changes the OTU-naming to taxa-naming for the leaves"""

    for node in tree.traverse():

        nstyle = NodeStyle()

        if node.is_leaf():
            otu = node.name
            taxa_name = label_dict[otu]
            nstyle['size'] = circle_size_dict[otu]
            color = color_dict[otu]

            node.add_face(TextFace(taxa_name, fsize=font_size, fgcolor=color), 0)

        else:
            nstyle['size'] = 0

        node.set_style(nstyle)

if __name__ == '__main__':
    main()
