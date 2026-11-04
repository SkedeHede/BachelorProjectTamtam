#Implementerer legitime klienter, som sender requests og måler svartider
import socket
import time
import argparse #bib til at læse argumenter i terminalen

SERVER_IP = "10.0.0.1"
PORT = 5000




def send_requests(num_requests, interval):
    try:
        # Create TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))

            for i in range(num_requests):
                message = f"Request {i + 1}\n".encode() #newline for at kunne skelne mellem pakker
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

                if i < num_requests - 1:
                    time.sleep(interval)

    except socket.timeout:
        print("Request timed out")

    except OSError as error:
        print(f"Connection error: {error}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Legitimate TCP client for Mininet DDoS experiments"
    )

    parser.add_argument( #antal requests kan angives i terminalen
        "--requests",
        type=int,
        default=3,
        choices=range(1, 6), #mellem 1-5 requests
        help="Number of requests (1-5)"
    ) 

    parser.add_argument( #hardcoded 1s mellem hvert request
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between requests"
    )

    args = parser.parse_args()

    if args.interval < 0:
        parser.error("--interval must be non-negative")

    send_requests(args.requests, args.interval)

