# -*- coding: utf-8 -*-

from builtins import object
import logging
import ntpath
import os
from simple_idml import exceptions
from simple_idml import ftp
from simple_idml.decorators import simple_decorator
from suds.client import Client
from xml.sax import SAXParseException
from zipfile import ZipFile

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


class InDesignSoapScript(object):
    def __init__(self, server_url, client_workdir, server_workdir, server_path_style="posix",
                 ftp_params=None, clean_workdir=True, logger=None, logger_extra=None):
        self.server_url = server_url
        self.client_workdir = client_workdir
        self.server_workdir = server_workdir
        self.ftp_params = ftp_params
        self.clean_workdir = clean_workdir

        if not logger:
            logger = logging.getLogger('simpleidml.indesign')
            logger.addHandler(logging.NullHandler())
        self.logger = logger
        self.logger_extra = logger_extra or {}

        self.server_path_mod = ntpath if server_path_style == "windows" else os.path

    def execute(self):
        self.copy_script_on_working_directory()

        self.client = Client("%s/service?wsdl" % self.server_url)
        self.client.set_options(location=self.server_url)
        self.set_params()
        return self.runscript()

    def copy_script_on_working_directory(self):
        javascript_master_filename = os.path.join(SCRIPTS_DIR, self.javascript_basename)
        self.javascript_client_copy_filename = os.path.join(self.client_workdir, self.javascript_basename)
        self.javascript_server_copy_filename = self.server_path_mod.join(self.server_workdir,
                                                                         self.javascript_basename)
        ftp.copy(javascript_master_filename, self.javascript_client_copy_filename,
                 self.ftp_params, src_open_mode="rb")

    def set_params(self):
        self.params = self.client.factory.create("ns0:RunScriptParameters")
        self.params.scriptLanguage = 'javascript'
        self.params.scriptFile = self.javascript_server_copy_filename

    def runscript(self):
        self.logger.debug('Calling SOAP "RunScript" service (params: %s)' % self.params, extra=self.logger_extra)
        try:
            response = self.client.service.RunScript(self.params)
        except SAXParseException as e:
            response = None
            self.logger.error('SAXParseException: %s' % e.getMessage(), extra=self.logger_extra)
        else:
            if response.errorNumber:
                self.logger.error("SOAP response: %s\nSOAP RunScript params: %s" % (response, self.params),
                                  extra=self.logger_extra)
                raise exceptions.InDesignSoapException(self.params, response)

            self.logger.debug('"RunScript" successful! Response: %s' % response, extra=self.logger_extra)
        finally:
            if self.clean_workdir:
                ftp.unlink(self.javascript_client_copy_filename, self.ftp_params)

        response = self.runscript_extra(response)
        return response

    def runscript_extra(self, response):
        return response


class ListProfiles(InDesignSoapScript):
    javascript_basename = "list_profiles.jsx"


class CloseAllDocuments(InDesignSoapScript):
    javascript_basename = "close_all_documents.jsx"


class SaveAsBase(InDesignSoapScript):
    def __init__(self, src_name, dst_format, js_params, server_url, client_workdir, server_workdir,
                 server_path_style="posix", ftp_params=None, clean_workdir=True, logger=None, logger_extra=None):
        super(SaveAsBase, self).__init__(server_url, client_workdir, server_workdir, server_path_style,
                                         ftp_params, clean_workdir, logger, logger_extra)
        self.js_params = js_params
        self.dst_format = dst_format

        self.src_name = src_name
        src_rootname = os.path.splitext(self.src_name)[0]
        self.set_dst_basename(src_rootname)

        self.response_client_copy_filename = os.path.join(self.client_workdir, self.dst_basename)

    def set_dst_basename(self, src_rootname):
        self.dst_basename = "%sTMP.%s" % (src_rootname, self.dst_format)

    def set_params(self):
        super(SaveAsBase, self).set_params()

        src_server_copy_filename = self.server_path_mod.join(self.server_workdir, self.src_name)
        src = self.client.factory.create("ns0:IDSP-ScriptArg")
        src.name = "source"
        src.value = src_server_copy_filename

        response_server_copy_filename = self.server_path_mod.join(self.server_workdir, self.dst_basename)
        dst = self.client.factory.create("ns0:IDSP-ScriptArg")
        dst.name = "destination"
        dst.value = response_server_copy_filename

        self.params.scriptArgs = [src, dst]

        # Extra parameters
        extra_params = []
        for k, v in self.js_params.items():
            param = self.client.factory.create("ns0:IDSP-ScriptArg")
            param.name = k
            param.value = v
            extra_params.append(param)
        self.params.scriptArgs.extend(extra_params)

    def runscript_extra(self, response):
        response = super(SaveAsBase, self).runscript_extra(response)
        if response:
            response = ftp.read(self.response_client_copy_filename, self.ftp_params)
            if self.clean_workdir:
                ftp.unlink(self.response_client_copy_filename, self.ftp_params)
        return response


class SaveAs(SaveAsBase):
    javascript_basename = "save_as.jsx"


class Export(SaveAsBase):
    javascript_basename = "export.jsx"

    def set_params(self):
        super(Export, self).set_params()
        fmt = self.client.factory.create("ns0:IDSP-ScriptArg")
        fmt.name = "format"
        fmt.value = self.dst_format
        self.params.scriptArgs.append(fmt)


class PackageForPrint(SaveAsBase):
    javascript_basename = "package_to_print.jsx"

    def set_dst_basename(self, src_rootname):
        self.dst_basename = src_rootname  # A directory

    def runscript_extra(self, response):
        # Zip the tree generated in response_client_copy_filename and
        # make that variable point on that zip file.
        zip_filename = "%s.zip" % self.response_client_copy_filename
        ftp.zip_dir(self.response_client_copy_filename, zip_filename, self.ftp_params)
        self.response_client_copy_filename = zip_filename

        return super(PackageForPrint, self).runscript_extra(response)


@simple_decorator
def use_dedicated_working_directory(view_func):
    def new_func(src_path, formats_options, indesign_server_url, indesign_client_workdir,
                 indesign_server_workdir, indesign_server_path_style="posix",
                 clean_workdir=True, ftp_params=None, logger=None, logger_extra=None):

        server_path_mod = os.path
        if indesign_server_path_style == "windows":
            server_path_mod = ntpath

        # Create a unique sub-directory.
        working_dir = ftp.mkdir_unique(indesign_client_workdir, ftp_params)

        # update the *_workdir parameters with the new working dir value.
        indesign_client_workdir = working_dir
        indesign_server_workdir = server_path_mod.join(indesign_server_workdir, os.path.basename(working_dir))

        try:
            response = view_func(src_path, formats_options, indesign_server_url,
                                 indesign_client_workdir, indesign_server_workdir,
                                 indesign_server_path_style, clean_workdir, ftp_params,
                                 logger, logger_extra)
        except BaseException as e:
            raise e
        finally:
            if clean_workdir:
                ftp.rmtree(working_dir, ftp_params)
        return response
    return new_func


@use_dedicated_working_directory
def save_as(src_path, formats_options, indesign_server_url,
            indesign_client_workdir, indesign_server_workdir,
            indesign_server_path_style="posix", clean_workdir=True,
            ftp_params=None, logger=None, logger_extra=None):
    """SOAP call to an InDesign Server to convert an InDesign file. """

    if not logger:
        logger = logging.getLogger('simpleidml.indesign')
        logger.addHandler(logging.NullHandler())
    logger_extra = logger_extra or {}

    src_name = os.path.basename(src_path)
    src_client_copy_filename = os.path.join(indesign_client_workdir, src_name)
    ftp.copy(src_path, src_client_copy_filename, ftp_params)

    responses = [
        _save_as(src_name, format_options, indesign_server_url,
                 indesign_client_workdir, indesign_server_workdir,
                 indesign_server_path_style, ftp_params, clean_workdir,
                 logger, logger_extra) for format_options in formats_options
    ]

    if clean_workdir:
        ftp.unlink(src_client_copy_filename, ftp_params)

    return responses


@use_dedicated_working_directory
def export_package_as(package_path, formats_options, indesign_server_url,
                      indesign_client_workdir, indesign_server_workdir,
                      indesign_server_path_style="posix", clean_workdir=True,
                      ftp_params=None, logger=None, logger_extra=None):
    """SOAP call to an InDesign Server to export a zipped package. """

    if not logger:
        logger = logging.getLogger('simpleidml.indesign')
        logger.addHandler(logging.NullHandler())
    logger_extra = logger_extra or {}

    # Search the relative path of the INDD file in the archive before unpacking.
    src_relpath = None
    with ZipFile(package_path) as package_zip:
        for name in package_zip.namelist():
            if name.startswith('.'):
                continue
            if name.endswith('.indd'):
                src_relpath = name
                break
    if not src_relpath:
        raise BaseException("No INDD file in the archive.")

    ftp.unpack_archive(package_path, ftp_params, indesign_client_workdir)

    # Add the directory that contains the indd to workdir paths.
    dirname, indd_name = os.path.split(src_relpath)
    indesign_client_workdir = os.path.join(indesign_client_workdir, dirname)
    server_path_mod = os.path
    if indesign_server_path_style == "windows":
        server_path_mod = ntpath
    indesign_server_workdir = server_path_mod.join(indesign_server_workdir, dirname)

    # Call the SOAP service.
    return [
        _save_as(indd_name, format_options, indesign_server_url,
                 indesign_client_workdir, indesign_server_workdir,
                 indesign_server_path_style, ftp_params, clean_workdir,
                 logger, logger_extra) for format_options in formats_options
    ]


def _save_as(src_name, format_options, indesign_server_url, indesign_client_workdir,
             indesign_server_workdir, indesign_server_path_style, ftp_params, clean_workdir,
             logger, logger_extra):
    fmt = format_options["fmt"]
    js_params = format_options.get("params", {})

    if fmt in ('idml', 'pdf', 'jpeg'):
        klass = Export
    elif fmt == 'zip':
        klass = PackageForPrint
    else:
        klass = SaveAs

    script = klass(src_name, fmt, js_params, indesign_server_url, indesign_client_workdir,
                   indesign_server_workdir, indesign_server_path_style, ftp_params, clean_workdir,
                   logger, logger_extra)

    return script.execute()
