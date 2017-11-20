#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A convenient script to create an IDML package from a flat directory.
"""

import argparse
from simple_idml.extras import create_idml_package_from_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', metavar='SOURCE_DIRECTORY', help="Directory to package as IDML")
    parser.add_argument('destination', metavar='DESTINATION', help="IDML filename to create from SOURCE dir")
    args = parser.parse_args()

    create_idml_package_from_dir(args.source, args.destination)


if __name__ == "__main__":
    main()
