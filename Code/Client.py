
#Implementerer legitime HTTP-klienter, som sender GET-requests til serveren og måler latenstid
import time         #Bruges til tidsmåling og pauser mellem requests
import argparse     #Bruges til at angive parametre ved kørsel af programmet
import http.client  #Bruges til at sende HTTP-requests og modtage HTTP-responses

#Importerer nødvendige biblioteker til at gemme i CSV-filer
import csv
from datetime import datetime
from pathlib import Path


#Serverens IP og port i Mininet
SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000


def send_requests(num_requests, interval, client_id, duration=None):
    #Sender HTTP-requests indtil det ønskede antal eller forsøgsvarighed er nået

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

        #Øger requestnummeret
        i += 1

        #Initialiserer forbindelsen som None, så den kan lukkes i finally-blokken
        connection = None

        try:
            #Opretter en HTTP-forbindelse til serveren med en timeout på 5 sekunder
            connection = http.client.HTTPConnection(
                SERVER_IP, SERVER_PORT, timeout=5
            )

            #Starter tidsmålingen for det enkelte request
            request_start = time.perf_counter()

            #Sender et HTTP GET-request til serverens rod ("/")
            connection.request("GET", "/")

            #Modtager HTTP-responsen fra serveren
            response = connection.getresponse()

            #Læser data fra HTTP-responsen (forventet 10240 bytes = 10 KiB)
            data = response.read()

            #Stopper tidsmålingen for det enkelte request
            request_end = time.perf_counter()

            #Udregner latenstiden i millisekunder
            latency_ms = (request_end - request_start) * 1000

            #Tjekker om HTTP-responsen er 200 OK, og om datamængden er 10240 bytes
            #Hvis begge betingelser er opfyldt, markeres requestet som SUCCESS
            #Ellers markeres det som FAILED
            if response.status == 200 and len(data) == 10240:
                status = "SUCCESS"
            else:
                status = "FAILED"

            #Udskriver resultatet af requestet i terminalen
            print(
                f"Request {i}: {status} | "
                f"HTTP {response.status} | "
                f"{len(data)} bytes | "
                f"Latency: {latency_ms:.3f} ms"
            )

            #Gemmer requestnummer, latenstid og status i klientens CSV-logfil
            log_request(
                client_id=client_id,
                request_id=i,
                latency=latency_ms,
                status=status
            )

        #Registrerer timeout og gemmer resultatet i logfilen
        except TimeoutError:
            print(f"Request {i}: TIMEOUT")

            log_request(
                client_id=client_id,
                request_id=i,
                latency=None,
                status="TIMEOUT"
            )

        #Registrerer netværks- og forbindelsesfejl og gemmer resultatet i logfilen
        except OSError as error:
            print(f"Request {i}: CONNECTION_ERROR - {error}")

            log_request(
                client_id=client_id,
                request_id=i,
                latency=None,
                status="CONNECTION_ERROR"
            )

        #Registrerer HTTP-protokolfejl og gemmer resultatet i logfilen
        except http.client.HTTPException as error:
            print(f"Request {i}: HTTP_ERROR - {error}")

            log_request(
                client_id=client_id,
                request_id=i,
                latency=None,
                status="HTTP_ERROR"
            )

        #Lukker HTTP-forbindelsen, uanset om requestet lykkedes eller fejlede
        finally:
            if connection is not None:
                connection.close()

        #Venter det angivne interval mellem requests
        #Der ventes ikke efter det sidste request ved antalsbaserede forsøg
        if num_requests is None or i < num_requests:

            if duration is None:
                time.sleep(interval)

            else:
                #Beregner hvor lang tid der er tilbage af eksperimentet
                remaining_time = duration - (
                    time.perf_counter() - experiment_start
                )

                #Venter højst den resterende forsøgsvarighed
                if remaining_time > 0:
                    time.sleep(min(interval, remaining_time))


def log_request(client_id, request_id, latency, status):
    #Opretter en mappe til logfiler, hvis den ikke allerede eksisterer
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    #Opretter en separat logfil for hver klient
    log_file = log_dir / f"client_{client_id}_log.csv"

    #Tjekker om logfilen allerede eksisterer
    file_exists = log_file.exists()

    #Åbner CSV-filen i append-tilstand, så tidligere målinger ikke overskrives
    with open(log_file, mode="a", newline="") as csvfile:

        #Definerer kolonnerne i CSV-filen
        fieldnames = [
            "timestamp",
            "request_id",
            "latency_ms",
            "status"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        #Skriver kolonneoverskrifter, hvis filen er ny
        if not file_exists:
            writer.writeheader()

        #Gemmer tidspunkt, requestnummer, latenstid og status
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "latency_ms": latency,
            "status": status
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
    if args.interval < 0:
        parser.error("--interval must be non-negative")

    #Starter klienten med de angivne parametre
    send_requests(
        args.requests,
        args.interval,
        args.client_id,
        args.duration
    )
