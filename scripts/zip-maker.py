#!/usr/bin/env python3
import argparse
from os.path import basename
import sys
from zipfile import ZipFile, ZIP_DEFLATED


def zip_file(path):
    return ZipFile(path, mode='x', compression=ZIP_DEFLATED, compresslevel=9)


def create_zip(zip_path, file_path_pairs):
    with zip_file(zip_path) as zip:
        for file_path_pair in file_path_pairs:
            zip.write(file_path_pair[0], file_path_pair[1])


def parse_args(argv):
    parser = argparse.ArgumentParser(basename(argv[0]))
    parser.add_argument('--zip', help='zip file to be created', required=True)
    # nargs='+' is supposed to imply required=True
    parser.add_argument('--input-list', help='file paths to add to the zip', nargs='+', required=True)
    parser.add_argument('--output-list', help='destination paths in the zip', nargs='+', required=True)

    args = parser.parse_args(argv[1:])
    if len(args.input_list) != len(args.output_list):
        raise ValueError('Input and output lists must specify the same number of files')

    return args


def main(argv):
    args = parse_args(argv)
    create_zip(args.zip, zip(args.input_list, args.output_list))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
