from Crypto.Cipher import AES


_HEAD_MARKER = b'AES-V-0000000001'
_HEAD_MARKER_BYTE_SIZE = 16
_HEAD_FILE_SIZE_BYTE_SIZE = 128
_HEAD_LENGTH = _HEAD_MARKER_BYTE_SIZE + _HEAD_FILE_SIZE_BYTE_SIZE + AES.block_size
