# -*- coding: utf-8 -*-

import ftplib
import logging
import ntpath
import os
import shlex
import shutil
import socket
import subprocess
import tempfile
import uuid
import zipfile
from io import BytesIO
from simple_idml import exceptions
from simple_idml.decorators import simple_decorator
from suds.client import Client
from tempfile import mkdtemp
from xml.sax import SAXParseException

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")

JS_SAVE_AS_SCRIPT = "save_as.jsx"
JS_EXPORT_SCRIPT = "export.jsx"
JS_PACKAGE_SCRIPT = "package_to_print.jsx"
JS_SAVE_AS_SCRIPTS = [JS_SAVE_AS_SCRIPT, JS_EXPORT_SCRIPT, JS_PACKAGE_SCRIPT]


class InDesignSoapScript(object):
    def __init__(self, server_url, client_workdir, server_workdir,
                 server_path_style="posix", ftp_params=None):
        self.server_url = server_url
        self.client_workdir = client_workdir
        self.server_workdir = server_workdir
        self.ftp_params = ftp_params

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
        _copy(javascript_master_filename, self.javascript_client_copy_filename, self.ftp_params, src_open_mode="r")

    def set_params(self):
        self.params = self.client.factory.create("ns0:RunScriptParameters")
        self.params.scriptLanguage = 'javascript'
        self.params.scriptFile = self.javascript_server_copy_filename

    def runscript(self):
        self.client.service.RunScript(self.params)


class ListProfiles(InDesignSoapScript):
    javascript_basename = "list_profiles.jsx"

    def runscript(self):
        try:
            self.client.service.RunScript(self.params)
        except SAXParseException:
            pass


class CloseAllDocuments(InDesignSoapScript):
    javascript_basename = "close_all_documents.jsx"


class SaveAsBase(InDesignSoapScript):
    def __init__(self, src_filename, dst_format, js_params, server_url, client_workdir, server_workdir,
                 server_path_style="posix", ftp_params=None, clean_workdir=True, logger=None, logger_extra=None):
        super(SaveAsBase, self).__init__(server_url, client_workdir, server_workdir, server_path_style, ftp_params)
        self.js_params = js_params
        self.dst_format = dst_format
        self.clean_workdir = clean_workdir
        self.logger = logger
        self.logger_extra = logger_extra

        self.src_basename = os.path.basename(src_filename)
        src_rootname = os.path.splitext(self.src_basename)[0]
        self.set_dst_basename(src_rootname)

        self.response_client_copy_filename = os.path.join(self.client_workdir, self.dst_basename)

    def set_dst_basename(self, src_rootname):
        self.dst_basename = "%sTMP.%s" % (src_rootname, self.dst_format)

    def set_params(self):
        super(SaveAsBase, self).set_params()

        src_server_copy_filename = self.server_path_mod.join(self.server_workdir, self.src_basename)
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

    def runscript(self):
        self.logger.debug('Calling SOAP "RunScript" service... (params: %s)' % self.params, extra=self.logger_extra)
        try:
            response = self.client.service.RunScript(self.params)
        except SAXParseException, e:
            response = None
            self.logger.error('SAXParseException: %s' % e.getMessage(), extra=self.logger_extra)
        else:
            if response.errorNumber:
                self.logger.error("InDesign server was unable to save as %s.\n"
                                  "SOAP response: %s\n"
                                  "SOAP RunScript params: %s" % (self.dst_format, response, self.params),
                                  extra=self.logger_extra)
                raise exceptions.InDesignSoapException(self.params, response)

            self.logger.debug('"RunScript" successful! Response: %s' % response, extra=self.logger_extra)
        finally:
            if self.clean_workdir:
                _unlink(self.javascript_client_copy_filename, self.ftp_params)

        self.runscript_extra()

        if response:
            response = _read(self.response_client_copy_filename, self.ftp_params)
            if self.clean_workdir:
                _unlink(self.response_client_copy_filename, self.ftp_params)

        return response

    def runscript_extra(self):
        pass


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

    def runscript_extra(self):
        # Zip the tree generated in response_client_copy_filename and
        # make that variable point on that zip file.
        zip_filename = "%s.zip" % self.response_client_copy_filename
        _zip_dir(self.response_client_copy_filename, zip_filename, self.ftp_params)
        self.response_client_copy_filename = zip_filename


@simple_decorator
def use_dedicated_working_directory(view_func):
    def new_func(src_filename, dst_formats_params, indesign_server_url, indesign_client_workdir,
                 indesign_server_workdir, indesign_server_path_style="posix",
                 clean_workdir=True, ftp_params=None, logger=None, logger_extra=None):

        server_path_mod = os.path
        if indesign_server_path_style == "windows":
            server_path_mod = ntpath

        # Create a unique sub-directory.
        working_dir = _mkdir_unique(indesign_client_workdir, ftp_params)

        # update the *_workdir parameters with the new working dir value.
        indesign_client_workdir = working_dir
        indesign_server_workdir = server_path_mod.join(indesign_server_workdir, os.path.basename(working_dir))

        try:
            response = view_func(src_filename, dst_formats_params, indesign_server_url,
                                 indesign_client_workdir, indesign_server_workdir,
                                 indesign_server_path_style, clean_workdir, ftp_params,
                                 logger, logger_extra)
        except BaseException, e:
            raise e
        finally:
            if clean_workdir:
                _rmtree(working_dir, ftp_params)
        return response
    return new_func


@use_dedicated_working_directory
def save_as(src_filename, dst_formats_params, indesign_server_url, indesign_client_workdir,
            indesign_server_workdir, indesign_server_path_style="posix",
            clean_workdir=True, ftp_params=None, logger=None, logger_extra=None):
    """SOAP call to an InDesign Server to make one or more conversions. """

    if not logger:
        logger = logging.getLogger('simpleidml.indesign')
        logger.addHandler(logging.NullHandler())
    logger_extra = logger_extra or {}

    def _save_as(dst_format_params):
        """
        o *_client_copy_filename : path/to/file as seen by the SOAP client.
        o *_server_copy_filename : localized/path/to/file as seen by the InDesign Server.
        """
        dst_format = dst_format_params["fmt"]
        js_params = dst_format_params.get("params", {})

        if dst_format in ('idml', 'pdf', 'jpeg'):
            klass = Export
        elif dst_format == 'zip':
            klass = PackageForPrint
        else:
            klass = SaveAs

        script = klass(src_filename, dst_format, js_params, indesign_server_url, indesign_client_workdir,
                       indesign_server_workdir, indesign_server_path_style, ftp_params, clean_workdir,
                       logger, logger_extra)

        return script.execute()

    src_basename = os.path.basename(src_filename)
    src_client_copy_filename = os.path.join(indesign_client_workdir, src_basename)
    _copy(src_filename, src_client_copy_filename, ftp_params)

    cl = Client("%s/service?wsdl" % indesign_server_url)
    cl.set_options(location=indesign_server_url, timeout=90)

    responses = map(lambda fmt: _save_as(fmt), dst_formats_params)
    if clean_workdir:
        _unlink(src_client_copy_filename, ftp_params)

    return responses


def _copy(src_filename, dst_filename, ftp_params=None, src_open_mode="rb"):
    if not ftp_params:
        shutil.copy(src_filename, dst_filename)
        return

    with open(src_filename, src_open_mode) as f:
        ftp = get_ftp(ftp_params)
        command = 'STOR %s' % dst_filename
        try:
            if "b" in src_open_mode:
                ftp.storbinary(command, f)
            else:
                ftp.storlines(command, f)
        except BaseException, e:
            print "Cannot STOR %s" % dst_filename
            close_ftp_conn(ftp, ftp_params)
            raise e

        close_ftp_conn(ftp, ftp_params)


def _unlink(filename, ftp_params=None):
    if not ftp_params:
        os.unlink(filename)
        return
    ftp = get_ftp(ftp_params)
    ftp.delete(filename)
    close_ftp_conn(ftp, ftp_params)


def _rmtree(tree, ftp_params=None):
    if not ftp_params:
        shutil.rmtree(tree)
        return
    ftp = get_ftp(ftp_params)
    rmtree_ftp(ftp, tree)
    close_ftp_conn(ftp, ftp_params)


def _read(filename, ftp_params=None):
    response = ""

    if not ftp_params:
        with open(filename, "rb") as f:
            response = f.read()
    else:
        with BytesIO() as r:
            ftp = get_ftp(ftp_params)
            ftp.retrbinary('RETR %s' % filename, r.write)
            close_ftp_conn(ftp, ftp_params)
            r.seek(0)
            response = r.read()

    return response


def _zip_dir(dirname, zip_filename, ftp_params=None):
    if ftp_params:
        # Work locally in a temporary directory.
        # and then upload the zip to the ftp.
        tmp_dirname = mkdtemp()
        tmp_zip_filename = os.path.join(tmp_dirname, os.path.basename(zip_filename))

        cmd = 'wget -r %(no_passive)s --ftp-user="%(user)s" --ftp-password="%(passwd)s" ftp://%(url)s/%(dirname)s -P %(dst)s -nH -nv' % {
            'user': ftp_params['auth'][1],
            'passwd': ftp_params['auth'][2],
            'url': ftp_params['auth'][0],
            'no_passive': ftp_params['passive'] and "" or "--no-passive-ftp",
            'dirname': dirname,
            'dst': tmp_dirname
        }
        p = subprocess.Popen(shlex.split(cmd))
        p.wait()

        zip_tree(os.path.join(tmp_dirname, dirname), tmp_zip_filename)
        _copy(tmp_zip_filename, zip_filename, ftp_params)
        shutil.rmtree(tmp_dirname)
        _rmtree(dirname, ftp_params)
    else:
        zip_tree(dirname, zip_filename)
        shutil.rmtree(dirname)


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


# https://gist.github.com/Starou/beb8bde114bf7a20cf80
def rmtree_ftp(ftp, path):
    """Recursively delete a directory tree on a remote server."""
    wd = ftp.pwd()

    try:
        names = ftp.nlst(path)
    except ftplib.all_errors as e:
        # some FTP servers complain when you try and list non-existent paths
        #_log.debug('FtpRmTree: Could not remove {0}: {1}'.format(path, e))
        return

    for name in names:
        if os.path.split(name)[1] in ('.', '..'):
            continue

        try:
            ftp.cwd(name)  # if we can cwd to it, it's a folder
            ftp.cwd(wd)  # don't try a nuke a folder we're in
            rmtree_ftp(ftp, name)
        except ftplib.all_errors:
            ftp.delete(name)

    try:
        ftp.rmd(path)
    except ftplib.all_errors as e:
        raise e


def _mkdir_unique(dir, ftp_params=None):
    if not ftp_params:
        unique_path = tempfile.mkdtemp(dir=dir)
    else:
        unique_path = os.path.join(dir, uuid.uuid1().hex)
        ftp = get_ftp(ftp_params)
        ftp.mkd(unique_path)
        close_ftp_conn(ftp, ftp_params)
    return unique_path


def close_ftp_conn(ftp, ftp_params=None):
    """ Go figure. For some reason ftp.quit() may hangs forever.
    Try not to be polite in that case. """
    if ftp_params and (ftp_params.get('polite', True) is False):
        ftp.close()
    else:
        ftp.quit()


def get_ftp(ftp_params):
    ftp = ftplib.FTP(*ftp_params["auth"])
    ftp.set_pasv(ftp_params["passive"])

    #https://bbs.archlinux.org/viewtopic.php?id=134529
    #https://github.com/keepitsimple/pyFTPclient/blob/master/pyftpclient.py
    if ftp_params.get('keepalive', False) is True:
        ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    if 'keepalive_interval' in ftp_params and hasattr(socket, "TCP_KEEPINTVL"):
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL,
                            ftp_params['keepalive_interval'])
    if 'keepalive_idle' in ftp_params and hasattr(socket, "TCP_KEEPIDLE"):
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE,
                            ftp_params['keepalive_idle'])

    return ftp
