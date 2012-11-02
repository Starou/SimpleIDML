# -*- coding: utf-8 -*-

import os
import re
import new
from types import MethodType


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

    return os.path.join(dirname, "%s%s" % (result, ext))


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


class Proxy(object):
    def __init__(self, target):
        self._target = target

    def __getattr__(self, aname):
        target = self._target
        f = getattr(target, aname)
        if isinstance(f, MethodType):
            return new.instancemethod(f.im_func, self, target.__class__)
        else:
            return f
