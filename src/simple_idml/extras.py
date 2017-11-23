# -*- coding: utf-8 -*-

import os
from simple_idml.idml import IDMLPackage


def create_idml_package_from_dir(src_dir, destination):
    if not os.path.exists(src_dir):
        raise IOError("%s does not exist." % src_dir)
    if os.path.exists(destination):
        raise IOError("%s already exist." % destination)

    with IDMLPackage(destination, mode="w") as package:
        for root, dirs, filenames in os.walk(src_dir):
            for filename in filenames:
                package.write(os.path.join(root, filename),
                              os.path.join(root.replace(src_dir, "."), filename))
