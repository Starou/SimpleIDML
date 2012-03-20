# -*- coding: utf-8 -*-

import os, shutil
import zipfile
import re
import copy

from lxml import etree
from xml.dom.minidom import parseString

from simple_idml.decorators import use_working_copy

BACKINGSTORY = "XML/BackingStory.xml"
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

class IDMLPackage(zipfile.ZipFile):
    """An IDML file (a package) is a Zip-stored archive/UCF container. """

    def __init__(self, *args, **kwargs):
        kwargs["compression"] = zipfile.ZIP_STORED
        zipfile.ZipFile.__init__(self, *args, **kwargs)
        self._XMLStructure = None
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
                new_xml = etree.tostring(doc.dom, xml_declaration=True,
                                         encoding="UTF-8",
                                         standalone=True,
                                         doctype=doctypes.get(filename, ""),
                                         pretty_print=True)
                xml_file.close()

                # override.
                new_file = open(abs_filename, mode="w+")
                new_file.write(new_xml)
                new_file.close()

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
        self._add_tags_from_idml(idml_package)
        
        p = self._add_spread_elements_from_idml(idml_package, at, only)
        p = p._add_stories_from_idml(idml_package, at, only)
        #p._add_XMLElements_from_idml(idml_package, at, only)
        p._XMLStructure = None
        return p

    def _add_fonts_from_idml(self, idml_package):
        pass

    def _add_graphic_from_idml(self, idml_package):
        pass

    def _add_tags_from_idml(self, idml_package):
        pass

    @use_working_copy
    def _add_spread_elements_from_idml(self, idml_package, at, only, working_copy_path=None):
        """ Append idml_package spread elements into self.spread[0] <Spread> node. """

        # There should be only one spread in the idml_package.
        spread_src = idml_package.open(idml_package.spreads[0], mode="r")
        spread_src_doc = XMLDocument(spread_src)

        # We work in the working_copy.
        spread_dest_filename = self.get_spread_by_xpath(at)
        spread_dest_abs_filename = os.path.join(working_copy_path, spread_dest_filename)
        spread_dest = open(spread_dest_abs_filename, mode="r")
        spread_dest_doc = XMLDocument(spread_dest)
        spread_dest_elt = spread_dest_doc.dom.xpath("./Spread")[0]

        for child in spread_src_doc.dom.xpath("./Spread")[0].iterchildren():
            if child.tag in ["Page", "FlattenerPreference"]:
                continue
            child_copy = copy.deepcopy(child)
            spread_dest_elt.append(child_copy)

        new_xml = etree.tostring(spread_dest_doc.dom, xml_declaration=True, encoding="UTF-8", standalone=True, pretty_print=True)
        spread_dest.close()
        spread_dest = open(spread_dest_abs_filename, mode="w+")
        spread_dest.write(new_xml)
        spread_dest.close()

        return self

    @use_working_copy
    def _add_stories_from_idml(self, idml_package, at, only, working_copy_path=None):
        """Add all idml_package stories and insert `only' refence at `at' position in self. 
        
        What we have:
        =============
        
        o self Story file containing "at" (say /Root/article[3] or "udd") [1]:

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="udd"/> (A)
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>


        o idml_package Story containing "only" (say /Root/module[1] or "u102") [2]:
        
            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/module" XMLContent="u102"/> (B)
            </XMLElement>

        What we get:
        ============

        o A glue-Story file (Story/Story_glue.xml) is created to link those elements [3]:

            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
                <Story Self="glue" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
                    <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="udd">        (A)
                        <XMLElement Self="di2i5i1" MarkupTag="XMLTag/module" XMLContent="u102"/> (B)
                    </XMLElement>
                </Story>
            </idPkg:Story>

        o the file in [1] is repaired to point to the glue-Story [4]:

            <XMLElement Self="di2" MarkupTag="XMLTag/Root">
                <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
                <XMLElement Self="di2i4" MarkupTag="XMLTag/article" XMLContent="udb"/>
                <XMLElement Self="di2i5" MarkupTag="XMLTag/article" XMLContent="glue"/> (A)
                <XMLElement Self="di2i6" MarkupTag="XMLTag/advertise" XMLContent="udf"/>
            </XMLElement>

        o the "Self" attributes of idml_package Story files are altered to fit in their new environment [5]:
        
        TODO 

        o The designmap.xml file is updated [6].
        
        """

        # get (A).
        xml_element_dest = self.XMLStructure.dom.xpath(at)[0]
        story_dest_filename = self.get_story_by_xpath(at)
        story_dest_abs_filename = os.path.join(working_copy_path, story_dest_filename)
        story_dest = open(story_dest_abs_filename, mode="r")
        story_dest_doc = XMLDocument(story_dest)
        story_dest_elt = story_dest_doc.dom.xpath("//XMLElement[@XMLContent='%s']" % xml_element_dest.get("XMLContent"))[0]

        # Init Glue-Story XML and copy (A) in it.
        glue_dom = etree.XML(create_story_xml("glue"))
        glue_dom_elt = glue_dom.xpath("//Story")[0]
        glue_dom_elt.append(copy.copy(story_dest_elt))

        # Get (B) and copy it in glue XML as (A) child.
        xml_element_src = idml_package.XMLStructure.dom.xpath(only)[0]
        story_src_filename = idml_package.get_story_by_xpath(only)
        story_src = idml_package.open(story_src_filename, mode="r")
        story_src_doc = XMLDocument(story_src)
        story_src_elt = story_src_doc.dom.xpath("//XMLElement[@XMLContent='%s']" % xml_element_src.get("XMLContent"))[0]
        glue_dom_elt = glue_dom.xpath("//Story/XMLElement[1]")[0]
        glue_dom_elt.append(copy.copy(story_src_elt))

        # [4]: (A) is now referencing the Glue Story file.
        story_dest_elt.set("XMLContent", "glue")
        new_xml = etree.tostring(story_dest_doc.dom, xml_declaration=True, encoding="UTF-8", standalone=True, pretty_print=True)
        story_dest.close()
        story_dest = open(story_dest_abs_filename, mode="w+")
        story_dest.write(new_xml)
        story_dest.close()

        # Save() Glue-Story file in the working_copy.
        glue_story_filename = os.path.join(working_copy_path, "Stories", "Story_glue.xml")
        glue_story = open(glue_story_filename, mode="w+")
        glue_story.write(etree.tostring(glue_dom, xml_declaration=True, encoding="UTF-8", standalone=True, pretty_print=True))
        glue_story.close()

        story_src.close()

        # Stories files are added.
        for filename in idml_package.stories:
            story_cp = open(os.path.join(working_copy_path, filename), mode="w+")
            story_cp.write(idml_package.open(filename, mode="r").read())
            story_cp.close()

        # Update designmap.xml.
        designmap_abs_filename = os.path.join(working_copy_path, "designmap.xml")
        designmap = open(designmap_abs_filename, mode="r")
        designmap_doc = XMLDocument(designmap)

        add_stories_to_designmap(designmap_doc.dom, ["glue"]+idml_package.story_ids)

        designmap.close()
        designmap = open(designmap_abs_filename, mode="w+")
        designmap.write(etree.tostring(designmap_doc.dom, xml_declaration=True, encoding="UTF-8", standalone=True, pretty_print=True))
        designmap.close()

        return self
        # BackingStory.xml ??

    def _add_XMLElements_from_idml(self, idml_package, at, only):
        only = copy.deepcopy(idml_package.XMLStructure.dom.xpath(only)[0])
        self.XMLStructure.dom.xpath(at)[0].append(only)

    def get_spread_by_xpath(self, xpath):
        """ Search for the spread file having the element identified by the XMLContent attribute
        of the XMLElement pointed by xpath value."""

        #TODO: caching.
        result = None
        reference = self.XMLStructure.dom.xpath(xpath)[0].get("XMLContent")
        for filename in self.spreads:
            spread = self.open(filename, mode="r")
            spread_doc = XMLDocument(spread)
            if spread_doc.dom.xpath("//*[@Self='%s']" % reference):
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


    # TODO: rename in get_story_filename_by_reference ?
    def get_story_filename_by_xml_value(self, xml_value):
        return u"Stories/Story_%s.xml" % xml_value


class XMLDocument(object):
    """A Document wrapper to fit IDML XML Structure."""
    
    def __init__(self, xml_file=None, XMLElement=None):
        if xml_file:
            self.dom = etree.fromstring(xml_file.read())
        elif XMLElement is not None:
            self.dom = XMLElementToElement(XMLElement)
        else:
            raise BaseException, "You must provide either a xml file or a name."

    def getElementById(self, id):
        return self.dom.find("*/XMLElement[@Self='%s']" % id)

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


def create_story_xml(story_name):
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
        <Story Self="%s" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
        </Story>
    </idPkg:Story>""" % story_name

def add_stories_to_designmap(dom, stories):
    """This function is outside IDMLPackage because of readonly limitations of ZipFile. """
    
    # Add stories in StoryList.
    elt = dom.xpath("/Document")[0]
    current_stories = elt.get("StoryList").split(" ")
    elt.set("StoryList", " ".join(current_stories+stories))

    # Add <idPkg:Story src="Stories/Story_[name].xml"/> elements.
    for story in stories:
        elt.append(etree.Element("{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Story", src="Stories/story_%s.xml" % story))
