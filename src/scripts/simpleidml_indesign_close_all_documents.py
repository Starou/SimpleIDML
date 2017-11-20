#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_idml.indesign import indesign
from simple_idml.commands import InDesignSoapCommand


class InDesignCloseAllDocs(InDesignSoapCommand):
    description = "SOAP call to a InDesignServer to close all documents."

    def execute(self):
        super(InDesignCloseAllDocs, self).execute()
        indesign.close_all_documents(self.args.url, self.args.client_workdir, self.args.server_workdir,
                                     self.args.server_path_style, self.ftp_params)


def main():
    command = InDesignCloseAllDocs()
    command.execute()


if __name__ == "__main__":
    main()
