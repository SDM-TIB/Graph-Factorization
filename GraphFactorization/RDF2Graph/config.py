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
    'rdf_folder_name',
    type=str,
    help='str, rdf folder name'
)
parser.add_argument(
    'rdf_format',
    type=str,
    help='RDF format'
)
parser.add_argument(
    'class_property_file_name',
    type=str,
    help='str, class and property list file name'
)
parser.add_argument(
    'graph_folder_name',
    type=str,
    help='str, graph folder name'
)
parser.add_argument(
    'output_folder_name',
    type=str,
    help='str, output folder name'
)