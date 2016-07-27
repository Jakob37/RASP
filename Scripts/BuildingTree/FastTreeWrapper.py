#!/usr/bin/env python3

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

import argparse
import subprocess

program_description = """
Wrapper for the program FastTree.
The reason for it is that FastTree prints directly to STDOUT, while the pipeline
as it is built at the point of writing this script needs the program to be able
to print directly to a file
"""

parser = argparse.ArgumentParser(description=program_description)
parser.add_argument('-i', '--input', help='The input argument', required=True)
parser.add_argument('-o', '--output', help='The output argument', required=True)
parser.add_argument('--fasttree_path', help='The path for FastTree executable', required=True)
args = parser.parse_args()

out_fh = open(args.output, 'w')

process = subprocess.Popen([args.fasttree_path, '-nt', args.input], stdout=out_fh)
process.wait()

out_fh.close()
