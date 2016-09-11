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


class BuildTreeModule(program_module.ProgramWrapper):

    """
    Computes phylogenetic trees and creates a PDF-image of the tree
    Takes an alignment in phylip format, here produced by PyNAST
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        tree_software = option_dict['tree_software']

        # PyNAST alignment
        pynast_alignment_fp = file_path_dict['pynast']['final_alignment']

        if tree_software == 'fasttree':
            tree_fp = self.output_dir + 'fast_tree.tre'
            self.add_command_entry(get_fast_tree_command(self.config_file, pynast_alignment_fp, tree_fp))
        elif tree_software == 'raxml':
            tree_fp = self.output_dir + 'RAxML_bestTree.raxml_tree.tre'
            self.add_command_entry(get_raxml_command(self.config_file, pynast_alignment_fp, self.output_dir))
        else:
            raise ValueError('Tree software: {} must match either "fasttree" or "raxml"!'.format(tree_software))

        otu_color_taxa_table = file_path_dict['rdp_classifier']['otu_color_taxa_table']

        # Run ETE to create tree rendering
        ete_output = self.path_generator('output') + 'fasttree'
        otu_abundance_information_fp = file_path_dict['pynast']['taxa_filtered_otu_abundancies']
        labels_fp = file_path_dict['rdp_classifier']['itol_labels']
        self.add_command_entry(get_ete_command(self.config_file, tree_fp, ete_output, otu_abundance_information_fp,
                               otu_color_taxa_table, labels_fp))

        file_path_dict[self._name]['tree_file'] = tree_fp


def get_fast_tree_command(config, input_alignment_fp, output_tree_fp):

    """Produces a tree file from a PyNAST alignment using Fast Tree"""

    description = 'FastTree'
    short = 'FT'

    command = [config['scripts']['fasttree'],
               '--input', input_alignment_fp,
               '--output', output_tree_fp,
               '--fasttree_path', config['programs']['fasttree']]

    return program_module.ProgramCommand(description, short, command)


def get_raxml_command(config, input_alignment_fp, output_dir):

    """Produces a tree file from a PyNAST alignment using Fast Tree"""

    description = 'RAxML'
    short = 'Rx'

    seed = 12345
    model_of_substitution = 'GTRGAMMA'
    raxml_out_name = 'raxml_tree.tre'

    command = [config['programs']['raxml'],
               '-p', seed,
               '-m', model_of_substitution,
               '-s', input_alignment_fp,
               '-n', raxml_out_name,
               '-w', output_dir]

    return program_module.ProgramCommand(description, short, command)


def get_ete_command(config, input_tree_fp, output_tree_pic_fp,
                    otu_abund_fp, color_strap_fp, labels_fp):

    """Uses the Python ETE module to create and render a tree"""

    description = 'ETE'
    short = 'ete'

    command = ['xvfb-run', config['scripts']['ete'],
               '--input', input_tree_fp,
               '--output', output_tree_pic_fp,
               '--labels', labels_fp,
               '--abundancies', otu_abund_fp,
               '--color_taxa', color_strap_fp]

    return program_module.ProgramCommand(description, short, command)
