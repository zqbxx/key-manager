from typing import List
import zipfile
import os
import time
import hashlib
from io import BytesIO

from keymanager.encryptor import encrypt_data_with_head, pad_key, is_encrypt_data, decrypt_data
from keymanager.utils import write_file, read_file, read_header, get_md5_data_dir


class Key:

    def __init__(self):
        self.id = os.urandom(16).hex()
        self.name: str = None
        self._key: bytes = None
        self.path: str = None
        self.md5: bytes = None
        self._update_last_access()

    def _update_last_access(self):
        self.last_access = time.time()

    @property
    def key(self):
        self._update_last_access()
        return self._key

    @key.setter
    def key(self, key: bytes):
        self._update_last_access()
        self._key = key

    @staticmethod
    def is_password_illegal(password: str):
        if password is None:
            return True, '密码不能为空'
        b = password.encode('utf-8')
        bl = len(b)
        if bl == 0:
            return True, '密码不能为空'
        if bl > 32:
            return True, '密码太长'
        return False, ''

    @staticmethod
    def need_password(key_path):
        marker_bytes = read_header(key_path)
        return is_encrypt_data(marker_bytes)

    def load(self, key_path, password: str = None):

        self._update_last_access()
        self.path = key_path

        input_raw_bytes = read_file(self.path)
        input_bytes = input_raw_bytes

        self.md5 = hashlib.md5(input_bytes)

        if password is not None:
            illegal, msg = Key.is_password_illegal(password)
            if illegal:
                raise InvalidKeyException(msg)
            password = self.pad_key(password)
            blank_password = self.pad_key('')
            # 整个文件用空密码加密
            input_bytes = decrypt_data(blank_password, input_raw_bytes)

        buffer = BytesIO(input_bytes)

        with zipfile.ZipFile(buffer) as mem_zipfile:
            self.id = mem_zipfile.read('id').decode('utf-8')
            self.name = mem_zipfile.read('name').decode('utf-8')
            self._key = mem_zipfile.read('key')
            if password is not None:
                self._key = decrypt_data(password, self._key)

    def save(self, key_path, password: str = None, calc_md5: bool = True):
        self._update_last_access()
        self.path = key_path

        # 补全密码
        if password is not None:
            illegal, msg = Key.is_password_illegal(password)
            if illegal:
                raise InvalidKeyException(msg)
            password = self.pad_key(password)

        # zip文件写入内存
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as mem_zipfile:
            mem_zipfile.writestr('id', self.id.encode('utf-8'))
            mem_zipfile.writestr('name', self.name.encode('utf-8'))
            # 使用密码加密key
            key_data = self._key
            if password is not None:
                key_data = encrypt_data_with_head(password, self._key)
            mem_zipfile.writestr('key', key_data)

        buffer.seek(0, 0)
        output_bytes = buffer.read()

        # 有密码的情况下使用空密码进行加密，作为标记
        if password is not None:
            blank_password = self.pad_key('')
            output_bytes = encrypt_data_with_head(blank_password, output_bytes)

        self.md5 = hashlib.md5(output_bytes).digest()

        # 写入文件
        write_file(key_path, output_bytes)

        if calc_md5:
            self.save_md5()

    def save_md5(self):
        write_file(self.get_md5_file_path(), self.md5)

    def get_md5_file_path(self):
        md5_dir = get_md5_data_dir()
        key_md5_file_path = os.join(md5_dir, self.id)
        return key_md5_file_path

    def is_key_modified(self):
        md5: bytes = self._load_md5()
        if md5 is None:
            return None
        return not (md5.hex() == self.md5.hex())

    def _load_md5(self):
        key_md5_file_path = self.get_md5_file_path()
        if not os.path.exists(key_md5_file_path):
            return None
        return read_file(key_md5_file_path)

    def pad_key(self, password: str):
        if password is None:
            password = ''
        return pad_key(password.encode('utf-8'))


class KeyTimeOutException(Exception):
    pass


class InvalidKeyException(Exception):
    pass


KEY_TIMEOUT = float(60 * 30)


class KeyCache:

    def __init__(self):
        self._current_key: Key = None
        self.key_list: List[Key] = []
        self.last_tm = time.time()

    @property
    def current_key(self):
        return self._current_key

    @current_key.setter
    def current_key(self, current_key):
        self._current_key = current_key

    def is_key_loaded(self):
        return self._current_key is not None

    def get_key_list(self):
        return self.key_list

    def update_tm(self):
        self.last_tm = time.time()

    def check_timeout(self):
        duration = time.time() - self.last_tm
        if duration > KEY_TIMEOUT:
            raise KeyTimeOutException


KEY_CACHE = KeyCache()
