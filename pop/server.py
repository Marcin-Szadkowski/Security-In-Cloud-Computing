from common_protocol import Responder
from models import Point, TaggedBlock
from utils import get_Fr, li_exp


class Server(Responder):
    def __init__(self, ip: str = None, port: int = None) -> None:
        if ip and port:
            super().__init__(ip, port)
        self.H = None  # This is a challenge, get from client
        self.tagged_blocks = {}
        self.proof_blocks = {}  # proofs dict computed on challange
        self.gr = None
        self.xc = None
        self.ordinate0 = None
        self.P = None  # a proof

    def set_tagged_blocks(self, T: dict[int, TaggedBlock]) -> None:
        self.tagged_blocks = T

    def set_challenge(self, H) -> None:
        self.H = H
        self.gr, self.xc, self.ordinate0 = H

    def gen_proof(self):
        for key, tagged_block in self.tagged_blocks.items():
            ordinate = self.gr * tagged_block.t
            self.proof_blocks[key] = Point(x=tagged_block.m, y=ordinate)

        self.proof_blocks[len(self.proof_blocks)] = Point(x=get_Fr(0), y=self.ordinate0)
        self.P = li_exp(x=self.xc, points=self.proof_blocks)

        return self.P


def main():
    host = "172.20.10.10"
    port = 8000

    server = Server(host, port)

    # receive tagged blocks
    T = server.receive_bytes()
    server.set_tagged_blocks(T)

    # get challange
    H = server.receive_bytes()
    server.set_challenge(H=H)

    # gen prove
    P = server.gen_proof()
    server.send_bytes(P)

    server.sock.close()


if __name__ == "__main__":
    main()
