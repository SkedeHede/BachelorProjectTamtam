# Implementerer legitime HTTP-klienter, som sender GET-requests til serveren og måler latenstid
import time         #Bruges til tidsmåling og pauser mellem requests
import argparse     #Bruges til at angive parametre ved kørsel af programmet
import http.client  #Bruges til at sende HTTP-requests og modtage HTTP-responses

#Importerer nødvendige biblioteker til at gemme i CSV-filer
import csv
from datetime import datetime
from pathlib import Path

#Serveren IP og port i mininet
SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000


def send_requests(num_requests, interval, client_id):
    #Sender det angivne antal HTTP-requests til serveren
    for i in range(num_requests):
        connection = None #Initialiserer forbindelsen som None, så den kan lukkes i finally-blokken
        try:
            
            connection = http.client.HTTPConnection(SERVER_IP, SERVER_PORT, timeout=5) #Opretter en HTTP-forbindelse til serveren med en timeout på 5 sekunder

            start_time = time.perf_counter() #Starter tidsmåling for latenstid

            connection.request("GET", "/") #Sender en HTTP GET-request til serverens rod ("/")
            response = connection.getresponse() #Modtager HTTP-responsen fra serveren
            data = response.read() #Læser data for HTTP-responsen, som sendes fra serveren (Forventet 10240 bytes ≈ 10 KB)

            end_time = time.perf_counter() #Stopper tidsmåling for latenstid

            latency_ms = (end_time - start_time) * 1000 #Udregner latenstid i millisekunder

            #Tjekker om HTTP-responsen er 200 OK og om dataens længde er 10240 bytes, som forventet. 
            #Hvis begge betingelser er opfyldt, markeres requesten som SUCCESS, ellers som FAILED.
            if response.status == 200 and len(data) == 10240:
                status = "SUCCESS"
            else:
                status = "FAILED"

            #Udskriver resultatet af requesten i terminalen
            print(f"Request {i + 1}: {status} | HTTP {response.status} | {len(data)} bytes | Latency: {latency_ms:.3f} ms")

            #Gemmer requestnummer, latenstid og status i en CSV-logfil for den pågældende klient
            log_request(
                client_id=client_id,
                request_id=i + 1,
                latency=latency_ms,
                status=status
            )

        #Registrerer timeout, hvis serveren ikke svarer inden for 5 sekunder, og gemmer dette i logfilen istedet
        except TimeoutError:
            print(f"Request {i + 1}: TIMEOUT")

            log_request(
                client_id=client_id,
                request_id=i + 1,
                latency=None,
                status="TIMEOUT"
            )

        #Registrerer netværksfejl, hvis forbindelsen til serveren ikke kan oprettes, og gemmer dette i logfilen istedet
        except OSError as error:
            print(f"Request {i + 1}: CONNECTION_ERROR - {error}")

            log_request(
                client_id=client_id,
                request_id=i + 1,
                latency=None,
                status="CONNECTION_ERROR"
            )

        #Registrerer HTTP-fejl, hvis der opstår en fejl i HTTP-kommunikationen, og gemmer dette i logfilen istedet
        except http.client.HTTPException as error:
            print(f"Request {i + 1}: HTTP_ERROR - {error}")

            log_request(
                client_id=client_id,
                request_id=i + 1,
                latency=None,
                status="HTTP_ERROR"
            )

        #Lukker HTTP-forbindelsen til serveren, uanset om requesten lykkedes eller fejlede
        finally:
            if connection is not None:
                connection.close()

        #Venter det angivne interval mellem requests, medmindre det er den sidste request
        if i < num_requests - 1:
            time.sleep(interval)

        


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