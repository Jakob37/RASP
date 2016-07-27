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

from src.util_scripts import timer
import subprocess

"""
An interface around the subprocess package
The user is able to build a chain of related commands through
the method "add_commands".

They can then be executed using the primitive method "execute_command_simple"
where the command simply is ran.

It can also be executed using the more extensive "execute_command_verbose",
where information about the process and the running time is printed to the terminal,
and logged to the provided file handle.
"""


class CommandBuilder:

    def __init__(self, name, short_description):
        self._command_list = []
        self._command_name = name
        self._command_name_short = short_description
        self._simple_timer = timer.Timer()

    def add_commands(self, commands):

        parsed_commands = []
        for command in commands:

            if not isinstance(command, str):
                command_str = str(command)
                parsed_commands.append(command_str)
            else:
                parsed_commands.append(command)

        self._command_list += parsed_commands

    def get_commands(self):
        return self._command_list

    def execute_command_simple(self):

        process = subprocess.Popen(self._command_list)
        process.wait()

    def execute_command_verbose(self, log_fh, log_table_fh=None):

        time_format_digits = 2
        self._simple_timer.reset()

        print(self._command_list)

        process = subprocess.Popen(self._command_list)
        print(">>> Command: {} is running".format(self._command_name))
        process.wait()

        runtime = self._simple_timer.get_formatted_time(time_format_digits)
        print(">>> Command finished after {} seconds".format(runtime))

        self._print_log_information(runtime, log_fh, log_table_fh)

    def _print_log_information(self, runtime, log_fh, log_table_fh):

        log_fh.write('Command: {}, Runtime: {} seconds\n'.format(self._command_name, runtime))

        if log_table_fh is not None:
            log_table_fh.write('{}\t{}\t{}\n'.format(self._command_name, runtime, self._command_name_short))
