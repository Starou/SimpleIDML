# -*- coding: utf-8 -*-

import os, sys, shutil
import glob
import unittest
import codecs
import StringIO
from lxml import etree

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "simpleIDML_files")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "simpleIDML")


class SimpleIDMLTestCase(unittest.TestCase):
    def setUp(self):
        super(SimpleIDMLTestCase, self).setUp()
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*")):
            os.unlink(f)

    def test_idml_package(self):
        from simple_idml.idml import IDMLPackage
        idml_file = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        idml_file = IDMLPackage(idml_file)
        
        # Spreads.
        self.assertEqual(idml_file.spreads, [u'Spreads/Spread_ub6.xml',
                                             u'Spreads/Spread_ubc.xml',
                                             u'Spreads/Spread_uc3.xml'])

        # Stories.
        self.assertEqual(idml_file.stories, [u'Stories/Story_u139.xml',
                                             u'Stories/Story_u11b.xml',
                                             u'Stories/Story_u102.xml',
                                             u'Stories/Story_ue4.xml'])

        # XML Structure.
        self.assertEqual(etree.tostring(idml_file.XMLStructure.dom, pretty_print=True),
"""<Root Self="di2">
  <article XMLContent="u102" Self="di2i3">
    <Story XMLContent="ue4" Self="di2i3i1">
      <title Self="di2i3i1i1"/>
      <subtitle Self="di2i3i1i2"/>
    </Story>
    <content XMLContent="u11b" Self="di2i3i2"/>
    <illustration XMLContent="u135" Self="di2i3i3"/>
    <description XMLContent="u139" Self="di2i3i4"/>
  </article>
  <article XMLContent="udb" Self="di2i4"/>
  <article XMLContent="udd" Self="di2i5"/>
  <advertise XMLContent="udf" Self="di2i6"/>
</Root>
""")

    def test_prefix(self):
        from simple_idml.idml import IDMLPackage

        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"), 
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))

        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        idml_file = idml_file.prefix("FOO")

        # Spreads.
        self.assertEqual(idml_file.spreads, ['Spreads/Spread_FOOub6.xml',
                                             'Spreads/Spread_FOOubc.xml',
                                             'Spreads/Spread_FOOuc3.xml'])
        # Stories.
        self.assertEqual(idml_file.stories, ['Stories/Story_FOOu102.xml',
                                             'Stories/Story_FOOu11b.xml',
                                             'Stories/Story_FOOu139.xml',
                                             'Stories/Story_FOOue4.xml'])

        # XML Structure.
        self.assertEqual(etree.tostring(idml_file.XMLStructure.dom, pretty_print=True),
"""<Root Self="FOOdi2">
  <article XMLContent="FOOu102" Self="FOOdi2i3">
    <Story XMLContent="FOOue4" Self="FOOdi2i3i1">
      <title Self="FOOdi2i3i1i1"/>
      <subtitle Self="FOOdi2i3i1i2"/>
    </Story>
    <content XMLContent="FOOu11b" Self="FOOdi2i3i2"/>
    <illustration XMLContent="FOOu135" Self="FOOdi2i3i3"/>
    <description XMLContent="FOOu139" Self="FOOdi2i3i4"/>
  </article>
  <article XMLContent="FOOudb" Self="FOOdi2i4"/>
  <article XMLContent="FOOudd" Self="FOOdi2i5"/>
  <advertise XMLContent="FOOudf" Self="FOOdi2i6"/>
</Root>
""")
        # designmap.xml
        designmap = etree.fromstring(idml_file.open("designmap.xml").read())
        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList"),
                         "FOOue4 FOOu102 FOOu11b FOOu139 FOOu9c")
        self.assertEqual(designmap.xpath(".//idPkg:Story", 
                                  namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})[0].get("src"),
                        "Stories/Story_FOOu139.xml")
        self.assertEqual(designmap.xpath(".//idPkg:Spread", 
                                  namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})[0].get("src"),
                        "Spreads/Spread_FOOub6.xml")


    def test_insert_idml(self):
        from simple_idml.idml import IDMLPackage

        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"), 
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo.idml"), 
                     os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        main_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        article_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        main_idml_file.insert_idml(article_idml_file, 
                                   at="/Root/article[3]",
                                   only="/Root/module[1]")

        # The XML Structure has integrated the new file.
        self.assertEqual(etree.tostring(main_idml_file.XMLStructure.dom, pretty_print=True),
"""<Root Self="di2">
  <article XMLContent="u102" Self="di2i3">
    <Story XMLContent="ue4" Self="di2i3i1">
      <title Self="di2i3i1i1"/>
      <subtitle Self="di2i3i1i2"/>
    </Story>
    <content XMLContent="u11b" Self="di2i3i2"/>
    <illustration XMLContent="u135" Self="di2i3i3"/>
    <description XMLContent="u139" Self="di2i3i4"/>
  </article>
  <article XMLContent="udb" Self="di2i4"/>
  <article XMLContent="udd" Self="di2i5">
    <module XMLContent="u102" Self="di2i3">
      <main_picture XMLContent="ue5" Self="di2i3i1"/>
      <headline XMLContent="ue8" Self="di2i3i2"/>
      <Story XMLContent="u11a" Self="di2i3i3">
        <article Self="di2i3i3i1"/>
        <informations Self="di2i3i3i2"/>
      </Story>
    </module>
  </article>
  <advertise XMLContent="udf" Self="di2i6"/>
</Root>
""")
                                   

class XMLDocumentTestCase(unittest.TestCase):
    def test_get_element_by_id(self):
        from simple_idml.idml import XMLDocument
        xml_file = open(os.path.join(IDMLFILES_DIR, "4-pages.idml.open", "Stories", "Story_ue4.xml"), mode="r")
        doc = XMLDocument(xml_file)
        elt = doc.getElementById("di2i3i1")
        self.assertTrue(elt is not None)

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleIDMLTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(XMLDocumentTestCase))
    return suite
