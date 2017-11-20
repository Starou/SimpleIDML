#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
from simple_idml.indesign import indesign
from simple_idml.commands import InDesignSoapCommand


class InDesignCloseAllDocs(InDesignSoapCommand):
    usage = "usage: %prog"
    version = "%prog 0.90"
    description = "SOAP call to a InDesignServer to close all documents."

    def execute(self):
        (options, args) = self.parser.parse_args()

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


def main():
    command = InDesignCloseAllDocs()
    command.execute()


if __name__ == "__main__":
    main()
