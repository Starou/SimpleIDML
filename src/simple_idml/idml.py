# -*- coding: utf-8 -*-

import os, shutil
import zipfile
import re
import copy
from decimal import Decimal

from lxml import etree
from xml.dom.minidom import parseString

from simple_idml.decorators import use_working_copy

BACKINGSTORY = "XML/BackingStory.xml"
TAGS = "XML/Tags.xml"

xmltag_prefix = "XMLTag/"
rx_contentfile = re.compile(r"^(Story_|Spread_)(.+\.xml)$")
rx_contentfile2 = re.compile(r"^(Stories/Story_|Spreads/Spread_)(.+\.xml)$")

rx_story_id = re.compile(r"Stories/Story_([\w]+)\.xml")

excluded_tags_for_prefix = [
    "Document",
    "Language",
    "NumberingList",
    "NamedGrid",
    "TextVariable",
    "Layer",
    "Section",
    "DocumentUser",
    "CrossReferenceFormat",
    "BuildingBlock",
    "IndexingSortOption",
    "ABullet",
    "Assignment",
    "XMLTag",
    "Page", # or update designmap.xml: <Section Self="uc9" Length="4" Name="" ... PageStart="ubb" SectionPrefix=""> ?
    "MasterSpread",
]

doctypes = {
    'designmap.xml': u'<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="7.5(142)" ?>',
}

def create_idml_package_from_dir(dir_path, package_path=None):
    # TODO. raise exception, add a parameter to force overwrite.
    if os.path.exists(package_path):
        print "%s already exists." % package_path
        return None

    package = IDMLPackage(package_path, mode="w")

    for root, dirs, filenames in os.walk(dir_path):
        for filename in filenames:
            package.write(os.path.join(root, filename),
                          os.path.join(root.replace(dir_path, "."), filename))
    return package


class IDMLPackage(zipfile.ZipFile):
    """An IDML file (a package) is a Zip-stored archive/UCF container. """

    def __init__(self, *args, **kwargs):
        kwargs["compression"] = zipfile.ZIP_STORED
        zipfile.ZipFile.__init__(self, *args, **kwargs)
        self._XMLStructure = None
        self._tags = None
        self._spreads = None
        self._stories = None
        self._story_ids = None

    @property
    def XMLStructure(self):
        """ Discover the XML structure from the story files.
        
        Starting at BackingStory.xml where the root-element is expected (because unused).
        Read a XML document and write another one in a parallel manner.
        """

        if self._XMLStructure is None:
            backing_story = self.open(BACKINGSTORY, mode="r")
            backing_story_doc = XMLDocument(xml_file=backing_story)

            root_elt = backing_story_doc.dom.find("*//XMLElement")
            structure = XMLDocument(XMLElement=root_elt)

            def append_childs(source_node, destination_node):
                """Recursive function to discover node structure from a story to another. """
                for elt in source_node.iter("XMLElement"):
                    if elt.get("Self") == source_node.get("Self"):
                        continue
                    new_destination_node = XMLElementToElement(elt)
                    destination_node.append(new_destination_node)
                    if elt.get("XMLContent"):
                        xml_content_value = elt.get("XMLContent")
                        story_filename = self.get_story_filename_by_xml_value(xml_content_value)
                        try:
                            story = self.open(story_filename, mode="r")
                        except KeyError:
                            continue
                        else:
                            story_doc = XMLDocument(xml_file=story)
                            # Prendre la valeur de cet attribut pour retrouver la Story.
                            # Parser cette story.
                            new_source_node = story_doc.getElementById(elt.get("Self"))
                            append_childs(new_source_node, new_destination_node)
                            story.close()

            append_childs(root_elt, structure.dom)

            backing_story.close()
            self._XMLStructure = structure
        return self._XMLStructure

    @property
    def tags(self):
        if self._tags is None:
            tags_src = self.open(TAGS, mode="r")
            tags_doc = XMLDocument(tags_src)
            tags = [copy.deepcopy(elt) for elt in tags_doc.dom.xpath("//XMLTag")]
            self._tags = tags
            tags_src.close()
        return self._tags
            
    @property
    def spreads(self):
        if self._spreads is None:
            spreads = [elt for elt in self.namelist() if re.match(ur"^Spreads/*", elt)]
            self._spreads = spreads
        return self._spreads
            
    @property
    def stories(self):
        if self._stories is None:
            stories = [elt for elt in self.namelist() if re.match(ur"^Stories/*", elt)]
            self._stories = stories
        return self._stories
            
    @property
    def story_ids(self):
        """ extract  `ID' from `Stories/Story_ID.xml'. """
        if self._story_ids is None:
            story_ids = [rx_story_id.match(elt).group(1) for elt in self.stories]
            self._story_ids = story_ids
        return self._story_ids
            
    @use_working_copy
    def prefix(self, prefix, working_copy_path=None):
        """Change references and filename by inserting `prefix_` everywhere. 
        
        files in ZipFile cannot be renamed or moved so we make a copy of it.
        """

        # Change the references inside the file.
        for root, dirs, filenames in os.walk(working_copy_path):
            if os.path.basename(root) in ["META-INF",]:
                continue
            for filename in filenames:
                if os.path.splitext(filename)[1] != ".xml":
                    continue
                abs_filename = os.path.join(root, filename)
                xml_file = open(abs_filename, mode="r")
                doc = XMLDocument(xml_file)
                doc.prefix_references(prefix)
                doc.overwrite_and_close(ref_doctype=filename)

        # Story and Spread XML files are "prefixed".
        for filename in self.namelist():
            if rx_contentfile.match(os.path.basename(filename)):
                new_basename = prefix_content_filename(os.path.basename(filename),
                                                       prefix, rx_contentfile)
                # mv file in the new archive with the prefix.
                old_name = os.path.join(working_copy_path, filename)
                new_name = os.path.join(os.path.dirname(old_name), new_basename)
                os.rename(old_name, new_name)

        return self

    def insert_idml(self, idml_package, at, only):
        self._add_fonts_from_idml(idml_package)
        self._add_graphic_from_idml(idml_package)
        p = self._add_tags_from_idml(idml_package)
        t = self._get_item_translation_for_insert(idml_package, at, only)
        p = p._add_spread_elements_from_idml(idml_package, at, only, t)
        p = p._add_stories_from_idml(idml_package, at, only)
        p._XMLStructure = None
        return p

    def _add_fonts_from_idml(self, idml_package):
        pass

    def _add_graphic_from_idml(self, idml_package):
        pass

    @use_working_copy
    def _add_tags_from_idml(self, idml_package, working_copy_path=None):
        tags_abs_filename = os.path.join(working_copy_path, TAGS)
        tags = open(tags_abs_filename, mode="r")
        tags_doc = XMLDocument(tags)
        tags_root_elt = tags_doc.dom.xpath("/idPkg:Tags", 
                                  namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"})[0]
        for tag in idml_package.tags:
            if not tags_root_elt.xpath("//XMLTag[@Self='%s']"%(tag.get("Self"))):
                tags_root_elt.append(copy.deepcopy(tag))
            
        tags_doc.overwrite_and_close(ref_doctype=None)
        return self

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

    @use_working_copy
    def _add_spread_elements_from_idml(self, idml_package, at, only, translation, working_copy_path=None):
        """ Append idml_package spread elements into self.spread[0] <Spread> node. """

        # There should be only one spread in the idml_package.
        spread_src = idml_package.open(idml_package.spreads[0], mode="r")
        spread_src_doc = XMLDocument(spread_src)

        spread_dest_filename = self.get_spread_by_xpath(at)
        spread_dest_abs_filename = os.path.join(working_copy_path, spread_dest_filename)
        spread_dest = open(spread_dest_abs_filename, mode="r")
        spread_dest_doc = XMLDocument(spread_dest)
        spread_dest_elt = spread_dest_doc.dom.xpath("./Spread")[0]

        for child in spread_src_doc.dom.xpath("./Spread")[0].iterchildren():
            if child.tag in ["Page", "FlattenerPreference"]:
                continue
            child_copy = copy.deepcopy(child)
            self.apply_translation_to_element(child_copy, translation)
            spread_dest_elt.append(child_copy)

        spread_dest_doc.overwrite_and_close(ref_doctype=None)
        return self

    @use_working_copy
    def _add_stories_from_idml(self, idml_package, at, only, working_copy_path=None):
        """Add all idml_package stories and insert `only' refence at `at' position in self. 
        
        What we have:
        =============
        
        o The Story file in self containing "at" (say /Root/article[3] or "udd") [1]:

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="udd"/> (A)
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>


        o The idml_package Story file containing "only" (say /Root/module[1] or "prefixedu102") [2]:
        
            <XMLElement Self="prefixeddi2" MarkupTag="XMLTag/Root">
                <XMLElement Self="prefixeddi2i3" MarkupTag="XMLTag/module" XMLContent="prefixedu102"/> (B)
            </XMLElement>

        What we need:
        =============

        o At (A) in the file in [1] we are pointing to (B):

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article"> (A)
                    <XMLElement Self="prefixeddi2i3" MarkupTag="XMLTag/article" XMLContent="prefixedu102"/> (A)
                </XMLElement>
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>

        o The designmap.xml file is updated [6].
        
        """

        xml_element_src = idml_package.XMLStructure.dom.xpath(only)[0]
        story_src_filename = idml_package.get_story_by_xpath(only)
        story_src = idml_package.open(story_src_filename, mode="r")
        story_src_doc = XMLDocument(story_src)
        story_src_elt = story_src_doc.dom.xpath("//XMLElement[@XMLContent='%s']" % xml_element_src.get("XMLContent"))[0]

        xml_element_dest = self.XMLStructure.dom.xpath(at)[0]
        story_dest_filename = self.get_story_by_xpath(at)
        story_dest_abs_filename = os.path.join(working_copy_path, story_dest_filename)
        story_dest = open(story_dest_abs_filename, mode="r")
        story_dest_doc = XMLDocument(story_dest)
        story_dest_elt = story_dest_doc.dom.xpath("//XMLElement[@XMLContent='%s']" % xml_element_dest.get("XMLContent"))[0]
        story_dest_elt.attrib.pop("XMLContent")
        story_dest_elt.append(copy.copy(story_src_elt))

        story_dest_doc.overwrite_and_close(ref_doctype=None)

        # Stories files are added.
        for filename in idml_package.stories:
            story_cp = open(os.path.join(working_copy_path, filename), mode="w+")
            story_cp.write(idml_package.open(filename, mode="r").read())
            story_cp.close()

        # Update designmap.xml.
        designmap_abs_filename = os.path.join(working_copy_path, "designmap.xml")
        designmap = open(designmap_abs_filename, mode="r")
        designmap_doc = XMLDocument(designmap)
        add_stories_to_designmap(designmap_doc.dom, idml_package.story_ids)
        designmap_doc.overwrite_and_close(ref_doctype="designmap.xml")

        return self
        # BackingStory.xml ??

    def get_spread_by_xpath(self, xpath):
        """ Search for the spread file having the element identified by the XMLContent attribute
        of the XMLElement pointed by xpath value."""

        #TODO: caching.
        result = None
        reference = self.XMLStructure.dom.xpath(xpath)[0].get("XMLContent")
        for filename in self.spreads:
            spread = self.open(filename, mode="r")
            spread_doc = XMLDocument(spread)
            if spread_doc.getElementById(reference, tag="*") is not None or \
               spread_doc.getElementById(reference, tag="*", attr="ParentStory") is not None:
                result = filename
            spread.close()
            if result:
                break
        return result

    def get_story_by_xpath(self, xpath):
        """Return the story (or BackingStory) filename containing the element selected by xpath string."""

        #TODO: caching, unittest.
        result = None
        reference = self.XMLStructure.dom.xpath(xpath)[0].get("Self")
        for filename in [BACKINGSTORY]+self.stories:
            story = self.open(filename, mode="r")
            story_doc = XMLDocument(story)
            if story_doc.dom.xpath("//*[@Self='%s']" % reference):
                result = filename
            story.close()
            if result:
                break
        return result

    def get_spread_elem_by_xpath(self, xpath):
        """Return the spread etree.Element designed by XMLElement xpath. """

        spread_filename = self.get_spread_by_xpath(xpath)
        spread_file = self.open(spread_filename, mode="r")
        spread_doc = XMLDocument(spread_file)
        elt_id = self.XMLStructure.dom.xpath(xpath)[0].get("XMLContent")
        # etree FutureWarning when trying to simply do elt = X or Y.
        elt = spread_doc.getElementById(elt_id, tag="*") 
        if elt is None:
            elt = spread_doc.getElementById(elt_id, tag="*", attr="ParentStory")
        spread_file.close()

        return elt

    # TODO: rename in get_story_filename_by_reference ?
    def get_story_filename_by_xml_value(self, xml_value):
        return u"Stories/Story_%s.xml" % xml_value

    def get_elem_point_position(self, elem, point_index=0):
        point = elem.xpath("Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType")[point_index]
        x, y = point.get("Anchor").split(" ")
        return Decimal(x), Decimal(y)

    def get_elem_translation(self, elem):
        item_transform = elem.get("ItemTransform").split(" ")
        return Decimal(item_transform[4]), Decimal(item_transform[5])

class XMLDocument(object):
    """An etree document wrapper to fit IDML XML Structure."""
    
    def __init__(self, xml_file=None, XMLElement=None):
        if xml_file:
            self.xml_file = xml_file
            self.dom = etree.fromstring(xml_file.read())
        elif XMLElement is not None:
            self.dom = XMLElementToElement(XMLElement)
        else:
            raise BaseException, "You must provide either a xml file or a name."

    def getElementById(self, id, tag="XMLElement", attr="Self"):
        """ tag is by default XMLElement, the XML tag representing the InDesign XML structure inside IDML files."""
        return self.dom.find("*/%s[@%s='%s']" % (tag, attr, id))

    def prefix_references(self, prefix):
        """Update references inside various XML files found in an IDML package after a call to prefix()."""

        # <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
        # <[Spread|Page|...] Self="ub6" FlattenerOverride="Default" 
        # <[TextFrame|...] Self="uca" ParentStory="u102" ...>
        for elt in self.dom.iter():
            if elt.tag in excluded_tags_for_prefix:
                continue
            for attr in ("Self", "XMLContent", "ParentStory"):
                if elt.get(attr):
                    #TODO prefix_element_attr(attr, prefix)
                    elt.set(attr, "%s%s" % (prefix, elt.get(attr)))

        # <idPkg:Spread src="Spreads/Spread_ub6.xml"/>
        # <idPkg:Story src="Stories/Story_u139.xml"/>
        for elt in self.dom.xpath(".//idPkg:Spread | .//idPkg:Story", 
                                  namespaces={'idPkg': "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"}):
            if elt.get("src") and rx_contentfile2.match(elt.get("src")):
                elt.set("src", prefix_content_filename(elt.get("src"), prefix, rx_contentfile2))

        # <Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"... StoryList="ue4 u102 u11b u139 u9c"...>
        elt = self.dom.xpath("/Document")
        if elt and elt[0].get("StoryList"):
            elt[0].set("StoryList", " ".join(["%s%s" % (prefix, s) 
                                           for s in elt[0].get("StoryList").split(" ")]))

    def tostring(self, ref_doctype=None):
        return etree.tostring(self.dom,
                              xml_declaration=True,
                              encoding="UTF-8",
                              standalone=True,
                              doctype=doctypes.get(ref_doctype, None),
                              pretty_print=True)

    def overwrite_and_close(self, ref_doctype=None):
        new_xml = self.tostring(ref_doctype)
        filename = self.xml_file.name
        self.xml_file.close()
        xml_file = open(filename, mode="w+")
        xml_file.write(new_xml)
        xml_file.close()


def XMLElementToElement(XMLElement):
    """ Extract data from a XMLElement tag to restore the tag as seen by the ID end-user.

    CamelCase Capfirst function name to keep the track.
      o XMLElement are XML tags inside IDML file to express the XML structure of the IDML
        document as seen by the end-user (not the developpers).
    """
    attrs = dict(XMLElement.attrib)
    name = attrs.pop("MarkupTag").replace(xmltag_prefix, "")
    return etree.Element(name, **attrs)

def prefix_content_filename(filename, prefix, rx):
    start, end = rx.match(filename).groups()
    return "%s%s%s" % (start, prefix, end)

def add_stories_to_designmap(dom, stories):
    """This function is outside IDMLPackage because of readonly limitations of ZipFile. """
    
    # Add stories in StoryList.
    elt = dom.xpath("/Document")[0]
    current_stories = elt.get("StoryList").split(" ")
    elt.set("StoryList", " ".join(current_stories+stories))

    # Add <idPkg:Story src="Stories/Story_[name].xml"/> elements.
    for story in stories:
        elt.append(etree.Element("{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Story", src="Stories/Story_%s.xml" % story))
