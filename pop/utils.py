import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(1, "/home/marcin//mcl-python")
from mcl import G1, Fr  # type: ignore

from models import Point


class Poly:
    def __init__(self, coefficients=None):
        if coefficients is None:
            coefficients = []

        self.coefficients = coefficients

    def __call__(self, x):
        pol_val = get_Fr(0)
        for i, a in enumerate(self.coefficients):
            exponent = len(self.coefficients) - i - 1
            pol_val += a * pow_Fr(fr=x, exp=exponent)
        return pol_val

    def __contains__(self, item):
        return item in self.coefficients


def li_exp(x, points: dict[Point]):
    _sum = G1()

    for i, point_i in points.items():
        xi = point_i.x
        yi = point_i.y
        exp_product_i = get_Fr(1)

        for j, point_j in points.items():
            if i == j:
                continue
            xj = point_j.x
            exp_product_i *= (x - xj) / (xi - xj)
        _sum += yi * exp_product_i

    return _sum


def get_file_hash(file_path: Path) -> str:
    block_size = 65536
    file_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        fb = file.read(block_size)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = file.read(block_size)
    return file_hash.hexdigest()


def partition_file(z_blocks: int, lines: list[str]) -> list[str]:
    """Divide file lines into z blocks"""
    k, m = divmod(len(lines), z_blocks)
    z_lines = (
        lines[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(z_blocks)
    )
    chunks = []
    for _lines in z_lines:
        chunks.append("".join(_lines))
    return chunks


def get_Fr(value=None):
    fr = Fr()
    if value is None:
        fr.setByCSPRNG()
    else:
        fr.setInt(value)
    return fr


def pow_Fr(fr, exp):
    result = get_Fr(1)
    for _ in range(exp):
        result *= fr
    return fr


def get_G1(value=None):
    if value is None:
        rnd_bytes = os.urandom(16)
        g = G1.hashAndMapTo(rnd_bytes)
    else:
        g = G1.hashAndMapTo(value)
    return g


def jstore(d):
    return json.dumps(
        {k: v.getStr().decode() if type(v) != bytes else v.hex() for k, v in d.items()}
    )


def jload(d, j):
    j = json.loads(j)
    r = []
    for k, t in d.items():
        if t != bytes:
            v = t()
            v.setStr(j[k].encode())
        else:
            v = t.fromhex(j[k])
        r.append(v)
    return r
