from cloud import Cloud
from common_protocol import Responder, jload, jstore
from utils import G1, get_G1


class CloudResponder(Responder, Cloud):
    def __init__(self, g: G1, private_set: set, ip: str = None, port: int = None):
        Responder.__init__(self, ip, port)
        Cloud.__init__(self, g=g, private_set=private_set)


def main():
    IP = "127.0.0.1"
    PORT = 8800
    my_set = ["f", "e", "d", "g", "h", "i"]

    g = get_G1(value=b"genQ")
    cloud_responder = CloudResponder(g=g, private_set=set(my_set), ip=IP, port=PORT)

    # # Get other party public set
    _payload = cloud_responder.receive_message()
    A = jload({"A": [G1]}, _payload, True)
    other_public_set = A["A"]
    cloud_responder.set_other_public_set(other_public_set)

    # # Send Ps and Pcs
    mine_public_set = cloud_responder.public_set
    other_pow_mine_set = cloud_responder.get_other_powr_mine_set()

    cloud_responder.send_message(
        message=jstore({"B": mine_public_set, "C": other_pow_mine_set})
    )

    # # Get Psc
    _payload = cloud_responder.receive_message()
    D = jload({"D": [G1]}, _payload, True)
    mine_public_set_party = D["D"]
    cloud_responder.set_mine_pow_other_set(mine_public_set_party)

    # # Calculate intersection
    intersection = cloud_responder.get_intersection()
    print(f"Intersection: {intersection}")


if __name__ == "__main__":
    main()
