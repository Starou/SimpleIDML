#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_idml.commands import InDesignSoapCommand
from simple_idml.indesign.indesign import CloseAllDocuments


class InDesignCloseAllDocs(InDesignSoapCommand):
    description = "SOAP call to a InDesignServer to close all documents."

    def execute(self):
        super(InDesignCloseAllDocs, self).execute()
        script = CloseAllDocuments(self.args.url, self.args.client_workdir, self.args.server_workdir,
                                   self.args.server_path_style, self.ftp_params)
        script.execute()


def main():
    command = InDesignCloseAllDocs()
    command.execute()


if __name__ == "__main__":
    main()
