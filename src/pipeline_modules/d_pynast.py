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

MIN_INPUT_TO_ALIGNMENT_LENGTH = 50
TAX_FILTER_SUFFIX = '.taxfiltered'


class PynastWrapper(program_module.ProgramWrapper):

    """
    Takes otus and aligns them to a given template alignment
    This alignment can be used for building phylogenetic trees
    """

    def setup_commands(self, file_path_dict, option_dict=None):

        min_alignment_similarity_percentage = option_dict['pynast_identity']
        rdp_database = option_dict['rdp_database']

        # Filter bad taxa
        raw_otus = file_path_dict['prepare_otus']['final_otus']
        otu_taxa_table = file_path_dict['rdp_classifier']['otu_significant_taxa']
        abundancy_matrix = file_path_dict['prepare_otus']['filtered_otu_abundancy']
        self.add_command_entry(get_filter_bad_taxa_command(self.config_file, raw_otus, abundancy_matrix,
                                                           otu_taxa_table, self.output_dir))

        filtered_otus = self.output_dir + raw_otus.split('/')[-1] + TAX_FILTER_SUFFIX
        filtered_abundance = self.output_dir + abundancy_matrix.split('/')[-1] + TAX_FILTER_SUFFIX
        annotated_otus = filtered_otus + '.annotated'
        annotated_abundance = filtered_abundance + '.annotated'

        # Annotate OTUs command
        self.add_command_entry(get_annotate_otus_command(self.config_file, filtered_otus, filtered_abundance,
                                                         annotated_otus, annotated_abundance, otu_taxa_table))

        # Run PyNAST
        pynast_alignment_fasta = self.output_dir + 'alignment.fasta'
        pynast_log = self.output_dir + 'log.txt'
        pynast_failed = self.output_dir + 'failed.fasta'
        self.add_command_entry(get_pynast_command(self.config_file, filtered_otus, pynast_alignment_fasta, pynast_log,
                                                  pynast_failed, min_alignment_similarity_percentage, rdp_database))

        # Convert alignment to Phylip format
        pynast_alignment_phylip = self.output_dir + 'alignment.phylip'
        self.add_command_entry(get_convert_to_phylip_command(self.config_file, pynast_alignment_fasta,
                                                             pynast_alignment_phylip))

        # Reduce Phylip alignment
        pynast_alignment_phylip_reduced = self.output_dir + 'alignment.phylip.script_reduced'
        self.add_command_entry(get_reduce_phylip_command(self.config_file, pynast_alignment_phylip,
                                                         pynast_alignment_phylip_reduced))

        file_path_dict['pynast']['taxa_filtered_otus'] = filtered_otus
        file_path_dict['pynast']['taxa_filtered_otu_abundancies'] = filtered_abundance
        file_path_dict['pynast']['final_alignment'] = pynast_alignment_phylip_reduced
        file_path_dict['pynast']['annotated_otus'] = annotated_otus
        file_path_dict['pynast']['annotated_abundance'] = annotated_abundance


def get_filter_bad_taxa_command(config, raw_otus, abundancy_matrix, otu_taxa_table, output_dir):

    """
    Filters out OTUs whose taxa is determined with low confidence
    by RDP classifier.
    Filtering effects both OTU fasta file, and abundancy table
    """

    description = 'filter taxa'
    short = 'ft'

    command = [config['scripts']['filter_poor_taxa'],
               '--input', raw_otus,
               '--taxa_table', otu_taxa_table,
               '--suffix', TAX_FILTER_SUFFIX,
               '--abund_matrix', abundancy_matrix,
               '--output_dir', output_dir]

    return program_module.ProgramCommand(description, short, command)


def get_annotate_otus_command(config, raw_otus, raw_abundance, annotated_otus, annotated_abundance, taxa_otu_rank):

    """
    Annotates an OTU-fasta file and an OTU-abundancy matrix
    """

    description = 'annotate otu'
    short = 'ao'

    command = [config['scripts']['annotate_otu'],
               '--input_fasta', raw_otus,
               '--input_abundancy', raw_abundance,
               '--input_taxa', taxa_otu_rank,
               '--annotated_fasta', annotated_otus,
               '--annotated_abundancy', annotated_abundance]

    return program_module.ProgramCommand(description, short, command)


def get_pynast_command(config, filtered_otus, pynast_alignment_fasta, pynast_log, pynast_failed,
                       min_alignment_similarity_percentage, rdp_database):

    """Run PyNAST"""

    description = 'PyNAST'
    short = 'PN'

    if rdp_database == '16S':
        pynast_database = config['databases']['pynast_16S']
    elif rdp_database == '18S':
        pynast_database = config['databases']['pynast_16S']
    else:
        raise AttributeError('Chosen RDP database: {} doesn\'t exist!'.format(rdp_database))

    command = [config['programs']['pynast'],
               '-i', filtered_otus,
               '-t', pynast_database,
               '-l', MIN_INPUT_TO_ALIGNMENT_LENGTH,
               '-p', min_alignment_similarity_percentage,

               '-a', pynast_alignment_fasta,
               '-g', pynast_log,
               '-f', pynast_failed]

    return program_module.ProgramCommand(description, short, command)


def get_convert_to_phylip_command(config, pynast_alignment_fasta, pynast_alignment_phylip):

    """Convert fasta-alignment to phylip format"""

    description = 'Convert fas/phy'
    short = 'Cfp'

    command = [config['scripts']['fasta_to_phylip'],
               '--input_fasta', pynast_alignment_fasta,
               '--output_phylip', pynast_alignment_phylip]

    # command = [config['programs']['fasta2phylip'],
    #            pynast_alignment_fasta,
    #            pynast_alignment_phylip]

    return program_module.ProgramCommand(description, short, command)


def get_reduce_phylip_command(config, phylip_alignment, phylip_alignment_reduced):

    """Remove empty columns from phylip alignment"""

    description = 'Reduce phylip'
    short = 'rp'

    command = [config['scripts']['reduce_phylip'],
               '-i', phylip_alignment,
               '-o', phylip_alignment_reduced]

    return program_module.ProgramCommand(description, short, command)
