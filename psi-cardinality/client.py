import logging
from random import shuffle

from common_protocol import Responder, jload, jstore
from utils import G2, get_Fr, get_G2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Client")


def main():
    IP = "localhost"
    PORT = 8800
    private_set = ["a", "d", "c", "f", "g", "h"]
    shuffle(private_set)

    # # Init params
    d = get_Fr()
    logger.info("Starting Responder...")
    logger.debug("this is debug")
    client = Responder(ip=IP, port=PORT)

    # # Calculate mine public set: hash of private set element to the power of random secret
    hash_set = [get_G2(value=c.encode()) for c in private_set]
    mine_hash_exp_set = [e * d for e in hash_set]

    # # Get other's party public set
    A_ = client.receive_message()
    A = jload({"A": [G2]}, A_, True)
    other_hash_exp_set = A["A"]

    # # Calcualte other's party public set to the power of my random secret
    shuffle(other_hash_exp_set)
    his_perm_hash_exp_exp_set = [e * d for e in other_hash_exp_set]

    client.send_message(
        message=jstore({"B": his_perm_hash_exp_exp_set, "C": mine_hash_exp_set})
    )

    result = client.receive_message()
    logger.info(f"Intersection: {result}")


if __name__ == "__main__":
    main()
