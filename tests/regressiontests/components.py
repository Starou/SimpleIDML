# -*- coding: utf-8 -*-

import os
import sys
import shutil
import unittest
from decimal import Decimal
from lxml import etree

from simple_idml.idml import IDMLPackage
from simple_idml.components import RECTO, VERSO
from simple_idml.components import Spread, Story

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "simpleIDML_files")


class SpreadTestCase(unittest.TestCase):
    def test_pages(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        spreads = idml_file.spreads

        spread1 = Spread(idml_file, spreads[0])
        spread1_pages = spread1.pages
        self.assertEqual(len(spread1_pages), 1)
        self.assertEqual(spread1_pages[0].node.tag, "Page")

        spread2 = Spread(idml_file, spreads[1])
        spread2_pages = spread2.pages
        self.assertEqual(len(spread2_pages), 2)
        self.assertEqual(spread2_pages[0].node.tag, "Page")
        self.assertEqual(spread2_pages[1].node.tag, "Page")


class StoryTestCase(unittest.TestCase):
    def test_pages(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        stories = idml_file.stories

        story = Story(idml_file, stories[0])
        self.assertEqual(story.node.tag, "Story")

    def test_get_element_by_id(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        story = idml_file.get_story_object_by_id("u11b")
        elem = story.get_element_by_id("di2i3i2")
        self.assertEqual(elem.get("MarkupTag"), "XMLTag/content")

    def test_get_element_content_by_id(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        story = idml_file.get_story_object_by_id("u11b")
        content = story.get_element_content_by_id("di2i3i2")
        self.assertEqual(content, u'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\u2029Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?')

        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"))
        # The <Story> node that contains <article> and <informations>.
        story = idml_file.get_story_object_by_id("uf7")
        content = story.get_element_content_by_id("di3i4i3")
        self.assertEqual(content, "")

    def test_get_story_id_for_xml_structure_node(self):
        from simple_idml.idml import get_story_id_for_xml_structure_node
        dom = etree.fromstring(
"""<Root Self="editodi2">
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
        self.assertEqual(get_story_id_for_xml_structure_node(dom.find(".//page/article/Story")), "editoue4")
        self.assertEqual(get_story_id_for_xml_structure_node(dom.find(".//page/article/Story/title")), "editoue4")


class PageTestCase(unittest.TestCase):
    def test_page_items(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs-3pages.idml"), mode="r")
        spread = Spread(idml_file, idml_file.spreads[1])

        page1 = spread.pages[0]
        self.assertEqual([i.tag for i in page1.page_items], ["Rectangle"])

        page2 = spread.pages[1]
        self.assertEqual([i.tag for i in page2.page_items], [
            'Rectangle',
            'TextFrame',
            'Polygon',
            'Polygon',
            'Polygon',
            'GraphicLine',
            'Polygon',
            'Polygon',
            'Oval',
            'Rectangle',
        ])

        # test the setter
        page2.page_items = ["foo", "bar"]
        self.assertEqual(page2.page_items, ["foo", "bar"])

    def test_coordinates(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs-3pages.idml"), mode="r")
        spread = Spread(idml_file, idml_file.spreads[1])

        page2 = spread.pages[0]
        self.assertEqual(page2.coordinates, {
            'x1': Decimal('-566.9291338582677'),
            'y1': Decimal('-379.8425196850394'),
            'x2': Decimal('0E-13'),
            'y2': Decimal('379.8425196850394')
        })

        page3 = spread.pages[1]
        self.assertEqual(page3.coordinates, {
            'x1': Decimal('0'),
            'y1': Decimal('-379.8425196850394'),
            'x2': Decimal('566.9291338582677'),
            'y2': Decimal('379.8425196850394'),
        })

    def test_is_recto(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs-3pages.idml"), mode="r")
        spread1 = Spread(idml_file, idml_file.spreads[0])
        page1 = spread1.pages[0]
        self.assertTrue(page1.is_recto)

        spread2 = Spread(idml_file, idml_file.spreads[1])
        page2 = spread2.pages[0]
        page3 = spread2.pages[1]
        self.assertFalse(page2.is_recto)
        self.assertTrue(page3.is_recto)

    def test_set_face(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs.idml"), mode="r")
        spread2 = Spread(idml_file, idml_file.spreads[1])
        page2 = spread2.pages[0]
        self.assertEqual(page2.face, VERSO)

        page2.set_face(RECTO)
        self.assertEqual(page2.face, RECTO)


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SpreadTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StoryTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PageTestCase))
    return suite
