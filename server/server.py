import socket
import threading

from shared.config import HOST, PORT, BUFFER_SIZE

clients = {}


def broadcast(message, sender_socket):
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.send(message)

            except:
                del clients[client]
                client.close()


def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE)

            if not message:
                username = clients[client_socket]

                print(f"[DISCONNECTED] {client_address} disconnected.")

                broadcast(
                    f"[SYSTEM] {username} left the chat.".encode(),
                    client_socket
                )

                if client_socket in clients:
                    del clients[client_socket]

                break

            decoded_message = message.decode()

            username = clients[client_socket]

            print(f"[MESSAGE RECEIVED] {username}: {decoded_message}")

            broadcast(
                f"{username}: {decoded_message}".encode(),
                client_socket
            )

        except:
            print(f"[ERROR] Connection lost with {client_address}")

            if client_socket in clients:
                username = clients[client_socket]

                broadcast(
                    f"[SYSTEM] {username} left the chat.".encode(),
                    client_socket
                )

                del clients[client_socket]

            break

    client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((HOST, PORT))

    server_socket.listen()

    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()

        username = client_socket.recv(BUFFER_SIZE).decode()

        clients[client_socket] = username
        
        broadcast(
            f"[SYSTEM] {username} joined the chat.".encode(),
            client_socket
        )

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )

        client_thread.start()


if __name__ == "__main__":
    start_server()