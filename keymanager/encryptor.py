from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad, unpad

from keymanager import _HEAD_MARKER, _HEAD_FILE_SIZE_BYTE_SIZE, _HEAD_LENGTH, _HEAD_MARKER_BYTE_SIZE


def pad_key(key, key_length=32):
    return pad(key, key_length, style='pkcs7')


def generate_iv():
    return Random.new().read(AES.block_size)


def encrypt_data(key, raw_data: bytes):
    data_len = len(raw_data)
    iv, enc_data = encrypt_data1(key, raw_data)
    return _HEAD_MARKER + data_len.to_bytes(_HEAD_FILE_SIZE_BYTE_SIZE, byteorder='big') + iv + enc_data


def encrypt_data1(key, raw_data: bytes):
    iv = generate_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_data = cipher.encrypt(pad(raw_data, AES.block_size, style='pkcs7'))
    return iv, enc_data


def decrypt_data(key, enc_data: bytes):

    if not is_encrypt_data(enc_data):
        return b''

    data_len_bytes = enc_data[_HEAD_MARKER_BYTE_SIZE:_HEAD_FILE_SIZE_BYTE_SIZE + _HEAD_MARKER_BYTE_SIZE]
    data_len = int.from_bytes(data_len_bytes, byteorder='big')

    iv = enc_data[_HEAD_FILE_SIZE_BYTE_SIZE + _HEAD_MARKER_BYTE_SIZE:_HEAD_LENGTH]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw_data = cipher.decrypt(enc_data[_HEAD_LENGTH:])
    return raw_data[:data_len]


def decrypt_data1(key, iv, length, enc_data: bytes):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw_data = cipher.decrypt(enc_data)
    if length == -1:
        return unpad(raw_data, AES.block_size, style='pkcs7')
    return raw_data[:length]


def is_encrypt_data(enc_data: bytes):
    marker_bytes = enc_data[:_HEAD_MARKER_BYTE_SIZE]
    if marker_bytes.hex() == _HEAD_MARKER.hex():
        return True
    return False


def not_encrypt_data(enc_data: bytes):
    return not is_encrypt_data(enc_data)
