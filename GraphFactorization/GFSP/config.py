"""Define some args."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse


def str2bool(s):
    """Convert str to bool."""
    return s.lower() not in ['false', 'f', '0', 'none', 'no', 'n']


parser = argparse.ArgumentParser()
parser.add_argument(
    'list_file_name',
    type=str,
    help='str, list file name'
)
parser.add_argument(
    'class_property_file_name',
    type=str,
    help='str, class and property list file name'
)
parser.add_argument(
    'frequent_stars_folder',
    type=str,
    help='str, output frequent stars folder name'
)
parser.add_argument(
    'output_folder_name',
    type=str,
    help='str, output folder name'
)
parser.add_argument(
    'instances_file',
    type=str,
    help='file containing total number of instances in the class'
)
parser.add_argument(
    'json_folder',
    type=str,
    help='str, output folder name to save json object containing class and properties involved in frequent star patterns'
)
parser.add_argument(
    '-s', '--min_support',
    type=int,
    default=5000,
    help='min support, default 5000'
)
