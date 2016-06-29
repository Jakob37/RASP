#!/usr/bin/python
__author__ = 'Jakob Willforss'

"""
This is an example script for using itol_interaction_script
To use itol_interaction_script, you essentially have to instantiate the object, set the tree,
submit the file to itol, then use the returned data

Credits: https://github.com/albertyw/itolapi
"""

import os
import sys

# noinspection PyUnresolvedReferences
from itolapi import Itol
# noinspection PyUnresolvedReferences
from itolapi import ItolExport

###

import argparse

FONT_SIZE = '35'
STRIP_WIDTH = '20'


def main():
    args = parse_arguments()

    pathname = os.path.dirname(sys.argv[0])
    fullpath = os.path.abspath(pathname)
    parent_path = fullpath + "/../"
    sys.path.append(parent_path + 'itolapi/')

    print('Running example itol and itolexport script')
    print('')
    print('Creating the upload params')

    #Create the Itol class
    itol_obj = Itol.Itol()

    setup_tree(itol_obj, args)

    # Check parameters
    #itol_obj.print_variables()

    #Submit the tree
    print('Uploading the tree. This may take some time depending on how '
          'large the tree is and how much load there is on the itol server')
    good_upload = itol_obj.upload()

    if not good_upload:
        print('There was an error:' + itol_obj.comm.upload_output)
        sys.exit(1)

    #Read the tree ID
    print('Tree ID: ' + str(itol_obj.comm.tree_id))

    #Read the iTOL API return statement
    print('iTOL output: ' + str(itol_obj.comm.upload_output))

    #Website to be redirected to iTOL tree
    print('Tree Web Page URL: ' + itol_obj.get_webpage())

    # Warnings associated with the upload
    print('Warnings: ' + str(itol_obj.comm.warnings))

    # export_tree(itol_obj, 'svg', args.output + '.svg')
    export_tree(itol_obj, 'svg', args.output + '.svg')


def parse_arguments():

    """Retrieves and returns command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='The input file', required=True)
    parser.add_argument('-o', '--output', help='The output file', required=True)
    parser.add_argument('-a', '--abundance', help='Dataset containing OTU abundance information')
    parser.add_argument('-c', '--coloring', help='Dataset containing color and taxonomical information')
    parser.add_argument('-d', '--color_def', help='Color definition file')
    parser.add_argument('-l', '--labels', help='Table with new label names')
    args = parser.parse_args()
    return args


def setup_tree(itol_object, args):

    """
    Prepares the tree for upload
    Adds the basic input file and basic settings
    If specified, also adds abundance- and coloring-datasets
    """

    tree = args.input
    itol_object.add_variable('treeFile', tree)

    itol_object.add_variable('treeName', 'TESTINGTREE')
    itol_object.add_variable('treeFormat', 'newick')
    itol_object.add_variable('midpointRoot', 'true')

    if args.labels:
        itol_object.add_variable('fontStylesFile', args.labels)

    if args.color_def:
        itol_object.add_variable('colorDefinitionFile', args.color_def)

    if args.coloring:
        add_taxa_color_dataset(itol_object, args.coloring)

    if args.abundance:
        add_abundance_dataset(itol_object, args.abundance)


def add_abundance_dataset(itol_object, dataset_fp):

    """Adds OTU abundance information based on an OTU - abundance matrix"""

    itol_object.add_variable('dataset1File', dataset_fp)
    itol_object.add_variable('dataset1Label', 'colorz')
    itol_object.add_variable('dataset1Separator', 'tab')
    itol_object.add_variable('dataset1Type', 'simplebar')
    itol_object.add_variable('dataset1CiclesFill', 'red')


def add_taxa_color_dataset(itol_object, dataset_fp):

    """
    Adds taxonomical information, and a separate color linked to each taxa
    This is then displayed as a color strip around the tree
    """

    itol_object.add_variable('dataset2File', dataset_fp)
    itol_object.add_variable('dataset2Label', 'colors')
    itol_object.add_variable('dataset2Separator', 'tab')
    itol_object.add_variable('dataset2Type', 'colorstrip')
    itol_object.add_variable('dataset2StripWidth', STRIP_WIDTH)


def export_tree(itol_object, file_format, output_fp):

    """Exports the retrieved tree to either pdf or svg format"""

    assert file_format in('svg', 'pdf', 'png'), 'Format must be png, svg or pdf'

    itol_exporter = ItolExport.ItolExport()
    itol_exporter.set_export_param_value('tree', '18793532031912684633930')

    print('Exporting to {}'.format(file_format))
    itol_exporter = itol_object.get_itol_export()
    itol_exporter.set_export_param_value('fontSize', FONT_SIZE)
    export_location = output_fp
    itol_exporter.set_export_param_value('format', file_format)
    datasets = 'dataset1,dataset2'
    itol_exporter.set_export_param_value('datasetList', datasets)
    itol_exporter.export(export_location)
    print('exported tree to ', export_location)

if __name__ == '__main__':
    main()












