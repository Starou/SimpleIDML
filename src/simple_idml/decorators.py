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
        if idml_package.working_copy_path is not None:
            return view_func(idml_package, *args, **kwargs)

        tmp_filename = NamedTemporaryFile().name
        idml_package.extractall(tmp_filename)
        idml_package.working_copy_path = tmp_filename
        idml_package.init_lazy_references()

        if idml_package.debug:
            # In debug it is useful to have the original trace.
            idml_package = view_func(idml_package, *args, **kwargs)
        else:
            # Catch any exception to reset working_copy_path.
            try:
                idml_package = view_func(idml_package, *args, **kwargs)
            except BaseException as err:
                idml_package.working_copy_path = None
                raise err

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
        idml_package.close()
        os.unlink(idml_package.filename)
        os.rename(tmp_package.filename, new_filename)
        shutil.rmtree(tmp_filename)
        idml_package.working_copy_path = None

        return IDMLPackage(new_filename)

    return new_func
