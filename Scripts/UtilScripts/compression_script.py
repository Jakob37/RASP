#!/usr/bin/env python3
__author__ = "Jakob Willforss"

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