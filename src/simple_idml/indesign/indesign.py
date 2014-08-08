# -*- coding: utf-8 -*-

import os
import shutil
from suds.client import Client

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


def save_as(src_filename, dst_extension, indesign_server_url, indesign_server_workdir):
    """SOAP call to an InDesign Server to make the conversion. """

    javascript_basename = "save_as.jsx"
    if dst_extension in ('pdf', ):
        javascript_basename = "export.jsx"

    local_javascript_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
    remote_javascript_filename = os.path.join(indesign_server_workdir, javascript_basename)

    src_basename = os.path.basename(src_filename)
    remote_src_filename = os.path.join(indesign_server_workdir, src_basename)
    remote_dst_filename = os.path.join(indesign_server_workdir,
                                       "%s.%s" % (os.path.splitext(src_basename)[0],
                                                  dst_extension))

    cl = Client("%s/service?wsdl" % indesign_server_url)
    params = cl.factory.create("ns0:RunScriptParameters")
    params.scriptLanguage = 'javascript'
    params.scriptFile = remote_javascript_filename

    src = cl.factory.create("ns0:IDSP-ScriptArg")
    src.name = "source"
    src.value = remote_src_filename

    dst = cl.factory.create("ns0:IDSP-ScriptArg")
    dst.name = "destination"
    dst.value = remote_dst_filename

    params.scriptArgs = [src, dst]

    if dst_extension in ('pdf', ):
        fmt = cl.factory.create("ns0:IDSP-ScriptArg")
        fmt.name = "format"
        fmt.value = dst_extension
        params.scriptArgs.append(fmt)

    shutil.copy(local_javascript_filename, remote_javascript_filename)
    shutil.copy(src_filename, remote_src_filename)
    response = cl.service.RunScript(params)
    # TODO check SOAP response before going any further.

    response = open(remote_dst_filename, "rb").read()

    os.unlink(remote_javascript_filename)
    os.unlink(remote_dst_filename)
    os.unlink(remote_src_filename)

    return response
