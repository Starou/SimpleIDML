#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A convenient script to create an IDML package from a flat directory.
"""

from optparse import OptionParser
from simple_idml.extras import create_idml_package_from_dir


def main():
    usage = "usage: %prog /path/to/dir /path/to/destination.idml"
    version = "%prog 0.1"
    parser = OptionParser(usage=usage, version=version, description=__doc__)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("You must provide 2 parameters to the script ('/path/to/dir' and '/path/to/destination.idml')")
    else:
        create_idml_package_from_dir(args[0], args[1])


if __name__ == "__main__":
    main()
