# -*- coding: utf-8 -*-

import os
import unittest

from simple_idml.id_package import ZipInDesignPackage
from simple_idml.id_package import merge_font_lst

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


class IDPackageTestCase(unittest.TestCase):
    def test_merge_font_lst(self):

        font_suitecases = [
            ("output/Document fonts/AdobeFnt13.lst", ""),
            ("output/Document fonts/AdobeFnt13.lst", ""),
            ("output/Document fonts/AdobeFnt13.lst", ""),
        ]

        filename, content = merge_font_lst(font_suitecases)
        self.assertEqual(content, "")

        # The first file may not reference any font.
        font_suitecases = [
("output/Document fonts/AdobeFnt13.lst", ""),
("output/Document fonts/AdobeFnt13.lst",
 """%!Adobe-FontList 1.13
%Locale:0x409

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:Times-Roman
OutlineFileName:\Times-Roman
ResourceID:20
MacStyle:0
FileLength:12882
FileModTime:1342371272
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:Times-Roman
FamilyName:Times
StyleName:Roman
MenuName:Times
StyleBits:0
WeightClass:400
WidthClass:5
AngleClass:0
FullName:Times Roman
WritingScript:Roman
OutlineFileName:\TimesRom
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:34006
FileModTime:1342371272
DesignSize:-1
%EndFont

"""),
("output/Document fonts/AdobeFnt13.lst",
"""%!Adobe-FontList 1.13
%Locale:0x409

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:AGaramond-BoldItalic
OutlineFileName:\AGaramond-BoldItalic.ECR
ResourceID:14570
MacStyle:0
FileLength:10327
FileModTime:1341477738
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:AGaramond-Regular
OutlineFileName:\AGaramond-Regular.ECR
ResourceID:14562
MacStyle:0
FileLength:18702
FileModTime:1341477705
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:AGaramond-BoldItalic
FamilyName:Adobe Garamond
StyleName:Bold Italic
MenuName:AGaramond Bold
StyleBits:3
WeightClass:700
WidthClass:5
AngleClass:1
FullName:Adobe Garamond Bold Italic
WritingScript:Roman
OutlineFileName:\AGarBolIta
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:45072
FileModTime:1341477738
DesignSize:-1
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:AGaramond-Regular
FamilyName:Adobe Garamond
StyleName:Regular
MenuName:AGaramond
StyleBits:0
WeightClass:400
WidthClass:5
AngleClass:0
FullName:Adobe Garamond Regular
WritingScript:Roman
OutlineFileName:\AGarReg
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:45376
FileModTime:1341477705
DesignSize:-1
%EndFont

""")]
        filename, content = merge_font_lst(font_suitecases)
        self.assertEqual(content,
"""%!Adobe-FontList 1.13
%Locale:0x409

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:Times-Roman
OutlineFileName:\Times-Roman
ResourceID:20
MacStyle:0
FileLength:12882
FileModTime:1342371272
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:Times-Roman
FamilyName:Times
StyleName:Roman
MenuName:Times
StyleBits:0
WeightClass:400
WidthClass:5
AngleClass:0
FullName:Times Roman
WritingScript:Roman
OutlineFileName:\TimesRom
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:34006
FileModTime:1342371272
DesignSize:-1
%EndFont


%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:AGaramond-BoldItalic
OutlineFileName:\AGaramond-BoldItalic.ECR
ResourceID:14570
MacStyle:0
FileLength:10327
FileModTime:1341477738
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:AGaramond-Regular
OutlineFileName:\AGaramond-Regular.ECR
ResourceID:14562
MacStyle:0
FileLength:18702
FileModTime:1341477705
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:AGaramond-BoldItalic
FamilyName:Adobe Garamond
StyleName:Bold Italic
MenuName:AGaramond Bold
StyleBits:3
WeightClass:700
WidthClass:5
AngleClass:1
FullName:Adobe Garamond Bold Italic
WritingScript:Roman
OutlineFileName:\AGarBolIta
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:45072
FileModTime:1341477738
DesignSize:-1
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:AGaramond-Regular
FamilyName:Adobe Garamond
StyleName:Regular
MenuName:AGaramond
StyleBits:0
WeightClass:400
WidthClass:5
AngleClass:0
FullName:Adobe Garamond Regular
WritingScript:Roman
OutlineFileName:\AGarReg
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:45376
FileModTime:1341477705
DesignSize:-1
%EndFont

""")

    def test_merge_font_lst_1file(self):
        font_suitecases = [
            ('21283009/Document fonts/AdobeFnt13.lst',
"""%!Adobe-FontList 1.13
%Locale:0x409

%BeginFont
Handler:DirectoryHandler
FontType:Suitcase
FontName:AGaramond-Bold
OutlineFileName:\\AGaramond-Bold.ECR
ResourceID:14571
MacStyle:0
FileLength:12909
FileModTime:1341477750
%EndFont

%BeginFont
Handler:DirectoryHandler
FontType:Type1
FontName:AGaramond-Bold
FamilyName:Adobe Garamond
StyleName:Bold
MenuName:AGaramond Bold
StyleBits:2
WeightClass:700
WidthClass:5
AngleClass:0
FullName:Adobe Garamond Bold
WritingScript:Roman
OutlineFileName:\\AGarBol
DataFormat:POSTResource
UsesStandardEncoding:yes
isCFF:no
FileLength:46237
FileModTime:1341477750
DesignSize:-1
%EndFont

""")
        ]
        filename, content = merge_font_lst(font_suitecases)
        self.assertEqual(content, '%!Adobe-FontList 1.13\n%Locale:0x409\n\n%BeginFont\nHandler:DirectoryHandler\nFontType:Suitcase\nFontName:AGaramond-Bold\nOutlineFileName:\\AGaramond-Bold.ECR\nResourceID:14571\nMacStyle:0\nFileLength:12909\nFileModTime:1341477750\n%EndFont\n\n%BeginFont\nHandler:DirectoryHandler\nFontType:Type1\nFontName:AGaramond-Bold\nFamilyName:Adobe Garamond\nStyleName:Bold\nMenuName:AGaramond Bold\nStyleBits:2\nWeightClass:700\nWidthClass:5\nAngleClass:0\nFullName:Adobe Garamond Bold\nWritingScript:Roman\nOutlineFileName:\\AGarBol\nDataFormat:POSTResource\nUsesStandardEncoding:yes\nisCFF:no\nFileLength:46237\nFileModTime:1341477750\nDesignSize:-1\n%EndFont\n\n')


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ZipInDesignPackageTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(IDPackageTestCase))
    return suite
