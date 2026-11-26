#Implementerer legitime HTTP-klienter, som sender GET-requests til serveren og måler latenstid
import time         #Bruges til tidsmåling og pauser mellem requests
import argparse     #Bruges til at angive parametre ved kørsel af programmet
import http.client  #Bruges til at sende HTTP-requests og modtage HTTP-responses
import socket       #Bruges til at håndtere netværksforbindelser

#Importerer nødvendige biblioteker til at gemme i CSV-filer
import csv
from datetime import datetime
from pathlib import Path

#Imports for offset og randomization
import random

#Import for threading
import threading


#Serverens IP og port i Mininet
SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000

CSV_LOCK = threading.Lock() #threading safety


""" brugt til at teste HTTP1.1 persistent connections i stedet for HTTP1.0. 
def test_persistent_connection():

    connection = http.client.HTTPConnection(
        SERVER_IP, SERVER_PORT, timeout=5
    )

    try:
        for i in range(3):

            connection.request("GET", "/")

            response = connection.getresponse()
            data = response.read()

            print(
                f"Request {i + 1}: "
                f"HTTP {response.status}, "
                f"{len(data)} bytes"
            )

            print(f"Socket: {connection.sock.getsockname()}")

    finally:
        connection.close()
"""


def send_pipelined_requests(request_ids, client_id, log_dir):

    start_times = {}
    completed_requests = set()  

    connection_start = time.perf_counter() #startet før 3-way-handshake
    try:
        #Opretter én TCP-forbindelse
        with socket.create_connection(
            (SERVER_IP, SERVER_PORT), timeout=5
        ) as connection:

            #Definerer et HTTP/1.1 GET-request. Dette skal gøres da http.client.HTTPConnection ikke understøtter pipelining direkte.
            request = (
                "GET / HTTP/1.1\r\n"
                f"Host: {SERVER_IP}:{SERVER_PORT}\r\n"
                "Connection: keep-alive\r\n"
                "\r\n"
            ).encode()

            #Sender alle requests uden at vente på responses
            for i, request_id in enumerate(request_ids):
                if i == 0:
                    start_times[request_id] = connection_start
                else:
                    start_times[request_id] = time.perf_counter()
                connection.sendall(request)

            #Bruger fælles buffer til at læse svar
            with connection.makefile("rb") as reader:

                for request_id in request_ids: #returner svar i samme rækkefølge som requests blev sendt
                    status_line = reader.readline().decode().strip()
                    content_length = None #reset længde efter hver response

                    #Kontrollerer HTTP-statuslinjen
                    if not status_line.startswith("HTTP/"):
                        raise ValueError("Invalid HTTP status line")

                    status_code = int(status_line.split()[1])

                    #Læser HTTP-header
                    while True:
                        line = reader.readline()

                        if not line: #fejl afbrudt hvis ikke flere byte modtages
                            raise ConnectionError("Unexpected end while reading HTTP headers")

                        if line == b"\r\n":
                            break

                        if line.lower().startswith(b"content-length:"):
                            content_length = int(line.split(b":", 1)[1])

                    if content_length is None or content_length < 0:
                        raise ValueError("Missing Content-Length")

                    #læser HTTP-response body
                    data = reader.read(content_length)

                    if len(data) != content_length:
                        raise ConnectionError("Incomplete response")

                    #beregner individuel latency
                    request_end = time.perf_counter()

                    latency_ms = (request_end - start_times[request_id]) * 1000

                    #Kontrollerer HTTP-response
                    error_message = None

                    if status_code == 200 and len(data) == 10240:
                        status = "SUCCESS"
                    else:
                        status = "FAILED"
                        error_message = (
                            f"HTTP status: {status_code}, "
                            f"Received bytes: {len(data)}, "
                            f"Expected bytes: 10240"
                        )

                    #Logger det individuelle request
                    log_request(
                        client_id=client_id,
                        request_id=request_id,
                        latency=latency_ms,
                        status=status,
                        log_dir=log_dir,
                        error_message=error_message
                    )

                    completed_requests.add(request_id)

    except (OSError, ValueError, IndexError) as error:

        if isinstance(error, TimeoutError):
            status = "TIMEOUT"
        elif isinstance(error, OSError):
            status = "CONNECTION_ERROR"
        else:
            status = "HTTP_ERROR"

        #Logger alle requests, som ikke blev færdigbehandlet
        for request_id in request_ids:

            if request_id not in completed_requests:

                log_request(
                    client_id=client_id,
                    request_id=request_id,
                    latency=None,
                    status=status,
                    log_dir=log_dir,
                    error_message=str(error)
                )
                    


def send_single_request(request_id, client_id, log_dir):

    connection = None
    latency_ms = None
    error_message = None

    try:
        #Opretter en individuel HTTP-forbindelse
        connection = http.client.HTTPConnection(
            SERVER_IP, SERVER_PORT, timeout=5
        )

        #Starter tidsmålingen
        request_start = time.perf_counter()

        #Sender HTTP GET-request
        connection.request("GET", "/")

        #Modtager HTTP-response og læser data
        response = connection.getresponse()
        data = response.read()

        #Stopper tidsmålingen
        request_end = time.perf_counter()
        latency_ms = (request_end - request_start) * 1000

        #Kontrollerer HTTP-response
        if response.status == 200 and len(data) == 10240:
            status = "SUCCESS"
        else:
            status = "FAILED"
            error_message = (
                f"HTTP status: {response.status}, "
                f"Received bytes: {len(data)}, "
                f"Expected bytes: 10240"
            )

            """debugging af HTTP-respons
            print(
            f"Request {request_id}: {status} | "
            f"HTTP {response.status} | "
            f"{len(data)} bytes | "
            f"Latency: {latency_ms:.3f} ms"
            )"""

    except TimeoutError as error:
        status = "TIMEOUT"
        error_message = str(error)
        print(f"Request {request_id}: TIMEOUT - {error}")

    except OSError as error:
        status = "CONNECTION_ERROR"
        error_message = str(error)
        print(f"Request {request_id}: CONNECTION_ERROR - {error}")

    except http.client.HTTPException as error:
        status = "HTTP_ERROR"
        error_message = str(error)
        print(f"Request {request_id}: HTTP_ERROR - {error}")

    finally:
        if connection is not None:
            connection.close()

    #Gemmer resultatet i klientens CSV-logfil
    log_request(
        client_id=client_id,
        request_id=request_id,
        latency=latency_ms,
        status=status,
        log_dir=log_dir,
        error_message=error_message
    )

def send_requests(num_requests, interval, client_id, duration=None, log_dir="logs", parallel_probability=0.10, max_extra_connections=4):
    #Starter tidsmålingen for hele eksperimentet
    experiment_start = time.perf_counter()
    i = 0

    while True:

        #Stopper når det ønskede antal requests er sendt
        if num_requests is not None and i >= num_requests:
            break

        #Stopper når den angivne forsøgsvarighed er nået
        if duration is not None:
            elapsed_time = time.perf_counter() - experiment_start

            if elapsed_time >= duration:
                break

        #Bestemmer antallet af HTTP-requests i denne gruppe
        num_connections = 1

        #10% sandsynlighed for ekstra parallelle forbindelser
        if random.random() < parallel_probability:
            num_connections += random.randint(1, max_extra_connections)

        #Sikrer at det maksimale antal requests ikke overskrides
        if num_requests is not None:
            num_connections = min(num_connections, num_requests - i)

        #Liste til at holde styr på trådene
        threads = []

        #Opretter og starter en tråd for hvert HTTP-request
        for j in range(num_connections):
            i += 1

            thread = threading.Thread(
                target=send_single_request,
                args=(i, client_id, log_dir)
            )

            threads.append(thread)
            thread.start()

        #Venter på at alle tråde i gruppen er færdige
        for thread in threads:
            thread.join()

        #Venter et eksponentialfordelt interval mellem requests
        if num_requests is None or i < num_requests:

            delay = random.expovariate(1 / interval)

            if duration is None:
                time.sleep(delay)

            else:
                #Beregner resterende forsøgsvarighed
                remaining_time = duration - (
                    time.perf_counter() - experiment_start
                )

                #Venter højst den resterende forsøgsvarighed
                if remaining_time > 0:
                    time.sleep(min(delay, remaining_time))


def log_request(client_id, request_id, latency, status, log_dir, error_message=None):

    #Opretter en mappe til logfiler
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    #Opretter en separat logfil for hver klient
    log_file = log_dir / f"client_{client_id}_log.csv"

    #Gemmer tidspunktet inden tråden eventuelt skal vente på låsen
    timestamp = datetime.now().isoformat()

    #Sikrer at kun én tråd skriver til CSV-filen ad gangen
    with CSV_LOCK:

        #Tjekker om logfilen allerede eksisterer
        file_exists = log_file.exists()

        with open(log_file, mode="a", newline="") as csvfile:

            fieldnames = [
                "timestamp",
                "request_id",
                "latency_ms",
                "status",
                "error_message"
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "timestamp": timestamp,
                "request_id": request_id,
                "latency_ms": latency,
                "status": status,
                "error_message": error_message
            })


#Udføres kun, når Client.py køres direkte
if __name__ == "__main__":

    #Opretter en parser til kommandolinjeargumenter
    parser = argparse.ArgumentParser(
        description="Legitimate HTTP client for Mininet DDoS experiments"
    )

    #Antal HTTP-requests, som klienten skal sende
    parser.add_argument(
        "--requests",
        type=int,
        default=None,
        help="Number of requests to send"
    )

    #Forsøgsvarighed angivet i sekunder
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Experiment duration in seconds"
    )

    #Ventetid mellem requests i sekunder
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between requests"
    )

    #Identifikation af klienten, som bruges til navngivning af logfilen
    parser.add_argument(
        "--client-id",
        type=str,
        default="client1",
        help="Identifier for the client"
    )

    #Path for specifikt eksperiment
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for client log files"
    )

    #Sandsynlighed for ekstra parallelle HTTP-forbindelser
    parser.add_argument(
        "--parallel-probability",
        type=float,
        default=0.10,
        help="Probability of extra parallel HTTP connections"
    )

    #Maksimalt antal ekstra parallelle forbindelser
    parser.add_argument(
        "--max-extra-connections",
        type=int,
        default=4,
        help="Maximum number of extra parallel connections"
    )

    #Indlæser argumenterne fra kommandolinjen
    args = parser.parse_args()

    #Hvis hverken antal requests eller varighed er angivet,
    #sendes som standard 3 requests
    if args.requests is None and args.duration is None:
        args.requests = 3

    #Kontrollerer at antallet af requests er positivt
    if args.requests is not None and args.requests < 1:
        parser.error("--requests must be positive")

    #Kontrollerer at forsøgsvarigheden er positiv
    if args.duration is not None and args.duration <= 0:
        parser.error("--duration must be positive")

    #Tillader ikke at både antal requests og varighed angives
    if args.requests is not None and args.duration is not None:
        parser.error("Specify either --requests or --duration, not both")

    #Kontrollerer at intervallet ikke er negativt
    if args.interval <= 0:
        parser.error("--interval must be positive")

    #Kontrollerer at sandsynligheden ligger mellem 0 og 1
    if not 0 <= args.parallel_probability <= 1:
        parser.error("--parallel-probability must be between 0 and 1")

    #Kontrollerer at maksimalt antal ekstra forbindelser er positivt
    if args.max_extra_connections < 1:
        parser.error("--max-extra-connections must be positive")

    #Starter klienten med de angivne parametre
    send_requests(
        args.requests,
        args.interval,
        args.client_id,
        args.duration,
        args.log_dir,
        args.parallel_probability,
        args.max_extra_connections
    )
