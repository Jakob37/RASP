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
import gzip
import tarfile

program_description = """
Script able to decompress to .tar.gz and .gz-files
Takes a string with full compressed file paths as input, and decompress them into
the target output_base directory
"""


def main():

    args = parse_arguments()
    if args.decompression_mode == 'gz':
        extract_gz_file(args.input, args.output_base, args.delimiter)
    elif args.decompression_mode == 'targz':
        extract_tar_gz_archive(args.input, args.output)
    else:
        raise ValueError('Unknown decompression mode encountered')


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='Accepts multiple files divided by the separator', required=True)
    parser.add_argument('-o', '--output_base', required=True)
    parser.add_argument('-c', '--decompression_mode', choices=['gz', 'targz'], default='gz')
    parser.add_argument('-d', '--delimiter', default=',')
    args = parser.parse_args()
    return args


def extract_gz_file(input_line, output_base, delim):

    """Takes a .gz file and decompress it into provided output filepath"""

    multiple_gz_input_fp = input_line.split(delim)

    for input_gz_fp in multiple_gz_input_fp:

        with gzip.open(input_gz_fp, 'rb') as file_in:
            content = file_in.read()
            with open(output_base + '.'.join(input_gz_fp.split('/')[-1].split('.')[:-1]), 'wb') as file_out:
                file_out.write(content)


def extract_tar_gz_archive(input_archive, output_folder):

    """Takes a .tar.gz archive and decompresses it into target folder"""

    tfile = tarfile.open(input_archive, 'r:gz')
    tfile.extractall(output_folder)

if __name__ == '__main__':
    main()
