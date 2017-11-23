# -*- coding: utf-8 -*-

import os
from simple_idml.idml import IDMLPackage


def create_idml_package_from_dir(src_dir, destination):
    if os.path.exists(destination):
        raise IOError("%s already exists." % destination)

    package = IDMLPackage(destination, mode="w")

    for root, dirs, filenames in os.walk(src_dir):
        for filename in filenames:
            package.write(os.path.join(root, filename),
                          os.path.join(root.replace(src_dir, "."), filename))
