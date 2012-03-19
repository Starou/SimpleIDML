# -*- coding: utf-8 -*-

import os, shutil
import zipfile
import re
import copy

from lxml import etree
from xml.dom.minidom import parseString

from simple_idml.decorators import use_working_copy

xmltag_prefix = "XMLTag/"
rx_contentfile = re.compile(r"^(Story_|Spread_)(.+\.xml)$")
rx_contentfile2 = re.compile(r"^(Stories/Story_|Spreads/Spread_)(.+\.xml)$")

class IDMLPackage(zipfile.ZipFile):
    """An IDML file (a package) is a Zip-stored archive/UCF container. """

    def __init__(self, *args, **kwargs):
        # TODO compression = ZIP_STORED.
        zipfile.ZipFile.__init__(self, *args, **kwargs)
        self._XMLStructure = None
        self._spreads = None
        self._stories = None

    @property
    def XMLStructure(self):
        """ Discover the XML structure from the story files.
        
        Starting at BackingStory.xml where the root-element is expected (because unused).
        Read a XML document and write another one in a parallel manner.
        """

        if self._XMLStructure is None:
            backing_story = self.open("XML/BackingStory.xml", mode="r")
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
            
    @use_working_copy
    def prefix(self, prefix, working_copy_path=None):
        """Change references and filename by inserting `prefix_` everywhere. 
        
        files in ZipFile cannot be renamed or moved so we make a copy of it.
        """

        # Change the references inside the file.
        for root, dirs, filenames in os.walk(working_copy_path):
            for filename in filenames:
                if os.path.splitext(filename)[1] != ".xml":
                    continue
                filename = os.path.join(root, filename)
                xml_file = open(filename, mode="r")
                doc = XMLDocument(xml_file)
                doc.prefix_references(prefix)
                new_xml = etree.tostring(doc.dom, pretty_print=True)
                xml_file.close()

                # override.
                new_file = open(filename, mode="w+")
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
        
        self._add_spread_elements_from_idml(idml_package, at, only)
        self._add_stories_from_idml(idml_package, at, only)
        self._add_XMLElements_from_idml(idml_package, at, only)

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

        new_xml = etree.tostring(spread_dest_doc.dom, pretty_print=True)
        spread_dest.close()
        spread_dest = open(spread_dest_abs_filename, mode="w+")
        spread_dest.write(new_xml)
        spread_dest.close()

        return self

    def _add_stories_from_idml(self, idml_package, at, only):
        # BackingStory.xml ??
        # Designmap.xml
        pass

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
            if spread_doc.dom.xpath("//*[@Self='%s']"%reference):
                result = filename
            spread.close()
            if result:
                break
        return result

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


