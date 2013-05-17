# -*- coding: utf-8 -*-

import os
import shutil
from tempfile import NamedTemporaryFile


def simple_decorator(decorator):
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


@simple_decorator
def use_working_copy(view_func):
    def new_func(idml_package, *args, **kwargs):
        # In nested calls, we use the working_copy of the parent method.
        if "working_copy_path" in kwargs:
            return view_func(idml_package, *args, **kwargs)

        tmp_filename = NamedTemporaryFile().name
        idml_package.extractall(tmp_filename)
        idml_package.working_copy_path = tmp_filename
        idml_package.init_lazy_references()

        kwargs["working_copy_path"] = tmp_filename

        idml_package = view_func(idml_package, *args, **kwargs)

        from simple_idml.idml import IDMLPackage
        # Create a new archive from the extracted one.
        tmp_package = IDMLPackage("%s.idml" % tmp_filename, mode="w")
        for root, dirs, filenames in os.walk(tmp_filename):
            for filename in filenames:
                filename = os.path.join(root, filename)
                arcname = filename.replace(tmp_filename, "")
                tmp_package.write(filename, arcname)
        tmp_package.close()

        # swap working_copy with initial IDML Package.
        new_filename = idml_package.filename
        os.unlink(idml_package.filename)
        os.rename(tmp_package.filename, new_filename)
        shutil.rmtree(tmp_filename)

        return IDMLPackage(new_filename)

    return new_func
