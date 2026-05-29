import socket

from shared.config import HOST, PORT


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))

    while True:
        message = input("You: ")

        if message.lower() == "exit":
            break

        client_socket.send(message.encode())

    client_socket.close()


if __name__ == "__main__":
    start_client()