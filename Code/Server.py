#Implementerer TCP-serveren, som skal modtage og besvare requests
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

#threading
def handle_client(connection, address):
    print(f"Connected: {address}")

    with connection:
        with connection.makefile("rb") as reader:
            while True:
                data = reader.readline()

                if not data:
                    break

                message = data.decode().strip()

                print(f"Received from {address}: {message}")

                connection.sendall(b"ACK\n")

    print(f"Disconnected: {address}")


#selve serveren
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
        #accept a client connection
        connection, address = server.accept()

        #create a thread for client
        client_thread = threading.Thread(
            target=handle_client,
            args=(connection, address),
            daemon=True
        )

        # Start the thread
        client_thread.start()



if __name__ == "__main__":
    start_server()
