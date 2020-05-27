# -*- coding: utf-8 -*-

import copy
import datetime
import os
import re
from decimal import Decimal
from lxml import etree
from simple_idml import IdPkgNS, BACKINGSTORY
from simple_idml.utils import increment_xmltag_id, prefix_content_filename
from simple_idml.utils import Proxy

RECTO = "recto"
VERSO = "verso"

rx_node_name_from_xml_name = re.compile(r"[\w]+/[\w]+_([\w]+)\.xml")


class IDMLXMLFile(object):
    """Abstract class for various XML files found in IDML Packages. """
    name = None
    doctype = None
    excluded_tags_for_prefix = (
        "Document",
        "Language",
        "NumberingList",
        "NamedGrid",
        "TextVariable",
        "Section",
        "DocumentUser",
        "CrossReferenceFormat",
        "BuildingBlock",
        "IndexingSortOption",
        "ABullet",
        "Assignment",
        "XMLTag",
        "MasterSpread",
    )
    prefixable_attrs = (
        "Self",
        "XMLContent",
        "ParentStory",
        "MappedStyle",
        "AppliedCharacterStyle",
        "AppliedParagraphStyle",
        "AppliedObjectStyle",
        "NextStyle",
        "FillColor",
        "StrokeColor",
        "ItemLayer",
    )

    def __init__(self, idml_package, working_copy_path=None):
        self.idml_package = idml_package
        self.working_copy_path = working_copy_path
        self._fobj = None
        self._dom = None

    def __repr__(self):
        return "<%s object %s at %s>" % (self.__class__.__name__,
                                         self.name, hex(id(self)))

    @property
    def fobj(self):
        if self._fobj is None:
            if self.working_copy_path:
                filename = os.path.join(self.working_copy_path, self.name)
                fobj = open(filename, mode="rb+")
            else:
                fobj = self.idml_package.open(self.name, mode="r")
            self._fobj = fobj
        return self._fobj

    @property
    def dom(self):
        if self._dom is None:
            xml = self.fobj.read()
            try:
                dom = etree.fromstring(xml, parser=etree.XMLParser(huge_tree=True))
            except ValueError:
                # Python3: when the fobj come from Story.create()
                # it is strictly a textfile that cannot be implicitly
                # read as a bytestring (required by etree.fromstring()).
                dom = etree.fromstring(xml.encode('utf-8'))
            self._dom = dom
            self._fobj.close()
            self._fobj = None
        return self._dom

    def tostring(self):
        kwargs = {"xml_declaration": True,
                  "encoding": "UTF-8",
                  "standalone": True,
                  "pretty_print": True}

        if etree.LXML_VERSION < (2, 3):
            s = etree.tostring(self.dom, **kwargs)
            if self.doctype:
                lines = s.splitlines()
                lines.insert(1, self.doctype)
                s = "\n".join(line.decode("utf-8") for line in lines)
                s += "\n"
                s = s.encode("utf-8")
        else:
            kwargs["doctype"] = self.doctype
            s = etree.tostring(self.dom, **kwargs)
        return s

    def synchronize(self):
        # Explicit initialization of dom from self._fobj before reset
        # because in tostring() we get the dom from this file if None.
        self.dom
        self.fobj.close()
        self._fobj = None

        # Must instanciate with a working_copy to use this.
        fobj = open(os.path.join(self.working_copy_path, self.name), mode="wb+")
        fobj.write(self.tostring())
        fobj.close()

    def get_element_by_id(self, value, tag="XMLElement", attr="Self"):
        elem = self.dom.xpath("//%s[@%s='%s']" % (tag, attr, value))
        # etree FutureWarning when trying to simply do: elem = len(elem) and elem[0] or None
        if len(elem):
            elem = elem[0]
            if elem.tag == "XMLElement":
                elem = XMLElement(elem)
        else:
            elem = None
        return elem

    def prefix_references(self, prefix):
        """Update references inside various XML files found in an IDML package
           after a call to prefix()."""

        # <XMLElement Self="di2i3" MarkupTag="XMLTag/article" XMLContent="u102"/>
        # <[Spread|Page|...] Self="ub6" FlattenerOverride="Default"
        # <[TextFrame|...] Self="uca" ParentStory="u102" ...>
        # <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"
        #  PointSize="10" />
        for elt in self.dom.iter():
            if elt.tag in self.excluded_tags_for_prefix:
                continue
            for attr in self.prefixable_attrs:
                if elt.get(attr):
                    elt.set(attr, "%s%s" % (prefix, elt.get(attr)))

        # <idPkg:Spread src="Spreads/Spread_ub6.xml"/>
        # <idPkg:Story src="Stories/Story_u139.xml"/>
        for elt in self.dom.xpath(".//idPkg:Spread | .//idPkg:Story",
                                  namespaces={'idPkg': IdPkgNS}):
            if elt.get("src"):
                elt.set("src", prefix_content_filename(elt.get("src"), prefix, "ref"))

        # <Document xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"...
        # StoryList="ue4 u102 u11b u139 u9c"...>
        elt = self.dom.xpath("/Document")
        if elt and elt[0].get("StoryList"):
            elt[0].set("StoryList", " ".join(["%s%s" % (prefix, s)
                                              for s in elt[0].get("StoryList").split(" ")]))

    def set_element_resource_path(self, element_id, resource_path, synchronize=False):
        """ For Spread and Story subclasses only (this comment is a call for a Mixin). """
        # the element may not be an <XMLElement> (so tag="*").
        elt = self.get_element_by_id(element_id, tag="*")
        if elt is None:
            return
        link = elt.find("Link")
        if link is not None:
            link.set("LinkResourceURI", resource_path)
            if synchronize:
                self.synchronize()

    def remove_xml_element_page_items(self, element_id, synchronize=False):
        """Page items are sometimes in Stories rather in Spread. """
        elt = self.get_element_by_id(element_id)
        if elt.get("NoTextMarker"):
            elt.attrib.pop("NoTextMarker")
        if elt.get("XMLContent"):
            elt.attrib.pop("XMLContent")
        for c in elt.iterchildren():
            elt.remove(c)
        if synchronize:
            self.synchronize()


class MasterSpread(IDMLXMLFile):
    def __init__(self, idml_package, name, working_copy_path=None):
        super(MasterSpread, self).__init__(idml_package, working_copy_path)
        self.name = name


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

    def __init__(self, idml_package, name, working_copy_path=None):
        super(Spread, self).__init__(idml_package, working_copy_path)
        self.name = name
        self._pages = None
        self._node = None

    @property
    def pages(self):
        if self._pages is None:
            pages = [Page(self, node) for node in self.dom.findall("Spread/Page")]
            self._pages = pages
        return self._pages

    @property
    def node(self):
        if self._node is None:
            node = self.dom.find("Spread")
            self._node = node
        return self._node

    def add_page(self, page):
        """ Spread only manage 2 pages. """
        if self.pages:
            # the last page is also the first (and only) one here and is a verso (front).
            face_required = RECTO
            last_page = self.pages[-1]
            last_page.node.addnext(copy.deepcopy(page.node))
        else:
            face_required = VERSO
            self.node.append(copy.deepcopy(page.node))
        # TODO: attributes (layer, masterSpread, ...)
        for item in page.page_items:
            self.node.append(copy.deepcopy(item))
        self._pages = None

        # Correct the position of the new page in the Spread.
        last_page = self.pages[-1]

        # At this level, because the last_page may not be in a correct position
        # into the Spread, a call to last_page.page_items may also return
        # the page items of the other page of the Spread.
        # So we force the setting from the inserted page and use those references
        # to move the items if the face has to be changed.
        items_references = [item.get("Self") for item in page.page_items]
        last_page.page_items = [item for item in last_page.page_items
                                if item.get("Self") in items_references]
        last_page.set_face(face_required)

    def clear(self):
        items = list(self.node.items())
        self.node.clear()
        for k, v in items:
            self.node.set(k, v)

        self._pages = None

    def get_node_name_from_xml_name(self):
        return rx_node_name_from_xml_name.match(self.name).groups()[0]

    def set_layer_references(self, layer_id):
        for elt in self.dom.iter():
            if elt.get("ItemLayer"):
                elt.set("ItemLayer", layer_id)
        self.synchronize()

    def has_any_item_on_layer(self, layer_id):
        # The page Guide are not page items.
        return bool(len(self.node.xpath(".//*[not(self::Guide)][@ItemLayer='%s']" % layer_id)))

    def has_any_guide_on_layer(self, layer_id):
        return bool(len(self.node.xpath(".//Guide[@ItemLayer='%s']" % layer_id)))

    def remove_guides_on_layer(self, layer_id, synchronize=False):
        for guide in self.node.xpath(".//Guide[@ItemLayer='%s']" % layer_id):
            guide.getparent().remove(guide)
        if synchronize:
            self.synchronize()

    def remove_page_item(self, item_id, synchronize=False):
        # etree FutureWarning when trying to simply do: elt = foo() or bar().
        elt = self.get_element_by_id(item_id, tag="*")
        if elt is None:
            elt = self.get_element_by_id(item_id, tag="*", attr="ParentStory")
        elt.getparent().remove(elt)
        if synchronize:
            self.synchronize()

    def rectangle_to_textframe(self, rectangle):
        from simple_idml.utils import deepcopy_element_as
        textframe = deepcopy_element_as(rectangle, "TextFrame")
        textframe.set("ContentType", "TextType")
        textframe.set("PreviousTextFrame", "n")
        textframe.set("NextTextFrame", "n")
        # These attributes and subelements must be removed.
        del textframe.attrib["StoryTitle"]  # Suppose it is always present.
        for sub_elt_name in ("InCopyExportOption", "FrameFittingOption", "ObjectExportOption"):
            try:
                textframe.remove(textframe.find(sub_elt_name))
            # There is not such subelement.
            except TypeError:
                pass
        rectangle.addnext(textframe)
        self.node.remove(rectangle)


STORIES_DIRNAME = "Stories"


class Story(IDMLXMLFile):
    def __init__(self, idml_package, name, working_copy_path=None):
        super(Story, self).__init__(idml_package, working_copy_path)
        self.name = name
        self.node_name = "Story"
        self._node = None

    @classmethod
    def create(cls, idml_package, story_id, xml_element_id, xml_element_tag, working_copy_path):
        dirname = os.path.join(working_copy_path, STORIES_DIRNAME)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        story_name = "%s/Story_%s.xml" % (STORIES_DIRNAME, story_id)
        story = Story(idml_package, story_name, working_copy_path)

        # Difficult to do it in .fobj() because we don't always need
        # to create a unexisting file.
        filename = os.path.join(working_copy_path, story_name)
        story._fobj = open(filename, mode="w+")
        story.fobj.write(
            f"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
   <idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">
     <Story Self="{story_id}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">
       <StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>
       <InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>
       <XMLElement Self="{xml_element_id}" MarkupTag="XMLTag/{xml_element_tag}" XMLContent="{story_id}" />
     </Story>
</idPkg:Story>
""")

        story.fobj.close()
        story._fobj = None
        return story

    @property
    def node(self):
        if self._node is None:
            node = self.dom.find(self.node_name)
            self._node = node
        return self._node

    def set_element_attributes(self, element_id, attrs):
        element = self.get_element_by_id(element_id)
        element.set_attributes(attrs)

    def set_element_content(self, element_id, content):
        self.clear_element_content(element_id)
        xml_element = self.get_element_by_id(element_id)
        xml_element.set_content(content)
        self._fix_siblings_style(xml_element)

    def _fix_siblings_style(self, xml_element):
        """Fix ticket #11 when importing XML."""
        # Get the sibling elts that need to be styled.
        siblings = []
        for elt in xml_element.itersiblings():
            if elt.tag not in ["Content", "Br"]:
                break
            siblings.append(elt)

        if not len(siblings):
            return

        # The parent style is locally applied.
        local_style = xml_element.clone_style_range()
        for sibling in siblings:
            local_style.append(sibling)
        xml_element.addnext(local_style)

    def clear_element_content(self, element_id):
        element = self.get_element_by_id(element_id)
        # We remove all `CharacterStyleRange' containers except the first.
        # FIXME: This should handle ./ParagraphStyleRange/CharacterStyleRange too.
        children = element.xpath("./CharacterStyleRange")[1:]
        for c in children:
            element.remove(c)
        for content_node in self.get_element_content_nodes(element):
            content_node.text = ""

    def get_element_content_nodes(self, element):
        return element.xpath(("./ParagraphStyleRange/CharacterStyleRange/Content | "
                              "./CharacterStyleRange/Content | "
                              "./XMLElement/CharacterStyleRange/Content | "
                              "./Content"))

    def get_element_content_and_xmlelement_nodes(self, element):
        return element.xpath(("./ParagraphStyleRange/CharacterStyleRange/Content | "
                              "./CharacterStyleRange/Content | "
                              "./ParagraphStyleRange/CharacterStyleRange/XMLElement | "
                              "./CharacterStyleRange/XMLElement | "
                              "./ParagraphStyleRange/XMLElement | "
                              "./XMLElement | "
                              "./Content"))

    def set_element_id(self, element):
        ref_element = [e for e in element.itersiblings(tag="XMLElement", preceding=True)]
        if ref_element:
            ref_element = ref_element[0]
            position = "sibling"
        else:
            ref_element = [e for e in element.iterancestors(tag="XMLElement")]
            if ref_element:
                ref_element = ref_element[0]
            else:
                raise NotImplementedError
            position = "child"
        element.set("Self", increment_xmltag_id(ref_element.get("Self"), position))

    def remove_element(self, element_id, synchronize=False):
        elt = self.get_element_by_id(element_id).element
        elt.getparent().remove(elt)
        if synchronize:
            self.synchronize()

    def remove_children(self, element_id, synchronize=False):
        elt = self.get_element_by_id(element_id).element
        for child in elt.iterchildren():
            elt.remove(child)
        if synchronize:
            self.synchronize()

    def add_element(self, element_destination_id, element):
        node = self.get_element_by_id(element_destination_id)
        node.append(element)
        self.set_element_id(element)

    def add_content_to_element(self, element_id, content, parent=None):
        element = self.get_element_by_id(element_id)
        xml_element = XMLElement(element=element)
        xml_element.add_content(content, parent)

    def add_note(self, element_id, note, author, when=None):
        element = self.get_element_by_id(element_id)
        when = when or datetime.datetime.now().replace(microsecond=0)
        when = when.isoformat()
        note_node = etree.fromstring(f"""<Note Collapsed="false" CreationDate="{when}" ModificationDate="{when}" UserName="{author}">
                                            <ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]">
                                                <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">
                                                    <Content>{note}</Content>
                                                </CharacterStyleRange>
                                            </ParagraphStyleRange>
                                        </Note>""")
        element.insert(0, note_node)


class BackingStory(Story):
    def __init__(self, idml_package, name=BACKINGSTORY, working_copy_path=None):
        super(BackingStory, self).__init__(idml_package, name, working_copy_path)
        self.node_name = "XmlStory"

    def get_root(self):
        return XMLElement(self.dom.find("*//XMLElement"))


class Designmap(IDMLXMLFile):
    name = "designmap.xml"
    doctype = '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="7.5(142)" ?>'
    page_start_attr = "PageStart"

    def __init__(self, idml_package, working_copy_path):
        super(Designmap, self).__init__(idml_package, working_copy_path)
        self._spread_nodes = None
        self._style_mapping_node = None
        self._section_node = None
        self._layer_nodes = None
        self._active_layer = None

    @property
    def spread_nodes(self):
        if self._spread_nodes is None:
            nodes = self.dom.findall("idPkg:Spread", namespaces={'idPkg': IdPkgNS})
            self._spread_nodes = nodes
        return self._spread_nodes

    @property
    def layer_nodes(self):
        if self._layer_nodes is None:
            nodes = self.dom.findall("Layer")
            self._layer_nodes = nodes
        return self._layer_nodes

    @property
    def active_layer(self):
        if self._active_layer is None:
            active_layer = self.dom.get("ActiveLayer")
            self._active_layer = active_layer
        return self._active_layer

    @active_layer.setter
    def active_layer(self, layer):
        self.dom.set("ActiveLayer", layer)
        self._active_layer = layer

    @active_layer.deleter
    def active_layer(self):
        if self.dom.get("ActiveLayer"):
            del self.dom.attrib["ActiveLayer"]
        self._active_layer = None

    @property
    def section_node(self):
        if self._section_node is None:
            nodes = self.dom.find("Section")
            self._section_node = nodes
        return self._section_node

    @property
    def style_mapping_node(self):
        """<idPkg:Mapping src="XML/Mapping.xml"/>"""
        if self._style_mapping_node is None:
            node = self.dom.find("idPkg:Mapping", namespaces={'idPkg': IdPkgNS})
            self._style_mapping_node = node
        return self._style_mapping_node

    def set_style_mapping_node(self):
        """Do it only if self.style_mapping_node is None."""
        self.dom.append(
            etree.Element("{%s}Mapping" % IdPkgNS, src=StyleMapping.name)
        )

    def add_spread(self, spread):
        if self.spread_nodes:
            self.spread_nodes[-1].addnext(
                etree.Element("{%s}Spread" % IdPkgNS, src=spread.name)
            )

    def prefix(self, prefix):
        self.prefix_active_layer(prefix)
        self.prefix_page_start(prefix)

    def prefix_active_layer(self, prefix):
        self.active_layer = "%s%s" % (prefix, self.active_layer)

    def prefix_page_start(self, prefix):
        section_node = self.section_node
        current_page_start = section_node.get(self.page_start_attr)
        section_node.set(self.page_start_attr, "%s%s" % (prefix, current_page_start))

    def add_stories(self, stories):
        # Add stories in StoryList.
        elt = self.dom.xpath("/Document")[0]
        current_stories = elt.get("StoryList").split(" ")
        elt.set("StoryList", " ".join(current_stories + stories))

        # Add <idPkg:Story src="Stories/Story_[name].xml"/> elements.
        for story in stories:
            elt.append(etree.Element("{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}Story",
                                     src="Stories/Story_%s.xml" % story))

    def add_layer_nodes(self, layer_nodes):
        current_layers_ids = [l.get("Self") for l in self.layer_nodes]
        for layer in reversed(layer_nodes):
            # If a similar layer is already present, we do not add it.
            if layer.get("Self") not in current_layers_ids:
                self.layer_nodes[-1].addnext(copy.deepcopy(layer))
        self._layer_nodes = None

    def remove_layer(self, layer_id, synchronize=False):
        layer = self.get_element_by_id(layer_id, tag="Layer", attr="Self")
        layer.getparent().remove(layer)
        self._layer_nodes = None
        if self.active_layer == layer_id:
            del self.active_layer
            # Change the active layer if some remains.
            if len(self.layer_nodes):
                self.active_layer = self.layer_nodes[0].get("Self")
        if synchronize:
            self.synchronize()

    def suffix_layers(self, suffix):
        for layer in self.layer_nodes:
            layer.set("Name", "%s%s" % (layer.get("Name"), suffix))

    def merge_layers(self, with_name=None):
        layer_0 = self.layer_nodes.pop(0)
        if with_name:
            layer_0.set("Name", with_name)
        for l in self.layer_nodes:
            l.getparent().remove(l)
        self._layer_nodes = None
        self.active_layer = layer_0.get("Self")
        self.synchronize()

    def get_layer_id_by_name(self, layer_name):
        layer_node = self.dom.xpath(".//Layer[@Name='%s']" % layer_name)[0]
        return layer_node.get("Self")

    def get_active_layer_name(self):
        layer_node = self.dom.xpath(".//Layer[@Self='%s']" % self.active_layer)[0]
        return layer_node.get("Name")


class Style(IDMLXMLFile):
    name = "Resources/Styles.xml"

    def __init__(self, idml_package, working_copy_path=None):
        super(Style, self).__init__(idml_package, working_copy_path)

    def get_style_node_by_name(self, style_name):
        return self.dom.xpath(".//CharacterStyle[@Self='%s']" % style_name)[0]

    def style_groups(self):
        """ Groups are `RootCharacterStyleGroup', `RootParagraphStyleGroup' etc. """
        return [elt for elt in self.dom.xpath("/idPkg:Styles/*", namespaces={'idPkg': IdPkgNS})
                if re.match(r"^.+Group$", elt.tag)]

    def get_root(self):
        return self.dom.xpath("/idPkg:Styles", namespaces={'idPkg': IdPkgNS})[0]


class StyleMapping(IDMLXMLFile):
    name = "XML/Mapping.xml"
    initial_dom = ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\
                   <idPkg:Mapping xmlns:idPkg=\"http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging\"\
                   DOMVersion=\"7.5\">\
                   </idPkg:Mapping>")

    def __init__(self, idml_package, working_copy_path=None):
        super(StyleMapping, self).__init__(idml_package, working_copy_path)
        self._character_style_mapping = None

    @property
    def fobj(self):
        """Overriden because it may not exists in the package. """
        try:
            super(StyleMapping, self).fobj
        except (KeyError, IOError):
            if self.working_copy_path:
                self._initialize_fobj()
        return self._fobj

    @property
    def dom(self):
        """Overriden because it may not exists in the package. """
        try:
            super(StyleMapping, self).dom
        except AttributeError:
            self._dom = etree.fromstring(self.initial_dom.encode("utf-8"))
        return self._dom

    @property
    def character_style_mapping(self):
        if self._character_style_mapping is None:
            mapping = {}
            for node in self.iter_stylenode():
                tag = node.get("MarkupTag").replace("XMLTag/", "")
                style = node.get("MappedStyle")
                mapping[tag] = style
            self._character_style_mapping = mapping
        return self._character_style_mapping

    def _initialize_fobj(self):
        filename = os.path.join(self.working_copy_path, self.name)
        fobj = open(filename, mode="w+")
        fobj.write(self.initial_dom)
        fobj.seek(0)
        self._fobj = fobj

    def iter_stylenode(self):
        for n in self.dom.xpath("//XMLImportMap"):
            yield n

    def add_stylenode(self, node):
        self.dom.append(copy.deepcopy(node))
        self._character_style_mapping = None


class Graphic(IDMLXMLFile):
    name = "Resources/Graphic.xml"


class Preferences(IDMLXMLFile):
    name = "Resources/Preferences.xml"


class Tags(IDMLXMLFile):
    name = "XML/Tags.xml"

    def tags(self):
        return self.dom.xpath("//XMLTag")

    def get_root(self):
        return self.dom.xpath("/idPkg:Tags", namespaces={'idPkg': IdPkgNS})[0]


class Fonts(IDMLXMLFile):
    name = "Resources/Fonts.xml"

    def fonts(self):
        return self.dom.xpath("//FontFamily")

    def get_root(self):
        return self.dom.xpath("/idPkg:Fonts", namespaces={'idPkg': IdPkgNS})[0]


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
        self._is_recto = None

    @property
    def page_items(self):
        if self._page_items is None:
            page_items = [i for i in self.node.itersiblings()
                          if not i.tag == "Page" and self.page_item_is_in_self(i)]
            self._page_items = page_items
        return self._page_items

    @page_items.setter
    def page_items(self, items):
        self._page_items = items

    @property
    def is_recto(self):
        if self._is_recto is None:
            is_recto = False
            if self.coordinates["x1"] >= Decimal("0"):
                is_recto = True
            self._is_recto = is_recto
        return self._is_recto

    @property
    def face(self):
        if self.is_recto:
            return RECTO
        else:
            return VERSO

    @property
    def geometric_bounds(self):
        return [Decimal(c) for c in self.node.get("GeometricBounds").split(" ")]

    @geometric_bounds.setter
    def geometric_bounds(self, matrix):
        self.node.set("GeometricBounds", " ".join([str(v) for v in matrix]))

    @property
    def item_transform(self):
        return [Decimal(c) for c in self.node.get("ItemTransform").split(" ")]

    @item_transform.setter
    def item_transform(self, matrix):
        self.node.set("ItemTransform", " ".join([str(v) for v in matrix]))

    @property
    def coordinates(self):
        if self._coordinates is None:
            geometric_bounds = self.geometric_bounds
            item_transform = self.item_transform
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

    def set_face(self, face):
        if self.face == face:
            return
        else:
            item_transform = self.item_transform
            item_transform_x_origin = item_transform[4]

            if face == RECTO:
                item_transform[4] = Decimal("0")
            elif face == VERSO:
                item_transform[4] = - self.geometric_bounds[3]

            item_transform_x = item_transform[4] - item_transform_x_origin
            self.item_transform = item_transform

            # All page items are moved according to item_transform_x.
            for item in self.page_items:
                item_transform = [Decimal(c) for c in item.get("ItemTransform").split(" ")]
                item_transform[4] = item_transform[4] + item_transform_x
                item.set("ItemTransform", " ".join([str(v) for v in item_transform]))

            self._is_recto = None
            self._coordinates = None


class XMLElement(Proxy):
    """A proxy over the etree.Element to represent XMLElement nodes in Story files. """
    def __repr__(self):
        if self.element is not None:
            return "%s {%s}" % (repr(self.element), ", ".join(["%s: %s" % (k, v) for k, v in self.element.items()]))
        else:
            return "XMLElement (no element)"

    def __init__(self, element=None, tag=None):
        if element is not None:
            self.element = element
        else:
            self.element = etree.Element("XMLElement", MarkupTag="XMLTag/%s" % tag)
        super(XMLElement, self).__init__(target=self.element)

    def add_content(self, content, parent=None, style_range_node=None):
        content_element = etree.Element("Content")
        content_element.text = content
        if style_range_node is None:
            style_range_node = parent.clone_style_range()
        style_range_node.append(content_element)
        self.element.append(style_range_node)

    def set_content(self, content):
        try:
            self.get_element_content_nodes()[0].text = content
        except IndexError:
            return
        # Ticket #8 - Fix the style locally.
        if self.get_local_character_style_range() is None and \
           self.get_super_character_style_range() is not None:
            local_style = self.clone_style_range()
            self.apply_style_locally(local_style)

    def apply_style_locally(self, style_range_node):
        """The content node of self is moved into style_range_node. """
        content_node = self.get_element_content_nodes()[0]
        style_range_node.append(content_node)
        self.append(style_range_node)

    def clone_style_range(self):
        style_node = self.get_character_style_range()
        applied_style = style_node.get("AppliedCharacterStyle")
        style_range_node = etree.Element("CharacterStyleRange", AppliedCharacterStyle=applied_style)
        properties_node = etree.SubElement(style_range_node, "Properties")

        attrs = [
            "PointSize",
            "FontStyle",
            "HorizontalScale",
            "Tracking",
            "FillColor",
            "FillTint",
            "Capitalization",
            "PointSize",
            "StrokeWeight",
            "MiterLimit",
            "RubyFontSize",
            "KentenFontSize",
            "DiacriticPosition",
            "Ligatures",
            "OTFContextualAlternate",
            "BaselineShift",
        ]

        for attr in attrs:
            if style_node.get(attr) is not None:
                style_range_node.set(attr, style_node.get(attr))

        for attr in ("Leading", "AppliedFont"):
            path = "Properties/%s" % attr
            attr_node = style_node.find(path)
            if attr_node is not None:
                properties_node.append(copy.deepcopy(attr_node))
        return style_range_node

    def get_attribute(self, name):
        attr_node = self._get_attribute_node(name)
        return (attr_node is not None and
                attr_node.get("Value") or None)

    def _get_attribute_node(self, name):
        attr_node = self.xpath("./XMLAttribute[@Name='%s']" % name)
        if len(attr_node):
            return attr_node[0]

    def get_attributes(self):
        return dict([(node.get("Name"), node.get("Value"))
                     for node in self.xpath("./XMLAttribute")])

    def set_attribute(self, name, value):
        attr_node = self._get_attribute_node(name)
        if attr_node is None:
            attr_node = etree.Element("XMLAttribute", Name=name,
                                      Self="%sXMLAttributen%s" % (self.get("Self"), name))
            self.append(attr_node)
        attr_node.set("Value", value)

    def set_attributes(self, attributes):
        for name, value in attributes.items():
            self.set_attribute(name, value)

    def get_character_style_range(self):
        """The applied style may be contained or the container. """
        node = self.get_local_character_style_range()
        if node is None:
            node = self.get_super_character_style_range()
        return node

    def get_local_character_style_range(self):
        try:
            node = self.xpath(("./ParagraphStyleRange/CharacterStyleRange | ./CharacterStyleRange"))[0]
        except (IndexError, AttributeError):
            node = None
        return node

    def get_super_character_style_range(self):
        node = self.getparent()
        if node.tag != "CharacterStyleRange":
            node = None
        return node

    # TODO: factorize with Story.get_element_content_nodes().
    def get_element_content_nodes(self):
        return self.xpath(("./ParagraphStyleRange/CharacterStyleRange/Content | "
                           "./CharacterStyleRange/Content | "
                           "./XMLElement/CharacterStyleRange/Content | "
                           "./Content"))

    def to_xml_structure_element(self):
        """Return the node as seen in the Structure panel of InDesign. """
        attrs = dict(self.attrib)
        name = attrs.pop("MarkupTag").replace("XMLTag/", "")
        return etree.Element(name, **attrs)


def get_idml_xml_file_by_name(idml_package, name, working_copy_path=None):
    kwargs = {"idml_package": idml_package, "name": name, "working_copy_path": working_copy_path}
    dirname, basename = os.path.split(name)
    if basename == "designmap.xml":
        kwargs.pop("name")
        klass = Designmap
    elif dirname == "MasterSpreads":
        klass = MasterSpread
    elif dirname == "Spreads":
        klass = Spread
    elif dirname == "Stories":
        klass = Story
    elif name == "XML/BackingStory.xml":
        kwargs.pop("name")
        klass = BackingStory
    elif name == "Resources/Fonts.xml":
        kwargs.pop("name")
        klass = Fonts
    elif name == "Resources/Graphic.xml":
        kwargs.pop("name")
        klass = Graphic
    elif name == "Resources/Preferences.xml":
        kwargs.pop("name")
        klass = Preferences
    elif name == "Resources/Styles.xml":
        kwargs.pop("name")
        klass = Style
    elif name == "XML/Tags.xml":
        kwargs.pop("name")
        klass = Tags
    elif name == "XML/Mapping.xml":
        kwargs.pop("name")
        klass = StyleMapping

    return klass(**kwargs)
