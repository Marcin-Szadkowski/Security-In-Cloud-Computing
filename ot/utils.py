import hashlib
import sys
import os

sys.path.insert(1, "/home/marcin//mcl-python")
from mcl import G1, Fr  # type: ignore


def xor(a: bytes, b: bytes) -> bytes:
    return bytes([x ^ y for x, y in zip(a, b)])


def my_hash(value: bytes) -> bytes:
    _hash = hashlib.sha256()
    _hash.update(value)
    return _hash.digest()


def get_Fr(value=None):
    fr = Fr()
    if value is None:
        fr.setByCSPRNG()
    else:
        fr.setInt(value)
    return fr


def get_G1(value=None):
    if value is None:
        rnd_bytes = os.urandom(16)
        g = G1.hashAndMapTo(rnd_bytes)
    else:
        g = G1.hashAndMapTo(value)
    return g
