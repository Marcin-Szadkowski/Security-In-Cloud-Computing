from client import Client
from server import Server


def main():
    client = Client(z_subblocks=8)
    client.setup()
    client.load_file("/home/marcin/Documents/cloud_sec/pop/file.txt")
    client.poly()
    T = client.tag_block()

    server = Server()
    server.set_tagged_blocks(T=T)

    H = client.gen_challenge()

    server.set_challenge(H=H)
    P = server.gen_proof()

    correct = client.check_proof(P=P)
    assert correct


if __name__ == "__main__":
    main()
