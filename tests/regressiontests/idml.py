# -*- coding: utf-8 -*-

import glob
import os
import shutil
import unittest
from tempfile import mkdtemp
from lxml import etree
from simple_idml.idml import IDMLPackage
from simple_idml.test import SimpleTestCase
from simple_idml.utils import etree_dom_to_tree

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")
XML_DIR = os.path.join(CURRENT_DIR, "XML")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs", "simpleIDML")

IDPKG_NS = "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"


def memory_dump():
    import gc
    import sys
    dump = {}
    for obj in gc.get_objects():
        i = id(obj)
        size = sys.getsizeof(obj, 0)
        referents = [id(o) for o in gc.get_referents(obj) if hasattr(o, '__class__')]
        if hasattr(obj, '__class__'):
            cls = obj.__class__
            dump.setdefault(cls.__name__, []).append({'id': i, 'obj': obj, 'size': size,
                                                      'referents': referents, 'class': str(cls)})
    return dump


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
        idml_filename = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        with IDMLPackage(idml_filename) as idml_file:

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
            self.assertEqual([etree_dom_to_tree(tag, True) for tag in idml_file.tags], [
                {'attrs': {'Name': 'advertise', 'Self': 'XMLTag/advertise'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Green'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'article', 'Self': 'XMLTag/article'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Red'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'content', 'Self': 'XMLTag/content'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Magenta'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'description', 'Self': 'XMLTag/description'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Gray'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'illustration', 'Self': 'XMLTag/illustration'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Cyan'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'Root', 'Self': 'XMLTag/Root'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'LightBlue'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'Story', 'Self': 'XMLTag/Story'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'BrickRed'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'subtitle', 'Self': 'XMLTag/subtitle'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Yellow'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''},
                {'attrs': {'Name': 'title', 'Self': 'XMLTag/title'},
                 'content': [{'attrs': {},
                              'content': [{'attrs': {'type': 'enumeration'},
                                           'content': [],
                                           'tag': 'TagColor',
                                           'tail': '',
                                           'text': 'Blue'}],
                              'tag': 'Properties',
                              'tail': '',
                              'text': ''}],
                 'tag': 'XMLTag',
                 'tail': '',
                 'text': ''}
            ])

            # Styles.
            self.assertEqual([style.tag for style in idml_file.style_groups], [
                'RootCharacterStyleGroup',
                'RootParagraphStyleGroup',
                'RootCellStyleGroup',
                'RootTableStyleGroup',
                'RootObjectStyleGroup'
            ])

            # Styles mapping.
            self.assertEqual(idml_file.style_mapping.tostring(),
                             "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<idPkg:Mapping xmlns:idPkg=\"http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging\" DOMVersion=\"7.5\">                   </idPkg:Mapping>\n")

            # Fonts.
            self.assertEqual([font.get("Name") for font in idml_file.font_families], [
                'Minion Pro',
                'Myriad Pro',
                'Kozuka Mincho Pro',
                'Vollkorn'
            ])

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
        idml_filename = os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml")
        with IDMLPackage(idml_filename) as idml_file:
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
        idml_filename = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        with IDMLPackage(idml_filename) as idml_file:
            self.assertEqual(idml_file.get_story_by_xpath("/Root"), "XML/BackingStory.xml")
            self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]"), "Stories/Story_u102.xml")
            self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/Story"), "Stories/Story_ue4.xml")
            self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/Story/title"), "Stories/Story_ue4.xml")
            self.assertEqual(idml_file.get_story_by_xpath("/Root/article[1]/illustration"), "Stories/Story_u102.xml")

    def test_namelist(self):
        # The namelist can be inherited from ZipFile or computed from the working copy.
        idml_filename = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        with IDMLPackage(idml_filename) as idml_file:
            zipfile_namelist = idml_file.namelist()

            idml_working_copy = mkdtemp()
            idml_file.extractall(idml_working_copy)
            idml_file.working_copy_path = idml_working_copy
            idml_file.init_lazy_references()

            working_copy_namelist = idml_file.namelist()
            self.assertEqual(set(zipfile_namelist), set(working_copy_namelist))

            shutil.rmtree(idml_working_copy)

    def test_contentfile_namelist(self):
        idml_filename = os.path.join(IDMLFILES_DIR, "4-pages.idml")
        with IDMLPackage(idml_filename) as idml_file:
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
        idml_filename = os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml")
        with IDMLPackage(idml_filename, mode="r") as idml_file:
            self.assertEqual(idml_file.referenced_layers, ['u2db', 'ua4'])

    def test_get_spread_elements_by_layer(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "2articles-1photo-elts-same-layer.idml")) as idml_file:
            self.assertEqual(
                set([elt.get("Name") for elt in
                     idml_file.get_spread_elements_by_layer(layer_name="Layer 2")]),
                set(['module2-Red_background', 'module2-Text', 'module2-Frame', 'module2-Image'])
            )

    def test_get_spread_object_by_xpath(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml")) as idml_file:
            spread = idml_file.get_spread_object_by_xpath("/Root/module/main_picture")
            self.assertEqual(spread.name, "Spreads/Spread_ud8.xml")

    def test_get_element_content_id_by_xpath(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml")) as idml_file:
            element_id = idml_file.get_element_content_id_by_xpath("/Root/module/main_picture")
            self.assertEqual(element_id, "u14a")

    def test_get_layer_id_by_name(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "2articles-1photo-elts-same-layer.idml")) as idml_file:
            self.assertEqual(idml_file.get_layer_id_by_name("Layer 2"), "u2a8")

    def test_get_structure_elements_layer_id(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "2articles-1photo-elts-same-layer.idml")) as idml_file:
            module_elt = idml_file.xml_structure.xpath("/Root/module[1]")[0]
            self.assertEqual(idml_file.get_structure_element_layer_id(module_elt), "ua4")

            picture_elt = idml_file.xml_structure.xpath("/Root/module[1]/main_picture")[0]
            self.assertEqual(idml_file.get_structure_element_layer_id(picture_elt), "ua4")

    def test_import_xml(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_import_xml_nested_tags(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-nested-tags.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-nested-tags.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-nested-tags.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

        # Idem with a style tag at the very beginning of the text.
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes2.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_import_xml_on_prefixed_package(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2-prefixed.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-extra-nodes2-prefixed.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-with-extra-nodes2.xml"), "r") as xml_file:
            with idml_file.prefix("myprefix") as prefixed_f:
                with prefixed_f.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                    xml = f.export_xml()
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

    def test_import_xml_with_setcontent_false(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-setcontent-false.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-with-setcontent-false.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-with-setcontent-false.xml"), "r") as xml_file:
            with idml_file.prefix("myprefix") as prefixed_f:
                with prefixed_f.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                    xml = f.export_xml()
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

    def test_import_xml_without_picture(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-without-picture.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-without-picture.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-without-picture.xml"), "r") as xml_file:
            with idml_file.prefix("myprefix") as prefixed_f:
                with prefixed_f.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                    xml = f.export_xml()
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

    def test_import_xml_ignore_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-ignorecontent.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-ignorecontent.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-ignorecontent.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_import_xml_force_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_import_xml_force_content2(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent2.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent2.idml")) as idml_file,\
             open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent2.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_import_xml_force_content3(self):
        """Forcecontent flag is not a direct child of ignorecontent flag. """
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent3.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-forcecontent3.idml")) as idml_file,\
            open(os.path.join(XML_DIR, "article-1photo_import-xml-forcecontent3.xml"), "r") as xml_file:
            with idml_file.import_xml(xml_file.read(), at="/Root/module[1]") as f:
                xml = f.export_xml()
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

    def test_export_as_tree(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-nested-xml.idml")) as idml_file:
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
                                                'content': [u'Pelé dos Santos (Seu Jorge)'],
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
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml")) as idml_file:
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

        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-xml.idml")) as idml_file:
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

        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo-with-attributes.idml")) as idml_file:
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
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_imported-nested-xml.idml")) as idml_file:
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

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml")) as idml_file:
            self.assertRaises(BaseException, idml_file.prefix, "bad-prefix")
            with idml_file.prefix("FOO") as prefixed_f:

                # Spreads.
                self.assertEqual(set(prefixed_f.spreads), set([
                    'Spreads/Spread_FOOub6.xml',
                    'Spreads/Spread_FOOubc.xml',
                    'Spreads/Spread_FOOuc3.xml']
                ))

                with prefixed_f.open("Spreads/Spread_FOOub6.xml") as f:
                    spread = etree.fromstring(f.read())
                    self.assertEqual(spread.xpath(".//Spread[1]")[0].get("Self"), "FOOub6")
                    self.assertEqual(spread.xpath(".//Spread[1]/Page[1]")[0].get("Self"), "FOOubb")
                    self.assertEqual(spread.xpath(".//Spread[1]/TextFrame[1]")[0].get("Self"), "FOOud8")
                    self.assertEqual(spread.xpath(".//Spread[1]/TextFrame[1]")[0].get("ParentStory"), "FOOu102")

                # Stories.
                self.assertEqual(set(prefixed_f.stories), set([
                    'Stories/Story_FOOu102.xml',
                    'Stories/Story_FOOu11b.xml',
                    'Stories/Story_FOOu139.xml',
                    'Stories/Story_FOOue4.xml']
                ))

                with prefixed_f.open("Stories/Story_FOOu102.xml") as f:
                    story = etree.fromstring(f.read())
                    self.assertEqual(story.xpath("//CharacterStyleRange")[0].get("AppliedCharacterStyle"),
                                     "FOOCharacterStyle/$ID/[No character style]")

                # XML Structure.
                self.assertXMLEqual(unicode(prefixed_f.xml_structure_pretty()),
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
                with prefixed_f.open("designmap.xml") as f:
                    designmap = etree.fromstring(f.read())
                    self.assertEqual(designmap.xpath("/Document")[0].get("StoryList"),
                                     "FOOue4 FOOu102 FOOu11b FOOu139 FOOu9c")
                    self.assertEqual(designmap.xpath(".//idPkg:Story",
                                                     namespaces={'idPkg': IDPKG_NS})[0].get("src"),
                                     "Stories/Story_FOOu139.xml")
                    self.assertEqual(designmap.xpath(".//idPkg:Spread",
                                                     namespaces={'idPkg': IDPKG_NS})[0].get("src"),
                                     "Spreads/Spread_FOOub6.xml")
                # Layer(s)
                self.assertEqual(prefixed_f.get_active_layer_name(), "Layer 1")

        # Prefixing a file with a Style / XML tag mapping.
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_import-xml-prefixed.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_import-xml-prefixed.idml")) as idml_file:
            with idml_file.prefix("FOO") as prefixed_f:
                pass

    def test_is_prefixed(self):
        with IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml")) as idml_file:
            self.assertFalse(idml_file.is_prefixed("foo"))

        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml")) as idml_file:
            with idml_file.prefix("foo") as prefixed_f:
                self.assertTrue(prefixed_f.is_prefixed("foo"))
                self.assertFalse(prefixed_f.is_prefixed("bar"))

    def test_suffix_layers(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages.idml")) as idml_file:
            with idml_file.suffix_layers(" - 23") as f:
                self.assertEqual(f.designmap.layer_nodes[0].get("Name"), "Layer 1 - 23")

    def test_insert_idml(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo.idml")) as main_idml_file,\
             IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo.idml")) as article_idml_file:

            # Always start by prefixing packages to avoid collision.
            with main_idml_file.prefix("main") as prefixed_main,\
                 article_idml_file.prefix("article1") as prefixed_article:

                with prefixed_main.insert_idml(prefixed_article,
                                               at="/Root/article[3]",
                                               only="/Root/module[1]") as f:

                    # Stories.
                    self.assertEqual(set(f.stories), set([
                        'Stories/Story_article1u188.xml',
                        'Stories/Story_article1u19f.xml',
                        'Stories/Story_article1u1db.xml',
                        'Stories/Story_mainu102.xml',
                        'Stories/Story_mainu11b.xml',
                        'Stories/Story_mainu139.xml',
                        'Stories/Story_mainudd.xml',
                        'Stories/Story_mainue4.xml']
                    ))

                    # Spreads
                    self.assertEqual(set(f.spreads), set([
                        'Spreads/Spread_mainub6.xml',
                        'Spreads/Spread_mainubc.xml',
                        'Spreads/Spread_mainuc3.xml']
                    ))

                    self.assertEqual([(elt.tag, dict(elt.attrib)) for elt in
                                      f.get_spread_object_by_name("Spreads/Spread_mainub6.xml").dom.iter()], [
                        ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                         {'DOMVersion': '7.5'}),
                        ('Spread',
                         {'AllowPageShuffle': 'true',
                          'BindingLocation': '0',
                          'FlattenerOverride': 'Default',
                          'ItemTransform': '1 0 0 1 0 0',
                          'PageCount': '1',
                          'PageTransitionDirection': 'NotApplicable',
                          'PageTransitionDuration': 'Medium',
                          'PageTransitionType': 'None',
                          'Self': 'mainub6',
                          'ShowMasterItems': 'true'}),
                        ('FlattenerPreference',
                         {'ClipComplexRegions': 'false',
                          'ConvertAllStrokesToOutlines': 'false',
                          'ConvertAllTextToOutlines': 'false',
                          'GradientAndMeshResolution': '150',
                          'LineArtAndTextResolution': '300'}),
                        ('Properties', {}),
                        ('RasterVectorBalance', {'type': 'double'}),
                        ('Page',
                         {'AppliedMaster': 'uca',
                          'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                          'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                          'GridStartingPoint': 'TopOutside',
                          'ItemTransform': '1 0 0 1 0 -379.8425196850394',
                          'MasterPageTransform': '1 0 0 1 0 0',
                          'Name': '1',
                          'OverrideList': '',
                          'Self': 'mainubb',
                          'TabOrder': '',
                          'UseMasterGrid': 'true'}),
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
                         {'Bottom': '36',
                          'ColumnCount': '1',
                          'ColumnDirection': 'Horizontal',
                          'ColumnGutter': '12',
                          'ColumnsPositions': '0 494.92913385826773',
                          'Left': '36',
                          'Right': '36',
                          'Top': '36'}),
                        ('GridDataInformation',
                         {'CharacterAki': '0',
                          'CharacterAlignment': 'AlignEmCenter',
                          'FontStyle': 'Regular',
                          'GridAlignment': 'AlignEmCenter',
                          'HorizontalScale': '100',
                          'LineAki': '9',
                          'LineAlignment': 'LeftOrTopLineJustify',
                          'PointSize': '12',
                          'VerticalScale': '100'}),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu102',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainud8',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -329.76377952755905',
                          'LeftDirection': '49.13385826771654 -329.76377952755905',
                          'RightDirection': '49.13385826771654 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -38.74015748031496',
                          'LeftDirection': '49.13385826771654 -38.74015748031496',
                          'RightDirection': '49.13385826771654 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 -38.74015748031496',
                          'LeftDirection': '516.8503937007873 -38.74015748031496',
                          'RightDirection': '516.8503937007873 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 -329.76377952755905',
                          'LeftDirection': '516.8503937007873 -329.76377952755905',
                          'RightDirection': '516.8503937007873 -329.76377952755905'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '467.71653543307076'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 2.842170943040401e-14 307.0866141732283',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainudb',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -329.76377952755905',
                          'LeftDirection': '49.13385826771654 -329.76377952755905',
                          'RightDirection': '49.13385826771654 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -38.74015748031496',
                          'LeftDirection': '49.13385826771654 -38.74015748031496',
                          'RightDirection': '49.13385826771654 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '236.22047244094495 -38.74015748031496',
                          'LeftDirection': '236.22047244094495 -38.74015748031496',
                          'RightDirection': '236.22047244094495 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '236.22047244094495 -329.76377952755905',
                          'LeftDirection': '236.22047244094495 -329.76377952755905',
                          'RightDirection': '236.22047244094495 -329.76377952755905'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '39.74015748031496',
                          'LeftCrop': '49.13385826771654',
                          'RightCrop': '-235.22047244094495',
                          'TopCrop': '-329.76377952755905'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 200.31496062992122 307.0866141732282',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainudd',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainuddToNode',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771655 -329.76377952755905',
                          'LeftDirection': '49.13385826771655 -329.76377952755905',
                          'RightDirection': '49.13385826771655 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771655 -38.740157480314764',
                          'LeftDirection': '49.13385826771655 -38.740157480314764',
                          'RightDirection': '49.13385826771655 -38.740157480314764'}),
                        ('PathPointType',
                         {'Anchor': '316.53543307086596 -38.740157480314764',
                          'LeftDirection': '316.53543307086596 -38.740157480314764',
                          'RightDirection': '316.53543307086596 -38.740157480314764'}),
                        ('PathPointType',
                         {'Anchor': '316.53543307086596 -329.76377952755905',
                          'LeftDirection': '316.53543307086596 -329.76377952755905',
                          'RightDirection': '316.53543307086596 -329.76377952755905'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainudf',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771657 278.74015748031496',
                          'LeftDirection': '49.13385826771657 278.74015748031496',
                          'RightDirection': '49.13385826771657 278.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771657 332.5984251968504',
                          'LeftDirection': '49.13385826771657 332.5984251968504',
                          'RightDirection': '49.13385826771657 332.5984251968504'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 332.5984251968504',
                          'LeftDirection': '516.8503937007873 332.5984251968504',
                          'RightDirection': '516.8503937007873 332.5984251968504'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 278.74015748031496',
                          'LeftDirection': '516.8503937007873 278.74015748031496',
                          'RightDirection': '516.8503937007873 278.74015748031496'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '-331.5984251968504',
                          'LeftCrop': '49.13385826771657',
                          'RightCrop': '-515.8503937007873',
                          'TopCrop': '278.74015748031496'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 277.3228346456692 -310.86614173228344',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainue4',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainuf6',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-192.28346456692918 -18.897637795275614',
                          'LeftDirection': '-192.28346456692918 -18.897637795275614',
                          'RightDirection': '-192.28346456692918 -18.897637795275614'}),
                        ('PathPointType',
                         {'Anchor': '-192.28346456692918 11.338582677165391',
                          'LeftDirection': '-192.28346456692918 11.338582677165391',
                          'RightDirection': '-192.28346456692918 11.338582677165391'}),
                        ('PathPointType',
                         {'Anchor': '192.28346456692913 11.338582677165391',
                          'LeftDirection': '192.28346456692913 11.338582677165391',
                          'RightDirection': '192.28346456692913 11.338582677165391'}),
                        ('PathPointType',
                         {'Anchor': '192.28346456692913 -18.897637795275614',
                          'LeftDirection': '192.28346456692913 -18.897637795275614',
                          'RightDirection': '192.28346456692913 -18.897637795275614'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '384.5669291338583'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 126.61417322834649 -189.92125984251965',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu11b',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainu12d',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-71.81102362204726 -106.77165354330708',
                          'LeftDirection': '-71.81102362204726 -106.77165354330708',
                          'RightDirection': '-71.81102362204726 -106.77165354330708'}),
                        ('PathPointType',
                         {'Anchor': '-71.81102362204726 151.1811023622045',
                          'LeftDirection': '-71.81102362204726 151.1811023622045',
                          'RightDirection': '-71.81102362204726 151.1811023622045'}),
                        ('PathPointType',
                         {'Anchor': '233.38582677165348 151.1811023622045',
                          'LeftDirection': '233.38582677165348 151.1811023622045',
                          'RightDirection': '233.38582677165348 151.1811023622045'}),
                        ('PathPointType',
                         {'Anchor': '233.38582677165348 -106.77165354330708',
                          'LeftDirection': '233.38582677165348 -106.77165354330708',
                          'RightDirection': '233.38582677165348 -106.77165354330708'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '305.19685039370074',
                          'VerticalBalanceColumns': 'true'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainu135',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '365.6692913385827 -296.6929133858267',
                          'LeftDirection': '365.6692913385827 -296.6929133858267',
                          'RightDirection': '365.6692913385827 -296.6929133858267'}),
                        ('PathPointType',
                         {'Anchor': '365.6692913385827 -124.7244094488189',
                          'LeftDirection': '365.6692913385827 -124.7244094488189',
                          'RightDirection': '365.6692913385827 -124.7244094488189'}),
                        ('PathPointType',
                         {'Anchor': '510.23622047244095 -124.7244094488189',
                          'LeftDirection': '510.23622047244095 -124.7244094488189',
                          'RightDirection': '510.23622047244095 -124.7244094488189'}),
                        ('PathPointType',
                         {'Anchor': '510.23622047244095 -296.6929133858267',
                          'LeftDirection': '510.23622047244095 -296.6929133858267',
                          'RightDirection': '510.23622047244095 -296.6929133858267'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '125.7244094488189',
                          'LeftCrop': '365.6692913385827',
                          'RightCrop': '-509.23622047244095',
                          'TopCrop': '-296.6929133858267'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 437.9527559055118 -97.79527559055123',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu139',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainu14b',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-72.28346456692913 -26.929133858267733',
                          'LeftDirection': '-72.28346456692913 -26.929133858267733',
                          'RightDirection': '-72.28346456692913 -26.929133858267733'}),
                        ('PathPointType',
                         {'Anchor': '-72.28346456692913 55.27559055118115',
                          'LeftDirection': '-72.28346456692913 55.27559055118115',
                          'RightDirection': '-72.28346456692913 55.27559055118115'}),
                        ('PathPointType',
                         {'Anchor': '72.28346456692913 55.27559055118115',
                          'LeftDirection': '72.28346456692913 55.27559055118115',
                          'RightDirection': '72.28346456692913 55.27559055118115'}),
                        ('PathPointType',
                         {'Anchor': '72.28346456692913 -26.929133858267733',
                          'LeftDirection': '72.28346456692913 -26.929133858267733',
                          'RightDirection': '72.28346456692913 -26.929133858267733'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '144.56692913385825'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 109.417322834645740 -76.62992125984261',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'Self': 'article1u182',
                          'StoryTitle': '$ID/',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '144.56692913385828 58.582677165354326',
                          'LeftDirection': '144.56692913385828 58.582677165354326',
                          'RightDirection': '144.56692913385828 58.582677165354326'}),
                        ('PathPointType',
                         {'Anchor': '144.56692913385828 199.46456692913392',
                          'LeftDirection': '144.56692913385828 199.46456692913392',
                          'RightDirection': '144.56692913385828 199.46456692913392'}),
                        ('PathPointType',
                         {'Anchor': '403.46456692913387 199.46456692913392',
                          'LeftDirection': '403.46456692913387 199.46456692913392',
                          'RightDirection': '403.46456692913387 199.46456692913392'}),
                        ('PathPointType',
                         {'Anchor': '403.46456692913387 58.582677165354326',
                          'LeftDirection': '403.46456692913387 58.582677165354326',
                          'RightDirection': '403.46456692913387 58.582677165354326'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ContourOption',
                         {'ContourPathName': '$ID/',
                          'ContourType': 'SameAsClipping',
                          'IncludeInsideEdges': 'false'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'FittingOnEmptyFrame': 'FillProportionally'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('Image',
                         {'ActualPpi': '72 72',
                          'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'EffectivePpi': '84 84',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ImageRenderingIntent': 'UseColorSettings',
                          'ImageTypeName': '$ID/JPEG',
                          'ItemTransform': '0.8544476494893585 0 0 0.8544476494893584 144.56692913385828 58.582677165354326',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Name': '$ID/',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'Self': 'article1u216',
                          'Space': '$ID/#Links_RGB',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('Profile', {'type': 'string'}),
                        ('GraphicBounds',
                         {'Bottom': '360',
                          'Left': '0',
                          'Right': '303',
                          'Top': '0'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ContourOption',
                         {'ContourPathName': '$ID/',
                          'ContourType': 'SameAsClipping',
                          'IncludeInsideEdges': 'false'}),
                        ('MetadataPacketPreference', {}),
                        ('Properties', {}),
                        ('Contents', {}),
                        ('Link',
                         {'AssetID': '$ID/',
                          'AssetURL': '$ID/',
                          'CanEmbed': 'true',
                          'CanPackage': 'true',
                          'CanUnembed': 'true',
                          'ExportPolicy': 'NoAutoExport',
                          'ImportPolicy': 'NoAutoImport',
                          'LinkClassID': '35906',
                          'LinkClientID': '257',
                          'LinkImportModificationTime': '2012-03-21T01:11:38',
                          'LinkImportStamp': 'file 129767622980000000 27644',
                          'LinkImportTime': '2014-09-24T14:47:22',
                          'LinkObjectModified': 'false',
                          'LinkResourceFormat': '$ID/JPEG',
                          'LinkResourceModified': 'false',
                          'LinkResourceSize': '0~6bfc',
                          'LinkResourceURI': 'file:/Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/git/simpleidml/tests/regressiontests/IDML/media/default.jpg',
                          'Self': 'article1u21a',
                          'ShowInUI': 'true',
                          'StoredState': 'Normal'}),
                        ('ClippingPathSettings',
                         {'AppliedPathName': '$ID/',
                          'ClippingType': 'None',
                          'IncludeInsideEdges': 'false',
                          'Index': '-1',
                          'InsetFrame': '0',
                          'InvertPath': 'false',
                          'RestrictToFrame': 'false',
                          'Threshold': '25',
                          'Tolerance': '2',
                          'UseHighResolutionImage': 'true'}),
                        ('ImageIOPreference',
                         {'AllowAutoEmbedding': 'true',
                          'AlphaChannelName': '$ID/',
                          'ApplyPhotoshopClippingPath': 'true'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 329.480314960629896 148.34645669291330',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u188',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u185',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-76.06299212598424 -19.842519685039377',
                          'LeftDirection': '-76.06299212598424 -19.842519685039377',
                          'RightDirection': '-76.06299212598424 -19.842519685039377'}),
                        ('PathPointType',
                         {'Anchor': '-76.06299212598424 -0.9448818897638205',
                          'LeftDirection': '-76.06299212598424 -0.9448818897638205',
                          'RightDirection': '-76.06299212598424 -0.9448818897638205'}),
                        ('PathPointType',
                         {'Anchor': '182.83464566929132 -0.9448818897638205',
                          'LeftDirection': '182.83464566929132 -0.9448818897638205',
                          'RightDirection': '182.83464566929132 -0.9448818897638205'}),
                        ('PathPointType',
                         {'Anchor': '182.83464566929132 -19.842519685039377',
                          'LeftDirection': '182.83464566929132 -19.842519685039377',
                          'RightDirection': '182.83464566929132 -19.842519685039377'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '1',
                          'TextColumnFixedWidth': '258.89763779527556',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 390.425196850393686 216.37795275590547',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u19f',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u19c',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-137.00787401574803 -64.25196850393701',
                          'LeftDirection': '-137.00787401574803 -64.25196850393701',
                          'RightDirection': '-137.00787401574803 -64.25196850393701'}),
                        ('PathPointType',
                         {'Anchor': '-137.00787401574803 51.968503937007945',
                          'LeftDirection': '-137.00787401574803 51.968503937007945',
                          'RightDirection': '-137.00787401574803 51.968503937007945'}),
                        ('PathPointType',
                         {'Anchor': '121.88976377952753 51.968503937007945',
                          'LeftDirection': '121.88976377952753 51.968503937007945',
                          'RightDirection': '121.88976377952753 51.968503937007945'}),
                        ('PathPointType',
                         {'Anchor': '121.88976377952753 -64.25196850393701',
                          'LeftDirection': '121.88976377952753 -64.25196850393701',
                          'RightDirection': '121.88976377952753 -64.25196850393701'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '2',
                          'TextColumnFixedWidth': '123.44881889763778',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 107.716535433070840 -42.51968503937020',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u1db',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u1d4',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '141.73228346456693 19.84251968503935',
                          'LeftDirection': '141.73228346456693 19.84251968503935',
                          'RightDirection': '141.73228346456693 19.84251968503935'}),
                        ('PathPointType',
                         {'Anchor': '141.73228346456693 310.8661417322836',
                          'LeftDirection': '141.73228346456693 310.8661417322836',
                          'RightDirection': '141.73228346456693 310.8661417322836'}),
                        ('PathPointType',
                         {'Anchor': '409.13385826771633 310.8661417322836',
                          'LeftDirection': '409.13385826771633 310.8661417322836',
                          'RightDirection': '409.13385826771633 310.8661417322836'}),
                        ('PathPointType',
                         {'Anchor': '409.13385826771633 19.84251968503935',
                          'LeftDirection': '409.13385826771633 19.84251968503935',
                          'RightDirection': '409.13385826771633 19.84251968503935'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '1',
                          'TextColumnFixedWidth': '267.4015748031494',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'})
                    ])

                    self.assertEqual([(elt.tag, dict(elt.attrib)) for elt in f.get_spread_object_by_name("Spreads/Spread_mainuc3.xml").dom.iter()], [
                        ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                         {'DOMVersion': '7.5'}),
                        ('Spread', {
                            'PageTransitionDirection': 'NotApplicable',
                            'BindingLocation': '1',
                            'PageTransitionDuration': 'Medium',
                            'ShowMasterItems': 'true',
                            'PageTransitionType': 'None',
                            'PageCount': '1',
                            'Self': 'mainuc3',
                            'AllowPageShuffle': 'true',
                            'ItemTransform': '1 0 0 1 0 1879.3700787401576',
                            'FlattenerOverride': 'Default'
                        }),
                        ('FlattenerPreference', {
                            'ConvertAllTextToOutlines': 'false',
                            'GradientAndMeshResolution': '150',
                            'ConvertAllStrokesToOutlines': 'false',
                            'ClipComplexRegions': 'false',
                            'LineArtAndTextResolution': '300'
                        }),
                        ('Properties', {}),
                        ('RasterVectorBalance', {'type': 'double'}),
                        ('Page', {
                            'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                            'Name': '4',
                            'Self': 'mainuc8',
                            'UseMasterGrid': 'true',
                            'MasterPageTransform': '1 0 0 1 0 0',
                            'TabOrder': '',
                            'OverrideList': '',
                            'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394',
                            'GridStartingPoint': 'TopOutside',
                            'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                            'AppliedMaster': 'uca'
                        }),
                        ('Properties', {}),
                        ('Descriptor', {'type': 'list'}),
                        ('ListItem', {'type': 'string'}),
                        ('ListItem', {'type': 'enumeration'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'long'}),
                        ('ListItem', {'type': 'string'}),
                        ('PageColor', {'type': 'enumeration'}),
                        ('MarginPreference', {
                            'ColumnCount': '1',
                            'Right': '36',
                            'Bottom': '36',
                            'Top': '36',
                            'ColumnGutter': '12',
                            'ColumnsPositions': '0 494.92913385826773',
                            'ColumnDirection': 'Horizontal',
                            'Left': '36'
                        }),
                        ('GridDataInformation', {
                            'LineAki': '9',
                            'FontStyle': 'Regular',
                            'PointSize': '12',
                            'CharacterAki': '0',
                            'GridAlignment': 'AlignEmCenter',
                            'LineAlignment': 'LeftOrTopLineJustify',
                            'HorizontalScale': '100',
                            'CharacterAlignment': 'AlignEmCenter',
                            'VerticalScale': '100'
                        }),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'})
                    ])

                    # The XML Structure has integrated the new file.
                    self.assertXMLEqual(unicode(f.xml_structure_pretty()), """<Root Self="maindi2">
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
                    with f.open("designmap.xml") as df:
                        designmap = etree.fromstring(df.read())
                        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList").split(" "), [
                            "mainue4",
                            "mainu102",
                            "mainu11b",
                            "mainu139",
                            "mainu9c",
                            "mainudd",
                            "article1u1db",
                            "article1u188",
                            "article1u19f"
                        ])
                        self.assertEqual(len(designmap.xpath("/Document/idPkg:Story",
                                                             namespaces={'idPkg': IDPKG_NS})), 8)

                    # Styles.
                    styles = [[style.get("Self") for style in style_group.iterchildren()]
                              for style_group in f.style_groups]
                    self.assertEqual(styles, [
                        [
                            'mainCharacterStyle/$ID/[No character style]',
                            'article1CharacterStyle/$ID/[No character style]',
                            'article1CharacterStyle/MyBoldStyle',
                        ],
                        [
                            'mainParagraphStyle/$ID/[No paragraph style]',
                            'mainParagraphStyle/$ID/NormalParagraphStyle',
                            'article1ParagraphStyle/$ID/[No paragraph style]',
                            'article1ParagraphStyle/$ID/NormalParagraphStyle'
                        ],
                        [
                            'mainCellStyle/$ID/[None]', 'article1CellStyle/$ID/[None]'
                        ],
                        [
                            'mainTableStyle/$ID/[No table style]',
                            'mainTableStyle/$ID/[Basic Table]',
                            'article1TableStyle/$ID/[No table style]',
                            'article1TableStyle/$ID/[Basic Table]'
                        ],
                        [
                            'mainObjectStyle/$ID/[None]',
                            'mainObjectStyle/$ID/[Normal Graphics Frame]',
                            'mainObjectStyle/$ID/[Normal Text Frame]',
                            'mainObjectStyle/$ID/[Normal Grid]',
                            'article1ObjectStyle/$ID/[None]',
                            'article1ObjectStyle/$ID/[Normal Graphics Frame]',
                            'article1ObjectStyle/$ID/[Normal Text Frame]',
                            'article1ObjectStyle/$ID/[Normal Grid]'
                        ]
                    ])

                    # Style mapping.
                    self.assertEqual(f.style_mapping.character_style_mapping,
                                     {'MyBoldTag': 'article1CharacterStyle/MyBoldStyle'})

                    # Graphics.
                    self.assertTrue(f.graphic.dom.xpath(".//Swatch[@Self='article1Swatch/None']"))

    def test_insert_idml_with_complex_source(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-complex.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-1photo.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-1photo.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-complex.idml")) as main_idml_file,\
             IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-1photo.idml")) as article_idml_file:

            # Always start by prefixing packages to avoid collision.
            with main_idml_file.prefix("main") as prefixed_main,\
                 article_idml_file.prefix("article1") as prefixed_article:

                with prefixed_main.insert_idml(prefixed_article,
                                               at="/Root/article[3]",
                                               only="/Root/module[1]") as f:

                    # Stories.
                    self.assertEqual(set(f.stories), set([
                        'Stories/Story_article1u188.xml',
                        'Stories/Story_article1u19f.xml',
                        'Stories/Story_article1u1db.xml',
                        'Stories/Story_mainu102.xml',
                        'Stories/Story_mainu11b.xml',
                        'Stories/Story_mainu139.xml',
                        'Stories/Story_mainudd.xml',
                        'Stories/Story_mainue4.xml']
                    ))

                    # Spreads
                    self.assertEqual(set(f.spreads), set([
                        'Spreads/Spread_mainub6.xml',
                        'Spreads/Spread_mainubc.xml',
                        'Spreads/Spread_mainuc3.xml']
                    ))

                    self.assertEqual([(elt.tag, dict(elt.attrib)) for elt in
                                      f.get_spread_object_by_name("Spreads/Spread_mainub6.xml").dom.iter()], [
                        ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                         {'DOMVersion': '7.5'}),
                        ('Spread',
                         {'AllowPageShuffle': 'true',
                          'BindingLocation': '0',
                          'FlattenerOverride': 'Default',
                          'ItemTransform': '1 0 0 1 0 0',
                          'PageCount': '1',
                          'PageTransitionDirection': 'NotApplicable',
                          'PageTransitionDuration': 'Medium',
                          'PageTransitionType': 'None',
                          'Self': 'mainub6',
                          'ShowMasterItems': 'true'}),
                        ('FlattenerPreference',
                         {'ClipComplexRegions': 'false',
                          'ConvertAllStrokesToOutlines': 'false',
                          'ConvertAllTextToOutlines': 'false',
                          'GradientAndMeshResolution': '150',
                          'LineArtAndTextResolution': '300'}),
                        ('Properties', {}),
                        ('RasterVectorBalance', {'type': 'double'}),
                        ('Page',
                         {'AppliedMaster': 'uca',
                          'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                          'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                          'GridStartingPoint': 'TopOutside',
                          'ItemTransform': '1 0 0 1 0 -379.8425196850394',
                          'MasterPageTransform': '1 0 0 1 0 0',
                          'Name': '1',
                          'OverrideList': '',
                          'Self': 'mainubb',
                          'TabOrder': '',
                          'UseMasterGrid': 'true'}),
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
                         {'Bottom': '36',
                          'ColumnCount': '1',
                          'ColumnDirection': 'Horizontal',
                          'ColumnGutter': '12',
                          'ColumnsPositions': '0 494.92913385826773',
                          'Left': '36',
                          'Right': '36',
                          'Top': '36'}),
                        ('GridDataInformation',
                         {'CharacterAki': '0',
                          'CharacterAlignment': 'AlignEmCenter',
                          'FontStyle': 'Regular',
                          'GridAlignment': 'AlignEmCenter',
                          'HorizontalScale': '100',
                          'LineAki': '9',
                          'LineAlignment': 'LeftOrTopLineJustify',
                          'PointSize': '12',
                          'VerticalScale': '100'}),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu102',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainud8',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -329.76377952755905',
                          'LeftDirection': '49.13385826771654 -329.76377952755905',
                          'RightDirection': '49.13385826771654 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -38.74015748031496',
                          'LeftDirection': '49.13385826771654 -38.74015748031496',
                          'RightDirection': '49.13385826771654 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 -38.74015748031496',
                          'LeftDirection': '516.8503937007873 -38.74015748031496',
                          'RightDirection': '516.8503937007873 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 -329.76377952755905',
                          'LeftDirection': '516.8503937007873 -329.76377952755905',
                          'RightDirection': '516.8503937007873 -329.76377952755905'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '467.71653543307076'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 2.842170943040401e-14 307.0866141732283',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainudb',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -329.76377952755905',
                          'LeftDirection': '49.13385826771654 -329.76377952755905',
                          'RightDirection': '49.13385826771654 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771654 -38.74015748031496',
                          'LeftDirection': '49.13385826771654 -38.74015748031496',
                          'RightDirection': '49.13385826771654 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '236.22047244094495 -38.74015748031496',
                          'LeftDirection': '236.22047244094495 -38.74015748031496',
                          'RightDirection': '236.22047244094495 -38.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '236.22047244094495 -329.76377952755905',
                          'LeftDirection': '236.22047244094495 -329.76377952755905',
                          'RightDirection': '236.22047244094495 -329.76377952755905'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '39.74015748031496',
                          'LeftCrop': '49.13385826771654',
                          'RightCrop': '-235.22047244094495',
                          'TopCrop': '-329.76377952755905'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 200.31496062992122 307.0866141732282',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainudd',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainuddToNode',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771655 -329.76377952755905',
                          'LeftDirection': '49.13385826771655 -329.76377952755905',
                          'RightDirection': '49.13385826771655 -329.76377952755905'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771655 -38.740157480314764',
                          'LeftDirection': '49.13385826771655 -38.740157480314764',
                          'RightDirection': '49.13385826771655 -38.740157480314764'}),
                        ('PathPointType',
                         {'Anchor': '316.53543307086596 -38.740157480314764',
                          'LeftDirection': '316.53543307086596 -38.740157480314764',
                          'RightDirection': '316.53543307086596 -38.740157480314764'}),
                        ('PathPointType',
                         {'Anchor': '316.53543307086596 -329.76377952755905',
                          'LeftDirection': '316.53543307086596 -329.76377952755905',
                          'RightDirection': '316.53543307086596 -329.76377952755905'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainudf',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771657 278.74015748031496',
                          'LeftDirection': '49.13385826771657 278.74015748031496',
                          'RightDirection': '49.13385826771657 278.74015748031496'}),
                        ('PathPointType',
                         {'Anchor': '49.13385826771657 332.5984251968504',
                          'LeftDirection': '49.13385826771657 332.5984251968504',
                          'RightDirection': '49.13385826771657 332.5984251968504'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 332.5984251968504',
                          'LeftDirection': '516.8503937007873 332.5984251968504',
                          'RightDirection': '516.8503937007873 332.5984251968504'}),
                        ('PathPointType',
                         {'Anchor': '516.8503937007873 278.74015748031496',
                          'LeftDirection': '516.8503937007873 278.74015748031496',
                          'RightDirection': '516.8503937007873 278.74015748031496'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '-331.5984251968504',
                          'LeftCrop': '49.13385826771657',
                          'RightCrop': '-515.8503937007873',
                          'TopCrop': '278.74015748031496'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 277.3228346456692 -310.86614173228344',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainue4',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainuf6',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-192.28346456692918 -18.897637795275614',
                          'LeftDirection': '-192.28346456692918 -18.897637795275614',
                          'RightDirection': '-192.28346456692918 -18.897637795275614'}),
                        ('PathPointType',
                         {'Anchor': '-192.28346456692918 11.338582677165391',
                          'LeftDirection': '-192.28346456692918 11.338582677165391',
                          'RightDirection': '-192.28346456692918 11.338582677165391'}),
                        ('PathPointType',
                         {'Anchor': '192.28346456692913 11.338582677165391',
                          'LeftDirection': '192.28346456692913 11.338582677165391',
                          'RightDirection': '192.28346456692913 11.338582677165391'}),
                        ('PathPointType',
                         {'Anchor': '192.28346456692913 -18.897637795275614',
                          'LeftDirection': '192.28346456692913 -18.897637795275614',
                          'RightDirection': '192.28346456692913 -18.897637795275614'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '384.5669291338583'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 126.61417322834649 -189.92125984251965',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu11b',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainu12d',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-71.81102362204726 -106.77165354330708',
                          'LeftDirection': '-71.81102362204726 -106.77165354330708',
                          'RightDirection': '-71.81102362204726 -106.77165354330708'}),
                        ('PathPointType',
                         {'Anchor': '-71.81102362204726 151.1811023622045',
                          'LeftDirection': '-71.81102362204726 151.1811023622045',
                          'RightDirection': '-71.81102362204726 151.1811023622045'}),
                        ('PathPointType',
                         {'Anchor': '233.38582677165348 151.1811023622045',
                          'LeftDirection': '233.38582677165348 151.1811023622045',
                          'RightDirection': '233.38582677165348 151.1811023622045'}),
                        ('PathPointType',
                         {'Anchor': '233.38582677165348 -106.77165354330708',
                          'LeftDirection': '233.38582677165348 -106.77165354330708',
                          'RightDirection': '233.38582677165348 -106.77165354330708'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '305.19685039370074',
                          'VerticalBalanceColumns': 'true'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 0 0',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'Self': 'mainu135',
                          'StoryTitle': '$ID/',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '365.6692913385827 -296.6929133858267',
                          'LeftDirection': '365.6692913385827 -296.6929133858267',
                          'RightDirection': '365.6692913385827 -296.6929133858267'}),
                        ('PathPointType',
                         {'Anchor': '365.6692913385827 -124.7244094488189',
                          'LeftDirection': '365.6692913385827 -124.7244094488189',
                          'RightDirection': '365.6692913385827 -124.7244094488189'}),
                        ('PathPointType',
                         {'Anchor': '510.23622047244095 -124.7244094488189',
                          'LeftDirection': '510.23622047244095 -124.7244094488189',
                          'RightDirection': '510.23622047244095 -124.7244094488189'}),
                        ('PathPointType',
                         {'Anchor': '510.23622047244095 -296.6929133858267',
                          'LeftDirection': '510.23622047244095 -296.6929133858267',
                          'RightDirection': '510.23622047244095 -296.6929133858267'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'BottomCrop': '125.7244094488189',
                          'LeftCrop': '365.6692913385827',
                          'RightCrop': '-509.23622047244095',
                          'TopCrop': '-296.6929133858267'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomImageSizeOption': 'SizeRelativeToPageWidth',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssEm',
                          'UseImagePageBreak': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'mainObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'ItemLayer': 'mainub3',
                          'ItemTransform': '1 0 0 1 437.9527559055118 -97.79527559055123',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'ParentStory': 'mainu139',
                          'PreviousTextFrame': 'n',
                          'Self': 'mainu14b',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-72.28346456692913 -26.929133858267733',
                          'LeftDirection': '-72.28346456692913 -26.929133858267733',
                          'RightDirection': '-72.28346456692913 -26.929133858267733'}),
                        ('PathPointType',
                         {'Anchor': '-72.28346456692913 55.27559055118115',
                          'LeftDirection': '-72.28346456692913 55.27559055118115',
                          'RightDirection': '-72.28346456692913 55.27559055118115'}),
                        ('PathPointType',
                         {'Anchor': '72.28346456692913 55.27559055118115',
                          'LeftDirection': '72.28346456692913 55.27559055118115',
                          'RightDirection': '72.28346456692913 55.27559055118115'}),
                        ('PathPointType',
                         {'Anchor': '72.28346456692913 -26.929133858267733',
                          'LeftDirection': '72.28346456692913 -26.929133858267733',
                          'RightDirection': '72.28346456692913 -26.929133858267733'}),
                        ('TextFramePreference',
                         {'TextColumnFixedWidth': '144.56692913385825'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('Rectangle',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'ContentType': 'GraphicType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 109.417322834645740 -76.62992125984261',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'Self': 'article1u182',
                          'StoryTitle': '$ID/',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '144.56692913385828 58.582677165354326',
                          'LeftDirection': '144.56692913385828 58.582677165354326',
                          'RightDirection': '144.56692913385828 58.582677165354326'}),
                        ('PathPointType',
                         {'Anchor': '144.56692913385828 199.46456692913392',
                          'LeftDirection': '144.56692913385828 199.46456692913392',
                          'RightDirection': '144.56692913385828 199.46456692913392'}),
                        ('PathPointType',
                         {'Anchor': '403.46456692913387 199.46456692913392',
                          'LeftDirection': '403.46456692913387 199.46456692913392',
                          'RightDirection': '403.46456692913387 199.46456692913392'}),
                        ('PathPointType',
                         {'Anchor': '403.46456692913387 58.582677165354326',
                          'LeftDirection': '403.46456692913387 58.582677165354326',
                          'RightDirection': '403.46456692913387 58.582677165354326'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ContourOption',
                         {'ContourPathName': '$ID/',
                          'ContourType': 'SameAsClipping',
                          'IncludeInsideEdges': 'false'}),
                        ('InCopyExportOption',
                         {'IncludeAllResources': 'false',
                          'IncludeGraphicProxies': 'true'}),
                        ('FrameFittingOption',
                         {'FittingOnEmptyFrame': 'FillProportionally'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('Image',
                         {'ActualPpi': '72 72',
                          'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'EffectivePpi': '84 84',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ImageRenderingIntent': 'UseColorSettings',
                          'ImageTypeName': '$ID/JPEG',
                          'ItemTransform': '0.8544476494893585 0 0 0.8544476494893584 144.56692913385828 58.582677165354326',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Name': '$ID/',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'Self': 'article1u216',
                          'Space': '$ID/#Links_RGB',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('Profile', {'type': 'string'}),
                        ('GraphicBounds',
                         {'Bottom': '360',
                          'Left': '0',
                          'Right': '303',
                          'Top': '0'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ContourOption',
                         {'ContourPathName': '$ID/',
                          'ContourType': 'SameAsClipping',
                          'IncludeInsideEdges': 'false'}),
                        ('MetadataPacketPreference', {}),
                        ('Properties', {}),
                        ('Contents', {}),
                        ('Link',
                         {'AssetID': '$ID/',
                          'AssetURL': '$ID/',
                          'CanEmbed': 'true',
                          'CanPackage': 'true',
                          'CanUnembed': 'true',
                          'ExportPolicy': 'NoAutoExport',
                          'ImportPolicy': 'NoAutoImport',
                          'LinkClassID': '35906',
                          'LinkClientID': '257',
                          'LinkImportModificationTime': '2012-03-21T01:11:38',
                          'LinkImportStamp': 'file 129767622980000000 27644',
                          'LinkImportTime': '2014-09-24T14:47:22',
                          'LinkObjectModified': 'false',
                          'LinkResourceFormat': '$ID/JPEG',
                          'LinkResourceModified': 'true',
                          'LinkResourceSize': '0~6bfc',
                          'LinkResourceURI': 'file:/Users/stan/Dropbox/Projets/Slashdev/SimpleIDML/repos/SimpleIDML/tests/regressiontests/IDML/media/default.jpg',
                          'Self': 'article1u21a',
                          'ShowInUI': 'true',
                          'StoredState': 'Normal'}),
                        ('ClippingPathSettings',
                         {'AppliedPathName': '$ID/',
                          'ClippingType': 'None',
                          'IncludeInsideEdges': 'false',
                          'Index': '-1',
                          'InsetFrame': '0',
                          'InvertPath': 'false',
                          'RestrictToFrame': 'false',
                          'Threshold': '25',
                          'Tolerance': '2',
                          'UseHighResolutionImage': 'true'}),
                        ('ImageIOPreference',
                         {'AllowAutoEmbedding': 'true',
                          'AlphaChannelName': '$ID/',
                          'ApplyPhotoshopClippingPath': 'true'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 329.480314960629896 148.34645669291330',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u188',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u185',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-76.06299212598424 -19.842519685039377',
                          'LeftDirection': '-76.06299212598424 -19.842519685039377',
                          'RightDirection': '-76.06299212598424 -19.842519685039377'}),
                        ('PathPointType',
                         {'Anchor': '-76.06299212598424 -0.9448818897638205',
                          'LeftDirection': '-76.06299212598424 -0.9448818897638205',
                          'RightDirection': '-76.06299212598424 -0.9448818897638205'}),
                        ('PathPointType',
                         {'Anchor': '182.83464566929132 -0.9448818897638205',
                          'LeftDirection': '182.83464566929132 -0.9448818897638205',
                          'RightDirection': '182.83464566929132 -0.9448818897638205'}),
                        ('PathPointType',
                         {'Anchor': '182.83464566929132 -19.842519685039377',
                          'LeftDirection': '182.83464566929132 -19.842519685039377',
                          'RightDirection': '182.83464566929132 -19.842519685039377'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '1',
                          'TextColumnFixedWidth': '258.89763779527556',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[Normal Text Frame]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 390.425196850393686 216.37795275590547',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u19f',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u19c',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '-137.00787401574803 -64.25196850393701',
                          'LeftDirection': '-137.00787401574803 -64.25196850393701',
                          'RightDirection': '-137.00787401574803 -64.25196850393701'}),
                        ('PathPointType',
                         {'Anchor': '-137.00787401574803 51.968503937007945',
                          'LeftDirection': '-137.00787401574803 51.968503937007945',
                          'RightDirection': '-137.00787401574803 51.968503937007945'}),
                        ('PathPointType',
                         {'Anchor': '121.88976377952753 51.968503937007945',
                          'LeftDirection': '121.88976377952753 51.968503937007945',
                          'RightDirection': '121.88976377952753 51.968503937007945'}),
                        ('PathPointType',
                         {'Anchor': '121.88976377952753 -64.25196850393701',
                          'LeftDirection': '121.88976377952753 -64.25196850393701',
                          'RightDirection': '121.88976377952753 -64.25196850393701'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '2',
                          'TextColumnFixedWidth': '123.44881889763778',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('TextFrame',
                         {'AppliedObjectStyle': 'article1ObjectStyle/$ID/[None]',
                          'ContentType': 'TextType',
                          'GradientFillAngle': '0',
                          'GradientFillHiliteAngle': '0',
                          'GradientFillHiliteLength': '0',
                          'GradientFillLength': '0',
                          'GradientFillStart': '0 0',
                          'GradientStrokeAngle': '0',
                          'GradientStrokeHiliteAngle': '0',
                          'GradientStrokeHiliteLength': '0',
                          'GradientStrokeLength': '0',
                          'GradientStrokeStart': '0 0',
                          'HorizontalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'ItemLayer': 'article1ua4',
                          'ItemTransform': '1 0 0 1 107.716535433070840 -42.51968503937020',
                          'LastUpdatedInterfaceChangeCount': '',
                          'LocalDisplaySetting': 'Default',
                          'Locked': 'false',
                          'Name': '$ID/',
                          'NextTextFrame': 'n',
                          'OverriddenPageItemProps': '',
                          'ParentInterfaceChangeCount': '',
                          'ParentStory': 'article1u1db',
                          'PreviousTextFrame': 'n',
                          'Self': 'article1u1d4',
                          'TargetInterfaceChangeCount': '',
                          'VerticalLayoutConstraints': 'FlexibleDimension FixedDimension FlexibleDimension',
                          'Visible': 'true'}),
                        ('Properties', {}),
                        ('PathGeometry', {}),
                        ('GeometryPathType', {'PathOpen': 'false'}),
                        ('PathPointArray', {}),
                        ('PathPointType',
                         {'Anchor': '141.73228346456693 19.84251968503935',
                          'LeftDirection': '141.73228346456693 19.84251968503935',
                          'RightDirection': '141.73228346456693 19.84251968503935'}),
                        ('PathPointType',
                         {'Anchor': '141.73228346456693 310.8661417322836',
                          'LeftDirection': '141.73228346456693 310.8661417322836',
                          'RightDirection': '141.73228346456693 310.8661417322836'}),
                        ('PathPointType',
                         {'Anchor': '409.13385826771633 310.8661417322836',
                          'LeftDirection': '409.13385826771633 310.8661417322836',
                          'RightDirection': '409.13385826771633 310.8661417322836'}),
                        ('PathPointType',
                         {'Anchor': '409.13385826771633 19.84251968503935',
                          'LeftDirection': '409.13385826771633 19.84251968503935',
                          'RightDirection': '409.13385826771633 19.84251968503935'}),
                        ('TextFramePreference',
                         {'AutoSizingReferencePoint': 'CenterPoint',
                          'AutoSizingType': 'Off',
                          'MinimumHeightForAutoSizing': '0',
                          'MinimumWidthForAutoSizing': '0',
                          'TextColumnCount': '1',
                          'TextColumnFixedWidth': '267.4015748031494',
                          'TextColumnMaxWidth': '0',
                          'UseMinimumHeightForAutoSizing': 'false',
                          'UseMinimumWidthForAutoSizing': 'false',
                          'UseNoLineBreaksForAutoSizing': 'false'}),
                        ('TextWrapPreference',
                         {'ApplyToMasterPageOnly': 'false',
                          'Inverse': 'false',
                          'TextWrapMode': 'None',
                          'TextWrapSide': 'BothSides'}),
                        ('Properties', {}),
                        ('TextWrapOffset',
                         {'Bottom': '0', 'Left': '0', 'Right': '0', 'Top': '0'}),
                        ('ObjectExportOption',
                         {'ActualTextSourceType': 'SourceXMLStructure',
                          'AltTextSourceType': 'SourceXMLStructure',
                          'ApplyTagType': 'TagFromStructure',
                          'CustomActualText': '$ID/',
                          'CustomAltText': '$ID/',
                          'CustomHeight': '$ID/',
                          'CustomHeightType': 'DefaultHeight',
                          'CustomImageAlignment': 'false',
                          'CustomImageConversion': 'false',
                          'CustomLayout': 'false',
                          'CustomLayoutType': 'AlignmentAndSpacing',
                          'CustomWidth': '$ID/',
                          'CustomWidthType': 'DefaultWidth',
                          'EpubType': '$ID/',
                          'GIFOptionsInterlaced': 'true',
                          'GIFOptionsPalette': 'AdaptivePalette',
                          'ImageAlignment': 'AlignLeft',
                          'ImageConversionType': 'JPEG',
                          'ImageExportResolution': 'Ppi300',
                          'ImagePageBreak': 'PageBreakBefore',
                          'ImageSpaceAfter': '0',
                          'ImageSpaceBefore': '0',
                          'JPEGOptionsFormat': 'BaselineEncoding',
                          'JPEGOptionsQuality': 'High',
                          'SpaceUnit': 'CssPixel',
                          'UseExistingImage': 'false',
                          'UseImagePageBreak': 'false',
                          'UseOriginalImage': 'false'}),
                        ('Properties', {}),
                        ('AltMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'}),
                        ('ActualMetadataProperty',
                         {'NamespacePrefix': '$ID/', 'PropertyPath': '$ID/'})
                    ])

                    self.assertEqual([(elt.tag, dict(elt.attrib)) for elt in
                                      f.get_spread_object_by_name("Spreads/Spread_mainubc.xml").dom.iter()], [
                        ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread', {'DOMVersion': '7.5'}),
                        ('Spread', {
                            'PageTransitionDirection': 'NotApplicable',
                            'BindingLocation': '1',
                            'PageTransitionDuration': 'Medium',
                            'ShowMasterItems': 'true',
                            'PageTransitionType': 'None',
                            'PageCount': '2',
                            'Self': 'mainubc',
                            'AllowPageShuffle': 'true',
                            'ItemTransform': '1 0 0 1 0 939.6850393700788',
                            'FlattenerOverride': 'Default'
                        }),
                        ('FlattenerPreference', {
                            'ConvertAllTextToOutlines': 'false',
                            'GradientAndMeshResolution': '150',
                            'ConvertAllStrokesToOutlines': 'false',
                            'ClipComplexRegions': 'false',
                            'LineArtAndTextResolution': '300'
                        }),
                        ('Properties', {}),
                        ('RasterVectorBalance', {'type': 'double'}),
                        ('Page', {
                            'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                            'Name': '2',
                            'Self': 'mainuc1',
                            'UseMasterGrid': 'true',
                            'MasterPageTransform': '1 0 0 1 0 0',
                            'TabOrder': '',
                            'OverrideList': '',
                            'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394',
                            'GridStartingPoint': 'TopOutside',
                            'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                            'AppliedMaster': 'uca'
                        }),
                        ('Properties', {}),
                        ('Descriptor', {'type': 'list'}),
                        ('ListItem', {'type': 'string'}),
                        ('ListItem', {'type': 'enumeration'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'long'}),
                        ('ListItem', {'type': 'string'}),
                        ('PageColor', {'type': 'enumeration'}),
                        ('MarginPreference', {
                            'ColumnCount': '1',
                            'Right': '36',
                            'Bottom': '36',
                            'Top': '36',
                            'ColumnGutter': '12',
                            'ColumnsPositions': '0 494.92913385826773',
                            'ColumnDirection': 'Horizontal',
                            'Left': '36'
                        }),
                        ('GridDataInformation', {
                            'LineAki': '9',
                            'FontStyle': 'Regular',
                            'PointSize': '12',
                            'CharacterAki': '0',
                            'GridAlignment': 'AlignEmCenter',
                            'LineAlignment': 'LeftOrTopLineJustify',
                            'HorizontalScale': '100',
                            'CharacterAlignment': 'AlignEmCenter',
                            'VerticalScale': '100'
                        }),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'}),
                        ('Page', {
                            'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                            'Name': '3',
                            'Self': 'mainuc2',
                            'UseMasterGrid': 'true',
                            'MasterPageTransform': '1 0 0 1 0 0',
                            'TabOrder': '',
                            'OverrideList': '',
                            'ItemTransform': '1 0 0 1 0 -379.8425196850394',
                            'GridStartingPoint': 'TopOutside',
                            'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                            'AppliedMaster': 'uca'
                        }),
                        ('Properties', {}),
                        ('Descriptor', {'type': 'list'}),
                        ('ListItem', {'type': 'string'}),
                        ('ListItem', {'type': 'enumeration'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'long'}),
                        ('ListItem', {'type': 'string'}),
                        ('PageColor', {'type': 'enumeration'}),
                        ('MarginPreference', {
                            'ColumnCount': '1',
                            'Right': '36',
                            'Bottom': '36',
                            'Top': '36',
                            'ColumnGutter': '12',
                            'ColumnsPositions': '0 494.92913385826773',
                            'ColumnDirection': 'Horizontal',
                            'Left': '36'
                        }),
                        ('GridDataInformation', {
                            'LineAki': '9',
                            'FontStyle': 'Regular',
                            'PointSize': '12',
                            'CharacterAki': '0',
                            'GridAlignment': 'AlignEmCenter',
                            'LineAlignment': 'LeftOrTopLineJustify',
                            'HorizontalScale': '100',
                            'CharacterAlignment': 'AlignEmCenter',
                            'VerticalScale': '100'
                        }),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'})
                    ])

                    self.assertEqual([(elt.tag, dict(elt.attrib)) for elt in
                                      f.get_spread_object_by_name("Spreads/Spread_mainuc3.xml").dom.iter()], [
                        ('{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread', {'DOMVersion': '7.5'}),
                        ('Spread', {
                            'PageTransitionDirection': 'NotApplicable',
                            'BindingLocation': '1',
                            'PageTransitionDuration': 'Medium',
                            'ShowMasterItems': 'true',
                            'PageTransitionType': 'None',
                            'PageCount': '1',
                            'Self': 'mainuc3',
                            'AllowPageShuffle': 'true',
                            'ItemTransform': '1 0 0 1 0 1879.3700787401576',
                            'FlattenerOverride': 'Default'
                        }),
                        ('FlattenerPreference', {
                            'ConvertAllTextToOutlines': 'false',
                            'GradientAndMeshResolution': '150',
                            'ConvertAllStrokesToOutlines': 'false',
                            'ClipComplexRegions': 'false',
                            'LineArtAndTextResolution': '300'
                        }),
                        ('Properties', {}),
                        ('RasterVectorBalance', {'type': 'double'}),
                        ('Page', {
                            'AppliedTrapPreset': 'TrapPreset/$ID/kDefaultTrapStyleName',
                            'Name': '4',
                            'Self': 'mainuc8',
                            'UseMasterGrid': 'true',
                            'MasterPageTransform': '1 0 0 1 0 0',
                            'TabOrder': '',
                            'OverrideList': '',
                            'ItemTransform': '1 0 0 1 -566.9291338582677 -379.8425196850394',
                            'GridStartingPoint': 'TopOutside',
                            'GeometricBounds': '0 0 759.6850393700788 566.9291338582677',
                            'AppliedMaster': 'uca'
                        }),
                        ('Properties', {}),
                        ('Descriptor', {'type': 'list'}),
                        ('ListItem', {'type': 'string'}),
                        ('ListItem', {'type': 'enumeration'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'boolean'}),
                        ('ListItem', {'type': 'long'}),
                        ('ListItem', {'type': 'string'}),
                        ('PageColor', {'type': 'enumeration'}),
                        ('MarginPreference', {
                            'ColumnCount': '1',
                            'Right': '36',
                            'Bottom': '36',
                            'Top': '36',
                            'ColumnGutter': '12',
                            'ColumnsPositions': '0 494.92913385826773',
                            'ColumnDirection': 'Horizontal',
                            'Left': '36'
                        }),
                        ('GridDataInformation', {
                            'LineAki': '9',
                            'FontStyle': 'Regular',
                            'PointSize': '12',
                            'CharacterAki': '0',
                            'GridAlignment': 'AlignEmCenter',
                            'LineAlignment': 'LeftOrTopLineJustify',
                            'HorizontalScale': '100',
                            'CharacterAlignment': 'AlignEmCenter',
                            'VerticalScale': '100'
                        }),
                        ('Properties', {}),
                        ('AppliedFont', {'type': 'string'})
                    ])

                    # The XML Structure has integrated the new file.
                    self.assertXMLEqual(unicode(f.xml_structure_pretty()), """<Root Self="maindi2">
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
                    with f.open("designmap.xml") as df:
                        designmap = etree.fromstring(df.read())
                        self.assertEqual(designmap.xpath("/Document")[0].get("StoryList").split(" "), [
                            "mainue4",
                            "mainu102",
                            "mainu11b",
                            "mainu139",
                            "mainu9c",
                            "mainudd",
                            "article1u1db",
                            "article1u188",
                            "article1u19f"
                        ])
                        self.assertEqual(len(designmap.xpath("/Document/idPkg:Story",
                                             namespaces={'idPkg': IDPKG_NS})), 8)

                    # Styles.
                    styles = [[style.get("Self") for style in style_group.iterchildren()]
                              for style_group in f.style_groups]
                    self.assertEqual(styles, [
                        [
                            'mainCharacterStyle/$ID/[No character style]',
                            'article1CharacterStyle/$ID/[No character style]',
                            'article1CharacterStyle/MyBoldStyle'
                        ],
                        [
                            'mainParagraphStyle/$ID/[No paragraph style]',
                            'mainParagraphStyle/$ID/NormalParagraphStyle',
                            'article1ParagraphStyle/$ID/[No paragraph style]',
                            'article1ParagraphStyle/$ID/NormalParagraphStyle'
                        ],
                        [
                            'mainCellStyle/$ID/[None]', 'article1CellStyle/$ID/[None]'
                        ],
                        [
                            'mainTableStyle/$ID/[No table style]',
                            'mainTableStyle/$ID/[Basic Table]',
                            'article1TableStyle/$ID/[No table style]',
                            'article1TableStyle/$ID/[Basic Table]'
                        ],
                        [
                            'mainObjectStyle/$ID/[None]',
                            'mainObjectStyle/$ID/[Normal Graphics Frame]',
                            'mainObjectStyle/$ID/[Normal Text Frame]',
                            'mainObjectStyle/$ID/[Normal Grid]',
                            'article1ObjectStyle/$ID/[None]',
                            'article1ObjectStyle/$ID/[Normal Graphics Frame]',
                            'article1ObjectStyle/$ID/[Normal Text Frame]',
                            'article1ObjectStyle/$ID/[Normal Grid]'
                        ]
                    ])

                    # Style mapping.
                    self.assertEqual(f.style_mapping.character_style_mapping,
                                     {'MyBoldTag': 'article1CharacterStyle/MyBoldStyle'})

                    # Graphics.
                    self.assertTrue(f.graphic.dom.xpath(".//Swatch[@Self='article1Swatch/None']"))

    def test_insert_idml_without_picture(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-0-photo-complex.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-0photo.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-0photo.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-0-photo-complex.idml")) as main_idml_file,\
             IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-0photo.idml")) as article_idml_file:

            # Always start by prefixing packages to avoid collision.
            with main_idml_file.prefix("main") as prefixed_main,\
                 article_idml_file.prefix("article1") as prefixed_article:

                with prefixed_main.insert_idml(prefixed_article,
                                               at="/Root/article[3]",
                                               only="/Root/module[1]") as f:

                    # Stories.
                    self.assertEqual(set(f.stories), set([
                        'Stories/Story_article1u188.xml',
                        'Stories/Story_article1u19f.xml',
                        'Stories/Story_article1u1db.xml',
                        'Stories/Story_mainu102.xml',
                        'Stories/Story_mainu11b.xml',
                        'Stories/Story_mainu139.xml',
                        'Stories/Story_mainudd.xml',
                        'Stories/Story_mainue4.xml']
                    ))

                    # Spreads
                    self.assertEqual(set(f.spreads), set([
                        'Spreads/Spread_mainub6.xml',
                        'Spreads/Spread_mainubc.xml',
                        'Spreads/Spread_mainuc3.xml']
                    ))

    def test_insert_idml_with_elements_on_same_layer(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "4-pages.idml"),
                     os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-elts-same-layer.idml"))
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-1photo-elts-same-layer.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-1photo.idml"))

        with IDMLPackage(os.path.join(OUTPUT_DIR, "4-pages-insert-article-1-photo-elts-same-layer.idml")) as main_idml_file,\
             IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-1photo.idml")) as article_idml_file:

            # Always start by prefixing packages to avoid collision.
            with main_idml_file.prefix("main") as prefixed_main,\
                 article_idml_file.prefix("article1") as prefixed_article:

                with prefixed_main.insert_idml(prefixed_article,
                                               at="/Root/article[3]",
                                               only="/Root/module[1]") as f:
                    pass  # TODO: some tests. But you can check the result against expected.

    def test_remove_content(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "article-1photo_imported-xml.idml"),
                     os.path.join(OUTPUT_DIR, "article-1photo_imported-xml.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "article-1photo_imported-xml.idml")) as idml_file:
            with idml_file.remove_content(under="/Root/module/Story") as f:
                self.assertXMLEqual(unicode(f.xml_structure_pretty()),
u"""<Root Self="di3">
  <module XMLContent="u10d" Self="di3i4">
    <main_picture XMLContent="udf" Self="di3i4i1"/>
    <headline XMLContent="ue1" Self="di3i4i2"/>
    <Story XMLContent="uf7" Self="di3i4i3"/>
  </module>
</Root>
""")

    def test_merge_layers(self):
        shutil.copy2(os.path.join(IDMLFILES_DIR, "2articles-1photo.idml"),
                     os.path.join(OUTPUT_DIR, "2articles-1photo-merged_layers.idml"))
        with IDMLPackage(os.path.join(OUTPUT_DIR, "2articles-1photo-merged_layers.idml")) as idml_file:
            with idml_file.merge_layers("All layers") as f:
                self.assertEqual(len(f.designmap.layer_nodes), 1)
                self.assertEqual(f.designmap.active_layer, f.designmap.layer_nodes[0].get("Self"))
                self.assertEqual(len(f.referenced_layers), 1)
                self.assertEqual(f.referenced_layers[0], f.designmap.layer_nodes[0].get("Self"))

    def test_add_page_from_idml(self):
        edito_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-edito.idml")
        courrier_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-courrier-des-lecteurs.idml")
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-edito.idml"), edito_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), courrier_idml_filename)

        with IDMLPackage(edito_idml_filename) as edito_idml_file,\
             IDMLPackage(courrier_idml_filename) as courrier_idml_file:

            # Always start by prefixing packages to avoid collision.
            with edito_idml_file.prefix("edito") as prefixed_edito,\
                 courrier_idml_file.prefix("courrier") as prefixed_courrier:

                self.assertEqual(len(prefixed_edito.pages), 2)
                with prefixed_edito.add_page_from_idml(prefixed_courrier,
                                                       page_number=1,
                                                       at="/Root",
                                                       only="/Root/page[1]") as new_idml:
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

    @unittest.skipIf(os.environ.get("TRAVIS"),
                     "This needs to be fixed. Gives some weird results on Travis C.I.")
    def test_add_pages_from_idml(self):
        edito_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-edito.idml")
        courrier_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-courrier-des-lecteurs.idml")
        bloc_notes_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-bloc-notes.idml")
        bloc_notes2_idml_filename = os.path.join(OUTPUT_DIR, "magazineA-bloc-notes2.idml")
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-edito.idml"), edito_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), courrier_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-bloc-notes.idml"), bloc_notes_idml_filename)
        shutil.copy2(os.path.join(IDMLFILES_DIR, "magazineA-bloc-notes.idml"), bloc_notes2_idml_filename)

        with IDMLPackage(edito_idml_filename) as edito_idml_file,\
            IDMLPackage(courrier_idml_filename) as courrier_idml_file,\
            IDMLPackage(bloc_notes_idml_filename) as bloc_notes_idml_file,\
            IDMLPackage(bloc_notes2_idml_filename) as bloc_notes2_idml_file:

            # Always start by prefixing packages to avoid collision.
            with edito_idml_file.prefix("edito") as prefixed_edito,\
                 courrier_idml_file.prefix("courrier") as prefixed_courrier,\
                 bloc_notes_idml_file.prefix("blocnotes") as prefixed_bnotes,\
                 bloc_notes2_idml_file.prefix("blocnotes2") as prefixed_bnotes2:

                packages_to_add = [
                    (prefixed_courrier, 1, "/Root", "/Root/page[1]"),
                    (prefixed_bnotes, 1, "/Root", "/Root/page[1]"),
                    (prefixed_bnotes2, 2, "/Root", "/Root/page[2]"),
                ]
                with prefixed_edito.add_pages_from_idml(packages_to_add) as new_idml:
                    self.assertEqual(len(new_idml.pages), 5)
                    self.assertEqual(set(new_idml.spreads), set([
                        'Spreads/Spread_editoub6.xml',
                        'Spreads/Spread_editoubc.xml',
                        'Spreads/Spread_editoubd.xml']
                    ))

    @unittest.skipIf(os.environ.get("TRAVIS"),
                     "This needs to be fixed. Gives some weird results on Travis C.I.")
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

        with IDMLPackage(magazineA_idml_filename) as magazineA_idml_file,\
            IDMLPackage(edito_idml_filename) as edito_idml_file,\
            IDMLPackage(courrier_idml_filename) as courrier_idml_file,\
            IDMLPackage(bloc_notes_idml_filename) as bloc_notes_idml_file:

            # Always start by prefixing packages to avoid collision.
            with magazineA_idml_file.prefix("mag") as prefixed_mag,\
                 edito_idml_file.prefix("edito") as prefixed_edito,\
                 courrier_idml_file.prefix("courrier") as prefixed_courrier,\
                 bloc_notes_idml_file.prefix("blocnotes") as prefixed_bnotes:

                packages_to_add = [
                    (prefixed_edito, 1, "/Root", "/Root/page[1]"),
                    (prefixed_courrier, 1, "/Root", "/Root/page[1]"),
                    (prefixed_bnotes, 1, "/Root", "/Root/page[1]"),
                ]

                with prefixed_mag.add_pages_from_idml(packages_to_add) as f:
                    self.assertEqual(len(f.pages), 4)
                    # FIXME Broken.
                    #self.assertEqual(f.spreads, ['Spreads/Spread_magub6.xml', 'Spreads/Spread_magub7.xml'])


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(IdmlTestCase)
    return suite
