# -*- coding: utf-8 -*-

import os
import shutil
from suds.client import Client

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


def save_as(src_filename, dst_formats, indesign_server_url, indesign_server_workdir):
    """SOAP call to an InDesign Server to make one or more conversions. """

    def _save_as(dst_format):
        javascript_basename = "save_as.jsx"
        if dst_format in ('idml', 'pdf', 'jpeg'):
            javascript_basename = "export.jsx"

        local_javascript_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
        remote_javascript_filename = os.path.join(indesign_server_workdir, javascript_basename)
        remote_dst_filename = os.path.join(indesign_server_workdir,
                                           "%s.%s" % (os.path.splitext(src_basename)[0],
                                                      dst_format))

        shutil.copy(local_javascript_filename, remote_javascript_filename)

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

        if dst_format in ('idml', 'pdf', 'jpeg'):
            fmt = cl.factory.create("ns0:IDSP-ScriptArg")
            fmt.name = "format"
            fmt.value = dst_format
            params.scriptArgs.append(fmt)

        response = cl.service.RunScript(params)
        response = open(remote_dst_filename, "rb").read()

        os.unlink(remote_dst_filename)
        os.unlink(remote_javascript_filename)

        return response

    src_basename = os.path.basename(src_filename)
    remote_src_filename = os.path.join(indesign_server_workdir, src_basename)
    shutil.copy(src_filename, remote_src_filename)

    cl = Client("%s/service?wsdl" % indesign_server_url)
    responses = map(lambda fmt: _save_as(fmt), dst_formats)

    os.unlink(remote_src_filename)

    return responses
