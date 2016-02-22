# -*- coding: utf-8 -*-

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import glob
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "scripts")
SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), 'src')

PYTHON_EXE = sys.executable
if platform.system() == "Windows":
    PYTHON_EXE = "python.exe"


class CreatePackageTestCase(unittest.TestCase):
    def setUp(self):
        super(CreatePackageTestCase, self).setUp()
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        if not (os.path.exists(OUTPUT_DIR)):
            os.makedirs(OUTPUT_DIR)

        self.watch_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.watch_dir)

    @unittest.skipIf((platform.system() == "Windows"), u"test skipped on Windows (needs fix).")
    def test_create_package_from_dir(self):
        flat_package_path = os.path.join(IDMLFILES_DIR,
                                         "article-1photo.idml Folder")
        destination_path = os.path.join(OUTPUT_DIR, "article-1photo_2.idml")
        script_path = os.path.join(SRC_DIR, 'scripts',
                                   'simpleidml_create_package_from_dir.py')
        stdout, stderr = subprocess.Popen([
            PYTHON_EXE, script_path, flat_package_path, destination_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={
            'PYTHONPATH': SRC_DIR,
        }).communicate()
        if stderr:
            print(stderr.decode())
        self.assertEqual(os.listdir(OUTPUT_DIR), ['article-1photo_2.idml'])


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(CreatePackageTestCase)
    return suite
