#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_idml.commands import InDesignSoapCommand
from simple_idml.indesign import indesign


class InDesignListProfiles(InDesignSoapCommand):
    description = """List the available joboptions files on a server (in an exception message...) """

    def execute(self):
        super(InDesignListProfiles, self).execute()
        indesign.list_profiles(self.args.url, self.args.client_workdir, self.args.server_workdir,
                               self.args.server_path_style, self.ftp_params)

    def set_suds_logging(self):
        self.args.verbose = True
        super(InDesignListProfiles, self).set_suds_logging()


def main():
    command = InDesignListProfiles()
    command.execute()


if __name__ == "__main__":
    main()
