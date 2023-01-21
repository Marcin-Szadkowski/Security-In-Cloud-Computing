import hashlib
import os
import sys

sys.path.insert(1, "/home/marcin//mcl-python")
from mcl import G1, Fr  # type: ignore


class Polynomial:
    def __init__(self, degree: int, coefficient_0_0: int = None):
        coefficients = [get_Fr() for _ in range(degree + 1)]
        if coefficient_0_0 is not None:
            coefficients[-1] = get_Fr(value=coefficient_0_0)
        self.coefficients = coefficients

    def __call__(self, x):
        pol_val = get_Fr(0)
        for i, a in enumerate(self.coefficients):
            exponent = len(self.coefficients) - i - 1
            pol_val += a * pow_Fr(fr=x, exp=exponent)
        return pol_val

    def __contains__(self, item):
        return item in self.coefficients


def lagrangian_interpolation(x, known_x_y):
    abscissas = [el[0] for el in known_x_y]
    seen = []
    for abscissa in abscissas:
        if abscissa not in seen:
            seen.append(abscissa)

    main_sum = get_Fr(0)
    for i, (x_i, ordinate_i) in enumerate(known_x_y):
        exp_product_i = get_Fr(1)
        for j, (x_j, _) in enumerate(known_x_y):
            if i == j:
                continue
            exp_product_i *= (x - x_j) / (x_i - x_j)
        main_sum += ordinate_i * exp_product_i

    return main_sum


def pow_Fr(fr, exp):
    if exp == 0:
        return get_Fr(1)
    result = get_Fr(1)
    for _ in range(exp):
        result *= fr
    return fr


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
