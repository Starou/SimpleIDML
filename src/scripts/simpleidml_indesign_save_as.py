#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOAP call to a InDesignServer to save a file in (an)other format(s).

Export PDF parameters
'''''''''''''''''''''

o Boolean parameters just need to be present to be set on:

    - colorBars, optimizePDF, cropMarks, pageInformationMarks,
        registrationMarks,


o String parameters:

    You can call a predifined preset (.joboptions file) with
    pdfExportPresetName:

    - pdfExportPresetName: [Press Quality], ...

    Or the the following parameters:

    - acrobatCompatibility: 4, 5, 6, 7 or 8
    - colorSpace: CMYK, iGry, rCMY, rRGB, cRGB or unFc
    - colorProfile (output > color > destination) and
        (output > PDF/X > profile): Generic CMYK Profile, ...
    - flattenerPresetName: [High resolution print], ...
    - standartsCompliance: 1A2001, 1A2003, 32002, 32003 or 42010
    - bleedTop, bleedBottom, bleedInside, bleedOutside: (float value)
    - pageMarksOffset: [0 to 72]
    - colorBitmapSampling: subSample, downSample or bicubicDownSample
    - colorBitmapQuality: minimum, low, medium, high, maximum, 4bits or 8bits
    - colorBitmapCompression: auto, jpeg, zip, jpeg2000 or autoJpeg2000
    - colorBitmapSamplingDPI: [9 to 2400]
    - grayscaleBitmapSampling: subSample, downSample or bicubicDownSample
    - grayscaleBitmapQuality: minimum, low, medium, high, maximum, 4bits or 8bits
    - grayscaleBitmapCompression: auto, jpeg, zip, jpeg2000 or autoJpeg2000
    - grayscaleBitmapSamplingDPI: [9 to 2400]
    - monochromeBitmapSampling: subSample, downSample or bicubicDownSample
    - monochromeBitmapCompression: CCIT3, CCIT4, zip, RLE
    - monochromeBitmapSamplingDPI: [9 to 2400]

"""

import locale
import logging
import os
import sys
from optparse import OptionParser
from simple_idml.indesign import indesign


def main():
    usage = ("usage: %prog /path/to/source-file"
             " \"/path/to/destination-fileA|colorsBars=1,colorSpace=cRGB;/path/to/destination-fileB\"")
    version = "%prog 0.1"
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
    parser.add_option("--no-clean-workdir", dest="no_clean_workdir", action="store_true", default=False,
                      help="Do not clean the working directory when finished.")
    parser.add_option("--ftp-url", dest="ftp_url", default="",
                      help=("The FTP server for the workir."
                            " It must be on the filesystem of the InDesign Server."))
    parser.add_option("--ftp-user", dest="ftp_user", default="")
    parser.add_option("--ftp-password", dest="ftp_password", default="")
    parser.add_option("--ftp-passive", dest="ftp_passive", action="store_true", default=False)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False)

    # Fix encoding first.
    encoding = locale.getpreferredencoding()
    for i, a in enumerate(sys.argv):
        sys.argv[i] = unicode(a.decode(encoding))

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("You must provide the source file and the destination file paths as parameters")
    else:
        src, destinations = args[0], args[1].split(";")

        def parse_destination_arg(arg):
            try:
                dest, params = arg.split("|")
            except ValueError:
                dest = arg
                params = {}
            else:
                params = dict([keyval.split("=") for keyval in params.split(",")])
            return {"fmt": os.path.splitext(dest)[1].replace(".", ""),
                    "params": params}

        formats = map(parse_destination_arg, destinations)

        ftp_params = None
        if options.ftp_url:
            ftp_params = {
                'auth': (options.ftp_url, options.ftp_user, options.ftp_password),
                'passive': options.ftp_passive,
            }

        if options.verbose:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)

        responses = indesign.save_as(src, formats, options.url, options.client_workdir,
                                     options.server_workdir, options.server_path_style,
                                     not options.no_clean_workdir, ftp_params)

        def _save_as(response, dst):
            with open(dst.split("|")[0], mode="w+") as fobj:
                fobj.write(response)

        map(_save_as, responses, destinations)


if __name__ == "__main__":
    main()
