from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from config import parser
#from .gspan import gSpan
from fsgpdetection import fgpDetection
def main(FLAGS=None):
    """Run FGPDetection."""

    if FLAGS is None:
        FLAGS, _ = parser.parse_known_args(args=sys.argv[1:])

    if not os.path.exists(FLAGS.list_file_name):
        print('{} does not exist.'.format(FLAGS.list_file_name))
        sys.exit()

    if not os.path.exists(FLAGS.class_property_file_name):
        print('{} does not exist.'.format(FLAGS.class_property_file_name))
        sys.exit()

    if not os.path.exists(FLAGS.instances_file):
        print('{} does not exist.'.format(FLAGS.instances_file))
        sys.exit()

    fgpd = fgpDetection(
        list_file_name=FLAGS.list_file_name,
        class_property_file_name =FLAGS.class_property_file_name,
        frequent_stars_folder=FLAGS.frequent_stars_folder,
        output_folder_name=FLAGS.output_folder_name,
        min_support=FLAGS.min_support,
        instances_file=FLAGS.instances_file,
        json_folder=FLAGS.json_folder
    )
    print("run algorithm",FLAGS.list_file_name)
    fgpd.run()
    fgpd.time_stats()
    return fgpd


if __name__ == '__main__':
    main()