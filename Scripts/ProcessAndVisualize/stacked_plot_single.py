#!/usr/bin/env python3
__author__ = "Jakob Willforss"

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm

import argparse

program_description = """
Creates a stacked make_plot from a taxa-matrix

IS CURRENTLY NOT GENERAL FOR SEVERAL SAMPLES
"""

COLOR_SCALE = cm.spectral
TITLE = 'Phylum/Class'


def main():

    args = parse_arguments()
    input_fh = open(args.input, 'r')

    title, headers, taxa_count_pairs = extract_data(input_fh)

    taxa_color_dict = None
    if args.color_table:
        taxa_color_dict = extract_color_dict(args.color_table)

    fig, leg = make_plot(taxa_count_pairs, TITLE, headers, taxa_color_dict)
    fig.savefig(args.output + '.png', format='png', bbox_extra_artists=(leg,), bbox_inches='tight')
    input_fh.close()


def parse_arguments():

    """Parses the command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='Input file', required=True)
    parser.add_argument('-o', '--output', help='Output file', required=True)
    parser.add_argument('-c', '--color_table', help='Optional table to specify taxa colors')
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


def extract_data(input_fh):

    """Retrieves information from matrix with taxonomical information"""

    taxa_count_pairs = []
    line_nbr = 1
    for line in input_fh:

        line = line.rstrip()

        if line_nbr == 1:
            title = line
        elif line_nbr == 2:
            headers = line.split('\t')
        else:
            taxa_count_pairs.append(line.split('\t'))
        line_nbr += 1

    return title, headers, taxa_count_pairs


def make_plot(taxa_count_pairs, title, headers, taxa_color_dict=None):

    """Takes taxonomical data and titles, returns a figure and legend"""

    xlocations = 0.5
    width = 0.2

    fig = plt.figure()
    plots = []
    tot_height = 0

    if taxa_color_dict is None:
        color_generator = get_bar_color(len(taxa_count_pairs))

    labels = []
    for taxa, count, sample in taxa_count_pairs:
        plot = plt.bar(xlocations, int(count), width=width, color='g', bottom=tot_height, align='center')
        tot_height += int(count)

        if taxa_color_dict is not None:
            color = taxa_color_dict[taxa]
        else:
            color = next(color_generator)

        plot[0].set_color(color)

        plots.append(plot)
        labels.append(taxa)

    plt.ylabel(headers[1])
    plt.title(title)
    plt.xticks([0.5], ('Sample1',))
    plt.xlim(0, 1)

    barlist = [container[0] for container in plots]
    leg = plt.legend(barlist, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

    return fig, leg


def get_bar_color(number_of_colors):

    """Colors a list with plotted bars"""

    for bar_nbr in range(number_of_colors):
        color = get_color(number_of_colors, bar_nbr)
        yield color
        # barlist[bar_nbr][0].set_color(color)


def get_color(sample_count, nbr):

    """Retrieves graded colors from a given color scale"""

    color_nbr = int((255 / (sample_count + 1)) * (nbr + 1))
    return COLOR_SCALE(color_nbr)

if __name__ == '__main__':
    main()
