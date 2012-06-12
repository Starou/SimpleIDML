# -*- coding: utf-8 -*-

import os, re

rx_numbered = re.compile(r"(.*?)(\d+)")


def increment_filename(filename):
    dirname = os.path.dirname(filename)
    root, ext = os.path.splitext(os.path.basename(filename))

    result = None

    try:
        root_start, root_number_end = rx_numbered.match(root).groups()
    except AttributeError:
        pass
    else:
        result = "%s%s" % (root_start, str(int(root_number_end)+1))

    if not result:
        root_start, root_end = root[:-1], root[-1]

        if root_end in ("z", "Z"):
            root_end = "%sa" % root_end
        else:
            root_end = chr(ord(root_end)+1)

        result = "%s%s" % (root_start, root_end)

    return os.path.join(dirname, "%s%s" % (result, ext))
