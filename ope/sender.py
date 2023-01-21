import logging
from common_protocol import Initiator, jload, jstore
from utils import G1, Fr, Polynomial, get_Fr, get_G1, my_hash, xor

GROUP = G1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sender")


class Sender(Initiator):
    def __init__(self, dp: int, k: int, g: G1, ip: str, port: int) -> None:
        super().__init__(ip, port)
        self.g = g
        self.dp = dp  # degree of secret polynomial P
        self.P = Polynomial(degree=dp)
        self.d = k * dp  # degree of polynomial Px
        # random polynomial to be generated, Px(0) = 0
        self.Px = Polynomial(degree=self.d, coefficient_0_0=0)
        # Q(x, y) = Px(x) + P(y)
        self.Q = lambda x, y: self.Px(x) + self.P(y)

        self.commitment_pairs = None
        self.Q_poly_results = None

    def set_commitment_pairs(self, commitment_pairs: list[tuple[Fr, Fr]]):
        """N points {(xi, yi)}"""
        self.commitment_pairs = commitment_pairs

    def calculate_Q_values(self):
        self.Q_poly_results = []
        self.Q_poly_results = [self.Q(x, y) for x, y in self.commitment_pairs]


class OtSender:
    def __init__(self, ope_sender: Sender) -> None:
        self.ope_sender = ope_sender

    def produce_Rs(self):
        self.rs = []
        self.Rs = []
        for _ in range(len(self.ope_sender.commitment_pairs)):
            r = get_Fr()
            self.rs.append(r)
            self.Rs.append(self.ope_sender.g * r)
        return self.Rs

    def set_W(self, W: GROUP):
        self.W = W

    def produce_Cs(self):
        self.Cs = []
        for r, R, m_fr in zip(self.rs, self.Rs, self.ope_sender.Q_poly_results):
            K = self.W * (get_Fr(1) / r)
            K_bytes = str(K).encode()
            h_K_bytes = my_hash(K_bytes)
            m_bytes = m_fr.serialize()
            C_bytes = xor(m_bytes, h_K_bytes)
            C = C_bytes.hex()
            self.Cs.append(C)
        return self.Cs


def main():
    HOST = "127.0.0.1"
    PORT = 8800
    n = 30  # n = kd_p + 1
    k = 20
    dp = (n - 1) // k
    alpha = 10
    g = get_G1(value=b"seed")

    sender = Sender(
        dp=dp,
        k=k,
        g=g,
        ip=HOST,
        port=PORT,
    )

    logger.info("Staring Sender...")
    logger.info(f"Sender's P(alpha) = {sender.P(get_Fr(alpha))}")
    commitment_pairs_ = sender.receive_message()
    commitment_pairs = jload({"S": [(Fr, Fr)]}, commitment_pairs_, True)["S"]
    sender.set_commitment_pairs(commitment_pairs=commitment_pairs)

    sender.calculate_Q_values()
    ot_sender = OtSender(sender)

    # # Perform n times OT
    logger.info("Performing OT...")
    for i in range(n):
        logger.debug(f"{i}/{n} OT")

        Rs = ot_sender.produce_Rs()
        sender.send_message(jstore({"Rs": Rs}))

        W_ = sender.receive_message()
        W = jload({"W": GROUP}, W_, True)["W"]
        ot_sender.set_W(W=W)

        Cs = ot_sender.produce_Cs()
        sender.send_message(jstore({"Cs": Cs}))


if __name__ == "__main__":
    main()
