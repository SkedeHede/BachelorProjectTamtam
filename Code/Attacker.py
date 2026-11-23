
import argparse
import csv
import http.client
import time
from datetime import datetime
from pathlib import Path


SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000

# Begrænsninger til kontrollerede eksperimenter
MAX_RATE = 50
MAX_DURATION = 120


def send_request():
    connection = None
    start = time.perf_counter()

    try:
        connection = http.client.HTTPConnection(
            SERVER_IP,
            SERVER_PORT,
            timeout=5
        )

        connection.request("GET", "/")
        response = connection.getresponse()
        data = response.read()

        latency_ms = (time.perf_counter() - start) * 1000

        if response.status == 200 and len(data) == 10240:
            status = "SUCCESS"
        else:
            status = "FAILED"

    except TimeoutError:
        latency_ms = (time.perf_counter() - start) * 1000
        status = "TIMEOUT"

    except OSError:
        latency_ms = (time.perf_counter() - start) * 1000
        status = "CONNECTION_ERROR"

    finally:
        if connection is not None:
            connection.close()

    return latency_ms, status


def start_attack(attacker_id, duration, rate, log_dir):

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"attacker_{attacker_id}_log.csv"

    interval = 1.0 / rate
    start_time = time.perf_counter()
    end_time = start_time + duration
    next_request = start_time

    request_id = 0

    with open(log_file, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "attacker_id",
            "request_id",
            "latency_ms",
            "status"
        ])

        while time.perf_counter() < end_time:

            now = time.perf_counter()

            if now < next_request:
                time.sleep(min(next_request - now, end_time - now))
                continue

            request_id += 1

            latency_ms, status = send_request()

            writer.writerow([
                datetime.now().isoformat(),
                attacker_id,
                request_id,
                round(latency_ms, 3),
                status
            ])

            next_request += interval

            # Undgå at indhente forsinkede requests i en burst
            next_request = max(next_request, time.perf_counter())

    print(f"{attacker_id} finished: {request_id} requests")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Controlled HTTP load generator for Mininet"
    )

    parser.add_argument("--attacker-id", type=str, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--rate", type=float, required=True)
    parser.add_argument("--log-dir", type=str, required=True)

    args = parser.parse_args()

    if not (0 < args.rate <= MAX_RATE):
        parser.error(f"Rate must be between 0 and {MAX_RATE} req/s")

    if not (0 < args.duration <= MAX_DURATION):
        parser.error(f"Duration must be between 0 and {MAX_DURATION} seconds")

    start_attack(
        args.attacker_id,
        args.duration,
        args.rate,
        args.log_dir
    )
