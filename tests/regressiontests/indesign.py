# -*- coding: utf-8 -*-

import glob
import mock
import os
import shutil
import unittest
import zipfile
from cStringIO import StringIO
from simple_idml.indesign import indesign
from suds.client import ServiceSelector
from urllib2 import OpenerDirector

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
SOAP_DIR = os.path.join(CURRENT_DIR, "SOAP")

# Client and server are the same machine here.
CLIENT_WORKDIR = os.path.join(CURRENT_DIR, "workdir")
SERVER_WORKDIR = os.path.join(CURRENT_DIR, "workdir")


class InDesignTestCase(unittest.TestCase):
    def setUp(self):
        super(InDesignTestCase, self).setUp()
        self.u2open_patcher = mock.patch('urllib2.OpenerDirector')
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
        self.assertEqual(responses, ['save_as.jsx, 4-pagesTMP.indd, {}'])

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
        self.assertEqual(responses[:2], [
            "export.jsx, 4-pagesTMP.pdf, {'colorSpace': 'CMYK', 'standartsCompliance': '1A2003', 'format': 'pdf'}",
            "export.jsx, 4-pagesTMP.jpeg, {'format': 'jpeg'}"
        ])
        zip_buf = StringIO()
        zip_buf.write(responses[2])
        self.assertTrue(zipfile.is_zipfile(zip_buf))

    def test_close_all_documents(self):
        indesign.close_all_documents("http://url-to-indesign-server:8080",
                                     CLIENT_WORKDIR, SERVER_WORKDIR,
                                     indesign_server_path_style="posix")
        self.assertTrue(self.runscript_mock.called)

        indesign.close_all_documents("http://url-to-indesign-server:8080",
                                     CLIENT_WORKDIR, SERVER_WORKDIR,
                                     indesign_server_path_style="windows")
        self.assertTrue(self.runscript_mock.called)


class OpenerDirectorMock(OpenerDirector):
    def open(self, fullurl=None, data=None, timeout=None):
        url = fullurl.get_full_url()
        if os.path.basename(url) == 'service?wsdl':
            return open(os.path.join(SOAP_DIR, 'indesign-service.xml'), "r")


class ServiceSelectorMock(ServiceSelector):
    def RunScript(self, params):
        script = os.path.basename(params['scriptFile'])
        script_args = dict([(p["name"], p["value"]) for p in params['scriptArgs']])
        if script in indesign.JS_SAVE_AS_SCRIPTS:
            script_args.pop("source")
            dst_filename = script_args.pop("destination")
            extra_params = script_args
            if script == indesign.JS_PACKAGE_SCRIPT:
                os.mkdir(dst_filename)  # Create the destination dir.
                dst_filename = "%s.zip" % dst_filename

            # Create the file in workdir and write something testable in it.
            fobj = open(dst_filename, "w+")
            fobj.write("%s, %s, %s" % (script,
                                       os.path.basename(dst_filename),
                                       extra_params))
        elif script in indesign.JS_CLOSE_ALL_SCRIPT:
            pass


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(InDesignTestCase)
    return suite
