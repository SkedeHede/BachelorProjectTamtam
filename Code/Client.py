#Implementerer legitime klienter, som sender requests og måler svartider
import socket
import time

SERVER_IP = "10.0.0.1"
PORT = 5000

NUM_REQUESTS = 3


def send_requests():
    try:
        # Create TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))

            for i in range(NUM_REQUESTS):
                message = f"Request {i + 1}".encode()

                start_time = time.perf_counter()

                client.sendall(message)
                response = client.recv(1024)

                end_time = time.perf_counter()

                if not response:
                    print("Server closed the connection")
                    break

                latency = (end_time - start_time) * 1000

                print(f"Request {i + 1}: {response.decode()}")
                print(f"Response time: {latency:.3f} ms")

                time.sleep(1)

    except socket.timeout:
        print("Request timed out")

    except OSError as error:
        print(f"Connection error: {error}")


if __name__ == "__main__":
    send_requests()
