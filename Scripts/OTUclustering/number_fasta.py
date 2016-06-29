#!/usr/bin/python3

__author__ = 'jakob'

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
