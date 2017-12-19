# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import open
import ftplib
import os
import shlex
import shutil
import socket
import subprocess
import tempfile
import uuid
import zipfile
from io import BytesIO
from tempfile import mkdtemp


def copy(src_filename, dst_filename, ftp_params=None, src_open_mode="rb"):
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
        except BaseException as e:
            print("Cannot STOR %s" % dst_filename)
            close_ftp_conn(ftp, ftp_params)
            raise e

        close_ftp_conn(ftp, ftp_params)


def unlink(filename, ftp_params=None):
    if not ftp_params:
        os.unlink(filename)
        return
    ftp = get_ftp(ftp_params)
    ftp.delete(filename)
    close_ftp_conn(ftp, ftp_params)


def rmtree(tree, ftp_params=None):
    if not ftp_params:
        shutil.rmtree(tree)
        return
    ftp = get_ftp(ftp_params)
    rmtree_ftp(ftp, tree)
    close_ftp_conn(ftp, ftp_params)


def read(filename, ftp_params=None):
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


def zip_dir(dirname, zip_filename, ftp_params=None):
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
        copy(tmp_zip_filename, zip_filename, ftp_params)
        shutil.rmtree(tmp_dirname)
        rmtree(dirname, ftp_params)
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


def mkdir_unique(dir, ftp_params=None):
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
