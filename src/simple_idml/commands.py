# -*- coding: utf-8 -*-

from builtins import object
import argparse
import logging


class InDesignSoapCommand(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.description,
                                             formatter_class=argparse.RawDescriptionHelpFormatter)
        self.parser.add_argument("-u", "--url", default="http://127.0.0.1:8082", help=u"InDesign Server SOAP url")
        self.parser.add_argument("--client-workdir", default="/tmp",
                                 help=("Directory where temporary files are written, as seen by the SOAP client."
                                     " This could be a FTP path."))
        self.parser.add_argument("--server-workdir", default="/tmp",
                                 help="Directory where temporary files are written, as seen by the InDesign server.")
        self.parser.add_argument("--server-path-style", default="posix",
                                 choices=['posix', 'windows'], help="The OS type running InDesign Server")
        self.parser.add_argument("--no-clean-workdir", action="store_true", default=False,
                                 help="Do not clean the working directory when finished")
        self.parser.add_argument("--ftp-url",
                                 help="The FTP server for the workdir. It must be on the filesystem of the InDesign Server.")
        self.parser.add_argument("--ftp-user", default="")
        self.parser.add_argument("--ftp-password", default="")
        self.parser.add_argument("--ftp-passive", action="store_true", default=False)
        self.parser.add_argument("-v", "--verbose", action="store_true", default=False)

    def execute(self):
        self.parse_options()
        self.set_ftp_params()
        self.set_suds_logging()

    def parse_options(self):
        self.args = self.parser.parse_args()

    def set_ftp_params(self):
        self.ftp_params = None
        if self.args.ftp_url:
            self.ftp_params = {
                'auth': (self.args.ftp_url, self.args.ftp_user, self.args.ftp_password),
                'passive': self.args.ftp_passive,
            }

    def set_suds_logging(self):
        if self.args.verbose:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
