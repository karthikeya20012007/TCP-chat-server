import socket
import threading

from shared.protocol import create_message, parse_message
from shared.config import HOST, PORT


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                print("[SERVER DISCONNECTED]")
                break

            parsed_message = parse_message(message)

            message_type = parsed_message["type"]
            sender = parsed_message["sender"]
            content = parsed_message["content"]

            if message_type == "chat":
                print(f"\n{sender}: {content}")

            elif message_type == "system":
                print(f"\n[SYSTEM] {content}")

            elif message_type == "user_list":
                print("\n[ONLINE USERS]")

                for user in content:
                    print(f"- {user}")

        except:
            print("[ERROR] Connection lost.")
            break


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))

    username = input("Enter your username: ")

    client_socket.sendall(username.encode())

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,)
    )

    receive_thread.start()

    try:
        while True:
            message = input()

            if message.lower() == "exit":
                print("[DISCONNECTING] Closing connection.")
                break

            structured_message = create_message(
                "chat",
                username,
                message
            )

            client_socket.sendall(structured_message)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Client shutting down.")

    finally:
        client_socket.close()
        print("[CONNECTION CLOSED]")


if __name__ == "__main__":
    start_client()