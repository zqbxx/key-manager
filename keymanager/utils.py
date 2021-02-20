from keymanager import _HEAD_MARKER_BYTE_SIZE


def write_file(path: str, bs: bytes):
    with open(path, 'wb') as f:
        f.write(bs)


def read_file(path: str):
    with open(path, 'rb') as f:
        return f.read()


def read_header(path: str):
    with open(path, 'rb') as f:
        return f.read(_HEAD_MARKER_BYTE_SIZE)
