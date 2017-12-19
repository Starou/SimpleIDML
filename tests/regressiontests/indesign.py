# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
from builtins import object
from builtins import open
from builtins import str
import glob
import json
import mock
import os
import shutil
import unittest
import zipfile
from io import BytesIO
from simple_idml.indesign import indesign
from suds.client import ServiceSelector
from urllib.request import OpenerDirector

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
SOAP_DIR = os.path.join(CURRENT_DIR, "SOAP")

# Client and server are the same machine here.
CLIENT_WORKDIR = os.path.join(CURRENT_DIR, "workdir")
SERVER_WORKDIR = os.path.join(CURRENT_DIR, "workdir")


class InDesignTestCase(unittest.TestCase):
    def setUp(self):
        super(InDesignTestCase, self).setUp()
        # although 'future' wraps urllib2 we still need to mock urllib2.
        import sys
        if sys.version_info.major == 2:
            self.u2open_patcher = mock.patch('urllib2.OpenerDirector')
        else:
            self.u2open_patcher = mock.patch('urllib.request.OpenerDirector')
        self.u2open_mock = self.u2open_patcher.start()
        self.u2open_mock.side_effect = OpenerDirectorMock

        self.runscript_patcher = mock.patch('suds.client.ServiceSelector')
        self.runscript_mock = self.runscript_patcher.start()
        self.runscript_mock.side_effect = ServiceSelectorMock

        for f in glob.glob(os.path.join(CLIENT_WORKDIR, "*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        if not (os.path.exists(CLIENT_WORKDIR)):
            os.makedirs(CLIENT_WORKDIR)

    def tearDown(self):
        self.u2open_patcher.stop()
        self.runscript_patcher.stop()

    def test_save_as(self):
        responses = indesign.save_as(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                                     [{"fmt": "indd"}],
                                     "http://url-to-indesign-server:8080",
                                     CLIENT_WORKDIR, SERVER_WORKDIR,
                                     indesign_server_path_style="posix")

        self.assertTrue(self.runscript_mock.called)
        self.assertEqual(len(responses), 1)
        self.assertEqual(json.loads(responses[0].decode('utf-8')), {
            "script": "save_as.jsx",
            "extra_params": {},
            "dst": "4-pagesTMP.indd"
        })

        responses = indesign.save_as(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                                     [{"fmt": "pdf",
                                       "params": {
                                           "colorSpace": "CMYK",
                                           "standartsCompliance": "1A2003",
                                       }},
                                      {"fmt": "jpeg"},
                                      {"fmt": "zip"}],
                                     "http://url-to-indesign-server:8080",
                                     CLIENT_WORKDIR, SERVER_WORKDIR,
                                     indesign_server_path_style="posix")
        self.assertTrue(self.runscript_mock.called)
        self.assertEqual(len(responses), 3)
        self.assertEqual(json.loads(responses[0].decode('utf-8')),
                         {"extra_params": {"colorSpace": "CMYK", "format": "pdf", "standartsCompliance": "1A2003"},
                          "script": "export.jsx", "dst": "4-pagesTMP.pdf"})
        self.assertEqual(json.loads(responses[1].decode('utf-8')),
                         {"dst": "4-pagesTMP.jpeg", "extra_params": {"format": "jpeg"}, "script": "export.jsx"})
        zip_buf = BytesIO()
        zip_buf.write(responses[2])
        self.assertTrue(zipfile.is_zipfile(zip_buf))

    def test_close_all_documents(self):
        script = indesign.CloseAllDocuments("http://url-to-indesign-server:8080",
                                            CLIENT_WORKDIR, SERVER_WORKDIR,
                                            server_path_style="posix")
        script.execute()
        self.assertTrue(self.runscript_mock.called)

        script = indesign.CloseAllDocuments("http://url-to-indesign-server:8080",
                                            CLIENT_WORKDIR, SERVER_WORKDIR,
                                            server_path_style="windows")
        script.execute()
        self.assertTrue(self.runscript_mock.called)


class OpenerDirectorMock(OpenerDirector):
    def open(self, fullurl=None, data=None, timeout=None):
        url = fullurl.get_full_url()
        if os.path.basename(url) == 'service?wsdl':
            return open(os.path.join(SOAP_DIR, 'indesign-service.xml'), "r")


class SoapResponse(object):
    def __init__(self, errorNumber=0):
        self.errorNumber = errorNumber


class ServiceSelectorMock(ServiceSelector):
    def RunScript(self, params):
        script = os.path.basename(params['scriptFile'])
        script_args = dict([(p["name"], p["value"]) for p in params['scriptArgs']])
        if script in [indesign.SaveAs.javascript_basename, indesign.Export.javascript_basename,
                      indesign.PackageForPrint.javascript_basename]:
            script_args.pop("source")
            dst_filename = script_args.pop("destination")
            extra_params = script_args
            if script == indesign.PackageForPrint.javascript_basename:
                os.mkdir(dst_filename)  # Create the destination dir.
                dst_filename = "%s.zip" % dst_filename

            # Create the file in workdir and write something testable in it.
            with open(dst_filename, "w+") as f:
                json_str = json.dumps({'script': script,
                                       'dst': os.path.basename(dst_filename),
                                       'extra_params': extra_params})
                f.write(str(json_str))
        elif script == indesign.CloseAllDocuments.javascript_basename:
            pass

        return SoapResponse()


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(InDesignTestCase)
    return suite
