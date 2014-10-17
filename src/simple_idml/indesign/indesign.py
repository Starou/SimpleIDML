# -*- coding: utf-8 -*-

import ftplib
import ntpath
import os
import shlex
import shutil
import subprocess
import zipfile
from io import BytesIO
from suds.client import Client
from tempfile import mkdtemp

CURRENT_DIR = os.path.abspath(os.path.split(__file__)[0])
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "scripts")


def save_as(src_filename, dst_formats, indesign_server_url, indesign_client_workdir,
            indesign_server_workdir, indesign_server_path_style="posix",
            clean_workdir=True, ftp_params=None):
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

        _copy(javascript_master_filename, javascript_client_copy_filename, ftp_params)

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
            _zip_dir(response_client_copy_filename, zip_filename, ftp_params)
            response_client_copy_filename = zip_filename

        response = _read(response_client_copy_filename, ftp_params)

        if clean_workdir:
            _unlink(response_client_copy_filename, ftp_params)
            _unlink(javascript_client_copy_filename, ftp_params)

        return response

    ##

    src_basename = os.path.basename(src_filename)
    src_client_copy_filename = os.path.join(indesign_client_workdir, src_basename)
    src_server_copy_filename = server_path_mod.join(indesign_server_workdir, src_basename)
    _copy(src_filename, src_client_copy_filename, ftp_params)

    cl = Client("%s/service?wsdl" % indesign_server_url)
    cl.set_options(location=indesign_server_url)
    responses = map(lambda fmt: _save_as(fmt), dst_formats)

    if clean_workdir:
        _unlink(src_client_copy_filename, ftp_params)

    return responses


def _copy(src_filename, dst_filename, ftp_params=None):
    if not ftp_params:
        shutil.copy(src_filename, dst_filename)
        return
    with open(src_filename, "rb") as f:
        ftp = ftplib.FTP(*ftp_params["auth"])
        ftp.set_pasv(ftp_params["passive"])
        try:
            ftp.storbinary('STOR %s' % dst_filename, f)
        except BaseException, e:
            print "Cannot STOR %s" % dst_filename
            ftp.quit()
            raise e

        ftp.quit()


def _unlink(filename, ftp_params=None):
    if not ftp_params:
        os.unlink(filename)
        return
    ftp = ftplib.FTP(*ftp_params["auth"])
    ftp.set_pasv(ftp_params["passive"])
    ftp.delete(filename)
    ftp.quit()


def _rmtree(tree, ftp_params=None):
    if not ftp_params:
        shutil.rmtree(tree)
        return
    ftp = ftplib.FTP(*ftp_params["auth"])
    ftp.set_pasv(ftp_params["passive"])
    rmtree_ftp(ftp, tree)
    ftp.quit()


def _read(filename, ftp_params=None):
    response = ""

    if not ftp_params:
        with open(filename, "rb") as f:
            response = f.read()
    else:
        with BytesIO() as r:
            ftp = ftplib.FTP(*ftp_params["auth"])
            ftp.set_pasv(ftp_params["passive"])
            ftp.retrbinary('RETR %s' % filename, r.write)
            ftp.quit()
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

