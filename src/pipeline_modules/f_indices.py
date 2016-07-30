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

SAMPLE_STEPS = 30
SAMPLE_REPLICATES = 3


class IndicesWrapper(program_module.ProgramWrapper):

    """
    Calculates species indices based on OTU abundancy tables

    Currently calculates:
        - Chao1 index
        - Rarefaction
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        otu_mapping_table = self.output_dir + 'otu_mapping_table.txt'

        derep_mapping_fp = file_path_dict['prepare_otus']['derep_mapping']
        cluster_mapping_fp = file_path_dict['prepare_otus']['cluster_mapping']
        name_mapping_table_fp = file_path_dict['prepare_otus']['otu_name_mapping']
        self.add_command_entry(get_create_otu_table_command(self.config_file, cluster_mapping_fp, derep_mapping_fp,
                                                            name_mapping_table_fp, otu_mapping_table))

        plot_rarefaction_fp = self.output_dir + 'rarefaction.png'
        plot_chao_fp = self.output_dir + 'chao.png'

        self.add_command_entry(get_generate_alpha_plots_command(self.config_file, plot_rarefaction_fp,
                                                                plot_chao_fp, otu_mapping_table))

        file_path_dict[self._name]['rarefaction_curve'] = plot_rarefaction_fp
        file_path_dict[self._name]['chao1_curve'] = plot_chao_fp

        file_path_dict[self._name]['otu_mapping_table'] = otu_mapping_table


def get_create_otu_table_command(config, cluster_mapping, derep_mapping, name_mapping_table, otu_table):

    """
    Creates OTU table where counts in separate samples are mapped to the different OTUs
    """

    description = 'OTU-table'
    short = 'OT'

    command = [config['scripts']['create_otu_table'],
               '--cluster_mapping', cluster_mapping,
               '--derep_mapping', derep_mapping,
               '--name_mapping', name_mapping_table,
               '--output', otu_table]

    return program_module.ProgramCommand(description, short, command)


def get_generate_alpha_plots_command(config, plot_rar, plot_chao, otu_mapping_table):

    """Runs the preliminary chao1/rarefaction calculating script"""

    description = 'Chao1'
    short = 'PC'

    command = [config['scripts']['alpha_plots'],
               '--plot_rarefaction',    plot_rar,
               '--plot_chao',           plot_chao,
               '--samplepoints',        SAMPLE_STEPS,
               '--replicates',          SAMPLE_REPLICATES,
               '--otu_mapping_table',   otu_mapping_table]

    return program_module.ProgramCommand(description, short, command)
