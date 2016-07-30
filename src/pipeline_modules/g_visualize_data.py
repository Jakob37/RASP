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


class CreateBarplotsWrapper(program_module.ProgramWrapper):

    def setup_commands(self, file_path_dict, option_dict=None):

        out_dir = self.output_dir

        otu_mapping_table_fp = file_path_dict['indices']['otu_mapping_table']

        # Create barplot data
        taxa_otu_rank = file_path_dict['rdp_classifier']['otu_significant_taxa']
        tax_count_table = out_dir + 'taxa_otu_rank.txt.barplot'
        tax_abund_table = out_dir + 'taxa_otu_rank_abund.txt.barplot'
        self.add_command_entry(get_create_barplot_data_command(self.config_file, taxa_otu_rank, otu_mapping_table_fp,
                                                               tax_count_table, tax_abund_table))

        taxa_color_table = file_path_dict['rdp_classifier']['taxa_color_table']

        # Create taxa barplot (clusters)
        matplotlib_out_fp = self.path_generator('output') + 'taxa_plot'
        self.add_command_entry(get_taxa_barplot_command(self.config_file, tax_count_table, matplotlib_out_fp,
                                                        taxa_color_table, plot_relative_abundance=True,
                                                        title='OTU counts (Phylum/Class)', 
                                                        ylabel='OTU count (fraction)'))

        # Create taxa barplot (abundance)
        matplotlib_out_abund = self.path_generator('output') + 'abund_taxa_plot'
        self.add_command_entry(get_taxa_barplot_command(self.config_file, tax_abund_table, matplotlib_out_abund,
                                                        taxa_color_table, plot_relative_abundance=True,
                                                        title='Read counts (Phylum/Class)',
                                                        ylabel='Read count (fraction)'))

        # Create timeplot
        time_data_fp = file_path_dict['input']['log_table']
        time_visualization_fp = self.output_dir + 'time_plot.pdf'
        self.add_command_entry(get_timeplot_command(self.config_file, time_data_fp, time_visualization_fp))

        file_path_dict[self._name]['abundance_barplot_data'] = tax_abund_table
        file_path_dict[self._name]['cluster_barplot_data'] = tax_count_table
        file_path_dict[self._name]['time_plot'] = time_visualization_fp


def get_create_barplot_data_command(config, taxa_otu_rank, otu_sample_table, tax_count_table, tax_abund_table):

    """Extracts data from the otu-taxa-table and outputs taxa barplot data"""

    description = 'Create bar-data'
    short = 'cbd'

    command = [config['scripts']['create_barplot_table'],
               '--taxa_table', taxa_otu_rank,
               '--otu_sample_table', otu_sample_table,
               '--barplot_cluster', tax_count_table,
               '--barplot_abund', tax_abund_table]

    return program_module.ProgramCommand(description, short, command)


def get_taxa_barplot_command(config, tax_count_table_fp, matlibplot_out_fp, taxa_color_table,
                             plot_relative_abundance=False, title='MODTITL', ylabel='MODYLABL'):

    """Create a taxa barplot using matplotlib"""

    description = 'Taxa-barplot'
    short = 'tb'

    command = [config['scripts']['make_barplot'],
               '--input', tax_count_table_fp,
               '--output', matlibplot_out_fp,
               '--title', title,
               '--ylabel', ylabel,
               '--color_table', taxa_color_table]

    if plot_relative_abundance:
        command.append('--relative_abundance')

    return program_module.ProgramCommand(description, short, command)


def get_timeplot_command(config, log_table_fp, timeplot_fp):

    """Create a taxa barplot using matplotlib"""

    description = 'Timeplot'
    short = 'tp'

    command = [config['scripts']['time_script'],
               '-i', log_table_fp,
               '-o', timeplot_fp]

    return program_module.ProgramCommand(description, short, command)
