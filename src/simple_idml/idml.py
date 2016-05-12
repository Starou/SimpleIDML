# -*- coding: utf-8 -*-

import copy
import os
import re
import shutil
import zipfile
from decimal import Decimal
from lxml import etree
from simple_idml import BACKINGSTORY, SETCONTENT_TAG, IGNORECONTENT_TAG, FORCECONTENT_TAG
from simple_idml.components import get_idml_xml_file_by_name
from simple_idml.components import (Designmap, Spread, Story, BackingStory,
                                    Style, StyleMapping, Graphic, Tags, Fonts, XMLElement)
from simple_idml.decorators import use_working_copy
from simple_idml.utils import increment_filename, prefix_content_filename, tree_to_etree_dom

STORIES_DIRNAME = "Stories"


class IDMLPackage(zipfile.ZipFile):
    """An IDML file (a package) is a Zip-stored archive/UCF container. """
    debug = False

    def __init__(self, *args, **kwargs):
        kwargs["compression"] = zipfile.ZIP_STORED
        zipfile.ZipFile.__init__(self, *args, **kwargs)
        self.working_copy_path = None
        self.init_lazy_references()

    def __repr__(self):
        return "<idml.IDMLPackage instance of '%s' at %s>" % (
            os.path.basename(self.filename),
            hex(id(self))
        )

    def init_lazy_references(self):
        self._xml_structure = None
        self._xml_structure_tree = None
        self._designmap = None
        self._tags = None
        self._font_families = None
        self._style_groups = None
        self._style = None
        self._style_mapping = None
        self._graphic = None
        self._spreads = None
        self._spreads_objects = None
        self._pages = None
        self._backing_story = None
        self._stories = None
        self._story_ids = None
        self._referenced_layers = None

    def namelist(self):
        if not self.working_copy_path:
            return zipfile.ZipFile.namelist(self)
        else:
            namelist = []
            for root, dirs, filenames in os.walk(self.working_copy_path):
                rel_root = root.replace(self.working_copy_path, "")[1:]
                for filename in filenames:
                    namelist.append("%(rel_root)s%(sep)s%(filename)s" % {
                        'rel_root': rel_root,
                        'sep': rel_root and "/" or "",
                        'filename': filename
                    })
            return namelist

    def contentfile_namelist(self):
        """Namelist filtered on Spreads and Stories. """
        return [f for f in self.namelist() if os.path.dirname(f) in ("Spreads", "Stories")]

    @property
    def xml_structure(self):
        """ Discover the XML structure from the story files.

        Starting at BackingStory.xml where the root-element is expected (because unused). """

        if self._xml_structure is None:
            source_node = self.backing_story.get_root()
            structure = source_node.to_xml_structure_element()

            def append_childs(source_node, destination_node):
                """Recursive function to discover node structure from a story to another. """
                for elt in source_node.iterchildren():
                    if not elt.tag == "XMLElement":
                        append_childs(elt, destination_node)
                    if elt.get("Self") == source_node.get("Self"):
                        continue
                    if not elt.get("MarkupTag"):
                        continue
                    elt = XMLElement(elt)
                    new_destination_node = elt.to_xml_structure_element()
                    destination_node.append(new_destination_node)
                    if elt.get("XMLContent"):
                        xml_content_value = elt.get("XMLContent")
                        story_name = "Stories/Story_%s.xml" % xml_content_value
                        story = Story(self, name=story_name)
                        try:
                            new_source_node = story.get_element_by_id(elt.get("Self"))
                        # The story does not exists.
                        except KeyError:
                            continue
                        else:
                            append_childs(new_source_node, new_destination_node)
                    else:
                        append_childs(elt, new_destination_node)

            append_childs(source_node, structure)
            self._xml_structure = structure
        return self._xml_structure

    def xml_structure_pretty(self):
        return etree.tostring(self.xml_structure, pretty_print=True)

    @property
    def xml_structure_tree(self):
        if self._xml_structure_tree is None:
            xml_structure_tree = etree.ElementTree(self.xml_structure)
            self._xml_structure_tree = xml_structure_tree
        return self._xml_structure_tree

    @property
    def designmap(self):
        if self._designmap is None:
            designmap = Designmap(self, working_copy_path=self.working_copy_path)
            self._designmap = designmap
        return self._designmap

    @property
    def tags(self):
        if self._tags is None:
            tags = [copy.deepcopy(elt) for elt in Tags(self).tags()]
            self._tags = tags
        return self._tags

    @property
    def font_families(self):
        if self._font_families is None:
            font_families = [copy.deepcopy(elt) for elt in Fonts(self).fonts()]
            self._font_families = font_families
        return self._font_families

    @property
    def style_groups(self):
        if self._style_groups is None:
            style_groups = [copy.deepcopy(elt) for elt in Style(self).style_groups()]
            self._style_groups = style_groups
        return self._style_groups

    @property
    def style(self):
        if self._style is None:
            style = Style(self, self.working_copy_path)
            self._style = style
        return self._style

    @property
    def style_mapping(self):
        """The style mapping file may not be present in the archive and is created in that case. """
        if self._style_mapping is None:
            style_mapping = StyleMapping(self, self.working_copy_path)
            self._style_mapping = style_mapping
        return self._style_mapping

    @property
    def graphic(self):
        if self._graphic is None:
            graphic = Graphic(self, self.working_copy_path)
            self._graphic = graphic
        return self._graphic

    @property
    def spreads(self):
        if self._spreads is None:
            spreads = [elt for elt in self.namelist() if re.match(ur"^Spreads/*", elt)]
            self._spreads = spreads
        return self._spreads

    @property
    def spreads_objects(self):
        if self._spreads_objects is None:
            spreads_objects = [Spread(self, s, self.working_copy_path) for s in self.spreads]
            self._spreads_objects = spreads_objects
        return self._spreads_objects

    @property
    def pages(self):
        if self._pages is None:
            pages = []
            for spread in self.spreads_objects:
                pages += spread.pages
            self._pages = pages
        return self._pages

    @property
    def backing_story(self):
        """The style mapping file may not be present in the archive and is created in that case. """
        if self._backing_story is None:
            backing_story = BackingStory(self, working_copy_path=self.working_copy_path)
            self._backing_story = backing_story
        return self._backing_story

    @property
    def stories(self):
        if self._stories is None:
            stories = [elt for elt in self.namelist()
                       if re.match(ur"^%s/*" % STORIES_DIRNAME, elt)]
            self._stories = stories
        return self._stories

    def stories_for_node(self, node_path):
        return ["%s/Story_%s.xml" % (STORIES_DIRNAME, child.get("XMLContent"))
                for child in self.xml_structure.xpath(node_path)[0].iter()
                if child.get("XMLContent") in self.story_ids]

    @property
    def story_ids(self):
        """ extract  `ID' from `Stories/Story_ID.xml'. """
        if self._story_ids is None:
            self._story_ids = self._get_story_ids_for_stories(self.stories)
        return self._story_ids

    def story_ids_for_node(self, node_path):
        return self._get_story_ids_for_stories(self.stories_for_node(node_path))

    def _get_story_ids_for_stories(self, stories):
        rx_story_id = re.compile(r"%s/Story_([\w]+)\.xml" % STORIES_DIRNAME)
        return [rx_story_id.match(elt).group(1) for elt in stories]

    @property
    def referenced_layers(self):
        if self._referenced_layers is None:
            referenced_layers = []
            for layer in self.designmap.layer_nodes:
                layer_id = layer.get("Self")
                for spread in self.spreads_objects:
                    if spread.has_any_item_on_layer(layer_id):
                        referenced_layers.append(layer_id)
            self._referenced_layers = referenced_layers
        return self._referenced_layers

    @use_working_copy
    def import_xml(self, xml, at):
        """ Reproduce the action «Import XML» on a XML Element in InDesign® Structure. """

        source_node = etree.fromstring(xml)

        def _set_content(xpath, element_id, content, story=None):
            story = story or self.get_story_object_by_xpath(xpath)
            story.set_element_content(element_id, content)
            story.synchronize()

        def _set_attributes(xpath, element_id, items):
            story = self.get_story_object_by_xpath(xpath)
            story.set_element_attributes(element_id, items)
            # Image references must be updated in the page item in Spread or Story.
            if "href" in items:
                resource_path = items.get("href")
                element_content_id = self.get_element_content_id_by_xpath(xpath)
                spread = self.get_spread_object_by_xpath(xpath)
                if resource_path == "":
                    story.remove_xml_element_page_items(element_id)
                    if spread:
                        spread.remove_page_item(element_content_id, synchronize=True)
                else:
                    story.set_element_resource_path(element_content_id, resource_path)
                    if spread:
                        spread.set_element_resource_path(element_content_id,
                                                         resource_path,
                                                         synchronize=True)
            story.synchronize()

        def _apply_style(style_range_node, style_to_apply_node, applied_style_node):
            """ A style_range_node as an applied_style_node overriden with style_to_apply_node. """
            for attr in ("PointSize", "FontStyle", "HorizontalScale", "Tracking", "FillColor", "Capitalization", "Position"):
                if style_to_apply_node.get(attr) is not None:
                    value_to_apply = style_to_apply_node.get(attr)
                    applied_value = style_range_node.get(attr) or applied_style_node.get(attr)
                    if attr == "FontStyle":
                        style_range_node.set(attr, _merge_font_style(applied_value, value_to_apply))
                    else:
                        style_range_node.set(attr, style_to_apply_node.get(attr))
            # TODO
            #for attr in ("Leading", "AppliedFont"):
            #    path = "Properties/%s" % attr
            #    source_attr_node = source_style_node.find(path)
            #    attr_node = (style_node is not None and style_node.find(path) is not None)
            #    if attr_node is None and source_attr_node is not None:
            #        properties_element.append(copy.deepcopy(source_attr_node))

        mergeable_font_styles = {
            "Condensed": {
                "Light": "Condensed Light",
            },
            "Bold": {
                "Italic": "Bold Italic",
            },
            "SemiBold": {
                "Italic": "SemiBold Italic",
            },
            "Semibold": {
                "Italic": "Semibold Italic",
            },
        }

        def _merge_font_style(applied_font_style, font_style_to_apply):
            """ If not mergeable, return the child."""
            parent = mergeable_font_styles.get(applied_font_style, {})
            return parent.get(font_style_to_apply, font_style_to_apply)

        def _get_nested_style_range_node(xml_structure_node):
            """Use the more distant parent as base style and then apply its children styles until the new tag itself.

            Returns:
             o new_style_range_node: unbound element.
             o root_style_node
            """
            nested_styles = []
            while(xml_structure_node is not None):
                style_name = self.style_mapping.character_style_mapping.get(xml_structure_node.tag)
                if style_name:
                    style_node = self.style.get_style_node_by_name(style_name)
                    nested_styles.insert(0, style_node)
                xml_structure_node = xml_structure_node.getparent()

            # Merge the styles starting from the top parent like in a HTML document.
            root_style_node = nested_styles.pop(0)
            new_style_range_node = etree.Element("CharacterStyleRange", AppliedCharacterStyle=root_style_node.get("Self"))
            etree.SubElement(new_style_range_node, "Properties")
            for style_to_apply_node in nested_styles:
                _apply_style(new_style_range_node, style_to_apply_node, root_style_node)

            return new_style_range_node, root_style_node

        def _apply_parent_style_range(style_range_node, applied_style_node, parent):
            """Parent CharacterStyleRange must be set locally. """
            properties_element = style_range_node.find("Properties")

            parent_style_node = parent.get_character_style_range()
            if parent_style_node is None:
                return
            # If the parent specify a font face, a font style or a font size and the style_node don't, it is added.
            for attr in ("PointSize", "FontStyle", "HorizontalScale", "Tracking", "FillColor", "Capitalization", "Position"):
                if parent_style_node.get(attr) is not None and (applied_style_node is None or not applied_style_node.get(attr)):
                    style_range_node.set(attr, parent_style_node.get(attr))

            for attr in ("Leading", "AppliedFont"):
                path = "Properties/%s" % attr
                parent_attr_node = parent_style_node.find(path)
                attr_node = (applied_style_node is not None and applied_style_node.find(path) is not None) or None
                if attr_node is None and parent_attr_node is not None:
                    properties_element.append(copy.deepcopy(parent_attr_node))

        def _move_siblings_content(at, element_id):
            """ When new XML elements are inserted, the siblings of the initial <content> (<BR> etc) are
                repositionned after the last <content> created.
            """
            story = self.get_story_object_by_xpath(at)
            element = story.get_element_by_id(element_id)
            content_nodes = element.get_element_content_nodes()
            if len(content_nodes) < 2:
                return

            first_content_node = content_nodes[0]
            last_content_node = content_nodes[-1]
            siblings = [s for s in first_content_node.itersiblings()]
            if not len(siblings):
                return

            for sibling in siblings:
                last_content_node.addnext(sibling)
            story.synchronize()

        def _import_new_node(source_node, at=None, element_id=None, story=None):
            xml_structure_parent_node = self.xml_structure.find("*//*[@Self='%s']" % element_id)
            xml_structure_new_node = etree.Element(source_node.tag)
            # We cannot force the self._xml_structure reset by setting it at None.
            xml_structure_parent_node.append(xml_structure_new_node)

            style_range_node, applied_style_node = _get_nested_style_range_node(xml_structure_new_node)
            story = story or self.get_story_object_by_xpath(at)
            parent = story.get_element_by_id(element_id)
            _apply_parent_style_range(style_range_node, applied_style_node, parent)

            new_xml_element = XMLElement(tag=source_node.tag)
            new_xml_element.add_content(source_node.text, parent, style_range_node)
            story.add_element(element_id, new_xml_element.element)

            xml_structure_new_node.set("Self", new_xml_element.get("Self"))

            # Source may also contains some children.
            source_node_children = source_node.getchildren()
            if len(source_node_children):
                story.synchronize()
                for j, source_node_child in enumerate(source_node_children):
                    _import_new_node(source_node_child,
                                     element_id=new_xml_element.get("Self"),
                                     story=story)

            if source_node.tail:
                story.add_content_to_element(element_id, source_node.tail, parent)
            story.synchronize()

        def _import_node(source_node, at=None, element_id=None, story=None, ignorecontent_parent_flag=False):
            element_id = element_id or self.xml_structure.xpath(at)[0].get("Self")
            items = dict(source_node.items())

            forcecontent = (items.get(FORCECONTENT_TAG) == "true")
            if not ignorecontent_parent_flag or forcecontent:
                if items:
                    _set_attributes(at, element_id, items)
                if not (items.get(SETCONTENT_TAG) == "false"):
                    _set_content(at, element_id, source_node.text or "", story)

            ignorecontent = (items.get(IGNORECONTENT_TAG) == "true") or (ignorecontent_parent_flag and not forcecontent)
            source_node_children = source_node.getchildren()
            if len(source_node_children):
                source_node_children_tags = [n.tag for n in source_node_children]
                destination_node = self.xml_structure.xpath(at)[0]
                destination_node_children = destination_node.iterchildren()
                destination_node_children_tags = [n.tag for n in destination_node.iterchildren()]
                # Childrens in source node (xml file) and destination node are an exact match,
                # we can call a map() on _import_node().
                # FIXME: what if source_node.text exists ?
                if destination_node_children_tags == source_node_children_tags:
                    map(lambda s, d: _import_node(s, at=d, ignorecontent_parent_flag=ignorecontent),
                        source_node_children, [self.xml_structure_tree.getpath(c) for c in destination_node.iterchildren()])
                # Step-by-step iteration.
                else:
                    destination_node_child = next(destination_node_children, None)
                    for i, source_child in enumerate(source_node_children):
                        # Source and destination match.
                        if destination_node_child is not None and source_child.tag == destination_node_child.tag:
                            _import_node(source_child, at=self.xml_structure_tree.getpath(destination_node_child),
                                         ignorecontent_parent_flag=ignorecontent)
                            destination_node_child = next(destination_node_children, None)
                        # Source does not match destination. It is added, but only if the tag is mapped to a style.
                        elif not ignorecontent and source_child.tag in self.style_mapping.character_style_mapping.keys():
                            _import_new_node(source_child, at, element_id)

                    _move_siblings_content(at, element_id)

        _import_node(source_node, at)
        return self

    def export_as_tree(self):
        """
        tree = {
            "tag": "Root",
            "attrs": {...},
            "content": ["foo", {subtree}, "bar", ...]
        }
        """

        def _export_content_as_tree(xml_structure_node):
            content = []
            tree = {"tag": xml_structure_node.tag,
                    "attrs": {},
                    "content": content}
            # Explore the story to discover the content and the attributes.
            xpath = self.xml_structure_tree.getpath(xml_structure_node)
            story = self.get_story_object_by_xpath(xpath)

            try:
                story.fobj
            except KeyError:
                story_content_and_xmlelement_nodes = []
            else:
                story_node = story.get_element_by_id(xml_structure_node.get("Self"))
                story_content_and_xmlelement_nodes = story.get_element_content_and_xmlelement_nodes(story_node)
                # Attributes. TODO: Attributes are already known in xml_structure.
                tree["attrs"] = copy.deepcopy(story_node.get_attributes())

            xml_structure_node_children = xml_structure_node.getchildren()

            if len(story_content_and_xmlelement_nodes):
                # Leaf with content.
                if len(xml_structure_node_children) == 0:
                    content.append("".join([c.text or "" for c in story_content_and_xmlelement_nodes]))  # if not XMLElement
                # Node with content.
                else:
                    xml_structure_child_node = xml_structure_node_children.pop(0)
                    for story_content_node in story_content_and_xmlelement_nodes:
                        if story_content_node.tag == "XMLElement":
                            content.append(_export_content_as_tree(xml_structure_child_node))
                            try:
                                xml_structure_child_node = xml_structure_node_children.pop(0)
                            except IndexError:
                                xml_structure_child_node = None
                        else:
                            content.append(story_content_node.text)
            else:
                # Node without content > `content' is fed with recursive call on childrens.
                if len(xml_structure_node_children):
                    content.extend(map(_export_content_as_tree, xml_structure_node_children))

            return tree

        xml_structure_root_node = self.xml_structure
        return _export_content_as_tree(xml_structure_root_node)

    def export_xml(self, from_tag=None, encoding=None):
        """ Reproduce the action «Export XML» on a XML Element in InDesign® Structure. """
        tree = self.export_as_tree()
        dom = tree_to_etree_dom(tree)
        return etree.tostring(dom, encoding=encoding, pretty_print=True)

    @use_working_copy
    def prefix(self, prefix):
        """Change references and filename by inserting `prefix' everywhere.

        files in ZipFile cannot be renamed or moved so we make a copies of them.
        """
        if not re.match("^\w+$", prefix):
            raise BaseException("Prefix must be alphanumeric.")

        # Change the references inside the file.
        for filename in self.namelist():
            if (
                os.path.basename(filename) in ["container.xml", "metadata.xml"] or
                os.path.splitext(filename)[1] != ".xml"
            ):
                continue
            idml_xml_file = get_idml_xml_file_by_name(self, filename, self.working_copy_path)
            idml_xml_file.prefix_references(prefix)
            idml_xml_file.synchronize()

        # Story and Spread XML files are "prefixed".
        for filename in self.contentfile_namelist():
            new_basename = prefix_content_filename(os.path.basename(filename),
                                                   prefix, "filename")
            # mv file in the new archive with the prefix.
            old_name = os.path.join(self.working_copy_path, filename)
            new_name = os.path.join(os.path.dirname(old_name), new_basename)
            os.rename(old_name, new_name)

        # Update designmap.xml.
        self.designmap.prefix(prefix)
        self.designmap.synchronize()

        return self

    def is_prefixed(self, prefix):
        # check the <XmlStory> root tag in BackingStory.xml.
        from simple_idml.utils import str_is_prefixed
        return str_is_prefixed(prefix, self.backing_story.node.get("Self"))

    @use_working_copy
    def suffix_layers(self, suffix):
        self.designmap.suffix_layers(suffix)
        self.designmap.synchronize()
        return self

    @use_working_copy
    def insert_idml(self, idml_package, at, only):
        t = self._get_item_translation_for_insert(idml_package, at, only)
        self.remove_content(at)
        self._add_font_families_from_idml(idml_package)
        self._add_styles_from_idml(idml_package)
        self._add_mapped_styles_from_idml(idml_package)
        self._add_graphics_from_idml(idml_package)
        self._add_tags_from_idml(idml_package)
        self._add_spread_elements_from_idml(idml_package, at, only, t)
        self._add_stories_from_idml(idml_package, at, only)
        self._add_layers_from_idml(idml_package, at, only)
        self.remove_orphan_layers()
        self._xml_structure = None
        return self

    @use_working_copy
    def remove_content(self, under):
        """Recursively reach the leafs to remove the content. """
        def _remove_content(node):
            if len(node.getchildren()):
                map(_remove_content, node.iterchildren())
            xpath = self.xml_structure_tree.getpath(node)
            element_content_id = self.get_element_content_id_by_xpath(xpath)

            story = self.get_story_object_by_xpath(xpath)
            story.clear_element_content(node.get("Self"))
            story.remove_element(node.get("Self"), synchronize=True)
            # call story.remove_xml_element_page_items() for images ?

            spread = self.get_spread_object_by_xpath(xpath)
            if spread:
                spread.remove_page_item(element_content_id, synchronize=True)

        try:
            node = self.xml_structure.xpath(under)[0]
        except IndexError:
            raise IndexError(u"Cannot remove content under path '%s'. Are you sure the path exists ?" % under)
        map(_remove_content, node.iterchildren())
        # `under' node may have a reference to its first children in his story.
        story = self.get_story_object_by_xpath(under)
        story.remove_children(node.get("Self"), synchronize=True)

        self.init_lazy_references()
        return self

    @use_working_copy
    def remove_orphan_layers(self):
        for layer in self.designmap.layer_nodes:
            layer_id = layer.get("Self")
            if layer_id not in self.referenced_layers:
                self.remove_layer(layer_id)
        return self

    @use_working_copy
    def remove_layer(self, layer_id):
        self.remove_guides_on_layer(layer_id)
        self.designmap.remove_layer(layer_id, synchronize=True)
        return self

    @use_working_copy
    def remove_guides_on_layer(self, layer_id):
        for spread in self.spreads_objects:
            if spread.has_any_guide_on_layer(layer_id):
                spread.remove_guides_on_layer(layer_id, synchronize=True)
        return self

    def _add_font_families_from_idml(self, idml_package):
        # TODO Optimization. There is a linear expansion of the Fonts.xml size
        #      as packages are merged. Do something cleaver to prune or reuse
        #      fonts already here.
        fonts = Fonts(self)
        fonts.working_copy_path = self.working_copy_path
        fonts_root_elt = fonts.get_root()
        for font_family in idml_package.font_families:
            fonts_root_elt.append(copy.deepcopy(font_family))
        fonts.synchronize()

    def _add_styles_from_idml(self, idml_package):
        """Append styles to their groups or add the group in the Styles file. """
        styles = Style(self)
        styles.working_copy_path = self.working_copy_path
        styles_root_elt = styles.get_root()
        for group_to_insert in idml_package.style_groups:
            group_host = styles_root_elt.xpath(group_to_insert.tag)
            # Either the group exists.
            if group_host:
                for style_to_insert in group_to_insert.iterchildren():
                    group_host[0].append(copy.deepcopy(style_to_insert))
            # or not.
            else:
                styles_root_elt.append(copy.deepcopy(group_to_insert))
        styles.synchronize()

    def _add_mapped_styles_from_idml(self, idml_package):
        if idml_package.style_mapping:
            for style_node in idml_package.style_mapping.iter_stylenode():
                self.style_mapping.add_stylenode(style_node)
            self.style_mapping.synchronize()

        # Update designmap.xml because it may not reference the Mapping file.
        # if self Package does not have any style mapping.
        if self.designmap.style_mapping_node is None:
            self.designmap.set_style_mapping_node()
            self.designmap.synchronize()

    def _add_graphics_from_idml(self, idml_package):
        for graphic_node in idml_package.graphic.dom.iterchildren():
            self.graphic.dom.append(copy.deepcopy(graphic_node))
        self.graphic.synchronize()

    def _add_tags_from_idml(self, idml_package):
        tags = Tags(self)
        tags.working_copy_path = self.working_copy_path
        tags_root_elt = tags.get_root()
        for tag in idml_package.tags:
            if not tags_root_elt.xpath("//XMLTag[@Self='%s']" % (tag.get("Self"))):
                tags_root_elt.append(copy.deepcopy(tag))
        tags.synchronize()

    def _get_item_translation_for_insert(self, idml_package, at, only):
        """ Compute the ItemTransform shift to apply to the elements in idml_package to insert. """

        at_elem = self.get_spread_elem_by_xpath(at)
        # the first `PathPointType' tag contain the upper-left position.
        at_rel_pos_x, at_rel_pos_y = self.get_elem_point_position(at_elem, 0)
        at_transform_x, at_transform_y = self.get_elem_translation(at_elem)

        only_elem = idml_package.get_spread_elem_by_xpath(only)
        # <Image>, <EPS> and <PDF> don't store positional informations, so we use the parent <Rectangle>.
        if only_elem.tag in ["Image", "EPS", "PDF"]:
            only_elem = only_elem.getparent()
        only_rel_pos_x, only_rel_pos_y = idml_package.get_elem_point_position(only_elem, 0)
        only_transform_x, only_transform_y = idml_package.get_elem_translation(only_elem)

        x = (at_transform_x + at_rel_pos_x) - (only_transform_x + only_rel_pos_x)
        y = (at_transform_y + at_rel_pos_y) - (only_transform_y + only_rel_pos_y)

        return x, y

    def apply_translation_to_element(self, element, translation):
        """ItemTransform is a space separated string of 6 numerical values forming the transform matrix. """
        translation_x, translation_y = translation
        item_transform = element.get("ItemTransform").split(" ")
        item_transform[4] = str(Decimal(item_transform[4]) + translation_x)
        item_transform[5] = str(Decimal(item_transform[5]) + translation_y)
        element.set("ItemTransform", " ".join(item_transform))

    def _add_spread_elements_from_idml(self, idml_package, at, only, translation):
        """ Append idml_package spread elements into self.spread[0] <Spread> node. """

        spread_dest_filename = self.get_spread_by_xpath(at)
        spread_dest = Spread(self, spread_dest_filename, self.working_copy_path)
        spread_dest_elt = spread_dest.dom.xpath("./Spread")[0]

        only_node = idml_package.xml_structure.xpath(only)[0]

        # Add spread elements on the same layer. We start by that because the order in the
        # Spread file is the z-position on the Layer.
        only_layer = idml_package.get_structure_element_layer_id(only_node)
        spread_elts_to_add = idml_package.get_spread_elements_by_layer(layer_id=only_layer,
                                                                       excluded_tags=["Guide"])

        # Then add the tagged elements that may be on others layers.
        for node in only_node.iter():
            if node.get("XMLContent") is None:
                continue
            spread_elt = idml_package.get_spread_elem_by_id(node.get("XMLContent"))
            # Image and EPS element are included in a Rectangle.
            if spread_elt.tag in ["Image", "EPS"]:
                spread_elt = spread_elt.getparent()
            if spread_elt not in spread_elts_to_add:
                spread_elts_to_add.append(spread_elt)

        def _add_spread_element(spread_dest_elt, spread_elt):
            spread_elt_copy = copy.deepcopy(spread_elt)
            self.apply_translation_to_element(spread_elt_copy, translation)
            spread_dest_elt.append(spread_elt_copy)

        map(lambda s: _add_spread_element(spread_dest_elt, s), spread_elts_to_add)

        spread_dest.synchronize()
        self.init_lazy_references()

    def _add_stories_from_idml(self, idml_package, at, only):
        """Add all idml_package stories and insert `only' refence at `at' position in self.

        What we have:
        =============

        o The Story file in self containing "at" (/Root/article[3] marked by (A)) [1]:

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="udd"/> (A)
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>


        o The idml_package Story file containing "only" (/Root/module[1] marked by (B)) [2]:

            <XMLElement Self="prefixeddi2" MarkupTag="XMLTag/Root">
                <XMLElement Self="prefixeddi2i3" MarkupTag="XMLTag/module" XMLContent="prefixedu102"/> (B)
            </XMLElement>

        What we want:
        =============

        o if XMLContent is not related to a story file, we create it and insert `only' XML content:

          <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="udd">
            <XMLElement Self="prefixeddi2i3" MarkupTag="XMLTag/module" XMLContent="prefixedu102"/> (A)
          </XMLElement>

        o The Story_udd.xml is created.
        o The Spread page item 'udd' is updated.
        o The designmap.xml file is updated.

        """

        xml_element_src_id = idml_package.xml_structure.xpath(only)[0].get("Self")
        story_src_filename = idml_package.get_story_by_xpath(only)
        story_src = Story(idml_package, story_src_filename)
        story_src_elt = story_src.get_element_by_id(xml_element_src_id).element

        xml_element_dest = self.xml_structure.xpath(at)[0]
        xml_element_dest_id = xml_element_dest.get("Self")
        content_ref = xml_element_dest.get("XMLContent")

        # We don't want to lose the XMLContent referencing the spread page item.
        # Neither we want to wipe the page item out from the spread.
        # To keep the document valid, the solution is to create a proxy story.
        if content_ref and (content_ref not in self.story_ids):
            self.add_story_with_content(content_ref, xml_element_dest_id, xml_element_dest.tag)
            self.xml_element_leaf_to_node(at, content_ref)
            xml_element_dest = self.xml_structure.xpath(at)[0]

        story_dest_filename = self.get_story_by_xpath(at)
        story_dest = Story(self, story_dest_filename, self.working_copy_path)
        story_dest_elt = story_dest.get_element_by_id(xml_element_dest_id)

        story_src_elt_copy = copy.copy(story_src_elt)
        if story_src_elt_copy.get("XMLContent"):
            for child in story_src_elt_copy.iterchildren():
                story_src_elt_copy.remove(child)
        story_dest_elt.append(story_src_elt_copy)
        story_dest.synchronize()

        # Add Story files.
        # `Stories' directory may not be present in the destination package.
        stories_dirname = os.path.join(self.working_copy_path, STORIES_DIRNAME)
        if not os.path.exists(stories_dirname):
            os.mkdir(stories_dirname)
        for filename in idml_package.stories_for_node(only):
            story_cp = open(os.path.join(self.working_copy_path, filename), mode="w+")
            story_cp.write(idml_package.open(filename, mode="r").read())
            story_cp.close()

        # Update designmap.xml.
        self.designmap.add_stories(idml_package.story_ids_for_node(only))
        self.designmap.synchronize()
        # BackingStory.xml ??
        self.init_lazy_references()

    def _add_layers_from_idml(self, idml_package, at, only):
        self.designmap.add_layer_nodes(idml_package.designmap.layer_nodes)
        self.designmap.synchronize()

    @use_working_copy
    def add_pages_from_idml(self, idml_packages):
        for package, page_number, at, only in idml_packages:
            self = self.add_page_from_idml(package, page_number, at, only)
        return self

    @use_working_copy
    def add_page_from_idml(self, idml_package, page_number, at, only):
        last_spread = self.spreads_objects[-1]
        if last_spread.pages[-1].is_recto:
            last_spread = self.add_new_spread(self.working_copy_path)

        page = idml_package.pages[page_number - 1]
        last_spread.add_page(page)
        self.init_lazy_references()
        last_spread.synchronize()

        self._add_stories_from_idml(idml_package, at, only)
        self._add_font_families_from_idml(idml_package)
        self._add_styles_from_idml(idml_package)
        self._add_tags_from_idml(idml_package)

        return self

    @use_working_copy
    def add_story_with_content(self, story_id, xml_element_id, xml_element_tag):
        Story.create(self, story_id, xml_element_id, xml_element_tag, self.working_copy_path)
        self.designmap.add_stories([story_id])
        self.designmap.synchronize()
        self.init_lazy_references()
        return self

    @use_working_copy
    def merge_layers(self, with_name=None):
        # Remove all Layer in Designmap but the first.
        self.designmap.merge_layers(with_name)
        layer_id = self.designmap.active_layer

        # Update ItemLayer in spread elements.
        for spread_object in self.spreads_objects:
            spread_object.set_layer_references(layer_id)
        return self

    @use_working_copy
    def xml_element_leaf_to_node(self, xpath, xml_content_ref):
        spread = self.get_spread_object_by_xpath(xpath)
        page_item = spread.get_element_by_id(xml_content_ref, tag="*", attr="Self")

        page_item.set("ParentStory", xml_content_ref)
        page_item.set("Self", "%sToNode" % xml_content_ref)

        # To be a node, a Rectangle must be converted into a TextFrame.
        # There is not simple way to change the tag of a XMLElement so
        # a new copy is created.
        if page_item.tag == "Rectangle":
            spread.rectangle_to_textframe(page_item)
        spread.synchronize()
        return self

    def add_new_spread(self, working_copy_path):
        """Create a new empty Spread in the working copy from the last one. """

        last_spread = self.spreads_objects[-1]
        # TODO : make sure the filename does not exists.
        new_spread_name = increment_filename(last_spread.name)
        new_spread_wc_path = os.path.join(working_copy_path, new_spread_name)
        shutil.copy2(
            os.path.join(working_copy_path, last_spread.name),
            new_spread_wc_path
        )
        self._spreads_objects = None

        new_spread = Spread(self, new_spread_name, working_copy_path)
        new_spread.clear()
        new_spread.node.set("Self", new_spread.get_node_name_from_xml_name())

        self.designmap.add_spread(new_spread)
        self.designmap.synchronize()

        # The spread synchronization is done outside.
        return new_spread

    def get_spread_elements_by_layer(self, layer_name=None, layer_id=None, excluded_tags=[]):
        layer_id = layer_id or self.get_layer_id_by_name(layer_name)

        spread_elements = []
        for spread_object in self.spreads_objects:
            spread_elements.extend(spread_object.dom.xpath(
                ".//*%(excluded_tags)s[@ItemLayer='%(layer_id)s']" % {
                    'excluded_tags': "".join(["[not(self::%s)]" % e for e in excluded_tags]),
                    'layer_id': layer_id}))

        return spread_elements

    def get_spread_object_by_name(self, name):
        """ - name : 'Spreads/Spread_mainub6.xml' """
        return filter(lambda s: s.name == name, self.spreads_objects)[0]

    def get_spread_object_by_xpath(self, xpath):
        elt_id = self.xml_structure.xpath(xpath)[0].get("XMLContent")
        return self.get_spread_object_by_id(elt_id)

    def get_spread_object_by_id(self, elt_id):
        """elt_id is the `XMLContent' attribute value in the xml_structure (Stories).

        Spread element matches Story one with the ParentStory or the Self attribute value."""

        result = None
        for spread in self.spreads_objects:
            if (
                spread.get_element_by_id(elt_id, tag="*") is not None or
                spread.get_element_by_id(elt_id, tag="*", attr="ParentStory") is not None
            ):
                result = spread
            # FIXME: That's ugly. return spread here ?
            if result:
                break
        return result

    def get_spread_elem_by_xpath(self, xpath):
        """Return the spread etree.Element matching the xml_structure's xpath. """
        spread = self.get_spread_object_by_xpath(xpath)
        elt_id = self.xml_structure.xpath(xpath)[0].get("XMLContent")
        elt = spread.get_element_by_id(elt_id, tag="*")
        if elt is None:
            elt = spread.get_element_by_id(elt_id, tag="*", attr="ParentStory")
        return elt

    def get_spread_elem_by_id(self, elt_id):
        """Return the spread etree.Element designed by XMLContent value. """
        spread = self.get_spread_object_by_id(elt_id)
        elt = spread.get_element_by_id(elt_id, tag="*")
        if elt is None:
            elt = spread.get_element_by_id(elt_id, tag="*", attr="ParentStory")
        return elt

    def get_spread_by_xpath(self, xpath):
        spread = self.get_spread_object_by_xpath(xpath)
        return spread and spread.name or None

    def get_layer_id_by_name(self, layer_name):
        return self.designmap.get_layer_id_by_name(layer_name)

    def get_active_layer_name(self):
        return self.designmap.get_active_layer_name()

    def get_structure_element_layer_id(self, xml_element):
        spread_elt = self.get_spread_elem_by_id(xml_element.get("XMLContent"))
        return self.get_spread_element_layer_id(spread_elt)

    def get_spread_element_layer_id(self, spread_element):
        return spread_element.get("ItemLayer") or \
            self.get_spread_element_layer_id(spread_element.getparent())

    def get_story_object_by_xpath(self, xpath):
        xml_element = self.xml_structure.xpath(xpath)[0]

        def get_story_name(xml_element):
            ref = xml_element.get("XMLContent")
            if ref:
                return ref
            else:
                parent = xml_element.getparent()
                if parent is not None:
                    return get_story_name(xml_element.getparent())
                else:
                    return BACKINGSTORY

        story_name = get_story_name(xml_element)

        # Some XMLElement store a reference which is not a Story.
        # In that case, the Story is the parent's Story.
        if (story_name not in self.story_ids) and (story_name is not BACKINGSTORY):
            xpath = self.xml_structure_tree.getpath(xml_element.getparent())
            story = self.get_story_object_by_xpath(xpath)
        else:
            if story_name == BACKINGSTORY:
                story = BackingStory(self)
            else:
                story = Story(self, "%s/Story_%s.xml" % (STORIES_DIRNAME, story_name))
        story.working_copy_path = self.working_copy_path
        return story

    def get_story_by_xpath(self, xpath):
        story = self.get_story_object_by_xpath(xpath)
        return story and story.name or None

    def get_element_content_id_by_xpath(self, xpath):
        return self.xml_structure.xpath(xpath)[0].get("XMLContent")

    def get_elem_point_position(self, elem, point_index=0):
        point = elem.xpath("Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType")[point_index]
        x, y = point.get("Anchor").split(" ")
        return Decimal(x), Decimal(y)

    def get_elem_translation(self, elem):
        item_transform = elem.get("ItemTransform").split(" ")
        return Decimal(item_transform[4]), Decimal(item_transform[5])
