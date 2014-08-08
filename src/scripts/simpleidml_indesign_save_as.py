#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOAP call to a InDesignServer to save a file in another format.
"""

import os
from optparse import OptionParser
from simple_idml.indesign import indesign


def main():
    usage = "usage: %prog /path/to/source-file /path/to/destination-file"
    version = "%prog 0.1"
    parser = OptionParser(usage=usage, version=version, description=__doc__)
    parser.add_option("-u", "--url", default="http://127.0.0.1:8082",
                      help=u"InDesign Server url.")
    parser.add_option("-w", "--workdir", default="/tmp",
                      help="InDesign Server directory where temporary files are written.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False)

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("You must provide the source file and the destination file paths as parameters")
    else:
        src, dst = args[0], args[1]
        fmt = os.path.splitext(dst)[1].replace(".", "")
        response = indesign.save_as(src, fmt, options.url, options.workdir)
        with open(dst, mode="w+") as fobj:
            fobj.write(response)


if __name__ == "__main__":
    main()
