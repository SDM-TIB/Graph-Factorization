"""The main program that runs rdf2graph."""
# -*- coding=utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from config import parser
from rdfclass2graph import rdfClass2Graph


def main(FLAGS=None):
    """Run gSpan."""

    if FLAGS is None:
        FLAGS, _ = parser.parse_known_args(args=sys.argv[1:])

    if not os.path.exists(FLAGS.rdf_folder_name):
        print('{} does not exist.'.format(FLAGS.rdf_folder_name))
        sys.exit()

    if not os.path.exists(FLAGS.class_property_file_name):
        print('{} does not exist.'.format(FLAGS.class_property_file_name))
        sys.exit()

    gs = rdfClass2Graph(
        rdf_folder_name=FLAGS.rdf_folder_name,
        rdf_format=FLAGS.rdf_format,
        class_property_file_name=FLAGS.class_property_file_name,
        graph_folder_name=FLAGS.graph_folder_name,
        output_folder_name=FLAGS.output_folder_name
    )

    gs.run()
    gs.time_stats()
    return gs


if __name__ == '__main__':
    main()
