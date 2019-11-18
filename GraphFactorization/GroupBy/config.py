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
    'endpoint_url',
    type=str,
    help='SPARQL Endpoint URL'
)
parser.add_argument(
    'class_property_file_name',
    type=str,
    help='str, class and property list file name'
)
parser.add_argument(
    'starList_folder_name',
    type=str,
    help='str, Stars list file name'
)
parser.add_argument(
    'instances_folder',
    type=str,
    help='str, output folder name to store total class instances'
)
parser.add_argument(
    'result_folder',
    type=str,
    help='str, output folder name'
)