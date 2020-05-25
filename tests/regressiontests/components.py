# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from decimal import Decimal
from lxml import etree
from simple_idml.components import RECTO, VERSO
from simple_idml.components import Spread, Story, Style, StyleMapping, XMLElement
from simple_idml.idml import IDMLPackage
from simple_idml.test import SimpleTestCase
from simple_idml.utils import etree_dom_to_tree

CURRENT_DIR = os.path.dirname(__file__)
IDMLFILES_DIR = os.path.join(CURRENT_DIR, "IDML")


class DesignmapTestCase(unittest.TestCase):
    def test_repr(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(repr(designmap), '<Designmap object designmap.xml at %s>' % hex(id(designmap)))
        idml_file.close()

    def test_layer_nodes(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(len(designmap.layer_nodes), 1)
        self.assertEqual(designmap.layer_nodes[0].get("Name"), 'Layer 1')
        idml_file.close()

    def test_add_layer_nodes(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        designmap = idml_file.designmap

        designmap.add_layer_nodes([
            etree.fromstring(
                """<Layer Self="toto" Name="Layer 2" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true">
                    <Properties>
                        <LayerColor type="enumeration">Red</LayerColor>
                    </Properties>
                </Layer>"""
            ),
            etree.fromstring(
                """<Layer Self="titi" Name="Layer 3" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true">
                    <Properties>
                        <LayerColor type="enumeration">Blue</LayerColor>
                    </Properties>
                </Layer>"""
            ),
        ])
        self.assertEqual(len(designmap.layer_nodes), 3)
        self.assertEqual([n.get("Name") for n in designmap.layer_nodes],
                         ['Layer 1', 'Layer 2', 'Layer 3'])
        idml_file.close()

    def test_suffix_layers(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(designmap.layer_nodes[0].get("Name"), 'Layer 1')
        designmap.suffix_layers(" #66")
        self.assertEqual(designmap.layer_nodes[0].get("Name"), 'Layer 1 #66')
        idml_file.close()

    def test_active_layer(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(designmap.active_layer, "u2db")

        designmap.active_layer = "ua4"
        self.assertEqual(designmap.active_layer, "ua4")

        del designmap.active_layer
        self.assertEqual(designmap.active_layer, None)
        idml_file.close()

    def test_remove_layer(self):
        # Remove active layer.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(designmap.active_layer, "u2db")

        designmap.remove_layer("u2db")
        self.assertEqual(designmap.active_layer, "ua4")
        idml_file.close()

        # Remove inactive layer.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual(designmap.active_layer, "u2db")

        designmap.remove_layer("ua4")
        self.assertEqual(designmap.active_layer, "u2db")
        designmap.remove_layer("u2db")
        self.assertEqual(designmap.active_layer, None)
        idml_file.close()

    def test_spread_nodes(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        designmap = idml_file.designmap
        self.assertEqual([etree_dom_to_tree(n, True) for n in designmap.spread_nodes], [
            {
                'attrs': {'src': 'Spreads/Spread_ud8.xml'},
                'content': [],
                'tag': '{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                'tail': '',
                'text': None
            },
            {
                'attrs': {'src': 'Spreads/Spread_u13b.xml'},
                'content': [],
                'tag': '{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                'tail': '',
                'text': None
            },
            {
                'attrs': {'src': 'Spreads/Spread_u142.xml'},
                'content': [],
                'tag': '{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Spread',
                'tail': '',
                'text': None
            }
        ])
        idml_file.close()


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

    def test_has_any_item_on_layer(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        spreads = idml_file.spreads

        # Spread_ud8.xml
        spread1 = Spread(idml_file, spreads[0])
        self.assertFalse(spread1.has_any_item_on_layer("unknown_layer"))
        self.assertTrue(spread1.has_any_item_on_layer("u2db"))

    def test_has_any_guide_on_layer(self):
        # Package with 2 layers, each one having guides.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        spreads = idml_file.spreads

        # Spread_ud8.xml
        spread1 = Spread(idml_file, spreads[0])
        self.assertFalse(spread1.has_any_guide_on_layer("unknown_layer"))
        self.assertTrue(spread1.has_any_guide_on_layer("u2db"))
        self.assertTrue(spread1.has_any_guide_on_layer("ua4"))

        # Package with one layer and no guides.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        spreads = idml_file.spreads

        # Spread_ub6.xml
        spread1 = Spread(idml_file, spreads[0])
        self.assertFalse(spread1.has_any_guide_on_layer("ub3"))

    def test_remove_guides_on_layer(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages-layers-with-guides.idml"), mode="r")
        spreads = idml_file.spreads

        # Spread_ud8.xml
        spread1 = Spread(idml_file, spreads[0])
        self.assertTrue(spread1.has_any_guide_on_layer("u2db"))
        self.assertTrue(spread1.has_any_item_on_layer("u2db"))
        self.assertTrue(spread1.has_any_guide_on_layer("ua4"))
        self.assertTrue(spread1.has_any_item_on_layer("ua4"))

        spread1.remove_guides_on_layer("u2db")
        self.assertFalse(spread1.has_any_guide_on_layer("u2db"))
        self.assertTrue(spread1.has_any_item_on_layer("u2db"))
        self.assertTrue(spread1.has_any_guide_on_layer("ua4"))
        self.assertTrue(spread1.has_any_item_on_layer("ua4"))

        spread1.remove_guides_on_layer("ua4")
        self.assertFalse(spread1.has_any_guide_on_layer("u2db"))
        self.assertTrue(spread1.has_any_item_on_layer("u2db"))
        self.assertFalse(spread1.has_any_guide_on_layer("ua4"))
        self.assertTrue(spread1.has_any_item_on_layer("ua4"))


class StoryTestCase(SimpleTestCase):
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

    def test_create(self):
        from tempfile import mkdtemp
        idml_working_copy = mkdtemp()
        story = Story.create(None, "my_story_id", "my_xml_element_id", "my_xml_element_tag", idml_working_copy)

        self.assertEqual(story.name, 'Stories/Story_my_story_id.xml')
        self.assertEqual(story.tostring(),
b"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
     <Story Self="my_story_id" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
       <StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
       <InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>
       <XMLElement Self="my_xml_element_id" MarkupTag="XMLTag/my_xml_element_tag" XMLContent="my_story_id"/>
     </Story>
</idPkg:Story>
""")
        shutil.rmtree(idml_working_copy)

    def test_add_note(self):
        import datetime
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        path = "/Root/article/Story/title"
        story = idml_file.get_story_object_by_xpath(path)
        element_id = idml_file.xml_structure.xpath(path)[0].get("Self")
        story.add_note(element_id, "This is a note", "Stanislas Guerra",
                       when=datetime.datetime(2020, 5, 20, 14, 46))
        self.assertXMLEqual(story.tostring().decode("utf8"),
                            """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
        <Story Self="ue4" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
                <StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
                <InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>
                <XMLElement Self="di2i3i1" MarkupTag="XMLTag/Story" XMLContent="ue4">
                        <ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" Justification="CenterJustified">
                                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="Bold">
                                        <Properties>
                                                <AppliedFont type="string">Vollkorn</AppliedFont>
                                        </Properties>
                                        <XMLElement Self="di2i3i1i1" MarkupTag="XMLTag/title">
                                                <Note Collapsed="false" CreationDate="2020-05-20T14:46:00" ModificationDate="2020-05-20T14:46:00" UserName="Stanislas Guerra">
                                            <ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]">
                                                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">
                                                    <Content>This is a note</Content>
                                                </CharacterStyleRange>
                                            </ParagraphStyleRange>
                                        </Note><Content>My Main Article Title</Content>
                                        </XMLElement>
                                        <Br/>
                                </CharacterStyleRange>
                                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="Italic">
                                        <Properties>
                                                <AppliedFont type="string">Vollkorn</AppliedFont>
                                        </Properties>
                                        <XMLElement Self="di2i3i1i2" MarkupTag="XMLTag/subtitle">
                                                <Content>And a subtitle</Content>
                                        </XMLElement>
                                </CharacterStyleRange>
                        </ParagraphStyleRange>
                </XMLElement>
        </Story>
</idPkg:Story>""")


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

    def test_geometric_bounds(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "magazineA-courrier-des-lecteurs-3pages.idml"), mode="r")
        spread = Spread(idml_file, idml_file.spreads[1])

        page3 = spread.pages[1]
        self.assertEqual(page3.geometric_bounds, [
            Decimal('0'),
            Decimal('0'),
            Decimal('759.6850393700788'),
            Decimal('566.9291338582677')
        ])

        page3.geometric_bounds = [
            Decimal('210'),
            Decimal('297'),
            Decimal('10.51'),
            Decimal('7.23')
        ]
        self.assertEqual(page3.geometric_bounds, [
            Decimal('210'),
            Decimal('297'),
            Decimal('10.51'),
            Decimal('7.23')
        ])

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
        self.assertEqual(style_node.nsmap, {'idPkg': 'http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging'})
        self.assertEqual(etree_dom_to_tree(style_node, True), {
            'attrs': {
                'FontStyle': 'Bold',
                'Imported': 'false',
                'KeyboardShortcut': '0 0',
                'Name': 'bold',
                'Self': 'CharacterStyle/bold'
            },
            'content': [
                {
                    'attrs': {},
                    'content': [
                        {
                            'attrs': {'type': 'string'},
                            'content': [],
                            'tag': 'BasedOn',
                            'tail': '',
                            'text': '$ID/[No character style]'
                        },
                        {
                            'attrs': {'type': 'enumeration'},
                            'content': [],
                            'tag': 'PreviewColor',
                            'tail': '',
                            'text': 'Nothing'
                        }
                    ],
                    'tag': 'Properties',
                    'tail': '',
                    'text': ''
                }
            ],
            'tag': 'CharacterStyle',
            'tail': '',
            'text': ''
        })


class StyleMappingTestCase(unittest.TestCase):
    def test_styles(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)
        self.assertEqual([line.strip() for line in style_mapping.tostring().split(b"\n")], [
            b"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>",
            b'<idPkg:Mapping xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="10.0">',
            b'<XMLImportMap Self="did2" MarkupTag="XMLTag/bold" MappedStyle="CharacterStyle/bold"/>',
            b'<XMLImportMap Self="di13f" MarkupTag="XMLTag/italique" MappedStyle="CharacterStyle/italique"/>',
            b'<XMLImportMap Self="di141" MarkupTag="XMLTag/sup" MappedStyle="CharacterStyle/sup"/>',
            b'</idPkg:Mapping>',
            b''
        ])

        # The XML/Mapping.xml may not be present.
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "4-pages.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)

    def test_character_style_mapping(self):
        idml_file = IDMLPackage(os.path.join(IDMLFILES_DIR, "article-1photo_import-xml.idml"), mode="r")
        style_mapping = StyleMapping(idml_file)
        self.assertEqual(style_mapping.character_style_mapping,
                         {'italique': 'CharacterStyle/italique',
                          'bold': 'CharacterStyle/bold',
                          'sup': 'CharacterStyle/sup'})


class XMLElementTestCase(unittest.TestCase):
    def test_repr(self):
        node = etree.fromstring('<XMLElement Self="di3i4i1" MarkupTag="XMLTag/main_picture" XMLContent="u143" />')
        elt = XMLElement(node)
        self.assertEqual(
            repr(elt),
            '<Element XMLElement at %s> {Self: di3i4i1, MarkupTag: XMLTag/main_picture, XMLContent: u143}' % hex(id(elt.element))
        )

    def test_attributes(self):
        dom = etree.fromstring(b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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

    def test_get_character_style_range(self):
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
        self.assertEqual(elt.get_character_style_range().get("AppliedCharacterStyle"), "CharacterStyle/$ID/MyFancyStyle")

        elt = XMLElement(etree.fromstring("""
        <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/MyOtherStyle" FontStyle="Regular" PointSize="9" HorizontalScale="90" Tracking="-30">
          <Properties>
            <Leading type="unit">10</Leading>
            <AppliedFont type="string">Adobe Garamond</AppliedFont>
          </Properties>
          <Content>﻿</Content>
          <XMLElement Self="di3i9i1i2" MarkupTag="XMLTag/texte">
            <Content>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</Content>
          </XMLElement>
          <Br/>
          <Content>Prix : </Content>
        </CharacterStyleRange>
        """).find("XMLElement"))
        self.assertEqual(elt.get_character_style_range().get("AppliedCharacterStyle"), "CharacterStyle/$ID/MyOtherStyle")


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SpreadTestCase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(DesignmapTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StoryTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PageTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StyleTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StyleMappingTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(XMLElementTestCase))
    return suite
