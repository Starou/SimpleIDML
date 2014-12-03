#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOAP call to a InDesignServer to close all documents.

"""

import logging
from optparse import OptionParser
from simple_idml.indesign import indesign


def main():
    usage = "usage: %prog"
    version = "%prog 0.90"
    parser = OptionParser(usage=usage, version=version, description=__doc__)
    parser.add_option("-u", "--url", default="http://127.0.0.1:8082",
                      help=u"InDesign Server url.")
    parser.add_option("--client-workdir", dest="client_workdir", default="/tmp",
                      help=("Directory where temporary files are written, as seen by the SOAP client."
                            " This could be a FTP path."))
    parser.add_option("--server-workdir", dest="server_workdir", default="/tmp",
                      help="Directory where temporary files are written, as seen by the InDesign server.")
    parser.add_option("--server-path-style", dest="server_path_style", default="posix",
                      help="[posix|windows] according to the OS running InDesign Server.")
    parser.add_option("--ftp-url", dest="ftp_url", default="",
                      help=("The FTP server for the workir."
                            " It must be on the filesystem of the InDesign Server."))
    parser.add_option("--ftp-user", dest="ftp_user", default="")
    parser.add_option("--ftp-password", dest="ftp_password", default="")
    parser.add_option("--ftp-passive", dest="ftp_passive", action="store_true", default=False)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False)

    (options, args) = parser.parse_args()

    ftp_params = None
    if options.ftp_url:
        ftp_params = {
            'auth': (options.ftp_url, options.ftp_user, options.ftp_password),
            'passive': options.ftp_passive,
        }

    if options.verbose:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)

    indesign.close_all_documents(options.url, options.client_workdir, options.server_workdir,
                                 options.server_path_style, ftp_params)


if __name__ == "__main__":
    main()
