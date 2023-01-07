from cloud import Cloud
from common_protocol import Initiator, jload, jstore
from utils import G1, get_G1


class CloudInitiator(Initiator, Cloud):
    def __init__(self, g: G1, private_set: set, ip: str = None, port: int = None):
        Initiator.__init__(self, ip, port)
        Cloud.__init__(self, g=g, private_set=private_set)


def main():
    IP = "127.0.0.1"
    PORT = 8800
    my_set = ["a", "b", "c", "d", "e", "f"]

    g = get_G1(value=b"genQ")
    cloud_initiator = CloudInitiator(g=g, private_set=set(my_set), ip=IP, port=PORT)

    # # Send mine public set
    mine_public_set = cloud_initiator.public_set
    cloud_initiator.send_message(message=jstore({"A": mine_public_set}))

    # # Get Ps and Pcs
    _payload = cloud_initiator.receive_message()
    B_C = jload({"B": [G1], "C": [G1]}, _payload, True)

    other_public_set = B_C["B"]
    mine_pow_other_set = B_C["C"]
    cloud_initiator.set_other_public_set(other_public_set)
    cloud_initiator.set_mine_pow_other_set(mine_pow_other_set)

    # # Send Psc
    party_public_set_mine = cloud_initiator.get_other_powr_mine_set()
    cloud_initiator.send_message(message=jstore({"D": party_public_set_mine}))

    # # Calculate intersection
    intersection = cloud_initiator.get_intersection()
    print(f"Intersection: {intersection}")


if __name__ == "__main__":
    main()
