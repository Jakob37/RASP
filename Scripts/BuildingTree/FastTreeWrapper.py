#!/usr/bin/python3

__author__ = 'jakob'

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

# process = subprocess.Popen(['/var/cgi-bin/PipelineFolder/Pipeline/Programs/FastTree', '-nt', args.input], stdout=out_fh)
process = subprocess.Popen([args.fasttree_path, '-nt', args.input], stdout=out_fh)
process.wait()

out_fh.close()