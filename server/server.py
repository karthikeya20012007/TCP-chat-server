import socket

from shared.config import HOST, PORT, BUFFER_SIZE


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((HOST, PORT))

    server_socket.listen()

    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    client_socket, client_address = server_socket.accept()

    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        message = client_socket.recv(BUFFER_SIZE)

        if not message:
            print("[DISCONNECTED] Client disconnected.")
            break

        print(f"[MESSAGE RECEIVED] {message.decode()}")

    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    start_server()