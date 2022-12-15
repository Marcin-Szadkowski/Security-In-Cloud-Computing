from typing import Callable

from common_protocol import Responder, jstore, jload
from utils import G1, Fr, get_Fr, get_G1, my_hash, xor


class Sender(Responder):
    def __init__(
        self,
        ip: str,
        port: int,
        messages: list[str],
        g: G1,
        callback: Callable = None,
    ) -> None:
        super().__init__(ip, port, callback)
        self.n = len(messages)
        self._messages = messages
        self.r = []
        self.R = []
        self.W = None
        self.g = g
        self.C = []

    def get_r(self) -> list[G1]:
        """Get list of R values"""
        for _ in range(self.n):
            r = get_Fr()
            self.r.append(r)
            self.R.append(self.g * r)
        return self.R

    def set_w(self, W: G1) -> None:
        """Set W obtained from Receiver"""
        self.W = W

    def get_c(self) -> list[str]:
        if self.C:
            return self.C

        for r, _, m in zip(self.r, self.R, self._messages):
            K = self.W * (get_Fr(1) / r)  # reverse
            K_bytes = str(K).encode("utf-8")
            # H(K)
            K_hash = my_hash(K_bytes)
            m_bytes = m.encode("utf-8")
            # cj = mj xor H(K)
            C_bytes = xor(m_bytes, K_hash)
            cj = C_bytes.hex()
            self.C.append(cj)
        return self.C


def main():
    n_messages = 10
    g = get_G1(value=b"someTest")
    messages = [f"Message: {i}." for i in range(n_messages)]

    # instantiate Sender
    sender = Sender(ip="172.20.10.10", port=8000, messages=messages, g=g)
    print("Started sender...")
    # get R values
    R = sender.get_r()
    sender.send_message(jstore({"R": R, "g": g}))

    W_ = sender.receive_message()
    W = jload({"W": G1}, W_, True)["W"]
    sender.set_w(W)

    C = sender.get_c()
    sender.send_message(jstore({"C": C}))


if __name__ == "__main__":
    main()
