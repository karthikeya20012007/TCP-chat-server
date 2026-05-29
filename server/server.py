import socket
import threading

from shared.protocol import create_message, parse_message

from shared.config import HOST, PORT, BUFFER_SIZE

from server.database import save_message, get_recent_messages

clients = {}


def broadcast(message, sender_socket):
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.send(message)

            except:
                del clients[client]
                client.close()

def send_user_list(client_socket):
    usernames = list(clients.values())

    user_list_message = create_message(
        "user_list",
        "SYSTEM",
        usernames
    )

    client_socket.sendall(user_list_message)

def send_chat_history(client_socket):
    recent_messages = get_recent_messages()

    for sender, content in recent_messages:
        history_message = create_message(
            "history",
            sender,
            content
        )

        client_socket.sendall(history_message)

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")

    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE)

            if not message:
                username = clients[client_socket]

                print(f"[DISCONNECTED] {client_address} disconnected.")

                broadcast(
                    create_message(
                        "system",
                        "SYSTEM",
                        f"{username} left the chat."
                    ),
                    client_socket
                )

                if client_socket in clients:
                    del clients[client_socket]

                break

            parsed_message = parse_message(message)

            message_type = parsed_message["type"]
            sender = parsed_message["sender"]
            content = parsed_message["content"]

            print(f"[MESSAGE RECEIVED] {sender}: {content}")
            
            save_message(sender, content)
            
            broadcast(
                create_message(
                    "chat",
                    sender,
                    content
                ),
                client_socket
            )

        except:
            print(f"[ERROR] Connection lost with {client_address}")

            if client_socket in clients:
                username = clients[client_socket]

                broadcast(
                    create_message(
                        "system",
                        "SYSTEM",
                        f"{username} left the chat."
                    ),
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
        
        send_user_list(client_socket)
        send_chat_history(client_socket)
        
        broadcast(
            create_message(
                "system",
                "SYSTEM",
                f"{username} joined the chat."
            ),
            client_socket
        )

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )

        client_thread.start()


if __name__ == "__main__":
    start_server()