#!/usr/bin/env python
# -*- coding: utf-8 -*-


from simple_idml.indesign import indesign
from simple_idml.commands import InDesignSoapCommand


class InDesignCloseAllDocs(InDesignSoapCommand):
    usage = "usage: %prog"
    version = "%prog 0.90"
    description = "SOAP call to a InDesignServer to close all documents."

    def execute(self):
        super(InDesignCloseAllDocs, self).execute()
        indesign.close_all_documents(self.options.url, self.options.client_workdir, self.options.server_workdir,
                                     self.options.server_path_style, self.ftp_params)


def main():
    command = InDesignCloseAllDocs()
    command.execute()


if __name__ == "__main__":
    main()
