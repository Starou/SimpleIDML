# -*- coding: utf-8 -*-

import os
from simple_idml.idml import IDMLPackage


def create_idml_package_from_dir(src_dir, destination):
    if not os.path.exists(src_dir):
        raise IOError(f"{src_dir} does not exist.")
    if os.path.exists(destination):
        raise IOError(f"{destination} already exist.")

    with IDMLPackage(destination, mode="w") as package:
        for root, dirs, filenames in os.walk(src_dir):
            for filename in filenames:
                if filename in ['.DS_Store']:
                    continue
                package.write(os.path.join(root, filename),
                              os.path.join(root.replace(src_dir, "."), filename))
