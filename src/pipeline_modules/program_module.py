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

from src.util_scripts import command_builder


class ProgramWrapper:

    """
    Base-class for all pipeline-segments
    Each contains a number of commands for which the purpose
    is to perform a specific task like 'clean reads' or 'build tree'
    """

    def __init__(self, name, path_generator, config_file):
        self._name = name
        self.executable_commands = []
        self.path_generator = path_generator
        self.output_dir = self.path_generator(name)

        self.config_file = config_file
        self.program_dir = config_file['basepaths']['programs']
        self.script_dir = config_file['basepaths']['scripts']

    def setup_commands(self, input_fp, file_path_dict):

        """
        Retrieve the specific execute_test command for the program instance
        Must be implemented by the subclass
        """

        raise NotImplementedError

    def is_setup(self):

        """Evaluate if commands are added to the module"""

        return len(self.executable_commands) is not None

    def run(self, log_fp, log_table_fp):

        """Main method, rigs the program call and executes it"""

        if self.is_setup():

            with open(log_fp, 'a') as log_fh, open(log_table_fp, 'a') as log_table_fh:
                log_fh.write('{} wrapper initiated\n'.format(self._name))
                self._execute_commands(log_fh, log_table_fh)
                log_fh.write('\n')
        else:
            raise Exception('The program-module is not setup. Call "setup_commands" before running')

    def add_command(self, command, description, short_description):

        """Adds an executable command to the list commands"""

        cb = command_builder.CommandBuilder(description, short_description)
        cb.add_commands(command)
        self.executable_commands.append(cb)

    def add_command_entry(self, command_class):

        """Adds an executable command to the list commands"""

        cb = command_builder.CommandBuilder(command_class.description, command_class.short)
        cb.add_commands(command_class.command)
        self.executable_commands.append(cb)

    def _execute_commands(self, log_fh, log_table_fh):

        """Executes the commands stored in the list executable_commands"""

        for command in self.executable_commands:
            command.execute_command_verbose(log_fh, log_table_fh)


class ProgramCommand:

    def __init__(self, description, short, command):
        self.description = description
        self.short = short

        for n in range(len(command)):
            command[n] = str(command[n])

        self.command = command
