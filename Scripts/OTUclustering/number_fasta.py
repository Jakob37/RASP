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
import re

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="The input file", required=True)
parser.add_argument("-o", "--output", help="The output file path", required=True)
parser.add_argument("-l", "--label", help="A base name for the fastas (XX1, XX2..)", default="")
args = parser.parse_args()

input_fh = open(args.input, "r")
output_fh = open(args.output, "w")

number = 1
for line in input_fh:

    if line.startswith(">"):
        line = ">" + args.label + str(number) + "\n"
        number += 1

    print(line, end="", file=output_fh)

input_fh.close()
output_fh.close()
