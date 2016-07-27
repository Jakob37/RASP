#!/usr/bin/env python3

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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm

import argparse

program_description = """
Creates a stacked make_plot from a taxa-matrix
"""

COLOR_SCALE = cm.spectral
CLUSTER_TITLE = 'OTU counts (Phylum/Class)'
ABUNDANCY_TITLE = 'OTU abundancies (Phylum/Class)'

def main():

    args = parse_arguments()

    header, taxa_count_dict = extract_tax_count_dict(args.input)
    header_entries = header.rstrip().split('\t')

    normalized_taxa_count_dict = normalize_tax_count_dict(taxa_count_dict)

    taxa_color_dict = None
    if args.color_table:
        taxa_color_dict = extract_color_dict(args.color_table)

    if args.relative_abundance:
        fig, leg = make_plot(normalized_taxa_count_dict, args.title, header_entries, args.ylabel, taxa_color_dict)
    else:
        fig, leg = make_plot(taxa_count_dict, args.title, header_entries, args.ylabel, taxa_color_dict)

    fig.savefig(args.output + '.png', format='png', bbox_extra_artists=(leg,), bbox_inches='tight')


def parse_arguments():

    """Parses the command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='Input file', required=True)
    parser.add_argument('-o', '--output', help='Output file', required=True)
    parser.add_argument('--title', help='Title of the plot', default='Default title')
    parser.add_argument('--ylabel', help='Y-axis for the plot', default='Default ylabel')
    parser.add_argument('-c', '--color_table', help='Optional table to specify taxa colors')
    parser.add_argument('--relative_abundance', action='store_true')
    args = parser.parse_args()
    return args


def extract_color_dict(taxa_color_table):

    """Extracts colors related from taxa from table, and returns the information as a dictionary"""

    taxa_color_dict = {}
    with open(taxa_color_table, 'r') as taxa_color_fh:
        for entry in taxa_color_fh:
            entry = entry.rstrip()
            taxa, color = entry.split('\t')
            taxa_color_dict[taxa] = color

    return taxa_color_dict


def extract_tax_count_dict(input_fp):

    """Retrieves information from matrix with taxonomical information"""

    taxa_counts_dict = dict()

    with open(input_fp) as input_fh:
        header = input_fh.readline()
        for line in input_fh:

            line_entries = line.rstrip('\n').split('\t')
            taxon = line_entries[0]
            taxa_counts_dict[taxon] = [int(entry) for entry in line_entries[1:]]

    return header, taxa_counts_dict


def normalize_tax_count_dict(taxa_count_dict):

    """Calculates sample fractions summing to one, instead of read count"""

    total_counts = [0] * len(next(iter(taxa_count_dict.values())))
    for sample_counts in taxa_count_dict.values():
        total_counts = [sum(counts) for counts in zip(total_counts, sample_counts)]

    normalized_dict = dict()
    for taxon in taxa_count_dict.keys():

        normalized_dict[taxon] = list()
        for n in range(len(total_counts)):
            if total_counts[n] == 0:
                taxa_frac = 0
            else:
                taxa_frac = taxa_count_dict[taxon][n] / total_counts[n]
            normalized_dict[taxon].append(taxa_frac)

    return normalized_dict


def make_plot(taxa_count_dict, title, headers, ylabel, taxa_color_dict=None):

    """Takes taxonomical data and titles, returns a figure and legend"""

    xlocations = [(pos + 1) / len(headers) for pos in range(len(headers) - 1)]
    width = 1 / (len(headers) - 1) * 0.4

    fig = plt.figure()
    plots = list()

    if taxa_color_dict is None:
        color_list = get_color_list(len(taxa_count_dict.keys()))

    x_labels = headers[1:]
    legend_labels = list()

    for plot_nr in range(len(x_labels)):

        tot_height = 0
        for taxon_nr, taxon in enumerate(sorted(taxa_count_dict.keys())):

            count = float(taxa_count_dict[taxon][plot_nr])
            plot = plt.bar(xlocations[plot_nr], height=count, width=width, color='g', bottom=tot_height, align='center')
            tot_height += count

            if taxa_color_dict is not None:
                color = taxa_color_dict[taxon]
            else:
                color = color_list[taxon_nr]

            plot[0].set_color(color)
            plots.append(plot)

            if plot_nr == 0:
                legend_labels.append(taxon)

    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(xlocations, x_labels)
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    barlist = [container[0] for container in plots]
    leg = plt.legend(barlist, legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

    return fig, leg


def get_color_list(number_of_colors):

    """Colors a list with plotted bars"""

    color_list = []
    for bar_nbr in range(number_of_colors):
        color = get_color(number_of_colors, bar_nbr)
        color_list.append(color)
    return color_list


def get_color(sample_count, nbr):

    """Retrieves graded colors from a given color scale"""

    color_nbr = int((255 / (sample_count + 1)) * (nbr + 1))
    return COLOR_SCALE(color_nbr)

if __name__ == '__main__':
    main()
