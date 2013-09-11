# -*- coding: utf-8 -*-

import os
import sys
import shutil
import tempfile
import glob
import unittest
import json
import re

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "scripts")


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

    def test_create_package_from_dir(self):
        flat_package_filename = os.path.join(IDMLFILES_DIR, "\"article-1photo.idml Folder\"")
        destination_filename = os.path.join(OUTPUT_DIR, "article-1photo_2.idml")

        args = [flat_package_filename, destination_filename]
        os.popen(('export PYTHONPATH="../src":$PYTHONPATH && '
                  'python ../src/scripts/simpleidml_create_package_from_dir.py %s' % " ".join(args)), "w")

        self.assertEqual(os.listdir(OUTPUT_DIR), ['article-1photo_2.idml'])


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(CreatePackageTestCase)
    return suite
