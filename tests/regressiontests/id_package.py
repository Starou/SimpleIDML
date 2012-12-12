# -*- coding: utf-8 -*-

import os
import unittest

from simple_idml.id_package import ZipInDesignPackage

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")


class ZipInDesignPackageTestCase(unittest.TestCase):
    def test_get_font_list(self):
        archive_name = os.path.join(IDMLFILES_DIR, "article-1photo-package.zip")
        zip_indesign_package = ZipInDesignPackage(archive_name, "r")
        self.assertEqual(
            set(zip_indesign_package.get_font_list()),
            set([('AdobeFnt13.lst', 'article-1photo-package/Document fonts/AdobeFnt13.lst'),
                 ('._AdobeFnt13.lst', '__MACOSX/article-1photo-package/Document fonts/._AdobeFnt13.lst'),
                 ('MinionPro-Bold.otf', 'article-1photo-package/Document fonts/MinionPro-Bold.otf'),
                 ('MinionPro-It.otf', 'article-1photo-package/Document fonts/MinionPro-It.otf'),
                 ('MinionPro-Regular.otf', 'article-1photo-package/Document fonts/MinionPro-Regular.otf')])
        )


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ZipInDesignPackageTestCase)
    return suite
