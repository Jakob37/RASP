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

from src.pipeline_modules import program_module

MEMORY_SIZE_GB = 8
TAX_FILTER_SUFFIX = '.taxfiltered'


class RDPClassifierWrapper(program_module.ProgramWrapper):

    def setup_commands(self, file_path_dict, option_dict=None):

        significance_threshold = option_dict['rdp_identity']
        rdp_database = option_dict['rdp_database']
        rdp_depth = option_dict['rdp_depth']

        input_fp = file_path_dict['prepare_otus']['final_otus']
        out_dir = self.output_dir

        # RDP classifier
        fixed_rank_fp = out_dir + 'fixedRank.txt'
        significant_taxa_fp = out_dir + 'significant.txt'
        self.add_command_entry(get_rdp_command(self.config_file, input_fp, fixed_rank_fp, significant_taxa_fp,
                                               significance_threshold, rdp_database))

        # Extract OTU tax-rank
        taxa_otu_rank_fp = out_dir + 'taxa_otu_rank.txt'
        itol_table_fp = out_dir + 'itol_labels.txt'
        abundancy_table = file_path_dict['prepare_otus']['filtered_otu_abundancy']
        self.add_command_entry(get_extract_otu_tax_rank_command(self.config_file, fixed_rank_fp, taxa_otu_rank_fp,
                                                                itol_table_fp, abundancy_table, significance_threshold,
                                                                rdp_database, rdp_depth))

        # Create color tables
        otu_color_taxa_table = self.output_dir + 'otu_color_taxa_table.txt'
        taxa_color_table = self.output_dir + 'taxa_color_table.txt'
        otu_significant_taxa = taxa_otu_rank_fp
        self.add_command_entry(get_create_color_tables_command(self.config_file, otu_significant_taxa,
                                                               otu_color_taxa_table, taxa_color_table))

        file_path_dict[self._name]['rdp_otu_taxa'] = fixed_rank_fp
        file_path_dict[self._name]['otu_significant_taxa'] = taxa_otu_rank_fp

        file_path_dict[self._name]['rdp_significant_tax_count'] = significant_taxa_fp
        file_path_dict[self._name]['itol_labels'] = itol_table_fp

        file_path_dict[self._name]['otu_color_taxa_table'] = otu_color_taxa_table
        file_path_dict[self._name]['taxa_color_table'] = taxa_color_table


def get_rdp_command(config, input_fp, fixed_rank_fp, significant_taxa_fp, significance_threshold, chosen_database):

    """Run the RDP classification program"""

    description = 'rdp classifier'
    short = 'RDP'

    if chosen_database == '18S':
        train_option = ['-t', config['databases']['rdpclassifier_18S']]
    else:
        train_option = []

    command = ['java', '-Xmx' + str(MEMORY_SIZE_GB) + 'g',
               '-jar',              config['programs']['rdpclassifier'],
               'classify', '-c',    significance_threshold,
               '-f',                'fixrank',
               '-o',                fixed_rank_fp,
               '-h',                significant_taxa_fp]

    command += train_option
    command += [input_fp]

    return program_module.ProgramCommand(description, short, command)


def get_create_color_tables_command(config, fixed_rdp_output_fp, otu_color_taxa_table, taxa_color_table):

    """Produces color tables for color strap and color definitions"""

    description = 'create color tables'
    short = 'cct'

    command = [config['scripts']['colors_from_phyla'],
               '--input',           fixed_rdp_output_fp,
               '--otu_color_taxa',  otu_color_taxa_table,
               '--taxa_color',      taxa_color_table]

    return program_module.ProgramCommand(description, short, command)


def get_extract_otu_tax_rank_command(config, fixed_rank, taxa_otu_rank, otu_taxa_labels, abund_table,
                                     significance_threshold, rdp_database, rdp_depth):

    """Extract OTU-tax-ranks"""

    description = 'OTU taxextr'
    short = 'te'

    command = [config['scripts']['taxrank_extractor'],
               '--input',                   fixed_rank,
               '--output',                  taxa_otu_rank,
               '--significance_threshold',  significance_threshold,
               '--out_taxlabel',            otu_taxa_labels,
               '--abundance_table',         abund_table]

    if rdp_database == '16S' and rdp_depth == 'phylum':
        command += ['--deeper_taxa', 'proteobacteria']

    if rdp_depth == 'phylum':
        base_depth = 1
    elif rdp_depth == 'class':
        base_depth = 2
    else:
        raise Exception('Unknown RDP depth encountered: {}'.format(rdp_depth))

    if rdp_database == '16S':
        command += ['--depth', base_depth]
    elif rdp_database == '18S':
        command += ['--depth', base_depth + 1]

    return program_module.ProgramCommand(description, short, command)
