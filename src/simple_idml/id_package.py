# -*- coding: utf-8 -*-

import zipfile
import re

DOCUMENT_FONT_DIR = "Document fonts"
DOCUMENT_LINK_DIR = "Links"
ADOBE_FONT_LIST = "AdobeFnt13.lst"


class ZipInDesignPackage(zipfile.ZipFile):
    """ Wrapper over a zipped InDesign Package.

       The Package is obtained with the action `File > Package' from InDesign menu. """
    
    # Maybe we should exlude '__MACOSX/foo/Document fonts/._AdobeFnt13.lst'.
    # Anyway, do not exclude the whole __MACOSX since it contains font fork resources.
    rx_font = re.compile("(?P<root_dir>.*)/%s/(?P<font_name>.+)" % DOCUMENT_FONT_DIR)
    rx_link = re.compile("(?P<root_dir>.*)/%s/(?P<link_name>.+)" % DOCUMENT_LINK_DIR)

    def get_font_list(self):
        return [(self.rx_font.match(filename).groupdict()["font_name"], filename)
                for filename in self.namelist() if self.rx_font.match(filename)]

    def get_link_list(self):
        return [(self.rx_link.match(filename).groupdict()["link_name"], filename)
                for filename in self.namelist() if self.rx_link.match(filename)]
