from pathlib import Path

from common_protocol import Initiator
from models import TaggedBlock
from utils import (
    Fr,
    Poly,
    get_file_hash,
    get_Fr,
    get_G1,
    partition_file,
)


class Client(Initiator):
    def __init__(self, z_subblocks: int, ip: str = None, port: int = None):
        if ip and port:
            super().__init__(ip, port)
        self.z = z_subblocks  # the number of subblocks that file is partioned in
        self.g = None
        self.sk = None  # secret key
        self.tagged_blocks: dict[TaggedBlock] = {}
        self.polynomial = None  # polynomial Lf = SUM 0..z (a_i * x^i)
        self.m_blocks: list[Fr] = []  # f = (m1,... ,mz)
        self.f_id: str | None = None
        self.H = None
        self.K = None

    def setup(self):
        """At setup client generates the secret key"""
        self.g = get_G1()
        self.sk = get_Fr()

    def tag_block(self) -> dict[int, TaggedBlock]:
        """Tag generating procedure"""
        for idx, m in enumerate(self.m_blocks):
            t = self.polynomial(m)
            self.tagged_blocks[idx] = TaggedBlock(m=m, t=t)

        return self.tagged_blocks

    def poly(self):
        """Polynomial generating procedure"""

        def gen_a(i: int):
            # ai = SPRNG(SKc, ID(f), i, Zq)
            # SKc, ID(f), i are used as a seed
            return Fr.setHashOf((str(self.sk) + self.f_id + str(i)).encode("UTF-8"))

        self.coefficients = list(map(gen_a, list(range(self.z + 1))))
        self.polynomial = Poly(coefficients=self.coefficients)

    def gen_challenge(self) -> tuple:
        """Generating a challange for server"""
        Lf = self.polynomial(get_Fr(0))
        r = get_Fr()
        xc = get_Fr()

        while xc in self.m_blocks:
            xc = get_Fr()

        self.K = self.g * (r * self.polynomial(xc))
        self.H = (self.g * r, xc, self.g * (r * Lf))
        return self.H

    def check_proof(self, P):
        """Verify proof returned by server"""
        if self.K == P:
            print("Proof accepted")
            return True
        else:
            print("Proof not correct")
            return False

    def load_file(self, file_path: Path):
        """Partition file to z subblocks"""
        subblocks = []
        self.f_id = get_file_hash(file_path)

        with open(file_path, "r") as file:
            file_lines = file.readlines()

        # divide into z chunks
        file_chunks = partition_file(self.z, file_lines)

        for chunk in file_chunks:
            m = Fr.setHashOf(chunk.encode("UTF-8"))  # exponent from hash value
            subblocks.append(m)

        self.m_blocks = subblocks


def main():
    host = "172.20.10.9"
    port = 8000

    client = Client(z_subblocks=8, ip=host, port=port)
    client.setup()
    client.load_file("/home/marcin/Documents/cloud_sec/pop/file.txt")
    client.poly()

    # send tagged blocks
    T = client.tag_block()
    client.send_bytes(T)

    # send challenge
    H = client.gen_challenge()
    client.send_bytes(H)

    # get prove
    P = client.receive_bytes()
    correct = client.check_proof(P=P)
    assert correct


if __name__ == "__main__":
    main()
