import json
import socket
from typing import Callable

RECV_BUF_SIZE = 4 * 1024  # Receive a page
STRING_ENCODING = "utf-8"
IP_VERSION = socket.AF_INET  # Use IPv4
SYNC_CHARACTER = "_"

UPDATED_VERSION = True


class Party:
    """Protocol party."""

    def send_message(self, message: str) -> None:
        """Send a message to the other party."""
        if UPDATED_VERSION:
            # Append a page of sync data to the payload
            payload = message + SYNC_CHARACTER * RECV_BUF_SIZE
        else:
            payload = message
        self.sock.send(bytes(payload, STRING_ENCODING))

    def receive_message(self) -> str:
        """Receive a message from the other party."""

        if UPDATED_VERSION:
            message = ""
            while message[-RECV_BUF_SIZE:] != SYNC_CHARACTER * RECV_BUF_SIZE:
                frame = str(self.sock.recv(RECV_BUF_SIZE), STRING_ENCODING)
                if not frame:
                    raise Exception(
                        "Failed to receive the message from the other party"
                    )
                message += frame
            # Skip the last page of sync
            return message[:-RECV_BUF_SIZE]
        else:
            return str(self.sock.recv(RECV_BUF_SIZE), STRING_ENCODING)


class Initiator(Party):
    """Initiator party (prover, signer, client)."""

    def __init__(self, ip: str, port: int) -> None:
        """Start the initiator."""
        # Open a clientside TCP socket
        self.sock = socket.socket(IP_VERSION, socket.SOCK_STREAM, 0)
        # Connect to the responder (verifier, server)
        self.sock.connect((ip, port))


class Responder(Party):
    """Responder party (verifier, server)."""

    def __init__(self, ip: str, port: int, callback: Callable = None) -> None:
        """Start the responder."""
        # Open a serverside TCP socket
        self.listen_sock = socket.socket(IP_VERSION, socket.SOCK_STREAM, 0)
        # Assign a name to the socket
        self.listen_sock.bind((ip, port))
        # Mark the socket as passive with no backlog
        self.listen_sock.listen(0)
        # Run a custom callback, if any provided, e.g. to synchronize
        # the initiator and the responder on a single host
        if callback:
            callback()
        # Block until a client connects
        self.sock, _ = self.listen_sock.accept()


class MCLJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "getStr"):
            return o.getStr().decode() if type(o) != bytes else o.hex()
        else:
            return json.JSONEncoder.default(self, o)


def jload(
    expected_values: dict, json_str: str, return_dict: bool = False
) -> dict | list:
    preprocessed_dict = json.loads(json_str)
    result = {} if return_dict else []

    for key, val in expected_values.items():
        type = val
        decoded = __parse_single(type, preprocessed_dict[key])

        if return_dict:
            result[key] = decoded
        else:
            result.append(decoded)

    return result


def __parse_single(cls, str_or_list):
    try:
        iter(cls)
        iterable = True
    except TypeError as te:
        iterable = False

    if iterable:
        decoded = []
        if len(cls) == 1:
            list = [cls[0] for i in range(len(str_or_list))]
        elif len(cls) == len(str_or_list):
            list = cls
        else:
            raise Exception("Expected list length differs.")
        for i, single in enumerate(str_or_list):
            decoded.append(__parse_single(list[i], single))
        decoded = type(cls)(decoded)
    else:
        object = str_or_list
        if not isinstance(object, cls) if cls != None else cls != None:
            if cls != bytes:
                decoded = cls()
                decoded.setStr(object.encode())
            else:
                decoded = cls.fromhex(object)
        else:
            decoded = object
    return decoded


def jstore(dictionary: dict) -> str:
    return json.dumps(dictionary, cls=MCLJsonEncoder)


def __jstore(d: dict) -> str:
    return json.dumps(
        {k: v.getStr().decode() if type(v) != bytes else v.hex() for k, v in d.items()}
    )


def __jload_single(d: dict, j: str) -> dict:
    j = json.loads(j)
    r = []
    for k, t in d.items():
        if t != bytes:
            v = t()
            v.setStr(j[k].encode())
        else:
            v = t.fromhex(j[k])
        r.append(v)
    return r
