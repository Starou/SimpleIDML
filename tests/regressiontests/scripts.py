# -*- coding: utf-8 -*-

import os
import platform
import shutil
import tempfile
import glob
import unittest

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "scripts")

PYTHON_EXE = "python"
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
        flat_package_filename = "\"%s\"" % os.path.join(IDMLFILES_DIR, "article-1photo.idml Folder")
        destination_filename = "\"%s\"" % os.path.join(OUTPUT_DIR, "article-1photo_2.idml")
        args = [flat_package_filename, destination_filename]

        os.popen(('export PYTHONPATH="%(path)s":$PYTHONPATH && '
                  '%(python)s %(script)s %(args)s' % {
                      'path': os.path.join('..', 'src'),
                      'python': PYTHON_EXE,
                      'script': os.path.join('..', 'src', 'scripts', 'simpleidml_create_package_from_dir.py'),
                      'args': " ".join(args)
                  }), "w")

        self.assertEqual(os.listdir(OUTPUT_DIR), ['article-1photo_2.idml'])


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(CreatePackageTestCase)
    return suite
