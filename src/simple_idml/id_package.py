# -*- coding: utf-8 -*-

import re
import zipfile
from copy import deepcopy

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


def merge_font_lst(font_lst_files):
    """This function is useful to generate the ADOBE_FONT_LIST file from several ones. """
    font_lst_files = deepcopy(font_lst_files)
    filename_out, content_out = None, []

    # Search for the first Suite case file not empty.
    while(font_lst_files):
        first = font_lst_files.pop(0)
        filename_out = first[0]
        if first[1] != "":
            content_out = [first[1]]
            break

    for filename, content in font_lst_files:
        if content != "":
            # Remove the header (3 first lines).
            lines = content.split("\n")[3:]
            content_out.append("\n".join(lines))

    return filename_out, "\n".join(content_out)
