# -*- coding: utf-8 -*-

import os
from simple_idml.idml import IDMLPackage


def create_idml_package_from_dir(dir_path, package_path=None):
    if os.path.exists(package_path):
        print "%s already exists." % package_path
        return None

    package = IDMLPackage(package_path, mode="w")

    for root, dirs, filenames in os.walk(dir_path):
        for filename in filenames:
            package.write(os.path.join(root, filename),
                          os.path.join(root.replace(dir_path, "."), filename))
    return package
