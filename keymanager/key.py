from typing import List, Callable, TypeVar
import zipfile
import os
import time
import hashlib
from io import BytesIO
import threading

from axel import Event

from keymanager.encryptor import encrypt_data, pad_key, is_encrypt_data, decrypt_data
from keymanager.utils import write_file, read_file, read_header, get_md5_data_dir

_Key = TypeVar("KeyType", bound="Key")


class Key:

    def __init__(self):
        self.id = os.urandom(16).hex()
        self.name: str = None
        self._key: bytes = None
        self.path: str = None
        self.md5: bytes = None
        self._update_last_access()

        self._timeout = False

    def copy(self) -> _Key:
        key = Key()
        key.id = self.id
        key.name = self.name
        key._key = self._key
        key.path = self.path
        key.md5 = self.md5
        key._update_last_access()
        key._timeout = False
        return key

    def _update_last_access(self):
        self.last_access = time.time()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        if timeout:
            self._key = None
        self._timeout = timeout

    @property
    def key(self):
        if not self._timeout:
            self._update_last_access()
            return self._key
        raise KeyTimeOutException()

    @key.setter
    def key(self, key: bytes):
        self._update_last_access()
        self._timeout = False
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

    def touch(self):
        return self.key

    @staticmethod
    def need_password(key_path):
        marker_bytes = read_header(key_path)
        return is_encrypt_data(marker_bytes)

    def load(self, key_path, password: str = None):

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
            # 整个文件用空密码解密
            input_bytes = decrypt_data(blank_password, input_raw_bytes)

        buffer = BytesIO(input_bytes)

        with zipfile.ZipFile(buffer) as mem_zipfile:
            self.id = mem_zipfile.read('id').decode('utf-8')
            self.name = mem_zipfile.read('name').decode('utf-8')
            self._key = mem_zipfile.read('key')
            if password is not None:
                password_b = self.sha_passwd(password)
                if mem_zipfile.read('passwd').hex() != password_b.hex():
                    raise InvalidPasswordException('密码错误')
            if password is not None:
                self._key = decrypt_data(password, self._key)

        self._update_last_access()
        self._timeout = False

    def save(self, key_path, password: str = None, calc_md5: bool = True):
        self._update_last_access()
        self.path = key_path

        passwd_md5 = None
        # 补全密码
        if password is not None:
            illegal, msg = Key.is_password_illegal(password)
            if illegal:
                raise InvalidKeyException(msg)
            password = self.pad_key(password)
            password_b = self.sha_passwd(password)

        # zip文件写入内存
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as mem_zipfile:
            mem_zipfile.writestr('id', self.id.encode('utf-8'))
            mem_zipfile.writestr('name', self.name.encode('utf-8'))
            # 使用密码加密key
            key_data = self._key
            if password is not None:
                mem_zipfile.writestr('passwd', password_b)
                key_data = encrypt_data(password, self._key)
            mem_zipfile.writestr('key', key_data)

        buffer.seek(0, 0)
        output_bytes = buffer.read()

        # 有密码的情况下使用空密码进行加密，作为标记
        if password is not None:
            blank_password = self.pad_key('')
            output_bytes = encrypt_data(blank_password, output_bytes)

        self.md5 = hashlib.md5(output_bytes).digest()

        # 写入文件
        write_file(key_path, output_bytes)

        if calc_md5:
            self.save_md5()

    def sha_passwd(self, password):
        passwd_sha512 = hashlib.sha512((password.decode('utf-8') + self.id).encode("utf-8"))
        passwd_sha512_b = passwd_sha512.digest()
        return passwd_sha512_b

    def save_md5(self):
        write_file(self.get_md5_file_path(), self.md5)

    def get_md5_file_path(self):
        md5_dir = get_md5_data_dir()
        key_md5_file_path = os.path.join(md5_dir, self.id)
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


class InvalidPasswordException(Exception):
    pass


class KeyCache:

    def __init__(self):
        self._key_list: List[Key] = []
        self._current_key:Key = None

        self.current_key_changed = Event()
        self.key_added = Event()
        self.key_removed = Event()

    def add_current_key_changed_callback(self, cb: Callable[[Key, Key], None]):
        self.current_key_changed += cb

    def add_key_added_callback(self, cb: Callable[[Key],None]):
        self.key_added += cb

    def add_key_removed_callback(self, cb: Callable[[Key], None]):
        self.key_removed += cb

    def set_current_key(self, key: Key):
        if key == self._current_key:
            return
        old_key = self._current_key
        self._current_key = key
        self.current_key_changed(old_key, key)

    def add_key(self, key: Key):
        self._key_list.append(key)
        self.key_added(key)

    def remove_key(self, idx):
        if self._current_key.id == self._key_list[idx]:
            self._current_key = None
        removed_key = self._key_list[idx]
        del self._key_list[idx]
        self.key_removed(removed_key)

    def get_cur_key(self):
        return self._current_key

    def is_cur_key(self, key: Key):
        if self._current_key is None:
            return False
        if key is None:
            return False
        return key.id == self._current_key.id

    def get_key_list(self):
        return self._key_list


def _check_key():
    while True:
        cache = KEY_CACHE
        key_list = cache.get_key_list()
        current_key = cache.get_cur_key()

        try:
            KEY_CHECKER['current_keystatus'](current_key)
        finally:
            pass

        for key in key_list:
            last_tm = key.last_access
            now = time.time()
            duration = now - last_tm
            if key.timeout:
                continue
            if duration > KEY_CHECKER['timeout']:
                try:
                    KEY_CHECKER['invalidate'](key)
                finally:
                    key.timeout = True
        time.sleep(1)


KEY_CACHE = KeyCache()
KEY_CHECKER = {
    'invalidate': Event(threads=0),
    'current_keystatus': Event(threads=0),
    'thread': None,
    'timeout': 60 * 5
}


def set_key_timeout(timeout: int):
    KEY_CHECKER['timeout'] = timeout


def start_check_key_thread():
    if KEY_CHECKER['thread'] is None:
        _CHECK_KEY_THREAD = threading.Thread(target=_check_key, daemon=True)
        _CHECK_KEY_THREAD.start()


def add_key_invalidate_callback(cb: Callable[[Key], None]):
    KEY_CHECKER['invalidate'] += cb


def add_current_keystatus_callback(cb: Callable[[Key], None]):
    KEY_CHECKER['current_keystatus'] += cb

