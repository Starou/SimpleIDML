# -*- coding: utf-8 -*-

import os
import shutil
import zipfile
import re
import copy
from decimal import Decimal

from lxml import etree
from xml.dom.minidom import parseString

from simple_idml.components import get_idml_xml_file_by_name
from simple_idml.components import (Designmap, Spread, Story, BackingStory,
                                    Style, StyleMapping, Graphic, Tags, Fonts, XMLElement)
from simple_idml.decorators import use_working_copy
from simple_idml.utils import increment_filename, prefix_content_filename

from simple_idml import IdPkgNS, BACKINGSTORY

STORIES_DIRNAME = "Stories"


class IDMLPackage(zipfile.ZipFile):
    """An IDML file (a package) is a Zip-stored archive/UCF container. """

    def __init__(self, *args, **kwargs):
        kwargs["compression"] = zipfile.ZIP_STORED
        zipfile.ZipFile.__init__(self, *args, **kwargs)
        self.working_copy_path = None
        self.init_lazy_references()

    def init_lazy_references(self):
        self._XMLStructure = None
        self._xml_structure_tree = None
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

    def namelist(self):
        if not self.working_copy_path:
            return zipfile.ZipFile.namelist(self)
        else:
            trailing_slash_wc = "%s/" % self.working_copy_path
            namelist = []
            for root, dirs, filenames in os.walk(self.working_copy_path):
                trailing_slash_root = "%s/" % root
                rel_root = trailing_slash_root.replace(trailing_slash_wc, "")
                for filename in filenames:
                    namelist.append("%s%s" % (rel_root, filename))
            return namelist

    def contentfile_namelist(self):
        """Namelist filtered on Spreads and Stories. """
        return [f for f in self.namelist() if os.path.dirname(f) in ("Spreads", "Stories")]

    @property
    def XMLStructure(self):
        """ Discover the XML structure from the story files.

        Starting at BackingStory.xml where the root-element is expected (because unused). """

        if self._XMLStructure is None:
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
            self._XMLStructure = structure
        return self._XMLStructure

    @property
    def xml_structure_tree(self):
        if self._xml_structure_tree is None:
            xml_structure_tree = etree.ElementTree(self.XMLStructure)
            self._xml_structure_tree = xml_structure_tree
        return self._xml_structure_tree

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

    @property
    def story_ids(self):
        """ extract  `ID' from `Stories/Story_ID.xml'. """
        if self._story_ids is None:
            rx_story_id = re.compile(r"%s/Story_([\w]+)\.xml" % STORIES_DIRNAME)
            story_ids = [rx_story_id.match(elt).group(1) for elt in self.stories]
            self._story_ids = story_ids
        return self._story_ids

    def get_xml_element_story(self, xml_element):
        """xml_element is a structure element."""
        STORY_REF_ATTR = "XMLContent"
        def get_story_id(xml_element):
            ref = xml_element.get(STORY_REF_ATTR)
            if ref:
                return ref
            else:
                parent = xml_element.getparent()
                if parent is not None:
                    return get_story_id(xml_element.getparent())
                else:
                    return BACKINGSTORY

        story_id = get_story_id(xml_element)

        # Some XMLElement store a reference which is not a Story.
        # In that case, the Story it the parent's Story.
        if (story_id not in self.story_ids) and (story_id is not BACKINGSTORY):
            story = self.get_xml_element_story(xml_element.getparent())
        else:
            if story_id == BACKINGSTORY:
                story = BackingStory(idml_package=self)
            else:
                story = Story(idml_package=self, 
                              name="%s/Story_%s.xml" % (STORIES_DIRNAME, story_id))
        story.working_copy_path = self.working_copy_path
        return story

    @use_working_copy
    def import_xml(self, xml_file, at, working_copy_path=None):
        """ Reproduce the action «Import XML» on a XML Element in InDesign® Structure. """

        source_node = etree.fromstring(xml_file.read())
        # destination_node is not the node in story file, but a representation from self.XMLStructure.
        destination_node = self.XMLStructure.xpath(at)[0]

        def _set_content(destination_node, content):
            element_id = destination_node.get("Self")
            story = self.get_xml_element_story(destination_node)
            story.set_element_content(element_id, content)
            story.synchronize()

        def _set_attributes(destination_node, items):
            element_id = destination_node.get("Self")
            story = self.get_xml_element_story(destination_node)
            story.set_element_attributes(element_id, items)
            # Image references must be updated in the page item in Spread or Story.
            if "href" in items:
                resource_path = items.get("href")
                xpath = self.xml_structure_tree.getpath(destination_node)
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

        def _import_xml(source_node, destination_node):
            items = dict(source_node.items())
            if items:
                _set_attributes(destination_node, items)
            if not (items.get("simpleidml-setcontent") == "false"):
                _set_content(destination_node, source_node.text or "")

            source_node_children = source_node.getchildren()
            if len(source_node_children):
                element_id = destination_node.get("Self")
                source_node_children_tags = [n.tag for n in source_node_children]
                destination_node_children = destination_node.iterchildren()
                destination_node_children_tags = [n.tag for n in destination_node.iterchildren()]
                # FIXME: what if source_node.text exists ?
                if destination_node_children_tags == source_node_children_tags:
                    map(_import_xml, source_node_children, destination_node.iterchildren())
                else:
                    destination_node_child = next(destination_node_children, None)
                    for i, source_child in enumerate(source_node_children):
                        # Source and destination match.
                        if destination_node_child is not None and source_child.tag == destination_node_child.tag:
                            _import_xml(source_child, destination_node_child)
                            destination_node_child = next(destination_node_children, None)
                        # Only mapped style tags are added.
                        elif source_child.tag in self.style_mapping.character_style_mapping.keys():
                            style_name = self.style_mapping.character_style_mapping[source_child.tag]
                            style_node = self.style.get_style_node_by_name(style_name)
                            story = self.get_xml_element_story(destination_node)
                            parent = story.get_element_by_id(element_id)
                            new_xml_element = XMLElement(tag=source_child.tag)
                            new_xml_element.add_content(source_child.text, parent, style_node=style_node)
                            story.add_element(element_id, new_xml_element.element)
                            if source_child.tail:
                                story.add_content_to_element(element_id, source_child.tail, parent)
                            story.synchronize()

        _import_xml(source_node, destination_node)
        return self

    def export_xml(self, from_tag=None):
        """ Reproduce the action «Export XML» on a XML Element in InDesign® Structure. """
        if not from_tag:
            export_from_node = self.XMLStructure
        else:
            # TODO
            pass
        dom = etree.Element(export_from_node.tag)

        def append_content(source_node, destination_node):
            # Retouver le node de la Story correspondant au node source_node.
            # Si ce node contient une sous balise <content>, l'ajouter au contenu
            # de la destination.
            source_node_children = source_node.getchildren()

            story = self.get_xml_element_story(source_node)
            story_content_nodes = None
            try:
                story.fobj
            except KeyError:
                pass
            else:
                story_node = story.get_element_by_id(source_node.get("Self"))
                for attr, value in story_node.get_attributes().items():
                    destination_node.set(attr, value)
                story_content_nodes = story.get_element_content_nodes(story_node)
            if story_content_nodes and not source_node_children:
                #TODO join() with XML_PARAGRAPH_SEP if getnext().tag == "Br"
                # XML_PARAGRAPH_SEP = u"\u2029"
                destination_node.text = "".join([c.text or "" for c in story_content_nodes])
            elif not story_content_nodes and source_node_children:
                for elt in source_node_children:
                    new_destination_node = etree.Element(elt.tag)
                    destination_node.append(new_destination_node)
                    append_content(elt, new_destination_node)
            elif story_content_nodes and source_node_children:
                last_child_inserted = None
                for story_content_node in story_content_nodes:
                    xml_element_for_content = story_content_node.iterancestors("XMLElement").next()
                    if (
                        not source_node_children or
                        (xml_element_for_content.get("Self") != source_node_children[0].get("Self"))
                    ):
                        if last_child_inserted is None:
                            # There should be several <Content> nodes.
                            destination_node.text = (destination_node.text or "") + \
                                                    (story_content_node.text or "")
                        else:
                            last_child_inserted.tail = (last_child_inserted.tail or "") + \
                                                       (story_content_node.text)
                    else:
                        xml_element_child = source_node_children.pop(0)
                        last_child_inserted = etree.Element(xml_element_child.tag)
                        destination_node.append(last_child_inserted)
                        append_content(xml_element_child, last_child_inserted)

        append_content(export_from_node, dom)
        return etree.tostring(dom, pretty_print=True)

    @use_working_copy
    def prefix(self, prefix, working_copy_path=None):
        """Change references and filename by inserting `prefix_` everywhere.

        files in ZipFile cannot be renamed or moved so we make a copy of it.
        """

        # Change the references inside the file.
        for filename in self.namelist():
            if (os.path.basename(filename) in ["container.xml", "metadata.xml"] or
                os.path.splitext(filename)[1] != ".xml"):
                continue
            idml_xml_file = get_idml_xml_file_by_name(self, filename, working_copy_path)
            idml_xml_file.prefix_references(prefix)
            idml_xml_file.synchronize()

        # Story and Spread XML files are "prefixed".
        for filename in self.contentfile_namelist():
            new_basename = prefix_content_filename(os.path.basename(filename),
                                                   prefix, "filename")
            # mv file in the new archive with the prefix.
            old_name = os.path.join(working_copy_path, filename)
            new_name = os.path.join(os.path.dirname(old_name), new_basename)
            os.rename(old_name, new_name)

        # Update designmap.xml.
        designmap = Designmap(self, working_copy_path=working_copy_path)
        designmap.prefix_page_start(prefix)
        designmap.synchronize()

        return self

    @use_working_copy
    def insert_idml(self, idml_package, at, only, working_copy_path=None):
        t = self._get_item_translation_for_insert(idml_package, at, only)
        self._add_font_families_from_idml(idml_package)
        self._add_styles_from_idml(idml_package)
        self._add_mapped_styles_from_idml(idml_package)
        self._add_graphics_from_idml(idml_package)
        self._add_tags_from_idml(idml_package)
        self._add_spread_elements_from_idml(idml_package, at, only, t)
        self._add_stories_from_idml(idml_package, at, only)
        self._XMLStructure = None
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
        designmap = Designmap(self, working_copy_path=self.working_copy_path)
        if designmap.style_mapping_node is not None:
            designmap.set_style_mapping_node()
            designmap.synchronize()

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

        # There should be only one spread in the idml_package.
        spread_src = idml_package.spreads_objects[0]
        spread_dest_filename = self.get_spread_by_xpath(at)
        spread_dest = Spread(self, spread_dest_filename, self.working_copy_path)
        spread_dest_elt = spread_dest.dom.xpath("./Spread")[0]

        for child in spread_src.dom.xpath("./Spread")[0].iterchildren():
            if child.tag in ["Page", "FlattenerPreference"]:
                continue
            child_copy = copy.deepcopy(child)
            self.apply_translation_to_element(child_copy, translation)
            spread_dest_elt.append(child_copy)
        spread_dest.synchronize()

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

        o At (A) in the file in [1] we are pointing to (B):

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article"> (A)
                    <XMLElement Self="prefixeddi2i3" MarkupTag="XMLTag/module" XMLContent="prefixedu102"/> (A)
                </XMLElement>
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>

        o The designmap.xml file is updated [6].

        """

        xml_element_src_id = idml_package.XMLStructure.xpath(only)[0].get("Self")
        story_src_filename = idml_package.get_node_story_by_xpath(only)
        story_src = Story(idml_package, story_src_filename)
        story_src_elt = story_src.get_element_by_id(xml_element_src_id).element

        xml_element_dest_id = self.XMLStructure.xpath(at)[0].get("Self")
        story_dest_filename = self.get_node_story_by_xpath(at)
        story_dest = Story(self, story_dest_filename, self.working_copy_path)
        story_dest_elt = story_dest.get_element_by_id(xml_element_dest_id)

        if story_dest_elt.get("XMLContent"):
            story_dest_elt.attrib.pop("XMLContent")
        story_src_elt_copy = copy.copy(story_src_elt)
        if story_src_elt_copy.get("XMLContent"):
            for child in story_src_elt_copy.iterchildren():
                story_src_elt_copy.remove(child)
        story_dest_elt.append(story_src_elt_copy)
        story_dest.synchronize()

        # Stories files are added.
        # `Stories' directory may not be present in the destination package.
        stories_dirname = os.path.join(self.working_copy_path, STORIES_DIRNAME)
        if not os.path.exists(stories_dirname):
            os.mkdir(stories_dirname)
        # TODO: add only the stories required.
        for filename in idml_package.stories:
            story_cp = open(os.path.join(self.working_copy_path, filename), mode="w+")
            story_cp.write(idml_package.open(filename, mode="r").read())
            story_cp.close()

        # Update designmap.xml.
        designmap = Designmap(self, working_copy_path=self.working_copy_path)
        designmap.add_stories(idml_package.story_ids)
        designmap.synchronize()
        # BackingStory.xml ??

    @use_working_copy
    def add_pages_from_idml(self, idml_packages, working_copy_path=None):
        for package, page_number, at, only in idml_packages:
            self = self.add_page_from_idml(package, page_number, at, only,
                                           working_copy_path=working_copy_path)
        return self

    @use_working_copy
    def add_page_from_idml(self, idml_package, page_number, at, only, working_copy_path=None):
        last_spread = self.spreads_objects[-1]
        if last_spread.pages[-1].is_recto:
            last_spread = self.add_new_spread(working_copy_path)

        page = idml_package.pages[page_number - 1]
        last_spread.add_page(page)
        self.init_lazy_references()
        last_spread.synchronize()

        self._add_stories_from_idml(idml_package, at, only)
        self._add_font_families_from_idml(idml_package)
        self._add_styles_from_idml(idml_package)
        self._add_tags_from_idml(idml_package)

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

        designmap = Designmap(self, working_copy_path=working_copy_path)
        designmap.add_spread(new_spread)
        designmap.synchronize()

        # The spread synchronization is done outside.
        return new_spread

    def get_spread_by_xpath(self, xpath):
        """ Search for the spread file having the element identified by the XMLContent attribute
        of the XMLElement pointed by xpath value."""

        result = None
        reference = self.XMLStructure.xpath(xpath)[0].get("XMLContent")
        for spread in self.spreads_objects:
            if (
                spread.get_element_by_id(reference, tag="*") is not None or
                spread.get_element_by_id(reference, tag="*", attr="ParentStory") is not None
            ):
                result = spread.name
            if result:
                break
        return result

    def get_spread_object_by_xpath(self, xpath):
        out = None
        filename = self.get_spread_by_xpath(xpath)
        for spread in self.spreads_objects:
            if filename == spread.name:
                out = spread
                break
        return out

    def get_element_content_id_by_xpath(self, xpath):
        return self.XMLStructure.xpath(xpath)[0].get("XMLContent")

    def get_node_story_by_xpath(self, xpath):
        """Return the Story (or BackingStory) filename containing the element selected by xpath."""
        node = self.XMLStructure.xpath(xpath)[0]
        return self.get_xml_element_story(node).name

    # TODO: use Spread.get_element_by_id(self.get_element_content_id_by_xpath(xpath)) instead.
    def get_spread_elem_by_xpath(self, xpath):
        """Return the spread etree.Element designed by XMLElement xpath. """

        spread_filename = self.get_spread_by_xpath(xpath)
        spread = Spread(self, spread_filename)
        elt_id = self.XMLStructure.xpath(xpath)[0].get("XMLContent")
        elt = spread.get_element_by_id(elt_id, tag="*")
        if elt is None:
            elt = spread.get_element_by_id(elt_id, tag="*", attr="ParentStory")
        return elt

    def get_elem_point_position(self, elem, point_index=0):
        point = elem.xpath("Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType")[point_index]
        x, y = point.get("Anchor").split(" ")
        return Decimal(x), Decimal(y)

    def get_elem_translation(self, elem):
        item_transform = elem.get("ItemTransform").split(" ")
        return Decimal(item_transform[4]), Decimal(item_transform[5])
