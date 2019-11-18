from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from config import parser
from collectstars import collectStars
def main(FLAGS=None):
    """Run collectStars."""

    if FLAGS is None:
        FLAGS, _ = parser.parse_known_args(args=sys.argv[1:])

    if not os.path.exists(FLAGS.class_property_file_name):
        print('{} does not exist.'.format(FLAGS.class_property_file_name))
        sys.exit()

    collstars = collectStars(
        endpoint_url=FLAGS.endpoint_url,
        class_property_file_name=FLAGS.class_property_file_name,
        starList_folder_name=FLAGS.starList_folder_name,
        instances_folder=FLAGS.instances_folder,
        result_folder=FLAGS.result_folder
    )
    print("run algorithm")
    collstars.run()
    collstars.time_stats()
    return collstars


if __name__ == '__main__':
    main()