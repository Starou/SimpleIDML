# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser


class InDesignSoapCommand(object):
    def __init__(self):
        self.parser = OptionParser(usage=self.usage, version=self.version, description=self.description)
        self.parser.add_option("-u", "--url", default="http://127.0.0.1:8082",
                               help=u"InDesign Server url.")
        self.parser.add_option("--client-workdir", dest="client_workdir", default="/tmp",
                               help=("Directory where temporary files are written, as seen by the SOAP client."
                                     " This could be a FTP path."))
        self.parser.add_option("--server-workdir", dest="server_workdir", default="/tmp",
                               help="Directory where temporary files are written, as seen by the InDesign server.")
        self.parser.add_option("--server-path-style", dest="server_path_style", default="posix",
                               help="[posix|windows] according to the OS running InDesign Server.")
        self.parser.add_option("--no-clean-workdir", dest="no_clean_workdir", action="store_true", default=False,
                               help="Do not clean the working directory when finished.")
        self.parser.add_option("--ftp-url", dest="ftp_url", default="",
                               help=("The FTP server for the workir."
                                     " It must be on the filesystem of the InDesign Server."))
        self.parser.add_option("--ftp-user", dest="ftp_user", default="")
        self.parser.add_option("--ftp-password", dest="ftp_password", default="")
        self.parser.add_option("--ftp-passive", dest="ftp_passive", action="store_true", default=False)
        self.parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                               default=False)

    def execute(self):
        self.parse_options()
        self.set_ftp_params()
        self.set_suds_logging()

    def parse_options(self):
        (self.options, self.args) = self.parser.parse_args()

    def set_ftp_params(self):
        self.ftp_params = None
        if self.options.ftp_url:
            self.ftp_params = {
                'auth': (self.options.ftp_url, self.options.ftp_user, self.options.ftp_password),
                'passive': self.options.ftp_passive,
            }

    def set_suds_logging(self):
        if self.options.verbose:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
