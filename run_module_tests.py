#!/usr/bin/python3

__author__ = 'jakob'

import argparse
from src.TestSuite import module_tests

module_description = """
Main script for running a sequence of
"""


def main():

    args = parse_arguments()

    if args.reset_logs:
        module_tests.Test.reset_logfiles()

    run_prinseq_module()
    run_cdhit_module()
    run_rdp_module()
    run_pynast_module()
    run_indices_module()
    run_tree_module()
    run_visualize_module()


def parse_arguments():

    """Parses command line arguments to the variable args"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--reset_logs', action='store_true')
    return parser.parse_args()


def run_prinseq_module():

    prinseq_test = module_tests.PrinseqTest()
    prinseq_test.run()


def run_cdhit_module():

    fasta_fastq_test = module_tests.FastqToFastaTest()
    fasta_fastq_test.run()

    derep_test = module_tests.DerepTest()
    derep_test.run()

    label_test = module_tests.LabelFastaHeaderTest()
    label_test.run()

    cdhit_test = module_tests.CDHitTest()
    cdhit_test.run()

    extract_mapping_table_test = module_tests.ExtractMappingTableTest()
    extract_mapping_table_test.run()

    filter_otus_test = module_tests.FilterOTUTest()
    filter_otus_test.run()

    chimera_checking_test = module_tests.ChimeraCheckingTest()
    chimera_checking_test.run()

    rename_otus = module_tests.RenameOTUsTest()
    rename_otus.run()


def run_rdp_module():

    # rdp = module_tests.RDPTest()
    # rdp.run()
    #
    # create_color_tables = module_tests.CreateColorTablesTest()
    # create_color_tables.run()

    extract_otu_tax_rank = module_tests.ExtractOTUTaxRankTest()
    extract_otu_tax_rank.run()


def run_pynast_module():

    filter_bad_taxa = module_tests.FilterBadTaxaTest()
    filter_bad_taxa.run()

    annotate_otu = module_tests.AnnotateOTUsTest()
    annotate_otu.run()

    pynast = module_tests.PyNASTTest()
    pynast.run()

    convert_to_phylip = module_tests.ConvertToPhylipTest()
    convert_to_phylip.run()

    reduce_phylip = module_tests.ReducePhylipTest()
    reduce_phylip.run()


def run_tree_module():

    fast_tree = module_tests.FastTreeTest()
    fast_tree.run()

    ete = module_tests.ETETest()
    ete.run()


def run_indices_module():

    chao = module_tests.ChaoTest()
    chao.run()


def run_visualize_module():

    create_barplot_data = module_tests.CreateBarplotDataTest()
    create_barplot_data.run()

    taxa_barplot = module_tests.TaxaBarplotTest()
    taxa_barplot.run()


if __name__ == '__main__':
    main()