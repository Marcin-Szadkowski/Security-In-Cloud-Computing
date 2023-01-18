import logging

from common_protocol import Initiator, jload, jstore
from utils import G2, get_Fr, get_G2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")


def main():
    IP = "localhost"
    PORT = 8800
    private_set = ["a", "b", "c", "d"]
    r = get_Fr()
    logger.info("Starting Initiator...")
    server = Initiator(ip=IP, port=PORT)

    # # Calculate my public set
    hash_set = [get_G2(value=s.encode()) for s in private_set]
    hash_exp_set = [e * r for e in hash_set]
    server.send_message(message=jstore({"A": hash_exp_set}))

    # # Get {a'l_1,.., a'lv} and {ts_1,.., ts_w} set
    data = server.receive_message()
    B_C = jload({"B": [G2], "C": [G2]}, data, True)

    mine_hash_exp_exp_list = B_C["B"]
    other_hash_exp_list = B_C["C"]

    # # Calculate intersection
    exp = get_Fr(1) / r
    mine_hash_exp_exp_rev_exp_list = [e * exp for e in mine_hash_exp_exp_list]
    mine_hash_exp_exp_set = set(str(e) for e in mine_hash_exp_exp_rev_exp_list)
    his_hash_exp_set = set(str(e) for e in other_hash_exp_list)
    result = len(mine_hash_exp_exp_set & his_hash_exp_set)

    logger.info(f"Intersection: {result}")
    server.send_message(message=str(result))


if __name__ == "__main__":
    main()
