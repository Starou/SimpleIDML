# -*- coding: utf-8 -*-

import unittest
from lxml import etree


class UtilsTestCase(unittest.TestCase):
    def test_increment_filename(self):
        from simple_idml.utils import increment_filename
        filename = "/path/to/myfile.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfilf.txt")

        filename = "/path/to/myfilez.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfileza.txt")

        filename = "/path/to/myfileZ.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfileZa.txt")

        filename = "/path/to/myfile-200.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfile-201.txt")

        filename = "/path/to/myfile-299.txt"
        self.assertEqual(increment_filename(filename), "/path/to/myfile-300.txt")

    def test_increment_xmltag_id(self):
        from simple_idml.utils import increment_xmltag_id
        self.assertEqual(increment_xmltag_id("di3i4", "sibling"), "di3i5")
        self.assertEqual(increment_xmltag_id("di3i4i10", "sibling"), "di3i4i11")

        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4", "sibling"), "MyL33tPrefixdi3i5")
        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4i10", "sibling"), "MyL33tPrefixdi3i4i11")

        self.assertEqual(increment_xmltag_id("di3i4", "child"), "di3i4i1")
        self.assertEqual(increment_xmltag_id("di3i4i10", "child"), "di3i4i10i1")

        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4", "child"), "MyL33tPrefixdi3i4i1")
        self.assertEqual(increment_xmltag_id("MyL33tPrefixdi3i4i10", "child"), "MyL33tPrefixdi3i4i10i1")

    def test_prefix_content_filename(self):
        from simple_idml.utils import prefix_content_filename

        # Prefix stories and spread filename references.
        src = "Stories/Story_u139.xml"
        result = prefix_content_filename(src, "MyPrefix", "ref")
        self.assertEqual(result, "Stories/Story_MyPrefixu139.xml")

        src = "Spreads/Spread_ub6.xml"
        result = prefix_content_filename(src, "MyPrefix", "ref")
        self.assertEqual(result, "Spreads/Spread_MyPrefixub6.xml")

        # Prefix filenames.
        src = "Story_u139.xml"
        result = prefix_content_filename(src, "MyPrefix", "filename")
        self.assertEqual(result, "Story_MyPrefixu139.xml")

        src = "Spread_ub6.xml"
        result = prefix_content_filename(src, "MyPrefix", "filename")
        self.assertEqual(result, "Spread_MyPrefixub6.xml")

    def test_str_is_prefixed(self):
        from simple_idml.utils import str_is_prefixed
        self.assertFalse(str_is_prefixed("foo", "bar"))
        self.assertTrue(str_is_prefixed("foo", "foobar"))

    def test_tree_to_etree_dom(self):
        from simple_idml.utils import tree_to_etree_dom
        tree = {
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
                                        u' is eaten by a creature Zissou describes as a "Jaguar shark."',
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
                                        ', a safety expert and Brazilian musician who sings David Bowie songs in Portuguese.'
                                    ],
                                },
                                {
                                    'tag': 'informations',
                                    'attrs': {},
                                    'content': [
                                        'The Life Aquatic with Steve Zissou is an American comedy-drama film.'
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        dom = tree_to_etree_dom(tree)
        self.assertMultiLineEqual(etree.tostring(dom, pretty_print=True),
"""<Root>
  <module>
    <main_picture href="file:///steve.jpg"/>
    <headline>The Life Aquatic with Steve Zissou</headline>
    <Story>
      <article>While oceanographer and documentarian <bold>Steve Zissou (Bill Murray) is <sup>working</sup> on his latest documentary at sea, his best friend <italique>Esteban du Plantier</italique> (Seymour Cassel)</bold> is eaten by a creature Zissou describes as a "Jaguar shark."<italique>Belafonte</italique> includes <italique>Pel&#233; dos Santos (Seu Jorge)</italique>, a safety expert and Brazilian musician who sings David Bowie songs in Portuguese.</article>
      <informations>The Life Aquatic with Steve Zissou is an American comedy-drama film.</informations>
    </Story>
  </module>
</Root>
""")

    def test_etree_dom_to_tree(self):
        from simple_idml.utils import etree_dom_to_tree
        dom = etree.fromstring("""<XMLTag Self="XMLTag/advertise" Name="advertise">
                               <Properties>
                               <TagColor type="enumeration">Green</TagColor>
                               </Properties>
                               </XMLTag>
                               """)
        self.assertEqual(etree_dom_to_tree(dom, True), {
            'attrs': {'Name': 'advertise', 'Self': 'XMLTag/advertise'},
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
            'tail': None,
            'text': ''
        })


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(UtilsTestCase)
    return suite
