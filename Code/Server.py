#Implementerer TCP-serveren, som skal modtage og besvare requests
import socket

HOST = "0.0.0.0"
PORT = 5000


def start_server():
    # Create TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow address reuse
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind socket to address and port
    server.bind((HOST, PORT))

    # Listen for incoming connections
    server.listen(10)

    print(f"Server listening on port {PORT}")

    while True:
        # Accept a client connection
        connection, address = server.accept()

        with connection:
            print(f"Connected: {address}")

            # Receive application request
            data = connection.recv(1024)

            while True:
                data = connection.recv(1024)

                if not data:
                    break

                print(f"Received: {data.decode()}")
                connection.sendall(b"ACK")


if __name__ == "__main__":
    start_server()
