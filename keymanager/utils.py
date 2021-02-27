from keymanager import _HEAD_MARKER_BYTE_SIZE
import appdirs
import os
import zipfile


def write_file(path: str, bs: bytes):
    with open(path, 'wb') as f:
        f.write(bs)


def read_file(path: str):
    with open(path, 'rb') as f:
        return f.read()


def read_header(path: str):
    with open(path, 'rb') as f:
        return f.read(_HEAD_MARKER_BYTE_SIZE)


def get_user_data_dir():
    user_dir = appdirs.user_data_dir('keymanager', 'wx_c')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.abspath(user_dir)


def get_md5_data_dir():
    md5_dir = os.path.join(get_user_data_dir(), 'md5')
    if not os.path.exists(md5_dir):
        os.makedirs(md5_dir)
    return md5_dir
