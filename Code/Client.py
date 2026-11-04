# Implementerer legitime klienter, som sender requests og måler svartider
import socket
import time
import argparse

#Importerer nødvendige biblioteker til at gemme i CSV-filer
import csv
from datetime import datetime
from pathlib import Path

SERVER_IP = "10.0.0.1"
PORT = 5000


def send_requests(num_requests, interval, client_id):
    try:
        # Create TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))

            with client.makefile("rb") as reader:
                for i in range(num_requests):
                    message = f"Request {i + 1}\n".encode()

                    start_time = time.perf_counter()

                    client.sendall(message)
                    response = reader.readline()

                    end_time = time.perf_counter()

                    if not response:
                        print("Server closed the connection")
                        break

                    latency = (end_time - start_time) * 1000

                    print(f"Request {i + 1}: {response.decode().strip()}")
                    print(f"Response time: {latency:.3f} ms")

                    log_request(
                        client_id=client_id,
                        request_id=i + 1,
                        latency=latency,
                        status="SUCCESS"
                    )

                    if i < num_requests - 1:
                        time.sleep(interval)

    except socket.timeout:
        print("Request timed out")

    except OSError as error:
        print(f"Connection error: {error}")


def log_request(client_id, request_id, latency, status):
    #Opretter en mappe til logfiler, hvis den ikke allerede eksisterer, og gemmer logdata i en CSV-fil
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    #Opretter en logfil for hver klient, hvis den ikke allerede eksisterer, og tilføjer logdata til filen
    log_file = log_dir / f"client_{client_id}_log.csv"

    #Tjekker om logfilen allerede eksisterer, og hvis ikke, opretter den en ny fil med kolonneoverskrifter
    file_exists = log_file.exists()

    #Gemmer logdata i CSV-filen med kolonneoverskrifterne: timestamp, request_id, latency_ms og status
    with open(log_file, mode="a", newline="") as csvfile:
        fieldnames = ["timestamp", "request_id", "latency_ms", "status"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "latency_ms": latency,
            "status": status
        })



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Legitimate TCP client for Mininet DDoS experiments"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=3,
        choices=range(1, 6),
        help="Number of requests (1-5)"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between requests"
    )

    parser.add_argument(
        "--client-id",
        type=str,
        default="client1",
        help="Identifier for the client"
    )

    args = parser.parse_args()

    if args.interval < 0:
        parser.error("--interval must be non-negative")

    send_requests(args.requests, args.interval, args.client_id)