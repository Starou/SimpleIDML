# -*- coding: utf-8 -*-

import ntpath
import os
import shutil
import zipfile
from suds.client import Client

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


def save_as(src_filename, dst_formats, indesign_server_url, indesign_client_workdir,
            indesign_server_workdir, indesign_server_path_style="posix"):
    """SOAP call to an InDesign Server to make one or more conversions. """

    server_path_mod = os.path
    if indesign_server_path_style == "windows":
        server_path_mod = ntpath

    def _save_as(dst_format):
        """
        o *_client_copy_filename : path/to/file as seen by the SOAP client.
        o *_server_copy_filename : localized/path/to/file as seen by the InDesign Server.
        """
        src_rootname = os.path.splitext(src_basename)[0]
        dst_basename = "%s.%s" % (src_rootname, dst_format)
        javascript_basename = "save_as.jsx"
        if dst_format in ('idml', 'pdf', 'jpeg'):
            javascript_basename = "export.jsx"
        elif dst_format == 'zip':
            javascript_basename = "package_to_print.jsx"
            dst_basename = src_rootname  # a directory.

        javascript_master_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
        javascript_client_copy_filename = os.path.join(indesign_client_workdir, javascript_basename)
        response_client_copy_filename = os.path.join(indesign_client_workdir, dst_basename)

        javascript_server_copy_filename = server_path_mod.join(indesign_server_workdir, javascript_basename)
        response_server_copy_filename = server_path_mod.join(indesign_server_workdir, dst_basename)

        shutil.copy(javascript_master_filename, javascript_client_copy_filename)

        params = cl.factory.create("ns0:RunScriptParameters")
        params.scriptLanguage = 'javascript'
        params.scriptFile = javascript_server_copy_filename

        src = cl.factory.create("ns0:IDSP-ScriptArg")
        src.name = "source"
        src.value = src_server_copy_filename

        dst = cl.factory.create("ns0:IDSP-ScriptArg")
        dst.name = "destination"
        dst.value = response_server_copy_filename

        params.scriptArgs = [src, dst]

        if dst_format in ('idml', 'pdf', 'jpeg'):
            fmt = cl.factory.create("ns0:IDSP-ScriptArg")
            fmt.name = "format"
            fmt.value = dst_format
            params.scriptArgs.append(fmt)

        response = cl.service.RunScript(params)

        if dst_format == 'zip':
            # Zip the tree generated in response_client_copy_filename and
            # make that variable point on that zip file.
            zip_filename = "%s.zip" % response_client_copy_filename
            zip_tree(response_client_copy_filename, zip_filename)
            shutil.rmtree(response_client_copy_filename)
            response_client_copy_filename = zip_filename

        response = open(response_client_copy_filename, "rb").read()

        os.unlink(response_client_copy_filename)
        os.unlink(javascript_client_copy_filename)

        return response

    ##

    src_basename = os.path.basename(src_filename)
    src_client_copy_filename = os.path.join(indesign_client_workdir, src_basename)
    src_server_copy_filename = server_path_mod.join(indesign_server_workdir, src_basename)
    shutil.copy(src_filename, src_client_copy_filename)

    cl = Client("%s/service?wsdl" % indesign_server_url)
    responses = map(lambda fmt: _save_as(fmt), dst_formats)

    os.unlink(src_client_copy_filename)

    return responses


def zip_tree(tree, destination):
    #http://stackoverflow.com/a/17080988/113036
    relroot = os.path.abspath(os.path.join(tree, os.pardir))
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(tree):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)
