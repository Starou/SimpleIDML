# -*- coding: utf-8 -*-

import os
import shutil
from suds.client import Client

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


def idml_to_indd(idml_filename, indesign_server_url, indesign_server_workdir):
    """SOAP call to an InDesign Server to make the conversion. """

    javascript_basename = "idml_to_indd.jsx"
    local_javascript_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
    remote_javascript_filename = os.path.join(indesign_server_workdir, javascript_basename)

    idml_basename = os.path.basename(idml_filename)
    remote_idml_filename = os.path.join(indesign_server_workdir, idml_basename)
    remote_indd_filename = os.path.join(indesign_server_workdir,
                                        "%s.indd" % os.path.splitext(idml_basename)[0])

    cl = Client("%s/service?wsdl" % indesign_server_url)
    params = cl.factory.create("ns0:RunScriptParameters")
    params.scriptLanguage = 'javascript'
    params.scriptFile = remote_javascript_filename

    src = cl.factory.create("ns0:IDSP-ScriptArg")
    src.name = "source"
    src.value = remote_idml_filename

    dst = cl.factory.create("ns0:IDSP-ScriptArg")
    dst.name = "destination"
    dst.value = remote_indd_filename

    params.scriptArgs = [src, dst]

    shutil.copy(local_javascript_filename, remote_javascript_filename)
    shutil.copy(idml_filename, remote_idml_filename)
    response = cl.service.RunScript(params)
    # TODO check SOAP response before going any further.

    response = open(remote_indd_filename, "rb").read()

    os.unlink(remote_javascript_filename)
    os.unlink(remote_idml_filename)
    os.unlink(remote_indd_filename)

    return response
