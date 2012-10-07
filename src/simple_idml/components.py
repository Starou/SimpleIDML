# -*- coding: utf-8 -*-

import os
import re
import copy
from lxml import etree
from decimal import Decimal

from simple_idml import IdPkgNS, BACKINGSTORY
from simple_idml.utils import increment_xmltag_id

RECTO = "recto"
VERSO = "verso"

rx_node_name_from_xml_name = re.compile(r"[\w]+/[\w]+_([\w]+)\.xml")


class IDMLXMLFile(object):
    """Abstract class for various XML files found in IDML Packages. """
    name = None
    doctype = None

    def __init__(self, idml_package, working_copy_path=None):
        self.idml_package = idml_package
        self.working_copy_path = working_copy_path
        self._fobj = None
        self._dom = None

    @property
    def fobj(self):
        if self._fobj is None:
            if self.working_copy_path:
                fobj = open(os.path.join(self.working_copy_path, self.name),
                            mode="r+")
            else:
                fobj = self.idml_package.open(self.name, mode="r")
            self._fobj = fobj
        return self._fobj

    @property
    def dom(self):
        if self._dom is None:
            dom = etree.fromstring(self.fobj.read())
            self._dom = dom
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
        self.fobj.close()
        self._fobj = None

        # Must instanciate with a working_copy to use this.
        fobj = open(os.path.join(self.working_copy_path, self.name), mode="w+")
        fobj.write(self.tostring())
        fobj.close()

    def get_element_by_id(self, value):
        elem = self.dom.xpath("//XMLElement[@Self='%s']" % value)
        # etree FutureWarning when trying to simply do: elem = len(elem) and elem[0] or None
        if len(elem):
            elem = elem[0]
        else:
            elem = None
        return elem


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

    def __init__(self, idml_package, spread_name, working_copy_path=None):
        super(Spread, self).__init__(idml_package, working_copy_path)
        self.name = spread_name
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
        items = self.node.items()
        self.node.clear()
        for k, v in items:
            self.node.set(k, v)

        self._pages = None

    def get_node_name_from_xml_name(self):
        return rx_node_name_from_xml_name.match(self.name).groups()[0]


class Story(IDMLXMLFile):
    def __init__(self, idml_package, story_name, working_copy_path=None):
        super(Story, self).__init__(idml_package, working_copy_path)
        self.name = story_name
        self.node_name = "Story"
        self._node = None

    @property
    def node(self):
        if self._node is None:
            node = self.dom.find(self.node_name)
            self._node = node
        return self._node

    def set_element_content(self, element_id, content):
        self.clear_element_content(element_id)
        element = self.get_element_by_id(element_id)
        self.get_element_content_nodes(element)[0].text = content

    def clear_element_content(self, element_id):
        element = self.get_element_by_id(element_id)
        for content_node in self.get_element_content_nodes(element):
            content_node.text = ""

    def get_element_content_nodes(self, element):
        return element.xpath(("./ParagraphStyleRange/CharacterStyleRange/Content | \
                               ./CharacterStyleRange/Content | \
                               ./XMLElement/CharacterStyleRange/Content"))

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

    def add_element(self, element_destination_id, element):
        node = self.get_element_by_id(element_destination_id)
        node.append(element)
        self.set_element_id(element)

    def add_content_to_element(self, element_id, content):
        element = self.get_element_by_id(element_id)
        xml_element = XMLElement(element=element)
        xml_element.add_content(content)


class BackingStory(Story):
    def __init__(self, idml_package, story_name=BACKINGSTORY, working_copy_path=None):
        super(BackingStory, self).__init__(idml_package, story_name, working_copy_path)
        self.node_name = "XmlStory"


class Designmap(IDMLXMLFile):
    name = "designmap.xml"
    doctype = u'<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="7.5(142)" ?>'
    page_start_attr = "PageStart"

    def __init__(self, idml_package, working_copy_path):
        super(Designmap, self).__init__(idml_package, working_copy_path)
        self._spread_nodes = None
        self._section_node = None

    @property
    def spread_nodes(self):
        if self._spread_nodes is None:
            nodes = self.dom.findall("idPkg:Spread", namespaces={'idPkg': IdPkgNS})
            self._spread_nodes = nodes
        return self._spread_nodes

    @property
    def section_node(self):
        if self._section_node is None:
            nodes = self.dom.find("Section")
            self._section_node = nodes
        return self._section_node

    def add_spread(self, spread):
        if self.spread_nodes:
            self.spread_nodes[-1].addnext(
                etree.Element("{%s}Spread" % IdPkgNS, src=spread.name)
            )

    def prefix_page_start(self, prefix):
        section_node = self.section_node
        current_page_start = section_node.get(self.page_start_attr)
        section_node.set(self.page_start_attr, "%s%s" % (prefix, current_page_start))


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


class XMLElement(object):
    """A wrapper over the etree.Element to represent XMLElement nodes in Story files. """
    def __init__(self, element=None, tag=None):
        if element is not None:
            self.element = element
        else:
            self.element = etree.Element("XMLElement", MarkupTag="XMLTag/%s" % tag)

    def add_content(self, content, style=None):
        style = style or "$ID/[No character style]"
        style = "CharacterStyle/%s" % style
        style_element = etree.Element("CharacterStyleRange", AppliedCharacterStyle=style)
        content_element = etree.Element("Content")
        content_element.text = content
        style_element.append(content_element)
        self.element.append(style_element)
