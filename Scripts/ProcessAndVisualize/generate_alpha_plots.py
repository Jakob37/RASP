#!/usr/bin/python3

import argparse
import random
import matplotlib
matplotlib.use('Agg')
import numpy
import matplotlib.pyplot as plt
from matplotlib import cm
import skbio.diversity.alpha as skbio

COLOR_SCALE = cm.nipy_spectral

program_description = """
Calculates CHAO1 index from abundance table
Able to visualize both rarefaction curve and chao1 subsampling curve
"""


def main():

    args = parse_arguments()
    if not args.plot_rarefaction and not args.plot_chao:
        raise Exception('No output plot is specified, use at least one of arguments "plot_rarefaction" and "plot_chao"')

    nbr_samplepoints = args.samplepoints
    replicates = args.replicates

    id_lists, samples = get_otu_id_list(args.otu_mapping_table)

    richness_datapoints = calculate_richness_datapoints_new(nbr_samplepoints, replicates, id_lists) 
    chao_datapoints = calculate_chao_datapoints(nbr_samplepoints, replicates, id_lists)

    if args.plot_rarefaction:
        plot_data('Rarefaction curve', richness_datapoints, samples, args.plot_rarefaction, args.plot_linefit)

    if args.plot_chao:
        plot_data('Chao1 curve', chao_datapoints, samples, args.plot_chao, args.plot_linefit)


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-m', '--otu_mapping_table', required=True,
                        help='Matrix with OTU/sample counts')
    parser.add_argument('--plot_rarefaction',
                        help='Output path for rarefaction plot')
    parser.add_argument('--plot_chao',
                        help='Output path for chao plot')
    parser.add_argument('-n', '--samplepoints', default=30, type=int,
                        help='Number of sample points')
    parser.add_argument('-r', '--replicates', default=5, type=int,
                        help='Number of replicates per sample point')
    parser.add_argument('--plot_linefit', default=False, action='store_true',
                        help='Should linefit be included')
    args = parser.parse_args()
    return args


def get_otu_id_list(raw_otu_table):

    """
    Generates a list where OTUs are represented by their ID and the ID is present the same
    number of times as the corresponding abundance
    """

    with open(raw_otu_table, 'r') as input_fh:

        samples = input_fh.readline().rstrip().split('\t')[1:]

        sample_id_lists = list()
        for _ in range(len(samples)):
            sample_id_lists.append(list())

        for line in input_fh:
            line = line.rstrip().split('\t')
            otu_id = line[0]
            id_counts = [int(count) for count in line[1:]]

            for pos in range(len(id_counts)):

                count = id_counts[pos]

                for _ in range(count):
                    sample_id_lists[pos].append(otu_id)

    return sample_id_lists, samples


def calculate_chao_datapoints(nbr_samplepoints, replicates, id_lists):

    """Calculates and returns sample count/Chao1 estimate value pairs"""

    datapoint_lists = list()
    for id_list in id_lists:

        total_read_count = len(id_list)
        interval = total_read_count // nbr_samplepoints

        datapoints = []
        for subset_size in range(interval, total_read_count, interval):

            total_value = 0
            for _ in range(replicates):

                single_chao_estimate = get_chao_subsample(id_list, subset_size)
                total_value += single_chao_estimate

            average_chao_estimate = total_value / replicates
            datapoints.append((subset_size, average_chao_estimate))

        datapoint_lists.append(datapoints)

    return datapoint_lists


def get_chao_subsample(ids_list, subset_size):

    """Calculate a single Chao1 using an id list and a target subset size"""

    id_subset = random.sample(ids_list, subset_size)

    otu_dict = dict()
    for otu_id in id_subset:

        if otu_id not in otu_dict:
            otu_dict[otu_id] = 1
        else:
            otu_dict[otu_id] += 1

    count_list_subset = list(otu_dict.values())
    chao_estimate = skbio.chao1(count_list_subset)

    return chao_estimate


def calculate_richness_datapoints_new(nbr_samplepoints, replicates, id_lists):

    """Calculates and retrieves sampled-sequence/richness value pairs"""

    datapoint_lists = list()
    for id_list in id_lists:

        datapoint_list = list()
        total_read_count = len(id_list)
        interval = total_read_count // nbr_samplepoints

        for subset_size in range(0, total_read_count, interval):

            total_value = 0
            for n in range(replicates):
                sub_value = get_richness_subsample_randomsample(id_list, subset_size)
                total_value += sub_value

            average_found_otus = total_value / replicates
            datapoint_list.append((subset_size, average_found_otus))

        datapoint_lists.append(datapoint_list)

    return datapoint_lists


def get_richness_subsample_randomsample(id_list, subset_size):

    """Calculates the number of found species in a subsample"""

    sample = random.sample(id_list, subset_size)
    found_species = len(set(sample))

    return found_species


def plot_data(title, datapoints, samples, plot_path, plot_linefit):

    """Generates a scatterplot from given x- and y-values"""

    fig = plt.figure()

    plots = list()          # Used for linefit

    color_list = get_color_list(len(samples))
    curve_steps = 1000

    current_pos = 0
    for datapoint_set in datapoints:

        xvalues = [coord[0] for coord in datapoint_set]
        yvalues = [coord[1] for coord in datapoint_set]

        plot = plt.plot(xvalues, yvalues, 'o', label='Original noised data')
        plot[0].set_color(color_list[current_pos])

        plots.append(plot)

        if plot_linefit:
            max_x = max(xvalues)
            step_x = max_x / curve_steps
            coefficients = numpy.polyfit(xvalues, yvalues, 2)
            polynomial = numpy.poly1d(coefficients)
            xs = numpy.arange(0, max_x, step_x)
            ys = polynomial(xs)
            linefit = plt.plot(xs, ys)
            linefit[0].set_color(color_list[current_pos])

        current_pos += 1

    plt.title(title)
    plt.xlabel('Number of reads')
    plt.ylabel('Number of OTUs')
    plt.ylim(0,)

    barlist = [container[0] for container in plots]
    legend = plt.legend(barlist, samples, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, numpoints=1)
    fig.savefig(plot_path, format='png', bbox_extra_artist=(legend,), bbox_inches='tight')


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
