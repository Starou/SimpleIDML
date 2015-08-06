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
from simple_idml.decorators import simple_decorator
from suds.client import Client
from tempfile import mkdtemp

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")

JS_SAVE_AS_SCRIPT = "save_as.jsx"
JS_EXPORT_SCRIPT = "export.jsx"
JS_PACKAGE_SCRIPT = "package_to_print.jsx"
JS_CLOSE_ALL_SCRIPT = "close_all_documents.jsx"
JS_SAVE_AS_SCRIPTS = [JS_SAVE_AS_SCRIPT, JS_EXPORT_SCRIPT, JS_PACKAGE_SCRIPT]


def close_all_documents(indesign_server_url, indesign_client_workdir, indesign_server_workdir,
                        indesign_server_path_style="posix", ftp_params=None):
    server_path_mod = os.path
    if indesign_server_path_style == "windows":
        server_path_mod = ntpath

    javascript_basename = JS_CLOSE_ALL_SCRIPT
    javascript_master_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
    javascript_client_copy_filename = os.path.join(indesign_client_workdir, javascript_basename)
    javascript_server_copy_filename = server_path_mod.join(indesign_server_workdir, javascript_basename)

    _copy(javascript_master_filename, javascript_client_copy_filename, ftp_params, src_open_mode="r")

    cl = Client("%s/service?wsdl" % indesign_server_url)
    cl.set_options(location=indesign_server_url)

    params = cl.factory.create("ns0:RunScriptParameters")
    params.scriptLanguage = 'javascript'
    params.scriptFile = javascript_server_copy_filename

    cl.service.RunScript(params)


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

        response = view_func(src_filename, dst_formats_params, indesign_server_url, indesign_client_workdir,
                             indesign_server_workdir, indesign_server_path_style, clean_workdir, ftp_params,
                             logger, logger_extra)
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

    server_path_mod = os.path
    if indesign_server_path_style == "windows":
        server_path_mod = ntpath

    def _save_as(dst_format_params):
        """
        o *_client_copy_filename : path/to/file as seen by the SOAP client.
        o *_server_copy_filename : localized/path/to/file as seen by the InDesign Server.
        """
        dst_format = dst_format_params["fmt"]
        js_params = dst_format_params.get("params", {})

        src_rootname = os.path.splitext(src_basename)[0]
        dst_basename = "%sTMP.%s" % (src_rootname, dst_format)
        javascript_basename = JS_SAVE_AS_SCRIPT
        if dst_format in ('idml', 'pdf', 'jpeg'):
            javascript_basename = JS_EXPORT_SCRIPT
        elif dst_format == 'zip':
            javascript_basename = JS_PACKAGE_SCRIPT
            dst_basename = src_rootname  # a directory.

        javascript_master_filename = os.path.join(SCRIPTS_DIR, javascript_basename)
        javascript_client_copy_filename = os.path.join(indesign_client_workdir, javascript_basename)
        response_client_copy_filename = os.path.join(indesign_client_workdir, dst_basename)

        javascript_server_copy_filename = server_path_mod.join(indesign_server_workdir, javascript_basename)
        response_server_copy_filename = server_path_mod.join(indesign_server_workdir, dst_basename)

        _copy(javascript_master_filename, javascript_client_copy_filename, ftp_params, src_open_mode="r")

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

        # Extra parameters
        extra_params = []
        for k, v in js_params.items():
            param = cl.factory.create("ns0:IDSP-ScriptArg")
            param.name = k
            param.value = v
            extra_params.append(param)
        params.scriptArgs.extend(extra_params)

        if dst_format in ('idml', 'pdf', 'jpeg'):
            fmt = cl.factory.create("ns0:IDSP-ScriptArg")
            fmt.name = "format"
            fmt.value = dst_format
            params.scriptArgs.append(fmt)

        logger.debug('Calling SOAP "RunScript" service... (params: %s)' % params, extra=logger_extra)
        response = cl.service.RunScript(params)
        logger.debug('"RunScript" successful! Response: %s' % response, extra=logger_extra)

        if dst_format == 'zip':
            # Zip the tree generated in response_client_copy_filename and
            # make that variable point on that zip file.
            zip_filename = "%s.zip" % response_client_copy_filename
            _zip_dir(response_client_copy_filename, zip_filename, ftp_params)
            response_client_copy_filename = zip_filename

        logger.debug('Reading response...')
        response = _read(response_client_copy_filename, ftp_params)
        logger.debug('Reading response done!')

        if clean_workdir:
            logger.debug('Cleaning workir...')
            _unlink(response_client_copy_filename, ftp_params)
            _unlink(javascript_client_copy_filename, ftp_params)
            logger.debug('Cleaning workir done!')

        return response

    ##

    src_basename = os.path.basename(src_filename)
    src_client_copy_filename = os.path.join(indesign_client_workdir, src_basename)
    src_server_copy_filename = server_path_mod.join(indesign_server_workdir, src_basename)
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
