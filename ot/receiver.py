from common_protocol import Initiator, jload, jstore
from utils import G1, Fr, get_Fr, my_hash, xor


class Receiver(Initiator):
    def __init__(self, ip: str, port: int, j: int) -> None:
        super().__init__(ip, port)
        self.alpha = None  # selected at random
        self.j = j  # j-th message to be requested
        self.R = []
        self.W = None
        self.g = None
        self.C = []  # cj list

    def set_r(self, R: list[G1], g: G1) -> None:
        self.R = R
        self.g = g

    def get_w(self) -> G1:
        self.alpha = get_Fr()
        R = self.R[self.j]
        self.W = R * self.alpha

        return self.W

    def get_message(self, C: list[str]) -> str:
        self.C = C

        C = self.C[self.j]
        print(f"Trying to decode: {C}")

        g_a_bytes = str(self.g * self.alpha).encode("utf-8")
        _hash = my_hash(g_a_bytes)

        C_bytes = bytes.fromhex(C)
        # m = c_j xor H(g^a)
        m_bytes = xor(C_bytes, _hash)
        m = m_bytes.decode()
        print(f"Decoded message: {m}")
        return m


def main():
    j = 3
    receiver = Receiver(ip="172.20.10.9", port=8000, j=j)

    _result = receiver.receive_message()
    result = jload({"R": [G1], "g": G1}, _result, True)
    R, g = result["R"], result["g"]

    receiver.set_r(R, g)

    W = receiver.get_w()
    receiver.send_message(jstore({"W": W}))

    _C = receiver.receive_message()
    C = jload({"C": [str]}, _C, True)["C"]
    m = receiver.get_message(C=C)

    print(f"Got message: {m}")


if __name__ == "__main__":
    main()
