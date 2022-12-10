import sys
import typing
from dataclasses import dataclass

sys.path.insert(1, "/home/marcin//mcl-python")
from mcl import G1, Fr  # type: ignore


@dataclass
class TaggedBlock:
    m: Fr
    t: Fr | None = None


@dataclass
class Point:
    x: typing.Any
    y: typing.Any


@dataclass
class Challenge:
    gr: G1
    xc: Fr
    grLf0: G1
