import socket
import threading

from shared.config import HOST, PORT

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                print("[SERVER DISCONNECTED]")
                break

            print(f"\n{message.decode()}")

        except:
            print("[ERROR] Connection lost.")
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))
    
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,)
    )

    receive_thread.start()

    try:
        while True:
            message = input("You: ")

            if message.lower() == "exit":
                print("[DISCONNECTING] Closing connection.")
                break

            client_socket.sendall(message.encode())

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Client shutting down.")

    finally:
        client_socket.close()
        print("[CONNECTION CLOSED]")


if __name__ == "__main__":
    start_client()