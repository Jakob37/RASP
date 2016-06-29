#!/usr/bin/python3
__author__ = 'Jakob Willforss'

import argparse
import re

program_description = """
Takes a RDP output table with OTUs linked to predicted taxa-levels
Parses it and outputs OTUs that reach a particular taxonomic level
together with their deepest determined taxa
"""

WEIRD_SIGNS_PATTERNS = [re.compile(r'(\W)'), re.compile(r'^_+')]
FILTER_KEYS = ['none']


def main():

    args = parse_arguments()

    deeper_pattern = None
    if args.deeper_taxa:
        deeper_pattern = re.compile(args.deeper_taxa, re.IGNORECASE)
        FILTER_KEYS.append(args.deeper_taxa.lower())

    abund_dict = get_abundancy_dictionary(args.abundance_table)
    entries = get_entries(args.input, args.significance_threshold, args.depth, abundance_dict=abund_dict,
                          deeper_pattern=deeper_pattern)
    output_entries(args.output, entries)

    if args.out_taxlabel:
        output_otu_taxa_table(args.output, args.out_taxlabel, args.depth)


def parse_arguments():

    """Parse the command line input arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='RDP fixed-rank table', required=True)
    parser.add_argument('-o', '--output', help='Output table', required=True)
    parser.add_argument('-s', '--significance_threshold', help='Level to denote significant threshold.',
                        type=float, default=0.8)
    parser.add_argument('-t', '--out_taxlabel', help='Output table with taxa labels')
    parser.add_argument('-a', '--abundance_table', help='Optional table with OTU abundancies')
    parser.add_argument('-d', '--depth', help='Depth for which taxa is extracted', type=int, default=3)

    parser.add_argument('--deeper_taxa', help='Extract taxa on level deeper if this taxa is encountered')

    return parser.parse_args()


def get_taxon_level_dict(rdp_fix_rank_fp):

    """Extracts taxon levels from RDP fix-rank file"""

    with open(rdp_fix_rank_fp, 'r') as fixrank_fh:
        fixrank_line = fixrank_fh.readline().rstrip()

    if fixrank_line is None:
        raise FileNotFoundError('Target file: {}, did not contain expected information!'.format(rdp_fix_rank_fp))

    fixrank_entries = fixrank_line.split('\t')[2:]
    taxon_dict = {n // 3 + 1: fixrank_entries[n] for n in range(len(fixrank_entries)) if n % 3 == 1}
    return taxon_dict


def get_abundancy_dictionary(otu_abund_table):

    """Extracts a dictionary with OTU abundancies from text file"""

    otu_abund_dict = {}
    with open(otu_abund_table, 'r') as fh:

        for line in fh:

            line = line.rstrip()
            otu, abund = line.split('\t')
            otu_abund_dict[otu] = int(abund)

    return otu_abund_dict


def get_entries(input_file, sign_threshold, target_taxdepth, abundance_dict=None, deeper_pattern=None):

    """Create and return a list with entries, each representing a line in the input file"""

    taxon_level_dict = get_taxon_level_dict(input_file)
    Entry.set_taxon_level_dict(taxon_level_dict, target_taxdepth)

    with open(input_file, 'r') as input_fh:
        entries = []
        for line in input_fh:
            line = line.rstrip()
            entry = Entry(line, sign_threshold, abundance_dict, deeper_pattern=deeper_pattern)
            entries.append(entry)

    return entries


def output_entries(output_file, entries):

    """Create a taxa-table displaying deepest match for each OTU"""

    with open(output_file, 'w') as output_fh:
        for entry in entries:
            if not entry.is_filtered(FILTER_KEYS):
                print(str(entry).rstrip(), file=output_fh)


def output_otu_taxa_table(taxa_rank_output_fp, itol_label_fp, target_tax_depth):

    """
    Take taxa/otu-table created by this script and
    extract a table with only OTUs and taxa-names for Itol upload
    """

    with open(taxa_rank_output_fp, 'r') as tax_rank_fh, open(itol_label_fp, 'w') as otu_taxa_fh:

        for line in tax_rank_fh:
            line_args = line.split('\t')
            otu = line_args[0]
            taxa = line_args[3]
            depth = int(line_args[2])
            if depth >= target_tax_depth:
                print('{}\t{}'.format(otu, taxa), file=otu_taxa_fh)


class Entry(object):

    """Represents the information from one line in the RDP output fixedRank-file"""

    taxon_level_dict = None

    def __init__(self, line, threshold, abundancy_dict, deeper_pattern=None):

        self._deepest_taxa_level = 1
        self._deepest_taxa_specification = ('undetermined', 0)
        self._taxa = []
        self.deeper_pattern = deeper_pattern

        self._abundance = 1
        self._otu, self._assigned_taxon = self._parse_line(line, threshold)
        self._abundance = abundancy_dict[self._otu]

    @classmethod
    def set_taxon_level_dict(cls, taxon_level_dict, target_depth):

        """Assign a taxon dictionary to class, used when outputting taxonomic information"""

        cls.taxon_level_dict = taxon_level_dict
        cls.target_depth = target_depth

    def _parse_line(self, line, threshold):

        """Retrieve target data from fixedRank-line"""

        line_array = line.split('\t')
        otu = line_array[0]
        taxa_array = line_array[2:]

        table_stepsize = 3
        for pos in range(0, len(taxa_array), table_stepsize):
            taxa_spec = taxa_array[pos]
            taxa_prob = taxa_array[pos + 2]

            # Clean away weird signs like " in the taxonomic name
            for pattern in WEIRD_SIGNS_PATTERNS:
                taxa_spec = re.sub(pattern, '', taxa_spec)

            if float(taxa_prob) > threshold:
                self._deepest_taxa_level += 1
                self._deepest_taxa_specification = (taxa_spec, taxa_prob)
                self._taxa.append(taxa_spec)

            else:
                break

        taxon = self._get_deeper_taxon()

        return otu, taxon

    def _get_deeper_taxon(self):

        """Retrieve class if proteobacteria, and otherwise phyla"""

        if self._deeper_taxon_identified(self.deeper_pattern):
            return self._taxa[self.target_depth + 1]

        else:
            if len(self._taxa) > self.target_depth + 1:
                return self._taxa[self.target_depth]
            else:
                return 'None'

    def _deeper_taxon_identified(self, pattern):

        """Identify target taxon, and if that case, decide deeper taxon"""

        if pattern is None:
            return False

        if len(self._taxa) > self.target_depth + 1:
            return re.match(pattern, self._taxa[self.target_depth])
        else:
            return False

    def __str__(self):

        """Output extensive entry information"""

        if self.taxon_level_dict is None:
            raise AttributeError('Taxon dictionary is not initiated for the Entry class')

        correction_offset = -1
        taxon = 0
        taxon_prob = 1

        try:
            output_string = '{}\t{}\t{}\t{}\t{}\t{}\t{}'\
                .format(self._otu,
                        self.taxon_level_dict[self._deepest_taxa_level + correction_offset],
                        self._deepest_taxa_level,
                        self._deepest_taxa_specification[taxon],
                        self._deepest_taxa_specification[taxon_prob],
                        self._assigned_taxon,
                        self._abundance)
        except IndexError:
            print('ERROR OCCURED FOR OTU: {}'.format(self._otu))
            output_string = '{} ERROR'.format(self._otu)

        return output_string

    # def get_barplot_tuple(self):
    #     return self._otu, self._assigned_taxon

    def is_filtered(self, filter_list):

        assigned_taxon_lower = self._assigned_taxon.lower()
        return assigned_taxon_lower in filter_list or assigned_taxon_lower == ''

if __name__ == '__main__':
    main()