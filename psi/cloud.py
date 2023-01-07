from utils import G1, get_Fr, get_G1


class Cloud:
    def __init__(self, g: G1, private_set: set):
        self.g = g
        self.exp = get_Fr()
        # mine private and public sets
        self.private_set = list(private_set)
        self._public_set = self._produce_public_set()

        self.other_public_set = None  # one of Ps or Pc
        self.other_pow_mine_set = None  # one of Psc or Pcs
        self.mine_pow_other_set = None  # one of Psc or Pcs
        print(f"My set: {private_set}")

    @property
    def public_set(self) -> list:
        return self._public_set

    def _produce_public_set(self):
        public_set = []
        for priv in self.private_set:
            g_hat = get_G1(value=priv.encode())
            public_set.append(g_hat * self.exp)

        self._public_set = public_set
        return public_set

    def get_other_powr_mine_set(self):
        other_pow_mine_set = []
        for party_pub in self.other_public_set:
            other_pow_mine_set.append(party_pub * self.exp)
        self.other_pow_mine_set = other_pow_mine_set
        return other_pow_mine_set

    def set_other_public_set(self, other_public_set: list):
        self.other_public_set = other_public_set

    def set_mine_pow_other_set(self, mine_pow_other_set: list):
        self.mine_pow_other_set = mine_pow_other_set

    def get_intersection(self) -> list:
        _intersection = []
        for i, mps in enumerate(self.mine_pow_other_set):
            for ps in self.other_public_set:
                if ps * self.exp == mps:
                    _intersection.append(self.private_set[i])
        return _intersection
