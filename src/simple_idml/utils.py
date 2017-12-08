# -*- coding: utf-8 -*-

from builtins import chr
from builtins import str
from builtins import object
import copy
import os
import re
from lxml import etree

rx_numbered = re.compile(r"(.*?)(\d+)")
rx_xmltag_sibling_id = re.compile(r"(.*?d.*i)(\d+)")
rx_contentfile_ref = re.compile(r"^(Stories/Story_|Spreads/Spread_)(.+\.xml)$")
rx_contentfile_name = re.compile(r"^(Story_|Spread_)(.+\.xml)$")


def increment_filename(filename):
    dirname = os.path.dirname(filename)
    root, ext = os.path.splitext(os.path.basename(filename))

    result = None

    try:
        root_start, root_number_end = rx_numbered.match(root).groups()
    except AttributeError:
        pass
    else:
        result = "%s%s" % (root_start, str(int(root_number_end) + 1))

    if not result:
        root_start, root_end = root[:-1], root[-1]

        if root_end in ("z", "Z"):
            root_end = "%sa" % root_end
        else:
            root_end = chr(ord(root_end) + 1)

        result = "%s%s" % (root_start, root_end)

    return "%(dirname)s%(sep)s%(root)s%(ext)s" % {
        'dirname': dirname,
        'sep': dirname and "/" or "",
        'root': result,
        'ext': ext
    }


def prefix_content_filename(filename, prefix, mode):
    if mode == "ref":
        rx = rx_contentfile_ref
    elif mode == "filename":
        rx = rx_contentfile_name
    start, end = rx.match(filename).groups()
    return "%s%s%s" % (start, prefix, end)


def increment_xmltag_id(xmltag_id, position="sibling"):
    if position == "sibling":
        root, last_number = rx_xmltag_sibling_id.match(xmltag_id).groups()
        return "%s%d" % (root, int(last_number) + 1)
    elif position == "child":
        return "%si1" % xmltag_id


def str_is_prefixed(prefix, strng):
    if re.match("^%s.+$" % prefix, strng):
        return True
    return False


class Proxy(object):
    def __init__(self, target):
        self._target = target

    def __getattr__(self, aname):
        return getattr(self._target, aname)


def tree_to_etree_dom(tree):
    """Convert a tree in a elementTree dom instance.

    tree = {
        "tag": "Root",
        "attrs": {...},
        "content": ["foo", {subtree}, "bar", ...]
    }

    """

    def _set_node_content(node, tree):
        for c in tree["content"]:
            if isinstance(c, dict):
                child = etree.Element(c["tag"], **c.get("attrs", {}))
                _set_node_content(child, c)
                node.append(child)
            else:
                node_children = node.getchildren()
                if len(node_children) == 0:
                    node.text = "%s%s" % (node.text or "", c or "")
                else:
                    node_children[-1].tail = "%s%s" % (node_children[-1].tail or "", c or "")

    dom = etree.Element(tree["tag"], **tree.get("attrs", {}))
    _set_node_content(dom, tree)

    return dom


def etree_dom_to_tree(dom, strip_text=False):
    """A mapping representation of a etree node. """
    return {
        "tag": dom.tag,
        "attrs": copy.deepcopy(dom.attrib),
        "text": dom.text.strip() if (dom.text and strip_text) else dom.text,
        "tail": dom.tail.strip() if (dom.tail and strip_text) else dom.tail,
        "content": [etree_dom_to_tree(elt, strip_text) for elt in dom.iterchildren()]
    }


def deepcopy_element_as(element, tag):
    new_element = etree.Element(tag, **element.attrib)
    for child in element.iterchildren():
        new_element.append(copy.deepcopy(child))
    return new_element
