# -*- coding: utf-8 -*-

import os, sys, shutil
import glob
import unittest
import codecs
import StringIO
from lxml import etree
from simple_idml.idml import IDMLPackage
from simple_idml.idml import XMLDocument

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "simpleIDML_files")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "simpleIDML")


class SimpleIDMLTestCase(unittest.TestCase):
    def setUp(self):
        super(SimpleIDMLTestCase, self).setUp()
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)

    def test_idml_package(self):
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

        # Tags.
        self.assertEqual([etree.tostring(tag) for tag in idml_file.tags], 
                        ['<XMLTag Self="XMLTag/advertise" Name="advertise">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Green</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/article" Name="article">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Red</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/content" Name="content">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Magenta</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/description" Name="description">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Gray</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/illustration" Name="illustration">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Cyan</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t', 
                         '<XMLTag Self="XMLTag/Root" Name="Root">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">LightBlue</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/Story" Name="Story">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">BrickRed</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/subtitle" Name="subtitle">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Yellow</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n\t',
                         '<XMLTag Self="XMLTag/title" Name="title">\n\t\t<Properties>\n\t\t\t<TagColor type="enumeration">Blue</TagColor>\n\t\t</Properties>\n\t</XMLTag>\n'])

        # Styles.
        self.assertEqual([style.tag for style in idml_file.style_groups], ['RootCharacterStyleGroup',
                                                                           'RootParagraphStyleGroup',
                                                                           'RootCellStyleGroup',
                                                                           'RootTableStyleGroup',
                                                                           'RootObjectStyleGroup'])

        # Fonts.
        self.assertEqual([font.get("Name") for font in idml_file.font_families], ['Minion Pro', 'Myriad Pro', 'Kozuka Mincho Pro', 'Vollkorn'])

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
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"), 
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))

        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        idml_file = idml_file.prefix("FOO")

        # Spreads.
        self.assertEqual(idml_file.spreads, ['Spreads/Spread_FOOub6.xml',
                                             'Spreads/Spread_FOOubc.xml',
                                             'Spreads/Spread_FOOuc3.xml'])
        spread = etree.fromstring(idml_file.open("Spreads/Spread_FOOub6.xml").read())
        self.assertEqual(spread.xpath(".//Spread[1]")[0].get("Self"), "FOOub6")
        self.assertEqual(spread.xpath(".//Spread[1]/Page[1]")[0].get("Self"), "ubb")
        self.assertEqual(spread.xpath(".//Spread[1]/TextFrame[1]")[0].get("Self"), "FOOud8")
        self.assertEqual(spread.xpath(".//Spread[1]/TextFrame[1]")[0].get("ParentStory"), "FOOu102")

        # Stories.
        self.assertEqual(idml_file.stories, ['Stories/Story_FOOu102.xml',
                                             'Stories/Story_FOOu11b.xml',
                                             'Stories/Story_FOOu139.xml',
                                             'Stories/Story_FOOue4.xml'])
        story = etree.fromstring(idml_file.open("Stories/Story_FOOu102.xml").read())
        self.assertEqual(story.xpath("//CharacterStyleRange")[0].get("AppliedCharacterStyle"),
                         "FOOCharacterStyle/$ID/[No character style]")

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

        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"), 
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo.idml"), 
                     os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        main_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        article_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        # Always start by prefixing packages to avoid collision.
        main_idml_file = main_idml_file.prefix("main")
        article_idml_file = article_idml_file.prefix("article1")

        main_idml_file = main_idml_file.insert_idml(article_idml_file, 
                                                    at="/Root/article[3]",
                                                    only="/Root/module[1]")

        # Stories.
        self.assertEqual(main_idml_file.stories, ['Stories/Story_article1u188.xml',
                                                  'Stories/Story_article1u19f.xml',
                                                  'Stories/Story_article1u1db.xml', 
                                                  'Stories/Story_mainu102.xml',
                                                  'Stories/Story_mainu11b.xml', 
                                                  'Stories/Story_mainu139.xml',
                                                  'Stories/Story_mainue4.xml'])

                                   
        # The XML Structure has integrated the new file.
        #print"\n", (etree.tostring(main_idml_file.XMLStructure.dom, pretty_print=True))
        self.assertEqual(etree.tostring(main_idml_file.XMLStructure.dom, pretty_print=True),
"""<Root Self="maindi2">
  <article XMLContent="mainu102" Self="maindi2i3">
    <Story XMLContent="mainue4" Self="maindi2i3i1">
      <title Self="maindi2i3i1i1"/>
      <subtitle Self="maindi2i3i1i2"/>
    </Story>
    <content XMLContent="mainu11b" Self="maindi2i3i2"/>
    <illustration XMLContent="mainu135" Self="maindi2i3i3"/>
    <description XMLContent="mainu139" Self="maindi2i3i4"/>
  </article>
  <article XMLContent="mainudb" Self="maindi2i4"/>
  <article Self="maindi2i5"/>
  <module XMLContent="article1u1db" Self="article1di3i12">
    <main_picture XMLContent="article1u182" Self="article1di3i12i1"/>
    <headline XMLContent="article1u188" Self="article1di3i12i2"/>
    <Story XMLContent="article1u19f" Self="article1di3i12i3">
      <article Self="article1di3i12i3i2"/>
      <informations Self="article1di3i12i3i1"/>
    </Story>
  </module>
  <advertise XMLContent="mainudf" Self="maindi2i6"/>
</Root>
""")

        # Designmap.xml.
        designmap = etree.fromstring(main_idml_file.open("designmap.xml", mode="r").read())
        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList"),
                         "mainue4 mainu102 mainu11b mainu139 mainu9c article1u188 article1u19f article1u1db")
        self.assertEqual(len(designmap.xpath("/Document/idPkg:Story",
                             namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})), 7)

        # TODO Test Spread_mainub6.xml content.

        # Styles.
        self.assertEqual([[style.get("Self") for style in style_group.iterchildren()] for style_group in main_idml_file.style_groups], 
                         [['mainCharacterStyle/$ID/[No character style]',
                           'article1CharacterStyle/$ID/[No character style]'],
                          ['mainParagraphStyle/$ID/[No paragraph style]',
                           'mainParagraphStyle/$ID/NormalParagraphStyle', 
                           'article1ParagraphStyle/$ID/[No paragraph style]',
                           'article1ParagraphStyle/$ID/NormalParagraphStyle'],
                          ['mainCellStyle/$ID/[None]', 'article1CellStyle/$ID/[None]'],
                          ['mainTableStyle/$ID/[No table style]',
                           'mainTableStyle/$ID/[Basic Table]', 
                           'article1TableStyle/$ID/[No table style]',
                           'article1TableStyle/$ID/[Basic Table]'],
                          ['mainObjectStyle/$ID/[None]',
                           'mainObjectStyle/$ID/[Normal Graphics Frame]',
                           'mainObjectStyle/$ID/[Normal Text Frame]',
                           'mainObjectStyle/$ID/[Normal Grid]', 
                           'article1ObjectStyle/$ID/[None]', 
                           'article1ObjectStyle/$ID/[Normal Graphics Frame]',
                           'article1ObjectStyle/$ID/[Normal Text Frame]', 
                           'article1ObjectStyle/$ID/[Normal Grid]']
                         ])


class XMLDocumentTestCase(unittest.TestCase):
    def test_get_element_by_id(self):
        xml_file = open(os.path.join(IDMLFILES_DIR, "4-pages.idml.open", "Stories", "Story_ue4.xml"), mode="r")
        doc = XMLDocument(xml_file)
        elt = doc.getElementById("di2i3i1")
        self.assertTrue(elt is not None)

    def test_to_string(self):
        xml_file = StringIO.StringIO()
        xml_file.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                          <document>This is a XML document with unicode : ₣.</document>""")
        xml_file.seek(0)
        doc = XMLDocument(xml_file)
        self.assertEqual(doc.tostring(), """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<document>This is a XML document with unicode : ₣.</document>
""")
        self.assertEqual(doc.tostring(ref_doctype="designmap.xml"), """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="7.5(142)" ?>
<document>This is a XML document with unicode : ₣.</document>
""")

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleIDMLTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(XMLDocumentTestCase))
    return suite
