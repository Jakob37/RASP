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
import zipfile
import os

program_description = """
Script able to compress a folder into a .zip-file
"""


def main():

    print('RUNNING')
    args = parse_arguments()
    compress_folder_to_zip_file(args.input, args.output)


def parse_arguments():

    """Parses command line arguments"""

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('-i', '--input', help='Accepts multiple files divided by a space', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()
    return args


def compress_folder_to_zip_file(input_file, zip_out_fp):

    """Takes a input folder, and creates a zipped output"""

    print("\nZIPPING! input: {} output: {}".format(input_file, zip_out_fp))

    zf = zipfile.ZipFile(zip_out_fp, mode='w')
    try:
        print('Adding inputted file..')
        zip_folder_name = zip_out_fp.split('/')[-1].split('.')[0]
        zipdir(input_file, zf, zip_folder_name)
        #zf.write(input_file)
    finally:
        print('Closing..')
        zf.close()


def zipdir(folder_path, zip_file, internal_folder_name):

    """
    Zip-compress entire folder
    folder_path - Path of folder
    zip_file - An zipfile object to which the files should be written
    """

    for root, dirs, files in os.walk(folder_path):

        for f in files:

            filename = os.path.join(root, f)

            f_with_internal_sub = internal_folder_name + '/' + f

            # arcname is the name used in the archive
            zip_file.write(filename, arcname=f_with_internal_sub)


if __name__ == '__main__':
    main()