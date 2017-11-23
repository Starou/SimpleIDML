# -*- coding: utf-8 -*-

import os
import shutil
import glob
import unittest
import zipfile
from simple_idml.extras import create_idml_package_from_dir

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs")

class ExtrasTestCase(unittest.TestCase):
    def setUp(self):
        super(ExtrasTestCase, self).setUp()
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        if not (os.path.exists(OUTPUT_DIR)):
            os.makedirs(OUTPUT_DIR)

    def test_create_package_from_dir(self):

        src_dir = os.path.join(IDMLFILES_DIR, "article-1photo")
        destination = os.path.join(OUTPUT_DIR, "article-1photo.idml")

        create_idml_package_from_dir(src_dir, destination)
        self.assertTrue(os.path.exists(destination))
        with zipfile.ZipFile(destination, 'r') as package:
            self.assertEqual(set(package.namelist()),
                             set(['mimetype', 'Stories/Story_u188.xml', 'Spreads/Spread_ud6.xml',
                                  'XML/BackingStory.xml', 'XML/Tags.xml', 'Resources/Graphic.xml',
                                  'Stories/Story_u1db.xml', 'Resources/Fonts.xml', 'META-INF/metadata.xml',
                                  'designmap.xml', 'Stories/Story_u19f.xml', 'META-INF/container.xml',
                                  'MasterSpreads/MasterSpread_ua5.xml', 'Resources/Preferences.xml',
                                  'Resources/Styles.xml', 'XML/Mapping.xml']))

        self.assertRaises(IOError, create_idml_package_from_dir, src_dir, destination)
        self.assertRaises(IOError, create_idml_package_from_dir, src_dir + "-foo", destination.replace(".idml",
                                                                                                       "-2.idml"))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ExtrasTestCase)
    return suite

