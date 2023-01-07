import random

from common_protocol import Responder, jload, jstore
from utils import (
    G1,
    Fr,
    Polynomial,
    get_Fr,
    get_G1,
    lagrangian_interpolation_list,
    my_hash,
    xor,
)

GROUP = G1


class Receiver(Responder):
    def __init__(
        self, k: int, n: int, m: int, dr: int, g: G1, alpha: int, ip: str, port: int
    ) -> None:
        super().__init__(ip, port)
        self.alpha = alpha
        self.n = n
        self.m = m
        self.g = g
        self.k = k  # degree of polynomial S
        self.S = Polynomial(degree=self.k, coefficient_0_0=self.alpha)  # S(0) = alpha
        self.dr = dr  # degree of polynomial R

        self.T = []
        self.interpolation_pairs = []
        self.xs = [
            get_Fr() for _ in range(self.n * self.m)
        ]  # N random elements from field F

    def produce_commitment_pairs(self):
        """Pairs <xi, S(x)> or <xi, random from field> if i not in T"""
        T = self._get_subset_of_indices()
        commitment_pairs = [None] * self.n * self.m

        for ind in range(self.n * self.m):
            if ind in T:
                x = self.xs[ind]
                commitment_pairs[ind] = (x, self.S(x))
            else:
                x = self.xs[ind]
                commitment_pairs[ind] = (x, get_Fr())
        print(f"{T=}")
        assert len(T) == self.n, "Wrong indexes (self.I) length."
        return commitment_pairs

    def _get_subset_of_indices(self) -> list:
        if self.T:
            return
        while len(self.T) < self.n:
            rand_ind = random.randint(a=0, b=self.n * self.m - 1)
            if rand_ind not in self.T:
                self.T.append(rand_ind)
        return self.T

    def set_Rs(self, Rs: list[GROUP]):
        self.Rs = Rs

    def set_Cs(self, Cs: list[str]):
        self.Cs = Cs

    def produce_W(self, j: int):
        self.rand_exp = get_Fr()
        R = self.Rs[j]
        self.W = R * self.rand_exp

        return self.W

    def produce_message(self, j: int):
        C = self.Cs[j]
        hash_obj = None
        g_a_bytes = str(self.g * self.rand_exp).encode()
        hash_obj = my_hash(g_a_bytes)

        h_g_bytes = hash_obj
        C_bytes = bytes.fromhex(C)
        m_bytes = xor(C_bytes, h_g_bytes)
        m = Fr()
        m.deserialize(m_bytes)
        return m

    def append_interpolation_pair(self, interpolation_pair):
        self.interpolation_pairs.append(interpolation_pair)

    def interpolate_polynomial_P(self):
        value = lagrangian_interpolation_list(
            x=get_Fr(value=0), abscissa_ordinate_list=self.interpolation_pairs
        )
        print(f"P(alpha)= {value}")


def main():
    HOST = "127.0.0.1"
    PORT = 8800
    n = 30  # n = d_r + 1 = d + 1 = kd_p + 1
    m = 10
    k = 20
    dr = n - 1
    alpha = 10
    g = get_G1(value=b"genQ")
    receiver = Receiver(
        k=k,
        n=n,
        m=m,
        dr=dr,
        g=g,
        alpha=alpha,
        ip=HOST,
        port=PORT,
    )

    commitment_pairs = receiver.produce_commitment_pairs()
    receiver.send_message(jstore({"S": commitment_pairs}))

    for i, ind in enumerate(receiver.T):
        print(f"Doing {i} OT.")
        Rs_ = receiver.receive_message()
        Rs = jload({"Rs": [GROUP]}, Rs_, True)["Rs"]
        receiver.set_Rs(Rs=Rs)

        W = receiver.produce_W(j=ind)
        receiver.send_message(jstore({"W": W}))

        Cs_ = receiver.receive_message()
        Cs = jload({"Cs": [str]}, Cs_, True)["Cs"]
        receiver.set_Cs(Cs=Cs)

        interpolation_ordinate = receiver.produce_message(j=ind)
        receiver.append_interpolation_pair((receiver.xs[ind], interpolation_ordinate))
    receiver.interpolate_polynomial_P()


if __name__ == "__main__":
    main()
