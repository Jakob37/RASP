#!/usr/bin/python3
__author__ = "Jakob Willforss"

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import cm

import argparse
import numpy as np

program_description = """
Plots time elapsed in different parts of the pipeline
Displays those processes that take up more than a certain
percentage of the execute_test time (decided by the filter_threshold)
"""

COLOR_SCALE = cm.gist_earth
FILTER_THRESHOLD = 0.01

BAR_WIDTH = 0.7
LABEL_FONT_SIZE = 16
TITLE_FONT_SIZE = 20


def main():

    args = parse_arguments()
    input_fh = open(args.input, 'r')

    title, xlabel, legend_label, ylabel, datapoints = extract_data(input_fh)
    time_col = 1
    tot_time = sum([float(dp[time_col]) for dp in datapoints])
    title += ' Total time: {} seconds'.format(int(tot_time))

    filter_short_prog_runs(datapoints, tot_time, FILTER_THRESHOLD)

    x_values, y_values, point_labels = get_expanded_datapoints(datapoints)

    fig, leg = bar_plot(x_values, y_values, point_labels, title, 'Run time (seconds)')
    fig.savefig(args.output, format='PDF', bbox_extra_artists=(leg,), bbox_inches='tight')

    input_fh.close()


def get_expanded_datapoints(datapoints):

    """
    Takes a list of datapoints (triple tuples)
    and returns the sub-values as three separate lists
    """

    x_values = [d_point[0] for d_point in datapoints]
    y_values = [float(d_point[1]) for d_point in datapoints]
    point_labels = [d_point[2] for d_point in datapoints]

    return x_values, y_values, point_labels


def filter_short_prog_runs(datapoints, total_time, filter_threshold_percentage):

    """
    Removes datapoints for programs for which the running time is lower than
    a certain percentage of the total running time
    """

    for pos in range(len(datapoints) - 1, -1, -1):
        if float(datapoints[pos][1]) < filter_threshold_percentage * total_time:
            del datapoints[pos]


def parse_arguments():

    """Parses the command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='The input file', required=True)
    parser.add_argument('-o', '--output', help='Path of output make_plot', required=True)
    args = parser.parse_args()
    return args


def extract_data(input_fh):

    """
    Retrieves x, y and label data from given textfile
    Returns labels and a list with data-point tuples (x, y, short name)
    """

    datapoints = []
    line_nbr = 1
    for line in input_fh:
        line = line.rstrip()
        if line_nbr == 1:
            title = line
        elif line_nbr == 2:
            xlabel, legend_label, ylabel = line.split('\t')
        else:
            x, y, acr = line.split('\t')
            datapoints.append((x, y, acr))
        line_nbr += 1
    return title, xlabel, legend_label, ylabel, datapoints


def bar_plot(xvalues, yvalues, shorts, title, ylab):

    """Takes data and labels, creates and returns plot and legend"""

    fig = pyplot.figure()
    ax = pyplot.subplot(111)
    remove_axes(ax)

    ind = np.arange(len(xvalues))
    barlist = pyplot.bar(ind, yvalues, align='center', width=BAR_WIDTH)
    color_bars(barlist)

    pyplot.ylabel(ylab, fontsize=LABEL_FONT_SIZE)
    pyplot.xticks(ind, shorts, fontsize=LABEL_FONT_SIZE)
    pyplot.title(title, fontsize=TITLE_FONT_SIZE)

    leg = pyplot.legend(barlist, xvalues, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

    return fig, leg


def remove_axes(ax):

    """Removes upper and right axes from axis object"""

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    return ax


def color_bars(barlist):

    """Colors a list with plotted bar-objects"""

    for bar_nbr in range(len(barlist)):
        color = get_color(len(barlist), bar_nbr)
        barlist[bar_nbr].set_facecolor(color)


def get_color(sample_count, nbr):

    """Calculates and returns color based on """

    scale_color_count = 255
    color_nbr = int((scale_color_count / (sample_count + 1)) * (nbr + 1))

    return COLOR_SCALE(color_nbr)

if __name__ == '__main__':
    main()
