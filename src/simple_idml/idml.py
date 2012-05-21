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
FONTS = "Resources/Fonts.xml"
STYLES = "Resources/Styles.xml"

IdPkgNS = "http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"

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
        self._font_families = None
        self._style_groups = None
        self._spreads = None
        self._spreads_objects = None
        self._pages = None
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
                for elt in source_node.iterchildren():
                    if not elt.tag == "XMLElement":
                        append_childs(elt, destination_node)
                    if elt.get("Self") == source_node.get("Self"):
                        continue
                    if not elt.get("MarkupTag"):
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
                    else:
                        append_childs(elt, new_destination_node)
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
    def font_families(self):
        if self._font_families is None:
            font_families_src = self.open(FONTS, mode="r")
            font_families_doc = XMLDocument(font_families_src)
            font_families = [copy.deepcopy(elt) for elt in font_families_doc.dom.xpath("//FontFamily")]
            self._font_families = font_families
            font_families_src.close()
        return self._font_families
            
    @property
    def style_groups(self):
        if self._style_groups is None:
            style_groups_src = self.open(STYLES, mode="r")
            style_groups_doc = XMLDocument(style_groups_src)
            style_groups = [copy.deepcopy(elt) for elt in style_groups_doc.dom.xpath("/idPkg:Styles/*",
                                                                                     namespaces={'idPkg':IdPkgNS})
                            if re.match(r"^.+Group$", elt.tag)]
            self._style_groups = style_groups
            style_groups_src.close()
        return self._style_groups

    @property
    def spreads(self):
        if self._spreads is None:
            spreads = [elt for elt in self.namelist() if re.match(ur"^Spreads/*", elt)]
            self._spreads = spreads
        return self._spreads

    @property
    def spreads_objects(self):
        if self._spreads_objects is None:
            spreads_objects = [Spread(self, s) for s in self.spreads]
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
        #self._add_graphic_from_idml(idml_package)
        t = self._get_item_translation_for_insert(idml_package, at, only)
        p = self._add_font_families_from_idml(idml_package)
        p = p._add_styles_from_idml(idml_package)
        p = p._add_tags_from_idml(idml_package)
        p = p._add_spread_elements_from_idml(idml_package, at, only, t)
        p = p._add_stories_from_idml(idml_package, at, only)
        p._XMLStructure = None
        return p

    @use_working_copy
    def _add_font_families_from_idml(self, idml_package, working_copy_path=None):
        # TODO test.
        # TODO Optimization. There is a linear expansion of the Fonts.xml size
        #      as packages are merged. Do something cleaver to prune or reuse
        #      fonts already here.
        fonts_abs_filename = os.path.join(working_copy_path, FONTS)
        fonts = open(fonts_abs_filename, mode="r")
        fonts_doc = XMLDocument(fonts)
        fonts_root_elt = fonts_doc.dom.xpath("/idPkg:Fonts", namespaces={'idPkg':IdPkgNS})[0]
        for font_family in idml_package.font_families:
            fonts_root_elt.append(copy.deepcopy(font_family))
            
        fonts_doc.overwrite_and_close(ref_doctype=None)
        return self

    @use_working_copy
    def _add_styles_from_idml(self, idml_package, working_copy_path=None):
        """Append styles to their groups in STYLES file. """
        styles_abs_filename = os.path.join(working_copy_path, STYLES)
        styles = open(styles_abs_filename, mode="r")
        styles_doc = XMLDocument(styles)
        styles_root_elt = styles_doc.dom.xpath("/idPkg:Styles", namespaces={'idPkg':IdPkgNS})[0]
        for group_to_insert in idml_package.style_groups:
            group_host = styles_root_elt.xpath(group_to_insert.tag)
            # Either the group exists.
            if group_host:
                for style_to_insert in group_to_insert.iterchildren():
                    group_host[0].append(copy.deepcopy(style_to_insert))
            # or not.
            else:
                styles_root_elt.append(copy.deepcopy(group_to_insert))
            
        styles_doc.overwrite_and_close(ref_doctype=None)
        return self

    def _add_graphic_from_idml(self, idml_package):
        pass

    @use_working_copy
    def _add_tags_from_idml(self, idml_package, working_copy_path=None):
        tags_abs_filename = os.path.join(working_copy_path, TAGS)
        tags = open(tags_abs_filename, mode="r")
        tags_doc = XMLDocument(tags)
        tags_root_elt = tags_doc.dom.xpath("/idPkg:Tags", namespaces={'idPkg':IdPkgNS})[0]
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
        story_src_elt = story_src_doc.dom.xpath("//XMLElement[@Self='%s']" % xml_element_src.get("Self"))[0]

        xml_element_dest = self.XMLStructure.dom.xpath(at)[0]
        story_dest_filename = self.get_story_by_xpath(at)
        story_dest_abs_filename = os.path.join(working_copy_path, story_dest_filename)
        story_dest = open(story_dest_abs_filename, mode="r")
        story_dest_doc = XMLDocument(story_dest)
        story_dest_elt = story_dest_doc.dom.xpath("//XMLElement[@Self='%s']" % xml_element_dest.get("Self"))[0]
        if story_dest_elt.get("XMLContent"):
            story_dest_elt.attrib.pop("XMLContent")
        story_dest_elt.append(copy.copy(story_src_elt))

        story_dest_doc.overwrite_and_close(ref_doctype=None)

        # Stories files are added. TODO: add only the stories required.
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

    @use_working_copy
    def add_page_from_idml(self, idml_package, page_number, at, only, working_copy_path=None):
        last_spread = self.spreads_objects[-1]
        if len(last_spread.pages) > 1:
            # TODO
            last_spread = self.add_spread()

        page = idml_package.pages[page_number-1]
        last_spread.add_page(page)
        last_spread.synchronize(working_copy_path)

        self._add_stories_from_idml(idml_package, at, only, working_copy_path=working_copy_path)
        self._add_font_families_from_idml(idml_package, working_copy_path=working_copy_path)
        self._add_styles_from_idml(idml_package, working_copy_path=working_copy_path)
        self._add_tags_from_idml(idml_package, working_copy_path=working_copy_path)
        
        return self

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
        # <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" PointSize="10"/>
        for elt in self.dom.iter():
            if elt.tag in excluded_tags_for_prefix:
                continue
            for attr in ("Self", "XMLContent", "ParentStory", "AppliedCharacterStyle"):
                if elt.get(attr):
                    #TODO prefix_element_attr(attr, prefix)
                    elt.set(attr, "%s%s" % (prefix, elt.get(attr)))

        # <idPkg:Spread src="Spreads/Spread_ub6.xml"/>
        # <idPkg:Story src="Stories/Story_u139.xml"/>
        for elt in self.dom.xpath(".//idPkg:Spread | .//idPkg:Story", namespaces={'idPkg':IdPkgNS}):
            if elt.get("src") and rx_contentfile2.match(elt.get("src")):
                elt.set("src", prefix_content_filename(elt.get("src"), prefix, rx_contentfile2))

        # <Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"... StoryList="ue4 u102 u11b u139 u9c"...>
        elt = self.dom.xpath("/Document")
        if elt and elt[0].get("StoryList"):
            elt[0].set("StoryList", " ".join(["%s%s" % (prefix, s) 
                                           for s in elt[0].get("StoryList").split(" ")]))

    # I'am not very happy with the «ref_doctype» choice. An explicit doctype looks better now. 
    def tostring(self, ref_doctype=None):
        doctype = doctypes.get(ref_doctype, None)
        kwargs = {"xml_declaration": True,
                  "encoding": "UTF-8",
                  "standalone": True,
                  "pretty_print": True}

        if etree.LXML_VERSION < (2, 3):
            s  = etree.tostring(self.dom, **kwargs)
            if doctype:
                lines = s.splitlines()
                lines.insert(1, doctype)
                s = "\n".join(line.decode("utf-8") for line in lines)
                s += "\n"
                s = s.encode("utf-8")
                
        else:
            kwargs["doctype"] = doctype
            s  = etree.tostring(self.dom, **kwargs)

        return s

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

class IDMLXMLFile(object):
    def __init__(self, idml_package):
        self.idml_package = idml_package
        self.doctype = None

    def tostring(self):
        kwargs = {"xml_declaration": True,
                  "encoding": "UTF-8",
                  "standalone": True,
                  "pretty_print": True}

        if etree.LXML_VERSION < (2, 3):
            s  = etree.tostring(self.dom, **kwargs)
            if self.doctype:
                lines = s.splitlines()
                lines.insert(1, self.doctype)
                s = "\n".join(line.decode("utf-8") for line in lines)
                s += "\n"
                s = s.encode("utf-8")
        else:
            kwargs["doctype"] = self.doctype
            s  = etree.tostring(self.dom, **kwargs)
        return s

class Spread(IDMLXMLFile):
    """ 

        Spread coordinates system
        -------------------------

                        _ -Y
       _________________|__________________
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
   -X |                 | (0,0)            | +X 
   |--|-----------------+-------------------->            
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |                 |                  |  
      |_________________|__________________|
                        |
                        ˇ +Y
    
    """


    def __init__(self, idml_package, spread_name):
        super(Spread, self).__init__(idml_package)
        self.name = spread_name
        self._fobj = None
        self._pages = None
        self._dom = None
        self._node = None

    @property
    def fobj(self):
        if self._fobj is None:
            fobj = self.idml_package.open(self.name, mode="r")
            self._fobj = fobj
        return self._fobj
            
    @property
    def pages(self):
        if self._pages is None:
            pages = [Page(self, node) for node in self.dom.findall("Spread/Page")]
            self._pages = pages
        return self._pages
            
    @property
    def dom(self):
        if self._dom is None:
            dom = etree.fromstring(self.fobj.read())
            self._dom = dom
        return self._dom

    @property
    def node(self):
        if self._node is None:
            node = self.dom.find("Spread")
            self._node = node
        return self._node

    def add_page(self, page):
        last_page = self.pages[-1]
        last_page.node.addnext(copy.deepcopy(page.node))
        # TODO: attributes (layer, masterSpread, ...)
        for item in page.page_items:
            self.node.append(copy.deepcopy(item))

    def synchronize(self, working_copy_path):
        spread_file = open(os.path.join(working_copy_path, self.name), mode="w+")
        spread_file.write(self.tostring())
        spread_file.close()
        
class Page(object):
    """ 
        Coordinate system
        -----------------

        The <Page> position in the <Spread> is expressed by 2 attributes :

            - `GeometricBounds' (y1 x1 y2 x2) where (x1, y1) is the position of the upper-left
                corner of the page in the Spread coordinates system *before* transformation
                and (x2, y2) is the position of the lower-right corner.
            - `ItemTransform' (a b c d x y) where x and y are the translation applied to the
                Page into the Spread.
    """
    
    def __init__(self, spread, node):
        self.spread = spread
        self.node = node
        self._page_items = None
        self._coordinates = None

    @property
    def page_items(self):
        if self._page_items is None:
            page_items = [i for i in self.node.itersiblings() 
                          if not i.tag == "Page" and self.page_item_is_in_self(i)]
            self._page_items = page_items
        return self._page_items

    @property
    def coordinates(self):
        if self._coordinates is None:
            geometric_bounds = [Decimal(c) for c in self.node.get("GeometricBounds").split(" ")]
            item_transform = [Decimal(c) for c in self.node.get("ItemTransform").split(" ")]
            coordinates = {
                "x1": geometric_bounds[1] + item_transform[4],
                "y1": geometric_bounds[0] + item_transform[5],
                "x2": geometric_bounds[3] + item_transform[4],
                "y2": geometric_bounds[2] + item_transform[5],
            }
            self._coordinates = coordinates
        return self._coordinates

    def page_item_is_in_self(self, page_item):
        """The rule is «If the first `PathPointType' is in the page so is the page item.» 
        
            A PathPointType is in the page if its X is in the X-axis range of the page
            because we assume that 2 pages (or more) of the same Spread are Y-aligned.
            There is not any D&D reference here.
        """

        item_transform = [Decimal(c) for c in page_item.get("ItemTransform").split(" ")]
        #TODO factoriser "Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType"
        point = page_item.xpath("Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType")[0]
        x, y = [Decimal(c) for c in point.get("Anchor").split(" ")]
        x = x + item_transform[4]
        y = y + item_transform[5]

        if x >= self.coordinates["x1"] and x <= self.coordinates["x2"]:
            return True
        else:
            return False
