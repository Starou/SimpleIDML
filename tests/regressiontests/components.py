# -*- coding: utf-8 -*-

import os
import sys
import shutil
import unittest
from decimal import Decimal
from lxml import etree

from simple_idml.idml import IDMLPackage
from simple_idml.components import RECTO, VERSO
from simple_idml.components import Spread, Story, Style, StyleMapping, XMLElement

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")


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

    def test_set_element_resource_path(self):
        pass


class StoryTestCase(unittest.TestCase):
    def test_pages(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        stories = idml_file.stories
        story = Story(idml_file, stories[0])
        self.assertEqual(story.node.tag, "Story")

    def test_get_element_by_id(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        stories = idml_file.stories
        story = Story(idml_file, stories[1])  # u11b
        elem = story.get_element_by_id("di2i3i2")
        self.assertEqual(elem.get("MarkupTag"), "XMLTag/content")

        elem = story.get_element_by_id("di2i3i2", tag="*")
        self.assertEqual(elem.get("MarkupTag"), "XMLTag/content")


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


class StyleTestCase(unittest.TestCase):
    def test_get_style_node_by_name(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"), mode="r")
        style = Style(idml_file)
        style_node = style.get_style_node_by_name("CharacterStyle/bold")
        #print(etree.tostring(style_node, pretty_print=True)).replace("\t"," ")
        self.assertEqual(etree.tostring(style_node, pretty_print=True).replace("\t", " "),
# Don't remove trailing space !
"""<CharacterStyle xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" Self="CharacterStyle/bold" Imported="false" KeyboardShortcut="0 0" Name="bold" FontStyle="Bold">
   <Properties>
    <BasedOn type="string">$ID/[No character style]</BasedOn>
    <PreviewColor type="enumeration">Nothing</PreviewColor>
   </Properties>
  </CharacterStyle>
  
""")


class StyleMappingTestCase(unittest.TestCase):
    def test_styles(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)
        self.assertEqual(style_mapping.tostring(), '<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n<idPkg:Mapping xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n\t<XMLImportMap Self="did2" MarkupTag="XMLTag/bold" MappedStyle="CharacterStyle/bold"/>\n\t<XMLImportMap Self="di13f" MarkupTag="XMLTag/italique" MappedStyle="CharacterStyle/italique"/>\n</idPkg:Mapping>\n')

        # The XML/Mapping.xml may not be present.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)

    def test_character_style_mapping(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)
        self.assertEqual(style_mapping.character_style_mapping,
                         {'italique': 'CharacterStyle/italique', 'bold': 'CharacterStyle/bold'})


class XMLElementTestCase(unittest.TestCase):
    def test_attributes(self):
        dom = etree.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
                <Story Self="u10d">
                    <XMLElement Self="di3i4" MarkupTag="XMLTag/module" XMLContent="u10d">
                        <ParagraphStyleRange>
                            <CharacterStyleRange>
                                <XMLElement Self="di3i4i1" MarkupTag="XMLTag/main_picture" XMLContent="u143">
                                    <XMLAttribute Self="di3i4i1XMLAttributenhref" Name="href" Value="file:///piscine.jpg"/>
                                    <XMLAttribute Self="di3i4i1XMLAttributenbar" Name="bar" Value="baz"/>
                                </XMLElement>
                                <XMLElement Self="di3i4i2" MarkupTag="XMLTag/headline" XMLContent="ue1"/>
                                <XMLElement Self="di3i4i3" MarkupTag="XMLTag/Story" XMLContent="uf7"/>
                            </CharacterStyleRange>
                        </ParagraphStyleRange>
                    </XMLElement>
                </Story>
            </idPkg:Story>""")

        # Getter.
        module_node = dom.xpath(".//XMLElement[@Self='di3i4']")[0]
        module_elt = XMLElement(module_node)
        self.assertEqual(module_elt.get_attribute("foo"), None)
        self.assertEqual(module_elt.get_attribute("href"), None)
        self.assertEqual(module_elt.get_attribute("bar"), None)

        picture_node = dom.xpath(".//XMLElement[@Self='di3i4i1']")[0]
        picture_elt = XMLElement(picture_node)
        self.assertEqual(picture_elt.get_attribute("foo"), None)
        self.assertEqual(picture_elt.get_attribute("href"), "file:///piscine.jpg")
        self.assertEqual(picture_elt.get_attribute("bar"), "baz")

        # Get all attributes (similar to Element.items()).
        self.assertEqual(picture_elt.get_attributes(),
                         {'href': 'file:///piscine.jpg', 'bar': 'baz'})

        # Setter.
        module_elt.set_attribute("foo", "bar")
        self.assertEqual(module_elt.get_attribute("foo"), "bar")

        picture_elt.set_attribute("href", "file:///jardin.jpg")
        self.assertEqual(picture_elt.get_attribute("href"), "file:///jardin.jpg")
        picture_elt.set_attribute("bar", "hello")
        self.assertEqual(picture_elt.get_attribute("bar"), "hello")

        # Set multiples attributes at once.
        picture_elt.set_attributes({"href": "file:///maison.jpg", 
                                    "style": "fancy"})
        self.assertEqual(picture_elt.get_attribute("href"), "file:///maison.jpg")
        self.assertEqual(picture_elt.get_attribute("style"), "fancy")

    def test_create_style_element(self):
        parent = XMLElement(etree.fromstring("""
            <XMLElement Self="di3i4i1i2i2i2" MarkupTag="XMLTag/texte">
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Semibold" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content>Lorem ipsum dolor sit amet, consectetur adipisicing elit,
                                  sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. </Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum d</Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content> nulla pariatur. Excepteur </Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content> cupidatat </Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content>, sunt in culpa qui officia dese</Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
                                  FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-10">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Br/>
                </CharacterStyleRange>
            </XMLElement>"""))

        # No style provided > parent style used.
        xml_element = XMLElement(tag="bold")
        style_element = xml_element._create_style_element(parent, style_node=None)
        self.assertEqual(etree.tostring(style_element, pretty_print=True),
"""<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" PointSize="9" FontStyle="Semibold" HorizontalScale="90" Tracking="-30">
  <Properties><Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
</CharacterStyleRange>
""")

        # Style specify the font style only : parent font-face and size are added.
        style_node = etree.fromstring("""
            <CharacterStyle Self="CharacterStyle/bold" Imported="false" KeyboardShortcut="0 0" Name="bold" FontStyle="Bold">
                <Properties>
                    <BasedOn type="string">$ID/[No character style]</BasedOn>
                    <PreviewColor type="enumeration">Nothing</PreviewColor>
                </Properties>
            </CharacterStyle>""")
        xml_element = XMLElement(tag="bold")
        style_element = xml_element._create_style_element(parent, style_node)
        self.assertEqual(etree.tostring(style_element, pretty_print=True),
"""<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/bold" PointSize="9" HorizontalScale="90" Tracking="-30">
  <Properties><Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
</CharacterStyleRange>
""")                         

        # Style specify the font style and size : parent font-face is added.
        style_node = etree.fromstring("""
            <CharacterStyle Self="CharacterStyle/bold12" Imported="false" KeyboardShortcut="0 0" Name="bold12" FontStyle="Bold" PointSize="12">
                <Properties>
                    <BasedOn type="string">$ID/[No character style]</BasedOn>
                    <PreviewColor type="enumeration">Nothing</PreviewColor>
                </Properties>
            </CharacterStyle>""")
        xml_element = XMLElement(tag="bold12")
        style_element = xml_element._create_style_element(parent, style_node)
        self.assertEqual(etree.tostring(style_element, pretty_print=True),
"""<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/bold12" HorizontalScale="90" Tracking="-30">
  <Properties><Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
</CharacterStyleRange>
""")                         

        # Style specify the font style, font-face and size.
        style_node = etree.fromstring("""
            <CharacterStyle Self="CharacterStyle/CSBold11" Imported="false" KeyboardShortcut="0 0" Name="CSBold11" FontStyle="Bold" PointSize="11">
                <Properties>
                    <BasedOn type="string">$ID/[No character style]</BasedOn>
                    <PreviewColor type="enumeration">Nothing</PreviewColor>
                    <AppliedFont type="string">Comic Sans MS</AppliedFont>
                </Properties>
            </CharacterStyle>""")
        xml_element = XMLElement(tag="CSBold11")
        style_element = xml_element._create_style_element(parent, style_node)
        self.assertEqual(etree.tostring(style_element, pretty_print=True),
"""<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/CSBold11" HorizontalScale="90" Tracking="-30">
  <Properties><Leading type="unit">10</Leading>
                        </Properties>
</CharacterStyleRange>
""")                         

    def test_get_applied_character_style(self):
        elt = XMLElement(etree.fromstring("""
            <XMLElement Self="di3i4i1i2i2i2" MarkupTag="XMLTag/texte">
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/MyFancyStyle" 
                                          FontStyle="Semibold" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. </Content>
                </CharacterStyleRange>
                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" 
                                          FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
                    <Properties>
                        <Leading type="unit">10</Leading>
                        <AppliedFont type="string">Adobe Garamond</AppliedFont>
                    </Properties>
                    <Content>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum d</Content>
                </CharacterStyleRange>
            </XMLElement>"""))
        self.assertEqual(elt.get_applied_character_style(), "CharacterStyle/$ID/MyFancyStyle")


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SpreadTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StoryTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PageTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StyleTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StyleMappingTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(XMLElementTestCase))
    return suite
