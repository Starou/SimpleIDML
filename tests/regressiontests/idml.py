# -*- coding: utf-8 -*-

import os
import shutil
import glob
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from tempfile import mkdtemp
from lxml import etree

from simple_idml.idml import IDMLPackage
from simple_idml.test import SimpleTestCase

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
XML_DIR = os.path.join(CURRENT_DIR, "XML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "simpleIDML")


class IdmlTestCase(SimpleTestCase):
    def setUp(self):
        super(IdmlTestCase, self).setUp()
        self.maxDiff = None
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        if not (os.path.exists(OUTPUT_DIR)):
            os.makedirs(OUTPUT_DIR)

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

        # Stories given a Xpath.
        self.assertEqual(idml_file.stories_for_node("/Root/article[1]"),
                         [u'Stories/Story_u102.xml',
                          u'Stories/Story_ue4.xml',
                          u'Stories/Story_u11b.xml',
                          u'Stories/Story_u139.xml'])

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

        # Styles mapping.
        self.assertEqual(idml_file.style_mapping.tostring(),
                         '<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n<idPkg:Mapping xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">                   </idPkg:Mapping>\n')

        # Fonts.
        self.assertEqual([font.get("Name") for font in idml_file.font_families], ['Minion Pro', 'Myriad Pro', 'Kozuka Mincho Pro', 'Vollkorn'])

        # XML Structure.
        self.assertXMLEqual(unicode(idml_file.xml_structure_pretty()),
u"""<Root Self="di2">
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

        # Test a file with a slighly different structure
        idml_file = os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml")
        idml_file = IDMLPackage(idml_file)
        self.assertXMLEqual(etree.tostring(idml_file.xml_structure, pretty_print=True),
"""<Root Self="di2">
  <page Self="di2ib">
    <title XMLContent="u1b2" Self="di2ibi34"/>
    <article XMLContent="u1c9" Self="di2ibi33"/>
    <article XMLContent="u1e0" Self="di2ibi32"/>
    <article XMLContent="u1fb" Self="di2ibi31"/>
    <article XMLContent="u212" Self="di2ibi30"/>
  </page>
  <page Self="di2i10">
    <advertise XMLContent="u278" Self="di2i10i36"/>
  </page>
</Root>
""")

    def test_get_story_by_xpath(self):
        idml_file = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        idml_file = IDMLPackage(idml_file)
        self.assertEqual(idml_file.get_story_by_xpath("/Root"), "XML/BackingStory.xml")
        self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]"), "Stories/Story_u102.xml")
        self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/Story"), "Stories/Story_ue4.xml")
        self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/Story/title"), "Stories/Story_ue4.xml")
        self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/illustration"), "Stories/Story_u102.xml")

    def test_namelist(self):
        # The namelist can be inherited from ZipFile or computed from the working copy.
        idml_file = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        idml_file = IDMLPackage(idml_file)
        zipfile_namelist = idml_file.namelist()

        idml_working_copy = mkdtemp()
        idml_file.extractall(idml_working_copy)
        idml_file.working_copy_path = idml_working_copy
        idml_file.init_lazy_references()

        working_copy_namelist = idml_file.namelist()
        self.assertEqual(set(zipfile_namelist), set(working_copy_namelist))

        shutil.rmtree(idml_working_copy)

    def test_contentfile_namelist(self):
        idml_file = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        idml_file = IDMLPackage(idml_file)
        self.assertEqual(idml_file.contentfile_namelist(), [
            u'Spreads/Spread_ub6.xml',
            u'Spreads/Spread_ubc.xml',
            u'Spreads/Spread_uc3.xml',
            u'Stories/Story_u139.xml',
            u'Stories/Story_u11b.xml',
            u'Stories/Story_u102.xml',
            u'Stories/Story_ue4.xml',
        ])

    def test_referenced_layers(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        self.assertEqual(idml_file.referenced_layers, ['u2db', 'ua4'])

    def test_get_spread_object_by_xpath(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"))
        spread = idml_file.get_spread_object_by_xpath("/Root/module/main_picture")
        self.assertEqual(spread.name, "Spreads/Spread_ud8.xml")

    def test_get_element_content_id_by_xpath(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"))
        element_id = idml_file.get_element_content_id_by_xpath("/Root/module/main_picture")
        self.assertEqual(element_id, "u14a")

    def test_import_xml(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertXMLEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_nested_tags(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-nested-tags.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-nested-tags.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-nested-tags.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertMultiLineEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is <sup>working</sup> on his latest documentary at sea, his best friend <italique>Esteban du Plantier</italique> (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")

    def test_import_xml_with_ignored_tags(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

        # Idem with a style tag at the very beginning of the text.
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes2.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article><italique>While oceanographer and documentarian</italique><bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_on_prefixed_package(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2-prefixed.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2-prefixed.idml"))
        idml_file = idml_file.prefix("myprefix")
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes2.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertMultiLineEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article><italique>While oceanographer and documentarian</italique><bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_with_setcontent_false(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-setcontent-false.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-setcontent-false.idml"))
        idml_file = idml_file.prefix("myprefix")
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-with-setcontent-false.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline simpleidml-setcontent="false">THE HEADLINE HERE</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_without_picture(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-without-picture.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-without-picture.idml"))
        idml_file = idml_file.prefix("myprefix")
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-without-picture.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        # Should check that the page item has been removed from the spread (or story).
        self.assertEqual(xml,
"""<Root>
  <module>
    <main_picture/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_ignore_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-ignorecontent.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-ignorecontent.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-ignorecontent.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertXMLEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story simpleidml-ignorecontent="true">
      <article>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</article>
      <informations>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_force_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertXMLEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story simpleidml-ignorecontent="true">
      <article>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</article>
      <informations simpleidml-forcecontent="true">The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_force_content2(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent2.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent2.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent2.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertXMLEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:../../IDML/media/bouboune.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story simpleidml-ignorecontent="true">
      <article simpleidml-forcecontent="true">While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.
            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_import_xml_force_content3(self):
        """Forcecontent flag is not a direct child of ignorecontent flag. """
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent3.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent3.idml"))
        xml_file = open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent3.xml"), "r")
        idml_file = idml_file.import_xml(xml_file.read(), at="/Root/module[1]")
        xml = idml_file.export_xml()
        self.assertXMLEqual(xml,
"""<Root>
  <module simpleidml-ignorecontent="true">
    <main_picture href="file:///Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/git/simpleidml/tests/regressiontests/IDML/media/default.jpg"/>
    <headline>THE HEADLINE HERE</headline>
    <Story>
      <article>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</article>
      <informations simpleidml-forcecontent="true">The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")
        xml_file.close()

    def test_export_as_tree(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-nested-xml.idml"))
        tree = idml_file.export_as_tree()
        self.assertEqual(tree, {
            'tag': 'Root',
            'attrs': {},
            'content': [
                {
                    'tag': 'module',
                    'attrs': {},
                    'content': [
                        {
                            'tag': 'main_picture',
                            'attrs': {'href': 'file:///steve.jpg'},
                            'content': [],
                        },
                        {
                            'tag': 'headline',
                            'attrs': {},
                            'content': ['The Life Aquatic with Steve Zissou'],
                        },
                        {
                            'tag': 'Story',
                            'attrs': {},
                            'content': [
                                {
                                    'tag': 'article',
                                    'attrs': {},
                                    'content': [
                                        'While oceanographer and documentarian ',
                                        {
                                            'tag': 'bold',
                                            'attrs': {},
                                            'content': [
                                                'Steve Zissou (Bill Murray) is ',
                                                {
                                                    'tag': 'sup',
                                                    'attrs': {},
                                                    'content': ['working'],
                                                },
                                                ' on his latest documentary at sea, his best friend ',
                                                {
                                                    'tag': 'italique',
                                                    'attrs': {},
                                                    'content': ['Esteban du Plantier'],
                                                },
                                                ' (Seymour Cassel)',
                                            ],
                                        },
                                        u' is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark\'s destruction.\u2028            The crew aboard Zissou\'s research vessel ',
                                        {
                                            'tag': 'italique',
                                            'attrs': {},
                                            'content': ['Belafonte'],
                                        },
                                        ' includes ',
                                        {
                                            'tag': 'italique',
                                            'attrs': {},
                                            'content': [u'Pel\xe9 dos Santos (Seu Jorge)'],
                                        },
                                        ', a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures'
                                    ],
                                },
                                {
                                    'tag': 'informations',
                                    'attrs': {},
                                    'content': [
                                        'The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.'
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        })

    def test_export_xml(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"))
        xml = idml_file.export_xml()
        self.assertMultiLineEqual(xml,
"""<Root>
  <module>
    <main_picture href="file:///Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/git/simpleidml/tests/regressiontests/IDML/media/default.jpg"/>
    <headline>THE HEADLINE HERE</headline>
    <Story>
      <article>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</article>
      <informations>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.</informations>
    </Story>
  </module>
</Root>
""")

        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-xml.idml"))
        xml = idml_file.export_xml()
        self.assertMultiLineEqual(xml,
"""<Root>
  <module>
    <main_picture/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is working on his latest documentary at sea, his best friend Esteban du Plantier (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")

        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo-with-attributes.idml"))
        xml = idml_file.export_xml()
        self.assertXMLEqual(unicode(xml),
u"""<Root>
  <module>
    <main_picture style="fancy" foo="bar"/>
    <headline>THE HEADLINE HERE</headline>
    <Story>
      <article>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.</article>
      <informations bar="baz">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt.</informations>
    </Story>
  </module>
</Root>
""")

    def test_export_xml_with_nested_nodes(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-nested-xml.idml"))
        xml = idml_file.export_xml()
        self.assertXMLEqual(unicode(xml),
u"""<Root>
  <module>
    <main_picture href="file:///steve.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is <sup>working</sup> on his latest documentary at sea, his best friend <italique>Esteban du Plantier</italique> (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark." For his next project, Zissou is determined to document the shark's destruction.&#8232;            The crew aboard Zissou's research vessel <italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese, and Klaus Daimler (Willem Dafoe), the German second-in-command who viewed Zissou and Esteban as father figures</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film directed, written, and co-produced by Wes Anderson.</informations>
    </Story>
  </module>
</Root>
""")

    def test_prefix(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))

        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        self.assertRaises(BaseException, idml_file.prefix, "bad-prefix")
        idml_file = idml_file.prefix("FOO")

        # Spreads.
        self.assertEqual(idml_file.spreads, ['Spreads/Spread_FOOub6.xml',
                                             'Spreads/Spread_FOOubc.xml',
                                             'Spreads/Spread_FOOuc3.xml'])
        spread = etree.fromstring(idml_file.open("Spreads/Spread_FOOub6.xml").read())
        self.assertEqual(spread.xpath(".//Spread[1]")[0].get("Self"), "FOOub6")
        self.assertEqual(spread.xpath(".//Spread[1]/Page[1]")[0].get("Self"), "FOOubb")
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
        self.assertXMLEqual(unicode(idml_file.xml_structure_pretty()),
u"""<Root Self="FOOdi2">
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
        self.assertEqual(designmap.xpath(
            ".//idPkg:Story",
            namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})[0].get("src"),
            "Stories/Story_FOOu139.xml")
        self.assertEqual(designmap.xpath(
            ".//idPkg:Spread",
            namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})[0].get("src"),
            "Spreads/Spread_FOOub6.xml")

        # Prefix d'un fichier avec un mapping Style/Tag XML.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-prefixed.idml"))

        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-prefixed.idml"))
        idml_file = idml_file.prefix("FOO")

    def test_is_prefixed(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"))
        self.assertFalse(idml_file.is_prefixed("foo"))

        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        idml_file = idml_file.prefix("foo")
        self.assertTrue(idml_file.is_prefixed("foo"))
        self.assertFalse(idml_file.is_prefixed("bar"))

    def test_suffix_layers(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))

        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml"))
        idml_file = idml_file.suffix_layers(" - 23")
        self.assertEqual(idml_file.designmap.layer_nodes[0].get("Name"), "Layer 1 - 23")

    def test_insert_idml(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        main_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo.idml"))
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
                                                  'Stories/Story_mainudd.xml',
                                                  'Stories/Story_mainue4.xml'])

        # Spreads
        self.assertEqual(main_idml_file.spreads, ['Spreads/Spread_mainub6.xml',
                                                  'Spreads/Spread_mainubc.xml',
                                                  'Spreads/Spread_mainuc3.xml'])

        self.assertEqual([(elt.tag, elt.attrib) for elt in main_idml_file.spreads_objects[0].dom.iter()], [
            ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
            {'DOMVersion': '7.5'}),
            ('Spread',
            {'PageTransitionDirection': 'NotApplicable', 'BindingLocation': '0', 'PageTransitionDuration': 'Medium', 'ShowMasterItems': 'true', 'PageTransitionType': 'None', 'PageCount': '1', 'Self': 'mainub6', 'AllowPageShuffle': 'true', 'ItemTransform': '1 0 0 1 0 0', 'FlattenerOverride': 'Default'}),
            ('FlattenerPreference',
            {'ConvertAllTextToOutlines': 'false', 'GradientAndMeshResolution': '150', 'ConvertAllStrokesToOutlines': 'false', 'ClipComplexRegions': 'false', 'LineArtAndTextResolution': '300'}),
            ('Properties', {}),
            ('RasterVectorBalance', {'type': 'double'}),
            ('Page',
            {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '1', 'Self': 'mainubb', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 0 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
            ('Properties', {}),
            ('Descriptor', {'type': 'list'}),
            ('ListItem', {'type': 'string'}),
            ('ListItem', {'type': 'enumeration'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'long'}),
            ('ListItem', {'type': 'string'}),
            ('PageColor', {'type': 'enumeration'}),
            ('MarginPreference',
            {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
            ('GridDataInformation',
            {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
            ('Properties', {}),
            ('AppliedFont', {'type': 'string'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainud8', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 0 0', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu102', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -329.76377952755905', 'Anchor': '49.13385826771654 -329.76377952755905', 'LeftDirection': '49.13385826771654 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -38.74015748031496', 'Anchor': '49.13385826771654 -38.74015748031496', 'LeftDirection': '49.13385826771654 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 -38.74015748031496', 'Anchor': '516.8503937007873 -38.74015748031496', 'LeftDirection': '516.8503937007873 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 -329.76377952755905', 'Anchor': '516.8503937007873 -329.76377952755905', 'LeftDirection': '516.8503937007873 -329.76377952755905'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '467.71653543307076'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainudb', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 2.842170943040401e-14 307.0866141732283', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -329.76377952755905', 'Anchor': '49.13385826771654 -329.76377952755905', 'LeftDirection': '49.13385826771654 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -38.74015748031496', 'Anchor': '49.13385826771654 -38.74015748031496', 'LeftDirection': '49.13385826771654 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '236.22047244094495 -38.74015748031496', 'Anchor': '236.22047244094495 -38.74015748031496', 'LeftDirection': '236.22047244094495 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '236.22047244094495 -329.76377952755905', 'Anchor': '236.22047244094495 -329.76377952755905', 'LeftDirection': '236.22047244094495 -329.76377952755905'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '49.13385826771654', 'TopCrop': '-329.76377952755905', 'RightCrop': '-235.22047244094495', 'BottomCrop': '39.74015748031496'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainuddToNode', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 200.31496062992122 307.0866141732282', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainudd', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771655 -329.76377952755905', 'Anchor': '49.13385826771655 -329.76377952755905', 'LeftDirection': '49.13385826771655 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771655 -38.740157480314764', 'Anchor': '49.13385826771655 -38.740157480314764', 'LeftDirection': '49.13385826771655 -38.740157480314764'}),
            ('PathPointType',
            {'RightDirection': '316.53543307086596 -38.740157480314764', 'Anchor': '316.53543307086596 -38.740157480314764', 'LeftDirection': '316.53543307086596 -38.740157480314764'}),
            ('PathPointType',
            {'RightDirection': '316.53543307086596 -329.76377952755905', 'Anchor': '316.53543307086596 -329.76377952755905', 'LeftDirection': '316.53543307086596 -329.76377952755905'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainudf', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 0 0', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771657 278.74015748031496', 'Anchor': '49.13385826771657 278.74015748031496', 'LeftDirection': '49.13385826771657 278.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771657 332.5984251968504', 'Anchor': '49.13385826771657 332.5984251968504', 'LeftDirection': '49.13385826771657 332.5984251968504'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 332.5984251968504', 'Anchor': '516.8503937007873 332.5984251968504', 'LeftDirection': '516.8503937007873 332.5984251968504'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 278.74015748031496', 'Anchor': '516.8503937007873 278.74015748031496', 'LeftDirection': '516.8503937007873 278.74015748031496'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '49.13385826771657', 'TopCrop': '278.74015748031496', 'RightCrop': '-515.8503937007873', 'BottomCrop': '-331.5984251968504'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainuf6', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 277.3228346456692 -310.86614173228344', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainue4', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-192.28346456692918 -18.897637795275614', 'Anchor': '-192.28346456692918 -18.897637795275614', 'LeftDirection': '-192.28346456692918 -18.897637795275614'}),
            ('PathPointType',
            {'RightDirection': '-192.28346456692918 11.338582677165391', 'Anchor': '-192.28346456692918 11.338582677165391', 'LeftDirection': '-192.28346456692918 11.338582677165391'}),
            ('PathPointType',
            {'RightDirection': '192.28346456692913 11.338582677165391', 'Anchor': '192.28346456692913 11.338582677165391', 'LeftDirection': '192.28346456692913 11.338582677165391'}),
            ('PathPointType',
            {'RightDirection': '192.28346456692913 -18.897637795275614', 'Anchor': '192.28346456692913 -18.897637795275614', 'LeftDirection': '192.28346456692913 -18.897637795275614'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '384.5669291338583'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainu12d', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 126.61417322834649 -189.92125984251965', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu11b', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-71.81102362204726 -106.77165354330708', 'Anchor': '-71.81102362204726 -106.77165354330708', 'LeftDirection': '-71.81102362204726 -106.77165354330708'}),
            ('PathPointType',
            {'RightDirection': '-71.81102362204726 151.1811023622045', 'Anchor': '-71.81102362204726 151.1811023622045', 'LeftDirection': '-71.81102362204726 151.1811023622045'}),
            ('PathPointType',
            {'RightDirection': '233.38582677165348 151.1811023622045', 'Anchor': '233.38582677165348 151.1811023622045', 'LeftDirection': '233.38582677165348 151.1811023622045'}),
            ('PathPointType',
            {'RightDirection': '233.38582677165348 -106.77165354330708', 'Anchor': '233.38582677165348 -106.77165354330708', 'LeftDirection': '233.38582677165348 -106.77165354330708'}),
            ('TextFramePreference',
            {'VerticalBalanceColumns': 'true', 'TextColumnFixedWidth': '305.19685039370074'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainu135', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 0 0', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '365.6692913385827 -296.6929133858267', 'Anchor': '365.6692913385827 -296.6929133858267', 'LeftDirection': '365.6692913385827 -296.6929133858267'}),
            ('PathPointType',
            {'RightDirection': '365.6692913385827 -124.7244094488189', 'Anchor': '365.6692913385827 -124.7244094488189', 'LeftDirection': '365.6692913385827 -124.7244094488189'}),
            ('PathPointType',
            {'RightDirection': '510.23622047244095 -124.7244094488189', 'Anchor': '510.23622047244095 -124.7244094488189', 'LeftDirection': '510.23622047244095 -124.7244094488189'}),
            ('PathPointType',
            {'RightDirection': '510.23622047244095 -296.6929133858267', 'Anchor': '510.23622047244095 -296.6929133858267', 'LeftDirection': '510.23622047244095 -296.6929133858267'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '365.6692913385827', 'TopCrop': '-296.6929133858267', 'RightCrop': '-509.23622047244095', 'BottomCrop': '125.7244094488189'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainu14b', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 437.9527559055118 -97.79527559055123', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu139', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-72.28346456692913 -26.929133858267733', 'Anchor': '-72.28346456692913 -26.929133858267733', 'LeftDirection': '-72.28346456692913 -26.929133858267733'}),
            ('PathPointType',
            {'RightDirection': '-72.28346456692913 55.27559055118115', 'Anchor': '-72.28346456692913 55.27559055118115', 'LeftDirection': '-72.28346456692913 55.27559055118115'}),
            ('PathPointType',
            {'RightDirection': '72.28346456692913 55.27559055118115', 'Anchor': '72.28346456692913 55.27559055118115', 'LeftDirection': '72.28346456692913 55.27559055118115'}),
            ('PathPointType',
            {'RightDirection': '72.28346456692913 -26.929133858267733', 'Anchor': '72.28346456692913 -26.929133858267733', 'LeftDirection': '72.28346456692913 -26.929133858267733'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '144.56692913385825'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'Self': 'article1u1d4', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 107.716535433070840 -42.51968503937020', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u1db', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '141.73228346456693 19.84251968503935', 'Anchor': '141.73228346456693 19.84251968503935', 'LeftDirection': '141.73228346456693 19.84251968503935'}),
            ('PathPointType',
            {'RightDirection': '141.73228346456693 310.8661417322836', 'Anchor': '141.73228346456693 310.8661417322836', 'LeftDirection': '141.73228346456693 310.8661417322836'}),
            ('PathPointType',
            {'RightDirection': '409.13385826771633 310.8661417322836', 'Anchor': '409.13385826771633 310.8661417322836', 'LeftDirection': '409.13385826771633 310.8661417322836'}),
            ('PathPointType',
            {'RightDirection': '409.13385826771633 19.84251968503935', 'Anchor': '409.13385826771633 19.84251968503935', 'LeftDirection': '409.13385826771633 19.84251968503935'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '267.4015748031494', 'TextColumnCount': '1', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('Rectangle',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'Self': 'article1u182', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'GradientFillStart': '0 0', 'Locked': 'false', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 109.417322834645740 -76.62992125984261', 'StoryTitle': '$ID/', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'GraphicType', 'GradientFillHiliteLength': '0', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '144.56692913385828 58.582677165354326', 'Anchor': '144.56692913385828 58.582677165354326', 'LeftDirection': '144.56692913385828 58.582677165354326'}),
            ('PathPointType',
            {'RightDirection': '144.56692913385828 199.46456692913392', 'Anchor': '144.56692913385828 199.46456692913392', 'LeftDirection': '144.56692913385828 199.46456692913392'}),
            ('PathPointType',
            {'RightDirection': '403.46456692913387 199.46456692913392', 'Anchor': '403.46456692913387 199.46456692913392', 'LeftDirection': '403.46456692913387 199.46456692913392'}),
            ('PathPointType',
            {'RightDirection': '403.46456692913387 58.582677165354326', 'Anchor': '403.46456692913387 58.582677165354326', 'LeftDirection': '403.46456692913387 58.582677165354326'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ContourOption',
            {'ContourType': 'SameAsClipping', 'IncludeInsideEdges': 'false', 'ContourPathName': '$ID/'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption', {'FittingOnEmptyFrame': 'FillProportionally'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('Image',
            {'GradientFillAngle': '0', 'Space': '$ID/#Links_RGB', 'Self': 'article1u216', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'LastUpdatedInterfaceChangeCount': '', 'ImageRenderingIntent': 'UseColorSettings', 'LocalDisplaySetting': 'Default', 'GradientFillStart': '0 0', 'Name': '$ID/', 'ItemTransform': '0.8544476494893585 0 0 0.8544476494893584 144.56692913385828 58.582677165354326', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'ImageTypeName': '$ID/JPEG', 'EffectivePpi': '84 84', 'Visible': 'true', 'TargetInterfaceChangeCount': '', 'ActualPpi': '72 72'}),
            ('Properties', {}),
            ('Profile', {'type': 'string'}),
            ('GraphicBounds', {'Bottom': '360', 'Top': '0', 'Right': '303', 'Left': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ContourOption',
            {'ContourType': 'SameAsClipping', 'IncludeInsideEdges': 'false', 'ContourPathName': '$ID/'}),
            ('MetadataPacketPreference', {}),
            ('Properties', {}),
            ('Contents', {}),
            ('Link',
            {'ImportPolicy': 'NoAutoImport', 'LinkImportStamp': 'file 129767622980000000 27644', 'CanPackage': 'true', 'LinkResourceModified': 'false', 'AssetID': '$ID/', 'ShowInUI': 'true', 'Self': 'article1u21a', 'LinkImportTime': '2014-09-24T14:47:22', 'LinkResourceSize': '0~6bfc', 'AssetURL': '$ID/', 'ExportPolicy': 'NoAutoExport', 'LinkResourceURI': 'file:/Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/git/simpleidml/tests/regressiontests/IDML/media/default.jpg', 'LinkImportModificationTime': '2012-03-21T01:11:38', 'CanUnembed': 'true', 'LinkClientID': '257', 'StoredState': 'Normal', 'LinkClassID': '35906', 'CanEmbed': 'true', 'LinkObjectModified': 'false', 'LinkResourceFormat': '$ID/JPEG'}),
            ('ClippingPathSettings',
            {'Index': '-1', 'ClippingType': 'None', 'AppliedPathName': '$ID/', 'RestrictToFrame': 'false', 'InvertPath': 'false', 'UseHighResolutionImage': 'true', 'InsetFrame': '0', 'IncludeInsideEdges': 'false', 'Threshold': '25', 'Tolerance': '2'}),
            ('ImageIOPreference',
            {'ApplyPhotoshopClippingPath': 'true', 'AlphaChannelName': '$ID/', 'AllowAutoEmbedding': 'true'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]', 'Self': 'article1u185', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 329.480314960629896 148.34645669291330', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u188', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-76.06299212598424 -19.842519685039377', 'Anchor': '-76.06299212598424 -19.842519685039377', 'LeftDirection': '-76.06299212598424 -19.842519685039377'}),
            ('PathPointType',
            {'RightDirection': '-76.06299212598424 -0.9448818897638205', 'Anchor': '-76.06299212598424 -0.9448818897638205', 'LeftDirection': '-76.06299212598424 -0.9448818897638205'}),
            ('PathPointType',
            {'RightDirection': '182.83464566929132 -0.9448818897638205', 'Anchor': '182.83464566929132 -0.9448818897638205', 'LeftDirection': '182.83464566929132 -0.9448818897638205'}),
            ('PathPointType',
            {'RightDirection': '182.83464566929132 -19.842519685039377', 'Anchor': '182.83464566929132 -19.842519685039377', 'LeftDirection': '182.83464566929132 -19.842519685039377'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '258.89763779527556', 'TextColumnCount': '1', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]', 'Self': 'article1u19c', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 390.425196850393686 216.37795275590547', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u19f', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-137.00787401574803 -64.25196850393701', 'Anchor': '-137.00787401574803 -64.25196850393701', 'LeftDirection': '-137.00787401574803 -64.25196850393701'}),
            ('PathPointType',
            {'RightDirection': '-137.00787401574803 51.968503937007945', 'Anchor': '-137.00787401574803 51.968503937007945', 'LeftDirection': '-137.00787401574803 51.968503937007945'}),
            ('PathPointType',
            {'RightDirection': '121.88976377952753 51.968503937007945', 'Anchor': '121.88976377952753 51.968503937007945', 'LeftDirection': '121.88976377952753 51.968503937007945'}),
            ('PathPointType',
            {'RightDirection': '121.88976377952753 -64.25196850393701', 'Anchor': '121.88976377952753 -64.25196850393701', 'LeftDirection': '121.88976377952753 -64.25196850393701'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '123.44881889763778', 'TextColumnCount': '2', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'})
        ])

        self.assertEqual([(elt.tag, elt.attrib) for elt in main_idml_file.spreads_objects[2].dom.iter()], [
            ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
              {'DOMVersion': '7.5'}),
             ('Spread',
              {'PageTransitionDirection': 'NotApplicable', 'BindingLocation': '1', 'PageTransitionDuration': 'Medium', 'ShowMasterItems': 'true', 'PageTransitionType': 'None', 'PageCount': '1', 'Self': 'mainuc3', 'AllowPageShuffle': 'true', 'ItemTransform': '1 0 0 1 0 1879.3700787401576', 'FlattenerOverride': 'Default'}),
             ('FlattenerPreference',
              {'ConvertAllTextToOutlines': 'false', 'GradientAndMeshResolution': '150', 'ConvertAllStrokesToOutlines': 'false', 'ClipComplexRegions': 'false', 'LineArtAndTextResolution': '300'}),
             ('Properties', {}),
             ('RasterVectorBalance', {'type': 'double'}),
             ('Page',
              {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '4', 'Self': 'mainuc8', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
             ('Properties', {}),
             ('Descriptor', {'type': 'list'}),
             ('ListItem', {'type': 'string'}),
             ('ListItem', {'type': 'enumeration'}),
             ('ListItem', {'type': 'boolean'}),
             ('ListItem', {'type': 'boolean'}),
             ('ListItem', {'type': 'long'}),
             ('ListItem', {'type': 'string'}),
             ('PageColor', {'type': 'enumeration'}),
             ('MarginPreference',
              {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
             ('GridDataInformation',
              {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
             ('Properties', {}),
             ('AppliedFont', {'type': 'string'})
        ])

        # The XML Structure has integrated the new file.
        self.assertXMLEqual(unicode(main_idml_file.xml_structure_pretty()), """<Root Self="maindi2">
  <article Self="maindi2i3" XMLContent="mainu102">
    <Story Self="maindi2i3i1" XMLContent="mainue4">
      <title Self="maindi2i3i1i1"/>
      <subtitle Self="maindi2i3i1i2"/>
    </Story>
    <content Self="maindi2i3i2" XMLContent="mainu11b"/>
    <illustration Self="maindi2i3i3" XMLContent="mainu135"/>
    <description Self="maindi2i3i4" XMLContent="mainu139"/>
  </article>
  <article Self="maindi2i4" XMLContent="mainudb"/>
  <article Self="maindi2i5" XMLContent="mainudd">
    <module Self="article1di3i12" XMLContent="article1u1db">
      <main_picture Self="article1di3i12i1" XMLContent="article1u216"/>
      <headline Self="article1di3i12i2" XMLContent="article1u188"/>
      <Story Self="article1di3i12i3" XMLContent="article1u19f">
        <article Self="article1di3i12i3i2"/>
        <informations Self="article1di3i12i3i1"/>
      </Story>
    </module>
  </article>
  <advertise Self="maindi2i6" XMLContent="mainudf"/>
</Root>
""")

        # Designmap.xml.
        designmap = etree.fromstring(main_idml_file.open("designmap.xml", mode="r").read())
        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList"),
                         "mainue4 mainu102 mainu11b mainu139 mainu9c mainudd article1u1db article1u188 article1u19f")
        self.assertEqual(len(designmap.xpath("/Document/idPkg:Story",
                             namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})), 8)

        # Styles.
        styles = [[style.get("Self") for style in style_group.iterchildren()]
                  for style_group in main_idml_file.style_groups]
        self.assertEqual(styles, [
            ['mainCharacterStyle/$ID/[No character style]',
             'article1CharacterStyle/$ID/[No character style]',
             'article1CharacterStyle/MyBoldStyle'],
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
             'article1ObjectStyle/$ID/[Normal Grid]']])

        # Style mapping.
        self.assertEqual(main_idml_file.style_mapping.character_style_mapping,
                         {'MyBoldTag': 'article1CharacterStyle/MyBoldStyle'})

        # Graphics.
        self.assertTrue(main_idml_file.graphic.dom.xpath(".//Swatch[@Self='article1Swatch/None']"))

    def test_insert_idml_with_complex_source(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-complex.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-1photo.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-1photo.idml"))

        main_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-complex.idml"))
        article_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-1photo.idml"))

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
                                                  'Stories/Story_mainudd.xml',
                                                  'Stories/Story_mainue4.xml'])

        # Spreads
        self.assertEqual(main_idml_file.spreads, ['Spreads/Spread_mainub6.xml',
                                                  'Spreads/Spread_mainubc.xml',
                                                  'Spreads/Spread_mainuc3.xml'])

        self.assertEqual([(elt.tag, elt.attrib) for elt in main_idml_file.spreads_objects[0].dom.iter()], [
            ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
            {'DOMVersion': '7.5'}),
            ('Spread',
            {'PageTransitionDirection': 'NotApplicable', 'BindingLocation': '0', 'PageTransitionDuration': 'Medium', 'ShowMasterItems': 'true', 'PageTransitionType': 'None', 'PageCount': '1', 'Self': 'mainub6', 'AllowPageShuffle': 'true', 'ItemTransform': '1 0 0 1 0 0', 'FlattenerOverride': 'Default'}),
            ('FlattenerPreference',
            {'ConvertAllTextToOutlines': 'false', 'GradientAndMeshResolution': '150', 'ConvertAllStrokesToOutlines': 'false', 'ClipComplexRegions': 'false', 'LineArtAndTextResolution': '300'}),
            ('Properties', {}),
            ('RasterVectorBalance', {'type': 'double'}),
            ('Page',
            {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '1', 'Self': 'mainubb', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 0 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
            ('Properties', {}),
            ('Descriptor', {'type': 'list'}),
            ('ListItem', {'type': 'string'}),
            ('ListItem', {'type': 'enumeration'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'long'}),
            ('ListItem', {'type': 'string'}),
            ('PageColor', {'type': 'enumeration'}),
            ('MarginPreference',
            {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
            ('GridDataInformation',
            {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
            ('Properties', {}),
            ('AppliedFont', {'type': 'string'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainud8', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 0 0', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu102', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -329.76377952755905', 'Anchor': '49.13385826771654 -329.76377952755905', 'LeftDirection': '49.13385826771654 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -38.74015748031496', 'Anchor': '49.13385826771654 -38.74015748031496', 'LeftDirection': '49.13385826771654 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 -38.74015748031496', 'Anchor': '516.8503937007873 -38.74015748031496', 'LeftDirection': '516.8503937007873 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 -329.76377952755905', 'Anchor': '516.8503937007873 -329.76377952755905', 'LeftDirection': '516.8503937007873 -329.76377952755905'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '467.71653543307076'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainudb', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 2.842170943040401e-14 307.0866141732283', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -329.76377952755905', 'Anchor': '49.13385826771654 -329.76377952755905', 'LeftDirection': '49.13385826771654 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771654 -38.74015748031496', 'Anchor': '49.13385826771654 -38.74015748031496', 'LeftDirection': '49.13385826771654 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '236.22047244094495 -38.74015748031496', 'Anchor': '236.22047244094495 -38.74015748031496', 'LeftDirection': '236.22047244094495 -38.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '236.22047244094495 -329.76377952755905', 'Anchor': '236.22047244094495 -329.76377952755905', 'LeftDirection': '236.22047244094495 -329.76377952755905'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '49.13385826771654', 'TopCrop': '-329.76377952755905', 'RightCrop': '-235.22047244094495', 'BottomCrop': '39.74015748031496'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainuddToNode', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 200.31496062992122 307.0866141732282', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainudd', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771655 -329.76377952755905', 'Anchor': '49.13385826771655 -329.76377952755905', 'LeftDirection': '49.13385826771655 -329.76377952755905'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771655 -38.740157480314764', 'Anchor': '49.13385826771655 -38.740157480314764', 'LeftDirection': '49.13385826771655 -38.740157480314764'}),
            ('PathPointType',
            {'RightDirection': '316.53543307086596 -38.740157480314764', 'Anchor': '316.53543307086596 -38.740157480314764', 'LeftDirection': '316.53543307086596 -38.740157480314764'}),
            ('PathPointType',
            {'RightDirection': '316.53543307086596 -329.76377952755905', 'Anchor': '316.53543307086596 -329.76377952755905', 'LeftDirection': '316.53543307086596 -329.76377952755905'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainudf', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 0 0', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '49.13385826771657 278.74015748031496', 'Anchor': '49.13385826771657 278.74015748031496', 'LeftDirection': '49.13385826771657 278.74015748031496'}),
            ('PathPointType',
            {'RightDirection': '49.13385826771657 332.5984251968504', 'Anchor': '49.13385826771657 332.5984251968504', 'LeftDirection': '49.13385826771657 332.5984251968504'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 332.5984251968504', 'Anchor': '516.8503937007873 332.5984251968504', 'LeftDirection': '516.8503937007873 332.5984251968504'}),
            ('PathPointType',
            {'RightDirection': '516.8503937007873 278.74015748031496', 'Anchor': '516.8503937007873 278.74015748031496', 'LeftDirection': '516.8503937007873 278.74015748031496'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '49.13385826771657', 'TopCrop': '278.74015748031496', 'RightCrop': '-515.8503937007873', 'BottomCrop': '-331.5984251968504'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainuf6', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 277.3228346456692 -310.86614173228344', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainue4', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-192.28346456692918 -18.897637795275614', 'Anchor': '-192.28346456692918 -18.897637795275614', 'LeftDirection': '-192.28346456692918 -18.897637795275614'}),
            ('PathPointType',
            {'RightDirection': '-192.28346456692918 11.338582677165391', 'Anchor': '-192.28346456692918 11.338582677165391', 'LeftDirection': '-192.28346456692918 11.338582677165391'}),
            ('PathPointType',
            {'RightDirection': '192.28346456692913 11.338582677165391', 'Anchor': '192.28346456692913 11.338582677165391', 'LeftDirection': '192.28346456692913 11.338582677165391'}),
            ('PathPointType',
            {'RightDirection': '192.28346456692913 -18.897637795275614', 'Anchor': '192.28346456692913 -18.897637795275614', 'LeftDirection': '192.28346456692913 -18.897637795275614'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '384.5669291338583'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainu12d', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 126.61417322834649 -189.92125984251965', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu11b', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-71.81102362204726 -106.77165354330708', 'Anchor': '-71.81102362204726 -106.77165354330708', 'LeftDirection': '-71.81102362204726 -106.77165354330708'}),
            ('PathPointType',
            {'RightDirection': '-71.81102362204726 151.1811023622045', 'Anchor': '-71.81102362204726 151.1811023622045', 'LeftDirection': '-71.81102362204726 151.1811023622045'}),
            ('PathPointType',
            {'RightDirection': '233.38582677165348 151.1811023622045', 'Anchor': '233.38582677165348 151.1811023622045', 'LeftDirection': '233.38582677165348 151.1811023622045'}),
            ('PathPointType',
            {'RightDirection': '233.38582677165348 -106.77165354330708', 'Anchor': '233.38582677165348 -106.77165354330708', 'LeftDirection': '233.38582677165348 -106.77165354330708'}),
            ('TextFramePreference',
            {'VerticalBalanceColumns': 'true', 'TextColumnFixedWidth': '305.19685039370074'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('Rectangle',
            {'GradientFillStart': '0 0', 'GradientStrokeStart': '0 0', 'ContentType': 'GraphicType', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]', 'Self': 'mainu135', 'GradientStrokeHiliteLength': '0', 'GradientStrokeAngle': '0', 'GradientStrokeHiliteAngle': '0', 'GradientFillLength': '0', 'GradientStrokeLength': '0', 'ItemTransform': '1 0 0 1 0 0', 'ItemLayer': 'mainub3', 'LocalDisplaySetting': 'Default', 'StoryTitle': '$ID/', 'Name': '$ID/', 'Visible': 'true', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'Locked': 'false'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '365.6692913385827 -296.6929133858267', 'Anchor': '365.6692913385827 -296.6929133858267', 'LeftDirection': '365.6692913385827 -296.6929133858267'}),
            ('PathPointType',
            {'RightDirection': '365.6692913385827 -124.7244094488189', 'Anchor': '365.6692913385827 -124.7244094488189', 'LeftDirection': '365.6692913385827 -124.7244094488189'}),
            ('PathPointType',
            {'RightDirection': '510.23622047244095 -124.7244094488189', 'Anchor': '510.23622047244095 -124.7244094488189', 'LeftDirection': '510.23622047244095 -124.7244094488189'}),
            ('PathPointType',
            {'RightDirection': '510.23622047244095 -296.6929133858267', 'Anchor': '510.23622047244095 -296.6929133858267', 'LeftDirection': '510.23622047244095 -296.6929133858267'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption',
            {'LeftCrop': '365.6692913385827', 'TopCrop': '-296.6929133858267', 'RightCrop': '-509.23622047244095', 'BottomCrop': '125.7244094488189'}),
            ('ObjectExportOption',
            {'ApplyTagType': 'TagFromStructure', 'ImageSpaceBefore': '0', 'CustomImageAlignment': 'false', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomImageSizeOption': 'SizeRelativeToPageWidth', 'SpaceUnit': 'CssEm', 'GIFOptionsInterlaced': 'true', 'AltTextSourceType': 'SourceXMLStructure', 'GIFOptionsPalette': 'AdaptivePalette', 'CustomActualText': '$ID/', 'CustomImageConversion': 'false', 'JPEGOptionsFormat': 'BaselineEncoding', 'UseImagePageBreak': 'false', 'ImageConversionType': 'JPEG', 'ImagePageBreak': 'PageBreakBefore', 'JPEGOptionsQuality': 'High', 'ImageSpaceAfter': '0', 'ImageAlignment': 'AlignLeft', 'CustomAltText': '$ID/', 'ImageExportResolution': 'Ppi300'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]', 'Self': 'mainu14b', 'GradientFillLength': '0', 'Locked': 'false', 'GradientStrokeHiliteLength': '0', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'mainub3', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 437.9527559055118 -97.79527559055123', 'ContentType': 'TextType', 'GradientFillHiliteAngle': '0', 'GradientStrokeLength': '0', 'GradientFillHiliteLength': '0', 'ParentStory': 'mainu139', 'GradientStrokeAngle': '0', 'Visible': 'true'}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-72.28346456692913 -26.929133858267733', 'Anchor': '-72.28346456692913 -26.929133858267733', 'LeftDirection': '-72.28346456692913 -26.929133858267733'}),
            ('PathPointType',
            {'RightDirection': '-72.28346456692913 55.27559055118115', 'Anchor': '-72.28346456692913 55.27559055118115', 'LeftDirection': '-72.28346456692913 55.27559055118115'}),
            ('PathPointType',
            {'RightDirection': '72.28346456692913 55.27559055118115', 'Anchor': '72.28346456692913 55.27559055118115', 'LeftDirection': '72.28346456692913 55.27559055118115'}),
            ('PathPointType',
            {'RightDirection': '72.28346456692913 -26.929133858267733', 'Anchor': '72.28346456692913 -26.929133858267733', 'LeftDirection': '72.28346456692913 -26.929133858267733'}),
            ('TextFramePreference', {'TextColumnFixedWidth': '144.56692913385825'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'Self': 'article1u1d4', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 107.716535433070840 -42.51968503937020', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u1db', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '141.73228346456693 19.84251968503935', 'Anchor': '141.73228346456693 19.84251968503935', 'LeftDirection': '141.73228346456693 19.84251968503935'}),
            ('PathPointType',
            {'RightDirection': '141.73228346456693 310.8661417322836', 'Anchor': '141.73228346456693 310.8661417322836', 'LeftDirection': '141.73228346456693 310.8661417322836'}),
            ('PathPointType',
            {'RightDirection': '409.13385826771633 310.8661417322836', 'Anchor': '409.13385826771633 310.8661417322836', 'LeftDirection': '409.13385826771633 310.8661417322836'}),
            ('PathPointType',
            {'RightDirection': '409.13385826771633 19.84251968503935', 'Anchor': '409.13385826771633 19.84251968503935', 'LeftDirection': '409.13385826771633 19.84251968503935'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '267.4015748031494', 'TextColumnCount': '1', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('Rectangle',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'Self': 'article1u182', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'GradientFillStart': '0 0', 'Locked': 'false', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 109.417322834645740 -76.62992125984261', 'StoryTitle': '$ID/', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'GraphicType', 'GradientFillHiliteLength': '0', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '144.56692913385828 58.582677165354326', 'Anchor': '144.56692913385828 58.582677165354326', 'LeftDirection': '144.56692913385828 58.582677165354326'}),
            ('PathPointType',
            {'RightDirection': '144.56692913385828 199.46456692913392', 'Anchor': '144.56692913385828 199.46456692913392', 'LeftDirection': '144.56692913385828 199.46456692913392'}),
            ('PathPointType',
            {'RightDirection': '403.46456692913387 199.46456692913392', 'Anchor': '403.46456692913387 199.46456692913392', 'LeftDirection': '403.46456692913387 199.46456692913392'}),
            ('PathPointType',
            {'RightDirection': '403.46456692913387 58.582677165354326', 'Anchor': '403.46456692913387 58.582677165354326', 'LeftDirection': '403.46456692913387 58.582677165354326'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ContourOption',
            {'ContourType': 'SameAsClipping', 'IncludeInsideEdges': 'false', 'ContourPathName': '$ID/'}),
            ('InCopyExportOption',
            {'IncludeGraphicProxies': 'true', 'IncludeAllResources': 'false'}),
            ('FrameFittingOption', {'FittingOnEmptyFrame': 'FillProportionally'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('Image',
            {'GradientFillAngle': '0', 'Space': '$ID/#Links_RGB', 'Self': 'article1u216', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]', 'LastUpdatedInterfaceChangeCount': '', 'ImageRenderingIntent': 'UseColorSettings', 'LocalDisplaySetting': 'Default', 'GradientFillStart': '0 0', 'Name': '$ID/', 'ItemTransform': '0.8544476494893585 0 0 0.8544476494893584 144.56692913385828 58.582677165354326', 'GradientFillHiliteAngle': '0', 'GradientFillHiliteLength': '0', 'ImageTypeName': '$ID/JPEG', 'EffectivePpi': '84 84', 'Visible': 'true', 'TargetInterfaceChangeCount': '', 'ActualPpi': '72 72'}),
            ('Properties', {}),
            ('Profile', {'type': 'string'}),
            ('GraphicBounds', {'Bottom': '360', 'Top': '0', 'Right': '303', 'Left': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ContourOption',
            {'ContourType': 'SameAsClipping', 'IncludeInsideEdges': 'false', 'ContourPathName': '$ID/'}),
            ('MetadataPacketPreference', {}),
            ('Properties', {}),
            ('Contents', {}),
            ('Link',
            {'ImportPolicy': 'NoAutoImport', 'LinkImportStamp': 'file 129767622980000000 27644', 'CanPackage': 'true', 'LinkResourceModified': 'false', 'AssetID': '$ID/', 'ShowInUI': 'true', 'Self': 'article1u21a', 'LinkImportTime': '2014-09-24T14:47:22', 'LinkResourceSize': '0~6bfc', 'AssetURL': '$ID/', 'ExportPolicy': 'NoAutoExport', 'LinkResourceURI': 'file:/Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/git/simpleidml/tests/regressiontests/IDML/media/default.jpg', 'LinkImportModificationTime': '2012-03-21T01:11:38', 'CanUnembed': 'true', 'LinkClientID': '257', 'StoredState': 'Normal', 'LinkClassID': '35906', 'CanEmbed': 'true', 'LinkObjectModified': 'false', 'LinkResourceFormat': '$ID/JPEG'}),
            ('ClippingPathSettings',
            {'Index': '-1', 'ClippingType': 'None', 'AppliedPathName': '$ID/', 'RestrictToFrame': 'false', 'InvertPath': 'false', 'UseHighResolutionImage': 'true', 'InsetFrame': '0', 'IncludeInsideEdges': 'false', 'Threshold': '25', 'Tolerance': '2'}),
            ('ImageIOPreference',
            {'ApplyPhotoshopClippingPath': 'true', 'AlphaChannelName': '$ID/', 'AllowAutoEmbedding': 'true'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]', 'Self': 'article1u185', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 329.480314960629896 148.34645669291330', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u188', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-76.06299212598424 -19.842519685039377', 'Anchor': '-76.06299212598424 -19.842519685039377', 'LeftDirection': '-76.06299212598424 -19.842519685039377'}),
            ('PathPointType',
            {'RightDirection': '-76.06299212598424 -0.9448818897638205', 'Anchor': '-76.06299212598424 -0.9448818897638205', 'LeftDirection': '-76.06299212598424 -0.9448818897638205'}),
            ('PathPointType',
            {'RightDirection': '182.83464566929132 -0.9448818897638205', 'Anchor': '182.83464566929132 -0.9448818897638205', 'LeftDirection': '182.83464566929132 -0.9448818897638205'}),
            ('PathPointType',
            {'RightDirection': '182.83464566929132 -19.842519685039377', 'Anchor': '182.83464566929132 -19.842519685039377', 'LeftDirection': '182.83464566929132 -19.842519685039377'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '258.89763779527556', 'TextColumnCount': '1', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('TextFrame',
            {'GradientStrokeStart': '0 0', 'GradientFillAngle': '0', 'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]', 'Self': 'article1u19c', 'GradientFillLength': '0', 'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'Locked': 'false', 'OverriddenPageItemProps': '', 'ParentInterfaceChangeCount': '', 'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension', 'GradientStrokeHiliteLength': '0', 'LastUpdatedInterfaceChangeCount': '', 'GradientStrokeHiliteAngle': '0', 'LocalDisplaySetting': 'Default', 'ItemLayer': 'article1ua4', 'NextTextFrame': 'n', 'GradientFillStart': '0 0', 'PreviousTextFrame': 'n', 'Name': '$ID/', 'ItemTransform': '1 0 0 1 390.425196850393686 216.37795275590547', 'GradientStrokeLength': '0', 'GradientFillHiliteAngle': '0', 'ContentType': 'TextType', 'GradientFillHiliteLength': '0', 'ParentStory': 'article1u19f', 'GradientStrokeAngle': '0', 'Visible': 'true', 'TargetInterfaceChangeCount': ''}),
            ('Properties', {}),
            ('PathGeometry', {}),
            ('GeometryPathType', {'PathOpen': 'false'}),
            ('PathPointArray', {}),
            ('PathPointType',
            {'RightDirection': '-137.00787401574803 -64.25196850393701', 'Anchor': '-137.00787401574803 -64.25196850393701', 'LeftDirection': '-137.00787401574803 -64.25196850393701'}),
            ('PathPointType',
            {'RightDirection': '-137.00787401574803 51.968503937007945', 'Anchor': '-137.00787401574803 51.968503937007945', 'LeftDirection': '-137.00787401574803 51.968503937007945'}),
            ('PathPointType',
            {'RightDirection': '121.88976377952753 51.968503937007945', 'Anchor': '121.88976377952753 51.968503937007945', 'LeftDirection': '121.88976377952753 51.968503937007945'}),
            ('PathPointType',
            {'RightDirection': '121.88976377952753 -64.25196850393701', 'Anchor': '121.88976377952753 -64.25196850393701', 'LeftDirection': '121.88976377952753 -64.25196850393701'}),
            ('TextFramePreference',
            {'UseMinimumHeightForAutoSizing': 'false', 'TextColumnFixedWidth': '123.44881889763778', 'TextColumnCount': '2', 'UseNoLineBreaksForAutoSizing': 'false', 'AutoSizingReferencePoint': 'CenterPoint', 'TextColumnMaxWidth': '0', 'AutoSizingType': 'Off', 'UseMinimumWidthForAutoSizing': 'false', 'MinimumWidthForAutoSizing': '0', 'MinimumHeightForAutoSizing': '0'}),
            ('TextWrapPreference',
            {'TextWrapSide': 'BothSides', 'Inverse': 'false', 'TextWrapMode': 'None', 'ApplyToMasterPageOnly': 'false'}),
            ('Properties', {}),
            ('TextWrapOffset', {'Right': '0', 'Top': '0', 'Bottom': '0', 'Left': '0'}),
            ('ObjectExportOption',
            {'GIFOptionsPalette': 'AdaptivePalette', 'JPEGOptionsFormat': 'BaselineEncoding', 'CustomImageAlignment': 'false', 'UseOriginalImage': 'false', 'CustomWidthType': 'DefaultWidth', 'ImagePageBreak': 'PageBreakBefore', 'AltTextSourceType': 'SourceXMLStructure', 'UseImagePageBreak': 'false', 'GIFOptionsInterlaced': 'true', 'ImageExportResolution': 'Ppi300', 'ImageSpaceBefore': '0', 'CustomHeightType': 'DefaultHeight', 'JPEGOptionsQuality': 'High', 'CustomLayout': 'false', 'ImageAlignment': 'AlignLeft', 'UseExistingImage': 'false', 'CustomLayoutType': 'AlignmentAndSpacing', 'ImageConversionType': 'JPEG', 'SpaceUnit': 'CssPixel', 'CustomImageConversion': 'false', 'ApplyTagType': 'TagFromStructure', 'ActualTextSourceType': 'SourceXMLStructure', 'CustomAltText': '$ID/', 'CustomActualText': '$ID/', 'CustomHeight': '$ID/', 'EpubType': '$ID/', 'ImageSpaceAfter': '0', 'CustomWidth': '$ID/'}),
            ('Properties', {}),
            ('AltMetadataProperty', {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'}),
            ('ActualMetadataProperty',
            {'PropertyPath': '$ID/', 'NamespacePrefix': '$ID/'})
 ])

        self.assertEqual([(elt.tag, elt.attrib) for elt in main_idml_file.spreads_objects[1].dom.iter()], [
            ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
            {'DOMVersion': '7.5'}),
            ('Spread',
            {'PageTransitionDirection': 'NotApplicable', 'BindingLocation': '1', 'PageTransitionDuration': 'Medium', 'ShowMasterItems': 'true', 'PageTransitionType': 'None', 'PageCount': '2', 'Self': 'mainubc', 'AllowPageShuffle': 'true', 'ItemTransform': '1 0 0 1 0 939.6850393700788', 'FlattenerOverride': 'Default'}),
            ('FlattenerPreference',
            {'ConvertAllTextToOutlines': 'false', 'GradientAndMeshResolution': '150', 'ConvertAllStrokesToOutlines': 'false', 'ClipComplexRegions': 'false', 'LineArtAndTextResolution': '300'}),
            ('Properties', {}),
            ('RasterVectorBalance', {'type': 'double'}),
            ('Page',
            {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '2', 'Self': 'mainuc1', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
            ('Properties', {}),
            ('Descriptor', {'type': 'list'}),
            ('ListItem', {'type': 'string'}),
            ('ListItem', {'type': 'enumeration'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'long'}),
            ('ListItem', {'type': 'string'}),
            ('PageColor', {'type': 'enumeration'}),
            ('MarginPreference',
            {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
            ('GridDataInformation',
            {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
            ('Properties', {}),
            ('AppliedFont', {'type': 'string'}),
            ('Page',
            {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '3', 'Self': 'mainuc2', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 0 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
            ('Properties', {}),
            ('Descriptor', {'type': 'list'}),
            ('ListItem', {'type': 'string'}),
            ('ListItem', {'type': 'enumeration'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'boolean'}),
            ('ListItem', {'type': 'long'}),
            ('ListItem', {'type': 'string'}),
            ('PageColor', {'type': 'enumeration'}),
            ('MarginPreference',
            {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
            ('GridDataInformation',
            {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
            ('Properties', {}),
            ('AppliedFont', {'type': 'string'})
        ])

        self.assertEqual([(elt.tag, elt.attrib) for elt in main_idml_file.spreads_objects[2].dom.iter()], [
            ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
              {'DOMVersion': '7.5'}),
             ('Spread',
              {'PageTransitionDirection': 'NotApplicable', 'BindingLocation': '1', 'PageTransitionDuration': 'Medium', 'ShowMasterItems': 'true', 'PageTransitionType': 'None', 'PageCount': '1', 'Self': 'mainuc3', 'AllowPageShuffle': 'true', 'ItemTransform': '1 0 0 1 0 1879.3700787401576', 'FlattenerOverride': 'Default'}),
             ('FlattenerPreference',
              {'ConvertAllTextToOutlines': 'false', 'GradientAndMeshResolution': '150', 'ConvertAllStrokesToOutlines': 'false', 'ClipComplexRegions': 'false', 'LineArtAndTextResolution': '300'}),
             ('Properties', {}),
             ('RasterVectorBalance', {'type': 'double'}),
             ('Page',
              {'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName', 'Name': '4', 'Self': 'mainuc8', 'UseMasterGrid': 'true', 'MasterPageTransform': '1 0 0 1 0 0', 'TabOrder': '', 'OverrideList': '', 'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394', 'GridStartingPoint': 'TopOutside', 'GeometricBounds': '0 0 759.6850393700788 566.9291338582677', 'AppliedMaster': 'uca'}),
             ('Properties', {}),
             ('Descriptor', {'type': 'list'}),
             ('ListItem', {'type': 'string'}),
             ('ListItem', {'type': 'enumeration'}),
             ('ListItem', {'type': 'boolean'}),
             ('ListItem', {'type': 'boolean'}),
             ('ListItem', {'type': 'long'}),
             ('ListItem', {'type': 'string'}),
             ('PageColor', {'type': 'enumeration'}),
             ('MarginPreference',
              {'ColumnCount': '1', 'Right': '36', 'Bottom': '36', 'Top': '36', 'ColumnGutter': '12', 'ColumnsPositions': '0 494.92913385826773', 'ColumnDirection': 'Horizontal', 'Left': '36'}),
             ('GridDataInformation',
              {'LineAki': '9', 'FontStyle': 'Regular', 'PointSize': '12', 'CharacterAki': '0', 'GridAlignment': 'AlignEmCenter', 'LineAlignment': 'LeftOrTopLineJustify', 'HorizontalScale': '100', 'CharacterAlignment': 'AlignEmCenter', 'VerticalScale': '100'}),
             ('Properties', {}),
             ('AppliedFont', {'type': 'string'})
        ])

        # The XML Structure has integrated the new file.
        self.assertXMLEqual(unicode(main_idml_file.xml_structure_pretty()), """<Root Self="maindi2">
  <article Self="maindi2i3" XMLContent="mainu102">
    <Story Self="maindi2i3i1" XMLContent="mainue4">
      <title Self="maindi2i3i1i1"/>
      <subtitle Self="maindi2i3i1i2"/>
    </Story>
    <content Self="maindi2i3i2" XMLContent="mainu11b"/>
    <illustration Self="maindi2i3i3" XMLContent="mainu135"/>
    <description Self="maindi2i3i4" XMLContent="mainu139"/>
  </article>
  <article Self="maindi2i4" XMLContent="mainudb"/>
  <article Self="maindi2i5" XMLContent="mainudd">
    <module Self="article1di3i12" XMLContent="article1u1db">
      <main_picture Self="article1di3i12i1" XMLContent="article1u216"/>
      <headline Self="article1di3i12i2" XMLContent="article1u188"/>
      <Story Self="article1di3i12i3" XMLContent="article1u19f">
        <article Self="article1di3i12i3i2"/>
        <informations Self="article1di3i12i3i1"/>
      </Story>
    </module>
  </article>
  <advertise Self="maindi2i6" XMLContent="mainudf"/>
</Root>
""")

        # Designmap.xml.
        designmap = etree.fromstring(main_idml_file.open("designmap.xml", mode="r").read())
        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList"),
                         "mainue4 mainu102 mainu11b mainu139 mainu9c mainudd article1u1db article1u188 article1u19f")
        self.assertEqual(len(designmap.xpath("/Document/idPkg:Story",
                             namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})), 8)

        # Styles.
        styles = [[style.get("Self") for style in style_group.iterchildren()]
                  for style_group in main_idml_file.style_groups]
        self.assertEqual(styles, [
            ['mainCharacterStyle/$ID/[No character style]',
             'article1CharacterStyle/$ID/[No character style]',
             'article1CharacterStyle/MyBoldStyle'],
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
             'article1ObjectStyle/$ID/[Normal Grid]']])

        # Style mapping.
        self.assertEqual(main_idml_file.style_mapping.character_style_mapping,
                         {'MyBoldTag': 'article1CharacterStyle/MyBoldStyle'})

        # Graphics.
        self.assertTrue(main_idml_file.graphic.dom.xpath(".//Swatch[@Self='article1Swatch/None']"))

    def test_insert_idml_without_picture(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-0-photo-complex.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-0photo.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-0photo.idml"))

        main_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-0-photo-complex.idml"))
        article_idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-0photo.idml"))

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
                                                  'Stories/Story_mainudd.xml',
                                                  'Stories/Story_mainue4.xml'])

        # Spreads
        self.assertEqual(main_idml_file.spreads, ['Spreads/Spread_mainub6.xml',
                                                  'Spreads/Spread_mainubc.xml',
                                                  'Spreads/Spread_mainuc3.xml'])

    def test_remove_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_imported-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_imported-xml.idml"))
        idml_file = IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_imported-xml.idml"))
        idml_file = idml_file.remove_content(under="/Root/module/Story")
        self.assertXMLEqual(unicode(idml_file.xml_structure_pretty()),
u"""<Root Self="di3">
  <module XMLContent="u10d" Self="di3i4">
    <main_picture XMLContent="udf" Self="di3i4i1"/>
    <headline XMLContent="ue1" Self="di3i4i2"/>
    <Story XMLContent="uf7" Self="di3i4i3"/>
  </module>
</Root>
""")

    def test_add_page_from_idml(self):
        edito_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-edito.idml")
        courrier_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-courrier-des-lecteurs.idml")
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-edito.idml"), edito_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), courrier_idml_filename)

        edito_idml_file = IDMLPackage(edito_idml_filename)
        courrier_idml_file = IDMLPackage(courrier_idml_filename)

        # Always start by prefixing packages to avoid collision.
        edito_idml_file = edito_idml_file.prefix("edito")
        courrier_idml_file = courrier_idml_file.prefix("courrier")
        self.assertEqual(len(edito_idml_file.pages), 2)

        new_idml = edito_idml_file.add_page_from_idml(courrier_idml_file,
                                                      page_number=1,
                                                      at="/Root",
                                                      only="/Root/page[1]")
        self.assertEqual(len(new_idml.pages), 3)

        # The XML Structure has integrated the new file.
        self.assertXMLEqual(unicode(new_idml.xml_structure_pretty()),
u"""<Root Self="editodi2">
  <page Self="editodi2ib">
    <article Self="editodi2ibif">
      <Story XMLContent="editoue4" Self="editodi2ibifi1f">
        <title Self="editodi2ibifi1fi1"/>
        <subtitle Self="editodi2ibifi1fi2"/>
      </Story>
      <content XMLContent="editou11b" Self="editodi2ibifi1e"/>
    </article>
  </page>
  <page Self="editodi2i10">
    <advertise XMLContent="editou1de" Self="editodi2i10i23"/>
  </page>
  <page Self="courrierdi2ib">
    <title XMLContent="courrieru1b2" Self="courrierdi2ibi34"/>
    <article XMLContent="courrieru1c9" Self="courrierdi2ibi33"/>
    <article XMLContent="courrieru1e0" Self="courrierdi2ibi32"/>
    <article XMLContent="courrieru1fb" Self="courrierdi2ibi31"/>
    <article XMLContent="courrieru212" Self="courrierdi2ibi30"/>
  </page>
</Root>
""")

    def test_add_pages_from_idml(self):
        edito_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-edito.idml")
        courrier_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-courrier-des-lecteurs.idml")
        bloc_notes_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-bloc-notes.idml")
        bloc_notes2_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-bloc-notes2.idml")
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-edito.idml"), edito_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), courrier_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-bloc-notes.idml"), bloc_notes_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-bloc-notes.idml"), bloc_notes2_idml_filename)

        edito_idml_file = IDMLPackage(edito_idml_filename)
        courrier_idml_file = IDMLPackage(courrier_idml_filename)
        bloc_notes_idml_file = IDMLPackage(bloc_notes_idml_filename)
        bloc_notes2_idml_file = IDMLPackage(bloc_notes2_idml_filename)

        # Always start by prefixing packages to avoid collision.
        edito_idml_file = edito_idml_file.prefix("edito")
        courrier_idml_file = courrier_idml_file.prefix("courrier")
        bloc_notes_idml_file = bloc_notes_idml_file.prefix("blocnotes")
        bloc_notes2_idml_file = bloc_notes2_idml_file.prefix("blocnotes2")

        packages_to_add = [
            (courrier_idml_file, 1, "/Root", "/Root/page[1]"),
            (bloc_notes_idml_file, 1, "/Root", "/Root/page[1]"),
            (bloc_notes2_idml_file, 2, "/Root", "/Root/page[2]"),
        ]

        new_idml = edito_idml_file.add_pages_from_idml(packages_to_add)
        os.unlink(courrier_idml_filename)
        os.unlink(bloc_notes_idml_filename)
        os.unlink(bloc_notes2_idml_filename)

        self.assertEqual(len(new_idml.pages), 5)
        self.assertEqual(new_idml.spreads, ['Spreads/Spread_editoub6.xml',
                                            'Spreads/Spread_editoubc.xml',
                                            'Spreads/Spread_editoubd.xml'])

    def test_add_pages_from_idml_to_template(self):
        # Now we use an empty document to hold the pages.
        magazineA_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-template.idml")
        edito_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-edito.idml")
        courrier_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-courrier-des-lecteurs.idml")
        bloc_notes_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-bloc-notes.idml")
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-template.idml"), magazineA_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-edito.idml"), edito_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), courrier_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-bloc-notes.idml"), bloc_notes_idml_filename)

        magazineA_idml_file = IDMLPackage(magazineA_idml_filename)
        edito_idml_file = IDMLPackage(edito_idml_filename)
        courrier_idml_file = IDMLPackage(courrier_idml_filename)
        bloc_notes_idml_file = IDMLPackage(bloc_notes_idml_filename)

        # Always start by prefixing packages to avoid collision.
        magazineA_idml_file = magazineA_idml_file.prefix("mag")
        edito_idml_file = edito_idml_file.prefix("edito")
        courrier_idml_file = courrier_idml_file.prefix("courrier")
        bloc_notes_idml_file = bloc_notes_idml_file.prefix("blocnotes")

        packages_to_add = [
            (edito_idml_file, 1, "/Root", "/Root/page[1]"),
            (courrier_idml_file, 1, "/Root", "/Root/page[1]"),
            (bloc_notes_idml_file, 1, "/Root", "/Root/page[1]"),
        ]

        magazineA_idml_file = magazineA_idml_file.add_pages_from_idml(packages_to_add)
        os.unlink(edito_idml_filename)
        os.unlink(courrier_idml_filename)
        os.unlink(bloc_notes_idml_filename)

        self.assertEqual(len(magazineA_idml_file.pages), 4)
        # FIXME Broken.
        self.assertEqual(magazineA_idml_file.spreads, ['Spreads/Spread_magub6.xml', 'Spreads/Spread_magub7.xml'])


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(IdmlTestCase)
    return suite
